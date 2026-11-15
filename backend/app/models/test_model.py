import torch
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

from app.ingestion.fusion import DataFusionPipeline
from app.models.tft import TFT
from app.models.deep_extrema import DeepExtrema

# Configuration - All India Major Onion Mandis
MANDI_CONFIG = [
    {'name': 'Dindigul', 'lat': 10.36, 'lon': 77.98, 'state': 'Tamil Nadu'},
    {'name': 'Bangalore', 'lat': 12.97, 'lon': 77.59, 'state': 'Karnataka'},
    {'name': 'Kurnool', 'lat': 15.83, 'lon': 78.04, 'state': 'Andhra Pradesh'},
    {'name': 'Nashik', 'lat': 19.99, 'lon': 73.78, 'state': 'Maharashtra'},
    {'name': 'Rajkot', 'lat': 22.30, 'lon': 70.78, 'state': 'Gujarat'},
    {'name': 'Indore', 'lat': 22.72, 'lon': 75.86, 'state': 'Madhya Pradesh'},
    {'name': 'Ludhiana', 'lat': 30.90, 'lon': 75.86, 'state': 'Punjab'},
    {'name': 'Karnal', 'lat': 29.69, 'lon': 76.98, 'state': 'Haryana'},
    {'name': 'Lucknow', 'lat': 26.85, 'lon': 80.95, 'state': 'Uttar Pradesh'},
    {'name': 'Jaipur', 'lat': 26.91, 'lon': 75.79, 'state': 'Rajasthan'},
    {'name': 'Delhi', 'lat': 28.61, 'lon': 77.23, 'state': 'Delhi'},
    {'name': 'Kolkata', 'lat': 22.57, 'lon': 88.36, 'state': 'West Bengal'},
    {'name': 'Patna', 'lat': 25.61, 'lon': 85.14, 'state': 'Bihar'},
    {'name': 'Bhubaneswar', 'lat': 20.30, 'lon': 85.82, 'state': 'Odisha'},
    {'name': 'Guwahati', 'lat': 26.14, 'lon': 91.74, 'state': 'Assam'},
]
COMMODITY = 'Onion'
# Fetch enough data to form at least one sequence (30 days)
START_DATE = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d") 
END_DATE = datetime.now().strftime("%Y-%m-%d")
SEQ_LEN = 30
HIDDEN_DIM = 64

def prepare_input(df, seq_len):
    """
    Prepares a single sequence for inference with normalization.
    Returns: [1, Seq_Len, Features], scaler_dict
    """
    import json
    
    # Feature selection matching train.py
    df = df.fillna(method='ffill').fillna(method='bfill')
    feature_cols = ['modal_price', 'max_temp', 'min_temp', 'precipitation', 'soil_moisture', 'sentiment']
    
    available_features = [c for c in feature_cols if c in df.columns]
    if not available_features:
        print("Model features missing in data!")
        return None, None
    
    # Load scaler
    scaler_path = os.path.join(os.path.dirname(__file__), 'saved', 'scaler.json')
    scaler = {}
    if os.path.exists(scaler_path):
        with open(scaler_path, 'r') as f:
            scaler = json.load(f)
        print("Scaler loaded for normalization.")
    else:
        print("Warning: No scaler found. Predictions may be inaccurate.")
    
    data_raw = df[available_features].values
    
    # Normalize using saved scaler
    data = np.zeros_like(data_raw, dtype=np.float32)
    for i, col in enumerate(available_features):
        if col in scaler:
            col_range = scaler[col]['max'] - scaler[col]['min']
            if col_range > 0:
                data[:, i] = (data_raw[:, i] - scaler[col]['min']) / col_range
            else:
                data[:, i] = 0.0
        else:
            data[:, i] = data_raw[:, i] # Fallback: no normalization
    
    # Handle insufficient data by padding
    if len(data) < seq_len:
        print(f"Warning: Only {len(data)} records available. Padding with first record to reach {seq_len}.")
        padding_len = seq_len - len(data)
        first_record = data[0]
        padding = np.tile(first_record, (padding_len, 1))
        seq = np.vstack([padding, data])
    else:
        seq = data[-seq_len:]
        
    return torch.FloatTensor(np.array([seq])), scaler

def denormalize_price(value, scaler):
    """Convert normalized value back to real price."""
    if 'modal_price' in scaler:
        price_min = scaler['modal_price']['min']
        price_range = scaler['modal_price']['max'] - price_min
        return value * price_range + price_min
    return value

