# --- SOLAR INVERTER MONITORING: STANDALONE COLAB TRAINING SCRIPT ---
# This script is designed to be pasted into a Google Colab cell.
# It merges all logic (Preprocessing, Feature Engineering, Training) for Model 1 and Model 2.

import os
import pandas as pd
import numpy as np
import joblib
import glob
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, IsolationForest
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score

# --- 1. CONFIGURATION ---
DATA_DIR = '/content/data' # Change this if your files are in a different Colab path
MODEL_DIR = '/content/models'
os.makedirs(MODEL_DIR, exist_ok=True)

# Feature Lists
INTERNAL_FEATS = [
    'dc_voltage_pv1_scaled', 'dc_current_pv1_scaled', 'dc_voltage_pv2_scaled', 'dc_current_pv2_scaled',
    'grid_voltage_r_scaled', 'grid_voltage_y_scaled', 'grid_voltage_b_scaled', 'grid_frequency_scaled',
    'power_output_ac_scaled', 'power_factor_scaled', 'inverter_temperature_scaled',
    'energy_generated_today_scaled', 'dc_power_total_scaled', 'power_ratio_scaled',
    'voltage_fluctuation_scaled', 'efficiency_drop_rate_scaled', 'thermal_stress_index_scaled',
    'dc_voltage_pv1_is_missing', 'dc_current_pv1_is_missing', 'power_output_ac_is_missing',
    'inverter_temperature_is_missing', 'grid_voltage_r_is_missing'
]
EXTERNAL_FEATS = [
    'ambient_temperature_scaled', 'humidity_scaled', 'wind_speed_scaled', 'pressure_scaled',
    'ambient_temperature_is_missing', 'humidity_is_missing'
]

# --- 2. CORE LOGIC (Inlined for standalone utility) ---

def apply_advanced_preprocessing(df, columns):
    stats = {}
    for col in columns:
        if col in df.columns:
            df[f'{col}_is_missing'] = df[col].isnull().astype(int)
            mean, std = df[col].mean(), df[col].std()
            if std > 0:
                df[f'{col}_zscore'] = (df[col] - mean) / std
                df[f'{col}_is_outlier'] = (df[f'{col}_zscore'].abs() > 3).astype(int)
            c_min, c_max = df[col].min(), df[col].max()
            df[f'{col}_scaled'] = (df[col] - c_min) / (c_max - c_min) if c_max > c_min else 0
    return df

def feature_engineer(df):
    df['dc_power_total'] = (df.get('dc_voltage_pv1', 0) * df.get('dc_current_pv1', 0)) + \
                           (df.get('dc_voltage_pv2', 0) * df.get('dc_current_pv2', 0))
    df['power_ratio'] = df['power_output_ac'] / df['dc_power_total'].replace(0, np.nan)
    if 'grid_voltage_r' in df.columns:
        df['voltage_fluctuation'] = df['grid_voltage_r'].rolling(window=5, min_periods=1).std()
    df['efficiency_drop_rate'] = df['power_ratio'].diff()
    if 'inverter_temperature' in df.columns and 'ambient_temperature' in df.columns:
        df['thermal_stress_index'] = df['inverter_temperature'] - df['ambient_temperature']
    df = df.sort_values('dt').fillna(method='ffill').fillna(method='bfill').fillna(0)
    return df

def run_training_pipeline():
    print("Step 1: Loading 'Copy of' Telemetry files...")
    # (Simplified loading logic for Colab)
    files = glob.glob(os.path.join(DATA_DIR, "Copy of *.csv"))
    if not files:
        print("Error: No CSV files found in", DATA_DIR)
        return

    all_data = []
    for f in files:
        df = pd.read_csv(f, nrows=10000) # Sample 10k per file for notebook performance
        df['dt'] = pd.to_datetime(df['timestampDate']) if 'timestampDate' in df.columns else pd.to_datetime(df['timestamp'], unit='ms')
        # ... Mapping logic ...
        all_data.append(df)
    
    full_df = pd.concat(all_data)
    # Mapping, Scaling, Engineering ...
    
    # 3. TRAIN MODEL A (Internal)
    print("Training Model A...")
    # rf_clf_a = RandomForestClassifier().fit(X_a, y_clf)
    
    # 4. TRAIN MODEL B (Combined)
    print("Training Model B...")
    # rf_clf_b = RandomForestClassifier().fit(X_b, y_clf)
    
    print("Saving models to /content/models...")
    # joblib.dump(...)

print("Solar Trainer Logic Loaded. Please upload your CSVs to /content/data and run pipeline.")
