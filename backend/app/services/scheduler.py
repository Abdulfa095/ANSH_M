from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.sms_service import send_twilio_sms
from app.api.endpoints.predict import get_inference_engine
from app.db.database import SessionLocal
from app.db import models
import os
import asyncio
from datetime import datetime

scheduler = AsyncIOScheduler()

async def daily_morning_alerts():
    """Fetches all subscriptions and sends the daily forecast SMS."""
    print(f"[{datetime.now()}] Running daily morning alerts task...")
    db = SessionLocal()
    try:
        subscriptions = db.query(models.AlertSubscription).all()
        print(f"Found {len(subscriptions)} active subscriptions.")
        
        for sub in subscriptions:
            try:
                engine = get_inference_engine(sub.commodity)
                # sub is a SQLAlchemy model instance
                results = engine.predict(sub.state, sub.mandi, 3)
                
                if results:
                    today_price = results[0]['price_p50']
                    msg_lines = [
                        f"Vanakkam {sub.name}! 🌅",
                        f"Mornin' Price for {sub.commodity.capitalize()} in {sub.mandi.capitalize()}: ₹{today_price:,.0f}/qtl",
                        "3-Day outlook:"
                    ]
                    for i, row in enumerate(results[:3]):
                        day_str = "Tomorrow" if i == 0 else f"Day {i+1}"
                        msg_lines.append(f"{day_str}: ₹{row['price_p50']:,.0f}")
                    
                    msg_lines.append("- ANSH-M Daily Alert")
                    message = "\n".join(msg_lines)
                    
                    send_twilio_sms(sub.phone, message)
            except Exception as e:
                print(f"Error in daily alert for {sub.phone}: {e}")
    finally:
        db.close()

async def price_spike_monitor():
    """
    Analyzes forecasts and triggers emergency alerts if a price surge > 15% is detected.
    """
    print(f"[{datetime.now()}] Running price spike monitor...")
    db = SessionLocal()
    try:
        subscriptions = db.query(models.AlertSubscription).all()
        # Group by unique commodity/mandi to avoid redundant predictions
        processed_pairs = set()
        
        for sub in subscriptions:
            key = (sub.commodity, sub.mandi, sub.state)
            if key in processed_pairs:
                continue
            processed_pairs.add(key)
            
            try:
                engine = get_inference_engine(sub.commodity)
                results = engine.predict(sub.state, sub.mandi, 2) # Today vs Tomorrow
                
                if len(results) >= 2:
                    today_price = results[0]['price_p50']
                    tomorrow_price = results[1]['price_p50']
                    
                    if today_price > 0:
                        increase_pct = (tomorrow_price - today_price) / today_price
                        
                        if increase_pct >= 0.15: # 15% Spike Threshold
                            print(f"🚨 SPIKE DETECTED: {sub.commodity} in {sub.mandi} ({increase_pct*100:.1f}%)")
                            
                            # Get all users for this specific market
                            users_to_alert = db.query(models.AlertSubscription).filter(
                                models.AlertSubscription.commodity == sub.commodity,
                                models.AlertSubscription.mandi == sub.mandi,
                                models.AlertSubscription.state == sub.state
                            ).all()
                            
                            for user in users_to_alert:
                                emergency_msg = (
                                    f"⚠️ EMERGENCY SPIKE ALERT! ⚠️\n"
                                    f"Prices for {user.commodity.capitalize()} in {user.mandi.capitalize()} "
                                    f"are predicted to surge by {increase_pct*100:.1f}% tomorrow!\n"
                                    f"Current: ₹{today_price:,.0f}\n"
                                    f"Predicted: ₹{tomorrow_price:,.0f}\n"
                                    f"- ANSH-M Smart Monitor"
                                )
                                send_twilio_sms(user.phone, emergency_msg)
            except Exception as e:
                print(f"Error in spike monitor for {sub.commodity}/{sub.mandi}: {e}")
    finally:
        db.close()

def start_scheduler():
    # Run daily at 7:00 AM
    scheduler.add_job(daily_morning_alerts, 'cron', hour=7, minute=0)
    
    # Run spike check every hour
    scheduler.add_job(price_spike_monitor, 'interval', hours=1)
    
    scheduler.start()
    print("Scheduler started!")
