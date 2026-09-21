import os
import csv
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase (Requires FIREBASE_SERVICE_ACCOUNT.json)
cred_path = os.getenv("FIREBASE_CREDENTIALS", "firebase_service_account.json")
if not os.path.exists(cred_path):
    print("WARNING: Firebase credentials not found. Ensure firebase_service_account.json is present.")
else:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()

COLLECTIONS = ["places", "visits", "satellite_observations", "weather_daily", "soil_static", "sensor_readings", "images", "labels", "predictions", "place_history_features"]
DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")
os.makedirs(DATA_DIR, exist_ok=True)

def export_firestore_to_csv():
    for coll_name in COLLECTIONS:
        try:
            docs = db.collection(coll_name).stream()
            records = [doc.to_dict() for doc in docs]
            
            if not records:
                continue
                
            csv_path = os.path.join(DATA_DIR, f"{coll_name}.csv")
            headers = list(records[0].keys())
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for record in records:
                    writer.writerow(record)
                    
            print(f"Exported {len(records)} records from {coll_name} to {csv_path}")
        except Exception as e:
            print(f"Error exporting {coll_name}: {e}")

if __name__ == "__main__":
    if os.path.exists(cred_path):
        export_firestore_to_csv()
