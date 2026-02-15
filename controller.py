import asyncio
from dataclasses import dataclass
from typing import Callable, Optional

from bleak import BleakClient, BleakScanner

AE3B = "0000ae3b-0000-1000-8000-00805f9b34fb"  # write no response [file:223]
AE3C = "0000ae3c-0000-1000-8000-00805f9b34fb"  # notify [file:223]

def _split20(msg: str):
    # Max 20 bytes per packet; split longer messages. [file:231]
    return [msg[i:i+20].encode("ascii") for i in range(0, len(msg), 20)]

def _hx(n: int, width: int) -> str:
    return format(n, "X").zfill(width)

@dataclass
class MotorCmd:
    speed: int = 0         # 0..0x7fff [file:221][file:231]
    ccw: bool = False      # ccw True -> Direction.Left behavior (adds 0x8000) [file:221]

class MKH4Controller:
    def __init__(self, device_name: str):
        self.device_name = device_name
        self.client: Optional[BleakClient] = None
        self._ready = asyncio.Event()

    async def connect(self, on_notify: Optional[Callable[[str], None]] = None):
        dev = await BleakScanner.find_device_by_filter(lambda d, ad: d.name == self.device_name)
        if not dev:
            raise RuntimeError(f"Device not found: {self.device_name}")

        self.client = BleakClient(dev)
        await self.client.connect()

        def _cb(_, data: bytearray):
            s = data.decode("ascii", errors="ignore")
            if on_notify:
                on_notify(s)
            # Ready event described in repo [file:231][file:221]
            if s.startswith("T01711W"):
                self._ready.set()

        await self.client.start_notify(AE3C, _cb)

    async def disconnect(self):
        if self.client:
            try:
                await self.client.stop_notify(AE3C)
            except Exception:
                pass
            await self.client.disconnect()
            self.client = None

    async def _send(self, msg: str):
        if not self.client:
            raise RuntimeError("Not connected")
        for pkt in _split20(msg):
            await self.client.write_gatt_char(AE3B, pkt, response=False)

    async def initialize(self, timeout_s: float = 10.0):
        # Init sequence from repo [file:231][file:221]
        await self._send("T041AABBW")
        await self._send("T00EW")
        await self._send("T01F1W")
        try:
            await asyncio.wait_for(self._ready.wait(), timeout=timeout_s)
        except asyncio.TimeoutError:
            # Some devices may still work; we continue.
            pass

    def _speed_field(self, m: MotorCmd) -> str:
        if m.speed < 0 or m.speed > 0x7FFF:
            raise ValueError("speed must be 0..32767 (0x7fff)")
        v = m.speed | (0x8000 if m.ccw else 0)  # direction bit [file:231][file:221]
        return _hx(v, 4)

    async def set_speeds(self, A: MotorCmd, B: MotorCmd, C: MotorCmd, D: MotorCmd):
        # T144: 4 motors speed fields [file:231]
        msg = (
            "T1440" + self._speed_field(A) +
            "0" + self._speed_field(B) +
            "0" + self._speed_field(C) +
            "0" + self._speed_field(D) + "W"
        )
        await self._send(msg)

    async def stop_all(self):
        # stopAll in repo [file:221]
        await self._send("T14400000000000000000000W")

