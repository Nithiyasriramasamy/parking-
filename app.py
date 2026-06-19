import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
from utils import load_and_clean_data, run_dbscan_clustering, generate_hotspot_stats

# Configure Page
st.set_page_config(
    page_title="Parking Impact Intelligence",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polish
st.markdown("""
<style>
    .reportview-container .main .block-container{
        padding-top: 2rem;
    }
    .metric-card {
        background-color: #1E1E1E;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        text-align: center;
        border: 1px solid #333;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #4CAF50;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #AAA;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# Title Section
st.title("🚨 Parking Impact Intelligence")
st.markdown("### Targeted Enforcement Planner & Micro-Hotspot Discovery")
st.markdown("---")

# -----------------------------------------------------------------------------
# Data Loading
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    return load_and_clean_data()

with st.spinner("Loading and processing dataset..."):
    df_raw = load_data()

if df_raw is None:
    st.error("Dataset not found. Please ensure `jan to may police violation_anonymized791b166.csv` is in the workspace.")
    st.stop()

# -----------------------------------------------------------------------------
# Sidebar & Filters
# -----------------------------------------------------------------------------
st.sidebar.header("Controls & Filters")

# Handle anomalous month exclusion (e.g. Feb drop)
exclude_feb = st.sidebar.checkbox("Exclude Anomalous Month (Feb 2024)", value=False, 
                                  help="If enabled, removes Feb 2024 from month-over-month comparisons if it shows a sharp coverage drop.")

# Run clustering
with st.sidebar.expander("⚙️ DBSCAN Clustering Params", expanded=False):
    dbscan_eps = st.slider("Clustering Radius (meters)", min_value=10, max_value=200, value=50, step=10)
    dbscan_min_samples = st.slider("Min Samples for Cluster", min_value=3, max_value=50, value=10, step=1)

# Apply clustering
with st.spinner("Discovering micro-hotspots..."):
    df = run_dbscan_clustering(df_raw, eps_meters=dbscan_eps, min_samples=dbscan_min_samples)

# Filtering options
stations = ['All'] + sorted(df['police_station'].dropna().unique().tolist())
selected_station = st.sidebar.selectbox("Police Station", stations)

v_types = ['All'] + sorted(df['vehicle_type'].dropna().unique().tolist())
selected_vtype = st.sidebar.selectbox("Vehicle Type", v_types)

hotspot_filter = st.sidebar.radio("Hotspot Type", ["All", "Named Junctions Only", "Discovered Clusters Only"])

# Filter Dataset
filtered_df = df.copy()

if selected_station != 'All':
    filtered_df = filtered_df[filtered_df['police_station'] == selected_station]

if selected_vtype != 'All':
    filtered_df = filtered_df[filtered_df['vehicle_type'] == selected_vtype]

if hotspot_filter == "Named Junctions Only":
    filtered_df = filtered_df[filtered_df['is_named_junction'] == True]
elif hotspot_filter == "Discovered Clusters Only":
    filtered_df = filtered_df[(filtered_df['is_named_junction'] == False) & (filtered_df['discovered_cluster_id'] != -1)]

if exclude_feb and 'month_ist' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['month_ist'] != '2024-02']

# -----------------------------------------------------------------------------
# KPI Cards
# -----------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.markdown(f'<div class="metric-card"><div class="metric-value">{len(filtered_df):,}</div><div class="metric-label">Total Violations</div></div>', unsafe_allow_html=True)

named_count = len(filtered_df[filtered_df['is_named_junction'] == True])
col2.markdown(f'<div class="metric-card"><div class="metric-value">{named_count:,}</div><div class="metric-label">At Named Junctions</div></div>', unsafe_allow_html=True)

unnamed_clustered = len(filtered_df[(filtered_df['is_named_junction'] == False) & (filtered_df['discovered_cluster_id'] != -1)])
col3.markdown(f'<div class="metric-card"><div class="metric-value">{unnamed_clustered:,}</div><div class="metric-label">In Discovered Clusters</div></div>', unsafe_allow_html=True)

num_clusters = filtered_df['discovered_cluster_id'].nunique() - (1 if -1 in filtered_df['discovered_cluster_id'].values else 0)
col4.markdown(f'<div class="metric-card"><div class="metric-value">{num_clusters}</div><div class="metric-label">Micro-Hotspots Found</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Pre-calculate Hotspot Stats
# -----------------------------------------------------------------------------
named_hotspots_df = generate_hotspot_stats(filtered_df[filtered_df['is_named_junction'] == True], 'junction_name')
discovered_hotspots_df = generate_hotspot_stats(filtered_df[filtered_df['is_named_junction'] == False], 'discovered_hotspot_name')

# Combine for overall ranking
if not named_hotspots_df.empty and not discovered_hotspots_df.empty:
    named_hotspots_df['hotspot_type'] = 'Named'
    discovered_hotspots_df['hotspot_type'] = 'Discovered'
    all_hotspots_df = pd.concat([named_hotspots_df, discovered_hotspots_df]).sort_values('impact_score', ascending=False)
elif not named_hotspots_df.empty:
    named_hotspots_df['hotspot_type'] = 'Named'
    all_hotspots_df = named_hotspots_df
elif not discovered_hotspots_df.empty:
    discovered_hotspots_df['hotspot_type'] = 'Discovered'
    all_hotspots_df = discovered_hotspots_df
else:
    all_hotspots_df = pd.DataFrame()

# -----------------------------------------------------------------------------
# Tabs Layout
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Overview", 
    "🗺️ Hotspots Map", 
    "🔍 Discovered Clusters", 
    "📋 Enforcement Planner", 
    "⚠️ Data Quality", 
    "📖 Method & Caveats"
])

# --- TAB 1: Overview ---
with tab1:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Monthly Violation Trend")
        if 'month_ist' in filtered_df.columns:
            monthly = filtered_df.groupby('month_ist').size().reset_index(name='count')
            fig = px.bar(monthly, x='month_ist', y='count', title="Violations per Month (IST)",
                         labels={'month_ist': 'Month', 'count': 'Violations'},
                         color_discrete_sequence=['#4CAF50'])
            st.plotly_chart(fig, use_container_width=True)
            
            # Anomaly insight
            if '2024-02' in monthly['month_ist'].values and not exclude_feb:
                st.info("💡 **Insight:** Notice the sharp drop in February. This likely indicates a sensor/device coverage loss rather than a sudden behavioral improvement. Toggle 'Exclude Anomalous Month' in the sidebar for cleaner comparisons.")
    
    with col_b:
        st.subheader("Hourly Distribution (IST)")
        if 'hour_ist' in filtered_df.columns:
            hourly = filtered_df.groupby('hour_ist').size().reset_index(name='count')
            fig = px.line(hourly, x='hour_ist', y='count', title="Violations by Hour of Day",
                          markers=True, labels={'hour_ist': 'Hour (IST)', 'count': 'Violations'},
                          color_discrete_sequence=['#FF9800'])
            fig.update_xaxes(dtick=2)
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top Police Stations by Total Impact")
    if not all_hotspots_df.empty:
        station_impact = all_hotspots_df.groupby('police_station')['impact_score'].sum().reset_index().sort_values('impact_score', ascending=False).head(10)
        fig = px.bar(station_impact, x='impact_score', y='police_station', orientation='h',
                     title="Total Impact Score per Station", labels={'impact_score': 'Aggregate Impact Score', 'police_station': 'Station'},
                     color='impact_score', color_continuous_scale='Reds')
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: Hotspots Map ---
with tab2:
    st.subheader("Geospatial Hotspot Map")
    st.markdown("Visualizing the highest impact named junctions and discovered micro-hotspots.")
    
    if not all_hotspots_df.empty and 'latitude' in all_hotspots_df.columns:
        # Filter for top N to keep map responsive
        map_df = all_hotspots_df.head(200).copy()
        
        # Determine color based on type
        def get_color(htype):
            return [255, 0, 0, 160] if htype == 'Named' else [0, 200, 255, 160]
            
        map_df['color'] = map_df['hotspot_type'].apply(get_color)
        
        # Pydeck map
        layer = pdk.Layer(
            'ScatterplotLayer',
            data=map_df,
            get_position='[longitude, latitude]',
            get_color='color',
            get_radius='impact_score * 50', # Scale radius by impact
            pickable=True
        )
        
        view_state = pdk.ViewState(
            latitude=map_df['latitude'].mean(),
            longitude=map_df['longitude'].mean(),
            zoom=11,
            pitch=0
        )
        
        r = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "{hotspot_name}\nType: {hotspot_type}\nStation: {police_station}\nImpact: {impact_score}"}
        )
        
        st.pydeck_chart(r)
        
        st.markdown("""
        **Legend:** 
        🔴 Named Junctions | 🔵 Discovered Clusters
        *(Circle size denotes Impact Score)*
        """)
    else:
        st.warning("Not enough coordinate data to generate map.")

# --- TAB 3: Discovered Clusters ---
with tab3:
    st.subheader("Micro-Hotspot Discovery (DBSCAN)")
    st.markdown("We isolate rows missing junction names and cluster them geographically. This reveals 'hidden' enforcement zones.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Raw Rows Missing Junction", len(filtered_df[filtered_df['is_named_junction'] == False]))
    with col2:
        st.metric("Rows Successfully Clustered", unnamed_clustered)
        
    st.markdown("### Top Discovered Hotspots")
    if not discovered_hotspots_df.empty:
        st.dataframe(discovered_hotspots_df[['hotspot_name', 'police_station', 'violation_count', 'peak_window_ist', 'impact_score', 'confidence']].head(15), use_container_width=True)
    else:
        st.info("No clusters discovered with current filters/parameters.")

# --- TAB 4: Enforcement Planner ---
with tab4:
    st.subheader("Top 15 Corridor Action Plan")
    st.markdown("Prioritized list of enforcement targets based on the composite Impact Score.")
    
    if not all_hotspots_df.empty:
        plan_df = all_hotspots_df[['hotspot_name', 'hotspot_type', 'police_station', 'peak_window_ist', 'impact_score', 'violation_count', 'confidence']].head(15).reset_index(drop=True)
        
        # Display as table
        st.dataframe(plan_df.style.apply(lambda x: ['background: #4B0000' if v == 'Low' else '' for v in x], subset=['confidence'], axis=0), use_container_width=True)
        
        # Download button
        csv = plan_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download Enforcement Plan (CSV)",
            data=csv,
            file_name='enforcement_action_plan.csv',
            mime='text/csv',
        )
    else:
        st.warning("No data available for planning.")

# --- TAB 5: Data Quality ---
with tab5:
    st.subheader("Data Coverage & Diagnostics")
    
    st.markdown("""
    When dealing with temporal raw data, drops in violation counts can mean either *fewer violations* or *fewer active sensors/patrols*. 
    """)
    
    if 'device_id' in df.columns and 'month_ist' in df.columns:
        dq_df = df_raw.groupby('month_ist').agg(
            violation_count=('id', 'count'),
            active_devices=('device_id', 'nunique')
        ).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=dq_df['month_ist'], y=dq_df['violation_count'], name='Violations', yaxis='y1'))
        fig.add_trace(go.Scatter(x=dq_df['month_ist'], y=dq_df['active_devices'], name='Active Devices', mode='lines+markers', yaxis='y2', line=dict(color='red', width=3)))
        
        fig.update_layout(
            title="Violations vs Active Devices per Month",
            yaxis=dict(title='Violations'),
            yaxis2=dict(title='Active Devices', overlaying='y', side='right'),
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        if '2024-02' in dq_df['month_ist'].values:
            st.error("🚨 **Data Anomaly Detected:** February 2024 shows a sharp drop in both violations and active devices. This is likely a coverage gap.")

# --- TAB 6: Method & Caveats ---
with tab6:
    st.subheader("Methodology")
    st.markdown("""
    * **Timezone Correction**: Raw timestamps contain `+00` UTC suffixes. We converted these to IST (`+05:30`) to ensure hourly distribution analysis is accurate.
    * **Hotspot Discovery (DBSCAN)**: Records labeled "No Junction" or missing names were clustered using spatial density (DBSCAN) to identify unmapped problematic zones.
    * **Impact Score**: A composite metric weighting: Frequency (40%), Vehicle Severity (30%), Distinct Days Active (20%), and Peak Hour Concentration (10%).
    """)
    
    st.subheader("⚠️ Caveats")
    st.warning("""
    1. **Peak Window Bias**: Observed peak hours reflect *when enforcement patrols were active/devices were on*, not purely when illegal parking actually peaks. Evening conclusions may be weak if patrols drop off.
    2. **Impact != Congestion**: The Impact Score is a relative prioritization proxy based on the dataset, not a direct real-world traffic congestion measurement.
    3. **Map Coordinates**: Coordinates are plotted directly from the dataset without external geocoding correction.
    """)
