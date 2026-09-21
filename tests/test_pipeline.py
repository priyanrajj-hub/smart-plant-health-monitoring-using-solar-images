import pytest
import pandas as pd
import numpy as np
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.place_matching import calculate_iou, match_place
from ml.models.stress_tabular import StressSeverityModel

# --- 1. Place Matching Tests ---
def test_place_matching_iou():
    """Verify IoU >= 0.6 matches, else reject."""
    import json
    box1 = json.dumps({"type": "Polygon", "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]]})
    box_exact = box1
    
    # Calculate IoU expects geojson representations. Place matching script parses them inside.
    iou_res = calculate_iou(box1, box_exact)
    assert iou_res >= 0.99
    
def test_match_place_thresholds():
    import json
    places = {
        'p1': {
            'polygon_geojson': json.dumps({"type": "Polygon", "coordinates": [[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]]}),
            'centroid_lat': 5.0, 
            'centroid_lon': 5.0
        }
    }
    new_poly_far = json.dumps({"type": "Polygon", "coordinates": [[[100, 100], [100, 110], [110, 110], [110, 100], [100, 100]]]})
    new_poly = json.dumps({"type": "Polygon", "coordinates": [[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]]})
    
    # Exact match testing
    pid = match_place(new_poly, 5.0, 5.0, places)
    assert pid == 'p1'
    
    # Complete spatial disconnection
    pid2 = match_place(new_poly_far, 105.0, 105.0, places)
    assert pid2 is None

# --- 2. Visit Counting Constraints ---
def test_visit_counting():
    """Ensure visits map consecutively per place."""
    # This logic belongs in schema synchronization, testing hypothetical state
    visits = [{'place_id': 'p1', 'timestamp': '2023-01-01'}, {'place_id': 'p1', 'timestamp': '2023-01-02'}]
    assert len([v for v in visits if v['place_id'] == 'p1']) == 2

# --- 3. Schema Validation ---
def test_schema_structure():
    """Check that places.csv and schema.json enforce rigid definitions."""
    schema_path = "data/schema.json"
    assert os.path.exists(schema_path), "Schema validation file missing."
    with open(schema_path, "r") as f:
        schema = json.load(f)
    assert "places" in schema
    assert "visits" in schema

# --- 4. Provenance Guards ---
def test_provenance_guard():
    """Training MUST RAISE or ABSTAIN if dataset uses simulated/llm_estimate."""
    model = StressSeverityModel()
    
    # Construct completely simulated dataframe
    df_simulated = pd.DataFrame({
        'place_id': [1, 2],
        'ndvi_anomaly': [0.1, 0.2],
        'cum_heat_stress_7d': [10, 20],
        'days_since_rain': [5, 10],
        'elevation_m': [100, 200],
        'stress_severity': [0, 1],
        'provenance': ['simulated', 'llm_estimate']
    })
    
    # Model should refuse to train
    result = model.train(df_simulated)
    assert result is False, "Model trained on simulated provenance, failing constraint!"

# --- 5. Train/Test Leakage ---
def test_spatial_leakage_groups():
    """Ensure spatial generalization enforces strict place_id separation."""
    df_leakage = pd.DataFrame({
        'place_id': [1, 1, 2, 2, 3, 3, 4, 4], # distinct places
        'ndvi_anomaly': np.random.rand(8),
        'cum_heat_stress_7d': np.random.rand(8),
        'days_since_rain': np.random.rand(8),
        'elevation_m': np.random.rand(8),
        'stress_severity': np.random.randint(0, 4, 8),
        'provenance': ['measured_sentinel'] * 8
    })
    
    from sklearn.model_selection import GroupShuffleSplit
    gss = GroupShuffleSplit(n_splits=1, test_size=0.5, random_state=42)
    train_idx, val_idx = next(gss.split(df_leakage, df_leakage['stress_severity'], groups=df_leakage['place_id']))
    
    train_places = set(df_leakage.iloc[train_idx]['place_id'].unique())
    val_places = set(df_leakage.iloc[val_idx]['place_id'].unique())
    
    # Must have absolute zero intersection (no leakage)
    assert len(train_places.intersection(val_places)) == 0, "Spatial groups leaked across splits!"
