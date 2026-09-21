import lightgbm as lgb
import pandas as pd
import numpy as np
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import cohen_kappa_score

class StressSeverityModel:
    def __init__(self):
        self.model = None
        self.features = ['ndvi_anomaly', 'cum_heat_stress_7d', 'days_since_rain', 'elevation_m']
        
    def train(self, df):
        """
        Train using rigorous group splits by place_id (Spatial Generalization)
        Target: stress_severity (0=None, 1=Low, 2=Moderate, 3=High)
        """
        # Enforce Provenance rule: MUST NOT train on simulated or LLM targets.
        valid_provenance = df['provenance'].isin(['measured_sentinel', 'measured_sensor', 'user_label', 'lab_label'])
        df_clean = df[valid_provenance].copy()
        
        if df_clean.empty:
            print("ERROR: No valid non-simulated data to train on. Abstaining.")
            return False
            
        gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
        train_idx, val_idx = next(gss.split(df_clean, df_clean['stress_severity'], groups=df_clean['place_id']))
        
        train_data = lgb.Dataset(df_clean.iloc[train_idx][self.features], label=df_clean.iloc[train_idx]['stress_severity'])
        val_data = lgb.Dataset(df_clean.iloc[val_idx][self.features], label=df_clean.iloc[val_idx]['stress_severity'])
        
        params = {
            'objective': 'multiclass',
            'num_class': 4,
            'metric': 'multi_error',
            'boosting_type': 'gbdt',
            'random_state': 42
        }
        
        self.model = lgb.train(
            params, 
            train_data, 
            num_boost_round=100, 
            valid_sets=[val_data], 
        )
        
        # Eval
        preds = self.predict(df_clean.iloc[val_idx])
        pred_classes = np.argmax(preds, axis=1)
        kappa = cohen_kappa_score(df_clean.iloc[val_idx]['stress_severity'], pred_classes, weights='quadratic')
        print(f"Validation Quadratic Weighted Kappa: {kappa:.3f}")
        return True
        
    def predict(self, df):
        if self.model is None:
            raise ValueError("Model not trained.")
        return self.model.predict(df[self.features])
