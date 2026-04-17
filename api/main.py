"""
api/main.py   Machine Failure Prediction REST API
Built with FastAPI for IoT edge/cloud deployment.

Run from project root:
    uvicorn api.main:app   reload   port 8000

Swagger UI   to   http://localhost:8000/docs
ReDoc        to   http://localhost:8000/redoc
"""
import os
os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import json
import sys
import threading
import time
from datetime import datetime, timezone
from typing import List, Optional

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

#  Resolve import path so we can find preprocess.py and other modules  #
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))

from preprocess import MachineFailurePreprocessor  # noqa: E402

#  Paths  #
MODELS_DIR = os.path.join(ROOT, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "model.joblib")
PREPROCESSOR_PATH = os.path.join(MODELS_DIR, "preprocessor.joblib")
METADATA_PATH = os.path.join(MODELS_DIR, "metadata.json")

#  App  #
app = FastAPI(
    title="Machine Failure Prediction API",
    description="""
## Machine Failure Prediction for IoT Deployment

Real-time predictive maintenance API.
IoT sensors stream readings -> API predicts failure probability -> Alert if risk is HIGH.

### Workflow
```
[Sensor/IoT Device] -> POST /predict -> [ML Model] -> { prediction, probability, risk_level }
```

### Features
- **< 5ms inference** per sensor reading
- **Batch endpoint** for IoT gateways
- **Risk categorisation**: LOW / MEDIUM / HIGH
- **Docker-ready** for edge or cloud deployment
    """,
    version="1.0.0",
    contact={
        "name": "Felix Hardyan",
        "url": "https://github.com/felixhardyan",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  Global model state  #
_state: dict = {
    "model": None,
    "preprocessor": None,
    "metadata": None,
    "loaded_at": None,
}


@app.on_event("startup")
async def _load_model():
    try:
        _state["model"] = joblib.load(MODEL_PATH)
        _state["preprocessor"] = joblib.load(PREPROCESSOR_PATH)
        with open(METADATA_PATH, encoding="utf-8") as f:
            _state["metadata"] = json.load(f)
        _state["loaded_at"] = datetime.now(timezone.utc).isoformat()
        print("OK Model loaded and ready.")
        
        # Start MQTT Subscriber
        _start_mqtt_client()
    except FileNotFoundError:
        print(
            "[WARN] Model files not found -- run `python train.py` first.\n"
            "       API will start but /predict will return 503."
        )


#  MQTT Integrated Ingestion  #

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = "factory/machine/telemetry"

def _on_mqtt_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        # Convert dict to SensorReading model
        reading = SensorReading(**payload)
        
        # Run inference
        result = _run_inference(reading)
        
        # Log to console (in a real app, this would go to a DB or Alert system)
        print(f" [MQTT] {result.device_id}: {result.risk_level} risk ({result.failure_probability*100:.1f}%)")
        
        # Optionally publish alerts back to MQTT
        if result.risk_level == "HIGH":
            client.publish("factory/alerts", json.dumps(result.model_dump()))
            
    except Exception as e:
        print(f" [MQTT ERR] Failed to process message: {e}")

def _start_mqtt_client():
    # paho-mqtt 2.0+ requires an explicit CallbackAPIVersion
    client = mqtt.Client(CallbackAPIVersion.VERSION2, "Predictive-Maintenance-API")
    client.on_message = _on_mqtt_message
    
    try:
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.subscribe(MQTT_TOPIC)
        # Run the MQTT loop in a background thread to not block FastAPI
        mqtt_thread = threading.Thread(target=client.loop_forever, daemon=True)
        mqtt_thread.start()
        print(f"OK MQTT Subscriber started on topic: {MQTT_TOPIC}")
    except Exception as e:
        print(f" [WARN] MQTT could not connect: {e}")

#  Schemas  #

class SensorReading(BaseModel):
    """Single IoT sensor reading."""

    type: str = Field(..., description="Machine quality: L | M | H", examples=["M"])
    air_temperature_K: float = Field(
        ..., description="Ambient air temperature (Kelvin)", examples=[298.1]
    )
    process_temperature_K: float = Field(
        ..., description="Process temperature (Kelvin)", examples=[308.6]
    )
    rotational_speed_rpm: float = Field(
        ..., description="Spindle rotational speed (RPM)", examples=[1551.0]
    )
    torque_Nm: float = Field(
        ..., description="Applied torque (Newton-metres)", examples=[42.8]
    )
    tool_wear_min: float = Field(
        ..., description="Cumulative tool wear (minutes)", examples=[100.0]
    )
    device_id: Optional[str] = Field(
        None, description="Optional IoT device identifier", examples=["sensor-001"]
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "M",
                "air_temperature_K": 298.1,
                "process_temperature_K": 308.6,
                "rotational_speed_rpm": 1551.0,
                "torque_Nm": 42.8,
                "tool_wear_min": 100.0,
                "device_id": "sensor-001",
            }
        }
    }


