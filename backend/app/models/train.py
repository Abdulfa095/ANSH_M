import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
import os
import json
from datetime import datetime, timedelta
from app.ingestion.fusion import DataFusionPipeline
from app.models.tft import TFT
from app.models.deep_extrema import DeepExtrema, extreme_value_loss
from app.utils.mandi_coords import MANDI_COORDS

# Configuration 
# Convert MANDI_COORDS dict to list of dicts expected by fusion pipeline
MANDI_CONFIG = []
for name, coords in MANDI_COORDS.items():
    # Simple state mapping (heuristic or could be improved)
    # For now, we rely on the fusion pipeline to find the state or we add it to coords if needed.
    # Fusion pipeline expects 'state' key. 
    # We need to add state to MANDI_COORDS or infer it here.
    # Actually, the user's mandi_coords.py has comments separating states. 
    # Let's make a helper to guess state or clearer: 
    # We will just iterate and try to map. 
    # For this implementation, I will manually map a few important ones or uses a mapping dict.
    pass

# Refined approach: Define explicit list or modify MANDI_COORDS to include state.
# Since modifying MANDI_COORDS is cleaner but might break other things, 
# let's just define the list of ALL mandis with their states here based on the coords file knowledge.
# OR, use a simple mapping function.

def get_state(mandi_name):
    """
    Maps a mandi name to its Indian state.
    - Uzhavar Sandhai / APMC suffix → Tamil Nadu (keyword catch-all)
    - Border mandis from KL / KA / AP have explicit sets
    - All other mandis use a plain lookup dict
    """
    # ── Tamil Nadu: all Uzhavar Sandhai / APMC mandis ─────────────
    if "Uzhavar Sandhai" in mandi_name or mandi_name.endswith("APMC"):
        return "Tamil Nadu"

    # ── Border mandis ─────────────────────────────────────────────
    kerala_mandis = {
        "Palakkad", "Ottapalam", "Thrissur", "Ernakulam",
        "Thiruvananthapuram", "Kollam", "Kottayam",
        "Mananthavady", "Sultan Bathery", "Palakkad Jn",
    }
    if mandi_name in kerala_mandis:
        return "Kerala"

    karnataka_border = {
        "Chamarajnagar", "Kollegal", "Gundlupet", "Bandipur",
        "Anekal", "Yelandur", "Electronic City",
    }
    if mandi_name in karnataka_border:
        return "Karnataka"

    ap_border = {"Chittoor", "Puttur", "Gudupalli", "Kavali"}
    if mandi_name in ap_border:
        return "Andhra Pradesh"

    # ── Explicit lookup for all other states ──────────────────────
    state_map = {
        # Maharashtra
        "Lasalgaon": "Maharashtra", "Pimpalgaon Baswant": "Maharashtra",
        "Pinoalgaon Baswant": "Maharashtra",
        "Nashik": "Maharashtra", "Pune": "Maharashtra", "Mumbai": "Maharashtra",
        "Vashi": "Maharashtra", "Nagpur": "Maharashtra", "Solapur": "Maharashtra",
        "Kolhapur": "Maharashtra", "Aurangabad": "Maharashtra", "Ahmednagar": "Maharashtra",
        "Rahata": "Maharashtra", "Sangli": "Maharashtra", "Satara": "Maharashtra",
        "Amravati": "Maharashtra", "Yeola": "Maharashtra", "Manmad": "Maharashtra",
        "Chandwad": "Maharashtra", "Kalvan": "Maharashtra", "Satana": "Maharashtra",
        "Malegaon": "Maharashtra",
        # Punjab
        "Ludhiana": "Punjab", "Amritsar": "Punjab", "Jalandhar": "Punjab",
        "Patiala": "Punjab", "Bathinda": "Punjab", "Khanna": "Punjab",
        "Moga": "Punjab", "Firozpur": "Punjab", "Hoshiarpur": "Punjab",
        "Pathankot": "Punjab", "Sahnewal": "Punjab",
        # Haryana
        "Karnal": "Haryana", "Panipat": "Haryana", "Ambala": "Haryana",
        "Hisar": "Haryana", "Rohtak": "Haryana", "Sonipat": "Haryana",
        "Gurgaon": "Haryana", "Faridabad": "Haryana", "Sirsa": "Haryana",
        "Fatehabad": "Haryana",
        # Uttar Pradesh
        "Lucknow": "Uttar Pradesh", "Kanpur": "Uttar Pradesh", "Agra": "Uttar Pradesh",
        "Varanasi": "Uttar Pradesh", "Ghaziabad": "Uttar Pradesh", "Meerut": "Uttar Pradesh",
        "Aligarh": "Uttar Pradesh", "Bareilly": "Uttar Pradesh",
        "Moradabad": "Uttar Pradesh", "Gorakhpur": "Uttar Pradesh", "Allahabad": "Uttar Pradesh",
        # Madhya Pradesh
        "Indore": "Madhya Pradesh", "Bhopal": "Madhya Pradesh", "Jabalpur": "Madhya Pradesh",
        "Gwalior": "Madhya Pradesh", "Ujjain": "Madhya Pradesh", "Sagar": "Madhya Pradesh",
        "Dewas": "Madhya Pradesh", "Satna": "Madhya Pradesh", "Ratlam": "Madhya Pradesh",
        # Rajasthan
        "Jaipur": "Rajasthan", "Jodhpur": "Rajasthan", "Kota": "Rajasthan",
        "Bikaner": "Rajasthan", "Ajmer": "Rajasthan", "Udaipur": "Rajasthan",
        "Bhilwara": "Rajasthan", "Alwar": "Rajasthan",
        # Gujarat
        "Ahmedabad": "Gujarat", "Surat": "Gujarat", "Vadodara": "Gujarat",
        "Rajkot": "Gujarat", "Bhavnagar": "Gujarat", "Jamnagar": "Gujarat",
        "Junagadh": "Gujarat", "Gandhinagar": "Gujarat",
        # Karnataka
        "Bangalore": "Karnataka", "Mysore": "Karnataka", "Hubli": "Karnataka",
        "Mangalore": "Karnataka", "Belgaum": "Karnataka", "Gulbarga": "Karnataka",
        "Davangere": "Karnataka", "Bellary": "Karnataka",
        # Tamil Nadu (plain names for backward compat)
        "Nagercoil": "Tamil Nadu", "Pollachi": "Tamil Nadu", "Coimbatore": "Tamil Nadu",
        "Chennai": "Tamil Nadu", "Madurai": "Tamil Nadu", "Tiruchirappalli": "Tamil Nadu",
        "Salem": "Tamil Nadu", "Tirunelveli": "Tamil Nadu", "Erode": "Tamil Nadu",
        "Vellore": "Tamil Nadu", "Dindigul": "Tamil Nadu",
        # Andhra Pradesh
        "Visakhapatnam": "Andhra Pradesh", "Vijayawada": "Andhra Pradesh",
        "Guntur": "Andhra Pradesh", "Nellore": "Andhra Pradesh",
        "Kurnool": "Andhra Pradesh", "Rajahmundry": "Andhra Pradesh",
        "Kakinada": "Andhra Pradesh", "Tirupati": "Andhra Pradesh",
        # Telangana
        "Hyderabad": "Telangana", "Warangal": "Telangana", "Nizamabad": "Telangana",
        "Karimnagar": "Telangana", "Khammam": "Telangana", "Ramagundam": "Telangana",
        "Mahbubnagar": "Telangana", "Nalgonda": "Telangana",
        # West Bengal
        "Kolkata": "West Bengal", "Howrah": "West Bengal", "Durgapur": "West Bengal",
        "Asansol": "West Bengal", "Siliguri": "West Bengal", "Bardhaman": "West Bengal",
        "Malda": "West Bengal", "Kharagpur": "West Bengal",
    }
    return state_map.get(mandi_name, "Unknown")
    
