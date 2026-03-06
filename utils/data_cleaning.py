import pandas as pd
import numpy as np

def clean_data(df: pd.DataFrame, numeric_cols: list):
    """
    Industrial Data Cleaning (Layer 8, 9, 10).
    - Missing Value Flags
    - Z-Score Outlier Detection
    - Forward Fill Imputation
    """
    if df.empty:
        return df, {}

    # 1. Forward Fill Imputation (Layer 8)
    df = df.sort_values('dt').fillna(method='ffill').fillna(method='bfill').fillna(0)

    stats = {}
    for col in numeric_cols:
        if col in df.columns:
            # Missing Value Flags
            df[f'{col}_is_missing'] = df[col].isnull().astype(int)
            
            # Z-Score Outlier Detection: Z = (X - μ) / σ (Layer 10)
            mean = df[col].mean()
            std = df[col].std()
            if std > 0:
                df[f'{col}_zscore'] = (df[col] - mean) / std
                # Mark as outlier if |Z| > 3
                df[f'{col}_is_outlier'] = (df[f'{col}_zscore'].abs() > 3).astype(int)
            
            # Normalization / Scaling (Min-Max)
            c_min = df[col].min()
            c_max = df[col].max()
            if c_max > c_min:
                df[f'{col}_scaled'] = (df[col] - c_min) / (c_max - c_min)
            else:
                df[f'{col}_scaled'] = 0
                
            stats[col] = {'mean': mean, 'std': std, 'min': c_min, 'max': c_max}
            
    return df, stats
