# AGRISENSE

> Stressor-Aware Capacitive Sensing: A Diurnally-Corrected, Conformal-Bounded Model Pipeline
>
> SIH26180 Problem Statement: Develop a low-cost, multi-modal sensor fusion approach to detect early-stage plant water and nutrient stress before visible wilting occurs, optimizing precision agriculture interventions.

## Architecture

```text
======================================
         SATELLITE MACRO LAYER
======================================
  [Sentinel-2 L2A] --> (10m Resolution) --> | LBP Texture Anomaly |
  [Open-Meteo] ------> (14-day vs 5-year)-> | Precipitation Deficit|
                                                  |
======================================            v
         GROUND MICRO LAYER                   [FUSION ALGORITHM] --> Fused Risk Score
======================================            ^
  [FDC1004] ---------> (Leaf Capacitance)-> | Diurnal Correction |
  [DS18B20] ---------> (Temp Reference) --> | Feature Engineering |
```

## What's Real vs Simulated

| Component | Status | Verification / Code Path |
| :--- | :--- | :--- |
| **Sentinel-2 L2A Pull** | LIVE | `GlobalPlantHealth/backend/sentinel_service.py:get_punjab_image_patch()` |
| **Open-Meteo Rainfall** | LIVE | `algorithm/weather_service.py:get_precipitation_deficit()` |
| **LBP Texture Calculation** | LIVE | `algorithm/fusion_model.py:texture_anomaly_layer()` (Uses genuine image patch) |
| **Historical NDVI Data** | [PROXY] | `algorithm/fusion_model.py` (Uses derived/synthetic baseline history) |
| **FDC1004 Hardware** | [PROXY] | `data/raw/synthetic_trial_dataset.csv` (Synthetic trials pending live-plant integration) |

## SIH Judging Criteria Mapping

### 1. Innovation and Novelty

- Actively mitigates hardware cost by relying on diurnal-drift correction for capacitive sensors instead of enterprise THz-TDS.
- Bridges macroscopic satellite endpoints (Sentinel-2) with microscopic leaf-level telemetry.

### 2. Technical Complexity

- Algorithm dynamically computes skimage Local Binary Patterns (LBP) dynamically on live Sentinel Hub arrays, rather than hardcoding static images.
- Implements Leave-One-Plant-Out Cross-Validation (LOPO-CV) rather than basic K-Fold to prevent biological data leakage.

### 3. Feasibility and Practicability

- Total hardware BOM is < $15 (FDC1004 + ESP32) eliminating the need for expensive spectroscopy.
- Entire software stack is open-source (Python/SciPy) and avoids recurring API lock-in.

### 4. Sustainability

- Reduces water wastage by pinpointing precise deficit triggers before visible wilting.
- Architecture is low-bandwidth, sending sparse sensor ticks to the backend rather than constant heavy payloads.

### 5. Project Completeness

- Provides an end-to-end data pipeline from API ingest (`sentinel_service.py`) to feature modeling (`fusion_model.py`) to UI mapping.
- All code handles authentication, environment variables, and fails gracefully to Proxy if APIs timeout.

### 6. User Experience

- Includes a live dashboard capable of demarcating `[PROXY]` vs `LIVE` statuses transparently.
- Demo walk-through natively maps theoretical risk scores to understandable farm-level alerts.

## Quickstart

```bash
# 1. Clone repository
git clone https://github.com/priyanrajj-hub/smart-plant-health-monitoring-using-solar-images.git
cd smart-plant-health-monitoring-using-solar-images

# 2. Add API Credentials
# Create GlobalPlantHealth/backend/.env and add:
# SENTINEL_HUB_CLIENT_ID="..."
# SENTINEL_HUB_CLIENT_SECRET="..."

# 3. Test Core Integration
python algorithm/fusion_model.py
```

## Team & Project Links

- **Team ID:** [PASTE FROM 'MY TEAM & PITCH' TAB]
- **Project URL:** <https://github.com/priyanrajj-hub/smart-plant-health-monitoring-using-solar-images>
- **Global Deployment (Companion):** <https://github.com/priyanrajj-hub/smart-plant-health-monitoring-using-solar-images/tree/main>

## Citations

1. Garg et al. (2025). AdapTree. Sensors. DOI: 10.3390/s25103149
2. Janni et al. (2019). Bioristor. Plant Phenomics. DOI: 10.34133/2019/6168209
3. Genangeli et al. (2023). Plants. DOI: 10.3390/plants12081730
4. CoMM-BIP Multimodal Plant Stress Models
5. AgEval Plant Stress Identification
