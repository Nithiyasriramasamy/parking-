from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON
from geoalchemy2 import Geometry
from database import Base

class Violation(Base):
    __tablename__ = "violations"
    
    id = Column(Integer, primary_key=True, index=True)
    violation_id = Column(String, index=True)
    created_datetime = Column(DateTime)
    hour = Column(Integer)
    day_of_week = Column(Integer)
    month = Column(Integer)
    is_feb_anomaly = Column(Boolean, default=False)
    
    latitude = Column(Float)
    longitude = Column(Float)
    geom = Column(Geometry(geometry_type='POINT', srid=4326))
    
    police_station = Column(String)
    junction_name = Column(String)
    location = Column(String)
    
    vehicle_type = Column(String)
    vehicle_number = Column(String)
    primary_violation = Column(String)
    
    is_discovered_cluster = Column(Boolean, default=False)
    hotspot_id = Column(Integer, nullable=True)
    
    # Impact calculations
    vehicle_weight = Column(Float)
    violation_weight = Column(Float)
    road_weight = Column(Float)
    peak_hour_weight = Column(Float)
    pis = Column(Float)
    pis_class = Column(String)
    dynamic_fine = Column(Integer)

class Settings(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(JSON)
