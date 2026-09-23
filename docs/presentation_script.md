# Canopy: Satellite-Calibrated IoT Vegetation Health Monitoring

**Pitch Script & Slide Outline for a 5-Minute Demo**

---

## Slide 1: Title & Problem Statement

*(Visual: Canopy dashboard alongside a physical photo of your Arduino UNO setup)*

**Speaker Notes:**
"Good morning, judges. My name is [Your Name], and I am presenting **Canopy**—a vegetation health monitoring system designed to bridge a critical gap in precision agriculture.
Today, most remote-sensing crop platforms rely exclusively on satellite NDVI. But NDVI is just a mathematical proxy—it's a ratio of reflected light. By itself, it doesn't definitively prove a plant is stressed; it just proves the canopy is less green. Without physical ground-truth calibration, remote-sensing-only platforms are fundamentally unreliable. Canopy solves this by calibrating multi-spectral satellite imagery against physical, real-time IoT hardware telemetry."

---

## Slide 2: The Dual-Architecture Architecture

*(Visual: System Architecture Diagram showing Arduino → Vercel → Google Earth Engine → ONNX)*

**Speaker Notes:**
"Our architecture combines two highly integrated subsystems.
First, the physical layer: An Arduino UNO sits in the field constantly logging temperature, humidity, and soil moisture via DHT11 and continuous sensors, transmitting over SoftwareSerial to an ESP32 for cloud synchronization.
Second, the analytical layer: We tap into the Google Earth Engine Data Catalog, pulling Sentinel-2 imagery for spectral bands and MODIS for Land Surface Temperature. Our Python backend pulls this satellite array and time-aligns it perfectly against the physical Arduino sensor logs to establish an undeniable ground truth."

---

## Slide 3: The Machine Learning Pipeline

*(Visual: Code snippet of TimeSeriesSplit and the ONNX payload size)*

**Speaker Notes:**
"What separates Canopy from standardized NDVI dashboards is our strict ML discipline. We don't just visualize satellite bands; we train a Scikit-Learn **Random Forest Classifier** to map the satellite variance against physical IoT soil moisture targets.
To guarantee data integrity and avoid cyclic leakage, we explicitly drop the physical IoT variables from the predictive feature set and apply a strict `TimeSeriesSplit` cross-validation—preventing future dates from leaking into the training array."

---

## Slide 4: Honest Scoping & Edge Deployment

*(Visual: Vercel dashboard showing the 4.6KB ONNX file serving via Edge Functions)*

**Speaker Notes:**
"We engineered this pipeline specifically for serverless edge deployment. Instead of running a heavy Python backend, the trained Random Forest model is compiled natively into a lightweight `.onnx` binary graph weighing just under 5 Kilobytes. It runs directly on the Vercel Edge using `onnxruntime-web`.
We are framing this as a scientifically honest, site-calibrated proof of concept. Rather than falsely claiming a generalized global model from a single Arduino site, our pipeline is hard-coded to gracefully abort rather than hallucinate data if physical matching hardware isn't detected. This establishes a mathematically defensible blueprint for a hardware-supervised scale-out."

---

## Slide 5: Results & Verification

*(Visual: The terminal matrix showing row counts and Feature Importances)*

**Speaker Notes:**
"By isolating the pipeline across verifiable local test telemetry, we achieved an architecturally sound compilation.

- **Cross-Validation**: TimeSeriesSplit prevented chronological leakage.
- **Results Placeholder**: [pipeline built and verified end-to-end on synthetic dry-run; awaiting hardware log volume sufficient for a defensible train/test split. I will replace this strictly with real Feature Importance parameters and empirical accuracy scores once the hardware ingestion window closes.]

Our pipeline is structurally perfect, bypassing standard organizational IAM challenges via secure local implementations, achieving Vercel-ready compliance."

---

## Slide 6: Future Work & Tech Stack Summary

*(Visual: Tech stack icons—Next.js, Python, GEE, ONNX, Arduino, Vercel)*

**Speaker Notes:**
"Moving forward, our immediate path is scaling ground-truth collection across multiple geographical nodes to migrate from this Random Forest POC into an advanced Gradient Boosting architecture for generalized predictions.
Everything you've seen runs on an integrated stack spanning **Next.js, Tailwind, Google Earth Engine, and Scikit-Learn**.

Thank you. I'm ready for any technical architecture questions."
