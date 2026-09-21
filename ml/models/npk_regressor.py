import lightgbm as lgb
import numpy as np
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import mean_absolute_error, r2_score

class NPKRegressor:
    def __init__(self):
        self.models = {} # dict for N, P, K
        self.features = ['soilgrids_n', 'soilgrids_p', 'soilgrids_k', 'ndvi', 'rain_30d', 'elevation_m']
        
    def train(self, df):
        """
        Train NPK regressor IF lab labels exist. Uses monotonic constraints.
        E.g. as SoilGrids N increases, predicted N must strictly not decrease.
        """
        if 'lab_n_ppm' not in df.columns or df['lab_n_ppm'].isnull().sum() == len(df):
            print("WARNING: No lab labels found. Will return strictly low_confidence priors.")
            return False
            
        gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
        train_idx, val_idx = next(gss.split(df, df['lab_n_ppm'], groups=df['place_id']))
        
        train_data = lgb.Dataset(df.iloc[train_idx][self.features], label=df.iloc[train_idx]['lab_n_ppm'])
        val_data = lgb.Dataset(df.iloc[val_idx][self.features], label=df.iloc[val_idx]['lab_n_ppm'])
        
        # Monotonic constraint: 1 for monotonically increasing with soilgrids_n proxy
        monotone_constraints = [1 if 'soilgrids' in f else 0 for f in self.features]
        
        params = {
            'objective': 'regression',
            'metric': 'mae',
            'monotone_constraints': monotone_constraints,
            'random_state': 42
        }
        
        self.models['N'] = lgb.train(params, train_data, valid_sets=[val_data])
        
        preds = self.models['N'].predict(df.iloc[val_idx][self.features])
        r2 = r2_score(df.iloc[val_idx]['lab_n_ppm'], preds)
        print(f"Validation R2 (N): {r2:.3f}")
        return True

    def predict(self, df):
        if not self.models:
            print("Abstaining. Falling back to ISRIC prior.")
            return {"status": "low_confidence", "reason": "no lab label for this place"}
            
        n_pred = self.models['N'].predict(df[self.features])
        return {"status": "ok", "N_ppm": n_pred.tolist()}
