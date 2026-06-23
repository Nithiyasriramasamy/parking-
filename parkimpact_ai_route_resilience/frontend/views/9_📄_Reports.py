import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit as st
from frontend.utils.ui_helpers import create_kpi_card, create_themed_bar_chart, create_parking_heatmap, create_animated_graph, create_realtime_animator, create_action_plan_card

st.title("📄 Automated Reports")
st.markdown("<p style='color:#94a3b8;'>Generate standardized PDFs for police jurisdiction briefings.</p>", unsafe_allow_html=True)
st.button("Generate Daily Report (PDF)")
st.button("Generate Weekly Heatmap Summary (PDF)")
