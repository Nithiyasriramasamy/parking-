import pandas as st_pandas
import pandas as pd
import streamlit as st
import os

@st.cache_data
def load_processed_data():
    """
    Load the processed violation dataset.
    Uses caching to avoid reloading the large CSV on every page interaction.
    """
    # Assuming the app is run from the root of the project
    data_path = 'processed_data.csv'
    
    if not os.path.exists(data_path):
        st.error(f"Data file not found at {data_path}. Please ensure the processed_data.csv exists.")
        return pd.DataFrame()
        
    df = pd.read_csv(data_path, low_memory=False)
    
    # Ensure datetime parsing if not already done
    if 'created_datetime' in df.columns:
        df['created_datetime'] = pd.to_datetime(df['created_datetime'], errors='coerce')
        
    # Calculate some additional metrics for the dashboard if not present
    if 'capacity_loss_pct' not in df.columns and 'disruption_index' in df.columns:
        # Mocking a road capacity loss percentage based on disruption index (max 100%)
        df['capacity_loss_pct'] = (df['disruption_index'] / df['disruption_index'].max()) * 100
        
    if 'predicted_delay_min' not in df.columns and 'disruption_index' in df.columns:
        # Mocking predicted delay in minutes
        df['predicted_delay_min'] = (df['disruption_index'] / 10).round(1)
        
    return df

@st.cache_data
def get_hotspot_summary(df):
    """
    Generates a grouped summary of hotspots.
    """
    if df.empty:
        return pd.DataFrame()
        
    summary = df.groupby(['junction_name', 'police_station']).agg(
        violation_count=('id', 'count'),
        avg_impact_score=('disruption_index', 'mean'),
        total_impact=('disruption_index', 'sum'),
        avg_capacity_loss=('capacity_loss_pct', 'mean'),
        top_vehicle=('vehicle_type', lambda x: x.mode()[0] if not x.empty else 'Unknown'),
        latitude=('latitude', 'mean'),
        longitude=('longitude', 'mean')
    ).reset_index()
    
    summary = summary.sort_values(by='total_impact', ascending=False)
    
    # Generate Priority ranking based on impact
    summary['priority'] = pd.qcut(summary['total_impact'], q=4, labels=['Low', 'Medium', 'High', 'Critical'])
    
    return summary
