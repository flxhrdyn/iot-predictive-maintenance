<div align="center">

  # Industrial Machine Failure Prediction System
  **Bridging Industrial Automation (Modbus) and IoT Ecosystems (MQTT) with State-of-the-Art ML Engineering.**
  
  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![MQTT](https://img.shields.io/badge/MQTT-3C3F41?style=for-the-badge&logo=mqtt)](https://mqtt.org/)
  [![Modbus](https://img.shields.io/badge/Modbus_TCP-FF6600?style=for-the-badge&logo=industrial-software)](https://modbus.org/)
  [![XGBoost](https://img.shields.io/badge/XGBoost-23B6E9?style=for-the-badge&logo=xgboost&logoColor=white)](https://xgboost.ai/)
  [![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
  [![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
</div>

---

## Overview

In Industry 4.0, unplanned downtime is a multi-million dollar problem. **Industrial Machine Failure Prediction** is a production-grade solution that demonstrates how to bridge the gap between physical field devices and real-time AI inference.

This project serves as a **Managed IIoT Microservice Architecture** that automates the machine health monitoring lifecycle: from polling Modbus registers in a simulated factory environment to executing predictive diagnostics via a high-performance MQTT telemetry stream.

## Technical Features

- **Industrial Interoperability**: Bi-directional communication between Modbus TCP PLC emulators and MQTT brokers for seamless sensor data ingestion.
- **Predictive Inference Engine**: High-performance XGBoost classifier trained to detect manufacturing failures (Tool Wear, Heat Dissipation, Power, etc.) with high precision.
- **Edge-to-Cloud Pipeline**: Realistic simulation of industrial gateways polling registers and publishing structured JSON telemetry to centralized subscribers.
- **Imbalanced Data Handling**: Specialized ML preprocessing and model weighting to handle rare failure events in a 10,000-sample industrial dataset.
- **Real-time Monitoring**: Professional dashboard for visualizing machine telemetry and AI-driven risk assessment.

## Technology Stack

### Backend & ML
- **Framework**: FastAPI, Uvicorn
- **ML Engine**: XGBoost, Scikit-learn
- **Data Engineering**: Pandas, NumPy
- **Protocols**: PyModbus (Modbus TCP), Paho-MQTT

### Simulation & IoT
- **Field Level**: PLC Emulator (Modbus TCP Server)
- **Gateway Level**: Industrial Gateway (Modbus-to-MQTT Bridge)

### Infrastructure
- **Message Broker**: Eclipse Mosquitto (MQTT)
- **Dashboard**: HTML5, Tailwind CSS, Chart.js

## System Architecture

```mermaid
graph TD
    subgraph PLC_Field_Level [🏭 Field Level]
        M1[Mechanical Machine] -->|Sensor Data| PLC[Modbus TCP Server]
        Note1[Air Temp, RPM, Torque, Wear]
    end
    
    subgraph Gateway_Edge_Level [🌐 Edge Level]
        PLC -->|Registers Poll| GW[Industrial Gateway]
        GW -->|JSON Publish| Broker[MQTT Mosquitto]
    end
    
    subgraph AI_Cloud_Level [🧠 Intelligence Level]
        Broker -->|Real-time Stream| API[FastAPI + MQTT Subscriber]
        API -->|XGBoost| Model[Inference Engine]
        Model -->|Predictions| UI[Interactive Dashboard]
        Model -->|High Risk Alert| AlertTopic[MQTT /factory/alerts]
    end
```

---

## How to Run (Step-by-Step)

To run the complete end-to-end demonstration, follow these steps in order. Ensure you have a Python virtual environment activated.

### 1. Start the MQTT Broker
Ensure Docker is running, then start the Mosquitto broker:
```bash
docker run -d --name mosquitto -p 1883:1883 eclipse-mosquitto
```

### 2. Start the AI API
This backend handles the predictive logic and health monitoring:
```bash
uvicorn api.main:app --reload
```

### 3. Start the PLC Emulator
Simulates the physical machine and its sensors using Modbus TCP:
```bash
python industrial_iot/plc_emulator.py
```

### 4. Start the Industrial Gateway
The jbridge that polls the PLC and sends data to the MQTT broker:
```bash
python industrial_iot/gateway.py
```

### 5. Launch the Dashboard
Open the monitoring interface in your browser:
```bash
# On Windows
start dashboard.html
```

---

## Industrial IoT Details

### Modbus Register Map
The PLC exposes its internal sensor state via standard Modbus TCP Holding Registers (Slave ID: 1):

| Address | Parameter | Scaling | Description |
| :--- | :--- | :--- | :--- |
| `0000` | Machine Type | ASCII | L (76), M (77), H (72) |
| `0001` | Air Temp | x10 | Ambient Temperature in Kelvin |
| `0002` | Proc Temp | x10 | Internal Process Temperature in Kelvin |
| `0003` | RPM | x1 | Rotational Speed |
| `0004` | Torque | x10 | Applied Spindle Torque (Nm) |
| `0005` | Tool Wear | x1 | Cumulative tool wear (min) |

---

## Author

**Felix Hardyan**
*   [GitHub](https://github.com/flxhrdyn)
