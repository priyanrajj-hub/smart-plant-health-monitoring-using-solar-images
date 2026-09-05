import os
import requests
import time
import datetime
from dotenv import load_dotenv

load_dotenv()

SH_TOKEN_URL = "https://services.sentinel-hub.com/oauth/token"
SH_STATISTICAL_URL = "https://services.sentinel-hub.com/api/v1/statistics"

_access_token = None
_token_expires = 0

def get_token():
    global _access_token, _token_expires
    if time.time() < _token_expires:
        return _access_token

    client_id = os.getenv("SENTINEL_CLIENT_ID")
    client_secret = os.getenv("SENTINEL_CLIENT_SECRET")
    
    if not client_id or not client_secret or client_id == "your_client_id_here":
        raise ValueError("Missing or invalid Sentinel Hub OAuth credentials in .env")
        
    data = {"grant_type": "client_credentials"}
    resp = requests.post(SH_TOKEN_URL, data=data, auth=(client_id, client_secret))
    
    if not resp.ok:
        raise ValueError(f"Failed to authenticate with Sentinel Hub: {resp.text}")
        
    token_data = resp.json()
    _access_token = token_data["access_token"]
    _token_expires = time.time() + token_data["expires_in"] - 60
    return _access_token

def fetch_ndvi_for_point(lat, lng):
    # bounding box ~5km around point
    offset = 0.05 
    bbox = [lng - offset, lat - offset, lng + offset, lat + offset]
    
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Evalscript fetches NDVI and returns a mask eliminating cloud cover using the SCL band
    evalscript = """
    //VERSION=3
    function setup() {
        return {
            input: [{ bands: ["B04", "B08", "SCL", "dataMask"] }],
            output: [
                { id: "ndvi", bands: 1, sampleType: "FLOAT32" },
                { id: "dataMask", bands: 1 }
            ]
        };
    }
    function evaluatePixel(samples) {
        let isCloud = [7, 8, 9, 10].includes(samples.SCL);
        let ndvi = (samples.B08 - samples.B04) / (samples.B08 + samples.B04);
        return {
            ndvi: [ndvi],
            dataMask: [samples.dataMask && !isCloud ? 1 : 0]
        };
    }
    """
    now = datetime.datetime.now()
    past = now - datetime.timedelta(days=30)
    
    payload = {
        "input": {
            "bounds": {
                "bbox": bbox,
                "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"}
            },
            "data": [{
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {
                        "from": past.strftime("%Y-%m-%dT00:00:00Z"),
                        "to": now.strftime("%Y-%m-%dT23:59:59Z")
                    }
                }
            }]
        },
        "aggregation": {
            "timeRange": {
                "from": past.strftime("%Y-%m-%dT00:00:00Z"),
                "to": now.strftime("%Y-%m-%dT23:59:59Z")
            },
            "aggregationInterval": {"of": "P30D"},
            "evalscript": evalscript,
            "resx": 100,
            "resy": 100
        }
    }
    
    resp = requests.post(SH_STATISTICAL_URL, headers=headers, json=payload)
    if not resp.ok:
        raise ValueError(f"Sentinel Hub API Error: {resp.text}")
        
    return resp.json()
