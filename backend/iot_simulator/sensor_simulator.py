"""
iot_simulator/sensor_simulator.py
Simulates IoT sensors streaming machine telemetry to the prediction API.

Usage:
    # Single device
    python iot_simulator/sensor_simulator.py

    # Custom device and type
    python iot_simulator/sensor_simulator.py --device-id press-003 --type L --interval 1

    # Simulate 3 devices simultaneously
    python iot_simulator/sensor_simulator.py --multi

    # Run exactly 50 readings then stop
    python iot_simulator/sensor_simulator.py --max-readings 50
"""
import os
os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import argparse
import random
import sys
import threading
import time
from datetime import datetime

import requests

#  Default API endpoint (override with   api url or API_URL env var)  #
DEFAULT_API = "http://localhost:8000"

#  Realistic operating ranges per machine quality type  #
#   Derived from dataset statistics (Kaggle predictive_maintenance.csv)
SENSOR_PROFILES = {
    "L": {  # Low quality — widest variance, highest wear per cycle
        "air_temp": (297.0, 303.0),
        "proc_temp_offset": (9.0, 12.0),   # Process temp = Air + offset
        "rpm_base": (1300, 1700),
        "torque_base": (35.0, 60.0),
        "wear_rate": 2,                     # minutes of wear per reading
    },
    "M": {
        "air_temp": (297.0, 302.0),
        "proc_temp_offset": (9.5, 11.5),
        "rpm_base": (1350, 1900),
        "torque_base": (30.0, 55.0),
        "wear_rate": 3,
    },
    "H": {  # High quality — most stable
        "air_temp": (297.5, 301.5),
        "proc_temp_offset": (9.8, 11.0),
        "rpm_base": (1400, 2100),
        "torque_base": (25.0, 50.0),
        "wear_rate": 5,
    },
}

# ANSI colour helpers
_GREEN = "\033[92m"
_YELLOW = "\033[93m"
_RED = "\033[91m"
_RESET = "\033[0m"
_BOLD = "\033[1m"

_RISK_COLOUR = {
    "LOW": _GREEN,
    "MEDIUM": _YELLOW,
    "HIGH": _RED,
}


