import os
import sys

from app.ingestion.agmarknet import AgmarknetClient

def test_agmarknet_variety():
    client = AgmarknetClient()
    
    # Test with Variety
    print("Fetching Onion data with variety 'Red'...")
    df_red = client.fetch_data(filters={'state': 'Maharashtra', 'commodity': 'Onion', 'variety': 'Red'}, limit=10)
    if not df_red.empty:
        print(df_red[['market', 'variety', 'modal_price']].head())
    else:
        print("No data found for Red Onion in Maharashtra.")

    # Test without Variety
    print("\nFetching Onion data without variety...")
    df_any = client.fetch_data(filters={'state': 'Maharashtra', 'commodity': 'Onion'}, limit=10)
    if not df_any.empty:
        print(df_any[['market', 'variety', 'modal_price']].head())
    else:
        print("No data found for Onion in Maharashtra.")

if __name__ == "__main__":
    test_agmarknet_variety()
