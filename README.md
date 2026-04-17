# 🏭 IIoT Predictive Maintenance System
### End-to-End ML Ops for Industrial Machine Failure Prediction

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![MQTT](https://img.shields.io/badge/MQTT-3C3F41?style=for-the-badge&logo=mqtt)](https://mqtt.org/)
[![Modbus](https://img.shields.io/badge/Modbus_TCP-FF6600?style=for-the-badge&logo=industrial-software)](https://modbus.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

This project is a professional-grade **Industrial IoT (IIoT) Predictive Maintenance** system. It transitions a static dataset into a live industrial environment, simulating a full automation stack from **PLC registers to Real-time ML Inference**.

---

## 🏗️ System Architecture (Industry 4.0)

This project implements a multi-layer "Edge-to-Cloud" architecture, reflecting modern Smart Factory standards:

```mermaid
graph TD
    subgraph Field_Level [Field Level - Physical Machine]
        M1[Mechanical Components] --> PLC[Modbus PLC Emulator]
    end
    
    subgraph Edge_Level [Edge Computing - IIoT Gateway]
        PLC -- Polls Registers -- GW[Industrial Gateway]
        GW -- Publishes JSON -- Broker[MQTT Mosquitto Broker]
    end
    
    subgraph Cloud_Level [AI Analytics - ML Service]
        Broker -- Real-time Stream -- API[FastAPI Inference Engine]
        API -- XGBoost -- Pred[Failure Prediction]
        API -- High Risk -- Alert[MQTT Alerts / Alerts Service]
    end
```

### 🛠️ Technology Stack
*   **Machine Learning**: **XGBoost (Extreme Gradient Boosting)**, native class weighting, custom OOP Preprocessors.
*   **Industrial Connectivity**: **Modbus TCP** (PLC level), **MQTT** (IIoT Messaging).
*   **Backend & API**: **FastAPI** (Uvicorn), Pydantic for data validation.
*   **Infrastructure**: **Docker** & Docker Compose for orchestration.

---

## 📂 Project Structure

```text
Machine_Failure_Classification/
├── industrial_iot/
│   ├── plc_emulator.py    # Local PLC Simulation (Modbus TCP Server)
│   └── gateway.py         # IIoT Gateway (Modbus Client -> MQTT Publisher)
├── api/
│   └── main.py            # Inference Service (FastAPI + MQTT Subscriber)
├── src/
│   ├── preprocess.py      # Feature Engineering & Scaling
│   ├── train.py           # ML Training Pipeline
│   └── predict.py         # Batch Prediction Scripts
├── models/                # Serialised ML Artefacts (.joblib)
├── docker-compose.yml     # Full Stack Orchestration
└── requirements.txt       # Core Dependencies
```

---

## 🚀 Quick Start Guide

### 1. Model Preparation
Initialize the Machine Learning algorithms by executing the core training sequence. This populates the `models/` directory with production-ready artefacts.
```bash
pip install -r requirements.txt
python src/train.py
```

### 2. Full Stack Deployment (Recommended)
Deploy the entire IIoT environment (Broker, PLC, Gateway, and API) using Docker:
```bash
docker compose --profile simulation up --build
```

### 3. Manual Interface
Once deployed, you can interact with the system via:
*   **REST API**: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)
*   **MQTT Telemetry**: Subscribe to `factory/machine/telemetry` via any MQTT client.
*   **Modbus Registers**: Connect to `localhost:502` to see internal PLC state.

---

## 📊 ML Engineering Features
*   **Class Imbalance Handling**: Utilises SMOTE (Synthetic Minority Over-sampling Technique) to ensure the model accurately predicts rare failure events.
*   **Feature Engineering**: Custom transformers for **Mechanical Power** and **Temperature Differentials** derived from raw sensor data.
*   **High Performance**: Sub-millisecond inference time (< 2ms) tuned for edge device limitations.

---

## 💼 Industrial Relevance
This portfolio project demonstrates the ability to:
1.  **Bridge OT and IT**: Connecting Operational Technology (PLC/Modbus) with Information Technology (MQTT/Web APIs).
2.  **Professional ML Ops**: Transitioning from legacy Random Forest to state-of-the-art Gradient Boosting (XGBoost) for enhanced reliability.
3.  **Design for Scalability**: Using containerisation and asynchronous messaging.

---
**Maintained by Felix Hardyan** | [GitHub](https://github.com/felixhardyan)
