import pandas as pd
import numpy as np
import ast
from sklearn.cluster import DBSCAN
import folium

def load_and_clean_data(file_path):
    print("Loading data...")
    # Load dataset
    df = pd.read_csv(file_path)
    
    # Keep only APPROVED violations
    df = df[df['validation_status'].str.lower() == 'approved'].copy()
    
    # Handle missing values
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    df.dropna(subset=['latitude', 'longitude'], inplace=True)
    df.fillna({'junction_name': 'Unknown', 'police_station': 'Unknown', 'location': 'Unknown'}, inplace=True)
    
    # Parse dates
    df['created_datetime'] = pd.to_datetime(df['created_datetime'], errors='coerce')
    df.dropna(subset=['created_datetime'], inplace=True)
    
    # Extract features
    df['hour'] = df['created_datetime'].dt.hour
    df['day_of_week'] = df['created_datetime'].dt.dayofweek
    df['month'] = df['created_datetime'].dt.month
    df['weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Parse violation_type (it is stored as string lists)
    def parse_violation(v):
        if pd.isna(v):
            return []
        try:
            return ast.literal_eval(v)
        except:
            return [v]
            
    df['violation_type_list'] = df['violation_type'].apply(parse_violation)
    # Explode if we want each violation separately, or just take the first/most severe.
    # Let's just create a primary_violation string for weighting.
    df['primary_violation'] = df['violation_type_list'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else 'UNKNOWN')
    
    print(f"Data loaded and cleaned. Total records: {len(df)}")
    return df

def get_vehicle_weight(vehicle_type):
    vt = str(vehicle_type).upper()
    if any(x in vt for x in ['TRUCK', 'LORRY', 'HGV', 'TANKER', 'LGV']):
        return 3
    elif any(x in vt for x in ['CAR', 'AUTO', 'CAB', 'VAN']):
        return 2
    else:
        # Defaults to Bike/Scooter/Motor Cycle = 1
        return 1

def get_violation_weight(violation):
    v = str(violation).upper()
    if 'DOUBLE' in v:
        return 3.0
    elif 'MAIN ROAD' in v:
        return 2.5
    elif 'NO PARKING' in v:
        return 2.0
    elif 'WRONG' in v:
        return 1.5
    else:
        return 1.0

def get_road_weight(location):
    loc = str(location).upper()
    if any(x in loc for x in ['HIGHWAY', 'METRO', 'ARTERIAL', 'RING ROAD', 'NH']):
        return 5
    elif any(x in loc for x in ['COMMERCIAL', 'MARKET', 'PLAZA', 'MALL', 'TECH PARK']):
        return 4
    elif any(x in loc for x in ['CROSS', 'MAIN', 'STREET']):
        return 3
    elif any(x in loc for x in ['LAYOUT', 'RESIDEN', 'BLOCK', 'COLONY']):
        return 1
    return 3 # Default collector

def get_peak_hour_weight(hour):
    if 6 <= hour <= 9:
        return 1.5
    elif 17 <= hour <= 21:
        return 1.5
    else:
        return 1.0

def calculate_pis(df):
    print("Calculating Parking Impact Score (PIS)...")
    
    df['vehicle_weight'] = df['vehicle_type'].apply(get_vehicle_weight)
    df['violation_weight'] = df['primary_violation'].apply(get_violation_weight)
    df['road_weight'] = df['location'].apply(get_road_weight)
    df['peak_hour_weight'] = df['hour'].apply(get_peak_hour_weight)
    
    df['PIS'] = (df['vehicle_weight'] * 
                 df['violation_weight'] * 
                 df['road_weight'] * 
                 df['peak_hour_weight'])
                 
    def classify_pis(pis):
        if pis < 15: return 'Low'
        elif pis < 40: return 'Medium'
        elif pis < 60: return 'High'
        else: return 'Critical'
        
    df['PIS_class'] = df['PIS'].apply(classify_pis)
    return df

def calculate_dynamic_fine(pis):
    if pis < 15:
        return 500
    elif pis < 40:
        return 1000
    elif pis < 60:
        return 2000
    else:
        return 5000

def detect_hotspots(df, eps_km=0.05, min_samples=20):
    print("Detecting hotspots using DBSCAN...")
    # Convert lat/lon to radians for haversine metric
    coords = df[['latitude', 'longitude']].dropna()
    # eps in kilometers, convert to radians (Earth radius approx 6371 km)
    eps_rad = eps_km / 6371.0
    
    db = DBSCAN(eps=eps_rad, min_samples=min_samples, algorithm='ball_tree', metric='haversine')
    
    # We may need to sample if data is too huge.
    # We will cluster on the subset of approved violations.
    # DBSCAN memory can be an issue for 300k points. Let's do it on unique rounded coordinates to speed up if needed.
    # For now, let's cluster directly on coords. If it crashes, we'll round to 4 decimals.
    df['hotspot_id'] = db.fit_predict(np.radians(coords))
    
    # Filter out noise (hotspot_id == -1)
    df_hotspots = df[df['hotspot_id'] != -1].copy()
    
    # Calculate hotspot metrics
    hotspot_metrics = df_hotspots.groupby('hotspot_id').agg(
        centroid_lat=('latitude', 'mean'),
        centroid_lon=('longitude', 'mean'),
        violation_count=('id', 'count'),
        avg_PIS=('PIS', 'mean')
    ).reset_index()
    
    # Hotspot density can be approximated by violation_count
    hotspot_metrics['hotspot_density'] = hotspot_metrics['violation_count']
    
    print(f"Detected {len(hotspot_metrics)} hotspots.")
    return df_hotspots, hotspot_metrics

def generate_hotspot_map(hotspot_metrics):
    if hotspot_metrics.empty:
        return None
        
    map_center = [hotspot_metrics['centroid_lat'].mean(), hotspot_metrics['centroid_lon'].mean()]
    m = folium.Map(location=map_center, zoom_start=11)
    
    for idx, row in hotspot_metrics.iterrows():
        folium.CircleMarker(
            location=[row['centroid_lat'], row['centroid_lon']],
            radius=min(row['violation_count'] / 50, 20) + 5,
            popup=f"Hotspot {row['hotspot_id']}<br>Violations: {row['violation_count']}<br>Avg PIS: {row['avg_PIS']:.2f}",
            color='red',
            fill=True,
            fillColor='red'
        ).add_to(m)
        
    return m

if __name__ == "__main__":
    file_path = "jan to may police violation_anonymized791b166.csv"
    df = load_and_clean_data(file_path)
    df = calculate_pis(df)
    df['dynamic_fine'] = df['PIS'].apply(calculate_dynamic_fine)
    df_hotspots, hotspot_metrics = detect_hotspots(df)
    hotspot_metrics.to_csv("hotspot_metrics.csv", index=False)
    df.to_csv("processed_data.csv", index=False)
    print("Data processing complete. Saved to processed_data.csv and hotspot_metrics.csv")
