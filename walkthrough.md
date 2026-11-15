# ANSH-M Prototype Walkthrough

## How to Run
1. **Backend**:
    - **Environment**: Active `venv` in `/backend`.
    - **Command**: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
    - **Status**: **RUNNING** at `http://localhost:8000` (Docs at `/docs`)
    - **Fix**: Installed missing `twilio` dependency.

2. **Frontend**:
    - **Directory**: `/frontend`
    - **Command**: `npm run dev`
    - **Status**: **RUNNING** at `http://localhost:3000`

## Features Implemented
### 1. Forecasting Engine (ANSH-M)
- **Architecture**: Dynamic Graph Neural Network (DGNN) + Temporal Fusion Transformer (TFT) + DeepExtrema (EVT).
- **Code Locations**:
    - `backend/app/models/dgnn.py`
    - `backend/app/models/tft.py`
    - `backend/app/models/deep_extrema.py`
- **Output**: Forecasts with Confidence Intervals (P10, P50, P90) and Extreme Risk Flags.

### 2. Mandi-Connect Engine
- **Features**:
    - Real-time **Net Profit Calculation** (Price - Transport - Tax).
    - **Tax Labyrinth**: State-specific APMC tax rules (Punjab, Haryana, Maharashtra).
    - **OSRM Integration**: Route optimization (Distance & Time).
- **Code Locations**:
    - `backend/app/engine/profit_optimizer.py`
    - `backend/app/engine/tax_graph.py`

### 3. Dashboard (Frontend)
- **Tech**: Next.js 14, TailwindCSS, Recharts.
- **Components**:
    - **Price Forecast Chart**: Interactive graph showing predicted prices and risk zones.
    - **Mandi Finder**: Tool to input quantity and find the most profitable mandi.
    
## Verification Results
- **API Tests**:
    - `/predict`: Returns mock forecast data with volatility and extreme flags.
    - `/suggest`: Returns ranked mandis based on profit logic.
- **Frontend**: Successfully renders the Dashboard and fetches data from Backend.