class DeviceSimulator:
    """Simulates one physical IoT sensor device."""

    def __init__(self, device_id: str, machine_type: str, api_url: str):
        self.device_id = device_id
        self.machine_type = machine_type.upper()
        self.api_url = api_url.rstrip("/")
        self.profile = SENSOR_PROFILES[self.machine_type]

        # State – cumulative tool wear
        self.tool_wear = random.randint(0, 40)

        # Stats
        self.n_sent = 0
        self.n_failure = 0
        self.n_error = 0

    #  #

    def _generate(self) -> dict:
        """Build a realistic sensor snapshot with gradual degradation."""
        p = self.profile
        wear_ratio = min(1.0, self.tool_wear / 250.0)  # [0 – 1]

        air_temp = random.uniform(*p["air_temp"])

        # Process temp rises slightly as tool wears
        proc_offset = random.uniform(*p["proc_temp_offset"]) + wear_ratio * 2.5
        proc_temp = air_temp + proc_offset

        # RPM drops & becomes noisier at high wear
        rpm_noise = random.gauss(0, 60 * (1 + wear_ratio))
        rpm = max(1100, random.uniform(*p["rpm_base"]) - wear_ratio * 150 + rpm_noise)

        # Torque increases slightly as cutting resistance grows
        torque = random.uniform(*p["torque_base"]) + wear_ratio * 8.0 + random.gauss(0, 1.5)

        # Advance wear (reset to 0 if exceeds threshold to simulate tool change)
        new_wear = self.tool_wear + p["wear_rate"] + random.randint(-1, 1)
        self.tool_wear = new_wear if new_wear <= 250 else 0

        return {
            "type": self.machine_type,
            "air_temperature_K": round(air_temp, 2),
            "process_temperature_K": round(proc_temp, 2),
            "rotational_speed_rpm": round(rpm, 1),
            "torque_Nm": round(torque, 2),
            "tool_wear_min": self.tool_wear,
            "device_id": self.device_id,
        }

    def _send(self, payload: dict) -> dict | None:
        try:
            resp = requests.post(
                f"{self.api_url}/predict",
                json=payload,
                timeout=5,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.ConnectionError:
            return {"error": f"Cannot reach API at {self.api_url}"}
        except requests.exceptions.Timeout:
            return {"error": "Request timed out"}
        except Exception as exc:
            return {"error": str(exc)}

    def _format_line(self, payload: dict, result: dict) -> str:
        ts = datetime.now().strftime("%H:%M:%S")
        device = f"[{self.device_id}]"

        if "error" in result:
            return f"{ts} [ERR] {device} -- {result['error']}"

        risk = result.get("risk_level", "LOW")
        label = result.get("label", "?")
        prob = result.get("failure_probability", 0.0) * 100
        col = _RISK_COLOUR.get(risk, "")

        if risk == "HIGH":
            icon = "[!!]"
        elif risk == "MEDIUM":
            icon = "[!] "
        else:
            icon = "[OK]"

        return (
            f"{ts} {icon} {_BOLD}{device:<16}{_RESET}"
            f"  type={self.machine_type}"
            f"  wear={payload['tool_wear_min']:>3d}min"
            f"  rpm={payload['rotational_speed_rpm']:>6.1f}"
            f"  torque={payload['torque_Nm']:>5.1f}Nm"
            f"  tempD={payload['process_temperature_K']-payload['air_temperature_K']:>4.1f}K"
            f"  ->  {col}{label} ({prob:.1f}%) [{risk}]{_RESET}"
        )

    #  #

    def run(self, interval: float = 2.0, max_readings: int | None = None):
        print(
            f"\n  >>  Starting {self.device_id}  "
            f"(type={self.machine_type}, interval={interval}s)"
        )
        try:
            while True:
                if max_readings and self.n_sent >= max_readings:
                    break

                payload = self._generate()
                result = self._send(payload)

                self.n_sent += 1
                if result and "error" not in result:
                    if result.get("prediction") == 1:
                        self.n_failure += 1
                else:
                    self.n_error += 1

                print(self._format_line(payload, result or {"error": "no response"}))
                time.sleep(interval)

        except KeyboardInterrupt:
            pass  # handled by parent

        return self.summary()

    def summary(self) -> dict:
        return {
            "device_id": self.device_id,
            "readings": self.n_sent,
            "failures": self.n_failure,
            "errors": self.n_error,
            "failure_rate": (
                f"{self.n_failure / self.n_sent * 100:.1f}%" if self.n_sent else "N/A"
            ),
        }


#  Main  #

def _print_header(api_url: str, multi: bool):
    print("\n" + "=" * 70)
    print("  IoT Sensor Simulator -- Machine Failure Prediction")
    print("=" * 70)
    print(f"  API endpoint  : {api_url}/predict")
    print(f"  Mode          : {'Multi-device (L + M + H)' if multi else 'Single device'}")
    print("  Press Ctrl+C to stop.\n")


def _print_summary(summaries: list):
    print("\n" + "=" * 70)
    print("  Summary Simulation Results")
    print("=" * 70)
    print(f"  {'Device':<20} {'Readings':>10} {'Failures':>10} {'Rate':>10} {'Errors':>10}")
    print("  " + "-" * 62)
    for s in summaries:
        print(
            f"  {s['device_id']:<20}"
            f"  {s['readings']:>8}"
            f"  {s['failures']:>8}"
            f"  {s['failure_rate']:>9}"
            f"  {s['errors']:>8}"
        )
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Simulate IoT sensors → Machine Failure Prediction API"
    )
    parser.add_argument("--api-url", default=DEFAULT_API, help="API base URL")
    parser.add_argument("--device-id", default="sensor-001",
                        help="Device identifier")
    parser.add_argument("--type", default="M", choices=["L", "M", "H"],
                        help="Machine quality type")
    parser.add_argument("--interval", type=float, default=2.0,
                        help="Seconds between readings (default: 2)")
    parser.add_argument("--max-readings", type=int, default=None,
                        help="Stop after N readings (default: infinite)")
    parser.add_argument("--multi", action="store_true",
                        help="Simulate 3 devices (L, M, H) concurrently")
    args = parser.parse_args()

    _print_header(args.api_url, args.multi)

    if args.multi:
        devices = [
            DeviceSimulator("sensor-L-001", "L", args.api_url),
            DeviceSimulator("sensor-M-001", "M", args.api_url),
            DeviceSimulator("sensor-H-001", "H", args.api_url),
        ]
        threads = [
            threading.Thread(
                target=d.run,
                kwargs={"interval": args.interval, "max_readings": args.max_readings},
                daemon=True,
            )
            for d in devices
        ]
        for t in threads:
            t.start()
        try:
            while any(t.is_alive() for t in threads):
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n  STOP Stopping ...\n")

        _print_summary([d.summary() for d in devices])

    else:
        device = DeviceSimulator(args.device_id, args.type, args.api_url)
        try:
            device.run(interval=args.interval, max_readings=args.max_readings)
        except KeyboardInterrupt:
            pass
        _print_summary([device.summary()])


if __name__ == "__main__":
    main()
