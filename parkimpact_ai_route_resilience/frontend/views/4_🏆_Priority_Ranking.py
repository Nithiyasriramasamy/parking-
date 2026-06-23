import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit as st
from frontend.utils.ui_helpers import create_kpi_card, create_themed_bar_chart, create_parking_heatmap, create_animated_graph, create_realtime_animator, create_action_plan_card

import pandas as pd
import importlib
import backend.services.graph_criticality
importlib.reload(backend.services.graph_criticality)
from backend.services.graph_criticality import GraphCriticality
st.title("🏆 Priority Ranking Engine")
st.markdown("<p style='color:#94a3b8;'>Rank hotspots based on Graph-Theoretic Criticality and road network resilience.</p>", unsafe_allow_html=True)
gc = GraphCriticality()
nodes_df, edges_df = gc.get_graph_data()
critical_edges = gc.get_critical_edges(edges_df, top_n=15)

# Interactive Deep Dive Selector
st.markdown("### 🔍 Deep Dive Intel")
top_edges = edges_df[edges_df['id'].isin(critical_edges)].sort_values('score', ascending=False)

# Create a list of location names for the dropdown
location_options = top_edges['location_name'].unique().tolist()
selected_location = st.selectbox("Select Location for Intelligence Briefing:", location_options)

if selected_location:
    # Get the specific edge data
    loc_data = top_edges[top_edges['location_name'] == selected_location].iloc[0]
    bw_pct = int(loc_data['betweenness'] * 100)
    loss_pct = int(loc_data['connectivity_loss'] * 100)
    
    explanation_html = f"""
    <div style="background: rgba(31, 41, 55, 0.8); border-left: 5px solid #F59E0B; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
        <h4 style="margin-top:0; color:#F59E0B;">Why is {selected_location} a Priority?</h4>
        <p style="font-size: 16px; margin-bottom: 10px;">
            The AI assigned this location a Criticality Score of <b>{loc_data['score']}</b> due to <b>{loc_data['primary_risk']}</b>.
        </p>
        <p style="font-size: 15px; color: #94A3B8;">
            <b>The Math:</b> Exactly {bw_pct}% of cross-city traffic relies on this specific route (<i>Betweenness Centrality</i>). 
            If an illegally parked vehicle obstructs this path, the entire surrounding road network suffers a <b>{loss_pct}% loss in total connectivity</b>.
        </p>
    </div>
    """
    st.markdown(explanation_html, unsafe_allow_html=True)

st.markdown("<hr style='border-color: rgba(56, 189, 248, 0.2);'>", unsafe_allow_html=True)

col1, col2 = st.columns([1.2, 1])
with col1:
    st.markdown("<h3>Criticality-Ranked Locations</h3>", unsafe_allow_html=True)
    display_df = pd.DataFrame({
        "Location": top_edges['location_name'], 
        "Primary Risk": top_edges['primary_risk'],
        "Impact": top_edges['betweenness'].round(2), 
        "Score": top_edges['score'].round(2)
    })
    st.dataframe(display_df, use_container_width=True, hide_index=True)
with col2:
    st.markdown("<h3>Road Network Vulnerability</h3>", unsafe_allow_html=True)
    fig = create_animated_graph(nodes_df, edges_df, critical_edges)
    st.plotly_chart(fig, use_container_width=True)
