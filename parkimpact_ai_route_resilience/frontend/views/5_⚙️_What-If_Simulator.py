import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit as st
from frontend.utils.ui_helpers import create_kpi_card, create_themed_bar_chart, create_parking_heatmap, create_animated_graph, create_realtime_animator, create_action_plan_card

from backend.services.collapse_simulator import CollapseSimulator
st.title("⚙️ What-If Simulator (Urban Collapse)")
st.markdown("<p style='color:#94a3b8;'>Simulate the cascading effects of illegal parking blocks on the city grid.</p>", unsafe_allow_html=True)
col_input, col_viz = st.columns([1, 2])
critical_edges = ["KR Market Bridge", "Silk Board Flyover", "Indiranagar 100ft", "MG Road Metro", "Whitefield Main"]
with col_input:
    st.markdown("<h4>Simulate Road Blocks</h4>", unsafe_allow_html=True)
    blocked = [edge for edge in critical_edges if st.checkbox(edge)]
    run_sim = st.button("Run Collapse Simulation")
with col_viz:
    if run_sim or blocked:
        sim = CollapseSimulator()
        results = sim.simulate(blocked)
        sev = results['severity']
        color = "#10b981" if sev < 3 else "#f59e0b" if sev < 6 else "#ef4444"
        st.markdown(f'<div style="background-color: {color}20; border: 1px solid {color}; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 15px;"><h3 style="color: {color}; margin: 0;">Collapse Severity: {sev}/10</h3></div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(create_kpi_card("Disconnected", f"{results['disconnected_nodes_pct']}%", "", "🚷", color), unsafe_allow_html=True)
        with c2: st.markdown(create_kpi_card("Travel Time", f"+{results['travel_time_increase']}", "min", "⏳", color), unsafe_allow_html=True)
        with c3: st.markdown(create_kpi_card("Emergency Reach", f"{results['emergency_reachability']}%", "", "🚑", color), unsafe_allow_html=True)
        with c4: st.markdown(create_kpi_card("Economic Loss", f"₹{(results['economic_loss']/1000000):.1f}M", "/hr", "📉", color), unsafe_allow_html=True)
        if sev > 6:
            st.markdown(create_action_plan_card(f"Deploy 3 officers to {blocked[0]} IMMEDIATELY", "CRITICAL", "🚨", "#ef4444"), unsafe_allow_html=True)
        elif sev > 0:
            st.markdown(create_action_plan_card("Dispatch patrol to investigate minor blockage", "LOW", "🚓", "#10b981"), unsafe_allow_html=True)
