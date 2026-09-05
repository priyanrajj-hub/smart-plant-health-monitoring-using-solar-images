# Low-Cost Capacitive Dielectric Sensing for Early Plant Water-Stress Detection

> **SIH26180 Capstone Project / Research Methodology**
> An alternative to THz-TDS spectroscopy utilizing low-cost capacitive dielectric sensing to predict early-stage plant water stress through diurnal baseline-drift correction.

![Dashboard Status](https://img.shields.io/badge/Dashboard-Live-brightgreen)
[Live Dashboard Website](https://priyanrajj-hub.github.io/MIC-REVIEW-1-PROJECT/) (If configured)

## Capstone Review Milestones

| Review Stage | Submissions & Focus | Directory Link |
| :--- | :--- | :--- |
| **Review 0** | Group members, project title, hardware/software split, intro & end outcome | [docs/review-0/](docs/review-0/) |
| **Review 1** | Literature survey (15 papers), methodology, simulation model (30%), hardware model (30%), presentation, article draft | [docs/review-1/](docs/review-1/) |
| **Review 2** | Literature survey (15 papers), simulation model (60%), hardware model (60%), hardware demo presentation, article draft (methodology) | [docs/review-2/](docs/review-2/) |
| **Review 3** | Literature survey (10 papers), simulation model (100%), hardware model (100%), presentation with hardware demo, article draft (results & discussion) | [docs/review-3/](docs/review-3/) |

## Project Resources

### Literature
Contains PDFs and markdown summaries of surveyed papers regarding capacitive/acoustic sensing approaches.
- [Literature Directory](literature/)

### Hardware
Contains schematics, wiring diagrams, BOM, and the multi-sensor firmware.
- [Hardware & Firmware](hardware/)
- [Source Code](hardware/firmware/)

### Simulation
Contains the simulation model source code and output plots.
- [Software / Simulation](software/simulation/)

### Media
Contains actual prototype photos, sensor rig, and result plots.
- [Media Directory](media/)
- ![Hardware Prototype Placeholder](media/images/Hardware-Prototype-Photos-TODO.txt) (TODO: update link to actual image once uploaded)
- ![Key Results](docs/images/architecture_diagram.png)

### Presentations
Contains all SIH/review presentation decks (PPTX + PDF formats).
- [Presentations](media/pptx-pdf/)

---

## Details from Base Implementation
# Stressor-Aware Capacitive Sensing: A Diurnally-Corrected, Conformal-Bounded Model Pipeline
>
> A comprehensive open-source Python framework for multi-class plant stress detection via diurnally-corrected leaf capacitive sensing.

![CI](https://github.com/priyanrajj-hub/MIC-REVIEW-1-PROJECT/actions/workflows/ci.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![Data Status: Synthetic](https://img.shields.io/badge/data-synthetic_(real_trial_pending)-orange.svg)

## Project Summary

This repository contains a complete machine learning pipeline for detecting distinct types of plant stress (underwater, overwater, nutrient deficiency) using low-cost hardware. It introduces a novel approach of diurnal baseline-drift correction for capacitive sensors, and wraps the Random Forest/XGBoost classifier in a conformal prediction framework to provide calibrated confidence intervals for every readout. This ensures high reliability to guide precision agriculture interventions.

## How It Works

![System Architecture Diagram](docs/images/architecture_diagram.png)

The hardware layer utilizes an FDC1004 capacitive probe measuring leaf dielectric permittivity, combined with DS18B20 temperature sensors and a BH1750 ambient light sensor. The ESP32 orchestrates data logging.
During preprocessing, a diurnal correction model effectively cancels out baseline capacitance drift caused by natural temperature and light cycles. The corrected signal is then pushed to a multi-class predictive model. Finally, the conformal wrapper yields a calibrated prediction set rather than a raw point estimate, expressing confidence matching an empirical coverage target (e.g., 90%).

## Data Pipeline

![Data Pipeline Diagram](docs/images/data_pipeline_diagram.png)

Raw timeseries logs enter the pipeline and undergo diurnal drift correction. Feature engineering generates robust indicators such as rolling slopes, leaf-ambient temperature differential ($\Delta T$), and corrected capacitance limits. A stratified split divides training, conformal calibration, and holdout testing sets. The Random Forest operates on the engineered data, evaluated robustly against the test set for its classification metrics and conformal coverage.

## Data and Methodology Disclosure

**Important Note for Reviewers:**
The dataset currently provided in this repository (`data/raw/synthetic_trial_dataset.csv`) is a **Methodology Validation Dataset (Synthetic)**. It is not currently presenting real 3-class biological trial results.

While the dataset utilizes real-world historical environmental telemetry (ambient temperature and light flux pulled via Open-Meteo API) as a baseline, the internal FDC1004 capacitance response curves are mathematically synthesized based on the expected diurnal drift and theoretical stress behavior.

This dataset serves entirely to:

1. Prove the computational pipeline (Data Ingestion $\rightarrow$ Diurnal Correction $\rightarrow$ XGBoost Classification $\rightarrow$ Conformal Confidence Calibration) is robust and operational.
2. Demonstrate the mathematical validity of the diurnal-correction algorithm prior to real sensor deployment.

For the final methodology evaluation (Phase 3 of the project), this synthetic generator will be swapped for in-vivo controlled trials consisting of physical *Solanum lycopersicum* specimens undergoing genuine watering/nutrient schema manipulations. The pipeline is architected to ingest the real test logs identically.

- **Storage**: The validation dataset is included in this repository at `data/raw/synthetic_trial_dataset.csv`.
- **Schema**: Review the exact column definitions and sampling rate at [data/DATA_SCHEMA.md](data/DATA_SCHEMA.md).

### GitHub-Hosted Real Datasets & Open Code References

If you prefer to pull real datasets and research data directly from open GitHub repositories, the following repositories contain excellent plant stress real-world telemetry and multi-modal models:

1. **[arbab-ml/AgEval](https://github.com/arbab-ml/AgEval)**: Contains code and dataset subsets for complex plant stress identification and classification.
2. **[MorillaLab/CoMM-BIP](https://github.com/MorillaLab/CoMM-BIP)**: A comprehensive open-source repository focusing on multi-modal learning for plant stress. Included are real datasets and examples of loading transcriptomics, metabolomics, and phenomics data directly from CSV files.
3. **[Between-the-Fjords/funcab_data](https://github.com/Between-the-Fjords/funcab_data)**: An extensive botanical and environmental open research repository on GitHub housing massive CSV records of soil temperature, variable soil moisture, and ecosystem environment data.

## Installation

Clone this repository and set up the Python environment:

```bash
git clone https://github.com/priyanrajj-hub/MIC-REVIEW-1-PROJECT.git
cd MIC-REVIEW-1-PROJECT
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

## Usage

Run the pipeline end-to-end using the master orchestrator script.

### 1. Execute with Synthetic Verification Data (Default)

To generate the robust synthetic dataset across 6 plants and execute the complete ML/Conformal validation pipeline:

```bash
python run_pipeline.py --source synthetic
```

### 2. Execute with Real Hardware Trials

The pipeline natively supports your live **FDC1004 / DS18B20** hardware trials.

1. Capture your sensor readings and format them as a CSV exactly matching `data/DATA_SCHEMA.md`.
2. Move the CSV directly into `data/raw/` (e.g., `data/raw/live_trial.csv`).
3. Execute the orchestrator in ingest mode:

```bash
python run_pipeline.py --source real --real_csv "data/raw/live_trial.csv"
```

*Note: `validate_dataset.py` will actively block execution if the CSV is missing columns or contains unsupported condition vectors to prevent corrupted downstream analysis.*

## Results

*SYNTHETIC-DATA PILOT RESULT, NOT YET VALIDATED ON REAL PLANTS*

### Confusion Matrix

![Confusion Matrix](docs/images/confusion_matrix.png)

### Diurnal Correction Action

![Diurnal Correction Before/After](docs/images/diurnal_correction_before_after.png)

### Lead-Time Benchmark Comparison (Synthetic)

| System / Reference | Detection Lead-Time vs Visible Symptoms |
| -------------------- | ----------------------------------------- |
| **This framework (Synthetic)** | ~X hours |
| AdapTree (Garg et al., 2025) | TBD |
| Bioristor (Janni et al., 2019) | ~30 hours |
| Genangeli et al. (2023) | TBD |

## Physiological Basis for Class Separability

The experimental validity of differentiating physical stress vectors via low-frequency capacitance lies in distinct physiological mechanics:

1. **Underwatering (Drought Stress):** Causes a systemic drop in bulk leaf volumetric water content (VWC), heavily reducing the dielectric constant of the leaf tissue, shifting baseline capacitance downward relative to the ambient air gap.
2. **Overwatering (Hypoxia):** Saturates the apoplastic space and induces root hypoxia, causing complex cell-membrane degradation. This alters the electrical double-layer capacitance of the leaf tissue differently than simple water-loss.
3. **Nutrient Deficiency:** Causes alterations in ionic sap concentrations. While true Electrochemical Impedance Spectroscopy (EIS) across multi-frequency sweeps is required to perfectly isolate ion profiles, changes in bulk tissue conductivity indirectly influence the fixed 25 kHz AC capacitive projection measured by the FDC1004, enabling correlative separation after rigorous diurnal normalization.

By anchoring these signatures against a robust LOPO-CV (Leave-One-Plant-Out Cross-Validation) framework, the model avoids overfitting to individual plant topographies.

### Directory Structure

```
capacitive-plant-stress-sensing/
├── data/
│   ├── raw/
│   │   └── synthetic_trial_dataset.csv
│   ├── processed/
│   └── DATA_SCHEMA.md
├── docs/
│   ├── images/
│   ├── architecture_diagram.md
│   └── data_pipeline_diagram.md
├── models/
├── src/
│   ├── data_generation/
│   │   └── generate_synthetic_dataset.py
│   ├── evaluation/
│   │   └── evaluate_and_report.py
│   ├── firmware/
│   │   └── esp32_logger/
│   ├── models/
│   │   ├── conformal_wrapper.py
│   │   └── train_classifier.py
│   └── preprocessing/
│       ├── diurnal_correction.py
│       └── feature_engineering.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── requirements.txt
└── README.md
```

## Hardware / Firmware

The core logging architecture leverages:

- **ESP32 Microcontroller**
- **FDC1004 Capacitive Probe** (Leaf dielectric permittivity)
- **2x DS18B20** (Leaf-contact and ambient temperature)
- **BH1750** (Light intensity lux)
- **Capacitive Soil Moisture Sensor** (Baseline reference)

Firmware templates and wiring notes are located in `src/firmware/esp32_logger/`.

## Novelty / Research Contributions

- **Multi-Class Stressor Discrimination**: Replaces pure anomaly-detection with explicit class categorization of unique stress modalities on a single low-cost probe architecture.
- **Diurnal Baseline-Drift Correction**: Actively models and subtracts expected circadian baseline responses governed by thermodynamic and irradiance variables, increasing classification SNR.
- **Conformal Prediction Calibration**: Wraps the inference in a post-hoc rigorous confidence set, bridging the gap between hardware heuristic metrics and statistical reliability.

## Citation

If you utilize this framework or methodology, please cite:

```bibtex
@article{placeholder2026,
  author={priyanrajj-hub},
  title={Stressor-Aware Capacitive Sensing: A Diurnally-Corrected, Confidence-Calibrated TinyML Framework for Multi-Class Plant Stress Detection},
  year={2026},
  journal={TBD}
}
```

## References & Open GitHub Implementations

1. Garg et al. (2025). AdapTree. *Sensors*. DOI: [10.3390/s25103149](https://doi.org/10.3390/s25103149)
2. Janni et al. (2019). Bioristor. *Plant Phenomics*. DOI: [10.34133/2019/6168209](https://doi.org/10.34133/2019/6168209)
3. Genangeli et al. (2023). *Plants*. DOI: [10.3390/plants12081730](https://doi.org/10.3390/plants12081730)
4. *CoMM-BIP Multimodal Plant Stress Models* (Morilla Lab). Source Code and Data: [GitHub Repository](https://github.com/MorillaLab/CoMM-BIP)
5. *AgEval Plant Stress Identification* (Arbab ML). Source Code and Dataset: [GitHub Repository](https://github.com/arbab-ml/AgEval)

## License

Provided under the [MIT License](LICENSE).

---
**Contact:** priyanrajj-hub
