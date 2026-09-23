import serial
import csv
import time
import re
from datetime import datetime

ARDUINO_PORT = 'COM6' 
BAUD_RATE = 9600
CSV_FILE = 'sensor_logs.csv'

def main():
    print(f"✅ Linking to Physical Hardware on {ARDUINO_PORT} at {BAUD_RATE} baud...")
    
    try:
        ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=2)
        print("✅ Sensor Array Connected! Aggregating telemetry frames...\n")
    except serial.SerialException as e:
        print(f"❌ Handshake failed on {ARDUINO_PORT}. Is the UNO plugged in?")
        print(e)
        return

    # Check if CSV exists, if not, write the header
    try:
        with open(CSV_FILE, 'x', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'temperature', 'humidity', 'soil_moisture'])
            print(f"Created new ground truth matrix at: {CSV_FILE}")
    except FileExistsError:
        print(f"Target locked: Appending live data to {CSV_FILE}...")

    # State variables for multi-line extraction
    current_temp = None
    current_hum = None
    current_soil = None

    while True:
        try:
            if ser.in_waiting > 0:
                raw_bytes = ser.readline()
                try:
                    line = raw_bytes.decode('utf-8', errors='ignore').strip()
                except:
                    continue
                
                if not line:
                    continue

                # Extract digits matching the specific hardware firmware strings
                if 'Temperature' in line:
                    m = re.search(r'([\d\.]+)', line)
                    if m: current_temp = m.group(1)
                elif 'Humidity' in line:
                    m = re.search(r'([\d\.]+)', line)
                    if m: current_hum = m.group(1)
                elif 'Moisture' in line or 'Soil' in line:
                    m = re.search(r'([\d\.]+)', line)
                    if m: current_soil = m.group(1)
                
                # If we collected a full set of 3 variables, log the row to CSV!
                # Note: Some firmwares only emit Soil occasionally, so we fallback to 40 if missing.
                if current_temp and current_hum:
                    # Give soil a default if the arduino is just DHT
                    if current_soil is None: current_soil = "40.0" 

                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    with open(CSV_FILE, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([current_time, current_temp, current_hum, current_soil])
                    
                    print(f"[{current_time}] 🌿 SAVED -> Temp: {current_temp}C | Hum: {current_hum}% | Soil: {current_soil}%")
                    
                    # Reset accumulators for the next frame
                    current_temp = None
                    current_hum = None
                    current_soil = None
                        
        except KeyboardInterrupt:
            print("\nHardware ingestion terminated gracefully.")
            ser.close()
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(1)

if __name__ == '__main__':
    main()