MANDI_CONFIG = []
for name, coords in MANDI_COORDS.items():
    state = get_state(name)
    if state != "Unknown":
        MANDI_CONFIG.append({
            'name': name,
            'lat': coords[0],
            'lon': coords[1],
            'state': state
        })

COMMODITY = 'Onion'
# 2 years of data is sufficient for prototype
TRAIN_START_DATE = (datetime.now() - timedelta(days=365*2)).strftime("%Y-%m-%d") 
TRAIN_END_DATE = datetime.now().strftime("%Y-%m-%d")
SEQ_LEN = 30 # 30 days lookback
PREDICT_LEN = 7 # 7 days forecast
BATCH_SIZE = 64 # Increased batch size for larger dataset
EPOCHS = 10 
HIDDEN_DIM = 64

def prepare_tft_data(df, seq_len, predict_len, commodity_name="onion"):
    """
    Prepares sequences for TFT with Global Min-Max normalization.
    Groups by mandi to ensure sequences don't cross mandi boundaries.
    
    X: [Batch, Seq_Len, Features]
    Y: [Batch, Predict_Len] (Target Price)
    """
    
    if 'mandi_name' not in df.columns and 'market' in df.columns:
        df['mandi_name'] = df['market']
    
    # Fill missing values and replace infinities
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.ffill().bfill()
    df = df.fillna(0)  # Final safety net
    
    feature_cols = ['modal_price', 'max_temp', 'min_temp', 'precipitation', 'soil_moisture', 'sentiment']
    target_col = 'modal_price'
    
    # Check if columns exist
    available_features = [c for c in feature_cols if c in df.columns]
    print(f"DEBUG: Available Features: {available_features}")
    
    if not available_features:
        print("No features found in dataframe!")
        return None, None
    
    # --- GLOBAL SCALER CALCULATION ---
    # We calculate min/max across the ENTIRE dataset (all mandis)
    data_raw = df[available_features].values.astype(np.float32)
    target_raw = df[target_col].values.astype(np.float32)
    
    # Replace any remaining NaN/Inf in numpy arrays
    data_raw = np.nan_to_num(data_raw, nan=0.0, posinf=0.0, neginf=0.0)
    target_raw = np.nan_to_num(target_raw, nan=0.0, posinf=0.0, neginf=0.0)
    
    scaler = {}
    for i, col in enumerate(available_features):
        col_min = float(data_raw[:, i].min())
        col_max = float(data_raw[:, i].max())
        scaler[col] = {'min': col_min, 'max': col_max}
    
    # Save scaler for inference
    scaler_filename = f"scaler_{commodity_name.lower()}.json"
    scaler_path = os.path.join(os.path.dirname(__file__), 'saved', scaler_filename)
    os.makedirs(os.path.dirname(scaler_path), exist_ok=True)
    with open(scaler_path, 'w') as f:
        json.dump(scaler, f)
    print(f"Global Scaler saved: {scaler_path}")
    
    # --- SEQUENCE GENERATION PER MANDI ---
    X_all, Y_all = [], []
    
    # Group by mandi to avoid mixing series
    grouped = df.groupby('mandi_name')
    
    print(f"Processing sequences for {len(grouped)} mandis...")
    
    for mandi_name, mandi_df in grouped:
        mandi_df = mandi_df.sort_values('date') # Ensure time order
        
        # Normalize this mandi's data using GLOBAL scaler
        mandi_data_raw = mandi_df[available_features].values.astype(np.float32)
        mandi_target_raw = mandi_df[target_col].values.astype(np.float32)
        
        # Clean NaN/Inf per mandi
        mandi_data_raw = np.nan_to_num(mandi_data_raw, nan=0.0, posinf=0.0, neginf=0.0)
        mandi_target_raw = np.nan_to_num(mandi_target_raw, nan=0.0, posinf=0.0, neginf=0.0)
        
        data = np.zeros_like(mandi_data_raw, dtype=np.float32)
        for i, col in enumerate(available_features):
            col_range = scaler[col]['max'] - scaler[col]['min']
            if col_range > 0:
                data[:, i] = (mandi_data_raw[:, i] - scaler[col]['min']) / col_range
            else:
                data[:, i] = 0.0
        
        # Normalize target
        target_min = scaler['modal_price']['min']
        target_range = scaler['modal_price']['max'] - target_min
        if target_range > 0:
            target = (mandi_target_raw - target_min) / target_range
        else:
            target = np.zeros_like(mandi_target_raw)
            
        # Create sequences
        if len(data) < seq_len + predict_len:
            continue # Skip if not enough data for this mandi
            
        for i in range(len(data) - seq_len - predict_len):
            X_all.append(data[i : i+seq_len])
            Y_all.append(target[i+seq_len : i+seq_len+predict_len])
            
    if not X_all:
        print("No valid sequences generated from any mandi.")
        return None, None

    X_tensor = torch.FloatTensor(np.array(X_all))
    Y_tensor = torch.FloatTensor(np.array(Y_all))
    
    # Final NaN check on tensors
    X_tensor = torch.nan_to_num(X_tensor, nan=0.0)
    Y_tensor = torch.nan_to_num(Y_tensor, nan=0.0)
    
    print(f"DEBUG: X has NaN: {torch.isnan(X_tensor).any()}, Y has NaN: {torch.isnan(Y_tensor).any()}")
    
    return X_tensor, Y_tensor

