# Model Card: Bayesian-weighted Fusion CSI (Composite Stress Index)

## Model Details

- **Architecture:** Naive Bayes / Probabilistic Weighting Fusion Model
- **Task:** Classifying agricultural plant health and stress categories
- **Version:** 1.0 (Phase 5)

## Intended Use

- Intended for real-time combination of isolated hardware telemetry data (capacitance moisture) and global NDVI indices.
- Designed as a fallback layer where traditional neural network inferences may be computationally prohibitive.
- **Out of Scope Use Cases:** Direct prediction of plant pathogens based solely on spatial data.

## Metrics

- Metrics currently TBD [Not yet evaluated on final held-out validation set].

## Limitations

- Model weighting relies on regional geographic assumptions and requires localized tuning per crop type.