class PredictionResult(BaseModel):
    device_id: Optional[str]
    prediction: int = Field(..., description="0 = No Failure | 1 = Failure")
    label: str = Field(..., description="Human-readable prediction label")
    failure_probability: float = Field(
        ..., description="Probability of failure [0.0 - 1.0]"
    )
    risk_level: str = Field(..., description="LOW | MEDIUM | HIGH")
    timestamp: str
    inference_time_ms: float


class BatchRequest(BaseModel):
    readings: List[SensorReading] = Field(..., min_length=1, max_length=500)


class BatchResult(BaseModel):
    total: int
    failures_detected: int
    high_risk_count: int
    results: List[PredictionResult]


#  Helpers  #

def _risk_level(prob: float) -> str:
    if prob < 0.30:
        return "LOW"
    elif prob < 0.70:
        return "MEDIUM"
    return "HIGH"


def _run_inference(reading: SensorReading) -> PredictionResult:
    model = _state["model"]
    preprocessor = _state["preprocessor"]

    if model is None or preprocessor is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Run `python train.py` to train the model first.",
        )

    t0 = time.perf_counter()

    input_dict = {
        "type": reading.type,
        "air_temperature_K": reading.air_temperature_K,
        "process_temperature_K": reading.process_temperature_K,
        "rotational_speed_rpm": reading.rotational_speed_rpm,
        "torque_Nm": reading.torque_Nm,
        "tool_wear_min": reading.tool_wear_min,
    }
    X = preprocessor.transform(input_dict)
    pred = int(model.predict(X)[0])
    prob = float(model.predict_proba(X)[0][1])

    elapsed_ms = (time.perf_counter() - t0) * 1_000

    return PredictionResult(
        device_id=reading.device_id,
        prediction=pred,
        label="FAILURE" if pred == 1 else "NO FAILURE",
        failure_probability=round(prob, 6),
        risk_level=_risk_level(prob),
        timestamp=datetime.now(timezone.utc).isoformat(),
        inference_time_ms=round(elapsed_ms, 3),
    )


#  Routes  #

@app.get("/", tags=["General"], summary="API root")
async def root():
    return {
        "name": "Machine Failure Prediction API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["General"], summary="Health check for monitoring/k8s probes")
async def health():
    model_ready = _state["model"] is not None
    return {
        "status": "healthy" if model_ready else "degraded",
        "model_loaded": model_ready,
        "loaded_at": _state["loaded_at"],
        "server_time": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/model/info", tags=["Model"], summary="Model performance & feature info")
async def model_info():
    meta = _state["metadata"]
    if meta is None:
        raise HTTPException(status_code=404, detail="Model metadata not available.")
    return {
        "model_type": meta.get("model_type"),
        "performance": {
            "accuracy": meta.get("accuracy"),
            "roc_auc": meta.get("roc_auc"),
        },
        "training_samples": meta.get("training_samples"),
        "features": meta.get("feature_columns"),
        "top_features": dict(
            list(meta.get("feature_importances", {}).items())[:5]
        ),
    }


@app.post(
    "/predict",
    response_model=PredictionResult,
    tags=["Prediction"],
    summary="Predict failure from a single IoT sensor reading",
)
async def predict(reading: SensorReading):
    """
    Send one sensor reading and get a real time failure prediction.

    Typical IoT usage: each device POSTs on a fixed interval (e.g. every 5 s).
    """
    return _run_inference(reading)


@app.post(
    "/predict/batch",
    response_model=BatchResult,
    tags=["Prediction"],
    summary="Batch predict for IoT gateways (up to 500 readings)",
)
async def predict_batch(batch: BatchRequest):
    """
    Send multiple sensor readings in one request.
    Useful when an IoT gateway aggregates data from many devices before
    forwarding to the cloud.
    """
    results = [_run_inference(r) for r in batch.readings]
    failures = [r for r in results if r.prediction == 1]
    high_risk = [r for r in results if r.risk_level == "HIGH"]

    return BatchResult(
        total=len(results),
        failures_detected=len(failures),
        high_risk_count=len(high_risk),
        results=results,
    )
