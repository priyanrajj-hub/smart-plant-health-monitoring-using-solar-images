import os
import requests
import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json

def get_session():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

class SoilGridsConnector:
    BASE_URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"
    
    @staticmethod
    def get_soil_properties(lat, lon):
        params = {
            "lon": lon,
            "lat": lat,
            "property": ["phh2o", "soc", "nitrogen", "sand", "silt", "clay", "cec", "bdod"],
            "depth": ["0-5cm", "5-15cm"],
            "value": ["mean"]
        }
        try:
            resp = get_session().get(SoilGridsConnector.BASE_URL, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                # simplified parse
                return {"source": "SoilGrids ISRIC", "raw_data": data, "provenance": "measured_sensor_prior"}
            return {"error": resp.status_code, "provenance": "simulated"}
        except:
            return {"error": "fetch_failed", "provenance": "simulated"}

class OpenMeteoConnector:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
    
    @staticmethod
    def get_weather(lat, lon, start_date=None, end_date=None):
        if not start_date:
            start_date = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
            end_date = datetime.datetime.utcnow().strftime("%Y-%m-%d")
            
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "et0_fao_evapotranspiration"],
            "timezone": "UTC"
        }
        try:
            resp = get_session().get(OpenMeteoConnector.ARCHIVE_URL, params=params, timeout=10)
            if resp.status_code == 200:
                return {"source": "OpenMeteo Archive", "data": resp.json(), "provenance": "measured_openmeteo"}
            return {"error": resp.status_code, "provenance": "simulated"}
        except:
            return {"error": "fetch_failed", "provenance": "simulated"}

class Sentinel2Connector:
    # Requires Copernicus Data Space / Sentinel Hub Credentials
    CLIENT_ID = os.getenv("SENTINEL_HUB_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SENTINEL_HUB_CLIENT_SECRET")
    
    @staticmethod
    def get_l2a_observations(polygon_geojson, date_from, date_to):
        if not Sentinel2Connector.CLIENT_ID:
            print("Sentinel-2 API Key Missing. Abstaining from Sentinel fetch.")
            return {"error": "CREDENTIALS_MISSING", "provenance": "insufficient_evidence"}
            
        # Placeholder for real OData / Sentinel Hub fetch logic
        return {"source": "Copernicus Sentinel-2", "data": [], "provenance": "measured_sentinel"}

if __name__ == "__main__":
    print(SoilGridsConnector.get_soil_properties(10.0, 78.0))
    print(OpenMeteoConnector.get_weather(10.0, 78.0))
    print(Sentinel2Connector.get_l2a_observations("{}", "2023-01-01", "2023-01-31"))
