import joblib
import pandas as pd
import numpy as np

class AnomalyDetector:
    def __init__(self, model):
        self.model = model

    def detect(self, df: pd.DataFrame):
        """
        Anomaly Score Logic (Layer Anomaly 10).
        s(x) = 2^(-E(h(x))/c(n))
        """
        if not self.model:
            return {"score": 0, "is_anomaly": False}

        # Predict latest row
        X = df[self.model.feature_names_].fillna(0).tail(1)
        
        # Isolation Forest score_samples returns raw anomaly score
        # We transform to 0-1 range (1 is most anomalous)
        raw_score = self.model.score_samples(X)[0]
        anomaly_score = round(1 - (raw_score + 1) / 2, 4)
        
        return {
            "anomaly_score": anomaly_score,
            "is_anomaly": bool(anomaly_score > 0.6),
            "detected_at": pd.Timestamp.now().isoformat()
        }
