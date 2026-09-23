import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import warnings
warnings.filterwarnings('ignore')

# 1. Synthesize Realistic Telemetry Data (500 rows)
np.random.seed(42)
dates = pd.date_range(start='2023-01-01', periods=500, freq='D')
temp = np.random.normal(25, 5, 500)
hum = np.random.normal(55, 10, 500)
soil = np.random.normal(40, 15, 500)
ndvi = np.clip(np.random.normal(0.5, 0.2, 500), 0, 1)
lst = temp + np.random.normal(5, 2, 500)

df = pd.DataFrame({'date': dates, 'temperature': temp, 'humidity': hum, 'soil_moisture': soil, 'NDVI': ndvi, 'LST': lst})
df['Target_Stressed'] = np.where((df['soil_moisture'] < 25) | (df['LST'] > 40) | (df['NDVI'] < 0.25), 1, 0)

os.makedirs('dataset', exist_ok=True)
df.to_csv('dataset/synthetic_gee_telemetry.csv', index=False)
print('Synthesized dataset generated: dataset/synthetic_gee_telemetry.csv')

# 2. Train and Export Model
features = ['NDVI', 'LST']
X = df[features].values
y = df['Target_Stressed'].values

model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
model.fit(X, y)
acc = model.score(X, y)
print(f'Random Forest trained on synthetic proxy (Accuracy: {acc:.2f})')

# Output Feature Importance
importances = model.feature_importances_
print("\n--- Feature Importance ---")
for fname, imp in zip(features, importances):
    print(f"{fname}: {imp:.4f}")

# 3. Compile ONNX Binary
initial_type = [('float_input', FloatTensorType([None, len(features)]))]
onx = convert_sklearn(model, initial_types=initial_type)

os.makedirs('public/models', exist_ok=True)
onnx_path = 'public/models/gee_forest.onnx'
with open(onnx_path, 'wb') as f:
    f.write(onx.SerializeToString())

size_kb = os.path.getsize(onnx_path) / 1024
print(f'ONNX payload built successfully: public/models/gee_forest.onnx ({size_kb:.2f} KB)')
print(f"Edge Deployable Size: {'YES' if size_kb < 1000 else 'NO'}")
