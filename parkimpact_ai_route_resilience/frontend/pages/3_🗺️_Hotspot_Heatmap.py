import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit as st
from frontend.utils.ui_helpers import create_kpi_card, create_themed_bar_chart, create_parking_heatmap, create_animated_graph, create_realtime_animator, create_action_plan_card

import pandas as pd
import numpy as np
st.title("🗺️ Hotspot Heatmap")
st.markdown("<p style='color:#94a3b8;'>Spatial clustering of severe violations using Plotly Dark Mapbox.</p>", unsafe_allow_html=True)
lats = np.random.normal(12.9716, 0.05, 500)
lons = np.random.normal(77.5946, 0.05, 500)
df = pd.DataFrame({'latitude': lats, 'longitude': lons, 'disruption_index': np.random.uniform(1, 10, 500)})
fig = create_parking_heatmap(df, lat_col='latitude', lon_col='longitude', z_col='disruption_index')
fig.update_layout(height=600)
st.plotly_chart(fig, use_container_width=True)
