import pandas as pd
import numpy as np

def apply_feature_engineering(df: pd.DataFrame):
    """
    Industrial Feature Engineering (Layer 4, 5).
    Derived features for thermal, electrical, and performance stress.
    """
    if df.empty:
        return df

    # 1. Electrical Derived
    # power_ratio = ac_power / dc_power
    if 'dc_power_total' in df.columns:
        df['power_ratio'] = df['power_output_ac'] / df['dc_power_total'].replace(0, np.nan)
    
    # voltage_fluctuation (Rolling std)
    if 'grid_voltage_r' in df.columns:
        df['voltage_fluctuation'] = df['grid_voltage_r'].rolling(window=10, min_periods=1).std()

    # 2. Performance Derived
    df['efficiency_trend'] = df['power_ratio'].rolling(window=50, min_periods=1).mean()
    df['power_variance'] = df['power_output_ac'].rolling(window=20, min_periods=1).var()

    # 3. Thermal Derived
    # thermal_stress_index = inverter_temp - ambient_temp
    if 'inverter_temperature' in df.columns and 'ambient_temperature' in df.columns:
        df['thermal_stress_index'] = df['inverter_temperature'] - df['ambient_temperature']
    
    # 4. Rolling Statistics
    df['rolling_mean_power'] = df['power_output_ac'].rolling(window=10, min_periods=1).mean()
    df['rolling_std_power'] = df['power_output_ac'].rolling(window=10, min_periods=1).std()

    return df.fillna(0)
