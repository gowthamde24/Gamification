import asyncio
from bleak import BleakClient

# YOUR HUB ADDRESS
HUB_ADDRESS = "8D7D0D4B-444C-B348-4F5D-2F5D560FEB23"

async def main():
    print(f"Connecting to {HUB_ADDRESS}...")
    try:
        async with BleakClient(HUB_ADDRESS) as client:
            print("Connected! Scanning for WRITE characteristics...\n")
            
            for service in client.services:
                for char in service.characteristics:
                    # We are looking for characteristics we can WRITE to
                    if "write" in char.properties or "write-without-response" in char.properties:
                        print(f"FOUND CANDIDATE: {char.uuid}")
                        print(f"   -> Properties: {char.properties}")
                        print("   ------------------------------------------------")
                        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())