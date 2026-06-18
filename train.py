import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
import lightgbm as lgb
import xgboost as xgb
import joblib
import os

def prepare_training_data(df):
    print("Preparing training data...")
    # Group by hotspot, date, hour to get violation count per hour per hotspot
    df['date'] = df['created_datetime'].dt.date
    
    # We need to build a time-series dataset. 
    # For simplicity, we aggregate and use shift to create historical features.
    grouped = df.groupby(['hotspot_id', 'date', 'hour', 'day_of_week', 'month', 'police_station', 'junction_name']).agg(
        violation_count=('id', 'count'),
        avg_PIS=('PIS', 'mean')
    ).reset_index()
    
    # Sort by hotspot and time
    grouped.sort_values(by=['hotspot_id', 'date', 'hour'], inplace=True)
    
    # Create historical features
    grouped['historical_violation_count'] = grouped.groupby('hotspot_id')['violation_count'].shift(1)
    grouped['historical_PIS'] = grouped.groupby('hotspot_id')['avg_PIS'].shift(1)
    
    # Drop NAs (first hour for each hotspot will have NA for historical features)
    grouped.dropna(inplace=True)
    
    return grouped

def encode_features(df):
    print("Encoding categorical features...")
    le_dict = {}
    categorical_cols = ['police_station', 'junction_name']
    
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        le_dict[col] = le
        
    return df, le_dict

def train_and_evaluate():
    data_path = 'processed_data.csv'
    if not os.path.exists(data_path):
        print("processed_data.csv not found. Please run hotspot.py first.")
        return
        
    # Read processed data
    # Parse dates explicitly
    df = pd.read_csv(data_path, parse_dates=['created_datetime'])
    
    # Keep only hotspots
    df = df[df['hotspot_id'] != -1].copy()
    
    train_df = prepare_training_data(df)
    train_df, le_dict = encode_features(train_df)
    
    features = ['hour', 'day_of_week', 'month', 'hotspot_id', 'police_station', 'junction_name', 
                'historical_violation_count', 'historical_PIS']
    target = 'violation_count'
    
    X = train_df[features]
    y = train_df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    models = {
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
        'LightGBM': lgb.LGBMRegressor(random_state=42, n_jobs=-1),
        'XGBoost': xgb.XGBRegressor(random_state=42, n_jobs=-1)
    }
    
    best_model = None
    best_r2 = -float('inf')
    best_name = ""
    
    print("Training models...")
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        
        mae = mean_absolute_error(y_test, preds)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        r2 = r2_score(y_test, preds)
        
        print(f"{name} Results:")
        print(f"MAE: {mae:.4f}, RMSE: {rmse:.4f}, R2: {r2:.4f}\n")
        
        if r2 > best_r2:
            best_r2 = r2
            best_model = model
            best_name = name
            
    print(f"Best Model: {best_name} with R2 = {best_r2:.4f}")
    
    # Save the best model and preprocessors
    joblib.dump(best_model, 'model.pkl')
    joblib.dump(le_dict, 'preprocessing_pipeline.pkl')
    print("Saved model.pkl and preprocessing_pipeline.pkl")

if __name__ == "__main__":
    train_and_evaluate()
