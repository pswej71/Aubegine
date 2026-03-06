import os
import pandas as pd
import numpy as np
from backend.data_loader import load_telemetry_data, load_weather_data, preprocess_and_merge
from backend.ml_service import ml_service

# Configuration
CSV_DIR = os.path.abspath("csv_files")
MODEL_DIR = os.path.abspath("backend/models")
os.makedirs(MODEL_DIR, exist_ok=True)

def train_system():
    print("--- SOLAR INVERTER AI: TRAINING INITIATED ---")
    
    # 1. Load Data (Using a sample for speed, but loading all files)
    print(f"Reading telemetry from: {CSV_DIR}...")
    # Limiting nrows per file to 50000 for local execution to prevent OOM on 450MB files
    telemetry = load_telemetry_data(CSV_DIR, nrows=50000)
    
    print("Reading weather history...")
    weather = load_weather_data(os.path.join(CSV_DIR, "weatherHistory.csv"))
    
    # 2. Preprocess & Merge
    print("Performing merging and feature engineering...")
    merged = preprocess_and_merge(telemetry, weather)
    
    # 3. Create dummy targets if not present (for initial train run)
    if 'target_7d' not in merged.columns:
        print("Generating synthetic targets for initial model warm-up...")
        # Rule-based failure target for training demonstration
        merged['target_7d'] = ((merged['power_ratio_scaled'] < 0.3) & (merged['inverter_temperature_scaled'] > 0.8)).astype(int)
    
    print(f"Final training set size: {len(merged)} rows")
    
    # 4. Train
    print("Training Regression and Classification models...")
    ml_service.train_models(merged)
    
    print("--- TRAINING COMPLETE: Models saved to backend/models ---")

if __name__ == "__main__":
    train_system()
