import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit as st
from frontend.utils.ui_helpers import create_kpi_card, create_themed_bar_chart, create_parking_heatmap, create_animated_graph, create_realtime_animator, create_action_plan_card

import pandas as pd
from backend.services.graph_criticality import GraphCriticality
st.title("🏆 Priority Ranking Engine")
st.markdown("<p style='color:#94a3b8;'>Rank hotspots based on Graph-Theoretic Criticality and road network resilience.</p>", unsafe_allow_html=True)
gc = GraphCriticality()
nodes_df, edges_df = gc.get_graph_data()
critical_edges = gc.get_critical_edges(edges_df, top_n=15)
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("<h3>Criticality-Ranked Locations</h3>", unsafe_allow_html=True)
    top_edges = edges_df[edges_df['id'].isin(critical_edges)].sort_values('score', ascending=False)
    display_df = pd.DataFrame({"Location ID": top_edges['id'], "Betweenness": top_edges['betweenness'].round(2), "Conn. Loss": top_edges['connectivity_loss'].round(2), "Criticality Score": top_edges['score'].round(2)})
    st.dataframe(display_df, use_container_width=True, hide_index=True)
with col2:
    st.markdown("<h3>Road Network Vulnerability</h3>", unsafe_allow_html=True)
    fig = create_animated_graph(nodes_df, edges_df, critical_edges)
    st.plotly_chart(fig, use_container_width=True)
