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
