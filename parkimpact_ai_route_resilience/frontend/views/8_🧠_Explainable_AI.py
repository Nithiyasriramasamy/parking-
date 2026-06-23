import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit as st
from frontend.utils.ui_helpers import create_kpi_card, create_themed_bar_chart, create_parking_heatmap, create_animated_graph, create_realtime_animator, create_action_plan_card

st.title("🧠 Explainable AI")
st.markdown("<p style='color:#94a3b8;'>Understand the feature importance and decision boundaries of the ML models.</p>", unsafe_allow_html=True)
import pandas as pd
df = pd.DataFrame({"Feature": ["Time of Day", "Location Centrality", "Vehicle Size", "Weather", "Day of Week"], "Importance": [0.35, 0.25, 0.20, 0.10, 0.10]})
fig = create_themed_bar_chart(df, "Feature", "Importance", "Model Feature Importance", "Feature", "Relative Importance")
st.plotly_chart(fig, use_container_width=True)
