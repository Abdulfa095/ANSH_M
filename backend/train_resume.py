"""
train_resume.py  –  Resumable all-mandi training for ANSH-M
============================================================
• Saves a per-mandi data checkpoint after each mandi is fetched.
• On restart, skips mandis whose checkpoint already exists.
• Retries up to 5 times with exponential back-off on 5xx errors.
• After ALL mandi data is collected, trains TFT + DeepExtrema and
  saves models as  tft_onion_all.pth / deep_extrema_onion_all.pth
  (or a different commodity if --commodity flag is given).

Usage:
    python train_resume.py              # trains Onion (default)
    python train_resume.py --commodity Tomato
    python train_resume.py --reset      # clears checkpoints and starts fresh
"""

import sys
import os
import json
import time
import argparse
from datetime import datetime, timedelta

import torch
import pandas as pd
import numpy as np

# ──────────────────────────────────────────────────────────────────────────────
# Path setup
# ──────────────────────────────────────────────────────────────────────────────
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ingestion.fusion import DataFusionPipeline
from app.ingestion.weather import WeatherClient
from app.ingestion.satellite import SatelliteDataMock
from app.ingestion.agmarknet import AgmarknetClient
from app.models.tft import TFT
from app.models.deep_extrema import DeepExtrema
from app.models.train import train_tft, train_deep_extrema, prepare_tft_data, get_state
from app.utils.mandi_coords import MANDI_COORDS

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────
START_DATE  = (datetime.now() - timedelta(days=365 * 2)).strftime("%Y-%m-%d")
END_DATE    = datetime.now().strftime("%Y-%m-%d")
SEQ_LEN     = 30
PREDICT_LEN = 7
HIDDEN_DIM  = 64
EPOCHS      = 10
MAX_RECORDS = 50_000
MAX_RETRIES = 5

# Real data cache produced by fetch_real_data.py
REAL_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/real")


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def checkpoint_path(checkpoint_dir: str, mandi_name: str, commodity: str) -> str:
    safe = mandi_name.replace(" ", "_").replace("/", "_")
    return os.path.join(checkpoint_dir, f"{safe}_{commodity.lower()}.csv")


def progress_file(checkpoint_dir: str, commodity: str) -> str:
    return os.path.join(checkpoint_dir, f"progress_{commodity.lower()}.json")


def load_progress(prog_file: str):
    if os.path.exists(prog_file):
        with open(prog_file) as f:
            return json.load(f)
    return {"completed": [], "failed": []}


def save_progress(prog_file: str, progress: dict):
    with open(prog_file, "w") as f:
        json.dump(progress, f, indent=2)


def generate_synthetic(mandi_name: str, state: str, commodity: str) -> pd.DataFrame:
    """Fall-back: realistic synthetic daily prices for the date range."""
    dates = pd.date_range(start=START_DATE, end=END_DATE)
    base_price = 2000
    noise       = np.random.normal(0, 100, len(dates))
    trend       = np.linspace(0, 500, len(dates))
    seasonality = 300 * np.sin(2 * np.pi * dates.day_of_year / 365)
    prices      = np.clip(base_price + trend + seasonality + noise, 500, 10_000)
    return pd.DataFrame({
        "date":        dates,
        "modal_price": prices,
        "min_price":   prices - 200,
        "max_price":   prices + 200,
        "market":      mandi_name,
        "commodity":   commodity,
        "state":       state,
    })


def fetch_with_retry(agmarknet: AgmarknetClient, state: str, commodity: str,
                     limit: int, offset: int) -> pd.DataFrame:
    """Fetch one page of data with exponential back-off."""
    for attempt in range(MAX_RETRIES):
        try:
            df = agmarknet.fetch_data(
                filters={"state": state, "commodity": commodity},
                limit=limit,
                offset=offset,
            )
            return df
        except Exception as e:
            wait = 5 * (2 ** attempt)     # 5, 10, 20, 40, 80 s
            print(f"  [Retry {attempt+1}/{MAX_RETRIES}] Error: {e}  – waiting {wait}s …")
            time.sleep(wait)
    return pd.DataFrame()


def fetch_mandi_prices(agmarknet: AgmarknetClient, mandi: dict, commodity: str) -> pd.DataFrame:
    """Paginate through Agmarknet to get price data for one mandi/state."""
    page_size  = 500
    import math
    num_pages  = math.ceil(MAX_RECORDS / page_size)
    all_pages  = []

    for page in range(num_pages):
        current_limit = min(page_size, MAX_RECORDS - page * page_size)
        if current_limit <= 0:
            break
        print(f"  Fetching page {page+1}/{num_pages} …", end=" ", flush=True)
        df_page = fetch_with_retry(agmarknet, mandi["state"], commodity,
                                   limit=current_limit, offset=page * page_size)
        if df_page.empty:
            print("no more data.")
            break
        all_pages.append(df_page)
        print(f"{len(df_page)} records")
        time.sleep(2)   # polite rate-limit

    return pd.concat(all_pages, ignore_index=True) if all_pages else pd.DataFrame()


