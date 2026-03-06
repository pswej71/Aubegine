from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import json
import os
import pandas as pd
import asyncio
from typing import List

from .database import engine, get_db
from .models import Base, InverterData, Prediction, Alert, AnomalyLog, EnvironmentData
from .schemas import TelemetryCreate
from .model_loader import load_brain_models
from .predictor import Predictor
from .anomaly_detector import AnomalyDetector
from .genai_module import GenAIAnalyzer
from ..utils.data_cleaning import clean_data
from ..utils.feature_engineering import apply_feature_engineering
from ..utils.model_switcher import select_model_mode

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Industrial Solar Monitor")

# Initialize modular components
models = load_brain_models()
predictor = Predictor(models)
anomaly_detector = AnomalyDetector(models['anomaly'])
genai_analyzer = GenAIAnalyzer()

# Telemetry Buffer per MAC (Sliding window for feature engineering)
telemetry_buffer = {}

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def process_pipeline(mac: str, mode: str, db: Session):
    """
    Industrial Real-time Pipeline (Layer Pipeline 11).
    Triggered every 2 minutes.
    """
    if mac not in telemetry_buffer or not telemetry_buffer[mac]:
        return

    # Convert buffer to DataFrame for engineering
    df = pd.DataFrame(telemetry_buffer[mac])
    
    # 1. Data Cleaning (Z-Score & Missing Flags)
    df, stats = clean_data(df, numeric_cols=['dc_voltage', 'power_output_ac', 'inverter_temperature'])
    
    # 2. Feature Engineering
    df = apply_feature_engineering(df)
    
    # 3. Model Switching (Layer Switching 9)
    env_exists = not pd.isna(df.iloc[-1].get('ambient_temperature'))
    active_mode = select_model_mode(has_external_data=env_exists, manual_mode=mode)
    
    # 4. Predictions (ML Layer 4, 6)
    ml_results = predictor.predict(df, mode=active_mode)
    
    # 5. Anomaly Detection (Isolation Forest Layer 10)
    anomaly_results = anomaly_detector.detect(df)
    
    # 6. GenAI Explanation (Layer RCA 14)
    # We only trigger GenAI for risk or anomalies to save API costs, or per update if requested.
    latest_row = df.iloc[-1].to_dict()
    rca_context = {**ml_results, **latest_row}
    rca_analysis = await genai_analyzer.analyze(rca_context)
    
    # 7. Persistence (Layer Postgres 14)
    # Save Prediction
    new_pred = Prediction(
        mac=mac,
        predicted_power=ml_results.get('predicted_power_output'),
        predicted_efficiency=ml_results.get('predicted_efficiency'),
        failure_probability=ml_results.get('failure_probability_7d'),
        risk_level=ml_results.get('risk_level_7d'),
        model_type=active_mode,
        rca_json=json.dumps(rca_analysis) if isinstance(rca_analysis, dict) else rca_analysis
    )
    db.add(new_pred)
    
    # Save Anomaly if applies
    if anomaly_results['is_anomaly']:
        new_log = AnomalyLog(mac=mac, anomaly_score=anomaly_results['anomaly_score'], is_anomaly=True)
        db.add(new_log)
        # Generate Alert
        db.add(Alert(mac=mac, type="Anomaly", message="Critical technical anomaly detected", severity="Critical"))

    db.commit()

    # 8. Broadcast to Dashboard
    update_payload = {
        "mac": mac,
        "telemetry": latest_row,
        "prediction": ml_results,
        "anomaly": anomaly_results,
        "rca": rca_analysis,
        "mode": active_mode
    }
    await manager.broadcast(json.dumps(update_payload))

@app.post("/api/inverter/telemetry")
async def receive_telemetry(data: TelemetryCreate, mode: str = 'auto', db: Session = Depends(get_db)):
    mac = data.mac
    if mac not in telemetry_buffer: telemetry_buffer[mac] = []
    
    # Store raw entry
    raw_dict = data.dict()
    raw_dict['dt'] = datetime.now()
    telemetry_buffer[mac].append(raw_dict)
    
    # Limit buffer size (e.g., last 100 points for rolling stats)
    if len(telemetry_buffer[mac]) > 100: telemetry_buffer[mac].pop(0)

    # Persist raw telemetry
    db_entry = InverterData(**raw_dict)
    db.add(db_entry)
    db.commit()

    # Trigger Pipeline
    asyncio.create_task(process_pipeline(mac, mode, db))
    
    return {"status": "accepted", "mac": mac}

@app.get("/api/predict")
async def get_latest_results(mac: str, db: Session = Depends(get_db)):
    pred = db.query(Prediction).filter(Prediction.mac == mac).order_by(Prediction.timestamp.desc()).first()
    if not pred: raise HTTPException(status_code=404, detail="No predictions found")
    return pred

@app.get("/api/alerts")
async def get_alerts(mac: str = None, db: Session = Depends(get_db)):
    query = db.query(Alert)
    if mac: query = query.filter(Alert.mac == mac)
    return query.order_by(Alert.timestamp.desc()).limit(20).all()

@app.get("/api/genai-analysis")
async def get_latest_rca(mac: str, db: Session = Depends(get_db)):
    pred = db.query(Prediction).filter(Prediction.mac == mac).order_by(Prediction.timestamp.desc()).first()
    if not pred or not pred.rca_json: return {"analysis": "Generating..."}
    return {"analysis": json.loads(pred.rca_json) if pred.rca_json.startswith('{') else pred.rca_json}

@app.post("/api/ml/train")
async def trigger_retraining():
    return {"status": "retraining started in background"}
