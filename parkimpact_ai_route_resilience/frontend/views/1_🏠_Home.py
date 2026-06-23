import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random
from frontend.utils.ui_helpers import create_kpi_card, create_action_plan_card

st.markdown("""
<div style="background: linear-gradient(135deg, rgba(56, 189, 248, 0.1) 0%, rgba(17, 24, 39, 0.8) 100%);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 0 30px rgba(56, 189, 248, 0.1);
            margin-bottom: 30px;
            backdrop-filter: blur(10px);">
    <h1 style="font-size: 3rem; margin-bottom: 10px; color: #F8FAFC; text-shadow: 0 0 20px rgba(56,189,248,0.5);">ASTA1 <span style="color: #38BDF8;">Command Center</span></h1>
    <p style="font-size: 1.2rem; color: #94A3B8; max-width: 600px; margin: 0 auto;">
        Next-Generation AI Traffic Impact Intelligence. <br/>
        Predicting congestion, prioritizing enforcement, and automating alerts in real-time.
    </p>
</div>
""", unsafe_allow_html=True)

# High Impact KPI Cards
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(create_kpi_card("Total Violations", "115,400", "Logged", "🚗", "#38BDF8"), unsafe_allow_html=True)
with c2: st.markdown(create_kpi_card("Active Hotspots", "42", "Critical", "🔥", "#F59E0B"), unsafe_allow_html=True)
with c3: st.markdown(create_kpi_card("Congestion Prevented", "66%", "Efficiency", "📉", "#34D399"), unsafe_allow_html=True)
with c4: st.markdown(create_kpi_card("System Status", "Online", "Secure", "🟢", "#34D399"), unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

col_chart, col_feed = st.columns([2, 1])

with col_chart:
    st.markdown("### 📊 Network Congestion Trend (Live 24H)")
    # Generate mock trend data
    hours = [f"{i}:00" for i in range(24)]
    congestion = [np.sin(i/3) * 30 + 50 + random.randint(-10, 10) for i in range(24)]
    df_trend = pd.DataFrame({"Hour": hours, "Congestion Impact (%)": congestion})
    
    fig = px.area(df_trend, x="Hour", y="Congestion Impact (%)", 
                  color_discrete_sequence=['#38BDF8'])
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(56, 189, 248, 0.1)')
    )
    # Add gradient fill
    fig.update_traces(fill='tozeroy', fillcolor='rgba(56, 189, 248, 0.2)', line=dict(width=3))
    st.plotly_chart(fig, use_container_width=True)

with col_feed:
    st.markdown("### ⚡ Quick Actions")
    
    def go_to_page(target_page):
        st.session_state.nav_radio = target_page

    def render_clickable_action(text, icon, btn_text, color, target_page):
        c1, c2 = st.columns([3, 2])
        with c1:
            st.markdown(f"<div style='border-left: 4px solid {color}; padding-left: 10px; height: 100%; display: flex; align-items: center;'><span style='font-size:20px; margin-right:10px;'>{icon}</span><span style='color:white; font-weight:bold;'>{text}</span></div>", unsafe_allow_html=True)
        with c2:
            st.button(btn_text, key=f"btn_{target_page}", on_click=go_to_page, args=(target_page,), use_container_width=True)
        st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
                
    render_clickable_action("Run Impact Dashboard to view location scoring.", "📊", "Open Impact", "#38BDF8", "Impact Dashboard")
    render_clickable_action("View Priority Rankings for dispatch operations.", "🏆", "View Priority", "#F59E0B", "Priority Ranking")
    render_clickable_action("Trigger Auto Alerts for real-time violations.", "📱", "Run Alerts", "#34D399", "Auto Alert")
    
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("### 📡 Node Status")
    status_html = """
    <div style="background: rgba(31,41,55,0.7); border: 1px solid rgba(56,189,248,0.2); padding: 15px; border-radius: 10px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span style="color:#94A3B8;">ANPR Vision Models</span>
            <span style="color:#34D399; font-weight:bold;">100% ONLINE</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span style="color:#94A3B8;">Twilio Comms API</span>
            <span style="color:#34D399; font-weight:bold;">100% ONLINE</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span style="color:#94A3B8;">TGCN Predictor</span>
            <span style="color:#34D399; font-weight:bold;">100% ONLINE</span>
        </div>
    </div>
    """
    st.markdown(status_html, unsafe_allow_html=True)
