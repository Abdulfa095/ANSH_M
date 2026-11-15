import pandas as pd
from app.ingestion.agmarknet import AgmarknetClient
from datetime import datetime

def test_agmarknet_date():
    client = AgmarknetClient()
    
    # 1. Test exactly the date the user mentioned
    filters = {
        'state': 'Tamil Nadu',
        'commodity': 'Rice',
        'arrival_date': '08/03/2026' 
    }
    
    print(f"Fetching with filters: {filters}")
    df = client.fetch_data(filters=filters, limit=50)
    
    if df is not None and not df.empty:
        print(f"Success! Found {len(df)} records for Rice on 08/03/2026.")
        print(df[['market', 'commodity', 'variety', 'arrival_date', 'modal_price']].head())
    else:
        print("Empty dataframe returned for Rice on 08/03/2026.")
        
    # 2. Test fetching all recent Rice in TN to see what dates are ACTUALLY available
    filters_no_date = {
        'state': 'Tamil Nadu',
        'commodity': 'Rice'
    }
    print(f"\nFetching with filters WITHOUT date: {filters_no_date}")
    df2 = client.fetch_data(filters=filters_no_date, limit=20)
    
    if df2 is not None and not df2.empty:
        print(f"Success! Found {len(df2)} records.")
        print("Current available dates in the API for Rice in TN:")
        print(df2['arrival_date'].value_counts())
        print(df2[['market', 'commodity', 'variety', 'arrival_date', 'modal_price']].head())
    else:
        print("Empty dataframe returned without date either.")

if __name__ == "__main__":
    test_agmarknet_date()
