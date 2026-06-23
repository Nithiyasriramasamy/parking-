import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit as st
from frontend.utils.ui_helpers import create_kpi_card, create_themed_bar_chart, create_parking_heatmap, create_animated_graph, create_realtime_animator, create_action_plan_card

import pandas as pd, numpy as np
st.title("🔴 Real-Time Integration")
st.markdown("<p style='color:#94a3b8;'>Live ANPR feed from 250 cameras across 165 monitored junctions.</p>", unsafe_allow_html=True)
c1, c2 = st.columns([2, 1])
with c1:
    st.markdown("<h3>Live Detection Heatmap</h3>", unsafe_allow_html=True)
    df = pd.DataFrame({'latitude': np.random.normal(12.9716, 0.05, 500), 'longitude': np.random.normal(77.5946, 0.05, 500)})
    st.plotly_chart(create_parking_heatmap(df), use_container_width=True)
with c2:
    st.markdown("<h3>ANPR Alert Stream</h3>", unsafe_allow_html=True)
    create_realtime_animator()
