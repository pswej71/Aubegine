import os
import joblib

MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))

def load_brain_models():
    """
    Unified model loader.
    Supports Failure, Power, Efficiency models for Internal and Combined modes.
    """
    models = {
        'internal': {},
        'combined': {},
        'anomaly': None
    }
    
    try:
        models['internal']['failure'] = joblib.load(os.path.join(MODEL_DIR, 'failure_model_internal.joblib'))
        models['combined']['failure'] = joblib.load(os.path.join(MODEL_DIR, 'failure_model_combined.joblib'))
        
        models['internal']['power'] = joblib.load(os.path.join(MODEL_DIR, 'power_model_internal.joblib'))
        models['combined']['power'] = joblib.load(os.path.join(MODEL_DIR, 'power_model_combined.joblib'))
        
        models['internal']['efficiency'] = joblib.load(os.path.join(MODEL_DIR, 'efficiency_model_internal.joblib'))
        models['combined']['efficiency'] = joblib.load(os.path.join(MODEL_DIR, 'efficiency_model_combined.joblib'))
        
        models['anomaly'] = joblib.load(os.path.join(MODEL_DIR, 'anomaly_model.joblib'))
        print("Models loaded successfully.")
    except Exception as e:
        print(f"Loading Error: {e}")
        
    return models