def add_weather_satellite(df: pd.DataFrame, mandi: dict, weather: WeatherClient,
                          satellite: SatelliteDataMock) -> pd.DataFrame:
    """Merge weather + satellite into the price dataframe."""
    weather_df    = weather.fetch_historical_weather(mandi["lat"], mandi["lon"], START_DATE, END_DATE)
    satellite_df  = satellite.fetch_ndvi_timeseries(mandi["lat"], mandi["lon"], START_DATE, END_DATE)

    if not weather_df.empty and "date" in weather_df.columns:
        weather_df["date"] = pd.to_datetime(weather_df["date"])
        df = pd.merge(df, weather_df, on="date", how="left")

    if not satellite_df.empty and "date" in satellite_df.columns:
        satellite_df["date"] = pd.to_datetime(satellite_df["date"])
        df = pd.merge(df, satellite_df[["date", "ndvi"]], on="date", how="left")

    return df


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--commodity", default="Onion")
    parser.add_argument("--reset",     action="store_true",
                        help="Clear checkpoints and start over")
    args = parser.parse_args()

    commodity      = args.commodity
    checkpoint_dir = os.path.join(os.path.dirname(__file__),
                                  f"data/checkpoints/{commodity.lower()}")
    os.makedirs(checkpoint_dir, exist_ok=True)

    prog_file = progress_file(checkpoint_dir, commodity)

    # ── Reset if requested ────────────────────────────────────────────────────
    if args.reset:
        import shutil
        if os.path.exists(checkpoint_dir):
            shutil.rmtree(checkpoint_dir)
        os.makedirs(checkpoint_dir, exist_ok=True)
        print("✅ Checkpoints cleared. Starting fresh.")

    # ── Build mandi list ──────────────────────────────────────────────────────
    mandi_config = []
    for name, coords in MANDI_COORDS.items():
        state = get_state(name)
        if state != "Unknown":
            mandi_config.append({"name": name, "lat": coords[0],
                                  "lon": coords[1], "state": state})
    print(f"\n{'='*60}")
    print(f"  ANSH-M Resumable Training  |  Commodity: {commodity}")
    print(f"  Total mandis: {len(mandi_config)}")
    print(f"  Date range  : {START_DATE} → {END_DATE}")
    print(f"{'='*60}\n")

    # ── Load progress ─────────────────────────────────────────────────────────
    progress = load_progress(prog_file)
    completed = set(progress["completed"])
    failed    = set(progress["failed"])

    remaining = [m for m in mandi_config if m["name"] not in completed]
    print(f"Already completed: {len(completed)}/{len(mandi_config)} mandis")
    print(f"Remaining        : {len(remaining)} mandis\n")

    if not remaining:
        print("All mandis already fetched. Proceeding to training …")
    else:
        # Initialise clients
        agmarknet = AgmarknetClient()
        weather   = WeatherClient()
        satellite = SatelliteDataMock()

        for idx, mandi in enumerate(remaining, 1):
            print(f"\n[{idx}/{len(remaining)}] ── Processing {mandi['name']} ({mandi['state']}) ──")
            ckpt = checkpoint_path(checkpoint_dir, mandi["name"], commodity)

            if os.path.exists(ckpt):
                print(f"  ✓ Checkpoint exists, skipping fetch.")
                completed.add(mandi["name"])
                progress["completed"] = list(completed)
                save_progress(prog_file, progress)
                continue

            prices = pd.DataFrame()

            # ── 1a. Check real data cache (from fetch_real_data.py) ───────────
            real_dir  = os.path.join(REAL_DATA_DIR, commodity.lower())
            safe_name = mandi["name"].replace(" ","_").replace("(","").replace(")","").replace("/","_")
            real_file = os.path.join(real_dir, f"{safe_name}.csv")

            if os.path.exists(real_file):
                real_df = pd.read_csv(real_file)
                is_synth = real_df.get("_synthetic", pd.Series([False])).any()
                tag = "synthetic cache" if is_synth else "REAL cache"
                prices = real_df
                print(f"  ✓ Loaded from {tag}: {len(prices)} rows")
            else:
                # ── 1b. Fetch via market-name API call ────────────────────────
                print(f"  Fetching via market name API...")
                try:
                    prices = agmarknet.fetch_market_history(
                        market    = mandi["name"],
                        state     = mandi["state"],
                        commodity = commodity,
                        max_rows  = 2000,
                    )
                    if not prices.empty:
                        if "arrival_date" in prices.columns:
                            prices["date"] = pd.to_datetime(prices["arrival_date"],
                                                            dayfirst=True, errors="coerce")
                        prices["modal_price"] = pd.to_numeric(
                            prices.get("modal_price", np.nan), errors="coerce")
                        prices = prices.dropna(subset=["date","modal_price"])
                        prices = prices.sort_values("date")
                        if len(prices) >= 30:
                            print(f"  ✅ Got {len(prices)} REAL rows")
                        else:
                            print(f"  ⚠ Only {len(prices)} rows — falling back to synthetic")
                            prices = pd.DataFrame()
                    else:
                        prices = pd.DataFrame()
                except Exception as e:
                    print(f"  ⚠ API error: {e}")
                    prices = pd.DataFrame()

            # ── 1c. Final fallback: synthetic ─────────────────────────────────
            if prices.empty:
                print(f"  ⚠ No data from API. Using synthetic data.")
                prices = generate_synthetic(mandi["name"], mandi["state"], commodity)
                # Standardise columns
                prices.columns = [c.replace(" ", "_") for c in prices.columns]
                if "arrival_date" in prices.columns:
                    prices["date"] = pd.to_datetime(prices["arrival_date"],
                                                    dayfirst=True, errors="coerce")
                    prices = prices.dropna(subset=["date"])
                elif "date" not in prices.columns:
                    print("  ⚠ No date column found. Using synthetic data.")
                    prices = generate_synthetic(mandi["name"], mandi["state"], commodity)

                # Filter to the mandi itself if possible
                if "market" in prices.columns:
                    mandi_rows = prices[prices["market"] == mandi["name"]]
                    if len(mandi_rows) >= 50:
                        prices = mandi_rows
                    # else keep state-level data

            # 2. Add weather + satellite
            try:
                prices = add_weather_satellite(prices, mandi, weather, satellite)
            except Exception as e:
                print(f"  ⚠ Weather/satellite fetch failed: {e}")

            prices["mandi_name"] = mandi["name"]
            prices["lat"]        = mandi["lat"]
            prices["lon"]        = mandi["lon"]

            # 3. Save checkpoint
            prices.to_csv(ckpt, index=False)
            print(f"  ✅ Saved {len(prices)} rows → {os.path.basename(ckpt)}")

            completed.add(mandi["name"])
            if mandi["name"] in failed:
                failed.discard(mandi["name"])
            progress["completed"] = list(completed)
            progress["failed"]    = list(failed)
            save_progress(prog_file, progress)

    # ── Collate all checkpoints ───────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(" Collating all checkpoint files …")
    print(f"{'='*60}")

    frames = []
    for name, _ in MANDI_COORDS.items():
        ckpt = checkpoint_path(checkpoint_dir, name, commodity)
        if os.path.exists(ckpt):
            df = pd.read_csv(ckpt)
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
            frames.append(df)

    if not frames:
        print("❌ No checkpoint files found. Cannot train.")
        return

    full_df = pd.concat(frames, ignore_index=True)
    print(f"Total collated rows: {len(full_df)}")

    # ── Prepare sequences ─────────────────────────────────────────────────────
    print("\nPreparing TFT sequences …")
    X, Y = prepare_tft_data(full_df, SEQ_LEN, PREDICT_LEN, commodity_name=commodity)

    if X is None:
        print("❌ Insufficient data for sequence generation.")
        return

    print(f"Training shapes: X={X.shape}, Y={Y.shape}")
    input_dim = X.shape[2]

    # ── Initialise models (optionally load existing) ──────────────────────────
    save_dir  = os.path.join(os.path.dirname(__file__), "app/models/saved")
    os.makedirs(save_dir, exist_ok=True)

    tft_path = os.path.join(save_dir, f"tft_{commodity.lower()}_all.pth")
    de_path  = os.path.join(save_dir, f"deep_extrema_{commodity.lower()}_all.pth")

    tft_model = TFT(input_dim=input_dim, hidden_dim=HIDDEN_DIM, output_dim=1)
    de_model  = DeepExtrema(input_dim=input_dim, hidden_dim=HIDDEN_DIM)

    # Resume model weights if they already exist (partial training)
    if os.path.exists(tft_path):
        print(f"  Loading existing TFT weights from {tft_path}")
        tft_model.load_state_dict(torch.load(tft_path, map_location="cpu"))

    if os.path.exists(de_path):
        print(f"  Loading existing DeepExtrema weights from {de_path}")
        de_model.load_state_dict(torch.load(de_path, map_location="cpu"))

    # ── Train ─────────────────────────────────────────────────────────────────
    print("\n[1/2] Training Temporal Fusion Transformer …")
    tft_model = train_tft(tft_model, X, Y, epochs=EPOCHS)

    torch.save(tft_model.state_dict(), tft_path)
    print(f"  ✅ TFT saved → {tft_path}")

    print("\n[2/2] Training DeepExtrema …")
    de_model = train_deep_extrema(de_model, X, Y, epochs=EPOCHS)

    torch.save(de_model.state_dict(), de_path)
    print(f"  ✅ DeepExtrema saved → {de_path}")

    print(f"\n{'='*60}")
    print(f"  🎉 Training complete for {commodity}!")
    print(f"  Models saved to: {save_dir}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
