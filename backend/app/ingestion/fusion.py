import pandas as pd
import os
import time
import numpy as np
from datetime import datetime, timedelta
from .agmarknet import AgmarknetClient
from .weather import WeatherClient
from .satellite import SatelliteDataMock
from .sentiment import SentimentAnalyzer

class DataFusionPipeline:
    def __init__(self):
        self.agmarknet = AgmarknetClient()
        self.weather = WeatherClient()
        self.satellite = SatelliteDataMock()
        # Sentiment analyzer is heavy, load only if needed
        try:
             self.sentiment = SentimentAnalyzer()
        except ImportError:
             print("Warning: transformers not installed. Sentiment analysis disabled.")
             self.sentiment = None

    def create_training_dataset(self, mandis, commodity, start_date, end_date, max_records=10000):
        """
        Merges data from all sources for a list of mandis.
        
        Args:
           mandis (list): List of dicts [{'name': 'Nashik', 'lat': 19.99, 'lon': 73.78, 'state': 'MH'}, ...]
           commodity (str): 'Onion', 'Tomato' etc.
           max_records (int): Maximum records to fetch (default 10000).
           
        Returns:
            pd.DataFrame: Merged dataset.
        """
        all_data = []
        
        for mandi in mandis:
            print(f"Processing {mandi['name']}...")
            
            # 1. Fetch Prices
            # Check for local cache first to avoid API instability
            cache_dir = os.path.join(os.path.dirname(__file__), f'../../data/{commodity.lower()}')
            os.makedirs(cache_dir, exist_ok=True)
            cache_file = os.path.join(cache_dir, f"{commodity}_{mandi['state']}_{max_records}.csv")
            
            prices = pd.DataFrame()
            
            if os.path.exists(cache_file):
                print(f"Loading data from local cache: {cache_file}")
                prices = pd.read_csv(cache_file)
                if 'date' in prices.columns:
                    prices['date'] = pd.to_datetime(prices['date'])
            else:
                print("No local cache found. Fetching from API...")
                # Fetch prices with pagination
                # Calculate pages based on max_records
                all_prices = []
                page_size = 500 # Reduced page size for reliability
                import math
                import time
                num_pages = math.ceil(max_records / page_size)
                
                for page in range(num_pages):
                    print(f"Fetching page {page+1}/{num_pages}...")
                    success = False
                    for attempt in range(5): # Increased retries for better reliability
                        try:
                            current_limit = min(page_size, max_records - (page * page_size))
                            if current_limit <= 0: break
                            
                            df_page = self.agmarknet.fetch_data(filters={
                                'state': mandi['state'], 
                                'commodity': commodity,
                            }, limit=current_limit, offset=page*page_size)
                            
                            if df_page.empty:
                                break
                            
                            all_prices.append(df_page)
                            success = True
                            time.sleep(2) # Increased delay
                            break 
                        except Exception as e:
                            print(f"Error fetching page {page} (Attempt {attempt+1}/5): {e}")
                            time.sleep(5 * (attempt + 1)) # More aggressive backoff
                    
                    if not success:
                        print(f"Failed to fetch page {page}. Saving partial data...")
                        break
                
                prices = pd.concat(all_prices, ignore_index=True) if all_prices else pd.DataFrame()
                
                # Save to cache ONLY if we got enough data (prevent overwriting good cache with bad data)
                if not prices.empty and len(prices) >= 100:
                    print(f"Saving fetched data to cache: {cache_file} ({len(prices)} rows)")
                    prices.to_csv(cache_file, index=False)
                elif not prices.empty:
                    print(f"Warning: Only {len(prices)} rows fetched. NOT caching (min 100 required).")
            
            # --- FALLBACK MECHANISM FOR TRAINING ---
            if prices.empty:
                print(f"Critical: No data fetched for {mandi['name']}. Generating SYNTHETIC training data.")
                # Generate mock price history
                dates = pd.date_range(start=start_date, end=end_date)
                base_price = 2000
                noise = np.random.normal(0, 100, len(dates))
                trend = np.linspace(0, 500, len(dates)) # Mild inflation
                seasonality = 300 * np.sin(2 * np.pi * dates.dayofyear / 365)
                
                mock_prices = base_price + trend + seasonality + noise
                mock_prices = np.clip(mock_prices, 500, 10000)
                
                prices = pd.DataFrame({
                    'date': dates,
                    'modal_price': mock_prices,
                    'min_price': mock_prices - 200,
                    'max_price': mock_prices + 200,
                    'market': mandi['name'],
                    'commodity': commodity,
                    'state': mandi['state']
                })
                print(f"Generated {len(prices)} synthetic records.")

            # Normalize date column early
            if not prices.empty:
                 # Standardize column names
                 prices.columns = [c.replace(' ', '_') for c in prices.columns]
                 
                 if 'arrival_date' in prices.columns:
                    prices['date'] = pd.to_datetime(prices['arrival_date'], dayfirst=True, errors='coerce')
                    prices = prices.dropna(subset=['date'])

            if not prices.empty and 'market' in prices.columns:
                req_market = mandi['name']
                market_data = prices[prices['market'] == req_market]
                
                if len(market_data) > 100:
                    prices = market_data
                    print(f"Using {len(prices)} records from {req_market}")
                else:
                    if len(prices) > 100: # Don't aggregate if we generated synthetic data for specific market
                         print(f"Warning: Only {len(market_data)} records for {req_market}. aggregating STATE AVERAGE for better training data.")
                         # Group by date and take mean of prices
                         # Ensure date column exists (it should now)
                         if 'date' in prices.columns:
                            agg_cols = ['min_price', 'max_price', 'modal_price']
                            # Include weather cols if they exist (e.g. from synthetic data)
                            possible_weather_cols = ['max_temp', 'min_temp', 'precipitation', 'ndvi', 'soil_moisture']
                            existing_weather_cols = [c for c in possible_weather_cols if c in prices.columns]
                            agg_cols.extend(existing_weather_cols)
                            
                            prices = prices.groupby('date')[agg_cols].mean().reset_index()
                            prices['market'] = f"{mandi['state']} Average"
                            print(f"Aggregated State Data: {len(prices)} rows")
                            print(f"Date Range: {prices['date'].min().date()} to {prices['date'].max().date()}")
                         else:
                            print("Error: Date column missing for aggregation.")
            
            # 2. Fetch Weather (Only if not already in data)
            weather_cols = ['max_temp', 'min_temp', 'precipitation', 'soil_moisture']
            has_weather = all(col in prices.columns for col in weather_cols)
            
            if not has_weather:
                weather = self.weather.fetch_historical_weather(
                    mandi['lat'], mandi['lon'], start_date, end_date
                )
            else:
                print("Using weather data from cache/source.")
                weather = pd.DataFrame() # Empty to skip merge
            
            # 3. Fetch Satellite (Only if not already in data)
            if 'ndvi' not in prices.columns:
                satellite = self.satellite.fetch_ndvi_timeseries(
                    mandi['lat'], mandi['lon'], start_date, end_date
                )
            else:
                print("Using satellite data from cache/source.")
                satellite = pd.DataFrame()

            # 4. Fetch REAL News & Analyze Sentiment
            sentiment_df = pd.DataFrame()
            if self.sentiment and not prices.empty:
                print("Fetching real news & analyzing sentiment with FinBERT...")
                
                # Fetch real headlines for the commodity
                real_headlines = self.sentiment.fetch_real_news(commodity=commodity)
                
                if real_headlines:
                    # Analyze sentiment of real headlines
                    sentiments = self.sentiment.analyze_headlines(real_headlines)
                    
                    if not sentiments.empty:
                        # Map real sentiment to each date in the price data
                        # Strategy: Use the average real news sentiment as the base,
                        # then modulate based on daily price movement direction
                        avg_sentiment = sentiments['compound_score'].mean()
                        print(f"  Real news avg sentiment: {avg_sentiment:.3f}")
                        
                        # Calculate daily price change for modulation
                        prices['change'] = prices['modal_price'].pct_change().fillna(0)
                        
                        # Create sentiment signal: base real sentiment + price-correlated adjustment
                        sentiment_values = []
                        for change in prices['change']:
                            # Modulate around real average: price up -> slightly more positive, etc.
                            adjustment = np.clip(change * 2, -0.3, 0.3)  # Scale price change
                            day_sentiment = np.clip(avg_sentiment + adjustment, -1.0, 1.0)
                            sentiment_values.append(day_sentiment)
                        
                        sentiment_df = prices[['date']].copy()
                        sentiment_df['sentiment'] = sentiment_values
                        print(f"  Mapped sentiment to {len(sentiment_df)} dates")
                else:
                    print("  No headlines available. Skipping sentiment feature.")
            else:
                print("Skipping sentiment analysis (model not loaded or no data).")
            
            # Merge logic (mock, assuming dates align or need resampling)
            # merging on 'date'
            if not prices.empty:
                # Date already converted upstream
                # prices['date'] = pd.to_datetime(prices['arrival_date'], dayfirst=True, errors='coerce')
                # prices = prices.dropna(subset=['date']) # Drop rows with invalid dates
                
                # Ensure weather date is also datetime
                if not weather.empty and 'date' in weather.columns:
                    weather['date'] = pd.to_datetime(weather['date'])

                # Merge
                merged = prices
                
                if not weather.empty and 'date' in weather.columns:
                    merged = pd.merge(merged, weather, on='date', how='left')
                
                if not satellite.empty and 'date' in satellite.columns and 'ndvi' in satellite.columns:
                    merged = pd.merge(merged, satellite[['date', 'ndvi']], on='date', how='left')
                
                if not sentiment_df.empty and 'date' in sentiment_df.columns:
                     merged = pd.merge(merged, sentiment_df, on='date', how='left')
                     merged['sentiment'] = merged['sentiment'].fillna(0) # Default neutral
                
                # Add static metadata
                merged['mandi_name'] = mandi['name']
                merged['lat'] = mandi['lat']
                merged['lon'] = mandi['lon']
                
                all_data.append(merged)
        
        return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

if __name__ == "__main__":
    pipeline = DataFusionPipeline()
    mandis = [{'name': 'Nashik', 'lat': 19.99, 'lon': 73.78, 'state': 'Maharashtra'}]
    df = pipeline.create_training_dataset(mandis, "Onion", "2023-01-01", "2023-01-10")
    print(df.head())
