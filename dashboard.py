import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.express as px
import os
import joblib

# Set page config
st.set_page_config(page_title="ParkImpact AI", layout="wide", page_icon="🚗")

# Load data
@st.cache_data
def load_data():
    processed_path = 'processed_data.csv'
    hotspot_path = 'hotspot_metrics.csv'
    if os.path.exists(processed_path):
        df = pd.read_csv(processed_path, parse_dates=['created_datetime'])
    else:
        df = pd.DataFrame()
        
    if os.path.exists(hotspot_path):
        hotspot_df = pd.read_csv(hotspot_path)
    else:
        hotspot_df = pd.DataFrame()
        
    return df, hotspot_df

df, hotspot_df = load_data()

# Helper function to get model
@st.cache_resource
def get_model():
    if os.path.exists('model.pkl') and os.path.exists('preprocessing_pipeline.pkl'):
        return joblib.load('model.pkl'), joblib.load('preprocessing_pipeline.pkl')
    return None, None

model, le_dict = get_model()

# Sidebar Navigation
st.sidebar.title("ParkImpact AI")
page = st.sidebar.radio("Navigation", [
    "Executive Overview",
    "Violation Analytics",
    "Hotspot Detection Map",
    "Parking Impact Heatmap",
    "Dynamic Fine Calculator",
    "Violation Prediction",
    "Enforcement Recommendation"
])

if df.empty:
    st.warning("Processed data not found. Please run `hotspot.py` to process data.")
    st.stop()

# --- PAGE 1: Executive Overview ---
if page == "Executive Overview":
    st.title("🚗 Executive Overview")
    st.markdown("Overview of the ParkImpact AI system metrics.")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Violations", f"{len(df):,}")
    col2.metric("Total Hotspots", f"{len(hotspot_df):,}")
    
    high_impact = len(df[df['PIS_class'].isin(['High', 'Critical'])])
    col3.metric("High/Critical Impact Violations", f"{high_impact:,}")
    
    total_potential_fine = df['dynamic_fine'].sum()
    col4.metric("Potential Revenue", f"₹ {total_potential_fine:,.0f}")
    
    st.markdown("### Top Corridors (Junctions)")
    top_junctions = df['junction_name'].value_counts().head(5)
    st.table(top_junctions)

