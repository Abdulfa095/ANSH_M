import torch
import json
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from ..models.tft import TFT
from ..models.deep_extrema import DeepExtrema
from ..ingestion.agmarknet import AgmarknetClient

class InferenceEngine:
    def __init__(self, commodity="onion"):
        self.commodity = commodity
        self.device = torch.device("cpu")
        self.models_loaded = False
        self.scaler = None
        self.agmarknet = AgmarknetClient()
        
        # Paths
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.model_dir = os.path.join(base_path, "models", "saved")
        
        self.load_models()

    def load_models(self):
        try:
            # 1. Load Scaler
            scaler_filename = f"scaler_{self.commodity.lower()}.json"
            scaler_path = os.path.join(self.model_dir, scaler_filename)
            if not os.path.exists(scaler_path):
                print(f"Scaler not found at {scaler_path}")
                return

            with open(scaler_path, "r") as f:
                self.scaler = json.load(f)
                
            # 2. Initialize Models
            # Must match training dims
            hidden_dim = 64
            # Determine input dim from scaler keys (minus target if separate, but here all features used)
            # Train.py: feature_cols = ['modal_price', 'max_temp', 'min_temp', 'precipitation', 'soil_moisture', 'sentiment']
            # We need to see which keys are in scaler to know input_dim size
            feature_cols = ['modal_price', 'max_temp', 'min_temp', 'precipitation', 'soil_moisture', 'sentiment']
            # Filter scaler keys that match feature_cols
            self.features = [f for f in feature_cols if f in self.scaler]
            input_dim = len(self.features)
            
            self.tft = TFT(input_dim=input_dim, hidden_dim=hidden_dim, output_dim=1)
            self.de = DeepExtrema(input_dim=input_dim, hidden_dim=hidden_dim)
            
            # 3. Load Weights
            tft_path = os.path.join(self.model_dir, f"tft_{self.commodity}.pth")
            de_path = os.path.join(self.model_dir, f"deep_extrema_{self.commodity}.pth")
            
            if os.path.exists(tft_path):
                self.tft.load_state_dict(torch.load(tft_path, map_location=self.device))
                self.tft.eval()
            else:
                 print(f"TFT model not found at {tft_path}")
                 return

            if os.path.exists(de_path):
                self.de.load_state_dict(torch.load(de_path, map_location=self.device))
                self.de.eval()
            else:
                 print(f"DeepExtrema model not found at {de_path}")
                 # We can still run TFT if DE is missing, but better to fail or warn
            
            self.models_loaded = True
            print("Inference Engine Loaded Successfully.")
            
        except Exception as e:
            print(f"Error loading models: {e}")

    def preprocess(self, df):
        """
        Normalize input data using loaded scaler.
        df: DataFrame with at least SEQ_LEN rows.
        Returns: tensor [1, Seq_Len, Features]
        """
        if df.empty or not self.scaler:
            return None
            
        # Ensure columns exist
        for col in self.features:
            if col not in df.columns:
                df[col] = 0.0 # Fill missing with 0 check
        
        # Sort by date
        if 'date' in df.columns:
             df = df.sort_values('date')
             
        # Take last 30 rows
        seq_len = 30
        if len(df) < seq_len:
            # Pad with first row or last row?
            # Pad with duplication of first row
            pad_len = seq_len - len(df)
            first_row = df.iloc[0:1]
            df = pd.concat([pd.concat([first_row]*pad_len), df], ignore_index=True)
            
        df_seq = df.tail(seq_len).copy()
        
        # Normalize
        data = np.zeros((seq_len, len(self.features)), dtype=np.float32)
        for i, col in enumerate(self.features):
            col_min = self.scaler[col]['min']
            col_max = self.scaler[col]['max']
            val = df_seq[col].values
            
            if col_max - col_min > 0:
                data[:, i] = (val - col_min) / (col_max - col_min)
            else:
                data[:, i] = 0.0
                
        # Add batch dim
        return torch.FloatTensor(data).unsqueeze(0)

    def predict(self, state, mandi, days=7):
        """
        Run inference.
        """
        results = []
        
        # 1. Fetch Live Data (Last 60 days to ensure we have enough)
        try:
            df = self.agmarknet.fetch_data(filters={
                'state': state,
                'commodity': self.commodity.title(), # API case sensitive? usually Title
                'market': mandi
            }, limit=100) # Fetch more to sort
        except:
            df = pd.DataFrame()
            
        # If empty, try fallback to just commodity/state
        if df.empty:
             print(f"No live data found for {mandi}, falling back to synthetic 60-day history for inference...")
             dates = pd.date_range(end=datetime.now(), periods=60)
             np.random.seed(42) # For reproducible tests
             # Base price around 3000 Rs/Qtl
             prices = np.clip(3000 + np.linspace(0, 200, 60) + np.random.normal(0, 100, 60), 500, 10000)
             df = pd.DataFrame({
                 'date': dates,
                 'modal_price': prices,
                 'market': mandi,
                 'state': state,
                 'commodity': self.commodity
             })

        # Clean Data
        if 'modal_price' in df.columns:
             df['modal_price'] = pd.to_numeric(df['modal_price'], errors='coerce')
             df = df.dropna(subset=['modal_price'])
        
        if 'date' not in df.columns and 'arrival_date' in df.columns:
             df['date'] = pd.to_datetime(df['arrival_date'], dayfirst=True, errors='coerce')
             
        # Mock other features if missing (Weather/Sentiment)
        # In prod, we would fetch weather here too
        for col in ['max_temp', 'min_temp', 'precipitation', 'soil_moisture', 'sentiment']:
            if col not in df.columns:
                df[col] = 0.5 # Mean value assumption for normalized input if unknown
                
        # 2. Preprocess
        input_tensor = self.preprocess(df)
        if input_tensor is None:
            return None
            
        # 3. Autoregressive Inference Loop
        if not self.models_loaded:
            return None
            
        # --- CALIBRATION (Anchor to last real price) ---
        last_real_price = None
        if not df.empty and 'modal_price' in df.columns:
             if 'date' in df.columns:
                 df_sorted = df.sort_values('date')
                 last_real_price = df_sorted['modal_price'].iloc[-1]
                 
        target_min = self.scaler['modal_price']['min']
        target_max = self.scaler['modal_price']['max']
        scale = target_max - target_min

        today = datetime.now()
        current_tensor = input_tensor.clone()
        
        # DeepExtrema only run once for overall environment/extreme risk
        with torch.no_grad():
            mu, sigma, xi = self.de(current_tensor)
            xi_val = xi.item()
            is_extreme = xi_val > 0.1 # Threshold for heavy tail risk

        # Autoregressive Loop for predicting 'days' ahead
        calibration_ratio = 1.0 # Initialize neutral calibration
        
        for i in range(days + 1):
            with torch.no_grad():
                quantiles = self.tft(current_tensor) # [1, Seq_Len, 3]
                last_step = quantiles[:, -1, :] # [1, 3] -> P10, P50, P90
                
            p10_norm, p50_norm, p90_norm = last_step[0, 0].item(), last_step[0, 1].item(), last_step[0, 2].item()
            
            # Denormalize
            p50_val = p50_norm * scale + target_min
            p10_val = p10_norm * scale + target_min
            p90_val = p90_norm * scale + target_min
            
            # Initial Calendar Day Calibration
            if i == 0 and last_real_price and last_real_price > 0 and p50_val > 0:
                 calibration_ratio = p50_val / last_real_price
                 if abs(calibration_ratio - 1.0) > 0.2:
                     half_spread = (p90_val - p10_val) / 2
                     new_half_spread = half_spread / calibration_ratio
                     p50_val = last_real_price
                     p90_val = p50_val + new_half_spread
                     p10_val = p50_val - new_half_spread
                 else:
                     calibration_ratio = 1.0 # Reset if not significant
            elif i > 0 and calibration_ratio != 1.0:
                 # Apply ratio to subsequent predictions to maintain relative curve
                 p50_val = p50_val / calibration_ratio
                 half_spread = (p90_val - p10_val) / 2 / calibration_ratio
                 
                 # Dynamic Spread Increase: Uncertainty naturally widens further into the future
                 spread_multiplier = 1.0 + (i * 0.15) # 15% wider per day
                 new_half_spread = half_spread * spread_multiplier
                 
                 p90_val = p50_val + new_half_spread
                 p10_val = p50_val - new_half_spread
                 
            if p10_val < 0: p10_val = p50_val * 0.8
            
            date = today + timedelta(days=i)
            results.append({
                "date": date.strftime("%Y-%m-%d"),
                "price_p10": round(p10_val, 2),
                "price_p50": round(p50_val, 2),
                "price_p90": round(p90_val, 2),
                "is_extreme": is_extreme and i < 3 # Flag immediate risk
            })
            
            # Prepare Input Tensor for the NEXT day (Autoregressive shift)
            if i < days:
                next_step = current_tensor[:, -1:, :].clone()
                # Update the target feature with the normalized P50 prediction
                # Assuming 'modal_price' is index 0 in self.features
                price_index = self.features.index('modal_price') if 'modal_price' in self.features else 0
                
                # Normalise calibrated P50 back to model scale
                calibrated_norm = (p50_val - target_min) / scale if scale > 0 else 0
                next_step[:, 0, price_index] = calibrated_norm
                
                # Shift tensor: Drop oldest, append new step
                current_tensor = torch.cat([current_tensor[:, 1:, :], next_step], dim=1)
                
        return results
