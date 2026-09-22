import os
import psycopg2
import csv
from datetime import datetime
from dotenv import load_dotenv

# Load Vercel/Neon .env configurations
load_dotenv('.env.local')

DB_URL = os.getenv('DATABASE_URL')

def export_telemetry_csv():
    if not DB_URL:
        print("ERROR: DATABASE_URL not found in environment variables. Run 'npx vercel env pull'.")
        return

    print("Connecting to Neon Postgres...")
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()

        query = """
            SELECT 
                v.visit_id, v.place_id, v.local_date, v.local_time, v.visit_number_for_place,
                o.ndvi, o.temperature_c, o.humidity_pct, o.capacitive_pf, o.acoustic_val,
                l.label_type, l.label_value
            FROM visits v
            LEFT JOIN observations o ON v.visit_id = o.visit_id
            LEFT JOIN labels l ON v.visit_id = l.visit_id
            ORDER BY v.visit_timestamp_utc ASC
        """
        
        cur.execute(query)
        rows = cur.fetchall()

        if not rows:
            print("No telemetry data found.")
            return

        # Extract headers from cursor description
        headers = [desc[0] for desc in cur.description]
        
        # Build safe export filename
        date_str = datetime.now().strftime('%Y-%m-%d')
        output_file = f"data/canopy_export_{date_str}.csv"
        
        os.makedirs('data', exist_ok=True)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
            
        print(f"SUCCESS: Exported {len(rows)} physical visits to {output_file} for model re-training pipeline.")

    except Exception as e:
        print(f"Fatal PostgreSQL Extraction Error: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    export_telemetry_csv()
