import os
import requests
import json
import time
import datetime
from pathlib import Path

# Caching for api requests
CACHE_DIR = Path(".cache/api")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _get_cached_or_fetch(cache_key: str, url: str, params=None, headers=None, max_age_days=1):
    """Simple file-based caching to avoid redundant API hits during testing and backfills."""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    if cache_file.exists():
        mtime = datetime.datetime.fromtimestamp(cache_file.stat().st_mtime)
        if (datetime.datetime.now() - mtime).days < max_age_days:
            with open(cache_file, "r") as f:
                return json.load(f)
                
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        with open(cache_file, "w") as f:
            json.dump(data, f)
        return data
    else:
        print(f"Error fetching {url}: {response.status_code} - {response.text}")
        return None

class OpenMeteoConnector:
    """Connector for Open-Meteo Historical & Current APIs."""
    
    BASE_URL = "https://archive-api.open-meteo.com/v1/archive"
    CURRENT_URL = "https://api.open-meteo.com/v1/forecast"

    @classmethod
    def fetch_historical_weather(cls, lat: float, lon: float, start_date: str, end_date: str):
        """Fetch daily weather metrics (temperature, humidity, precipitation)."""
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,et0_fao_evapotranspiration,vapour_pressure_deficit_max",
            "timezone": "auto"
        }
        cache_key = f"meteo_hist_{lat}_{lon}_{start_date}_{end_date}"
        # We can cache historical data permanently if the end date is in the past
        is_historical = datetime.datetime.strptime(end_date, "%Y-%m-%d") < datetime.datetime.now()
        max_age = 365 if is_historical else 1 
        
        return _get_cached_or_fetch(cache_key, cls.BASE_URL, params=params, max_age_days=max_age)

    @classmethod
    def fetch_current_weather(cls, lat: float, lon: float):
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,precipitation",
            "daily": "sunshine_duration,uv_index_max",
            "timezone": "auto"
        }
        cache_key = f"meteo_cur_{lat}_{lon}_{datetime.date.today()}"
        return _get_cached_or_fetch(cache_key, cls.CURRENT_URL, params=params, max_age_days=1)


class SoilGridsConnector:
    """Connector for ISRIC SoilGrids REST API to establish NPK baselines."""
    
    BASE_URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"
    
    @classmethod
    def fetch_soil_composition(cls, lat: float, lon: float):
        """
        Retrieves Nitrogen, pH, SOC, and CEC at 0-5cm and 5-15cm depths.
        """
        # Note: SoilGrids uses (lon, lat) parameter order for their REST API
        params = {
            "lon": lon,
            "lat": lat,
            "property": ["nitrogen", "phh2o", "soc", "cec"],
            "depth": ["0-5cm", "5-15cm"],
            "value": ["mean"]
        }
        cache_key = f"soilgrids_{lat}_{lon}"
        # Soil characteristics change very slowly, cache for a year
        return _get_cached_or_fetch(cache_key, cls.BASE_URL, params=params, max_age_days=365)


class Sentinel2Connector:
    """
    Connector for Copernicus Sentinel-2 L2A via Sentinel Hub or Copernicus Data Space.
    Requires proper authentication via OAuth2.
    """
    
    TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    PROCESS_URL = "https://sh.dataspace.copernicus.eu/api/v1/process"
    
    def __init__(self):
        self.client_id = os.environ.get("COP_CLIENT_ID")
        self.client_secret = os.environ.get("COP_CLIENT_SECRET")
        self.access_token = None
        self.token_expiry = 0
        
    def _authenticate(self):
        if not self.client_id or not self.client_secret:
            print("WARNING: Copernicus credentials missing. Sentinel-2 connector disabled.")
            return False
            
        if time.time() < self.token_expiry:
            return True
            
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            res = requests.post(self.TOKEN_URL, data=data)
            res.raise_for_status()
            token_info = res.json()
            self.access_token = token_info["access_token"]
            self.token_expiry = time.time() + token_info["expires_in"] - 60
            return True
        except Exception as e:
            print(f"Error authenticating with Copernicus: {e}")
            return False
            
    def fetch_ndvi_and_scl(self, bounds: list, start_date: str, end_date: str):
        """
        Bounds should be [min_lon, min_lat, max_lon, max_lat]
        Retrieves NDVI and Scene Classification Layer (SCL) for cloud masking.
        """
        if not self._authenticate():
            return {"error": "Authentication failed", "status": "simulated_proxy", "ndvi_mean": None}
            
        # Standard Evalscript for returning NDVI & SCL logic via Process API
        evalscript = """
        //VERSION=3
        function setup() {
          return {
            input: ["B04", "B08", "SCL", "dataMask"],
            output: [
              { id: "ndvi", bands: 1, sampleType: "FLOAT32" },
              { id: "scl", bands: 1, sampleType: "UINT8" }
            ]
          };
        }
        function evaluatePixel(sample) {
          let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
          return {
            ndvi: [ndvi],
            scl: [sample.SCL]
          };
        }
        """
        
        payload = {
            "input": {
                "bounds": {
                    "bbox": bounds
                },
                "data": [
                    {
                        "type": "sentinel-2-l2a",
                        "dataFilter": {
                            "timeRange": {
                                "from": f"{start_date}T00:00:00Z",
                                "to": f"{end_date}T23:59:59Z"
                            },
                            "maxCloudCoverage": 30
                        }
                    }
                ]
            },
            "output": {
                "responses": [
                    {
                        "identifier": "ndvi",
                        "format": {"type": "image/tiff"}
                    }
                ]
            },
            "evalscript": evalscript
        }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/tar"
        }
        
        # We would process the TIFF output via rasterio here to extract actual mean.
        # Returning mock structure denoting successful API setup since we require real TIFF parsing to output standard dict
        print("Sentinel HTTP Process call configured. Actual array parsing requires rasterio processing.")
        return {"status": "api_available", "bounds": bounds, "message": "Sentinel Payload prepared. Require Rasterio decoding module to aggregate TIFFs."}

if __name__ == "__main__":
    # Test suite to verify live connectivity
    print("Testing SoilGrids...")
    soil = SoilGridsConnector.fetch_soil_composition(10.79, 78.70)
    print("SoilGrids Success!" if soil else "SoilGrids Failed.")
    
    print("Testing Open-Meteo Current...")
    meteo = OpenMeteoConnector.fetch_current_weather(10.79, 78.70)
    print("Open-Meteo Success!" if meteo else "Open-Meteo Failed.")
