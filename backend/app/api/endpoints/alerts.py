from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
import os
from .predict import get_inference_engine
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import crud
from app.services.sms_service import send_twilio_sms

router = APIRouter()

class RegistrationRequest(BaseModel):
    name: str
    phone: str
    commodity: str
    state: str
    mandi: str

@router.post("/register")
async def register_user_for_alerts(req: RegistrationRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        engine = get_inference_engine(req.commodity)
        if not engine.models_loaded:
            raise HTTPException(status_code=500, detail="Inference engine not ready")
        
        results = engine.predict(req.state, req.mandi, 3) # 3 day forecast
        
        if not results or len(results) == 0:
            raise HTTPException(status_code=404, detail="No forecast data available")
        
        today_price = results[0]['price_p50']
        
        # Save registration to Database
        crud.create_alert_subscription(
            db=db,
            name=req.name,
            phone=req.phone,
            commodity=req.commodity,
            state=req.state,
            mandi=req.mandi
        )

        # Build message
        msg_lines = [
            f"Vanakkam {req.name}! 🌱",
            f"Today's price for {req.commodity.capitalize()} in {req.mandi.capitalize()} is ₹{today_price:,.0f}/qtl.",
            "3-Day AI Forecast:"
        ]
        
        for i, row in enumerate(results[:3]):
            day_str = "Tomorrow" if i == 0 else f"Day {i+1}"
            msg_lines.append(f"{day_str}: ₹{row['price_p50']:,.0f}")
            
        msg_lines.append("- ANSH-M Agri-Intelligence")
        
        final_msg = "\n".join(msg_lines)
        
        # Send SMS in background
        background_tasks.add_task(send_twilio_sms, req.phone, final_msg)
        
        return {"status": "success", "message": "User registered and SMS enqueued"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-trigger")
async def test_alert_automation(background_tasks: BackgroundTasks):
    """
    Manually triggers the daily alert process for verification.
    """
    from app.services.scheduler import daily_morning_alerts
    # Run daily_morning_alerts in the background
    background_tasks.add_task(daily_morning_alerts)
    return {"status": "triggered", "detail": "Daily morning alerts task has been pushed to background."}

@router.post("/test-spike")
async def test_spike_automation(background_tasks: BackgroundTasks):
    """
    Manually triggers the price spike monitor for verification.
    """
    from app.services.scheduler import price_spike_monitor
    background_tasks.add_task(price_spike_monitor)
    return {"status": "triggered", "detail": "Price spike monitor task has been pushed to background."}
