import sys
import os
sys.path.append(os.getcwd())

from app.db.database import SessionLocal, engine
from app.db import models
from app.services.scheduler import daily_morning_alerts, price_spike_monitor
import asyncio

async def test_automation():
    print("Testing SMS Automation...")
    db = SessionLocal()
    
    # 1. Ensure at least one subscription exists
    sub = db.query(models.AlertSubscription).first()
    if not sub:
        print("Adding dummy subscription for testing...")
        new_sub = models.AlertSubscription(
            name="Test Farmer",
            phone="+919876543210",
            commodity="onion",
            state="Maharashtra",
            mandi="Lasalgaon"
        )
        db.add(new_sub)
        db.commit()
        sub = new_sub
    
    print(f"Testing with user: {sub.name} ({sub.phone})")
    
    # 2. Test Daily Alerts
    print("\n--- Triggering Daily Alerts ---")
    await daily_morning_alerts()
    
    # 3. Test Spike Monitor
    print("\n--- Triggering Price Spike Monitor ---")
    await price_spike_monitor()
    
    db.close()
    print("\nTest Complete. check the console output above for 'MOCK SMS SENT'.")

if __name__ == "__main__":
    asyncio.run(test_automation())
