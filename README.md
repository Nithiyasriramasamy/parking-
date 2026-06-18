# ParkImpact AI

ParkImpact AI is an AI-driven parking intelligence platform that identifies illegal parking hotspots, estimates congestion impact using proxy metrics, predicts future parking violations, generates dynamic fine recommendations, and provides enforcement planning.

## Features

- **Hotspot Detection Module**: Uses DBSCAN clustering to identify violation hotspots.
- **Congestion Impact Engine**: Calculates a Parking Impact Score (PIS) for each violation based on vehicle type, violation type, road type, and peak hours.
- **Dynamic Fine Recommendation**: Computes fines ranging from ₹500 to ₹5000 based on the PIS.
- **Prediction Model**: Forecasts future hotspot risks and violation counts using Machine Learning (LightGBM/XGBoost/RandomForest).
- **Enforcement Planner**: Calculates Priority Scores and provides an enforcement deployment plan.
- **Streamlit Dashboard**: A comprehensive multipage dashboard for analytics and visualizations.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the dashboard:
   ```bash
   streamlit run dashboard.py
   ```

## Files

- `hotspot.py`: Contains core logic for preprocessing, clustering, and PIS calculations.
- `train.py`: Script to train ML models for predicting parking violations.
- `predict.py`: Script to load models and make predictions for the enforcement planner.
- `dashboard.py`: Multipage Streamlit application.
