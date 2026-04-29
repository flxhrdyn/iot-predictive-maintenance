import subprocess
import sys
import time
import os
from datetime import datetime

def log(tag, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{tag}] {message}")

def start_backend():
    # Ensure we are in the backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("-" * 60)
    log("SYSTEM", "Initializing Predictive Maintenance Backend")
    print("-" * 60)
    
    # Start FastAPI API
    log("INFO", "Starting FastAPI Server on http://0.0.0.0:8000")
    api_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "api.main:app", 
        "--host", "0.0.0.0", "--port", "8000", "--reload"
    ])

    # Wait a bit for API to initialize
    time.sleep(2)

    # Start Sensor Simulator
    log("INFO", "Starting IoT Sensor Simulator service")
    sim_process = subprocess.Popen([
        sys.executable, "iot_simulator/sensor_simulator.py", "--interval", "1.0"
    ])

    try:
        log("SUCCESS", "All backend services are operational")
        log("SYSTEM", "Press Ctrl+C to terminate services")
        print("-" * 60)
        
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n" + "-" * 60)
        log("SYSTEM", "Shutdown signal received")
        api_process.terminate()
        sim_process.terminate()
        log("SUCCESS", "Backend services terminated successfully")
        print("-" * 60)

if __name__ == "__main__":
    start_backend()
