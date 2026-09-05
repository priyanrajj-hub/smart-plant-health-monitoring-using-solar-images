import os
from dotenv import load_dotenv
import datetime
from sentinelhub import SHConfig, SentinelHubStatistical, BBox, CRS, DataCollection

load_dotenv()

# Phase 1: Hardcoded Punjab Bounding Box
# Punjab, India — 30.5,74.5 to 31.5,75.5 
# Format for sentinelhub BBox is (min_x, min_y, max_x, max_y) -> (min_lon, min_lat, max_lon, max_lat)
PUNJAB_BBOX = BBox(bbox=[74.5, 30.5, 75.5, 31.5], crs=CRS.WGS84)

def get_punjab_ndvi():
    CLIENT_ID = os.getenv('SENTINEL_HUB_CLIENT_ID')
    CLIENT_SECRET = os.getenv('SENTINEL_HUB_CLIENT_SECRET')

    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError("Missing Sentinel Hub OAuth credentials in .env")

    config = SHConfig()
    config.sh_client_id = CLIENT_ID
    config.sh_client_secret = CLIENT_SECRET

    # A simple Statistical API request for NDVI mean over the last 30 days
    # (Since this is phase 1, we start with the simplest statistical confirmation)
    time_interval = (
        (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d'),
        datetime.datetime.now().strftime('%Y-%m-%d')
    )

    evalscript = """
    //VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["B04", "B08", "dataMask"]
            }],
            output: [
                { id: "default", bands: 1 },
                { id: "dataMask", bands: 1 }
            ]
        };
    }
    function evaluatePixel(samples) {
        let val = (samples.B08 - samples.B04) / (samples.B08 + samples.B04);
        return {
            default: [val],
            dataMask: [samples.dataMask]
        };
    }
    """

    request = SentinelHubStatistical(
        aggregation=SentinelHubStatistical.aggregation(
            evalscript=evalscript,
            time_interval=time_interval,
            aggregation_interval='P30D',
            resolution=(100, 100) # Reduce resolution to save processing units on large area
        ),
        input_data=[SentinelHubStatistical.input_data(
            DataCollection.SENTINEL2_L2A
        )],
        bbox=PUNJAB_BBOX,
        config=config
    )

    # Perform the API call
    response = request.get_data()
    return response

if __name__ == "__main__":
    # For independent testing run
    print(get_punjab_ndvi())
