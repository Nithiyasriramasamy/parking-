import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import os
import joblib

# Set page config
st.set_page_config(page_title="ParkImpact AI", layout="wide", page_icon="🚗", initial_sidebar_state="expanded")

# Custom CSS for Premium Glassmorphism Look
st.markdown("""
<style>
    .reportview-container .main .block-container{
        padding-top: 1.5rem;
    }
    .metric-card {
        background: rgba(30, 30, 46, 0.8);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
        text-align: center;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    .metric-icon {
        font-size: 2.5rem;
        margin-bottom: 10px;
    }
    .metric-title {
        font-size: 1rem;
        color: #A0A0B0;
        margin-bottom: 5px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #FFFFFF;
    }
    .fine-card {
        background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%);
        border-radius: 16px;
        padding: 30px;
        text-align: center;
        color: white;
        box-shadow: 0 10px 25px rgba(255, 75, 43, 0.4);
        margin-top: 20px;
    }
    .fine-card-title {
        font-size: 1.2rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        opacity: 0.9;
    }
    .fine-card-value {
        font-size: 4rem;
        font-weight: 900;
        margin: 10px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .action-card {
        background: rgba(46, 204, 113, 0.15);
        border-left: 5px solid #2ECC71;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 25px;
    }
    .action-title {
        color: #2ECC71;
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    /* Tier styling */
    .tier-1 { background-color: rgba(231, 76, 60, 0.2); border-left: 4px solid #E74C3C; padding: 5px 10px; border-radius: 4px; font-weight: bold; color: #E74C3C; }
    .tier-2 { background-color: rgba(241, 196, 15, 0.2); border-left: 4px solid #F1C40F; padding: 5px 10px; border-radius: 4px; font-weight: bold; color: #F1C40F; }
    .tier-3 { background-color: rgba(52, 152, 219, 0.2); border-left: 4px solid #3498DB; padding: 5px 10px; border-radius: 4px; font-weight: bold; color: #3498DB; }
</style>
""", unsafe_allow_html=True)

# Helper function to render metric cards
def render_metric_card(title, value, icon):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

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
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2909/2909633.png", width=60)
st.sidebar.title("ParkImpact AI")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", [
    "📊 Executive Overview",
    "📈 Violation Analytics",
    "🗺️ Hotspot Detection Map",
    "🔥 Parking Impact Heatmap",
    "💰 Dynamic Fine Calculator",
    "🎯 Strategic Enforcement Planner",
    "🔮 Violation Prediction"
])
st.sidebar.markdown("---")
st.sidebar.info("Prototype built for congestion-aware enforcement prioritizing high-impact corridors.")

if df.empty:
    st.warning("Processed data not found. Please run `hotspot.py` to process data.")
    st.stop()

# Plotly Theme
plotly_template = "plotly_dark"

# --- PAGE 1: Executive Overview ---
if page == "📊 Executive Overview":
    st.title("🚗 Executive Overview")
    st.markdown("Overview of the ParkImpact AI system metrics, focusing on the split between predefined named junctions and newly discovered micro-hotspots.")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card("Total Violations", f"{len(df):,}", "📋")
        
    if 'is_discovered_cluster' in hotspot_df.columns:
        named_hotspots = hotspot_df[~hotspot_df['is_discovered_cluster']]
        discovered_hotspots = hotspot_df[hotspot_df['is_discovered_cluster']]
        
        with col2:
            render_metric_card("Named Junctions", f"{len(named_hotspots):,}", "🚥")
        with col3:
            render_metric_card("Discovered Hotspots", f"{len(discovered_hotspots):,}", "🔍")
    else:
        with col2:
            render_metric_card("Total Hotspots", f"{len(hotspot_df):,}", "🗺️")
        with col3:
            render_metric_card("Discovered Hotspots", "N/A", "🔍")
            
    high_impact = len(df[df['PIS_class'].isin(['High', 'Critical'])])
    with col4:
        render_metric_card("High/Critical Impact", f"{high_impact:,}", "⚠️")
        
    st.markdown("---")
    
    # Bottom section with charts
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.markdown("### Hotspot Composition")
        if 'is_discovered_cluster' in hotspot_df.columns:
            composition_data = pd.DataFrame({
                'Type': ['Named Junctions (53%)', 'Discovered Hotspots (47%)'],
                'Count': [len(named_hotspots), len(discovered_hotspots)]
            })
            fig_donut = px.pie(composition_data, names='Type', values='Count', hole=0.6, 
                               color_discrete_sequence=['#E74C3C', '#3498DB'], template=plotly_template)
            fig_donut.update_traces(textposition='inside', textinfo='percent+label')
            fig_donut.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_donut, use_container_width=True)
    
    with c2:
        st.markdown("### Top Stations by Impact Score")
        if 'impact_score' in hotspot_df.columns:
            station_impact = hotspot_df.groupby('police_station')['impact_score'].sum().sort_values(ascending=False).head(5).reset_index()
            fig = px.bar(station_impact, x='impact_score', y='police_station', text='impact_score', 
                         orientation='h', template=plotly_template, color='impact_score', 
                         color_continuous_scale='Reds')
            fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("Impact score not found. Please rerun hotspot data generation.")

