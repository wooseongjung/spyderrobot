# 12 — Ultimate Vision

The "north star" — what spyderrobot looks like at maturity, beyond the v1 deliverables in `docs/08-roadmap-milestones.md`.

This file exists so the **framing stays coherent** even when the v1 scope is deliberately small. Anything in here is **explicitly out of scope for v1** unless promoted to a milestone.

## One-line vision

> A small, low-cost, fully self-contained quadruped sensing platform that can be dropped into a hazardous environment, walk autonomously through a defined area, and stream live environmental and platform-state telemetry back to a remote operator over LoRa or WiFi.

## What "mature" looks like

### Custom hardware (v2 / v3 PCB)
- PCA9685 integrated on the main PCB
- BME680 (or equivalent) for air quality / VOC
- 9-DoF IMU (MPU9250 or ICM-20948)
- INA226 + battery fuel-gauge IC for full power telemetry
- Onboard buck/boost so the board can power the Pi 5 directly from battery
- USB-C programming + power
- Designed for assembly (DFA): all SMD, single side where possible

### Firmware
- FreeRTOS with proper task priorities (replacing the v1 super-loop)
- Self-test on boot — every sensor checked, results sent to Pi
- OTA firmware update via the Pi
- Crash dump captured to flash on hard fault

### Pi-side software
- Polished operator dashboard (FastAPI + React or similar)
- Ground-station UI accessible from any phone on the same network
- Live camera with object detection (Pi AI Camera does this on-device)
- Map view with robot position (if outdoor + GPS added)
- Replayable session logs

### Communications
- LoRa link for long-range telemetry when WiFi isn't available
- Optional 4G/LTE modem for true remote ops
- Encrypted link

### Autonomy
- Waypoint following on a small predefined map
- Obstacle-avoidance using HC-SR04 + IMU + camera
- Return-to-home on low battery or loss of link
- Tip-over recovery routine

### Mechanical
- 3D-printed payload bay with quick-release sensor modules
- Weatherproof enclosure (IP54 or better) for the electronics
- Hot-swappable battery

### Multi-robot (very stretch)
- Two or more spyder units can coordinate to cover an area
- Shared telemetry into a single dashboard

## What this vision intentionally excludes

- Manipulator arm — out of scope, project is about sensing
- High-speed running gait — not the point
- Full SLAM / map building — too large; if needed, use an existing solution rather than build one
- ROS at runtime — the runtime stack is intentionally simple (Pi + MCU), not ROS-heavy

## How this connects to v1

| v1 (in `docs/08`) | v∞ (this file) |
|---|---|
| STM32 super-loop firmware | FreeRTOS + OTA |
| 2- or 4-layer hand-soldered PCB | DFM-optimised, JLCPCB-assembled |
| WiFi telemetry from Pi | LoRa / 4G long-range |
| Joystick teleop | Waypoint autonomy |
| DHT11 → BME280 | BME680 + air-quality story |
| Bench test → field test | Multi-robot coordinated deployment |

Everything in v1 is a stepping stone toward this — but **v1 is the goal that gets shipped**. This file just keeps the long arc visible so v1 design choices don't paint v2 into a corner.

---

> Update this file whenever the long-term vision shifts. Don't let it become aspirational fan-fiction — it should always describe a reachable end state, not a fantasy.
