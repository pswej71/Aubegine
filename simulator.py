import pandas as pd
import requests
import time
import glob
import os

API_URL = "http://localhost:8000/api/inverter/telemetry"
CSV_DIR = "csv_files"

FEATURE_MAP = {
    'inverters[0].pv1_voltage': 'dc_voltage', 'inverters[0].pv1_current': 'dc_current',
    'inverters[0].pv2_voltage': 'dc_voltage_pv2', 'inverters[0].pv2_current': 'dc_current_pv2',
    'meters[0].v_r': 'grid_voltage', 'inverters[0].power': 'power_output_ac',
    'inverters[0].temp': 'inverter_temperature'
}

def simulate():
    print("--- INGESTION SIMULATOR STARTING ---")
    files = glob.glob(os.path.join(CSV_DIR, "Copy of *.csv"))
    if not files:
        print("No CSV files found in csv_files/")
        return

    for f in files:
        mac = os.path.basename(f).replace("Copy of ", "").replace(".raws.csv", "")
        print(f"Feeding data for MAC: {mac}...")
        df = pd.read_csv(f, nrows=100) # Feed first 100 rows for demo
        df = df.rename(columns=FEATURE_MAP)
        
        for _, row in df.iterrows():
            payload = {
                "mac": mac,
                "dc_voltage": float(row.get('dc_voltage', 0)),
                "dc_current": float(row.get('dc_current', 0)),
                "ac_voltage": float(row.get('ac_voltage', 230)),
                "ac_current": float(row.get('ac_current', 10)),
                "grid_voltage": float(row.get('grid_voltage', 230)),
                "power_output_ac": float(row.get('power_output_ac', 0)),
                "inverter_temperature": float(row.get('inverter_temperature', 40))
            }
            try:
                requests.post(API_URL, json=payload)
                print(".", end="", flush=True)
            except Exception as e:
                print(f"Error: {e}")
            time.sleep(1) # 1s delay per point
        print(f"\nFinished {mac}")

if __name__ == "__main__":
    simulate()
