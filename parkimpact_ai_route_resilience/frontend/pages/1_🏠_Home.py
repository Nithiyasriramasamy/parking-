import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit as st
from frontend.utils.ui_helpers import create_kpi_card, create_themed_bar_chart, create_parking_heatmap, create_animated_graph, create_realtime_animator, create_action_plan_card

st.title("🏠 ASTA1 Command Center")
st.markdown("<p style='color:#94a3b8;'>Welcome to the AI Traffic Impact Intelligence System.</p>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: st.markdown(create_kpi_card("Total Violations", "115.4K", "", "🚗", "#6366F1"), unsafe_allow_html=True)
with c2: st.markdown(create_kpi_card("Active Hotspots", "42", "", "🔥", "#ef4444"), unsafe_allow_html=True)
with c3: st.markdown(create_kpi_card("System Status", "Online", "", "🟢", "#10b981"), unsafe_allow_html=True)
