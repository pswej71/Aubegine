import pandas as pd
import numpy as np

class Predictor:
    def __init__(self, models):
        self.models = models

    def get_failure_risk_label(self, prob):
        if prob < 0.3: return "Low"
        if prob < 0.6: return "Medium"
        return "High"

    def predict(self, df: pd.DataFrame, mode: str = 'internal'):
        """
        Executes inference for the latest record.
        """
        model_set = self.models.get(mode, self.models['internal'])
        if not model_set:
            return {"error": "Model group not loaded"}

        # Get the feature columns that the model was trained on
        clf = model_set.get('failure')
        if not clf: return {"error": "Target model not found"}
        
        # Prepare inference vector (Layer 12)
        X = df[clf.feature_names_].fillna(0).tail(1)
        
        # 1. Failure Probability
        prob_7d = clf.predict_proba(X)[0][1]
        
        # 2. Power Output Prediction (Regression)
        pred_power = model_set['power'].predict(X)[0]
        
        # 3. Efficiency Prediction (Regression)
        pred_eff = model_set['efficiency'].predict(X)[0]
        
        return {
            "failure_probability_7d": round(float(prob_7d), 4),
            "risk_level_7d": self.get_failure_risk_label(prob_7d),
            "predicted_power_output": round(float(pred_power), 2),
            "predicted_efficiency": round(float(pred_eff) * 100, 2),
            "mode_used": mode
        }
