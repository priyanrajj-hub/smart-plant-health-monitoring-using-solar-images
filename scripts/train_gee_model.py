import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit # Using TimeSeries to prevent leakage
from sklearn.metrics import classification_report, accuracy_score
import warnings

# skl2onnx required for edge inferencing
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

def train():
    dataset_path = 'dataset/gee_telemetry.csv'
    if not os.path.exists(dataset_path):
        print(f"ERROR: {dataset_path} not found. Run gee_ingestion.py first.")
        return

    df = pd.read_csv(dataset_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date') # Absolute sorting required for TimeSeriesSplit

    print(f"Loaded {len(df)} telemetry samples.")
    if len(df) < 50:
        print("WARNING: Dataset contains fewer than 50 verified ground-truth loops. Model is highly likely to overfit.")
        print("Note: This implementation is strictly a 'one-site calibrated proof-of-concept' mapping IoT sensors to specific physical coordinates.")

    if 'Target_Stressed' not in df.columns:
        raise ValueError("[FATAL] Training pipeline aborted: Ground truth target 'Target_Stressed' is missing from telemetry. Refusing to synthesize fake labels.")
        
    # Feature Selection (Explicitly excluding Arduino sensory targets like Soil Moisture!)
    # We only train on OSINT / GEE values.
    features = ['NDVI', 'LST']
    
    # Drop NaNs
    df = df.dropna(subset=features + ['Target_Stressed'])

    X = df[features].values
    y = df['Target_Stressed'].values

    # Strict Time-Based Split (Guard against day-to-day autocorrelation leakage)
    tscv = TimeSeriesSplit(n_splits=3)
    
    model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)

    fold = 1
    print("\n--- Validating via TimeSeriesSplit ---")
    for train_index, test_index in tscv.split(X):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
        
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        print(f"Fold {fold} - Accuracy: {acc:.2f} | Train Size: {len(X_train)} | Test Size: {len(X_test)}")
        fold += 1

    # Train final deployment model on 100% of available data
    model.fit(X, y)
    
    # Output Feature Importance
    importances = model.feature_importances_
    print("\n--- Feature Importance ---")
    for fname, imp in zip(features, importances):
        print(f"{fname}: {imp:.4f}")

    # Compile to ONNX for Vercel edge deployment
    print("\nExporting ONNX graph targeting Vercel Edge Serverless execution...")
    initial_type = [('float_input', FloatTensorType([None, len(features)]))]
    onx = convert_sklearn(model, initial_types=initial_type)
    
    os.makedirs('../public/models', exist_ok=True)
    onnx_path = '../public/models/gee_forest.onnx'
    with open(onnx_path, "wb") as f:
        f.write(onx.SerializeToString())
        
    print(f"Success! Model compiled natively to {onnx_path}.")
    size_kb = os.path.getsize(onnx_path) / 1024
    print(f"Payload Size: {size_kb:.1f} KB (Serverless Safe: {'YES' if size_kb < 1000 else 'NO'})")

if __name__ == "__main__":
    warnings.filterwarnings('ignore')
    train()
