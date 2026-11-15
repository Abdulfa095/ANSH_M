import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class SatelliteDataMock:
    """
    Mock adapter for Google Earth Engine (GEE) satellite data.
    Generates synthetic NDVI (Normalized Difference Vegetation Index) 
    and VHI (Vegetation Health Index) timeseries.
    """
    
    def __init__(self):
        pass

    def fetch_ndvi_timeseries(self, lat, lon, start_date, end_date):
        """
        Generates daily NDVI data between start and end dates.
        NDVI typically ranges from -1 to 1.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            start_date (str): YYYY-MM-DD
            end_date (str): YYYY-MM-DD
            
        Returns:
            pd.DataFrame: Date and NDVI values.
        """
        dates = pd.date_range(start=start_date, end=end_date)
        # Generate synthetic seasonality (sine wave) + noise
        day_of_year = dates.dayofyear
        
        # Simple crop cycle model: peak greenness in middle of season
        # This is a mock, so we just assume a generic cycle
        ndvi_values = 0.5 + 0.3 * np.sin(2 * np.pi * day_of_year / 365) + np.random.normal(0, 0.05, len(dates))
        ndvi_values = np.clip(ndvi_values, -1, 1)
        
        return pd.DataFrame({
            'date': dates,
            'ndvi': ndvi_values,
            'lat': lat,
            'lon': lon
        })

    def fetch_vhi_timeseries(self, lat, lon, start_date, end_date):
        """
        Generates daily VHI (Vegetation Health Index).
        VHI (0-100), where <40 indicates stress.
        """
        dates = pd.date_range(start=start_date, end=end_date)
        # Correlated with NDVI but with some lag/variation
        vhi_values = 50 + 30 * np.sin(2 * np.pi * dates.dayofyear / 365) + np.random.normal(0, 10, len(dates))
        vhi_values = np.clip(vhi_values, 0, 100)
        
        return pd.DataFrame({
            'date': dates,
            'vhi': vhi_values,
            'lat': lat,
            'lon': lon
        })

if __name__ == "__main__":
    sat = SatelliteDataMock()
    df = sat.fetch_ndvi_timeseries(18.5204, 73.8567, "2023-01-01", "2023-01-10")
    print(df)
