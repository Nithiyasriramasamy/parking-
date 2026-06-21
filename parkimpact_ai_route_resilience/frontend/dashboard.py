import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import runpy
from frontend.utils.ui_helpers import load_css

st.set_page_config(page_title="ASTA1 Command Center", page_icon="🚗", layout="wide")

# Load global CSS
load_css()

def go_prev(page_keys, current_selection):
    idx = page_keys.index(current_selection)
    if idx > 0:
        st.session_state.nav_radio = page_keys[idx - 1]

def go_next(page_keys, current_selection):
    idx = page_keys.index(current_selection)
    if idx < len(page_keys) - 1:
        st.session_state.nav_radio = page_keys[idx + 1]

def render_navigation(page_keys, selection, position="top"):
    current_idx = page_keys.index(selection)
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if current_idx > 0:
            st.button("⬅️ Previous", key=f"prev_{position}", on_click=go_prev, args=(page_keys, selection), use_container_width=True)
    with col3:
        if current_idx < len(page_keys) - 1:
            st.button("Next ➡️", key=f"next_{position}", on_click=go_next, args=(page_keys, selection), use_container_width=True)

def create_sidebar():
    st.sidebar.markdown("<a href='/' target='_self' style='text-decoration:none;'><h2 style='text-align: center; color: #38BDF8; text-shadow: 0 0 10px rgba(56,189,248,0.5);'>🚗 ASTA1<br><span style='font-size:14px; color:#9CA3AF; text-shadow:none;'>AI Traffic Impact Intelligence</span></h2></a>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    pages = {
        "Home": "1_🏠_Home.py",
        "Impact Dashboard": "2_📊_Impact_Dashboard.py",
        "Hotspot Heatmap": "3_🗺️_Hotspot_Heatmap.py",
        "Priority Ranking": "4_🏆_Priority_Ranking.py",
        "What-If Simulator": "5_⚙️_What-If_Simulator.py",
        "Resource Planner": "6_📋_Resource_Planner.py",
        "Predictive Insights": "7_🔮_Predictive_Insights.py",
        "Explainable AI": "8_🧠_Explainable_AI.py",
        "Reports": "9_📄_Reports.py",
        "Occlusion Robustness": "10_🌳_Occlusion_Robustness.py",
        "Dynamic Fines": "11_💰_Dynamic_Fines.py",
        "Real-Time Integration": "12_🔴_Real-Time_Integration.py",
        "Auto Alert": "13_📱_Auto_Alert.py"
    }
    
    page_keys = list(pages.keys())
    
    if "nav_radio" not in st.session_state:
        st.session_state.nav_radio = page_keys[0]
        
    selection = st.sidebar.radio("Command Center Modules", page_keys, key="nav_radio")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("<div style='text-align:center; color:#34D399; font-weight:bold; text-shadow: 0 0 5px rgba(52,211,153,0.5);'>System Status: Active 🟢</div>", unsafe_allow_html=True)
    
    return selection, pages, page_keys

# Main routing logic
selection, pages, page_keys = create_sidebar()
selected_page_file = pages[selection]

# Construct the path to the selected page
page_path = os.path.join(os.path.dirname(__file__), "pages", selected_page_file)

# Top Navigation
render_navigation(page_keys, selection, "top")

# Execute the selected page
if os.path.exists(page_path):
    runpy.run_path(page_path)
else:
    st.error(f"Module {selected_page_file} is currently under construction or missing.")

# Bottom Navigation
st.markdown("<br><hr style='border-color: rgba(56, 189, 248, 0.2);'>", unsafe_allow_html=True)
render_navigation(page_keys, selection, "bottom")
