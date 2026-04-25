import logging
import os
from dotenv import load_dotenv
from datetime import datetime
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s"
)
log = logging.getLogger(__name__)
load_dotenv()

# 🔐 Replace with your NEW credentials
TWILIO_ACCOUNT_SID  = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN   = os.getenv("TWILIO_AUTH")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE")


# ─── Voice + language config ──────────────────────────────────────────────────
# Using Twilio's standard "alice" voice (Free tier friendly)
LANGUAGE_CONFIG = {"voice": "alice", "language": "en-IN"}

# ─────────────────────────────────────────────
# 🔊 Build dynamic message from MongoDB data
# ─────────────────────────────────────────────
def _build_message(data, is_high_risk):

    caregiver = data.get("caregiver_name", "Caregiver")
    patient   = data.get("patient_name", "Patient")
    hospital  = data.get("hospital", "Hospital")
    age       = data.get("age", "")
    condition = data.get("condition", "health condition")

    age_phrase = f", age {age}," if age else ""
    
    if is_high_risk:
        return (
            f"Hello {caregiver}. This is an important call from the Government Hospital. "
            f"{patient}{age_phrase} has been discharged. " 
            f"There is a high risk condition. Please give medicines daily without skipping. "
            f"Bring the patient for checkup within 3 days. "
            f"If the {condition} worsens, go to hospital immediately. Thank you."
        )
    else:
        return (
            f"Hello {caregiver}. {patient}{age_phrase} has been discharged from {hospital}. "
            f"Please give medicines regularly. Bring the patient for follow up within 7 days. "
            f"Thank you."
        )


# ─────────────────────────────────────────────
# 📞 Make Voice Call
# ─────────────────────────────────────────────
def make_voice_call(phone, patient_data, is_high_risk):

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # Ensure phone format
        if not phone.startswith("+"):
            phone = "+91" + phone

        message = _build_message(patient_data, is_high_risk)

        log.info(f"Calling {phone}")

        call = client.calls.create(
            to=phone,
            from_=TWILIO_PHONE_NUMBER,
            twiml=f"""
<Response>
    <Say voice="{LANGUAGE_CONFIG['voice']}" language="{LANGUAGE_CONFIG['language']}">
        {message}
    </Say>
</Response>
"""
        )

        log.info(f"Call SID: {call.sid}")

        return {
            "success": True,
            "call_sid": call.sid,
            "method": "Voice Call",
            "final_status": "Call initiated",
            "call_answered": False,
            "attempts": 1,
            "timestamp": datetime.now().isoformat()
        }

    except TwilioRestException as e:
        log.error(f"Twilio Error: {e}")

        return {
            "success": False,
            "error": str(e),
            "method": "Call Failed"
        }


# ─────────────────────────────────────────────
# 📩 SMS fallback
# ─────────────────────────────────────────────
def send_sms(phone, patient_data, is_high_risk):

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        if not phone.startswith("+"):
            phone = "+91" + phone

        patient  = patient_data.get("patient_name")
        caregiver = patient_data.get("caregiver_name")

        if is_high_risk:
            body = f"{patient} discharged. HIGH RISK. Give medicines daily. Visit hospital in 3 days."
        else:
            body = f"{patient} discharged. Give medicines regularly. Follow up in 7 days."

        msg = client.messages.create(
            to=phone,
            from_=TWILIO_PHONE_NUMBER,
            body=body
        )

        return {
            "success": True,
            "message_sid": msg.sid,
            "method": "SMS",
            "final_status": "SMS sent"
        }

    except TwilioRestException as e:
        return {
            "success": False,
            "error": str(e)
        }


# ─────────────────────────────────────────────
# 🎯 Main function (used in app.py)
# ─────────────────────────────────────────────
def notify_caregiver(patient_data, is_high_risk):

    phone = patient_data.get("caregiver_phone")

    if not phone:
        return {"success": False, "error": "No phone number"}

    # Try voice call first
    call_result = make_voice_call(phone, patient_data, is_high_risk)

    if call_result["success"]:
        return call_result

    # Fallback to SMS
    return send_sms(phone, patient_data, is_high_risk)


# ─────────────────────────────────────────────
# 🧪 Test run
# ─────────────────────────────────────────────
if __name__ == "__main__":

    test_patient = {
        "patient_name": "Ramu",
        "caregiver_name": "Lakshmi",
        "caregiver_phone": "6374858750",
        "hospital": "City Hospital",
        "age": 65,
        "condition": "breathing problem"
    }

    result = notify_caregiver(test_patient, True)
    print(result)