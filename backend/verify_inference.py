
import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.engine.inference import InferenceEngine

def verify_inference():
    print("--- Verifying Inference Engine Setup ---")
    
    # 1. Check Files
    base_path = "app/models/saved"
    required_files = [
        "scaler_onion.json",
        "tft_onion.pth",
        "deep_extrema_onion.pth"
    ]
    
    missing = []
    for f in required_files:
        path = os.path.join(base_path, f)
        if not os.path.exists(path):
            print(f"❌ Missing: {path}")
            missing.append(f)
        else:
            print(f"✅ Found: {path}")
            
    if missing:
        print("CRITICAL: Missing model files. Inference will fail.")
        return

    # 2. Load Engine
    print("\nLoading Inference Engine for 'Onion'...")
    try:
        engine = InferenceEngine(commodity="onion")
        if engine.models_loaded:
            print("✅ Engine loaded successfully.")
        else:
            print("❌ Engine failed to load models.")
            return
    except Exception as e:
        print(f"❌ Exception loading engine: {e}")
        return

    # 3. Test Prediction for User Request
    print("\nTesting Prediction for User Request: (Tamil Nadu, Madurai)...")
    try:
        # Real Inference attempt
        results = engine.predict(state="Tamil Nadu", mandi="Madurai", days=7)
        
        if results:
            print("✅ Prediction Successful for Madurai!")
            for i, r in enumerate(results):
                day_label = "Today" if i == 0 else f"Day {i}"
                print(f"   [{day_label}] {r['date']} - P50: ₹{r['price_p50']} (Range: ₹{r['price_p10']} - ₹{r['price_p90']})")
            
            trend = "Up" if results[-1]['price_p50'] > results[0]['price_p50'] else "Down"
            print(f"   Overall 7-Day Trend: {trend}")
            
            if any(r['is_extreme'] for r in results):
                print("   ⚠️ EXTREME VOLATILITY DETECTED in the 7-day window")
        else:
            print("⚠️ Prediction returned None.")
            print("   Possible reasons:")
            print("   1. Agmarknet API has no recent data for 'Madurai' + 'Onion'")
            print("   2. API Rate limit reached")
            
    except Exception as e:
        print(f"❌ Prediction failed with error: {e}")

if __name__ == "__main__":
    verify_inference()
