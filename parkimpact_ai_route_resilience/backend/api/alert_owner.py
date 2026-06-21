from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import datetime
import os
import threading
from .voice_script import generate_voice_script

try:
    from twilio.rest import Client
except ImportError:
    Client = None

router = APIRouter()

# In-memory mock database for tracking active countdowns
active_alerts: Dict[str, Any] = {}

class AlertRequest(BaseModel):
    vehicle_plate: str
    owner_phone: str
    location: str

def escalate_to_fine(alert_id: str):
    """Background task that runs after 15 seconds to simulate E-Challan issuance"""
    if alert_id in active_alerts:
        if active_alerts[alert_id]["status"] == "COUNTDOWN_ACTIVE":
            active_alerts[alert_id]["status"] = "E_CHALLAN_ISSUED"
            active_alerts[alert_id]["sms_sent"] = active_alerts[alert_id]["sms_sent"] + " | E-Challan Sent"

@router.post("/alert-owner")
def dispatch_auto_alert(req: AlertRequest):
    """
    Dispatches an SMS and Voice Call to the vehicle owner.
    Starts a 15-second countdown timer for demo purposes.
    """
    dispatch_time = datetime.datetime.now()
    deadline = dispatch_time + datetime.timedelta(seconds=15)
    alert_id = f"ALT-{req.vehicle_plate}-{int(dispatch_time.timestamp())}"
    
    sms_content = f"ASTA1 ALERT: Vehicle {req.vehicle_plate} parked illegally at {req.location}. Remove in 10 mins or face ₹500 fine."
    sms_status = "Simulated (No Twilio Keys)"
    
    # 1. Real Twilio Integration
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_number = os.environ.get("TWILIO_FROM_NUMBER")
    
    if account_sid and auth_token and from_number and Client:
        try:
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                body=sms_content,
                from_=from_number,
                to=req.owner_phone
            )
            sms_status = f"Sent Real SMS (SID: {message.sid})"
        except Exception as e:
            sms_status = f"Failed to send: {str(e)}"
    
    # 2. Mock Voice Call Dispatch
    voice_twiml = generate_voice_script(req.location)

    # 3. Save to active alerts
    active_alerts[alert_id] = {
        "vehicle_plate": req.vehicle_plate,
        "phone": req.owner_phone,
        "location": req.location,
        "status": "COUNTDOWN_ACTIVE",
        "deadline": deadline.isoformat(),
        "sms_sent": sms_status,
        "call_initiated": True
    }
    
    # 4. Start 15-second AI escalation timer
    threading.Timer(15.0, escalate_to_fine, args=(alert_id,)).start()

    return {
        "status": "success",
        "message": "Alert dispatched successfully. 15-second countdown started.",
        "alert_id": alert_id,
        "sms_status": sms_status,
        "mock_voice_preview": "Voice call initiated via Twilio TwiML."
    }

@router.get("/active-alerts")
def get_active_alerts():
    """Returns all active countdown alerts for the dashboard."""
    if not active_alerts:
        now = datetime.datetime.now()
        active_alerts["ALT-MOCK-1"] = {
            "vehicle_plate": "KA-01-AB-1234",
            "phone": "+91 98765 43210",
            "location": "Indiranagar 100ft Road",
            "status": "COUNTDOWN_ACTIVE",
            "deadline": (now + datetime.timedelta(minutes=4)).isoformat(),
            "sms_sent": "Simulated",
            "call_initiated": True
        }
        active_alerts["ALT-MOCK-2"] = {
            "vehicle_plate": "KA-05-MN-4567",
            "phone": "+91 99887 76655",
            "location": "MG Road",
            "status": "E_CHALLAN_ISSUED",
            "deadline": (now - datetime.timedelta(minutes=5)).isoformat(),
            "sms_sent": "Simulated",
            "call_initiated": True
        }
    return active_alerts
