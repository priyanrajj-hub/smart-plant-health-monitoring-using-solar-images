# Canopy ML Pipeline Status Matrix

| Phase | Task Description | Verification Criteria | Status |
| --- | --- | --- | --- |
| **1** | System Audit & Cleanup | No `Math.random()`, fake `LIVE` badges, or uncalibrated high confidence indicators exist. | **Complete** (`test_ui_honesty`, manual `grep`) |
| **2** | Schema & Database Rules | Data validates against `schema.json`. Firebase sync and caching logic function properly. | **Partial** (`test_schema_structure` passes but Firebase visit syncing lacks tests) |
| **3** | Telemetry Pipelines | Sentinel-2, Open-Meteo, and SoilGrids integrations fetch real physical environment telemetry. | **Partial** (API proxy is established, needs end-to-end endpoint tests for Sentinel-2, Open-Meteo, SoilGrids) |
| **4** | Feature Engineering | Physical models track trailing weather deficits correctly based on API metrics. | **Not Started** |
| **5** | Tabular Models (Stress) | The active-learning pipeline trains LightGBM models or abstains when valid empirical training visits `< 50`. | **Not Started** (no stress model trained, only abstain logic exists) |
| **6** | Vision Model (Crop Disease) | EfficientNet CNN pipeline trains smoothly when image sets scale appropriately. | **Not Started** |
| **7** | Soil NPK Estimator | NPK baseline mapping models process trailing dataset logs efficiently. | **Not Started** |
| **8** | Risk Engine API Serving | Process models and serve analytical queries dynamically to the frontend endpoints. | **Not Started** |
| **9** | Active Learning CI/CD | Retraining logic processes automatically on Github Action schedulers. | **Not Started** |
| **10** | Final Evaluation & Docs | Prove real testing scores vs simulated outputs and freeze test sets. | **Not Started** |
