import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import pandas as pd
import time
from frontend.utils.ui_helpers import create_kpi_card, create_action_plan_card
from backend.api.alert_owner import active_alerts, dispatch_auto_alert, AlertRequest

st.title("📱 Auto Alert & Owner Notification")
st.markdown("<p style='color:#94a3b8;'>Real-time automated SMS and Voice call dispatch to violators with 10-minute countdowns.</p>", unsafe_allow_html=True)

# Impact KPIs
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(create_kpi_card("Response Time", "5 sec", "-99.9%", "⚡", "#38BDF8"), unsafe_allow_html=True)
with col2:
    st.markdown(create_kpi_card("Voluntary Removals", "70%", "of alerts", "🏃‍♂️", "#34D399"), unsafe_allow_html=True)
with col3:
    st.markdown(create_kpi_card("Congestion Drops", "66%", "", "📉", "#A78BFA"), unsafe_allow_html=True)
with col4:
    st.markdown(create_kpi_card("Owner Satisfaction", "85%", "+65%", "😊", "#38BDF8"), unsafe_allow_html=True)

st.markdown("<hr style='border-color: rgba(56, 189, 248, 0.2);'>", unsafe_allow_html=True)

c_left, c_right = st.columns([1, 2])

with c_left:
    st.markdown("<h3>Manual Dispatch Override</h3>", unsafe_allow_html=True)
    with st.form("dispatch_form"):
        plate = st.text_input("Vehicle Plate", "KA-01-XX-0000")
        phone = st.text_input("Owner Phone", "+91 ")
        location = st.text_input("Location", "MG Road Metro")
        
        submitted = st.form_submit_button("Send SMS & Voice Alert")
        if submitted:
            with st.spinner("Initiating Twilio APIs..."):
                time.sleep(1) # simulate api delay
                try:
                    req = AlertRequest(vehicle_plate=plate, owner_phone=phone, location=location)
                    res = dispatch_auto_alert(req)
                    st.success("Alert successfully dispatched!")
                    st.json(res)
                except Exception as e:
                    st.error(f"Error: {e}")

with c_right:
    st.markdown("<h3>Active Countdowns & Logs</h3>", unsafe_allow_html=True)
    
    # Render active alerts into a table
    if not active_alerts:
        st.info("No active alerts.")
    else:
        log_data = []
        for alert_id, data in active_alerts.items():
            status_color = "🟢" if data['status'] == "REMOVED_VOLUNTARILY" else "🔴" if data['status'] == "E_CHALLAN_ISSUED" else "⏳"
            log_data.append({
                "Alert ID": alert_id,
                "Vehicle": data['vehicle_plate'],
                "Location": data['location'],
                "Status": f"{status_color} {data['status']}",
                "Deadline": data['deadline'].split("T")[1][:8]
            })
            
        df = pd.DataFrame(log_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown(create_action_plan_card("Twilio webhook standing by for delivery receipts.", "SYSTEM", "📡", "#38BDF8"), unsafe_allow_html=True)
