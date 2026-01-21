import asyncio
from bleak import BleakScanner

async def run():
    print("Scanning for devices... (Turn on your Hub now)")
    devices = await BleakScanner.discover()
    for d in devices:
        # Filter for likely candidates
        if d.name and ("MK" in d.name or "Mould" in d.name or "LEGO" in d.name):
            print(f"FOUND POSSIBLE HUB: {d.name} - Address: {d.address}")
        else:
            # Print everything just in case
            print(f"Device: {d.name} - {d.address}")

asyncio.run(run())