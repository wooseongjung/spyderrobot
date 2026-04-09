# 02 — System Architecture

## Top-level block diagram

```
+------------------+         +-----------------------+
|  Operator (PC /  |  WiFi   |   Raspberry Pi 5      |
|  phone browser)  +<------->+   - dashboard         |
+------------------+         |   - telemetry logger  |
                             |   - camera handler    |
                             |   - operator UI       |
                             +-----------+-----------+
                                         |
                                         |  UART (primary)
                                         |  I²C (optional, for fast bulk reads)
                                         |
                             +-----------v-----------+
                             |  Custom STM32 board   |
                             |  (the deliverable)    |
                             |                       |
                             |  +----------------+   |
                             |  |  STM32 G4/F4   |   |
                             |  +-------+--------+   |
                             |          |            |
                             |  I²C / SPI / ADC / GPIO|
                             +---+---+---+---+---+---+
                                 |   |   |   |   |
                                 |   |   |   |   +--> raindrop (analog/digital)
                                 |   |   |   +------> HC-SR04 (GPIO trigger/echo)
                                 |   |   +----------> DHT11 → BME280 (1-wire / I²C)
                                 |   +--------------> MPU6050 → MPU9250 (I²C)
                                 +------------------> INA226 (I²C, planned)

                             +-----------------------+
                             |  External, off-board  |
                             |  (Option A, v1)       |
                             |                       |
                             |  Pi 5  → PCA9685 → 12×|
                             |               MG996R  |
                             |  Pi 5  → OLED (I²C)   |
                             |  Pi 5  → joystick     |
                             |  Pi 5  → AI Camera    |
                             +-----------------------+
```

## Why Option A (Pi + custom MCU + external PCA9685)

| Decision | Reason |
|---|---|
| Custom MCU board does **not** include the servo driver in v1 | PCA9685 is a known-good module; integrating it complicates the v1 PCB. Keeps v1 finishable. |
| Pi 5 talks directly to PCA9685, not via the MCU | Servo trajectories are computed on the Pi. Lets the MCU stay focused on sensing/monitoring with a deterministic loop. |
| MCU is the sole sensor frontend | Centralises analog and timing-sensitive sampling. Pi is freed from real-time sensor duties. |
| UART as primary Pi↔MCU link | Simple, robust, easy to scope. I²C considered for bulk reads if UART throughput becomes a bottleneck. |

Detailed rationale → [`docs/10-design-decisions.md`](10-design-decisions.md).

## Comms topology

- **Pi 5 ↔ MCU board:** UART, framed protocol with start byte, length, payload, CRC. Frame format defined in [`docs/05-firmware-architecture.md`](05-firmware-architecture.md).
- **MCU ↔ sensors:** I²C primary bus for IMU, environmental, power monitor. GPIO for HC-SR04 trigger/echo. ADC for raindrop analog channel.
- **Pi 5 ↔ PCA9685:** I²C (separate from MCU bus).
- **Pi 5 ↔ operator:** WiFi, browser-based dashboard.

## Power tree (planned)

```
LiPo battery (2S/3S, TODO: select cell)
   |
   +--> Servo bus (raw, switched, fused) ----> PCA9685 / 12× servos
   |
   +--> Buck → 5 V ----+--> Raspberry Pi 5
                       |
                       +--> Custom MCU board 5 V input
                                  |
                                  +--> LDO 3.3 V → STM32 + sensors
```

> TODO: pick battery, buck converter, fuse rating; document in `docs/03-hardware-bom.md` and update this diagram.

## Functional partitioning

| Function | Where it runs | Why |
|---|---|---|
| Sensor sampling, filtering | STM32 | deterministic timing |
| IMU fusion (tilt / fall detection) | STM32 | low-latency local decisions |
| Power / current monitoring | STM32 | tight loop, can trigger safety stop |
| Telemetry framing → UART | STM32 | clean handoff to Pi |
| Telemetry parsing & logging | Pi 5 | non-real-time, lots of storage |
| Servo trajectory generation | Pi 5 | high-level, easy to iterate |
| Camera capture | Pi 5 | only the Pi has the AI camera interface |
| Operator dashboard | Pi 5 (web) | accessible from any device |

---

> TODO: replace the ASCII diagrams with proper SVG/PNG block diagrams in `assets/diagrams/` once Phase 1 is underway.
