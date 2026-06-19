import pandas as pd
import numpy as np
import streamlit as st
from sklearn.cluster import DBSCAN
from pathlib import Path
import json

DATA_FILE = "jan to may police violation_anonymized791b166.csv"

VEHICLE_WEIGHTS = {
    "SCOOTER": 1.0,
    "MOTORCYCLE": 1.0,
    "TWO WHEELER": 1.0,
    "CAR": 3.0,
    "AUTO": 3.0,
    "AUTO RICKSHAW": 3.0,
    "MAXI-CAB": 5.0,
    "VAN": 5.0,
    "GOODS VEHICLE": 5.0,
    "BUS": 5.0,
    "TRUCK": 5.0,
    "LMV": 4.0,
    "HTV": 5.0,
    "HMV": 5.0,
}

@st.cache_data
def load_and_clean_data(file_path=DATA_FILE):
    """
    Loads data, corrects timezones, and cleans column strings.
    """
    # Look for the file in the current directory
    if not Path(file_path).exists():
        # graceful error message in streamlit later if df is None
        return None

    # Load a sample first to check columns, or load full
    df = pd.read_csv(file_path)
    
    # Clean column names just in case
    df.columns = [str(c).strip().lower() for c in df.columns]
    
    # 1. Parse dates and convert UTC to IST
    # created_datetime looks like: '2023-11-20 00:28:46+00'
    if 'created_datetime' in df.columns:
        # It's given as +00 UTC, parse and convert
        df['datetime_utc'] = pd.to_datetime(df['created_datetime'], errors='coerce')
        # Convert to IST (+5:30)
        df['datetime_ist'] = df['datetime_utc'] + pd.Timedelta(hours=5, minutes=30)
        
        # Extract features
        df['date_ist'] = df['datetime_ist'].dt.date
        df['hour_ist'] = df['datetime_ist'].dt.hour
        df['weekday_ist'] = df['datetime_ist'].dt.day_name()
        df['month_ist'] = df['datetime_ist'].dt.to_period('M').astype(str)
    
    # 2. Vehicle Severity Weight
    if 'vehicle_type' in df.columns:
        df['vehicle_type'] = df['vehicle_type'].fillna('UNKNOWN').astype(str).str.upper().str.strip()
        df['vehicle_severity'] = df['vehicle_type'].map(VEHICLE_WEIGHTS).fillna(2.0) # default weight 2.0
    else:
        df['vehicle_severity'] = 1.0

    # 3. Clean Junction Name
    if 'junction_name' in df.columns:
        df['junction_name'] = df['junction_name'].fillna('Missing').astype(str).str.strip()
        df['is_named_junction'] = ~df['junction_name'].str.lower().isin(['no junction', 'missing', 'null', 'nan', ''])
    else:
        df['junction_name'] = 'Missing'
        df['is_named_junction'] = False

    # 4. Clean Police Station
    if 'police_station' in df.columns:
        df['police_station'] = df['police_station'].fillna('Unknown').astype(str).str.title().str.strip()
        
    # Validation filters - drop null lat/lon for spatial work
    if 'latitude' in df.columns and 'longitude' in df.columns:
        # Ensure numeric
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    
    return df

@st.cache_data
def run_dbscan_clustering(df, eps_meters=50, min_samples=10):
    """
    Runs DBSCAN on records with NO junction to discover micro-hotspots.
    eps in meters is roughly converted to degrees (1 deg ~ 111km)
    """
    # Filter rows with coordinates and without a named junction
    mask = df['latitude'].notnull() & df['longitude'].notnull() & (~df['is_named_junction'])
    cluster_df = df[mask].copy()
    
    if len(cluster_df) == 0:
        df['discovered_cluster_id'] = -1
        return df
        
    coords = cluster_df[['latitude', 'longitude']].values
    
    # eps conversion: roughly 111,111 meters per degree of latitude
    eps_deg = eps_meters / 111111.0 
    
    # Haversine metric would be better but requires radians. Let's use simple euclidean on degrees for speed,
    # as Bangalore's latitude doesn't cause huge distortion for small eps.
    db = DBSCAN(eps=eps_deg, min_samples=min_samples, metric='euclidean').fit(coords)
    
    cluster_df['discovered_cluster_id'] = db.labels_
    
    # Merge back
    df = df.join(cluster_df[['discovered_cluster_id']], how='left')
    df['discovered_cluster_id'] = df['discovered_cluster_id'].fillna(-1).astype(int)
    
    # Generate names for clusters
    cluster_centers = cluster_df[cluster_df['discovered_cluster_id'] != -1].groupby('discovered_cluster_id')[['latitude', 'longitude']].mean()
    
    def get_cluster_name(row):
        cid = row['discovered_cluster_id']
        if cid == -1:
            return 'Noise / Unclustered'
        # Get approx lat/lon center to 4 decimals
        if cid in cluster_centers.index:
            lat = cluster_centers.loc[cid, 'latitude']
            lon = cluster_centers.loc[cid, 'longitude']
            return f"Discovered Hotspot {cid} ({lat:.4f}, {lon:.4f})"
        return f"Discovered Hotspot {cid}"
        
    df['discovered_hotspot_name'] = df.apply(get_cluster_name, axis=1)
    
    return df

