# Parking Impact Intelligence

A polished, production-ready Streamlit application built for discovering actionable parking enforcement insights and micro-hotspots.

## Project Overview

This app transforms raw parking violation data into a targeted enforcement planner. It prioritizes data quality and transparent methodology, strictly using **only** the provided dataset without relying on external geocoding, APIs, or mapping engines.

### Key Innovations

1. **Micro-Hotspot Discovery (DBSCAN)**: Automatically clusters coordinate points for records with missing or "No Junction" labels, unearthing previously hidden parking problem zones.
2. **Impact-Aware Ranking**: Replaces simple counts with a transparent Impact Score that weights vehicle severity (e.g., Trucks > Cars > Scooters), recurrence across multiple days, and peak hour concentration.
3. **Data Quality Awareness**: Actively monitors for device coverage anomalies (e.g., sudden drops in February) and allows users to exclude them to prevent skewed behavioral analysis.
4. **Timezone Accuracy**: Corrects raw UTC timestamps to IST, ensuring critical insights like "Peak Enforcement Windows" are off by 0 hours instead of 5.5 hours.

## How to Run

1. Ensure Python is installed.
2. Place the dataset file (`jan to may police violation_anonymized791b166.csv`) in the same directory as `app.py`.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Caveats & Constraints

- **Dataset Only**: The app adheres to the strict constraint of using *only* the provided CSV. Maps are plotted using existing lat/lon columns.
- **Enforcement Bias**: Peak violation windows indicate when enforcement patrols were active or devices were on, not necessarily when parking violations were highest.
- **Impact vs Congestion**: The Impact Score is a relative prioritization proxy and does not directly measure real-world traffic congestion.
