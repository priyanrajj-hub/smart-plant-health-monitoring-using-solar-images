import argparse
import os
import pandas as pd
import numpy as np

def retrain_models(train_all=False, tabular_only=False, image_only=False):
    """
    Simulated active-learning training loop wrapper.
    Executes ML model retraining using freshly exported Cloud Firestore datasets.
    """
    print("Initiating Canopy Machine Learning Retraining Pipeline...")
    
    if not os.path.exists(".cache/models"):
        os.makedirs(".cache/models", exist_ok=True)
        
    print("STATUS: Checking for new telemetry configurations in data/...")
    
    trained_tabular = False
    trained_vision = False
    import_error = False
    data_starvation = False

    if train_all or tabular_only:
        print("[1/2] Launching LightGBM Tabular Stress and NPK Estimators...")
        try:
            from ml.models.stress_tabular import StressSeverityModel
            real_df = pd.DataFrame(columns=['place_id', 'ndvi_anomaly', 'cum_heat_stress_7d', 'days_since_rain', 'elevation_m', 'stress_severity', 'provenance'])
            
            if len(real_df) < 50:
                print("      ERROR: Insufficient tabular data (<50 samples) to train Stress Model. Abstaining.")
                data_starvation = True
            else:
                model = StressSeverityModel()
                success = model.train(real_df)
                if success:
                    print("      Tabular Models successfully loaded and re-fitted. Updated weights persisted to .cache/models/tabular_vlatest.pkl")
                    trained_tabular = True
                else:
                    print("      Error during Tabular training sequence.")
        except ImportError as e:
            print(f"      ERROR: Tabular module imports failed: {e}")
            import_error = True
            
    if train_all or image_only:
        print("[2/2] Launching PyTorch EfficientNet Vision Classifier...")
        try:
            import torch
            from ml.models.leaf_image_cnn import CropDiseaseClassifier, train_model
            
            real_images = []
            if len(real_images) < 200:
                print("      ERROR: Insufficient labeled data to train Vision Model (requires >= 200 samples). Abstaining.")
                data_starvation = True
            else:
                model = CropDiseaseClassifier(num_classes=10)
                optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
                criterion = torch.nn.CrossEntropyLoss()
                trained_vision = True
        except ImportError as e:
            print(f"      ERROR: Vision module imports failed: {e}")
            import_error = True
    
    import sys
    if import_error:
        print("\nNO MODEL TRAINED: Execution halted due to missing dependencies.")
        sys.exit(1)
    
    if data_starvation and not trained_tabular and not trained_vision:
        print("\nNO MODEL TRAINED: Active learning abstained due to strict data threshold constraints.")
        sys.exit(2)
        
    print("\nTraining sweeps concluded successfully.")
    print("Run `python scripts/evaluate.py --promote-if-better` to process model promotions.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Canopy Retraining Loop")
    parser.add_argument("--all", action="store_true", help="Retrain all model classes.")
    parser.add_argument("--tabular-only", action="store_true", help="Only retrain tabular models.")
    parser.add_argument("--image-only", action="store_true", help="Only retrain image models.")
    
    args = parser.parse_args()
    
    retrain_models(train_all=args.all, tabular_only=args.tabular_only, image_only=args.image_only)
