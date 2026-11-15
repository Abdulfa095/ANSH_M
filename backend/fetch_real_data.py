"""
fetch_real_data.py — Pre-fetch REAL Agmarknet data for all mandis
=================================================================
Queries each mandi by its exact API market name so we get real
historical price rows (not state averages).

Results saved to:  data/real/{commodity}/{market_safe}.csv

Usage:
    python fetch_real_data.py                       # Onion (default)
    python fetch_real_data.py --commodity Tomato
    python fetch_real_data.py --reset               # clear & re-fetch
"""

import sys, os, time, argparse
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.ingestion.agmarknet import AgmarknetClient
from app.models.train        import get_state
from app.utils.mandi_coords  import MANDI_COORDS

MIN_REAL_ROWS = 30          # below this: use synthetic
START_DATE    = (datetime.now() - timedelta(days=365*2)).strftime("%Y-%m-%d")
END_DATE      = datetime.now().strftime("%Y-%m-%d")

def safe_name(s):
    return s.replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")

def generate_synthetic(mandi_name, state, commodity):
    dates = pd.date_range(start=START_DATE, end=END_DATE)
    noise       = np.random.normal(0, 100, len(dates))
    trend       = np.linspace(0, 500, len(dates))
    seasonality = 300 * np.sin(2 * np.pi * dates.day_of_year / 365)
    prices      = np.clip(2000 + trend + seasonality + noise, 500, 10000)
    return pd.DataFrame({
        "date":        dates,
        "modal_price": prices.astype(float),
        "min_price":   (prices - 200).astype(float),
        "max_price":   (prices + 200).astype(float),
        "market":      mandi_name,
        "commodity":   commodity,
        "state":       state,
        "_synthetic":  True,
    })

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--commodity", default="Onion")
    parser.add_argument("--reset",     action="store_true")
    args = parser.parse_args()

    commodity = args.commodity
    out_dir   = os.path.join(os.path.dirname(__file__), f"data/real/{commodity.lower()}")
    os.makedirs(out_dir, exist_ok=True)

    if args.reset:
        import shutil; shutil.rmtree(out_dir); os.makedirs(out_dir)
        print("Checkpoints cleared.\n")

    agmarknet = AgmarknetClient()

    # Build mandi list with state info
    mandi_list = []
    for name, coords in MANDI_COORDS.items():
        state = get_state(name)
        if state != "Unknown":
            mandi_list.append({"name": name, "lat": coords[0], "lon": coords[1], "state": state})

    total   = len(mandi_list)
    results = []   # for summary table

    print(f"\n{'='*65}")
    print(f"  Real Data Pre-fetch  |  Commodity: {commodity}  |  {total} mandis")
    print(f"{'='*65}\n")
    print(f"  {'#':>4}  {'Mandi':<45} {'Rows':>6}  {'Type':>10}")
    print(f"  {'-'*4}  {'-'*45} {'-'*6}  {'-'*10}")

    for idx, mandi in enumerate(mandi_list, 1):
        fp = os.path.join(out_dir, f"{safe_name(mandi['name'])}.csv")

        # Skip if already done
        if os.path.exists(fp):
            df_ex = pd.read_csv(fp)
            is_synth = df_ex.get("_synthetic", pd.Series([False])).any()
            tag = "SYNTHETIC" if is_synth else "real"
            print(f"  {idx:>4}  {mandi['name']:<45} {len(df_ex):>6}  {tag:>10}  [cached]")
            results.append((mandi["name"], len(df_ex), tag))
            continue

        # Fetch real data by exact market name
        df = agmarknet.fetch_market_history(
            market    = mandi["name"],
            state     = mandi["state"],
            commodity = commodity,
            max_rows  = 2000,
        )

        if not df.empty:
            # Normalise date column
            if "arrival_date" in df.columns:
                df["date"] = pd.to_datetime(df["arrival_date"], dayfirst=True, errors="coerce")
            df["modal_price"] = pd.to_numeric(df.get("modal_price", np.nan), errors="coerce")
            df = df.dropna(subset=["date", "modal_price"])
            df = df.sort_values("date")

        use_synthetic = df.empty or len(df) < MIN_REAL_ROWS

        if use_synthetic:
            df = generate_synthetic(mandi["name"], mandi["state"], commodity)
            tag = "SYNTHETIC"
        else:
            df["_synthetic"] = False
            tag = "REAL"

        df["mandi_name"] = mandi["name"]
        df["lat"]        = mandi["lat"]
        df["lon"]        = mandi["lon"]

        df.to_csv(fp, index=False)
        print(f"  {idx:>4}  {mandi['name']:<45} {len(df):>6}  {tag:>10}")
        results.append((mandi["name"], len(df), tag))
        time.sleep(0.3)

    # Summary
    real_count  = sum(1 for _, _, t in results if t == "REAL")
    synth_count = sum(1 for _, _, t in results if t == "SYNTHETIC")
    total_rows  = sum(r for _, r, _ in results)

    print(f"\n{'='*65}")
    print(f"  SUMMARY")
    print(f"  Real data    : {real_count}/{total}  ({real_count/total*100:.0f}%)")
    print(f"  Synthetic    : {synth_count}/{total}  ({synth_count/total*100:.0f}%)")
    print(f"  Total rows   : {total_rows:,}")
    print(f"  Saved to     : {out_dir}")
    print(f"{'='*65}\n")
    print("Now run:")
    print(f"  python train_resume.py --commodity {commodity} --reset")
    print()

if __name__ == "__main__":
    main()
