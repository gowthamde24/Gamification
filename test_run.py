import asyncio
import json

from controller import MKH4Controller, MotorCmd

def load_config(path="config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

async def main():
    cfg = load_config()

    dev_name = cfg["device_name"]
    prof = cfg["profiles"]

    # Profiles (decimal speeds)
    Aprof = prof["A"]
    Bprof = prof["B"]

    def A_cw():  return MotorCmd(speed=Aprof["cwSpeed"], ccw=False)
    def A_ccw(): return MotorCmd(speed=Aprof["ccwSpeed"], ccw=True)
    def B_cw():  return MotorCmd(speed=Bprof["cwSpeed"], ccw=False)
    def B_ccw(): return MotorCmd(speed=Bprof["ccwSpeed"], ccw=True)

    ctrl = MKH4Controller(dev_name)

    try:
        await ctrl.connect(on_notify=lambda s: print("NOTIFY:", s))
        await ctrl.initialize()

        for step in cfg["sequence"]:
            d = step["dir"]
            t = float(step["seconds"])

            # 4-direction mapping with 2 motors:
            # FORWARD:  A CW,  B CW
            # BACKWARD: A CCW, B CCW
            # LEFT:     A CCW, B CW
            # RIGHT:    A CW,  B CCW
            if d == "FORWARD":
                await ctrl.set_speeds(A_cw(),  B_cw(),  MotorCmd(), MotorCmd())
            elif d == "BACKWARD":
                await ctrl.set_speeds(A_ccw(), B_ccw(), MotorCmd(), MotorCmd())
            elif d == "LEFT":
                await ctrl.set_speeds(A_ccw(), B_cw(),  MotorCmd(), MotorCmd())
            elif d == "RIGHT":
                await ctrl.set_speeds(A_cw(),  B_ccw(), MotorCmd(), MotorCmd())
            else:
                raise ValueError(f"Unknown dir: {d}")

            await asyncio.sleep(t)
            await ctrl.stop_all()

        await ctrl.stop_all()

    finally:
        await ctrl.disconnect()

asyncio.run(main())
