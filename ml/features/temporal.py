import pandas as pd
import numpy as np

def compute_rolling_baselines(obs_df):
    """
    Computes per-place seasonal baselines (rolling median NDVI).
    Expects DataFrame with: place_id, scene_date, ndvi
    """
    if obs_df.empty:
        return obs_df
        
    obs_df['scene_date'] = pd.to_datetime(obs_df['scene_date'])
    obs_df['doy'] = obs_df['scene_date'].dt.dayofyear
    
    # Calculate seasonal anomaly vs place's own baseline over the last 10 visits
    obs_df = obs_df.sort_values(by=['place_id', 'scene_date'])
    obs_df['ndvi_rolling_median'] = obs_df.groupby('place_id')['ndvi'].transform(
        lambda x: x.rolling(window=10, min_periods=1).median()
    )
    obs_df['ndvi_anomaly'] = obs_df['ndvi'] - obs_df['ndvi_rolling_median']
    
    return obs_df

def compute_weather_features(weather_df):
    """
    Computes cumulative stress days, max drop, etc.
    Expects DataFrame with: place_id, date, tmax, rain_mm
    """
    if weather_df.empty:
        return weather_df
        
    weather_df['date'] = pd.to_datetime(weather_df['date'])
    weather_df = weather_df.sort_values(by=['place_id', 'date'])
    
    weather_df['days_since_rain'] = weather_df.groupby('place_id')['rain_mm'].apply(
        lambda x: (x == 0).astype(int).groupby((x > 0).cumsum()).cumsum()
    ).reset_index(level=0, drop=True)
    
    weather_df['heat_stress_daily'] = (weather_df['tmax'] > 35).astype(int)
    weather_df['cum_heat_stress_7d'] = weather_df.groupby('place_id')['heat_stress_daily'].transform(
        lambda x: x.rolling(window=7, min_periods=1).sum()
    )
    
    return weather_df

if __name__ == "__main__":
    # Test stub
    print("Feature pipeline ready.")
