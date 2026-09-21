import os
import csv
import firebase_admin
from firebase_admin import credentials, firestore

cred_path = os.getenv("FIREBASE_CREDENTIALS", "firebase_service_account.json")
if not os.path.exists(cred_path):
    print("WARNING: Firebase credentials not found. Ensure firebase_service_account.json is present.")
else:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()

COLLECTIONS_KEYS = {
    "places": "place_id",
    "visits": "visit_id",
    "satellite_observations": "obs_id"
}

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")

def import_csv_to_firestore():
    for coll_name, pk in COLLECTIONS_KEYS.items():
        csv_path = os.path.join(DATA_DIR, f"{coll_name}.csv")
        if not os.path.exists(csv_path):
            continue
            
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                batch = db.batch()
                count = 0
                for row in reader:
                    doc_ref = db.collection(coll_name).document(row[pk])
                    batch.set(doc_ref, row, merge=True)
                    count += 1
                    if count % 500 == 0:
                        batch.commit()
                        batch = db.batch()
                batch.commit()
            print(f"Imported {count} records back to {coll_name} in Firestore")
        except Exception as e:
            print(f"Error importing {coll_name}: {e}")

if __name__ == "__main__":
    if os.path.exists(cred_path):
        import_csv_to_firestore()
