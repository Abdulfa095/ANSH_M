import requests
import os
from dotenv import load_dotenv

load_dotenv()

OSRM_API_URL = os.getenv("OSRM_API_URL", "http://router.project-osrm.org")

class OSRMClient:
    """
    Client for Open Source Routing Machine (OSRM).
    Calculates distance and travel time between coordinates.
    """
    def __init__(self, base_url=None):
        self.base_url = base_url or OSRM_API_URL

    def get_route(self, start_lat, start_lon, end_lat, end_lon):
        """
        Get route details between two points.
        
        Args:
            start_lat, start_lon: Origin coordinates.
            end_lat, end_lon: Destination coordinates.
            
        Returns:
            dict: {distance_km, duration_min}
        """
        # OSRM expects: lon,lat;lon,lat
        coordinates = f"{start_lon},{start_lat};{end_lon},{end_lat}"
        url = f"{self.base_url}/route/v1/driving/{coordinates}"
        
        params = {
            "overview": "false",
            "steps": "false"
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['code'] == 'Ok' and data['routes']:
                route = data['routes'][0]
                # Distance in meters, duration in seconds
                distance_km = route['distance'] / 1000.0
                duration_min = route['duration'] / 60.0
                
                return {
                    "distance_km": round(distance_km, 2),
                    "duration_min": round(duration_min, 2)
                }
            else:
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching OSRM route: {e}")
            return None

if __name__ == "__main__":
    osrm = OSRMClient()
    # Example: Nashik to Mumbai (Vashi)
    route = osrm.get_route(19.9975, 73.7898, 19.0760, 72.8777)
    print(route)
