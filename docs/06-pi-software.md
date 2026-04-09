# 06 — Raspberry Pi 5 Software

The Pi 5 is the high-level brain. It is **not** the custom board — its job is logging, dashboard, camera, and operator interface.

## Roles

| Role | Module (in `pi/`) |
|---|---|
| Telemetry logger | `pi/telemetry/` |
| Operator dashboard | `pi/telemetry/dashboard/` |
| Camera capture | `pi/camera/` |
| Operator UI / joystick | `pi/interface/` |
| Servo control (PCA9685) | `pi/interface/servo/` |

## Telemetry logger

- Opens UART to MCU (likely `/dev/ttyAMA0` or `/dev/serial0`)
- Parses framed telemetry (sync bytes → length → payload → CRC)
- Validates CRC, drops bad frames, increments error counters
- Writes to:
  - rolling CSV file (one row per frame)
  - in-memory ring buffer for the dashboard
- Configurable via `pi/telemetry/config.yaml`

> TODO: pick lib — `pyserial` + a hand-written framer is fine. Avoid heavy frameworks.

## Dashboard

- Web-based, served on the Pi (FastAPI / Flask + a simple JS frontend, or Streamlit for v1)
- Live plots: temp, humidity, distance, IMU tilt, battery V/I
- Status indicators: link OK, last frame age, error count
- Camera tile: latest frame from Pi AI Camera
- Accessible from a phone on the same WiFi

> TODO: decide between Streamlit (fast to build) vs FastAPI + small HTML (more polished).

## Camera capture

- Wraps `picamera2` or the AI Camera SDK
- Captures still frames on demand or at low rate (1 Hz)
- Saves to `pi/camera/captures/` with timestamps
- Optional: pushes latest frame to dashboard

## Operator interface

- Joystick driver (PS2 module via GPIO or USB)
- Maps joystick → servo command stream → PCA9685
- Emergency stop button binding

## Servo control (PCA9685)

- I²C (separate bus from MCU board)
- Library: `adafruit-circuitpython-pca9685` or direct smbus
- Trajectory generation lives here, not on the MCU

## Telemetry storage

- Logs go to `/var/log/spyder/` on the Pi (rotated)
- Sample data committed under `pi/telemetry/sample_data/` for the repo (small representative slices only)

## Why this all stays on the Pi

- These tasks are non-real-time and benefit from a full OS (file system, web server, USB camera stack)
- Keeping them off the MCU means the MCU firmware stays small, fast, and easy to verify

---

> TODO: add `pi/telemetry/parser.py` once the frame format in `docs/05` is locked.