def quantile_loss(preds, target, quantiles=[0.1, 0.5, 0.9]):
    """
    preds: [Batch, Seq_Len/Pred_Len, 3] -> (P10, P50, P90)
    target: [Batch, Seq_Len/Pred_Len]
    """
    losses = []
    for i, q in enumerate(quantiles):
        errors = target - preds[:, :, i]
        loss = torch.max((q-1) * errors, q * errors)
        losses.append(loss.mean())
    return sum(losses)

def train_tft(model, X, Y, epochs=EPOCHS):
    optimizer = optim.Adam(model.parameters(), lr=0.0005)
    dataset = torch.utils.data.TensorDataset(X, Y)
    loader = torch.utils.data.DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    
    print(f"Starting TFT Training for {epochs} epochs...")
    model.train()
    for epoch in range(epochs):
        epoch_loss = 0
        for batch_X, batch_Y in loader:
            optimizer.zero_grad()
            
            preds = model(batch_X) 
            
            last_step_pred = preds[:, -1, :] # [Batch, 3]
            target_next = batch_Y[:, 0] # [Batch] - Just predicting 1st day ahead
            
            # Reshape for loss
            last_step_pred = last_step_pred.unsqueeze(1) # [Batch, 1, 3]
            target_next = target_next.unsqueeze(1) # [Batch, 1]
            
            loss = quantile_loss(last_step_pred, target_next)
            
            # Skip if loss is NaN
            if torch.isnan(loss):
                print(f"WARNING: NaN loss detected in TFT, skipping batch.")
                continue
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)  # Gradient clipping
            optimizer.step()
            epoch_loss += loss.item()
            
        print(f"Epoch {epoch+1}/{epochs}, Loss: {epoch_loss/max(len(loader),1):.4f}")
    
    return model

