import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import pandas as pd
import time
import random
import streamlit.components.v1 as components
from frontend.utils.ui_helpers import create_kpi_card, create_action_plan_card
import requests
API_URL = os.environ.get("BACKEND_URL", "https://parking-h8qb.onrender.com")

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

# THE ANIMATION COMPONENT
# We build an HTML/JS/CSS blob that visualizes the network.
animation_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  body {
    background: transparent;
    color: #F8FAFC;
    font-family: 'Inter', sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 150px;
    margin: 0;
    overflow: hidden;
  }
  .network-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 600px;
    position: relative;
  }
  .node {
    width: 80px;
    height: 80px;
    background: rgba(31, 41, 55, 0.9);
    border: 2px solid #38BDF8;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 32px;
    z-index: 2;
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
    transition: all 0.3s ease;
    position: relative;
  }
  .node.active {
    border-color: #34D399;
    box-shadow: 0 0 30px #34D399;
    transform: scale(1.1);
  }
  .node.ringing {
    animation: shake 0.5s infinite;
    border-color: #F59E0B;
    box-shadow: 0 0 30px #F59E0B;
  }
  .line {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    height: 4px;
    background: rgba(56, 189, 248, 0.2);
    z-index: 1;
  }
  .line-1 { left: 40px; width: 260px; }
  .line-2 { left: 300px; width: 260px; }
  
  .packet {
    width: 15px;
    height: 15px;
    background: #34D399;
    border-radius: 50%;
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    box-shadow: 0 0 10px #34D399;
    opacity: 0;
    z-index: 3;
  }
  
  .animate-packet-1 {
    animation: moveRight 1s ease-in-out forwards;
  }
  .animate-packet-2 {
    animation: moveRight2 1s ease-in-out forwards;
    animation-delay: 1s;
  }
  
  @keyframes moveRight {
    0% { left: 40px; opacity: 1; }
    90% { opacity: 1; }
    100% { left: 300px; opacity: 0; }
  }
  @keyframes moveRight2 {
    0% { left: 300px; opacity: 1; }
    90% { opacity: 1; }
    100% { left: 560px; opacity: 0; }
  }
  @keyframes shake {
    0% { transform: translate(1px, 1px) rotate(0deg); }
    10% { transform: translate(-1px, -2px) rotate(-10deg); }
    20% { transform: translate(-3px, 0px) rotate(10deg); }
    30% { transform: translate(3px, 2px) rotate(0deg); }
    40% { transform: translate(1px, -1px) rotate(10deg); }
    50% { transform: translate(-1px, 2px) rotate(-10deg); }
    60% { transform: translate(-3px, 1px) rotate(0deg); }
    70% { transform: translate(3px, 1px) rotate(-10deg); }
    80% { transform: translate(-1px, -1px) rotate(10deg); }
    90% { transform: translate(1px, 2px) rotate(0deg); }
    100% { transform: translate(1px, -2px) rotate(-10deg); }
  }
  
  .label {
    position: absolute;
    bottom: -30px;
    font-size: 14px;
    color: #94A3B8;
    white-space: nowrap;
    text-align: center;
    width: 100%;
  }
  .message-bubble {
    position: absolute;
    top: -40px;
    background: #34D399;
    color: #0B0F19;
    padding: 5px 10px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: bold;
    opacity: 0;
    transition: opacity 0.3s;
  }
  .show-bubble {
    opacity: 1;
  }
</style>
</head>
<body>
  <div class="network-container">
    <div class="line line-1"></div>
    <div class="line line-2"></div>
    
    <div class="node" id="cam">
      📷
      <div class="label">AI ANPR Feed</div>
      <div class="message-bubble" id="cam-bubble">Detected!</div>
    </div>
    
    <div class="packet" id="pkt1"></div>
    
    <div class="node" id="brain">
      🧠
      <div class="label">ASTA1 Server</div>
      <div class="message-bubble" id="brain-bubble">Dispatching SMS...</div>
    </div>
    
    <div class="packet" id="pkt2"></div>
    
    <div class="node" id="phone">
      📱
      <div class="label">Owner Phone</div>
      <div class="message-bubble" id="phone-bubble">Calling...</div>
    </div>
  </div>

  <script>
    function triggerAnimation() {
      // Reset
      document.getElementById('pkt1').className = 'packet';
      document.getElementById('pkt2').className = 'packet';
      document.getElementById('cam').className = 'node';
      document.getElementById('brain').className = 'node';
      document.getElementById('phone').className = 'node';
      
      document.getElementById('cam-bubble').classList.remove('show-bubble');
      document.getElementById('brain-bubble').classList.remove('show-bubble');
      document.getElementById('phone-bubble').classList.remove('show-bubble');
      
      // Force reflow
      void document.getElementById('pkt1').offsetWidth;
      
      // Start Anim
      document.getElementById('cam').classList.add('active');
      document.getElementById('cam-bubble').classList.add('show-bubble');
      document.getElementById('pkt1').classList.add('animate-packet-1');
      
      setTimeout(() => {
        document.getElementById('cam').classList.remove('active');
        document.getElementById('cam-bubble').classList.remove('show-bubble');
        
        document.getElementById('brain').classList.add('active');
        document.getElementById('brain-bubble').classList.add('show-bubble');
        document.getElementById('pkt2').classList.add('animate-packet-2');
      }, 1000);
      
      setTimeout(() => {
        document.getElementById('brain').classList.remove('active');
        document.getElementById('brain-bubble').classList.remove('show-bubble');
        
        document.getElementById('phone').classList.add('ringing');
        document.getElementById('phone-bubble').classList.add('show-bubble');
      }, 2000);
      
      setTimeout(() => {
        document.getElementById('phone').classList.remove('ringing');
        document.getElementById('phone').classList.add('active');
        document.getElementById('phone-bubble').innerText = "SMS Delivered!";
      }, 4000);
    }
    
    // Listen for messages from Streamlit
    window.addEventListener('message', function(event) {
      if (event.data.type === 'TRIGGER_ALERT') {
        triggerAnimation();
      }
    });
  </script>
