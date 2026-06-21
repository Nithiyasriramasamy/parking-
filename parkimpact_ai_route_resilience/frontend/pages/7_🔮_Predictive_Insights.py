import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit as st
from frontend.utils.ui_helpers import create_kpi_card, create_themed_bar_chart, create_parking_heatmap, create_animated_graph, create_realtime_animator, create_action_plan_card

import pandas as pd
from backend.models.tgcn import TGCNModel
st.title("🔮 Predictive Insights (TGCN)")
st.markdown("<p style='color:#94a3b8;'>Temporal Graph Convolutional Network forecasting for traffic violations (85% Accuracy).</p>", unsafe_allow_html=True)
col1, col2 = st.columns([1, 2])
with col1:
    hour = st.slider("Target Hour", 0, 23, 14)
    day = st.selectbox("Day of Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    predict_btn = st.button("Run Forecast", type="primary")
with col2:
    if predict_btn:
        model = TGCNModel()
        results = model.predict(hour, day, "Clear")
        df = pd.DataFrame(results)
        fig = create_themed_bar_chart(df, "zone", "violations", f"Forecast for {day} {hour:02d}:00", "Zone", "Predicted Violations")
        st.plotly_chart(fig, use_container_width=True)
