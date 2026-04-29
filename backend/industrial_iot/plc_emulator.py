"""
industrial_iot/plc_emulator.py
Simulates a Programmable Logic Controller (PLC) using Modbus TCP.
Acts as the 'Field Level' of our Industrial IoT stack.
"""
import asyncio
import logging
import random
from pymodbus.server import StartAsyncTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Constants for scaling (Modbus registers are 16-bit integers)
# We multiply floats by 10 or 100 to preserve decimal precision
TEMP_SCALE = 10
TORQUE_SCALE = 10

async def update_machine_data(context):
    """
    Background task that simulates a running industrial machine
    and updates Modbus Holding Registers with 'sensor' data.
    """
    log.info("PLC Simulation: Machine logic started.")
    slave_id = 0x01
    
    # Initial state
    wear = 0
    machine_type_code = random.choice([76, 77, 72]) # L, M, H (ASCII)
    
    while True:
        try:
            # 1. Generate realistic data (similar logic to sensor_simulator.py)
            air_temp = 298.0 + random.uniform(0, 5)
            proc_temp = air_temp + 10.0 + (wear / 50.0)
            rpm = 1500 + random.randint(-100, 100) - (wear * 2)
            torque = 40.0 + random.uniform(0, 10) + (wear / 10.0)
            wear = (wear + 1) % 250 # Loop wear for continuous simulation
            
            # 2. Update Holding Registers (FC 03)
            # Address 0: Machine Type
            # Address 1: Air Temp
            # Address 2: Proc Temp
            # Address 3: RPM
            # Address 4: Torque
            # Address 5: Tool Wear
            values = [
                machine_type_code,
                int(air_temp * TEMP_SCALE),
                int(proc_temp * TEMP_SCALE),
                int(rpm),
                int(torque * TORQUE_SCALE),
                int(wear)
            ]
            
            # Set registers (Function Code 3 maps to 'hr')
            context[slave_id].setValues(3, 0x00, values)
            # log.debug(f"PLC Update: {values}")
            
        except Exception as e:
            log.error(f"PLC logic error: {e}")
            
        await asyncio.sleep(1.0)

async def run_server():
    # Define Data Store (Holding Registers only for this demo)
    # Define Data Store (Holding Registers only)
    store = ModbusSlaveContext(
        hr=ModbusSequentialDataBlock(0, [0] * 100)
    )
    # Define Server Context with Slave ID 1
    context = ModbusServerContext(slaves={0x01: store}, single=False)
    
    # Server Identification
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Industrial Logic Systems'
    identity.ProductCode = 'ILS-PLC-001'
    identity.VendorUrl = 'http://industrial-systems.local'
    identity.ProductName = 'Predictive Maintenance PLC Emulator'
    identity.ModelName = 'Industrial-V1'
    identity.MajorMinorRevision = '1.0.0'

    # Start the simulation loop
    asyncio.create_task(update_machine_data(context))

    # Start the Modbus TCP Server
    log.info("Starting Modbus TCP Server on 0.0.0.0:502")
    # Port 502 is standard for Modbus, but requires root usually. 
    # In Docker, we can use 502 or 5020.
    await StartAsyncTcpServer(
        context=context, 
        identity=identity, 
        address=("0.0.0.0", 502)
    )

if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        log.info("PLC Server stopped.")
