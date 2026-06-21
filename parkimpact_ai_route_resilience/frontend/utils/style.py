import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* Hide Streamlit Default Elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Command Center Background */
        .stApp {
            background-color: #0e1117;
            color: #c9d1d9;
        }
        
        /* Modern KPI Cards */
        .kpi-card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .kpi-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.5);
            border-color: rgba(99, 102, 241, 0.5);
        }
        .kpi-title {
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #94a3b8;
            margin-bottom: 10px;
            font-weight: 600;
        }
        .kpi-value {
            font-size: 32px;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 5px;
        }
        .kpi-subtitle {
            font-size: 12px;
            color: #64748b;
        }
        
        /* Highlight specific KPI */
        .kpi-critical {
            border-left: 4px solid #ef4444;
        }
        .kpi-success {
            border-left: 4px solid #10b981;
        }
        .kpi-warning {
            border-left: 4px solid #f59e0b;
        }
        .kpi-info {
            border-left: 4px solid #3b82f6;
        }
        
        /* Custom Container styling */
        .dashboard-container {
            background: #1e293b;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.05);
            margin-bottom: 20px;
        }
        
        /* Table Styling */
        .dataframe {
            background: transparent !important;
        }
        
        /* Custom Headers */
        h1, h2, h3 {
            font-weight: 700 !important;
            letter-spacing: -0.5px;
        }
        </style>
    """, unsafe_allow_html=True)

def kpi_card(title, value, subtitle="", type="info"):
    return f"""
    <div class="kpi-card kpi-{type}">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtitle">{subtitle}</div>
    </div>
    """