# --- PAGE 2: Violation Analytics ---
elif page == "📈 Violation Analytics":
    st.title("📈 Violation Analytics")
    
    exclude_feb = st.toggle("Exclude February Data (Coverage Anomaly)", value=True)
    plot_df = df[df['is_feb_anomaly'] == False] if exclude_feb and 'is_feb_anomaly' in df.columns else df
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Police Stations")
        top_ps = plot_df['police_station'].value_counts().head(10).reset_index()
        top_ps.columns = ['Police Station', 'Count']
        fig = px.bar(top_ps, x='Police Station', y='Count', color='Count', color_continuous_scale='Blues', template=plotly_template)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("Vehicle Type Distribution")
        v_types = plot_df['vehicle_type'].value_counts().reset_index()
        v_types.columns = ['Vehicle Type', 'Count']
        fig = px.pie(v_types, names='Vehicle Type', values='Count', hole=0.5, template=plotly_template)
        st.plotly_chart(fig, use_container_width=True)
        
    st.subheader("Hourly Trends (IST Corrected)")
    hourly = plot_df.groupby('hour').size().reset_index(name='count')
    fig = px.area(hourly, x='hour', y='count', markers=True, title="Violations by Hour of Day", template=plotly_template, color_discrete_sequence=['#9B59B6'])
    st.plotly_chart(fig, use_container_width=True)

# --- PAGE 3: Hotspot Detection Map ---
elif page == "🗺️ Hotspot Detection Map":
    st.title("🗺️ Hotspot Detection Map")
    st.markdown("Red markers represent **Predefined Junctions**, while Blue markers represent **Discovered Micro-Hotspots** (hidden prior to DBSCAN clustering).")
    
    if not hotspot_df.empty:
        map_center = [hotspot_df['centroid_lat'].mean(), hotspot_df['centroid_lon'].mean()]
        m = folium.Map(location=map_center, zoom_start=12, tiles="CartoDB dark_matter")
        
        for idx, row in hotspot_df.iterrows():
            is_discovered = row.get('is_discovered_cluster', False)
            color = '#3498DB' if is_discovered else '#E74C3C' 
            
            folium.CircleMarker(
                location=[row['centroid_lat'], row['centroid_lon']],
                radius=min(row['violation_count'] / 50, 15) + 5,
                popup=f"<div style='font-family:sans-serif; width:200px;'><b>Junction:</b> {row['junction_name']}<br><b>Violations:</b> {row['violation_count']}<br><b>Impact Score:</b> {row.get('impact_score', 0):.0f}<br><b>Peak Window:</b> {row.get('peak_window', 'N/A')}</div>",
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7
            ).add_to(m)
            
        st_data = st_folium(m, width="100%", height=600)
    else:
        st.write("No hotspot data available.")

