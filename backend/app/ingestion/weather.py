import requests
import pandas as pd
from datetime import datetime, timedelta

class WeatherClient:
    """
    Client for fetching weather data.
    Uses Open-Meteo API as a free, no-key alternative to ERA5 for this prototype.
    """
    BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

    def fetch_historical_weather(self, lat, lon, start_date, end_date):
        """
        Fetch historical weather data (Max Temp, Precipitation, etc.)
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            start_date (str): YYYY-MM-DD
            end_date (str): YYYY-MM-DD
            
        Returns:
            pd.DataFrame: Weather data.
        """
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "soil_moisture_0_to_7cm_mean"],
            "timezone": "auto"
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            daily_data = data.get("daily", {})
            df = pd.DataFrame(daily_data)
            
            # Rename columns for consistency
            df.rename(columns={
                "time": "date",
                "temperature_2m_max": "max_temp",
                "temperature_2m_min": "min_temp",
                "precipitation_sum": "precipitation",
                "soil_moisture_0_to_7cm_mean": "soil_moisture"
            }, inplace=True)
            
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return pd.DataFrame()

if __name__ == "__main__":
    client = WeatherClient()
    # Example: Nashik
    df = client.fetch_historical_weather(19.9975, 73.7898, "2023-01-01", "2023-01-10")
    print(df)
