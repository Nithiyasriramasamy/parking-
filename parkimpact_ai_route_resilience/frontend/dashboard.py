import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import runpy
from frontend.utils.ui_helpers import load_css

st.set_page_config(page_title="ASTA1 Command Center", page_icon="🚗", layout="wide")

# Load global CSS
load_css()

def create_sidebar():
    st.sidebar.markdown("<h2 style='text-align: center; color: #6366F1;'>🚗 ASTA1<br><span style='font-size:14px; color:#9CA3AF;'>AI Traffic Impact Intelligence</span></h2>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    pages = {
        "Home": "1_🏠_Home.py",
        "Impact Dashboard": "2_📊_Impact_Dashboard.py",
        "Hotspot Heatmap": "3_🗺️_Hotspot_Heatmap.py",
        "Priority Ranking": "4_🏆_Priority_Ranking.py",
        "What-If Simulator": "5_⚙️_What-If_Simulator.py",
        "Resource Planner": "6_🚓_Resource_Planner.py",
        "Predictive Insights": "7_🔮_Predictive_Insights.py",
        "Explainable AI": "8_🧠_Explainable_AI.py",
        "Reports": "9_📄_Reports.py",
        "Occlusion Robustness": "10_🌳_Occlusion_Robustness.py",
        "Dynamic Fines": "11_💰_Dynamic_Fines.py",
        "Real-Time Integration": "12_🔴_Real-Time_Integration.py"
    }
    
    selection = st.sidebar.radio("Command Center Modules", list(pages.keys()))
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("<div style='text-align:center; color:#10b981; font-weight:bold;'>System Status: Active 🟢</div>", unsafe_allow_html=True)
    
    return pages[selection]

# Main routing logic
selected_page_file = create_sidebar()

# Construct the path to the selected page
page_path = os.path.join(os.path.dirname(__file__), "pages", selected_page_file)

# Execute the selected page
if os.path.exists(page_path):
    runpy.run_path(page_path)
else:
    st.error(f"Module {selected_page_file} is currently under construction or missing.")
