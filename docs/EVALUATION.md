# Evaluation & Data Collection Strategy

This document outlines the requisite steps, constraints, and statistical thresholds necessary to bring the Canopy ML Pipeline from the structural placeholder architectures to production viability in the field without relying on mocked proxies.

## Current ML Component Capabilities & Limitations

**1. Simulated Data Dependencies**

- **Prior State**: The UI dynamically rendered crop health indicators relying explicitly on deterministic heuristic matrices and mock random variances in `index.html`.
- **Planned Mitigation**: Strict provenance enforcements are **planned to be deployed** across `ml/models`. No model will be permitted to train on labels explicitly tagged `simulated` or `llm_estimate`.

**2. Satellite Processing Latency**

- Absolute ground truth validation derived from Sentinel missions carries a 12-48 hour delay.
- Fast telemetry estimates rely on Open-Meteo forecasts coupled with spatial proxy interpolations.

## Out-Of-Distribution (OOD) Guarding

- **CNN Energy Scoring**: A deterministic Energy Score validation **is planned to wrap** around all image architectures (e.g. `CropDiseaseClassifier`). Field shots failing energy entropy thresholds will force an "Abstain" prediction rather than yielding aggressive false positives.
- **Monotonic NPK Modeling**: Regression models attempting to extrapolate SoilGrids background distributions **are planned to adhere** strictly to monotonic gradient rules relative to verifiable topological covariates. An absolute `low_confidence` marker **will trigger** if corresponding lab tags are missing.

## Data Collection Plan - Reaching Confidence Baselines

To successfully bypass the `insufficient_evidence` catch blocks authored in the structural pipeline, the following minimum training thresholds must be met by active field operators:

### Required Label Volumes

- **Disease & Pest Matrices (CNN)**: Requires a strict minimum of **200 verified images per target class**, obtained specifically from varying field lighting conditions (not just laboratory samples).
- **NPK & Stress Calibration (Tabular/Boosted)**: Requires **100 local lab soil-test labels** synchronized geographically (IoU > 0.6) with the farm locations to calibrate the local background gradients properly.

### Pilot Deployment Strategy (Tamil Nadu)

A 3-month physical pilot across Amrita engineering facilities and adjacent agrarian parcels will validate the structural ML ingestion code developed in Phase 1-9:

- **Weekly Collection**: Agronomists upload RGB images against specific polygons with validated disease notes manually into the UI panel.
- **Syncing Loop**: `scripts/import_csv_to_firestore.py` caches the data locally where GitHub workflows **evaluate models on frozen test sets and promote them only if performance improves over current metrics.**
