def generate_voice_script(location: str, penalty_range: str = "500 to 5,000") -> str:
    """
    Generates TwiML (Twilio Markup Language) for an automated voice call.
    In a real implementation, this would be returned as XML.
    """
    script = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Aditi" language="en-IN">
        Hello. This is an automated alert from the Bengaluru Traffic Police.
    </Say>
    <Pause length="1"/>
    <Say voice="Polly.Aditi" language="en-IN">
        Your vehicle is currently parked illegally at {location}.
        You are causing a severe traffic bottleneck.
    </Say>
    <Pause length="1"/>
    <Say voice="Polly.Aditi" language="en-IN">
        Please remove your vehicle within the next 10 minutes.
        Failure to do so will result in an automatic e-challan of Rupees {penalty_range}, and your vehicle may be towed.
    </Say>
    <Say voice="Polly.Aditi" language="en-IN">
        Thank you for your cooperation.
    </Say>
</Response>"""
    return script
