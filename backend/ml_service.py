import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, IsolationForest
from sklearn.metrics import mean_squared_error, r2_score
from datetime import timedelta

MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
os.makedirs(MODEL_DIR, exist_ok=True)

class SolarInverterML:
    def __init__(self):
        self.internal_features = [
            'dc_voltage_pv1_scaled', 'dc_current_pv1_scaled', 'dc_voltage_pv2_scaled', 'dc_current_pv2_scaled',
            'grid_voltage_r_scaled', 'grid_voltage_y_scaled', 'grid_voltage_b_scaled', 'grid_frequency_scaled',
            'power_output_ac_scaled', 'power_factor_scaled', 'inverter_temperature_scaled',
            'energy_generated_today_scaled', 'dc_power_total_scaled', 'power_ratio_scaled',
            'voltage_fluctuation_scaled', 'efficiency_drop_rate_scaled', 'thermal_stress_index_scaled',
            # Diagnostic Flags (Layer 7 & Phase 6)
            'dc_voltage_pv1_is_missing', 'dc_current_pv1_is_missing', 'power_output_ac_is_missing',
            'inverter_temperature_is_missing', 'grid_voltage_r_is_missing'
        ]
        self.external_features = [
            'ambient_temperature_scaled', 'humidity_scaled', 'wind_speed_scaled', 'pressure_scaled',
            'ambient_temperature_is_missing', 'humidity_is_missing'
        ]
        
        # Classification Models (next 7 days)
        self.clf_a = None # Internal only
        self.clf_b = None # Combined
        
        # Regression Models (Power & Efficiency)
        self.reg_power_a = None
        self.reg_power_b = None
        self.reg_eff_a = None
        self.reg_eff_b = None
        
        # Anomaly Detection
        self.anomaly_detector = None
        
        self.load_models()

    def load_models(self):
        """Load persistent models."""
        try:
            self.clf_a = joblib.load(os.path.join(MODEL_DIR, 'clf_a.joblib'))
            self.clf_b = joblib.load(os.path.join(MODEL_DIR, 'clf_b.joblib'))
            self.reg_power_a = joblib.load(os.path.join(MODEL_DIR, 'reg_power_a.joblib'))
            self.reg_power_b = joblib.load(os.path.join(MODEL_DIR, 'reg_power_b.joblib'))
            self.reg_eff_a = joblib.load(os.path.join(MODEL_DIR, 'reg_eff_a.joblib'))
            self.reg_eff_b = joblib.load(os.path.join(MODEL_DIR, 'reg_eff_b.joblib'))
            self.anomaly_detector = joblib.load(os.path.join(MODEL_DIR, 'anomaly_detector.joblib'))
        except:
            print("Models not found, training required.")

    def calculate_failure_risk(self, prob):
        """Map probability to risk levels."""
        if prob < 0.3: return "Low"
        if prob < 0.6: return "Medium"
        return "High"

    def detect_rule_based_safety(self, row):
        """Rule-based safety detection as per Layer Rule 13."""
        alerts = []
        if row.get('inverter_temperature', 0) > 85:
            alerts.append("Overheating Alert: Inverter temperature > 85°C")
        if row.get('power_output_ac', 0) == 0 and row.get('ambient_temperature', 0) > 10:
            alerts.append("Inverter Fault: No power output detected during daytime")
        if abs(row.get('voltage_fluctuation', 0)) > 10:
            alerts.append("Grid Instability: High voltage fluctuation detected")
        return alerts

    def train_models(self, df):
        """Train classifier and regressors for internal (A) and combined (B) modes."""
        if df.empty: return False
        
        df = df.sort_values('dt')
        df['is_failed'] = ((df['fault_code'] > 0) | (df['op_state'] != 0)).astype(int)
        df['target_7d'] = df['is_failed'].rolling(window=5040, min_periods=1).max().shift(-5040).fillna(0)
        
        # Internal Features
        available_internal = [f for f in self.internal_features if f in df.columns]
        X_internal = df[available_internal].fillna(0)
        
        # Combined Features
        available_combined = available_internal + [f for f in self.external_features if f in df.columns]
        X_combined = df[available_combined].fillna(0)
        
        targets = {
            'fail': df['target_7d'],
            'power': df['power_output_ac'],
            'eff': df['power_ratio']
        }
        
        # Training Pipeline Helpers
        def train_and_save(X, y, name, task_type='clf'):
            if task_type == 'clf':
                model = RandomForestClassifier(n_estimators=100, random_state=42)
            else:
                model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            # Evaluate (Layer 15)
            preds = model.predict(X)
            mse = mean_squared_error(y, preds)
            r2 = r2_score(y, preds)
            print(f"Model {name} trained. MSE: {mse:.4f}, R2: {r2:.4f}")
            
            model.feature_names_ = X.columns.tolist()
            joblib.dump(model, os.path.join(MODEL_DIR, f"{name}.joblib"))
            return model

        print("Training Internal Mode (A)...")
        self.clf_a = train_and_save(X_internal, targets['fail'], 'clf_a', 'clf')
        self.reg_power_a = train_and_save(X_internal, targets['power'], 'reg_power_a', 'reg')
        self.reg_eff_a = train_and_save(X_internal, targets['eff'], 'reg_eff_a', 'reg')
        
        print("Training Combined Mode (B)...")
        self.clf_b = train_and_save(X_combined, targets['fail'], 'clf_b', 'clf')
        self.reg_power_b = train_and_save(X_combined, targets['power'], 'reg_power_b', 'reg')
        self.reg_eff_b = train_and_save(X_combined, targets['eff'], 'reg_eff_b', 'reg')
        
        # Anomaly Detection
        self.anomaly_detector = IsolationForest(contamination=0.05, random_state=42)
        self.anomaly_detector.fit(X_internal)
        joblib.dump(self.anomaly_detector, os.path.join(MODEL_DIR, 'anomaly_detector.joblib'))
        
        return True

    def predict(self, df, mode='internal'):
        """Predict failures and performance metrics."""
        # Selector (Layer 9)
        if mode == 'combined' and self.clf_b is not None:
            clf, reg_power, reg_eff = self.clf_b, self.reg_power_b, self.reg_eff_b
        else:
            clf, reg_power, reg_eff = self.clf_a, self.reg_power_a, self.reg_eff_a
            
        if clf is None:
            return {"error": f"Model {mode} not trained."}
            
        X = df[clf.feature_names_].fillna(0).tail(1)
        latest_row = df.tail(1).to_dict('records')[0]
        
        # Predictions
        prob_7d = clf.predict_proba(X)[0][1]
        pred_power = reg_power.predict(X)[0]
        pred_eff = reg_eff.predict(X)[0]
        
        results = {
            "failure_probability_7d": round(float(prob_7d), 4),
            "risk_level_7d": self.calculate_failure_risk(prob_7d),
            "predicted_power_output": round(float(pred_power), 2),
            "predicted_efficiency": round(float(pred_eff) * 100, 2), # Percentage
            "safety_alerts": self.detect_rule_based_safety(latest_row)
        }
        
        # Anomaly Detection (Always uses internal features as baseline)
        if self.anomaly_detector:
            X_internal = df[self.internal_features].fillna(0).tail(1)
            score = self.anomaly_detector.score_samples(X_internal)[0]
            results['anomaly_score'] = round(1 - (score + 1) / 2, 4)
            results['is_anomaly'] = bool(results['anomaly_score'] > 0.6)
            
        return results

ml_service = SolarInverterML()
