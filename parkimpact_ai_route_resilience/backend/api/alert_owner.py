from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import datetime
import os
from .voice_script import generate_voice_script

router = APIRouter()

# In-memory mock database for tracking active countdowns
active_alerts: Dict[str, Any] = {}

class AlertRequest(BaseModel):
    vehicle_plate: str
    owner_phone: str
    location: str

@router.post("/alert-owner")
def dispatch_auto_alert(req: AlertRequest):
    """
    Dispatches an SMS and Voice Call to the vehicle owner.
    Starts a 10-minute countdown timer.
    """
    # 1. Mock Twilio Integration (Showcase Mode)
    # Bypassing strict credential checks for the hackathon demo

    # 2. Mock SMS Dispatch
    sms_content = f"BTP ALERT: Your vehicle ({req.vehicle_plate}) is parked illegally at {req.location}. Remove within 10 min to avoid ₹500-₹5,000 fine."
    
    # 3. Mock Voice Call Dispatch
    voice_twiml = generate_voice_script(req.location)

    # 4. Start Countdown
    dispatch_time = datetime.datetime.now()
    deadline = dispatch_time + datetime.timedelta(minutes=10)
    
    alert_id = f"ALT-{req.vehicle_plate}-{int(dispatch_time.timestamp())}"
    
    active_alerts[alert_id] = {
        "vehicle_plate": req.vehicle_plate,
        "phone": req.owner_phone,
        "location": req.location,
        "status": "COUNTDOWN_ACTIVE",
        "deadline": deadline.isoformat(),
        "sms_sent": True,
        "call_initiated": True
    }

    return {
        "status": "success",
        "message": "Alerts dispatched successfully. 10-minute countdown started.",
        "alert_id": alert_id,
        "mock_sms_preview": sms_content,
        "mock_voice_preview": "Voice call initiated via Twilio TwiML."
    }

@router.get("/active-alerts")
def get_active_alerts():
    """Returns all active countdown alerts for the dashboard."""
    # In a real app, we would dynamically check if the timer expired.
    # For the mock dashboard, we will just return the active dict, and maybe inject some fake ones.
    
    # Inject some fake ones if empty to make the dashboard look good
    if not active_alerts:
        now = datetime.datetime.now()
        active_alerts["ALT-MOCK-1"] = {
            "vehicle_plate": "KA-01-AB-1234",
            "phone": "+91 98765 43210",
            "location": "Indiranagar 100ft Road",
            "status": "COUNTDOWN_ACTIVE",
            "deadline": (now + datetime.timedelta(minutes=4)).isoformat(),
            "sms_sent": True,
            "call_initiated": True
        }
        active_alerts["ALT-MOCK-2"] = {
            "vehicle_plate": "KA-03-XY-9876",
            "phone": "+91 91234 56789",
            "location": "Silk Board Junction",
            "status": "REMOVED_VOLUNTARILY",
            "deadline": (now - datetime.timedelta(minutes=2)).isoformat(),
            "sms_sent": True,
            "call_initiated": True
        }
        active_alerts["ALT-MOCK-3"] = {
            "vehicle_plate": "KA-05-MN-4567",
            "phone": "+91 99887 76655",
            "location": "MG Road",
            "status": "E_CHALLAN_ISSUED",
            "deadline": (now - datetime.timedelta(minutes=5)).isoformat(),
            "sms_sent": True,
            "call_initiated": True
        }
        
    return active_alerts