# --- PAGE 2: Violation Analytics ---
elif page == "Violation Analytics":
    st.title("📊 Violation Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Police Stations")
        top_ps = df['police_station'].value_counts().head(10).reset_index()
        top_ps.columns = ['Police Station', 'Count']
        fig = px.bar(top_ps, x='Police Station', y='Count', color='Count', color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("Vehicle Type Distribution")
        v_types = df['vehicle_type'].value_counts().reset_index()
        v_types.columns = ['Vehicle Type', 'Count']
        fig = px.pie(v_types, names='Vehicle Type', values='Count', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
        
    st.subheader("Hourly Trends")
    hourly = df.groupby('hour').size().reset_index(name='count')
    fig = px.line(hourly, x='hour', y='count', markers=True, title="Violations by Hour of Day")
    st.plotly_chart(fig, use_container_width=True)

# --- PAGE 3: Hotspot Detection Map ---
elif page == "Hotspot Detection Map":
    st.title("🗺️ Hotspot Detection Map")
    
    if not hotspot_df.empty:
        map_center = [hotspot_df['centroid_lat'].mean(), hotspot_df['centroid_lon'].mean()]
        m = folium.Map(location=map_center, zoom_start=11)
        
        for idx, row in hotspot_df.iterrows():
            folium.CircleMarker(
                location=[row['centroid_lat'], row['centroid_lon']],
                radius=min(row['violation_count'] / 50, 20) + 5,
                popup=f"Hotspot: {int(row['hotspot_id'])}<br>Violations: {int(row['violation_count'])}",
                color='crimson',
                fill=True,
                fillColor='crimson'
            ).add_to(m)
            
        st_data = st_folium(m, width=1000, height=500)
    else:
        st.write("No hotspot data available.")

# --- PAGE 4: Parking Impact Heatmap ---
elif page == "Parking Impact Heatmap":
    st.title("🔥 Parking Impact Heatmap")
    
    if not df.empty:
        # We sample data to avoid crashing the browser
        sample_df = df.sample(min(10000, len(df)))
        map_center = [sample_df['latitude'].mean(), sample_df['longitude'].mean()]
        m = folium.Map(location=map_center, zoom_start=11)
        
        heat_data = [[row['latitude'], row['longitude'], row['PIS']] for index, row in sample_df.iterrows()]
        HeatMap(heat_data, min_opacity=0.2, radius=15, blur=10).add_to(m)
        
        st_data = st_folium(m, width=1000, height=500)
    else:
        st.write("No data available.")

# --- PAGE 5: Dynamic Fine Calculator ---
elif page == "Dynamic Fine Calculator":
    st.title("💰 Dynamic Fine Calculator")
    
    st.markdown("Calculate the recommended fine based on violation parameters.")
    
    col1, col2 = st.columns(2)
    with col1:
        v_type = st.selectbox("Vehicle Type Weight", [("Truck/Lorry/HGV (3)", 3), ("Car/Auto (2)", 2), ("Bike/Scooter (1)", 1)], format_func=lambda x: x[0])
        v_viol = st.selectbox("Violation Weight", [("Double Parking (3.0)", 3.0), ("Main Road (2.5)", 2.5), ("No Parking (2.0)", 2.0), ("Wrong Parking (1.5)", 1.5)], format_func=lambda x: x[0])
    with col2:
        v_road = st.selectbox("Road Weight", [("Metro/Arterial (5)", 5), ("Commercial (4)", 4), ("Collector (3)", 3), ("Residential (1)", 1)], format_func=lambda x: x[0])
        v_hour = st.selectbox("Peak Hour Weight", [("Peak (6-9 AM or 5-9 PM) (1.5)", 1.5), ("Off-Peak (1.0)", 1.0)], format_func=lambda x: x[0])
        
    pis = v_type[1] * v_viol[1] * v_road[1] * v_hour[1]
    
    if pis < 15: fine = 500
    elif pis < 40: fine = 1000
    elif pis < 60: fine = 2000
    else: fine = 5000
    
    st.markdown(f"### Calculated PIS: **{pis:.2f}**")
    st.markdown(f"### Recommended Fine: **₹ {fine}**")

# --- PAGE 6: Violation Prediction ---
elif page == "Violation Prediction":
    st.title("🔮 Violation Prediction")
    
    if model is None:
        st.warning("Model not found. Run `train.py` to train the model.")
    else:
        st.markdown("Predict the expected violations for a given hour.")
        
        col1, col2 = st.columns(2)
        with col1:
            hotspot_id = st.number_input("Hotspot ID", min_value=0, value=1)
            hour = st.slider("Hour of Day", 0, 23, 12)
            day_of_week = st.slider("Day of Week (0=Mon, 6=Sun)", 0, 6, 0)
            month = st.slider("Month", 1, 12, 1)
        with col2:
            hist_count = st.number_input("Historical Violation Count", min_value=0, value=10)
            hist_pis = st.number_input("Historical Avg PIS", min_value=0.0, value=25.0)
            
            # Use raw strings as inputs if you want to use the pipeline properly
            police_station_names = le_dict['police_station'].classes_ if 'police_station' in le_dict else ['Unknown']
            junction_names = le_dict['junction_name'].classes_ if 'junction_name' in le_dict else ['Unknown']
            
            ps = st.selectbox("Police Station", police_station_names)
            jn = st.selectbox("Junction Name", junction_names)
            
        if st.button("Predict"):
            ps_enc = le_dict['police_station'].transform([ps])[0] if ps in le_dict['police_station'].classes_ else 0
            jn_enc = le_dict['junction_name'].transform([jn])[0] if jn in le_dict['junction_name'].classes_ else 0
            
            X_input = pd.DataFrame([{
                'hour': hour,
                'day_of_week': day_of_week,
                'month': month,
                'hotspot_id': hotspot_id,
                'police_station': ps_enc,
                'junction_name': jn_enc,
                'historical_violation_count': hist_count,
                'historical_PIS': hist_pis
            }])
            
            pred = model.predict(X_input)[0]
            pred = max(0, pred) # Ensure no negative
            
            st.success(f"Expected Violations: **{pred:.1f}**")
            
# --- PAGE 7: Enforcement Recommendation ---
elif page == "Enforcement Recommendation":
    st.title("🚨 Enforcement Recommendation")
    
    if hotspot_df.empty:
        st.warning("Hotspot data not available.")
    else:
        st.markdown("Top priority hotspots for immediate enforcement action.")
        
        # In a real scenario, this would use the predictive model for the NEXT hour.
        # For simplicity, we calculate a pseudo priority score from recent history.
        hotspot_df['Priority Score'] = hotspot_df['violation_count'] * hotspot_df['avg_PIS']
        top_hotspots = hotspot_df.sort_values(by='Priority Score', ascending=False).head(10)
        
        st.table(top_hotspots[['hotspot_id', 'centroid_lat', 'centroid_lon', 'violation_count', 'Priority Score']])
        
        st.markdown("### Deployment Plan")
        st.write("Deploy patrol units to the top hotspots listed above during peak hours (6-9 AM, 5-9 PM) for maximum impact.")
