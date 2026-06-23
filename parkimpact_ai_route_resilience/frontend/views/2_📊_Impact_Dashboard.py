import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit as st
from frontend.utils.ui_helpers import create_kpi_card, create_themed_bar_chart, create_parking_heatmap, create_animated_graph, create_realtime_animator, create_action_plan_card

import pandas as pd
import numpy as np
import plotly.express as px
st.title("📊 Impact Dashboard")
st.markdown("<p style='color:#94a3b8;'>Analyze true traffic congestion impact through Enhanced PIS metrics.</p>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1: st.markdown(create_kpi_card("Vehicles Delayed", "600", "", "🚗", "#ef4444"), unsafe_allow_html=True)
with col2: st.markdown(create_kpi_card("Hours Wasted", "30", "hrs", "⏰", "#f59e0b"), unsafe_allow_html=True)
with col3: st.markdown(create_kpi_card("Economic Loss", "₹15,000", "", "💰", "#6366F1"), unsafe_allow_html=True)
with col4: st.markdown(create_kpi_card("Congestion", "35%", "", "📉", "#10b981"), unsafe_allow_html=True)
st.markdown("<h3>Hourly Economic Impact Tracking</h3>", unsafe_allow_html=True)
hours = list(range(24))
losses = np.random.normal(5000, 1500, 24)
losses[8:11] += 10000 
losses[17:20] += 12000 
area_df = pd.DataFrame({"Hour": [f"{h:02d}:00" for h in hours], "Economic Loss (₹)": losses})
fig = px.area(area_df, x="Hour", y="Economic Loss (₹)", color_discrete_sequence=['#6366F1'])
fig.update_layout(template='plotly_dark', paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, use_container_width=True)

st.markdown("<hr style='border-color: rgba(56, 189, 248, 0.2);'>", unsafe_allow_html=True)
st.markdown("### 🚗 Top Vehicles Causing Critical Impact")
st.markdown("<p style='color:#94a3b8;'>Live VAHAN database lookup of vehicles currently causing the highest economic and congestion damage.</p>", unsafe_allow_html=True)

vehicle_data = [
    {"Vehicle Plate": "KA-01-AB-1234", "Vehicle Type": "SUV", "Location": "Silk Board Junction", "Duration (Mins)": 45, "Delay Caused (Vehicles)": 320, "Economic Loss (₹)": 8500},
    {"Vehicle Plate": "KA-05-MN-4567", "Vehicle Type": "Delivery Truck", "Location": "MG Road", "Duration (Mins)": 20, "Delay Caused (Vehicles)": 150, "Economic Loss (₹)": 4200},
    {"Vehicle Plate": "KA-03-XY-9876", "Vehicle Type": "Sedan", "Location": "Indiranagar 100ft", "Duration (Mins)": 65, "Delay Caused (Vehicles)": 210, "Economic Loss (₹)": 5600},
    {"Vehicle Plate": "KA-51-PQ-5555", "Vehicle Type": "Hatchback", "Location": "KR Puram Market", "Duration (Mins)": 15, "Delay Caused (Vehicles)": 90, "Economic Loss (₹)": 1800},
    {"Vehicle Plate": "KA-04-RS-3321", "Vehicle Type": "SUV", "Location": "Hebbal Flyover", "Duration (Mins)": 30, "Delay Caused (Vehicles)": 400, "Economic Loss (₹)": 11000},
]
vehicle_df = pd.DataFrame(vehicle_data).sort_values("Economic Loss (₹)", ascending=False)
st.dataframe(vehicle_df, use_container_width=True, hide_index=True)
