import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit as st
from frontend.utils.ui_helpers import create_kpi_card, create_themed_bar_chart, create_parking_heatmap, create_animated_graph, create_realtime_animator, create_action_plan_card

import pandas as pd
st.title("💰 Dynamic Fines")
st.markdown("<p style='color:#94a3b8;'>Compute violation fines dynamically using the Graph-Theoretic Criticality Multiplier.</p>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: st.markdown(create_kpi_card("Average Fine", "₹2,100", "", "💰", "#10b981"), unsafe_allow_html=True)
with c2: st.markdown(create_kpi_card("Total Rev.", "₹300M", "/yr", "📈", "#6366F1"), unsafe_allow_html=True)
with c3: st.markdown(create_kpi_card("Criticality", "5x", "multiplier", "⚠️", "#ef4444"), unsafe_allow_html=True)
st.markdown("<h3>Sample Fine Ledger</h3>", unsafe_allow_html=True)
ledger = pd.DataFrame({"Location": ["Silk Board", "Indiranagar", "KR Market", "MG Road"], "Base Fine": [500, 1000, 500, 1000], "Criticality": [8.2, 4.1, 9.5, 2.1], "Multiplier": ["5x", "2x", "5x", "1x"], "Final Fine": ["₹2,500", "₹2,000", "₹2,500", "₹1,000"]})
st.dataframe(ledger, use_container_width=True, hide_index=True)
