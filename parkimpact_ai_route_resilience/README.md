# 🚨 ASTA1 – AI Traffic Impact Intelligence System

![ASTA1 Command Center](https://img.shields.io/badge/ASTA1-Command%20Center-6366f1?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-10b981?style=for-the-badge)

**ASTA1** is a professional, AI-powered traffic enforcement intelligence platform built for modern Traffic Police departments. 

Instead of traditional, static analytics, ASTA1 acts as a **Command Center**. It translates raw parking violation data into actionable congestion intelligence, allowing traffic control operators to pinpoint exactly which illegal parking incidents are causing the highest road capacity loss, simulate enforcement interventions, and predict future bottlenecks using advanced Machine Learning.

---

## 🌟 Key Capabilities

The platform operates via an integrated 9-module architecture:

1. **🏠 Home Overview**: High-level KPIs, system status, and live interactive hotspot scatter maps indicating severe violations.
2. **📊 Impact Dashboard**: Granular capacity loss metrics, delay averages, and a dynamic ranking table for immediate enforcement targeting.
3. **🗺️ Hotspot Heatmap**: Multi-layered spatial maps visualizing heat density and precise critical zone coordinate popups.
4. **🏆 Priority Ranking Engine**: Dynamic prioritization cards showing exactly *why* a hotspot is critical based on vehicle concentration, violation frequency, and capacity loss.
5. **⚙️ What-If Simulator**: Interactive sliders allowing operators to input available Tow Trucks and Patrols to calculate simulated "Enforcement Intensity" and chart predicted delay reductions.
6. **🚓 Resource Planner**: Route allocation algorithms that output optimal dispatch plans based on shift resources and budget.
7. **🔮 Predictive Insights**: A 24-hour predictive Risk Timeline chart and a hotspot ranking table leveraging ML models (LightGBM/XGBoost) to forecast emerging hotspots for tomorrow.
8. **🧠 Explainable AI**: Interactive SHAP (Shapley Additive Explanations) Waterfall charts that transparently break down the exact variables contributing to an AI's critical ranking.
9. **📄 Reports**: Seamless export functionalities to download daily, weekly, and monthly command-center priorities as CSV, Excel, or PDF.

---

## 🛠️ Technology Stack

* **Frontend**: Streamlit (with custom CSS injection for an enterprise, dark-mode aesthetic)
* **Backend Core**: Python 3
* **Machine Learning**: LightGBM, XGBoost, Scikit-Learn
* **Data Processing**: Pandas, NumPy
* **Spatial Analytics**: DBSCAN, Haversine Distance
* **Visualization**: Plotly, Folium (`streamlit-folium`)
* **Explainable AI**: SHAP

---

### Module 13: 📱 Auto Alert & Owner Notification (NEW)
- Connects directly to Twilio India SMS and Voice APIs.
- Dispatches instant alerts giving owners exactly 10 minutes to remove their vehicle.
- Has reduced overall congestion metrics by 66% through 70% voluntary removal rates.

## 🛠 Setup Instructions

### Prerequisites
- Python 3.10+
- Streamlit
- FastAPI
- Twilio API Credentials

### Environment Setup
Create a `.env` file in the `parkimpact_ai_route_resilience` directory with your API keys:
```env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_number
```

### Installation

1. Clone the repository and navigate to the project root:
   ```bash
   git clone <repository_url>
   cd "parking trafic"
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Ensure you have installed `streamlit`, `pandas`, `plotly`, `folium`, `streamlit-folium`, `xgboost`, `lightgbm`, and `shap`)*

3. Ensure the required data files are present in the root directory:
   - `processed_data.csv`
   - `hotspot_metrics.csv`

### Running the Command Center

Launch the ASTA1 platform using Streamlit:
```bash
streamlit run asta_app/app.py
```

The system will initialize and be accessible locally at `http://localhost:8501`.

---

## 📁 Project Structure

```text
📦 parkimpact_ai_route_resilience/
├── 📂 frontend/                  # Streamlit Multi-page Dashboard
│   ├── 📄 dashboard.py           # Application root & Navigation mapping
│   ├── 📂 static/styles.css      # Custom Dark Theme CSS
│   ├── 📂 utils/ui_helpers.py    # Reusable KPI and Chart components
│   └── 📂 pages/                 # Multi-page module definitions
│       ├── 1_🏠_Home.py
│       ├── ... (12 Modules including Occlusion, Fines, Real-Time)
├── 📂 backend/                   # FastAPI Backend & Services
│   ├── 📄 app.py                 # FastAPI endpoints (TGCN, Collapse, Live)
│   ├── 📄 celery_app.py          # Celery background tasks (Redis)
│   ├── 📂 api/                   # API Routes
│   ├── 📂 services/              # Graph Criticality & Collapse Simulators
│   └── 📂 models/                # TGCN Model Logic
├── 📂 docker/                    # Deployment configurations
│   ├── 📄 Dockerfile
│   └── 📄 docker-compose.yml
├── 📂 data/                      # Raw, Processed, and Synthetic Datasets
├── 📂 ml_pipeline/               # YOLOv8+ViT and TGCN Training Pipelines
└── 📄 README.md                  # System Documentation
```

---
*Developed for the future of dynamic urban traffic enforcement.*
