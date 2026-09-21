# Codebase Audit: Simulated and Fallback Data Flows

This document lists every occurrence where simulated, mocked, or fallback data is generated and fed into the Canopy UI. The goal of the ML Pipeline project is to systematically replace these with real, verified, and calibrated machine learning models using ground truth data.

## 1. `index.html` Frontend Mocks

The primary dashboard relies on multiple heuristics and randomizations to simulate a fully populated AI panel.

### Sensor Reading Simulations (Moonlight Fusion Fallbacks)

- `currentTemp = 25` and `deficit = 0`: Used as hardcoded fallbacks if the Open-Meteo API fetch fails.
- `ndvi = 0.45`: A hardcoded fallback NDVI used before any rules apply.
- **NDVI Proxy from OSM Tags**: Land-use tags (e.g., "water", "farmland", "building") act as proxies to manually override the `ndvi` score (lines 1159-1166). This is an OSINT heuristic, not true satellite reflectance.
- **PseudoVariance**: A deterministic hash based on map coordinates `(Math.abs(centerLng + centerLat) % 0.1) - 0.05` is added to the NDVI to simulate natural variation between polygons without needing high-res raster data.
- **Hardware Sensor Proxies**:
  - `C_t = 0.4`: Simulated capacitive proxy for soil moisture.
  - `A_t = 0.2`: Simulated acoustic proxy.
  - `N_t`: Constructed from the mocked NDVI.
  - `R_t`: Constructed from the generalized rainfall deficit.
- **Cloud Cover Contamination Proxy**: `cloudFrac = Math.random() * 0.3` is used to simulate Sentinel SCL cloud masking, lowering the weight (`w_N`) of the optical index randomly.

### AI Insight Presentation (Gemini Fallbacks)

- If the Gemini API times out or fails (or if CORS blocks the request), the UI catches the error and injects a heavily hardcoded string containing static text like `"summary": "Environmental telemetry strongly correlates with stable vegetation health..."` and `"Confidence_caveat": "Insight derived via system fallback simulation"`.
- The frontend renders `"AI Estimate - Failed to parse structured JSON"` if the response drops into the catch block.
- The `confidence` score presented in the UI (`(confidence * 100).toFixed(1)%`) is derived purely from the sum of the arbitrary weights (`w_C`, `w_A`, `w_N`, `w_R`) and variance calculations of these simulated proxies, not from a calibrated machine learning probability.

### Time-Series Charts (NDVI Trajectory)

- The bottom right line chart displays an "NDVI Trajectory (simulated — no historical API)". It plots past days by injecting random jitter: `baseNdvi + (Math.random() * 0.1 - 0.05)`.

## 2. API Backend & Edge Functions

### `api/gemini/index.js`

- **Offline / Model Degradation Proxies**: If the API keys for the LLM are missing or invalid (`Google API Key Offline`), the serverless function immediately returns a structured JSON payload filled with static simulation strings: `disease_indicator: "No visible signs..."`, `stress_severity: "Stable to Low Stress"`.
- These fallback payloads literally contain the flag `"confidence_caveat": "Insight derived via system fallback simulation (Google API Key Offline) using open-source telemetry models."`

## Summary & Action Plan

Every piece of data concerning crop health (NDVI, Stress, Confidence, History) is presently supplemented by simulation or proxy values to ensure a continuous demo experience.

**Next Steps**: We will replace this entire synthetic stack. We will persist every polygon scan to Firestore (and CSV), compute genuine historical baselines, fetch true Sentinel L2A reflectances, and train explicit Image/Tabular models for Species, Disease, and NPK targets to substitute this proxy logic.