def train_deep_extrema(model, X, Y, epochs=EPOCHS):
    optimizer = optim.Adam(model.parameters(), lr=0.0005)
    dataset = torch.utils.data.TensorDataset(X, Y)
    loader = torch.utils.data.DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    
    print(f"Starting DeepExtrema Training for {epochs} epochs...")
    model.train()
    for epoch in range(epochs):
        epoch_loss = 0
        for batch_X, batch_Y in loader:
            optimizer.zero_grad()
            
            mu, sigma, xi = model(batch_X)
            block_maxima, _ = torch.max(batch_Y, dim=1, keepdim=True)
            
            loss = extreme_value_loss(block_maxima, mu, sigma, xi)
            
            # Skip if loss is NaN
            if torch.isnan(loss):
                print(f"WARNING: NaN loss detected in DeepExtrema, skipping batch.")
                continue
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)  # Gradient clipping
            optimizer.step()
            epoch_loss += loss.item()
            
        print(f"Epoch {epoch+1}/{epochs}, Loss: {epoch_loss/max(len(loader),1):.4f}")
        
    return model

def main():
    import argparse
    parser = argparse.ArgumentParser(description='ANSH-M Model Training')
    parser.add_argument('--commodity', type=str, default='Onion',
                        help='Commodity to train for (e.g., "Onion", "Rice")')
    args = parser.parse_args()
    
    commodity = args.commodity
    commodity_lower = commodity.lower()
    
    # 1. Pipeline
    print(f"Initializing Data Pipeline for {commodity}...")
    try:
        pipeline = DataFusionPipeline()
        
        # 2. Fetch Data
        print(f"Fetching data for {commodity} across {len(MANDI_CONFIG)} mandis. This may take time...")
        try:
            # We want to fetch separate files likely, but create_training_dataset concatenates.
            # That is fine as long as we have 'mandi_name' or 'market' column to group by later.
            df = pipeline.create_training_dataset(MANDI_CONFIG, commodity, TRAIN_START_DATE, TRAIN_END_DATE, max_records=20000)
        except Exception as e:
            print(f"Error fetching data: {e}")
            df = pd.DataFrame()
            
    except ValueError as e:
        print(f"Warning: {e}")
        df = pd.DataFrame()

    if df.empty:
        print("No data fetched. Check API connectivity.")
        return

    print(f"Total Data Fetched: {len(df)} rows.")
    
    # 3. Preprocess
    print("Preprocessing & Generating Sequences...")
    X, Y = prepare_tft_data(df, SEQ_LEN, PREDICT_LEN, commodity_name=commodity)
    
    if X is None:
        return

    print(f"Training Data Summary: {len(X)} sequences generated.")
    print(f"Shape: X={X.shape}, Y={Y.shape}")
    input_dim = X.shape[2]
    
    # 4. Initialize Models
    tft_model = TFT(input_dim=input_dim, hidden_dim=HIDDEN_DIM, output_dim=1)
    de_model = DeepExtrema(input_dim=input_dim, hidden_dim=HIDDEN_DIM)
    
    # 5. Train
    tft_model = train_tft(tft_model, X, Y)
    de_model = train_deep_extrema(de_model, X, Y)
    
    # 6. Save with commodity-specific names
    os.makedirs("app/models/saved", exist_ok=True)
    torch.save(tft_model.state_dict(), f"app/models/saved/tft_{commodity_lower}.pth")
    torch.save(de_model.state_dict(), f"app/models/saved/deep_extrema_{commodity_lower}.pth")
    print(f"Models saved to app/models/saved/ (tft_{commodity_lower}.pth, deep_extrema_{commodity_lower}.pth)")

if __name__ == "__main__":
    main()
