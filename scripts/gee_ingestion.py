import ee
import geemap
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# 1. Authenticaton and Initialization
# Make sure to run `earthengine authenticate` on your machine once before running this.
try:
    print("Initializing Google Earth Engine directly via local OAuth...")
    ee.Initialize()
except Exception as e:
    print("Earth Engine initialization failed. Launching interactive OAuth browser flow...")
    ee.Authenticate()
    ee.Initialize()

# 2. Config & Inputs
# Target coordinate matching the Arduino physical location (Modify as needed)
LAT = 30.7333
LON = 76.7794 
START_DATE = '2023-01-01'
END_DATE = '2024-01-01'

# We map a tight 10x10 meter polygon exactly where the sensor is.
point = ee.Geometry.Point([LON, LAT])
region = point.buffer(10).bounds()

def get_gee_data():
    print(f"Fetching Sentinel-2 & MODIS collections over Arduino Site ({LAT}, {LON})...")
    
    # Sentinel-2 Surface Reflectance (Multi-spectral proxy)
    s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterBounds(region) \
        .filterDate(START_DATE, END_DATE) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) # Strict cloud mask

    # MODIS LST (Land Surface Temperature)
    modis = ee.ImageCollection('MODIS/006/MOD11A1') \
        .filterBounds(region) \
        .filterDate(START_DATE, END_DATE)

    def extract_s2(img):
        date = img.date().format('YYYY-MM-dd')
        # Compute NDVI
        ndvi = img.normalizedDifference(['B8', 'B4']).rename('NDVI')
        mean_ndvi = ndvi.reduceRegion(reducer=ee.Reducer.mean(), geometry=region, scale=10).get('NDVI')
        return ee.Feature(None, {'date': date, 'NDVI': mean_ndvi})
    
    def extract_lst(img):
        date = img.date().format('YYYY-MM-dd')
        # MODIS LST is scaled by 0.02 and converted to Celsius
        lst = img.select('LST_Day_1km').multiply(0.02).subtract(273.15).rename('LST')
        mean_lst = lst.reduceRegion(reducer=ee.Reducer.mean(), geometry=region, scale=1000).get('LST')
        return ee.Feature(None, {'date': date, 'LST': mean_lst})

    print("Extracting time-series arrays. This may take a minute based on GEE quotas...")
    # Map extractors
    s2_features = s2.map(extract_s2).getInfo()['features']
    modis_features = modis.map(extract_lst).getInfo()['features']

    # Build Dataframes
    df_s2 = pd.DataFrame([f['properties'] for f in s2_features])
    df_lst = pd.DataFrame([f['properties'] for f in modis_features])
    
    # Merge and interpolate
    # Because Sentinel is 5-day and MODIS is daily, we do a nearest-neighbor interpolation max 5 days.
    df_s2['date'] = pd.to_datetime(df_s2['date'])
    df_lst['date'] = pd.to_datetime(df_lst['date'])

    df_merged = pd.merge_asof(
        df_s2.sort_values('date'), 
        df_lst.sort_values('date'), 
        on='date', 
        direction='nearest',
        tolerance=pd.Timedelta('5d')
    )
    
    df_merged = df_merged.dropna()
    print(f"Extracted {len(df_merged)} cloud-free coincident satellite observations.")
    return df_merged

def integrate_arduino_ground_truth(df_gee):
    """
    Simulates linking the real Arduino IoT export (`sensor_logs.csv`) to establish ground truth.
    Since we don't have the user's actual CSV here, we construct the join logic expecting it.
    """
    csv_path = 'sensor_logs.csv'
    if os.path.exists(csv_path):
        df_ard = pd.read_csv(csv_path)
        df_ard['date'] = pd.to_datetime(df_ard['date']).dt.normalize() # align to daily
        # Calculate daily mean if arduino logs hourly
        df_ard_daily = df_ard.groupby('date').mean().reset_index()
        
        # Merge exactly on date
        final_df = pd.merge(df_gee, df_ard_daily, on='date', how='inner')
        print(f"Final Merged Telemetry pairs: {len(final_df)} valid dates.")
        
        # Create Target (Stressed vs Optimal)
        # Using soil moisture strictly as the target, completely excluding it from ML features.
        # Threshold: if moisture < 30%, it is stressed (1), else healthy (0)
        if 'soil_moisture' in final_df.columns:
            final_df['Target_Stressed'] = np.where(final_df['soil_moisture'] < 30, 1, 0)
            # Drip leakage: remove soil_moisture from feature pool!
            final_df = final_df.drop(columns=['soil_moisture'])
        
        # Save output
        os.makedirs('dataset', exist_ok=True)
        final_df.to_csv('dataset/gee_telemetry.csv', index=False)
        print("Successfully exported synchronized pipeline target: `dataset/gee_telemetry.csv`")
        
    else:
        print("\n[CRITICAL ERROR] STRICT GROUND-TRUTH MODE ENABLED.")
        print("`sensor_logs.csv` from the Arduino hardware project was not found in the root directory.")
        print("To strictly conform to SIH deployment standards and prevent cyclic leakage, this pipeline REFUSES to train on fabricated or synthetic environmental proxies.")
        raise FileNotFoundError("Missing hardware ground truth. Please supply `sensor_logs.csv` to proceed.")

if __name__ == "__main__":
    gee_data = get_gee_data()
    integrate_arduino_ground_truth(gee_data)
