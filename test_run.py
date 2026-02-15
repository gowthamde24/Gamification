import asyncio
import json

from controller import MKH4Controller, MotorCmd

def load_config(path="config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_motor_cmd(motor_cfg):
    """Converts the JSON motor config into a MotorCmd object."""
    # If the motor is missing from config, default to stopped.
    if not motor_cfg:
        return MotorCmd(speed=0, ccw=False)
        
    direction = motor_cfg.get("direction", "STOP")
    speed = motor_cfg.get("speed", 0)

    if direction == "CW":
        return MotorCmd(speed=speed, ccw=False)
    elif direction == "CCW":
        return MotorCmd(speed=speed, ccw=True)
    else:
        return MotorCmd(speed=0, ccw=False)

async def main():
    cfg = load_config()
    dev_name = cfg["device_name"]
    ctrl = MKH4Controller(dev_name)

    try:
        await ctrl.connect(on_notify=lambda s: print("NOTIFY:", s))
        await ctrl.initialize()

        for step in cfg["sequence"]:
            desc = step.get("description", "Running step")
            t = float(step["duration"])
            motors = step.get("motors", {})

            # Extract commands for all 4 independent ports
            cmd_A = get_motor_cmd(motors.get("A"))
            cmd_B = get_motor_cmd(motors.get("B"))
            cmd_C = get_motor_cmd(motors.get("C"))
            cmd_D = get_motor_cmd(motors.get("D"))

            print(f"--- {desc} for {t} seconds ---")
            
            # Send the independent commands to all 4 motors at once
            await ctrl.set_speeds(cmd_A, cmd_B, cmd_C, cmd_D)

            # Wait for the specified duration of this step
            await asyncio.sleep(t)
            
            # Stop all motors briefly before the next step to prevent hardware stress
            await ctrl.stop_all()
            await asyncio.sleep(0.1) 

        print("--- Sequence Complete ---")

    finally:
        await ctrl.disconnect()

if __name__ == "__main__":
    asyncio.run(main())