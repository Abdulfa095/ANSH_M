from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from ...ingestion.agmarknet import AgmarknetClient
from ...engine.inference import InferenceEngine

router = APIRouter()
agmarknet = AgmarknetClient()
# Global Cache for Inference Engines
engine_cache = {}

def get_inference_engine(commodity: str):
    commodity_lower = commodity.lower()
    if commodity_lower not in engine_cache:
        print(f"Loading Inference Engine for {commodity}...")
        engine_cache[commodity_lower] = InferenceEngine(commodity=commodity_lower)
    return engine_cache[commodity_lower]

class ForecastResponse(BaseModel):
    date: str
    price_p10: float
    price_p50: float
    price_p90: float
    is_extreme: bool
    reason: Optional[str] = None

@router.get("/", response_model=List[ForecastResponse])
def get_prediction(
    commodity: str = Query(..., description="Crop name (e.g., Onion)"),
    variety: Optional[str] = Query(None, description="Commodity Variety"),
    state: str = Query(..., description="State name"),
    mandi: str = Query(..., description="Mandi name"),
    date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD) for prediction. Defaults to today."),
    days: int = Query(7, description="Forecast horizon in days"),
    current_price: Optional[float] = Query(None, description="Current price to align predictions")
):
    """
    Get price forecast for a specific commodity and mandi.
    Uses Deep Learning Models (TFT + DeepExtrema) with fallback to Smart Heuristic.
    """
    results = []
    
    # ---------------------------------------------------------
    # 1. Try ML Model Inference
    # ---------------------------------------------------------
    print(f"Attempting ML Inference for {commodity} in {mandi}...")
    try:
        # Get or Load Engine
        engine = get_inference_engine(commodity)
        
        if engine.models_loaded and engine.commodity == commodity.lower():
            ml_results = engine.predict(state, mandi, days)
            if ml_results:
                print("ML Inference Successful!")
                
                # Shift dates to the requested historical date if provided
                if date:
                    try:
                        start_date = datetime.strptime(date, "%Y-%m-%d")
                        for i, row in enumerate(ml_results):
                            current_date = start_date + timedelta(days=i)
                            row['date'] = current_date.strftime("%Y-%m-%d")
                    except ValueError:
                        pass
                
                # Anchor ML results to the real live price if provided
                if current_price is not None and len(ml_results) > 0:
                    try:
                        shift_amount = float(current_price) - ml_results[0]['price_p50']
                        for row in ml_results:
                            row['price_p50'] += shift_amount
                            row['price_p10'] += shift_amount
                            row['price_p90'] += shift_amount
                            row['price_p10'] = max(100.0, row['price_p10'])
                    except Exception as shift_e:
                        print(f"Error shifting ML prices: {shift_e}")
                
                # Add Reason for ML Inference if missing
                if len(ml_results) > 1 and 'reason' not in ml_results[-1]:
                    start_price = ml_results[0]['price_p50']
                    end_price = ml_results[-1]['price_p50']
                    change_pct = ((end_price - start_price) / start_price) * 100
                    
                    reason_text = f"Deep Learning (TFT) model projects a {change_pct:+.1f}% shift based on historical patterns and momentum."
                    if any(r.get('is_extreme', False) for r in ml_results):
                        reason_text += " DeepExtrema warns of anomaly conditions."
                    
                    ml_results[-1]['reason'] = reason_text
                    
                return ml_results
            else:
                print("ML Inference returned None (insufficient data or error). Falling back...")
        else:
             print("ML Model not loaded or commodity mismatch. Falling back...")
    except Exception as e:
        print(f"ML Inference failed: {e}. No fallback logic available.")
        raise HTTPException(status_code=500, detail="ML inference failed or no sufficient data to predict.")
        
    raise HTTPException(status_code=404, detail="No ML models or data could fulfill this request.")
