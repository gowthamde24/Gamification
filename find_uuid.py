import asyncio
from bleak import BleakClient

# REPLACE THIS WITH YOUR HUB'S ADDRESS
HUB_ADDRESS = "8D7D0D4B-444C-B348-4F5D-2F5D560FEB23" 

async def main():
    print(f"Connecting to {HUB_ADDRESS}...")
    try:
        async with BleakClient(HUB_ADDRESS) as client:
            print(f"Connected to {HUB_ADDRESS}")
            print("-" * 40)
            
            # Get all services offered by the hub
            for service in client.services:
                print(f"[Service] {service.uuid} ({service.description})")
                
                # Get all characteristics inside each service
                for char in service.characteristics:
                    print(f"  --> [Characteristic] {char.uuid}")
                    print(f"      Properties: {', '.join(char.properties)}")
                    
                    # WE ARE LOOKING FOR "WRITE"
                    if "write" in char.properties or "write-without-response" in char.properties:
                        print("      *** THIS IS YOUR CONTROL UUID!")
                    
                print("-" * 40)
                
    except Exception as e:
        print(f"Could not connect: {e}")

asyncio.run(main())