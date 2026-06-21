import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import time

def load_css():
    with open("frontend/static/styles.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def create_kpi_card(title, value, unit="", icon="📊", color="#38BDF8"):
    """Creates a stylized KPI card."""
    # We use inline styles for dynamic color where needed, but base styles from CSS
    html = f"""
    <div class="kpi-card">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-value" style="color: {color};">{value} {unit}</div>
        <div class="kpi-title">{title}</div>
    </div>
    """
    return html

def create_action_plan_card(action, priority, icon, color):
    """Creates an Action Plan card with priority badge."""
    html = f"""
    <div class="action-plan-card" style="border-left: 4px solid {color};">
        <div style="font-size: 24px; margin-right: 15px;">{icon}</div>
        <div style="flex-grow: 1; font-weight: bold; color: white;">{action}</div>
        <div style="background-color: {color}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;">
            {priority}
        </div>
    </div>
    """
    return html

def create_themed_bar_chart(data, x_col, y_col, title, x_label, y_label):
    """Creates a dark-themed Plotly bar chart."""
    fig = px.bar(data, x=x_col, y=y_col, title=title)
    fig.update_traces(marker_color='#38BDF8')
    fig.update_layout(
        template='plotly_dark',
        title_font_color='#F8FAFC',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title=x_label,
        yaxis_title=y_label
    )
    return fig

def create_parking_heatmap(violations_df, lat_col='latitude', lon_col='longitude', z_col=None):
    """Creates a Mapbox density heatmap."""
    fig = px.density_mapbox(
        violations_df, 
        lat=lat_col, 
        lon=lon_col, 
        z=z_col,
        radius=15,
        center=dict(lat=12.9716, lon=77.5946), # Bangalore center
        zoom=10,
        mapbox_style="carto-darkmatter",
        color_continuous_scale="reds"
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)')
    return fig

def create_animated_graph(nodes_df, edges_df, critical_edges):
    """Creates an animated network graph highlighting critical edges."""
    # Simplified mock implementation using Scatter for nodes and lines for edges
    fig = go.Figure()
    
    # Non-critical edges (gray)
    for _, edge in edges_df.iterrows():
        if edge['id'] not in critical_edges:
            fig.add_trace(go.Scatter(
                x=[edge['start_lon'], edge['end_lon'], None],
                y=[edge['start_lat'], edge['end_lat'], None],
                mode='lines',
                line=dict(color='gray', width=1),
                hoverinfo='none',
                showlegend=False
            ))
            
    # Critical edges (red, animated style)
    for _, edge in edges_df.iterrows():
        if edge['id'] in critical_edges:
            fig.add_trace(go.Scatter(
                x=[edge['start_lon'], edge['end_lon'], None],
                y=[edge['start_lat'], edge['end_lat'], None],
                mode='lines',
                line=dict(color='#ef4444', width=3),
                text=f"Criticality: {edge.get('score', 'High')}",
                hoverinfo='text',
                showlegend=False
            ))
            
    # Nodes
    fig.add_trace(go.Scatter(
        x=nodes_df['lon'],
        y=nodes_df['lat'],
        mode='markers',
        marker=dict(size=8, color='#38BDF8'),
        text=nodes_df['name'],
        hoverinfo='text',
        showlegend=False
    ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    return fig

def create_realtime_animator():
    """Simulates a live ANPR feed using st.empty()."""
    placeholder = st.empty()
    
    # Mock data arrays
    cameras = [f"CAM-{str(i).zfill(3)}" for i in range(1, 251)]
    locations = ["KR Market", "MG Road", "Indiranagar", "Silk Board", "Koramangala", "HSR Layout", "Whitefield", "Bellandur"]
    
    import random
    
    with placeholder.container():
        for i in range(10):
            cam = random.choice(cameras)
            loc = random.choice(locations)
            plate = f"KA-01-{random.choice('ABCDEFGH')}{random.choice('ABCDEFGH')}-{random.randint(1000, 9999)}"
            fine = random.choice([500, 1000, 1500, 2000, 2500, 5000])
            
            with st.spinner(f"Scanning camera {random.randint(1,250)}/250..."):
                time.sleep(0.5)
                
            html = f"""
            <div style="background-color: #1A1F2E; border-left: 4px solid #10b981; padding: 15px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #2D3748;">
                <h4 style="margin-top:0; color: #10b981;">🔴 LIVE DETECTION</h4>
                <p style="margin:5px 0;"><b>📹 Camera:</b> {cam}</p>
                <p style="margin:5px 0;"><b>📍 Location:</b> {loc}</p>
                <p style="margin:5px 0;"><b>🚗 Plate:</b> <span style="background:white; color:black; padding:2px 6px; border-radius:4px; font-family:monospace; font-weight:bold;">{plate}</span></p>
                <p style="margin:5px 0;"><b>💰 Fine Issued:</b> ₹{fine}</p>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
