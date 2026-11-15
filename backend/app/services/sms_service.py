from twilio.rest import Client
import os
import re
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Absolute path ensure .env is loaded correctly regardless of execution context
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def format_phone_number(phone: str) -> str:
    """
    Ensures phone number is in E.164 format (+91 for India).
    """
    clean_number = re.sub(r'\D', '', str(phone))
    if len(clean_number) == 10:
        return f"+91{clean_number}"
    elif len(clean_number) == 12 and clean_number.startswith('91'):
        return f"+{clean_number}"
    elif clean_number.startswith('+'):
        return clean_number
    return f"+{clean_number}" if not clean_number.startswith('+') else clean_number

def send_twilio_sms(to_number: str, message_body: str):
    """
    Sends an SMS via Twilio with automatic formatting and error reporting.
    """
    # Reload from env in case of recent changes
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE_NUMBER")
    
    formatted_to = format_phone_number(to_number)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not all([sid, token, from_number]) or "your_" in sid:
        print(f"[{timestamp}] SMS_SIMULATION: To={formatted_to} (Missing/Invalid Credentials)")
        print(f"Content: {message_body}\n")
        return True
    
    try:
        client = Client(sid, token)
        message = client.messages.create(
            body=message_body,
            from_=from_number,
            to=formatted_to
        )
        print(f"[{timestamp}] SMS_DISPATCH_SUCCESS: SID={message.sid} To={formatted_to}")
        return True
    except Exception as e:
        print(f"[{timestamp}] SMS_DISPATCH_FAILURE: To={formatted_to} | Error: {e}")
        return False
