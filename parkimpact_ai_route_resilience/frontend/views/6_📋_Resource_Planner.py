import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit as st
from frontend.utils.ui_helpers import create_kpi_card, create_themed_bar_chart, create_parking_heatmap, create_animated_graph, create_realtime_animator, create_action_plan_card

st.title("📋 Resource Planner")
st.markdown("<p style='color:#94a3b8;'>Optimal deployment of traffic police officers based on predictive modeling.</p>", unsafe_allow_html=True)
st.markdown(create_action_plan_card("Allocate 15 officers to Silk Board Junction", "HIGH", "👮", "#ef4444"), unsafe_allow_html=True)
st.markdown(create_action_plan_card("Deploy 5 towing vehicles to Indiranagar 100ft Rd", "MEDIUM", "🚜", "#f59e0b"), unsafe_allow_html=True)
