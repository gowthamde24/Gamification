# Mould King Hexapod Control

This project enables PC-based control of a LEGO/Mould King Stewart Platform (Hexapod) using Python. 

Unlike standard LEGO Control+ hubs, the Mould King hubs are "dumb" receivers. Therefore, all **Inverse Kinematics (math)** and **Control Logic** run on the PC, which streams raw motor commands to the hub via Bluetooth Low Energy (BLE).

## Current Project Status
* **Mechanics:** Hexapod frame built (MOC-107567 style).
* **Electronics:** 1x Mould King Hub (4 Ports).
* **Software:** Python script calculating leg lengths and sending Bluetooth commands.
* **Limitation:** We currently have **1 Hub (4 ports)** but the robot has **6 Legs**. 
    * *Interim Solution:* We are driving 4 legs for testing (Ports A, B, C, D).
    * *Goal:* Acquire a second hub or use Y-cables to control all 6 legs.

---

## Hardware Requirements
1.  **PC/Laptop** with Bluetooth support.
2.  **Mould King Battery Hub** (Series 4.0 or 6.0).
3.  **Mould King/LEGO Motors** connected to ports A, B, C, D.
4.  **Python 3.7+** installed.

---

## Installation & Setup

### 1. Set up the Environment
We use a virtual environment to keep dependencies clean.

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate