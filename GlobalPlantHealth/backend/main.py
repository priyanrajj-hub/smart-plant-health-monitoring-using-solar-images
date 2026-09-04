from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import json

app = FastAPI(title="GlobalPlantHealth Gemini Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = "AQ.Ab8RN6KKhVtBlJH7c-UOPcnb48Ll1k5_AUAmn4cuLOk2THr9ug"

@app.get("/")
def read_root():
    return {"status": "ok", "app": "Canopy Gemini Backend Proxy"}

@app.get("/api/inspect")
def inspect_region(lat: float, lng: float):
    """
    Live proxy fetching directly from Google Gemini API to synthesize environmental data 
    for the exact coordinates dynamically!
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"Analyze global agricultural and biome geographic data for coordinates Lat: {lat}, Lng: {lng}. Evaluate the likely vegetation health there right now. Return ONLY a raw JSON object string with absolutely NO markdown block formatting. It must have exactly these keys: 'ndvi_mean' (a float between 0.0 and 1.0 representing realistic normalized difference vegetation index for this terrain), 'status' ('healthy', 'stressed', or 'critical' based on ndvi), and 'source' (a short 4-word string describing the geography, e.g., 'Gemini Analysis: Arid Desert')."
    
    payload = {
        "contents": [{"parts":[{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2}
    }
    
    try:
        resp = requests.post(url, json=payload)
        
        if not resp.ok:
            raise HTTPException(status_code=500, detail="Gemini API Error: " + resp.text)
            
        res_json = resp.json()
        raw_text = res_json['candidates'][0]['content']['parts'][0]['text']
        
        # Strip potential markdown block if Gemini accidentally wraps it
        raw_text = raw_text.replace('```json', '').replace('```', '').strip()
        data = json.loads(raw_text)
        
        return {
            "lat": lat,
            "lng": lng,
            "ndvi_mean": float(data.get("ndvi_mean", 0.5)),
            "status": data.get("status", "healthy").lower(),
            "source": data.get("source", "Gemini Synthetic Analysis")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed connecting to Gemini Engine: {str(e)}")
