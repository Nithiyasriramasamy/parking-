from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class CalculateRequest(BaseModel):
    congestion_level: int = 8
    vehicles_per_min: int = 3
    duration_min: int = 30
    vehicle_type: str = "Car"
    location: str = "Upparpet"
    hour: int = 9

class CalculateResponse(BaseModel):
    vehicles_delayed: int
    economic_damage: float
    congestion_charge: float
    base_fine: float
    total_fine: float

class SMSRequest(BaseModel):
    vehicle_number: str
    junction_name: str
    police_station: str
    hour: int
    duration_min: int
    charge: float
    weight: float
    vehicle_type: str
    location: float
    hour_mult: float
    peak_status: str
    total: float
    vehicles_delayed: int
    hours_wasted: float
    economic_damage: float

class SettingsRequest(BaseModel):
    vehicle_weights: Dict[str, float]
    location_multipliers: Dict[str, float]
    hour_multipliers: Dict[str, float]
