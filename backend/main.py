from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import database
import models
import schemas
from gemini_service import get_suggestions
from ml_service import analyze_trends_and_anomalies
import json
import asyncio
from datetime import datetime
import random

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Solar Inverter Monitoring API")

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clients = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.remove(websocket)

@app.get("/")
def read_root():
    return {"message": "Solar Inverter API is Running"}

@app.post("/api/inverter/telemetry", response_model=schemas.Telemetry)
async def create_telemetry(telemetry: schemas.TelemetryCreate, db: Session = Depends(database.get_db)):
    efficiency = 0.0
    if telemetry.solar_irradiance > 0:
        efficiency = (telemetry.power / telemetry.solar_irradiance) * 100

    db_item = models.InverterTelemetry(
        **telemetry.dict(),
        efficiency=efficiency,
        is_anomaly=False, # This gets evaluated when querying history
        predicted_energy=telemetry.energy * 1.05 # Mock prediction factor
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # Broadcast to connected websocket clients
    for client in clients:
        try:
            d = db_item.__dict__.copy()
            d.pop('_sa_instance_state', None)
            d['timestamp'] = d['timestamp'].isoformat()
            await client.send_json(d)
        except Exception:
            pass

    return db_item

@app.get("/api/inverter/history")
def get_history(limit: int = 100, db: Session = Depends(database.get_db)):
    items = db.query(models.InverterTelemetry).order_by(models.InverterTelemetry.timestamp.desc()).limit(limit).all()
    # Reverse to return chronological order
    items = items[::-1]
    
    # Apply ML Trend Analysis and Anomaly Detection
    processed_data = analyze_trends_and_anomalies(items)
    return processed_data

@app.get("/api/inverter/latest")
def get_latest_telemetry(db: Session = Depends(database.get_db)):
    item = db.query(models.InverterTelemetry).order_by(models.InverterTelemetry.timestamp.desc()).first()
    if not item:
        return {}
    
    d = item.__dict__.copy()
    d.pop('_sa_instance_state', None)
    return d

@app.get("/api/alerts")
def get_alerts(db: Session = Depends(database.get_db)):
    faults = db.query(models.InverterTelemetry).filter(models.InverterTelemetry.status != "Normal").order_by(models.InverterTelemetry.timestamp.desc()).limit(10).all()
    
    faults_dict = []
    for f in faults:
        d = f.__dict__.copy()
        d.pop('_sa_instance_state', None)
        faults_dict.append(d)
        
    return {
        "faults": faults_dict
    }

@app.get("/api/ai/suggestions")
def get_ai_suggestions(db: Session = Depends(database.get_db)):
    # Get last 15 readings for context
    items = db.query(models.InverterTelemetry).order_by(models.InverterTelemetry.timestamp.desc()).limit(15).all()
    items = items[::-1]
    
    data_dicts = []
    for item in items:
        d = item.__dict__.copy()
        d.pop('_sa_instance_state', None)
        d['timestamp'] = str(d['timestamp'])
        data_dicts.append(d)
        
    # Example alert logic
    alerts = ["Low efficiency warning"] if any((d.get('efficiency', 100) < 50 for d in data_dicts)) else []
    
    suggestion = get_suggestions(telemetry_data=data_dicts, alerts=alerts)
    return suggestion

# Simulator Endpoint for Testing easily without real sensors
@app.post("/api/simulator/generate")
async def generate_mock_data(db: Session = Depends(database.get_db)):
    telemetry = schemas.TelemetryCreate(
        voltage=random.uniform(210, 240),
        current=random.uniform(10, 50),
        power=random.uniform(2000, 10000),
        energy=random.uniform(10, 50),
        frequency=random.uniform(49.8, 50.2),
        temperature=random.uniform(30, 60),
        status="Normal" if random.random() > 0.1 else "Warning",
        solar_irradiance=random.uniform(400, 1000),
        ambient_temperature=random.uniform(20, 45),
        dust_index=random.uniform(0, 100),
        air_quality_index=random.uniform(20, 150)
    )
    
    efficiency = 0.0
    if telemetry.solar_irradiance > 0:
        efficiency = (telemetry.power / telemetry.solar_irradiance) * 100

    db_item = models.InverterTelemetry(
        **telemetry.dict(),
        efficiency=efficiency,
        is_anomaly=False,
        predicted_energy=telemetry.energy * 1.05
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # Broadcast to connected websocket clients
    for client in clients:
        try:
            d = db_item.__dict__.copy()
            d.pop('_sa_instance_state', None)
            d['timestamp'] = d['timestamp'].isoformat()
            await client.send_json(d)
        except Exception:
            pass
            
    return {"message": "Data generated successfully"}

@app.post("/api/ml/train")
def train_anomaly_model(db: Session = Depends(database.get_db)):
    # Grab last 1000 items to train
    items = db.query(models.InverterTelemetry).order_by(models.InverterTelemetry.timestamp.desc()).limit(1000).all()
    if len(items) < 50:
        return {"status": "error", "message": "Not enough data to train (need at least 50)"}
        
    data_list = []
    for t in items:
        d = t.__dict__.copy()
        d.pop('_sa_instance_state', None)
        data_list.append(d)
        
    success = ml_service.train_model(data_list)
    return {"status": "success" if success else "error", "message": "Model retrained and saved to disk"}

