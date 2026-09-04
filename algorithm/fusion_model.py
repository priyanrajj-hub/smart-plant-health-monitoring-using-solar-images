import numpy as np
from skimage import feature
from collections import deque
# We will just write the structure using basic skimage to process random arrays or real local matrices.

class AgrisenseFusionModel:
    def __init__(self, history_size=5):
        self.texture_threshold = 0.65
        self.temporal_threshold = 0.50
        self.history = deque(maxlen=history_size)

        
    def rgb_to_nndvi(self, rgb_array):
        # Normal ExG heuristic setup mapped -1 to 1 proxy
        r, g, b = rgb_array[0], rgb_array[1], rgb_array[2] 
        exg = 2 * g - r - b 
        return np.clip(exg / 255.0, -1, 1)

    def temporal_anomaly_layer(self, current_scene, baseline_rolling_avg):
        # Simulated delta of rolling historical
        delta = current_scene - baseline_rolling_avg
        change_score = np.abs(delta)
        return change_score

    def texture_anomaly_layer(self, image_patch):
        # Now Genuinely Computing LBP instead of random number
        # Convert RGB to grayscale manually assuming shape (16, 16, 3)
        if len(image_patch.shape) == 3:
            gray = np.dot(image_patch[...,:3], [0.2989, 0.5870, 0.1140])
        else:
            gray = image_patch
            
        radius = 1
        n_points = 8 * radius
        lbp = feature.local_binary_pattern(gray, n_points, radius, method="uniform")
        
        # Calculate a simple histogram anomaly 
        # (Uniform patterns > n_points denote rough edges/lesions potentially)
        anomalies = np.sum(lbp >= n_points)
        total_pixels = lbp.shape[0] * lbp.shape[1]
        
        return min(anomalies / float(total_pixels) * 5.0, 1.0) # normalizer heuristic

    def predict_field_risk(self, rgb_patch):
        # 1. Base Proxy Index
        base_nndvi = self.rgb_to_nndvi(np.mean(rgb_patch, axis=(0,1)))
        
        # 2. Temporal (Rolling Buffer)
        # If history is empty, assume current as baseline to prevent massive delta on day 1
        if not self.history:
             baseline_history = base_nndvi
        else:
             baseline_history = sum(self.history) / len(self.history)
             
        temporal = self.temporal_anomaly_layer(base_nndvi, baseline_history)
        
        # Add current capture to the rolling buffer for future checks
        self.history.append(base_nndvi)
        
        # 3. LBP Texture Score (Genuinely Computed)
        texture = self.texture_anomaly_layer(rgb_patch)
        
        risk_score = (0.4 * (1.0 - base_nndvi)) + (0.3 * temporal) + (0.3 * texture)
        
        return {
            "nNDVI_raw": base_nndvi,
            "texture_anomaly": texture,
            "temporal_change": temporal,
            "fused_macro_risk": min(max(risk_score, 0), 1.0)
        }

if __name__ == "__main__":
    fusion = AgrisenseFusionModel(history_size=5)
    
    print("\n--- Test 1: Gradient Image ---")
    gradient_img = np.linspace(0, 255, 32*32*3).reshape((32, 32, 3)).astype(np.uint8)
    print(fusion.predict_field_risk(gradient_img))
    
    print("\n--- Test 2: Solid Color Image (Simulating sudden anomaly changes) ---")
    solid_img = np.ones((32, 32, 3), dtype=np.uint8) * 128
    print(fusion.predict_field_risk(solid_img))