def calculate_impact_score(df_agg):
    """
    Given an aggregated dataframe of hotspots (count, severity, distinct_days, peak_ratio),
    computes an impact score.
    """
    # Normalizing components
    if len(df_agg) == 0:
        df_agg['impact_score'] = 0
        return df_agg
        
    max_count = df_agg['violation_count'].max() or 1
    max_sev = df_agg['avg_severity'].max() or 1
    max_days = df_agg['distinct_days'].max() or 1
    
    # 40% volume, 30% severity, 20% persistence (days), 10% peak concentration
    freq_comp = (df_agg['violation_count'] / max_count) * 40
    sev_comp = (df_agg['avg_severity'] / max_sev) * 30
    day_comp = (df_agg['distinct_days'] / max_days) * 20
    peak_comp = df_agg['peak_ratio'] * 10 # already 0-1
    
    df_agg['impact_score'] = np.round(freq_comp + sev_comp + day_comp + peak_comp, 1)
    
    # Confidence flag
    # Low confidence if low sample count or very few distinct days
    df_agg['confidence'] = np.where((df_agg['violation_count'] < 10) | (df_agg['distinct_days'] < 3), 'Low', 'High')
    
    return df_agg

@st.cache_data
def generate_hotspot_stats(df, group_by_col='junction_name'):
    """
    Aggregates data into hotspot metrics.
    """
    if group_by_col not in df.columns:
        return pd.DataFrame()
        
    # Remove noise if grouping by discovered cluster
    if group_by_col == 'discovered_hotspot_name':
        df = df[df['discovered_cluster_id'] != -1]
        
    if len(df) == 0:
        return pd.DataFrame()
        
    # Basic aggregation
    agg_funcs = {
        'id': 'count',
        'vehicle_severity': 'mean',
        'date_ist': 'nunique',
        'hour_ist': lambda x: x.value_counts().idxmax() if not x.empty else -1, # Peak hour
        'police_station': lambda x: x.mode()[0] if not x.empty else 'Unknown',
        'latitude': 'mean',
        'longitude': 'mean'
    }
    
    # Compute total volume for peak ratio
    def peak_ratio(x):
        if len(x) == 0: return 0
        vc = x.value_counts()
        return vc.max() / len(x)
        
    agg_funcs_ext = agg_funcs.copy()
    agg_funcs_ext['peak_ratio'] = ('hour_ist', peak_ratio)
    
    # We do a custom groupby to get all pieces
    grouped = df.groupby(group_by_col)
    
    res = grouped.agg(
        violation_count=('id', 'count'),
        avg_severity=('vehicle_severity', 'mean'),
        distinct_days=('date_ist', 'nunique'),
        peak_hour=('hour_ist', lambda x: x.value_counts().index[0] if len(x.value_counts()) > 0 else -1),
        peak_ratio=('hour_ist', peak_ratio),
        police_station=('police_station', lambda x: x.mode()[0] if len(x) > 0 else 'Unknown'),
        latitude=('latitude', 'mean'),
        longitude=('longitude', 'mean')
    ).reset_index()
    
    # Rename grouping column for standard output
    res.rename(columns={group_by_col: 'hotspot_name'}, inplace=True)
    
    # Calculate Impact Score
    res = calculate_impact_score(res)
    
    # Format peak window
    def format_window(h):
        if pd.isna(h) or h == -1: return "Unknown"
        h = int(h)
        return f"{h:02d}:00 - {(h+2)%24:02d}:00"
        
    res['peak_window_ist'] = res['peak_hour'].apply(format_window)
    
    return res.sort_values('impact_score', ascending=False).reset_index(drop=True)
