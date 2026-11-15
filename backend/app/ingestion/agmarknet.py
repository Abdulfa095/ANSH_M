import os
import requests
import pandas as pd
import time
import math
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

AGMARKNET_API_KEY     = os.getenv("AGMARKNET_API_KEY")
AGMARKNET_RESOURCE_ID = os.getenv("AGMARKNET_RESOURCE_ID", "9ef84268-d588-465a-a308-a864a43d0070")
BASE_URL              = f"https://api.data.gov.in/resource/{AGMARKNET_RESOURCE_ID}"

class AgmarknetClient:
    """Client for fetching live and historical mandi prices from data.gov.in"""

    def __init__(self, api_key=None):
        self.api_key = api_key or AGMARKNET_API_KEY
        if not self.api_key:
            raise ValueError("AGMARKNET_API_KEY not found in environment variables.")

    def fetch_data(self, filters=None, limit=1000, offset=0, timeout=30):
        """
        Generic fetch with any filter dict.
        filters = {'state': 'Tamil Nadu', 'commodity': 'Onion', 'market': 'Chokkikulam...'}
        """
        params = {
            "api-key": self.api_key,
            "format":  "json",
            "limit":   limit,
            "offset":  offset
        }
        if filters:
            for key, value in filters.items():
                params[f"filters[{key}]"] = value

        try:
            response = requests.get(BASE_URL, params=params, timeout=timeout)
            response.raise_for_status()
            data    = response.json()
            if "total" in data:
                print(f"Total records available: {data['total']}")
            records = data.get("records", [])
            df      = pd.DataFrame(records)
            if not df.empty:
                df.columns = [c.lower() for c in df.columns]
            return df
        except requests.exceptions.Timeout as e:
            print(f"Agmarknet API Timeout: {e}")
            raise  # Re-raise so callers can fail-fast instead of trying 5 more states
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from Agmarknet: {e}")
            return pd.DataFrame()

    def fetch_market_history(self, market: str, state: str, commodity: str,
                             variety: str = None,
                             max_rows: int = 2000, page_size: int = 500,
                             max_retries: int = 5) -> pd.DataFrame:
        """
        Fetch ALL available historical rows for a specific market by exact name.

        Uses market filter so we get mandi-specific rows, not state averages.
        Auto-paginates until no more rows are available.

        Args:
            market:     Exact API market name e.g. 'Chokkikulam(Uzhavar Sandhai ) APMC'
            state:      State name e.g. 'Tamil Nadu'
            commodity:  e.g. 'Onion'
            max_rows:   Cap on total rows
            page_size:  Rows per API call (500 is data.gov.in safe limit)
            max_retries: Retry attempts on server errors

        Returns:
            pd.DataFrame with real price rows, or empty DataFrame
        """
        all_pages  = []
        num_pages  = math.ceil(max_rows / page_size)

        for page in range(num_pages):
            offset        = page * page_size
            current_limit = min(page_size, max_rows - offset)
            if current_limit <= 0:
                break

            success = False
            for attempt in range(max_retries):
                try:
                    params = {
                        "api-key":             self.api_key,
                        "format":              "json",
                        "limit":               current_limit,
                        "offset":              offset,
                        "filters[market]":     market,
                        "filters[state]":      state,
                        "filters[commodity]":  commodity,
                    }
                    if variety:
                        params["filters[variety]"] = variety
                    resp = requests.get(BASE_URL, params=params, timeout=30)
                    resp.raise_for_status()
                    data = resp.json()

                    records = data.get("records", [])
                    if not records:
                        # No more data — stop pagination
                        return pd.concat(all_pages, ignore_index=True) if all_pages else pd.DataFrame()

                    page_df = pd.DataFrame(records)
                    page_df.columns = [c.lower().replace(" ", "_") for c in page_df.columns]
                    all_pages.append(page_df)
                    success = True
                    time.sleep(1.5)   # polite rate-limit
                    break

                except Exception as e:
                    wait = 5 * (2 ** attempt)
                    print(f"    [Retry {attempt+1}/{max_retries}] {e} -- wait {wait}s")
                    time.sleep(wait)

            if not success:
                print(f"    Failed after {max_retries} retries for {market}")
                break

        return pd.concat(all_pages, ignore_index=True) if all_pages else pd.DataFrame()

    def get_prices_by_date(self, date_str):
        """Fetch prices for a specific date. Format: YYYY-MM-DD"""
        return self.fetch_data(filters={"arrival_date": date_str})


if __name__ == "__main__":
    try:
        client = AgmarknetClient()
        df = client.fetch_market_history(
            market    = "Chokkikulam(Uzhavar Sandhai ) APMC",
            state     = "Tamil Nadu",
            commodity = "Onion",
        )
        print(f"Fetched {len(df)} real rows")
        print(df.head())
    except ValueError as e:
        print(e)
