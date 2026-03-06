import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime

# Feature Mapping based on Specification
FEATURE_MAP = {
    # Electrical
    'inverters[0].pv1_voltage': 'dc_voltage_pv1',
    'inverters[0].pv1_current': 'dc_current_pv1',
    'inverters[0].pv2_voltage': 'dc_voltage_pv2',
    'inverters[0].pv2_current': 'dc_current_pv2',
    'meters[0].v_r': 'grid_voltage_r',
    'meters[0].v_y': 'grid_voltage_y',
    'meters[0].v_b': 'grid_voltage_b',
    'meters[0].freq': 'grid_frequency',
    'inverters[0].power': 'power_output_ac',
    'meters[0].pf': 'power_factor',
    
    # Thermal
    'inverters[0].temp': 'inverter_temperature',
    
    # Performance
    'inverters[0].kwh_today': 'energy_generated_today',
    'inverters[0].kwh_total': 'energy_generated_total',
    
    # Operational
    'inverters[0].alarm_code': 'fault_code',
    'inverters[0].op_state': 'op_state',
}

EXTERNAL_FEATURE_MAP = {
    'Temperature (C)': 'ambient_temperature',
    'Humidity': 'humidity',
    'Wind Speed (km/h)': 'wind_speed',
    'Pressure (millibars)': 'pressure',
    'Summary': 'weather_summary'
}

def load_telemetry_data(csv_dir, nrows=100000):
    """Load all 'Copy of' CSV files and map columns to standard names."""
    csv_dir = os.path.abspath(csv_dir)
    pattern = os.path.join(csv_dir, "Copy of *.csv")
    files = glob.glob(pattern)
    
    all_data = []
    for f in files:
        try:
            # Read telemetry CSV
            df = pd.read_csv(f, nrows=nrows)
            
            # Map columns and force numeric types
            df = df.rename(columns=FEATURE_MAP)
            for col in FEATURE_MAP.values():
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Ensure timestamp is datetime
            if 'timestampDate' in df.columns:
                df['dt'] = pd.to_datetime(df['timestampDate']).dt.tz_localize(None)
            elif 'timestamp' in df.columns:
                df['dt'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Calculate DC Power (Derived)
            df['dc_power_total'] = (df.get('dc_voltage_pv1', 0) * df.get('dc_current_pv1', 0)) + \
                                   (df.get('dc_voltage_pv2', 0) * df.get('dc_current_pv2', 0))
            
            # Extract MAC address
            mac = os.path.basename(f).replace("Copy of ", "").replace(".raws.csv", "")
            df['mac'] = mac
            all_data.append(df)
        except Exception as e:
            print(f"Error loading {f}: {e}")
            
    if not all_data:
        return pd.DataFrame()
        
    return pd.concat(all_data, ignore_index=True)

def load_weather_data(weather_file):
    """Load and map weather history data."""
    try:
        df = pd.read_csv(weather_file)
        df['dt'] = pd.to_datetime(df['Formatted Date']).dt.tz_localize(None)
        df = df.rename(columns=EXTERNAL_FEATURE_MAP)
        
        # Select mapped columns
        keep_cols = ['dt'] + list(EXTERNAL_FEATURE_MAP.values())
        return df[keep_cols]
    except Exception as e:
        print(f"Error loading weather data: {e}")
        return pd.DataFrame()

def apply_advanced_preprocessing(df, columns):
    """Implement Z-score outlier detection and scaling as per Layer 9 & 10."""
    if df.empty:
        return df, {}
    
    stats = {}
    for col in columns:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            # 1. Missing Value Flag (Layer 8)
            df[f'{col}_is_missing'] = df[col].isnull().astype(int)
            
            # 2. Outlier Detection (Z-score) (Layer 9)
            mean = df[col].mean()
            std = df[col].std()
            if std > 0:
                df[f'{col}_zscore'] = (df[col] - mean) / std
                df[f'{col}_is_outlier'] = (df[f'{col}_zscore'].abs() > 3).astype(int)
            
            # 3. Feature Scaling (Normalization) (Layer 10)
            c_min = df[col].min()
            c_max = df[col].max()
            if c_max > c_min:
                df[f'{col}_scaled'] = (df[col] - c_min) / (c_max - c_min)
            else:
                df[f'{col}_scaled'] = 0
                
            stats[col] = {'mean': mean, 'std': std, 'min': c_min, 'max': c_max}
            
    return df, stats

def apply_feature_engineering(df):
    """Implement derived features as per specification (Layer 4 & 5)."""
    if df.empty:
        return df

    # 1. Electrical Derived
    # power_ratio = ac_power / dc_power
    df['power_ratio'] = df['power_output_ac'] / df['dc_power_total'].replace(0, np.nan)
    
    # voltage_fluctuation (Rolling std of grid voltage)
    if 'grid_voltage_r' in df.columns:
        df['voltage_fluctuation'] = df['grid_voltage_r'].rolling(window=5, min_periods=1).std()

    # 2. Performance Derived
    # efficiency_drop_rate (change in power ratio)
    df['efficiency_drop_rate'] = df['power_ratio'].diff()

    # 3. Thermal Derived
    # thermal_stress_index = inverter_temp - ambient_temp
    if 'inverter_temperature' in df.columns and 'ambient_temperature' in df.columns:
        df['thermal_stress_index'] = df['inverter_temperature'] - df['ambient_temperature']
    else:
        df['thermal_stress_index'] = df['inverter_temperature'].diff()

    # Handling missing values (Forward fill strategy Layer 8)
    df = df.sort_values('dt').fillna(method='ffill').fillna(method='bfill').fillna(0)
    
    return df

def preprocess_and_merge(telemetry_df, weather_df):
    """Merge telemetry and weather data, then apply advanced processing."""
    if telemetry_df.empty:
        return pd.DataFrame()
        
    telemetry_df = telemetry_df.sort_values('dt')
    
    if not weather_df.empty:
        weather_df = weather_df.sort_values('dt')
        merged_df = pd.merge_asof(
            telemetry_df, 
            weather_df, 
            on='dt', 
            direction='nearest',
            tolerance=pd.Timedelta('1 hour')
        )
    else:
        merged_df = telemetry_df
        
    # Apply engineering
    merged_df = apply_feature_engineering(merged_df)
    
    # Apply advanced preprocessing (Scaling & Outliers)
    numeric_cols = merged_df.select_dtypes(include=[np.number]).columns.tolist()
    # Exclude flags and raw IDs from scaling/outliers
    exclude = ['dt', 'timestamp', 'mac', 'is_failed', 'target_7d', 'is_anomaly', 'fault_code', 'op_state']
    scale_cols = [c for c in numeric_cols if c not in exclude and not c.endswith('_is_missing') and not c.endswith('_is_outlier')]
    
    merged_df, stats = apply_advanced_preprocessing(merged_df, scale_cols)
    
    return merged_df

if __name__ == "__main__":
    CSV_DIR = r"d:\Aubegine\csv_files"
    WEATHER_FILE = os.path.join(CSV_DIR, "weatherHistory.csv")
    
    print("Loading telemetry...")
    telemetry = load_telemetry_data(CSV_DIR, nrows=1000)
    print("Loading weather...")
    weather = load_weather_data(WEATHER_FILE)
    
    print("Merging and Advanced Engineering...")
    merged = preprocess_and_merge(telemetry, weather)
    print(f"Final columns (sample): {merged.columns.tolist()[:20]}...")
    print(f"Z-score Check (power): {merged['power_output_ac_zscore'].head() if 'power_output_ac_zscore' in merged.columns else 'N/A'}")
