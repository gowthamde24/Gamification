import asyncio
import numpy as np
from bleak import BleakClient
from pynput import keyboard 

# --- CONFIGURATION ---
HUB_ADDRESS = "8D7D0D4B-444C-B348-4F5D-2F5D560FEB23" # Your found Address
# UPDATE THIS LINE WITH THE NEW UUID FROM YOUR SCAN:
CHARACTERISTIC_UUID = "0000ae01-0000-1000-8000-00805f9b34fb" 

# ROBOT SETTINGS
DEFAULT_HEIGHT = 15.0 
MAX_TILT = 8.0  

# GLOBAL STATE
current_pitch = 0.0
current_roll = 0.0
current_height = DEFAULT_HEIGHT
running = True

# --- KEYBOARD LISTENER ---
def on_press(key):
    global current_pitch, current_roll, current_height, running
    try:
        if key == keyboard.Key.esc:
            running = False
            return False
            
        if hasattr(key, 'char'):
            if key.char == 'w': current_pitch = MAX_TILT   # Forward
            if key.char == 's': current_pitch = -MAX_TILT  # Back
            if key.char == 'a': current_roll = -MAX_TILT   # Left
            if key.char == 'd': current_roll = MAX_TILT    # Right
            if key.char == 'q': current_height = DEFAULT_HEIGHT + 5 # Up
            if key.char == 'e': current_height = DEFAULT_HEIGHT - 5 # Down
            
    except AttributeError:
        pass

def on_release(key):
    global current_pitch, current_roll, current_height
    if hasattr(key, 'char'):
        if key.char in ['w', 's']: current_pitch = 0
        if key.char in ['a', 'd']: current_roll = 0
        if key.char in ['q', 'e']: current_height = DEFAULT_HEIGHT

# --- HEXAPOD LOGIC ---
class StewartPlatform:
    def calculate_leg_lengths(self, pitch, roll, height):
        l0 = height + (pitch * 0.5) + (roll * 0.5)
        l1 = height + (pitch * 0.5) - (roll * 0.5)
        l2 = height - (pitch * 0.5) + (roll * 0.5)
        l3 = height - (pitch * 0.5) - (roll * 0.5)
        return [l0, l1, l2, l3]

async def send_command(client, speeds):
    # Some 'AE' hubs use a different packet structure.
    # We will try the STANDARD one first. 
    # If this connects but motors don't move, we will change this packet.
    packet = bytearray([
        0x7E, 
        int(speeds[0]) & 0xFF, 
        int(speeds[1]) & 0xFF, 
        int(speeds[2]) & 0xFF, 
        int(speeds[3]) & 0xFF, 
        0xEF
    ])
    try:
        await client.write_gatt_char(CHARACTERISTIC_UUID, packet)
    except Exception as e:
        print(f"Packet Send Error: {e}")

# --- MAIN LOOP ---
async def main():
    print(f"Connecting to {HUB_ADDRESS}...")
    
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    try:
        async with BleakClient(HUB_ADDRESS) as client:
            print("Connected! USE KEYS: W/A/S/D to tilt. Q/E for height. ESC to quit.")
            platform = StewartPlatform()
            
            while running:
                targets = platform.calculate_leg_lengths(current_pitch, current_roll, current_height)
                speeds = []
                for target_len in targets:
                    if abs(target_len - DEFAULT_HEIGHT) < 0.5:
                        speeds.append(0)
                    elif target_len > DEFAULT_HEIGHT:
                        speeds.append(50) 
                    else:
                        speeds.append(-50) # Note: If motors spin wrong way, swap 50/-50 here
                
                await send_command(client, speeds)
                await asyncio.sleep(0.1)
    except Exception as e:
        print(f"Connection Failed: {e}")
            
    print("Disconnected.")

if __name__ == "__main__":
    asyncio.run(main())