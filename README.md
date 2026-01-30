# MKH4.0 (Mould King) — Python BLE Controller (2-DOF Platform)

This repository provides a Python-based Bluetooth Low Energy (BLE) controller for the Mould King MKH4.0 hub, designed to run repeatable two-motor motion sequences from a PC. Motor behavior is defined externally in `config.json`, including per-motor CW/CCW speeds, step durations, and optional start delays so motors don’t have to begin at the same time. The code is organized so `controller.py` handles BLE connection and command framing, while `test_run.py` focuses on high-level movement logic (FORWARD/BACKWARD/LEFT/RIGHT) and safe start/stop sequencing, making it easy to tune motion without changing the protocol layer.

This project controls a **Mould King MKH4.0** Bluetooth hub from a **computer using Python**, with a clean separation of:
- `controller.py` (BLE + protocol)
- `test_run.py` (your motion logic / sequence runner)
- `config.json` (input file: speeds, directions, timing)

It supports **4 directions using 2 motors (A & B)** and lets you set:
- CW/CCW speeds per motor
- Per-step duration in seconds
- Per-step per-motor start delays (A_delay, B_delay)

---


## Requirements

- Python 3.9+ recommended
- Bluetooth enabled on your computer
- Only **one** device can control the hub at a time: close the Mould King phone app before running.

---

## Install

```bash
cd Gamification
pip install -r requirements.txt