# --- PAGE 4: Parking Impact Heatmap ---
elif page == "🔥 Parking Impact Heatmap":
    st.title("🔥 Parking Impact Heatmap")
    
    if not df.empty:
        sample_df = df.sample(min(10000, len(df)))
        map_center = [sample_df['latitude'].mean(), sample_df['longitude'].mean()]
        m = folium.Map(location=map_center, zoom_start=12, tiles="CartoDB dark_matter")
        
        heat_data = [[row['latitude'], row['longitude'], row['PIS']] for index, row in sample_df.iterrows()]
        HeatMap(heat_data, min_opacity=0.2, radius=15, blur=10, gradient={0.2:'blue', 0.4:'cyan', 0.6:'lime', 0.8:'yellow', 1.0:'red'}).add_to(m)
        
        st_data = st_folium(m, width="100%", height=600)
    else:
        st.write("No data available.")

# --- PAGE 5: Dynamic Fine Calculator ---
elif page == "💰 Dynamic Fine Calculator":
    st.title("💰 Dynamic Fine Calculator")
    st.markdown("Calculate the recommended fine based on violation severity, road type, and peak hours.")
    
    col_input, col_output = st.columns([1, 1.2])
    
    with col_input:
        st.markdown("### 🎛️ Parameters")
        v_type = st.selectbox("Vehicle Type Weight", [("Truck/Lorry/HGV (3)", 3), ("Car/Auto (2)", 2), ("Bike/Scooter (1)", 1)], format_func=lambda x: x[0])
        v_viol = st.selectbox("Violation Weight", [("Double Parking (3.0)", 3.0), ("Main Road (2.5)", 2.5), ("No Parking (2.0)", 2.0), ("Wrong Parking (1.5)", 1.5)], format_func=lambda x: x[0])
        v_road = st.selectbox("Road Weight", [("Metro/Arterial (5)", 5), ("Commercial (4)", 4), ("Collector (3)", 3), ("Residential (1)", 1)], format_func=lambda x: x[0])
        v_hour = st.selectbox("Peak Hour Weight", [("Peak (8-11 AM or 5-9 PM) (1.5)", 1.5), ("Off-Peak (1.0)", 1.0)], format_func=lambda x: x[0])
        
    pis = v_type[1] * v_viol[1] * v_road[1] * v_hour[1]
    
    if pis < 15: fine, color = 500, "#2ECC71"
    elif pis < 40: fine, color = 1000, "#F1C40F"
    elif pis < 60: fine, color = 2000, "#E67E22"
    else: fine, color = 5000, "#E74C3C"
    
    with col_output:
        st.markdown("### 📊 Calculated Impact")
        # Plotly Gauge Chart for PIS
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = pis,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Parking Impact Score (PIS)"},
            gauge = {
                'axis': {'range': [None, 70]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 15], 'color': "rgba(46, 204, 113, 0.2)"},
                    {'range': [15, 40], 'color': "rgba(241, 196, 15, 0.2)"},
                    {'range': [40, 60], 'color': "rgba(230, 126, 34, 0.2)"},
                    {'range': [60, 70], 'color': "rgba(231, 76, 60, 0.2)"}],
            }
        ))
        fig.update_layout(template=plotly_template, height=300, margin=dict(t=50, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
        
        # Giant styled HTML card for the fine
        st.markdown(f"""
        <div class="fine-card">
            <div class="fine-card-title">Recommended Dynamic Fine</div>
            <div class="fine-card-value">₹ {fine:,}</div>
        </div>
        """, unsafe_allow_html=True)

# --- PAGE 6: Strategic Enforcement Planner ---
elif page == "🎯 Strategic Enforcement Planner":
    st.title("🎯 Strategic Enforcement Planner")
    st.markdown("Allocates towing and patrol resources using a greedy planner approach based on the calculated Impact Score. Prioritizes corridors where interventions yield the highest impact return.")
    
    if hotspot_df.empty or 'impact_score' not in hotspot_df.columns:
        st.warning("Hotspot impact data not available. Please regenerate hotspot data.")
    else:
        # Action Card for Pilot
        st.markdown("""
        <div class="action-card">
            <div class="action-title">🏆 OFFICIAL PILOT RECOMMENDATION: UPPARPET</div>
            <div>Upparpet holds the highest combined impact score and several top corridors, making it the clearest candidate for an initial rollout. Proceed with deploying Tier 1 patrols in this jurisdiction immediately.</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Rank corridors
        top_corridors = hotspot_df.sort_values(by='impact_score', ascending=False).head(15).copy()
        
        # Add styled Tier logic
        top_corridors['Tier'] = '<span class="tier-3">Tier 3 (Monitor)</span>'
        if len(top_corridors) > 0:
            top_corridors.iloc[:5, top_corridors.columns.get_loc('Tier')] = '<span class="tier-1">Tier 1 (Immediate)</span>'
        if len(top_corridors) > 5:
            top_corridors.iloc[5:10, top_corridors.columns.get_loc('Tier')] = '<span class="tier-2">Tier 2 (Scheduled)</span>'
            
        top_corridors['Type'] = top_corridors['is_discovered_cluster'].map({True: '🔍 Discovered', False: '🚥 Named Junction'})
        
        st.subheader("🚨 Top 15 Ranked Corridors (Greedy Allocation)")
        
        # Render as HTML table for rendering CSS badges
        html_table = "<table style='width:100%; text-align:left; border-collapse: collapse;'>"
        html_table += "<tr style='border-bottom: 2px solid #555;'><th style='padding: 10px;'>Tier</th><th>Corridor / Junction</th><th>Station</th><th>Peak Window (IST)</th><th>Type</th><th>Impact Score</th></tr>"
        
        for _, row in top_corridors.iterrows():
            html_table += f"<tr style='border-bottom: 1px solid #333;'>"
            html_table += f"<td style='padding: 15px 10px;'>{row['Tier']}</td>"
            html_table += f"<td><b>{row['junction_name']}</b></td>"
            html_table += f"<td>{row['police_station']}</td>"
            html_table += f"<td>{row.get('peak_window', 'N/A')}</td>"
            html_table += f"<td>{row['Type']}</td>"
            html_table += f"<td style='color: #FF4B4B; font-weight: bold;'>{row['impact_score']:,.0f}</td>"
            html_table += "</tr>"
            
        html_table += "</table>"
        st.markdown(html_table, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("💡 **Note on Peak Windows**: The observed 'peak windows' partly reflect when patrols and devices were active. Evening peaks are currently under-represented due to operational coverage gaps in the data.")

# --- PAGE 7: Violation Prediction ---
elif page == "🔮 Violation Prediction":
    st.title("🔮 Violation Prediction")
    
    if model is None:
        st.warning("Model not found. Run `train.py` to train the model.")
    else:
        st.markdown("Predict expected violations for a given hour.")
        
        col1, col2 = st.columns(2)
        with col1:
            hotspot_id = st.number_input("Hotspot ID", min_value=0, value=1)
            hour = st.slider("Hour of Day (IST)", 0, 23, 10)
            day_of_week = st.slider("Day of Week (0=Mon, 6=Sun)", 0, 6, 0)
            month = st.slider("Month", 1, 12, 1)
        with col2:
            hist_count = st.number_input("Historical Violation Count", min_value=0, value=10)
            hist_pis = st.number_input("Historical Avg PIS", min_value=0.0, value=25.0)
            
            police_station_names = le_dict['police_station'].classes_ if 'police_station' in le_dict else ['Unknown']
            junction_names = le_dict['junction_name'].classes_ if 'junction_name' in le_dict else ['Unknown']
            
            ps = st.selectbox("Police Station", police_station_names)
            jn = st.selectbox("Junction Name", junction_names)
            
        if st.button("Predict Expected Violations", type="primary"):
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
            pred = max(0, pred) 
            
            # Action card for prediction
            st.markdown(f"""
            <div style="background: rgba(52, 152, 219, 0.15); border-left: 5px solid #3498DB; padding: 20px; border-radius: 8px; margin-top: 20px;">
                <div style="color: #3498DB; font-size: 1.1rem; font-weight: bold; margin-bottom: 5px;">MODEL PREDICTION</div>
                <div style="font-size: 2rem; color: white;">Expected Violations: <b>{pred:.1f}</b></div>
            </div>
            """, unsafe_allow_html=True)
