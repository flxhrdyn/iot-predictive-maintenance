"""
industrial_iot/gateway.py
Edge Gateway: Bridges the Field Level (Modbus) to the IoT Cloud (MQTT).
Reads from PLC and publishes to MQTT Broker.
"""
import os
import time
import json
import logging
from pymodbus.client import ModbusTcpClient
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Environment variables with defaults
MODBUS_HOST = os.getenv("MODBUS_HOST", "localhost")
MODBUS_PORT = int(os.getenv("MODBUS_PORT", 502))
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = "factory/machine/telemetry"

# Scaling constants (must match plc_emulator.py)
TEMP_SCALE = 10
TORQUE_SCALE = 10

def run_gateway():
    log.info(f"Connecting to PLC at {MODBUS_HOST}:{MODBUS_PORT}")
    log.info(f"Connecting to MQTT Broker at {MQTT_HOST}:{MQTT_PORT}")

    # Initialize Clients
    mb_client = ModbusTcpClient(MODBUS_HOST, port=MODBUS_PORT)
    # paho-mqtt 2.0+ requires an explicit CallbackAPIVersion
    mqtt_client = mqtt.Client(CallbackAPIVersion.VERSION2, "IIoT-Gateway")
    
    try:
        mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
        mqtt_client.loop_start()
        log.info("MQTT Client connected.")
    except Exception as e:
        log.error(f"Failed to connect to MQTT: {e}")
        return

    while True:
        try:
            if not mb_client.connected:
                mb_client.connect()
                
            # Read Holding Registers 0 to 5 from Slave 1
            rr = mb_client.read_holding_registers(0, 6, slave=1)
            
            if not rr.isError():
                vals = rr.registers
                
                # Unpack and descale
                payload = {
                    "device_id": "industrial-plc-001",
                    "type": chr(vals[0]),
                    "air_temperature_K": round(vals[1] / TEMP_SCALE, 2),
                    "process_temperature_K": round(vals[2] / TEMP_SCALE, 2),
                    "rotational_speed_rpm": float(vals[3]),
                    "torque_Nm": round(vals[4] / TORQUE_SCALE, 2),
                    "tool_wear_min": int(vals[5]),
                    "timestamp": time.time()
                }
                
                # Publish to MQTT
                mqtt_client.publish(MQTT_TOPIC, json.dumps(payload))
                # log.info(f"Published: {payload['tool_wear_min']} min wear")
            else:
                log.warning(f"Modbus Read Error: {rr}")
                
        except Exception as e:
            log.error(f"Gateway loop error: {e}")
            
        time.sleep(2.0) # Poll every 2 seconds

if __name__ == "__main__":
    try:
        run_gateway()
    except KeyboardInterrupt:
        log.info("Gateway stopped.")
