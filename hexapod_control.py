import asyncio
import numpy as np
import time
from bleak import BleakClient

# --- CONFIGURATION ---
HUB_ADDRESS = "8D7D0D4B-444C-B348-4F5D-2F5D560FEB23"  # 
CHARACTERISTIC_UUID = "0000ae3c-0000-1000-8000-00805f9b34fb" 

# HEXAPOD GEOMETRY
BASE_RADIUS = 10.0
PLATFORM_RADIUS = 6.0
DEFAULT_HEIGHT = 15.0 # The "Zero" height for your legs

class StewartPlatform:
    def __init__(self):
        self.legs = np.zeros(6)
        
    def calculate_leg_lengths(self, pitch, roll, height_offset):
        """
        Returns target lengths for all 6 legs.
        We will only use the first 4 for this test.
        """
        l0 = DEFAULT_HEIGHT + (pitch * 0.5) + (roll * 0.5) + height_offset
        l1 = DEFAULT_HEIGHT + (pitch * 0.5) - (roll * 0.5) + height_offset
        l2 = DEFAULT_HEIGHT + height_offset # Middle legs less affected by pitch
        l3 = DEFAULT_HEIGHT + height_offset
        l4 = DEFAULT_HEIGHT - (pitch * 0.5) + (roll * 0.5) + height_offset
        l5 = DEFAULT_HEIGHT - (pitch * 0.5) - (roll * 0.5) + height_offset
        
        return [l0, l1, l2, l3, l4, l5]

async def send_command(client, motor_speeds):
    """
    Sends speeds to Ports A, B, C, D.
    """
    def to_byte(speed):
        # Converts standard int (-100 to 100) to hex byte
        return int(speed) & 0xFF

    # Packet Structure: [Header, A, B, C, D, Footer]
    packet = bytearray([
        0x7E,           
        to_byte(motor_speeds[0]), # Port A
        to_byte(motor_speeds[1]), # Port B
        to_byte(motor_speeds[2]), # Port C 
        to_byte(motor_speeds[3]), # Port D 
        0xEF            
    ])
    
    try:
        await client.write_gatt_char(CHARACTERISTIC_UUID, packet)
    except Exception as e:
        print(f"Send failed: {e}")

async def main():
    print(f"Connecting to {HUB_ADDRESS}...")
    try:
        async with BleakClient(HUB_ADDRESS) as client:
            print("Connected! Starting 4-Port Test Loop.")
            platform = StewartPlatform()
            
            t = 0
            while True:
                t += 0.1
                
                # 1. SIMULATE INPUT
                # We create a wobble to force motors to change direction
                pitch = np.sin(t) * 5  
                roll = np.cos(t) * 5   
                
                # 2. CALCULATE LEGS
                lengths = platform.calculate_leg_lengths(pitch, roll, 0)
                
                # 3. DETERMINE SPEEDS FOR ALL 4 PORTS
                # Logic: If Target Length > Default Height -> Extend (+50)
                #        If Target Length < Default Height -> Retract (-50)
                
                # Map Leg 0 -> Port A
                speed_a = 50 if lengths[0] > DEFAULT_HEIGHT else -50
                
                # Map Leg 1 -> Port B
                speed_b = 50 if lengths[1] > DEFAULT_HEIGHT else -50
                
                # Map Leg 2 -> Port C
                speed_c = 50 if lengths[2] > DEFAULT_HEIGHT else -50
                
                # Map Leg 3 -> Port D
                speed_d = 50 if lengths[3] > DEFAULT_HEIGHT else -50
                
                # Debug Print
                print(f"Pitch:{pitch:.1f} | A:{speed_a} B:{speed_b} C:{speed_c} D:{speed_d}")
                
                # 4. SEND COMMAND
                await send_command(client, [speed_a, speed_b, speed_c, speed_d])
                
                await asyncio.sleep(0.1)

    except Exception as e:
        print(f"Connection Error: {e}")
        print("Make sure the Hub is ON and blinking.")

if __name__ == "__main__":
    asyncio.run(main())