def main():
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='ANSH-M Price Prediction')
    parser.add_argument('--state', type=str, default=None, 
                        help='State to predict for (e.g., "Tamil Nadu", "Punjab")')
    args = parser.parse_args()
    
    # Get available states
    available_states = list(set(m['state'] for m in MANDI_CONFIG))
    available_states.sort()
    
    # If no state specified, show menu
    if args.state is None:
        print("=" * 40)
        print("ANSH-M Price Prediction System")
        print("=" * 40)
        print("\nAvailable States:")
        for i, state in enumerate(available_states, 1):
            print(f"  {i}. {state}")
        print(f"\nUsage: python -m app.models.test_model --state \"State Name\"")
        print(f"Example: python -m app.models.test_model --state \"Punjab\"")
        return
    
    # Find matching state (case-insensitive)
    selected_state = None
    for state in available_states:
        if state.lower() == args.state.lower():
            selected_state = state
            break
    
    if selected_state is None:
        print(f"Error: State '{args.state}' not found!")
        print(f"Available states: {', '.join(available_states)}")
        return
    
    # Filter mandi config for selected state
    selected_mandis = [m for m in MANDI_CONFIG if m['state'] == selected_state]
    
    print(f"--- ANSH-M Prediction: {COMMODITY} in {selected_state} ---")
    
    # 1. Load Data
    print("Fetching recent data...")
    pipeline = DataFusionPipeline()
    df = pipeline.create_training_dataset(selected_mandis, COMMODITY, START_DATE, END_DATE, max_records=1000)
    
    if df.empty:
        print("No data fetched.")
        return
        
    print(f"Fetched {len(df)} records.")
    
    # 2. Prepare Input
    result = prepare_input(df, SEQ_LEN)
    if result[0] is None:
        return
    input_tensor, scaler = result
        
    input_dim = input_tensor.shape[2]
    print(f"Input Shape: {input_tensor.shape}")

    # 3. Load Models
    print("\nLoading models...")
    tft = TFT(input_dim=input_dim, hidden_dim=HIDDEN_DIM, output_dim=1)
    de = DeepExtrema(input_dim=input_dim, hidden_dim=HIDDEN_DIM)
    
    try:
        tft.load_state_dict(torch.load("app/models/saved/tft_onion.pth"))
        de.load_state_dict(torch.load("app/models/saved/deep_extrema_onion.pth"))
        print("Models loaded successfully.")
    except Exception as e:
        print(f"Error loading models: {e}")
        print("Make sure you have trained the models first (python -m app.models.train)")
        return

    # 4. Inference
    tft.eval()
    de.eval()
    
    with torch.no_grad():
        # TFT Prediction
        tft_out = tft(input_tensor)
        next_step_pred = tft_out[0, -1, :] # [P10, P50, P90]
        
        # Denormalize predictions back to real price
        p10 = denormalize_price(next_step_pred[0].item(), scaler)
        p50 = denormalize_price(next_step_pred[1].item(), scaler)
        p90 = denormalize_price(next_step_pred[2].item(), scaler)
        
        # DeepExtrema Prediction
        mu, sigma, xi = de(input_tensor)
        
    # 5. Display Results
    last_price = df['modal_price'].iloc[-1]
    last_date = pd.to_datetime(df['date'].iloc[-1]).strftime('%Y-%m-%d') if 'date' in df.columns else 'Unknown'
    
    print("\n" + "="*40)
    print(f"  PREDICTION FOR: {COMMODITY} in {selected_state}")
    print("="*40)
    print(f"  Prediction Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"  Last Known Price: ₹{last_price:.2f} (as of {last_date})")
    print("-" * 40)
    print(f"  FORECAST (Next Day):")
    print(f"  📉 P10 (Low):      ₹{p10:.2f}")
    print(f"  📊 P50 (Expected): ₹{p50:.2f}")
    print(f"  📈 P90 (High):     ₹{p90:.2f}")
    print("-" * 40)
    print(f"  RISK ANALYSIS (DeepExtrema):")
    print(f"  Mu: {mu.item():.4f}  Sigma: {sigma.item():.4f}  Xi: {xi.item():.4f}")
    
    # Risk interpretation
    risk_level = "LOW ✅"
    if xi.item() > 0.1 or p90 > p50 * 1.5:
        risk_level = "HIGH ⚠️ (Potential Spike)"
    elif xi.item() > 0.05:
        risk_level = "MEDIUM 🟡"
    print(f"  Risk Level: {risk_level}")
    print("="*40)

if __name__ == "__main__":
    main()
