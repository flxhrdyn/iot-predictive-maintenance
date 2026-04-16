# IoT Predictive Maintenance System

An end to end Machine Learning Operations project designed to predict industrial machine failure. This system transitions a static Kaggle dataset into a robust localized application, complete with automated preprocessing, training pipelines, a lightning fast REST API, and a multithreaded IoT simulator.

## Project Architecture

This repository adopts a strict software engineering standard by isolating concerns. Data lives in the data folder, experiments remain inside notebooks, core capabilities sit in the src directory, and deployment mechanisms fall under the API or Docker configs.

```text
Machine_Failure_Classification_Tabular/
   data/
      predictive_maintenance.csv
   notebooks/
      Machine_Failure_Classification.ipynb
   src/
      preprocess.py
      train.py
      predict.py
   api/
      main.py
   iot_simulator/
      sensor_simulator.py
   models/
      model.joblib
      preprocessor.joblib
      metadata.json
   Dockerfile
   docker-compose.yml
   requirements.txt
```

## Features

* **Intelligent Preprocessing**: An object oriented preprocessor dynamically builds engineered parameters like Temperature Differentials and Mechanical Power while handling rigorous Tukey IQR winsorizing against extreme outliers.
* **Automated Training**: One simple command triggers data shuffling, SMOTE minority class generation, and precise Random Forest compiling. The engine produces lightweight memory artefacts automatically.
* **Continuous IoT Emulation**: A robust threading simulator broadcasts organically degrading machine profiles to challenge the API exactly like a true factory floor.
* **Sub Millisecond API Interfacing**: Powered by FastAPI, inference algorithms process edge inputs almost instantly, enabling confident production deployments.

## Quick Start Guide

### Step One
Provision your environment with the core dependencies.
```bash
pip install -r requirements.txt
```

### Step Two
Instantiate the Machine Learning algorithms by executing the core training sequence. This procedure parses the raw diagnostic data in the background and populates the models directory.
```bash
python src/train.py
```

### Step Three
Engage the backend router layer. This boots up the inference proxy on localhost.
```bash
uvicorn api.main:app --reload --port 8000
```

### Step Four
You can immediately view the live API interface using your browser by navigating to `http://localhost:8000/docs`. To mimic physical edge sensors, open a secondary terminal pane and execute the physics simulator to trigger telemetry broadcasts.
```bash
# Simulates three varied machines experiencing cascading mechanical stress
python iot_simulator/sensor_simulator.py --multi
```

## Application Programming Interface Reference

### Checking Infrastructure Status
A lightweight GET request verifying deep component health.
* Route: `GET /health`
* Response confirms model load readiness alongside timestamps.

### Individual Sensor Validation
Submit structured operational signals to receive deterministic risks.
* Route: `POST /predict`
* Required Parameters: Type, Air Temperature, Process Temperature, Torque, Rotational Speed, and cumulative Tool Wear.
* Response fields outline absolute prediction booleans, risk magnitude labels, and exact floating point probabilities.

### Gateway Batching
Designed explicitly for aggregated packet scenarios.
* Route: `POST /predict/batch`
* Evaluates lists encompassing up to five hundred individual items simultaneously to conserve pipeline overhead.

## Containerization

For seamless cloud or local provisioning, bypass local Python setups entirely.

```bash
# Deploys both the API algorithm and the background simulated machines
docker compose --profile simulation up --build
```
