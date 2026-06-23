import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import pandas as pd
import numpy as np
from frontend.utils.ui_helpers import create_kpi_card, create_parking_heatmap, create_action_plan_card

st.title("🗺️ Active Threat Heatmap")
st.markdown("<p style='color:#94a3b8; font-size: 1.1rem;'>Live spatial clustering of illegal parking hotspots causing critical traffic disruption.</p>", unsafe_allow_html=True)

# 1. Officer KPI Cards
st.markdown("### 🚦 Live Situation Report")
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(create_kpi_card("Active Hotspots", "12", "Zones", "🔥", "#ef4444"), unsafe_allow_html=True)
with c2: st.markdown(create_kpi_card("Highest Risk", "Silk Board", "Junction", "⚠️", "#F59E0B"), unsafe_allow_html=True)
with c3: st.markdown(create_kpi_card("Required Tows", "5", "Trucks", "🛻", "#38BDF8"), unsafe_allow_html=True)
with c4: st.markdown(create_kpi_card("Disruption Level", "SEVERE", "", "📉", "#ef4444"), unsafe_allow_html=True)

st.markdown("<hr style='border-color: rgba(56, 189, 248, 0.2);'>", unsafe_allow_html=True)

# 2. Main Layout (Map + Sidebar)
col_map, col_intel = st.columns([2.5, 1.2])

with col_map:
    # Time Filter
    st.markdown("### 🧭 Tactical Map View")
    time_filter = st.selectbox("Select Time Context:", ["Current Live View", "Morning Peak (08:00 - 11:00)", "Evening Peak (17:00 - 20:00)"])
    
    # Generate Map Data & Narrative based on filter
    if time_filter == "Morning Peak (08:00 - 11:00)":
        narrative = "During **Morning Peak (08:00 - 11:00)**, parking violations are **extremely heavy** around **KR Puram Market** and **Indiranagar**, causing up to a 60% reduction in traffic flow for office commuters."
        lats = np.random.normal(12.9716, 0.08, 400)
        lons = np.random.normal(77.5946, 0.08, 400)
    elif time_filter == "Evening Peak (17:00 - 20:00)":
        narrative = "During **Evening Peak (17:00 - 20:00)**, illegal parking heavily chokes **Silk Board Junction** and **HSR Layout**. This is severely restricting outbound IT corridor traffic."
        lats = np.random.normal(12.9279, 0.04, 600) # Shifted towards Silk Board
        lons = np.random.normal(77.6271, 0.04, 600)
    else:
        narrative = "Right now in the **Current Live View**, there is a sudden spike in illegal parking at **MG Road Metro Station**. Immediate enforcement is required to prevent a gridlock."
        lats = np.random.normal(12.9716, 0.05, 300)
        lons = np.random.normal(77.5946, 0.05, 300)
        
    st.info(f"🤖 **AI Executive Summary:** {narrative}")
        
    df = pd.DataFrame({'latitude': lats, 'longitude': lons, 'disruption_index': np.random.uniform(5, 10, len(lats))})
    
    fig = create_parking_heatmap(df, lat_col='latitude', lon_col='longitude', z_col='disruption_index')
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

with col_intel:
    st.markdown("### 📖 How to Read This Map")
    st.info("""
    **What am I looking at?**
    This map uses AI to detect clusters of illegally parked vehicles. 
    
    **What do the colors mean?**
    - 🟥 **Dark Red Zones:** Critical! Parking here is reducing traffic flow by >60%.
    - 🟧 **Orange Zones:** Warning. Traffic speed is dropping rapidly.
    
    **What should I do?**
    Focus all towing and enforcement resources on the Dark Red zones first.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("### 🚔 Automated Dispatch Intel")
    if time_filter == "Evening Peak (17:00 - 20:00)":
        st.markdown(create_action_plan_card("Silk Board Junction: Critical congestion. Dispatch 3 Tow Trucks.", "PRIORITY 1", "🚨", "#ef4444"), unsafe_allow_html=True)
        st.markdown(create_action_plan_card("HSR Layout Sector 2: Moderate blockage. Dispatch 1 Patrol Bike.", "PRIORITY 2", "🏍️", "#F59E0B"), unsafe_allow_html=True)
    elif time_filter == "Morning Peak (08:00 - 11:00)":
        st.markdown(create_action_plan_card("KR Puram Market: Gridlock forming. Dispatch 2 Tow Trucks.", "PRIORITY 1", "🚨", "#ef4444"), unsafe_allow_html=True)
        st.markdown(create_action_plan_card("Indiranagar 100ft: Illegal double parking. Send Warning SMS blast.", "PRIORITY 2", "📱", "#F59E0B"), unsafe_allow_html=True)
    else:
        st.markdown(create_action_plan_card("MG Road Metro: Live bottleneck detected. Dispatch 2 Tow Trucks.", "PRIORITY 1", "🚨", "#ef4444"), unsafe_allow_html=True)
        st.markdown(create_action_plan_card("Koramangala 80ft: Flow restricted. Dispatch 1 Patrol Bike.", "PRIORITY 2", "🏍️", "#F59E0B"), unsafe_allow_html=True)
        st.markdown(create_action_plan_card("Brigade Road: Low risk. Proceed with standard automated E-Challans.", "MONITORING", "👁️", "#38BDF8"), unsafe_allow_html=True)
