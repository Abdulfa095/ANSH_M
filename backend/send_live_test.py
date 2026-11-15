import sys
import os
sys.path.append(os.getcwd())

from app.services.sms_service import send_twilio_sms
from datetime import datetime

def send_live_test():
    phone_number = "+918248808048"
    print(f"[{datetime.now()}] Initiating LIVE SMS Test to {phone_number}...")
    
    message = (
        "Vanakkam! 🌱\n"
        "This is a LIVE test from your ANSH-M Agriculture Intelligence System.\n"
        "Your SMS automation is now PROPERLY ACTIVE with real Twilio credentials!\n"
        "- ANSH-M Team"
    )
    
    success = send_twilio_sms(phone_number, message)
    if success:
        print("\n✅ LIVE SMS DISPATCHED SUCCESSFULLY!")
        print("Please check your mobile phone for the message.")
    else:
        print("\n❌ LIVE SMS DISPATCH FAILED. Check backend console for error details.")

if __name__ == "__main__":
    send_live_test()
