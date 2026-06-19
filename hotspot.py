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
    
    # Parse dates and convert UTC to IST
    df['created_datetime'] = pd.to_datetime(df['created_datetime'], errors='coerce')
    df.dropna(subset=['created_datetime'], inplace=True)
    
    if df['created_datetime'].dt.tz is not None:
        df['created_datetime'] = df['created_datetime'].dt.tz_convert('Asia/Kolkata')
    else:
        df['created_datetime'] = df['created_datetime'].dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
    
    # Extract features
    df['hour'] = df['created_datetime'].dt.hour
    df['day_of_week'] = df['created_datetime'].dt.dayofweek
    df['month'] = df['created_datetime'].dt.month
    df['weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Flag February anomaly (for dashboard exclusion)
    df['is_feb_anomaly'] = (df['month'] == 2)
    
    # Parse violation_type (it is stored as string lists)
    def parse_violation(v):
        if pd.isna(v):
            return []
        try:
            return ast.literal_eval(v)
        except:
            return [v]
            
    df['violation_type_list'] = df['violation_type'].apply(parse_violation)
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
    # Morning peak 08:00-11:00 as per report, and evening 17:00-21:00
    if 8 <= hour <= 11:
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
    print("Detecting hotspots (Split: Named vs DBSCAN Discovered)...")
    
    # Exclude February data from hotspot clustering to avoid skewing by the anomaly
    # Actually, the report says "February should not be used in month-over-month trend interpretation", 
    # but let's exclude it from the core hotspot clustering to be safe, or keep it but it will just add less weight.
    # We will keep it but it has naturally less count.
    
    df['is_discovered_cluster'] = False
    
    named_mask = ~df['junction_name'].isin(['No Junction', 'Unknown', 'nan', ''])
    df_named = df[named_mask].copy()
    
    named_junctions = df_named['junction_name'].unique()
    named_id_map = {name: i + 1000 for i, name in enumerate(named_junctions)}
    df_named['hotspot_id'] = df_named['junction_name'].map(named_id_map)
    df_named['is_discovered_cluster'] = False
    
    df_unnamed = df[~named_mask].copy()
    
    # Run DBSCAN on unnamed
    coords = df_unnamed[['latitude', 'longitude']].dropna()
    eps_rad = eps_km / 6371.0
    
    db = DBSCAN(eps=eps_rad, min_samples=min_samples, algorithm='ball_tree', metric='haversine')
    if not coords.empty:
        df_unnamed['hotspot_id'] = db.fit_predict(np.radians(coords))
    else:
        df_unnamed['hotspot_id'] = -1
        
    df_unnamed['is_discovered_cluster'] = True
    
    # Combine back
    df_combined = pd.concat([df_named, df_unnamed])
    
    # Filter out noise (hotspot_id == -1)
    df_hotspots = df_combined[df_combined['hotspot_id'] != -1].copy()
    
    # Helper to calculate peak window
    def get_peak_window(hours_series):
        if hours_series.empty:
            return "N/A"
        mode_hour = hours_series.mode()[0]
        # Make a 2-hour window around the mode hour
        start = mode_hour
        end = (mode_hour + 2) % 24
        return f"{start:02d}:00–{end:02d}:00"
    
    # Calculate hotspot metrics
    hotspot_metrics = df_hotspots.groupby(['hotspot_id', 'is_discovered_cluster']).agg(
        centroid_lat=('latitude', 'mean'),
        centroid_lon=('longitude', 'mean'),
        violation_count=('id', 'count'),
        avg_PIS=('PIS', 'mean'),
        police_station=('police_station', lambda x: x.mode()[0] if not x.empty else 'Unknown'),
        junction_name=('junction_name', lambda x: x.mode()[0] if not x.empty else 'Unknown')
    ).reset_index()
    
    # Add peak window separately to avoid pandas warning on mode
    peak_windows = df_hotspots.groupby(['hotspot_id', 'is_discovered_cluster'])['hour'].apply(get_peak_window).reset_index()
    peak_windows.rename(columns={'hour': 'peak_window'}, inplace=True)
    hotspot_metrics = pd.merge(hotspot_metrics, peak_windows, on=['hotspot_id', 'is_discovered_cluster'])
    
    # Rename junctions for discovered clusters
    hotspot_metrics.loc[hotspot_metrics['is_discovered_cluster'], 'junction_name'] = hotspot_metrics.loc[hotspot_metrics['is_discovered_cluster'], 'hotspot_id'].apply(lambda x: f"Discovered Cluster #{x}")
    
    hotspot_metrics['impact_score'] = hotspot_metrics['violation_count'] * hotspot_metrics['avg_PIS']
    
    print(f"Detected {len(hotspot_metrics)} total hotspots (Named + Discovered).")
    return df_hotspots, hotspot_metrics

if __name__ == "__main__":
    file_path = "jan to may police violation_anonymized791b166.csv"
    df = load_and_clean_data(file_path)
    df = calculate_pis(df)
    df['dynamic_fine'] = df['PIS'].apply(calculate_dynamic_fine)
    df_hotspots, hotspot_metrics = detect_hotspots(df)
    hotspot_metrics.to_csv("hotspot_metrics.csv", index=False)
    df_hotspots.to_csv("processed_data.csv", index=False)
    print("Data processing complete. Saved to processed_data.csv and hotspot_metrics.csv")
