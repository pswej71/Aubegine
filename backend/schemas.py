from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TelemetryCreate(BaseModel):
    mac: str
    dc_voltage: float
    dc_current: float
    ac_voltage: float
    ac_current: float
    grid_voltage: float
    grid_frequency: Optional[float] = 50.0
    power_output_ac: float
    inverter_temperature: float
    heat_sink_temperature: Optional[float] = None
    efficiency: Optional[float] = None
    power_factor: Optional[float] = 1.0
    runtime_hours: Optional[float] = 0.0
    load_percentage: Optional[float] = 0.0
    fault_code: Optional[int] = 0
    
    # External features (can be null if internal-only mode)
    solar_irradiance: Optional[float] = None
    ambient_temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    dust_density: Optional[float] = None
    panel_soiling_index: Optional[float] = None

class Telemetry(TelemetryCreate):
    id: int
    timestamp: datetime
    is_anomaly: Optional[bool] = False
    predicted_energy: Optional[float] = None
    efficiency: Optional[float] = None

    class Config:
        from_attributes = True

class GeminiSuggestion(BaseModel):
    insight: str
    recommendation: str
    severity: str
    trend: str
