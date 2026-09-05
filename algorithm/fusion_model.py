import math
import numpy as np
import sys
import os
from skimage import feature
from collections import deque
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from algorithm.weather_service import get_precipitation_deficit
from GlobalPlantHealth.backend.sentinel_service import get_punjab_image_patch

def moonlight_fusion(C, A, N, R, meta, prev_csi, dt, tau, threshold):
    """
    MOONLIGHT: Multi-Modal Oscillation-Optical fusion with Nocturnal-drift correction
    """
    EPS = 1e-6
    # 1. Compute live reliability weights from metadata
    w_C = 1 - min(abs(meta['delta_T']) / meta.get('T_max', 20.0), 1.0)
    w_A = 1 - min(meta['noise_sigma'] / meta.get('noise_sigma_max', 10.0), 1.0)
    w_N = (1 - meta.get('cloud_frac', 0.0)) ** 2
    w_R = 0.0 if meta.get('irrigation_flag', False) else 1.0
    
    weights = [w_C, w_A, w_N, w_R]
    signals = [C, A, N, R]

    # 2. Weighted aggregation with fallback
    total_w = sum(weights)
    if total_w < EPS:
        csi_raw = prev_csi if prev_csi is not None else 0.0
    else:
        csi_raw = sum(w * x for w, x in zip(weights, signals)) / total_w

    # 3. Exponential temporal smoothing
    lam = 1 - math.exp(-dt / tau) if tau > 0 else 1.0
    csi = csi_raw if prev_csi is None else lam * csi_raw + (1 - lam) * prev_csi

    # 4. Confidence decomposition
    mean_w = sum(weights) / len(weights)
    var_w = sum((w - mean_w) ** 2 for w in weights) / len(weights)
    confidence = max(weights) / (var_w + 1)

    # 5. Lead-time estimate
    lead_time = None
    if prev_csi is not None and dt > 0:
        slope = (csi - prev_csi) / dt
        if slope > EPS:
            lead_time = (threshold - csi) / slope

    return {
        "csi": round(csi, 4),
        "confidence": round(confidence, 4),
        "weights": {"capacitive": round(w_C, 3), "acoustic": round(w_A, 3), "ndvi_texture": round(w_N, 3), "rainfall": round(w_R, 3)},
        "lead_time_hours": round(lead_time, 1) if lead_time else None,
        "label": "ESTIMATED (linear trend) — not a forecast model"
    }

class AgrisenseFusionModel:
    def __init__(self, history_size=5):
        self.history = deque(maxlen=history_size)
    
    def rgb_to_nndvi(self, rgb_array):
        r, g, b = rgb_array[0], rgb_array[1], rgb_array[2] 
        exg = 2 * g - r - b 
        return np.clip(exg / 255.0, -1, 1)

    def texture_anomaly_layer(self, image_patch):
        if len(image_patch.shape) == 3:
            gray = np.dot(image_patch[...,:3], [0.2989, 0.5870, 0.1140])
        else:
            gray = image_patch
        radius = 1
        n_points = 8 * radius
        lbp = feature.local_binary_pattern(gray, n_points, radius, method="uniform")
        anomalies = np.sum(lbp >= n_points)
        total_pixels = lbp.shape[0] * lbp.shape[1]
        return min(anomalies / float(total_pixels) * 5.0, 1.0) 

    def predict_field_risk(self, rgb_patch=None, invoke_apis=False, prev_csi=0.2):
        if invoke_apis or rgb_patch is None:
            rgb_patch = get_punjab_image_patch()
            weather_data = get_precipitation_deficit()
        else:
            weather_data = {"deficit_mm": 0.0, "status": "SYNTHETIC_TEST"}

        base_nndvi = self.rgb_to_nndvi(np.mean(rgb_patch, axis=(0,1)))
        
        # C (Capacitive), A (Acoustic), N (NDVI Texture), R (Rainfall)
        C = 0.4 # Proxy ground-truth baseline
        A = 0.2 # Proxy acoustic string
        N = self.texture_anomaly_layer(rgb_patch)
        R = min(max(weather_data['deficit_mm'] / 50.0, 0.0), 1.0)
        
        # Meta for dynamic weighting
        meta = {
            'delta_T': 2.5, 'T_max': 20.0,       # C fail bounds
            'noise_sigma': 2.0, 'noise_sigma_max': 10.0, # A fail bounds
            'cloud_frac': 0.15,                 # N fail bounds
            'irrigation_flag': False            # R fail bounds
        }
        
        result = moonlight_fusion(C, A, N, R, meta, prev_csi=prev_csi, dt=24.0, tau=48.0, threshold=0.7)
        # Append nNDVI_raw and status to output payload
        result['nNDVI_raw'] = base_nndvi
        result['data_status'] = weather_data.get('status', 'PROXY')
        return result

if __name__ == "__main__":
    fusion = AgrisenseFusionModel()
    print("--- Testing Live Api MOONLIGHT Fusion ---")
    print(fusion.predict_field_risk(invoke_apis=True))
