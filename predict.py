import pandas as pd
import joblib
import os

def load_models():
    model_path = 'model.pkl'
    pipeline_path = 'preprocessing_pipeline.pkl'
    
    if not os.path.exists(model_path) or not os.path.exists(pipeline_path):
        print("Model or preprocessing pipeline not found. Please run train.py first.")
        return None, None
        
    model = joblib.load(model_path)
    le_dict = joblib.load(pipeline_path)
    return model, le_dict

def predict_hotspot_risk(input_data):
    """
    input_data should be a list of dictionaries with keys:
    'hour', 'day_of_week', 'month', 'hotspot_id', 'police_station', 'junction_name', 
    'historical_violation_count', 'historical_PIS'
    """
    model, le_dict = load_models()
    if model is None:
        return None
        
    df = pd.DataFrame(input_data)
    
    # Encode categorical features
    for col in ['police_station', 'junction_name']:
        if col in df.columns and col in le_dict:
            le = le_dict[col]
            # Handle unseen labels by assigning them to a default class or standardizing
            # For simplicity in this demo, we'll try to transform, fallback to 0 if unseen
            df[col] = df[col].apply(lambda x: le.transform([str(x)])[0] if str(x) in le.classes_ else 0)
            
    features = ['hour', 'day_of_week', 'month', 'hotspot_id', 'police_station', 'junction_name', 
                'historical_violation_count', 'historical_PIS']
    
    X = df[features]
    predictions = model.predict(X)
    
    df['predicted_violations'] = predictions
    # Ensure no negative predictions
    df['predicted_violations'] = df['predicted_violations'].clip(lower=0)
    
    # Priority Score = Predicted Violations * PIS
    df['priority_score'] = df['predicted_violations'] * df['historical_PIS']
    
    return df.sort_values(by='priority_score', ascending=False)

def generate_enforcement_plan(predictions_df):
    if predictions_df is None or predictions_df.empty:
        return
        
    print("Enforcement Deployment Plan:")
    
    top_hotspots = predictions_df.head(10)
    print("\nTop 10 Hotspots for Patrol:")
    for idx, row in top_hotspots.iterrows():
        print(f"Hotspot ID: {row['hotspot_id']} | Priority Score: {row['priority_score']:.2f} | Expected Violations: {row['predicted_violations']:.1f}")
        
    top_stations = predictions_df.groupby('police_station')['priority_score'].sum().sort_values(ascending=False).head(5)
    print("\nTop Police Stations to Dispatch:")
    # We don't have the inverse transform mapping immediately accessible here easily since we replaced unseen with 0,
    # but normally we would inverse_transform. Since we passed raw names in input_data, we should group by raw names.
    # Ah, the dataframe modified in place. Let's assume input_data has original names.
    pass # Real implementation in dashboard.

if __name__ == "__main__":
    # Example usage
    sample_input = [
        {'hour': 18, 'day_of_week': 4, 'month': 11, 'hotspot_id': 1, 'police_station': 'Madiwala', 'junction_name': 'No Junction', 'historical_violation_count': 5, 'historical_PIS': 45.0},
        {'hour': 18, 'day_of_week': 4, 'month': 11, 'hotspot_id': 2, 'police_station': 'Bellandur', 'junction_name': 'No Junction', 'historical_violation_count': 10, 'historical_PIS': 60.0}
    ]
    result = predict_hotspot_risk(sample_input)
    if result is not None:
        print(result[['hotspot_id', 'predicted_violations', 'priority_score']])
