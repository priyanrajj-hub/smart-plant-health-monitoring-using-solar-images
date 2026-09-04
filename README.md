# Canopy: Global Vegetation Health Monitor

[![Vercel Deploy](https://img.shields.io/badge/Vercel-Deployed-success)](https://smart-plant-health-monitoring-using-solar-images.vercel.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*Companion Hardware Research Repo:* [Review-2 Repository (Microwave Dielectric Leaf Sensing)](https://github.com/priyanrajj-hub/review2)

Canopy is a browser-based vegetation monitoring dashboard that combines OpenStreetMap land-use classification with real-time weather data to estimate crop health indicators.

## ⚠️ Data Source Transparency

| Feature | Data Source | Status |
|---------|-----------|--------|
| **NDVI Value** | OSM land-use tags via Overpass API | **Proxy** — not satellite multispectral. Maps `farmland`→0.72, `building`→0.12, etc. |
| **Temperature, Humidity, UV** | Open-Meteo Forecast API | **Live** — real data for polygon centroid |
| **14-day Rainfall** | Open-Meteo Forecast API | **Live** — real precipitation history |
| **Rainfall Baseline** | Open-Meteo Archive API (same window last year) | **Live** — real location-specific norm |
| **Pest Risk / Irrigation**| Rule engine on live weather + proxy NDVI | **Heuristic** — thresholds not validated against pest incidence data |
| **Temporal Δ Change** | Deterministic coord-hash offset | **Simulated** — requires Sentinel Hub API for real time series |
| **AI Narrative** | Gemini 1.5 Flash (via `/api/gemini`) | **Live** when configured. |
| **7-day NDVI Trend** | Simulated walk from current proxy NDVI | **Simulated** — no historical NDVI data source |

### What Would Make NDVI Real?
To get actual satellite-derived NDVI, you need credentials for one of:
- **Sentinel Hub** (ESA Copernicus) — free tier available, requires OAuth2 flow
- **NASA MODIS/VIIRS** (AppEEARS API) — free, but data is coarse
- **Google Earth Engine** — free for research, requires approved account

## 🏗 Architecture

```
User draws polygon on Leaflet map
        ↓
┌───────────────────────────────────┐
│  3 parallel API calls (browser)  │
├──────────┬──────────┬─────────────┤
│ Overpass │Open-Meteo│ Rain Archive│
│ (OSM tags)│(weather) │ (baseline)  │
└────┬─────┴────┬─────┴──────┬──────┘
     ↓          ↓            ↓
  NDVI proxy  Live temp   Deficit %
     ↓          humidity     ↓
  Rule engine merges all signals
     ↓
  Gemini API (if key) or rule fallback
     ↓
  UI renders with source labels
```

## 🛠️ Running Locally

```bash
# Install dependencies
npm install

# Start local server
node server.js

# Note: The frontend explicitly relies on standard web technologies
# (Leaflet, Chart.js) and does not require complex build steps.
```

## 🧪 Smoke Testing

Run the included smoke test to verify API routes and external fetch stability:
```bash
node test_smoke.js
```