</body>
</html>
"""

st.markdown("### 🌐 Live Dispatch Visualizer")
components.html(animation_html, height=180)

# Trick to trigger the JS animation from Python
if "trigger_anim" not in st.session_state:
    st.session_state.trigger_anim = False

if st.session_state.trigger_anim:
    st.components.v1.html("""
    <script>
        window.parent.postMessage({type: 'TRIGGER_ALERT'}, '*');
    </script>
    """, height=0)
    st.session_state.trigger_anim = False

st.markdown("<hr style='border-color: rgba(56, 189, 248, 0.2);'>", unsafe_allow_html=True)

c_left, c_right = st.columns([1, 1.5])

with c_left:
    st.markdown("### 🤖 Live AI Detection Feed")
    
    # Auto-scrolling mock feed
    feed_placeholder = st.empty()
    
    st.markdown("### 🎛️ Manual Dispatch Override")
    with st.form("dispatch_form"):
        plate = st.text_input("Vehicle Plate", "KA-01-XX-0000")
        phone = st.text_input("Owner Phone", "+91 9988776655")
        location = st.text_input("Location", "MG Road Metro")
        
        submitted = st.form_submit_button("🚨 Simulate Dispatch")
        if submitted:
            st.session_state.trigger_anim = True
            try:
                payload = {"vehicle_plate": plate, "owner_phone": phone, "location": location}
                response = requests.post(f"{API_URL}/api/alert-owner", json=payload)
                response.raise_for_status()
                res = response.json()
                st.success("Alert Dispatched Successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

with c_right:
    st.markdown("### ⏳ Active Countdowns & Logs")
    if st.button("🔄 Refresh Logs", use_container_width=True):
        st.rerun()
    
    # Render active alerts into a table
    # Fetch active alerts from remote backend
    try:
        resp = requests.get(f"{API_URL}/api/active-alerts")
        active_alerts = resp.json() if resp.status_code == 200 else {}
    except:
        active_alerts = {}
        
    if not active_alerts:
        st.info("No active alerts.")
    else:
        log_data = []
        # Sort by most recent
        sorted_alerts = dict(sorted(active_alerts.items(), key=lambda item: item[1]['deadline'], reverse=True))
        
        for alert_id, data in sorted_alerts.items():
            status_color = "🟢" if data['status'] == "REMOVED_VOLUNTARILY" else "🔴" if data['status'] == "E_CHALLAN_ISSUED" else "⏳"
            log_data.append({
                "Alert ID": alert_id,
                "Vehicle": data['vehicle_plate'],
                "Location": data['location'],
                "Status": f"{status_color} {data['status']}",
                "Deadline": data['deadline'].split("T")[1][:8] if "T" in data['deadline'] else data['deadline']
            })
            
        df = pd.DataFrame(log_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown(create_action_plan_card("Twilio webhook standing by for delivery receipts.", "SYSTEM", "📡", "#38BDF8"), unsafe_allow_html=True)

# Run a mini mock detection loop if the page just loaded
if not submitted:
    feed_html = "<div style='background: #111827; border: 1px solid #374151; padding: 10px; border-radius: 8px; height: 120px; overflow-y: auto; font-family: monospace; font-size: 12px; color: #34D399;'>"
    now = time.strftime("%H:%M:%S")
    feed_html += f"[{now}] 📷 CAM-045 scanning Indiranagar...<br>"
    feed_html += f"[{now}] ✅ Plate recognized: KA-03-MK-4567<br>"
    feed_html += f"[{now}] ⚠️ Checking VAHAN database...<br>"
    feed_html += f"[{now}] ❌ Illegal Parking Detected!<br>"
    feed_html += f"[{now}] ⏳ Waiting for Manual Dispatch Override...<br>"
    feed_html += "</div>"
    feed_placeholder.markdown(feed_html, unsafe_allow_html=True)
