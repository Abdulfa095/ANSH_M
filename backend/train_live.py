
import sys
import os
from datetime import datetime, timedelta

# Add backend directory to sys.path to allow imports from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ingestion.fusion import DataFusionPipeline
from app.models.tft import TFT
from app.models.deep_extrema import DeepExtrema
from app.models.train import train_tft, train_deep_extrema, prepare_tft_data
import torch
import pandas as pd

def train_live_demo(commodity="Onion"):
    print(f"--- Starting Live Data Training Demo for {commodity} ---")
    
    # 1. Define Target Mandis (Focus on major hubs to save time)
    # Lasalgaon is the biggest Onion mandi in Asia
    target_mandis = [
        {'name': 'Lasalgaon', 'lat': 20.1477, 'lon': 74.2255, 'state': 'Maharashtra'},
        {'name': 'Pune', 'lat': 18.5204, 'lon': 73.8567, 'state': 'Maharashtra'},
        {'name': 'Bangalore', 'lat': 12.9716, 'lon': 77.5946, 'state': 'Karnataka'},
        {'name': 'Azadpur', 'lat': 28.7041, 'lon': 77.1025, 'state': 'NCT of Delhi'} # Often just 'Delhi' in API
    ]
    
    print(f"Targeting {len(target_mandis)} major mandis for rapid live calibration.")
    
    pipeline = DataFusionPipeline()
    
    # 2. Fetch Data (Last 1 year to keep it fast but relevant)
    start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"Fetching LIVE data from Agmarknet ({start_date} to {end_date})...")
    
    # Modify pipeline call to be robust
    try:
        df = pipeline.create_training_dataset(target_mandis, commodity, start_date, end_date, max_records=2000)
    except Exception as e:
        print(f"Error in pipeline: {e}")
        return

    if df.empty:
        print("CRITICAL: No data fetched. API might be down or key invalid.")
        return

    print(f"Successfully fetched {len(df)} records.")
    
    # 3. Train
    print("Preprocessing...")
    SEQ_LEN = 30
    PREDICT_LEN = 7
    
    X, Y = prepare_tft_data(df, SEQ_LEN, PREDICT_LEN, commodity_name=commodity)
    
    if X is None:
        print("Insufficient data for sequence generation.")
        return

    print(f"Training on {len(X)} sequences...")
    
    input_dim = X.shape[2]
    HIDDEN_DIM = 64
    
    # Initialize models
    tft_model = TFT(input_dim=input_dim, hidden_dim=HIDDEN_DIM, output_dim=1)
    de_model = DeepExtrema(input_dim=input_dim, hidden_dim=HIDDEN_DIM)
    
    # Train
    print("Training TFT...")
    tft_model = train_tft(tft_model, X, Y, epochs=5) # 5 epochs for demo speed
    
    print("Training DeepExtrema...")
    de_model = train_deep_extrema(de_model, X, Y, epochs=5)
    
    # Save
    save_dir = "app/models/saved"
    os.makedirs(save_dir, exist_ok=True)
    
    tft_path = f"{save_dir}/tft_{commodity.lower()}.pth"
    de_path = f"{save_dir}/deep_extrema_{commodity.lower()}.pth"
    
    torch.save(tft_model.state_dict(), tft_path)
    torch.save(de_model.state_dict(), de_path)
    
    print(f"✅ Models calibrated on LIVE data and saved to:")
    print(f"   - {tft_path}")
    print(f"   - {de_path}")

if __name__ == "__main__":
    train_live_demo("Onion")
