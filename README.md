# Gamification

Python-based Bluetooth Low Energy (BLE) control for the **Mould King MKH4.0** hub. This project connects to the hub from a computer, performs the required initialization handshake, and runs motor sequences defined in `config.json` using the `bleak` BLE client library.[web:267][web:276]

## Overview

This project allows the MKH4.0 hub to be controlled from a PC instead of the mobile app. The program reads a sequence from `config.json`, converts each motor instruction into the hub command format, sends it over BLE, waits for the configured duration, and then stops the motors before moving to the next step.

The project is organized into three main files:

- `config.json` — stores the BLE device name and motion sequence.
- `controller.py` — handles BLE communication, notifications, initialization, and command encoding.
- `test_run.py` — reads the configuration and executes the sequence.

## Project structure

```text
Gamification/
├── config.json
├── controller.py
├── test_run.py
├── requirements.txt
└── README.md
```

## Features

- Connects to the MKH4.0 hub using Python and `bleak`.[web:267][web:276]
- Performs the BLE initialization handshake before motor control starts.
- Supports motor commands for ports A, B, C, and D.
- Loads the motion sequence from `config.json`.
- Executes each step with configurable direction, speed, and duration.
- Stops all motors briefly between steps.

## Requirements

- Python 3.9 or later.
- Bluetooth enabled on the computer.
- Mould King MKH4.0 hub powered on.
- The official mobile app must be closed before running the script.
- `bleak` installed for BLE communication.[web:267][web:276]

## Installation

Clone the repository:

```bash
git clone https://github.com/gowthamde24/Gamification.git
cd Gamification
```

Create and activate a virtual environment:

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows
```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Example `requirements.txt`:

```txt
bleak
```

## Configuration

The motion sequence is defined in `config.json`.

### Example

```json
{
  "device_name": "YX-01EB2C",
  "sequence": [
    {
      "description": "Forward",
      "duration": 2.0,
      "motors": {
        "A": { "direction": "CCW", "speed": 12288 }
      }
    },
    {
      "description": "Backward",
      "duration": 0.0,
      "motors": {
        "A": { "direction": "CW", "speed": 12288 }
      }
    },
    {
      "description": "left",
      "duration": 0.0,
      "motors": {
        "B": { "direction": "CCW", "speed": 12288 }
      }
    },
    {
      "description": "right",
      "duration": 0.0,
      "motors": {
        "B": { "direction": "CW", "speed": 12288 }
      }
    }
  ]
}
```

### Configuration fields

| Field | Description |
|---|---|
| `device_name` | BLE advertised name of the MKH4.0 hub. |
| `sequence` | List of steps executed in order. |
| `description` | Step label printed in the terminal. |
| `duration` | Time in seconds for that step. |
| `motors` | Motor commands for ports `A`, `B`, `C`, and `D`. |
| `direction` | `CW` or `CCW`. |
| `speed` | Motor speed from `0` to `32767`. |

### Notes

- If a motor is not included in a step, it stays stopped.
- A `duration` of `0.0` sends the command and moves to the next stop almost immediately.
- For visible movement, use a duration greater than `0.0`.

## How the code works

### `controller.py`

`controller.py` contains the BLE communication logic.

It does the following:

- Finds the device by BLE name.
- Connects using `BleakClient`.[web:267][web:276]
- Subscribes to notifications.
- Sends the initialization commands.
- Encodes motor speeds and directions.
- Sends motor packets to the hub.
- Stops all motors when needed.

### BLE characteristics

```python
AE3B = "0000ae3b-0000-1000-8000-00805f9b34fb"  # write no response
AE3C = "0000ae3c-0000-1000-8000-00805f9b34fb"  # notify
```

### Initialization sequence

The controller sends these commands before starting motor control:

```text
T041AABBW
T00EW
T01F1W
```

The hub is considered ready when it sends a notification starting with:

```text
T01711W
```

### Motor encoding

Each motor uses a 4-character hexadecimal field.

- Speed range: `0` to `32767`
- `CW` → normal speed value
- `CCW` → speed value with direction bit `0x8000` added

Examples:

| Direction | Speed | Encoded field |
|---|---:|---:|
| CW | 12288 | `3000` |
| CCW | 12288 | `B000` |
| Stop | 0 | `0000` |

### Packet format

The packet sent by `set_speeds()` is:

```text
T1440AAAA0BBBB0CCCC0DDDDW
```

Where:
- `AAAA` = Motor A
- `BBBB` = Motor B
- `CCCC` = Motor C
- `DDDD` = Motor D

BLE messages are split into chunks of up to 20 bytes before sending, which matches common BLE write handling in practice.[web:273][web:276]

### `test_run.py`

`test_run.py` is the main script that executes the motion sequence.

It does the following:

1. Loads `config.json`
2. Connects to the hub
3. Runs initialization
4. Reads each step from `sequence`
5. Converts motor settings into `MotorCmd` objects
6. Sends the motor command
7. Waits for the configured duration
8. Stops all motors briefly
9. Proceeds to the next step

### Direction handling

The helper function `get_motor_cmd()` converts JSON motor settings into `MotorCmd` values:

- `CW` → `MotorCmd(speed=speed, ccw=False)`
- `CCW` → `MotorCmd(speed=speed, ccw=True)`
- Missing or unknown direction → stopped motor

## Running the project

Run the script with:

```bash
python3 test_run.py
```

Example terminal output:

```text
NOTIFY: T01711W
--- Forward for 2.0 seconds ---
--- Backward for 0.0 seconds ---
--- left for 0.0 seconds ---
--- right for 0.0 seconds ---
--- Sequence Complete ---
```

## Example motor steps

### Motor A only
```json
{
  "description": "Motor A CCW",
  "duration": 2.0,
  "motors": {
    "A": { "direction": "CCW", "speed": 12288 }
  }
}
```

### Motor B only
```json
{
  "description": "Motor B CW",
  "duration": 2.0,
  "motors": {
    "B": { "direction": "CW", "speed": 12288 }
  }
}
```

### Motor A and B together
```json
{
  "description": "A and B together",
  "duration": 3.0,
  "motors": {
    "A": { "direction": "CCW", "speed": 12288 },
    "B": { "direction": "CW", "speed": 12288 }
  }
}
```

## Troubleshooting

### Device not found
- Check that `device_name` exactly matches the hub BLE name.
- Make sure the hub is powered on.
- Make sure Bluetooth is enabled.
- Close the official mobile app if it is connected.

### No motor movement
- Check that initialization completed successfully.
- Make sure the motor is connected to the expected hub port.
- Increase the `duration` if it is too short.
- Verify the speed is greater than `0`.

### Import or dependency errors
Install dependencies again:

```bash
pip install -r requirements.txt
```

## Repository

GitHub: [https://github.com/gowthamde24/Gamification](https://github.com/gowthamde24/Gamification)

## Acknowledgment

This project uses the Python `bleak` library for asynchronous, cross-platform BLE communication with GATT devices.[web:267][web:276]