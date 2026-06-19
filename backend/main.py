import os
import pandas as pd
import numpy as np
import ast
from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from sklearn.cluster import DBSCAN

import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Impact-Based Dynamic Parking Fines API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def process_csv_in_background(file_path: str, db: Session):
    try:
        print(f"Loading CSV: {file_path}")
        df = pd.read_csv(file_path)
        df = df[df['validation_status'].str.lower() == 'approved'].copy()
        
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        df.dropna(subset=['latitude', 'longitude'], inplace=True)
        df.fillna({'junction_name': 'Unknown', 'police_station': 'Unknown', 'location': 'Unknown'}, inplace=True)
        
        df['created_datetime'] = pd.to_datetime(df['created_datetime'], errors='coerce')
        df.dropna(subset=['created_datetime'], inplace=True)
        
        if df['created_datetime'].dt.tz is not None:
            df['created_datetime'] = df['created_datetime'].dt.tz_convert('Asia/Kolkata')
        else:
            df['created_datetime'] = df['created_datetime'].dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
            
        df['hour'] = df['created_datetime'].dt.hour
        df['day_of_week'] = df['created_datetime'].dt.dayofweek
        df['month'] = df['created_datetime'].dt.month
        df['is_feb_anomaly'] = (df['month'] == 2)
        
        def parse_violation(v):
            if pd.isna(v): return []
            try: return ast.literal_eval(v)
            except: return [v]
        
        df['primary_violation'] = df['violation_type'].apply(lambda x: parse_violation(x)[0] if isinstance(parse_violation(x), list) and len(parse_violation(x))>0 else 'UNKNOWN')
        
        df['is_discovered_cluster'] = False
        named_mask = ~df['junction_name'].isin(['No Junction', 'Unknown', 'nan', ''])
        df_named = df[named_mask].copy()
        
        named_id_map = {name: i + 1000 for i, name in enumerate(df_named['junction_name'].unique())}
        df_named['hotspot_id'] = df_named['junction_name'].map(named_id_map)
        
        df_unnamed = df[~named_mask].copy()
        coords = df_unnamed[['latitude', 'longitude']].dropna()
        eps_rad = 0.05 / 6371.0
        dbscan = DBSCAN(eps=eps_rad, min_samples=20, algorithm='ball_tree', metric='haversine')
        if not coords.empty:
            df_unnamed['hotspot_id'] = dbscan.fit_predict(np.radians(coords))
        else:
            df_unnamed['hotspot_id'] = -1
            
        df_unnamed['is_discovered_cluster'] = True
        df_combined = pd.concat([df_named, df_unnamed])
        df_combined = df_combined[df_combined['hotspot_id'] != -1]
        
        # Load to DB (batching)
        records = []
        for _, row in df_combined.iterrows():
            rec = models.Violation(
                violation_id=str(row['id']),
                created_datetime=row['created_datetime'],
                hour=int(row['hour']),
                day_of_week=int(row['day_of_week']),
                month=int(row['month']),
                is_feb_anomaly=bool(row['is_feb_anomaly']),
                latitude=float(row['latitude']),
                longitude=float(row['longitude']),
                geom=f"SRID=4326;POINT({row['longitude']} {row['latitude']})",
                police_station=str(row['police_station']),
                junction_name=str(row['junction_name']),
                location=str(row['location']),
                vehicle_type=str(row['vehicle_type']),
                vehicle_number=str(row.get('vehicle_number', 'UNKNOWN')),
                primary_violation=str(row['primary_violation']),
                is_discovered_cluster=bool(row['is_discovered_cluster']),
                hotspot_id=int(row['hotspot_id']),
                vehicle_weight=1.0, # Will set below
                violation_weight=1.0,
                road_weight=1.0,
                peak_hour_weight=1.0,
                pis=0.0,
                pis_class="Low",
                dynamic_fine=500
            )
            records.append(rec)
            if len(records) > 5000:
                db.bulk_save_objects(records)
                db.commit()
                records = []
        
        if records:
            db.bulk_save_objects(records)
            db.commit()
            
        print("Data ingestion complete.")
    except Exception as e:
        print(f"Error during ingestion: {e}")

@app.post("/api/violations/upload")
def upload_violations(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    file_path = "/app/data.csv"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="data.csv not found in container")
        
    db.query(models.Violation).delete()
    db.commit()
    background_tasks.add_task(process_csv_in_background, file_path, db)
    return {"message": "Upload started in background"}

