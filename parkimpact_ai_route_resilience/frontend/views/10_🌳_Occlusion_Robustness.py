import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit as st
from frontend.utils.ui_helpers import create_kpi_card, create_themed_bar_chart, create_parking_heatmap, create_animated_graph, create_realtime_animator, create_action_plan_card

import plotly.graph_objects as go
st.title("🌳 Occlusion Robustness (ViT Enhanced)")
st.markdown("<p style='color:#94a3b8;'>YOLOv8 + Vision Transformer for parking detection under severe occlusions (trees, shadows, clouds).</p>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: st.markdown(create_kpi_card("Detection Accuracy", "96.4%", "", "🌳", "#10b981"), unsafe_allow_html=True)
with c2: st.markdown(create_kpi_card("Standard Accuracy", "67.2%", "", "📉", "#ef4444"), unsafe_allow_html=True)
with c3: st.markdown(create_kpi_card("Synthetic Dataset", "173,160", "images", "📸", "#6366F1"), unsafe_allow_html=True)
tab1, tab2 = st.tabs(["Standard Detection (YOLOv8)", "Occlusion-Robust (YOLOv8 + ViT)"])
def mock_img(robust):
    fig = go.Figure()
    fig.add_shape(type="rect", x0=0, y0=0, x1=10, y1=10, fillcolor="#2d3748", line=dict(width=0))
    fig.add_shape(type="rect", x0=3, y0=4, x1=5, y1=7, fillcolor="#94a3b8")
    fig.add_shape(type="circle", x0=2, y0=3, x1=6, y1=8, fillcolor="#10b981", opacity=0.8)
    if robust:
        fig.add_shape(type="rect", x0=2.8, y0=3.8, x1=5.2, y1=7.2, line=dict(color="#ef4444", width=3, dash="dash"))
    fig.update_layout(xaxis=dict(showticklabels=False), yaxis=dict(showticklabels=False), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=300, margin=dict(l=0, r=0, t=0, b=0))
    return fig
with tab1: st.plotly_chart(mock_img(False), use_container_width=True)
with tab2: st.plotly_chart(mock_img(True), use_container_width=True)
