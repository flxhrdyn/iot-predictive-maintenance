"""Quick API test script — run after `uvicorn api.main:app --port 8000`"""
import json
import sys
import requests

BASE = "http://localhost:8000"

def check(label, r):
    status = "OK" if r.ok else f"FAIL ({r.status_code})"
    print(f"\n[{status}] {label}")
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text[:400])

# 1. Health
check("GET /health", requests.get(f"{BASE}/health"))

# 2. Model info
check("GET /model/info", requests.get(f"{BASE}/model/info"))

# 3. Normal reading
normal = {
    "type": "M",
    "air_temperature_K": 298.1,
    "process_temperature_K": 308.6,
    "rotational_speed_rpm": 1551.0,
    "torque_Nm": 42.8,
    "tool_wear_min": 10,
    "device_id": "sensor-M-001"
}
check("POST /predict (normal machine)", requests.post(f"{BASE}/predict", json=normal))

# 4. High-risk reading (high wear + extreme conditions)
danger = {
    "type": "L",
    "air_temperature_K": 301.5,
    "process_temperature_K": 313.5,
    "rotational_speed_rpm": 1180.0,
    "torque_Nm": 72.0,
    "tool_wear_min": 240,
    "device_id": "sensor-L-danger"
}
check("POST /predict (HIGH RISK)", requests.post(f"{BASE}/predict", json=danger))

# 5. Batch
batch_payload = {
    "readings": [
        normal,
        danger,
        {
            "type": "H",
            "air_temperature_K": 299.5,
            "process_temperature_K": 309.8,
            "rotational_speed_rpm": 1800.0,
            "torque_Nm": 35.0,
            "tool_wear_min": 50,
            "device_id": "sensor-H-001"
        }
    ]
}
r = requests.post(f"{BASE}/predict/batch", json=batch_payload)
print(f"\n[{'OK' if r.ok else 'FAIL'}] POST /predict/batch")
if r.ok:
    data = r.json()
    print(f"  total={data['total']}  failures={data['failures_detected']}  high_risk={data['high_risk_count']}")
    for res in data["results"]:
        prob_pct = res["failure_probability"] * 100
        inf_ms   = res["inference_time_ms"]
        print(f"  [{res['device_id']:<20}] {res['label']:<12} {prob_pct:5.1f}%  [{res['risk_level']}]  {inf_ms:.1f}ms")

print("\n=== All tests done ===")