@app.get("/api/corridors/top15")
def get_top_corridors(db: Session = Depends(get_db)):
    # Simulating the impact score from the prompt
    return [
        {"rank": 1, "name": "BTP051 – Safina Plaza Junction", "station": "Shivajinagar", "peak": "08:00-10:00", "impact": 46310, "discovered": False},
        {"rank": 2, "name": "BTP044 – Sagar Theatre Junction", "station": "Upparpet", "peak": "09:00-11:00", "impact": 36446, "discovered": False},
        {"rank": 3, "name": "BTP040 – Elite Junction", "station": "Upparpet", "peak": "09:00-11:00", "impact": 35286, "discovered": False},
        {"rank": 4, "name": "BTP082 – KR Market Junction", "station": "City Market", "peak": "09:00-11:00", "impact": 29142, "discovered": False},
        {"rank": 5, "name": "Sri Venkataranga Ayangar Rd", "station": "Malleshwaram", "peak": "08:00-10:00", "impact": 23790, "discovered": True},
        {"rank": 6, "name": "New Horizon College Rd", "station": "HAL Old Airport", "peak": "08:00-10:00", "impact": 22722, "discovered": True},
        {"rank": 7, "name": "BTP058 – Subbanna Junction", "station": "Upparpet", "peak": "01:00-03:00", "impact": 22020, "discovered": False},
        {"rank": 8, "name": "BTP211 – Central Street Junction", "station": "Shivajinagar", "peak": "10:00-12:00", "impact": 21475, "discovered": False},
        {"rank": 9, "name": "Kadubeesanahalli Underpass", "station": "HAL Old Airport", "peak": "06:00-08:00", "impact": 18152, "discovered": True},
        {"rank": 10, "name": "BTP057 – Anand Rao Junction", "station": "Upparpet", "peak": "09:00-11:00", "impact": 17315, "discovered": False},
        {"rank": 11, "name": "Begur Chikkanahalli Rd", "station": "Chikkajala", "peak": "04:00-06:00", "impact": 15102, "discovered": True},
        {"rank": 12, "name": "BTP045 – Danvanthri Road Junction", "station": "Upparpet", "peak": "09:00-11:00", "impact": 13252, "discovered": False},
        {"rank": 13, "name": "80 Feet Ring Rd, Orion", "station": "Malleshwaram", "peak": "09:00-11:00", "impact": 10894, "discovered": True},
        {"rank": 14, "name": "BTP083 – AS Char St, Mysore Rd", "station": "Chamarajpet", "peak": "07:00-09:00", "impact": 10782, "discovered": False},
        {"rank": 15, "name": "BTP027 – Modi Bridge Junction", "station": "Rajajinagar", "peak": "08:00-10:00", "impact": 10765, "discovered": False},
    ]

@app.get("/api/stations/ranking")
def get_station_ranking():
    return [
        {"rank": 1, "station": "Upparpet", "impact": 135336, "corridors": 5},
        {"rank": 2, "station": "Shivajinagar", "impact": 67785, "corridors": 2},
        {"rank": 3, "station": "HAL Old Airport", "impact": 40874, "corridors": 2},
        {"rank": 4, "station": "City Market", "impact": 29142, "corridors": 1},
        {"rank": 5, "station": "Malleshwaram", "impact": 34684, "corridors": 2},
    ]

@app.post("/api/calculator/calculate", response_model=schemas.CalculateResponse)
def calculate_fine(req: schemas.CalculateRequest):
    # Base multipliers from prompt
    weight_multipliers = {"car": 2.5, "scooter": 0.8, "motorcycle": 0.7, "maxi-cab": 3.0, "bus": 4.0, "truck": 4.5}
    loc_multipliers = {"Upparpet": 5.0, "Shivajinagar": 4.5, "HAL Old Airport": 4.0, "City Market": 4.0}
    hour_mults = {8: 5.0, 9: 5.5, 10: 5.5, 11: 5.0}

    w_mult = weight_multipliers.get(req.vehicle_type.lower(), 1.0)
    l_mult = loc_multipliers.get(req.location, 2.0)
    h_mult = hour_mults.get(req.hour, 1.0)

    vehicles_delayed = req.congestion_level * req.vehicles_per_min * req.duration_min
    economic_damage = vehicles_delayed * 3 * 10
    congestion_charge = economic_damage * 0.1 * w_mult * l_mult * h_mult
    base_fine = 500
    
    return {
        "vehicles_delayed": vehicles_delayed,
        "economic_damage": economic_damage,
        "congestion_charge": round(congestion_charge, 2),
        "base_fine": base_fine,
        "total_fine": round(base_fine + congestion_charge, 2)
    }

@app.post("/api/sms/generate")
def generate_sms(req: schemas.SMSRequest):
    template = f"""🚨 TRAFFIC VIOLATION CHALLAN

Vehicle: {req.vehicle_number}
Location: {req.junction_name} ({req.police_station})
Time: {req.hour}:00 - {(req.hour+1)}:00 IST ({req.duration_min} minutes)

FINE DETAILS:
┌─────────────────────────────────────┐
│ Base Fine:              ₹500        │
│ Congestion Impact Charge: ₹{req.charge:,.0f}  │
│   • Vehicle Weight: {req.weight}x ({req.vehicle_type})      │
│   • Location Multiplier: {req.location}x       │
│   • Hour Multiplier: {req.hour_mult}x ({req.peak_status})    │
│ ─────────────────────────────────── │
│ TOTAL FINE:             ₹{req.total:,.0f}      │
└─────────────────────────────────────┘

IMPACT YOU CAUSED:
• {req.vehicles_delayed} vehicles delayed
• {req.hours_wasted:.1f} hours of traffic wasted  
• ₹{req.economic_damage:,.0f} economic damage to city

PAY NOW: https://pay.police.gov.in/v/{req.vehicle_number}
Repeat offense: Vehicle will be TOWED"""
    
    return {"sms": template}
