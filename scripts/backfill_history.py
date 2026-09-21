import os
import csv
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from ml.data.connectors import OpenMeteoConnector, SoilGridsConnector

def backfill_places():
    """Reads places.csv and pulls up to 12 months history for weather, and constant soil."""
    places_file = 'data/places.csv'
    if not os.path.exists(places_file):
        print(f"File {places_file} not found. Cannot backfill.")
        return

    end_date = datetime.now()
    start_date = end_date - relativedelta(months=12)
    end_date_str = end_date.strftime("%Y-%m-%d")
    start_date_str = start_date.strftime("%Y-%m-%d")

    print(f"Backfilling from {start_date_str} to {end_date_str}")
    
    with open(places_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        places = list(reader)

    if not places:
        print("No places found.")
        return

    for place in places:
        pid = place.get('place_id')
        lat = float(place.get('latitude', 0))
        lng = float(place.get('longitude', 0))
        
        if lat == 0 and lng == 0:
            print(f"Skipping {pid} - invalid coords")
            continue

        print(f"Backfilling {pid} at {lat}, {lng}...")
        
        # 1. Fetch Soil Data (Baseline)
        soil = SoilGridsConnector.fetch_soil_composition(lat, lng)
        if soil:
            print(f"  [OK] SoilGrids metadata retrieved")
        else:
            print(f"  [FAIL] SoilGrids metadata failed")
            
        # 2. Fetch Historical Weather 
        hist_weather = OpenMeteoConnector.fetch_historical_weather(lat, lng, start_date_str, end_date_str)
        if hist_weather:
            print(f"  [OK] Open-Meteo historical (365 days) retrieved and cached")
        else:
            print(f"  [FAIL] Open-Meteo historical failed")
            
        # Rate limit respect
        time.sleep(1)

    print("Backfill process complete! Aggregated time-series are stored in .cache/api ready for feature extraction.")

if __name__ == "__main__":
    backfill_places()
