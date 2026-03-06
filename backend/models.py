from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class InverterData(Base):
    __tablename__ = "inverter_data"
    id = Column(Integer, primary_key=True, index=True)
    mac = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    dc_voltage = Column(Float)
    dc_current = Column(Float)
    ac_voltage = Column(Float)
    ac_current = Column(Float)
    grid_voltage = Column(Float)
    power_output = Column(Float)
    temperature = Column(Float)
    load_percentage = Column(Float)
    fault_code = Column(Integer)
    runtime_hours = Column(Float)

class EnvironmentData(Base):
    __tablename__ = "environment_data"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    solar_irradiance = Column(Float)
    ambient_temperature = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    dust_density = Column(Float)
    air_quality_index = Column(Float)

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    mac = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    predicted_power = Column(Float)
    predicted_efficiency = Column(Float)
    failure_probability = Column(Float)
    risk_level = Column(String) # Low, Medium, High
    model_type = Column(String) # Internal, Combined

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    mac = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    type = Column(String) # Anomaly, Failure Risk, Technical
    message = Column(String)
    severity = Column(String) # Normal, Warning, Critical

class AnomalyLog(Base):
    __tablename__ = "anomaly_logs"
    id = Column(Integer, primary_key=True, index=True)
    mac = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    anomaly_score = Column(Float)
    feature_impact = Column(String) # JSON string of high-impact features
