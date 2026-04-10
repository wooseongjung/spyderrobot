# 04 — PCB Design

Custom MCU board specification. This is the **main engineering deliverable** of the project.

## Goals

- Single 2- or 4-layer PCB that hosts an STM32 MCU, environmental + IMU + power-monitoring sensors, and a clean UART interface to a Raspberry Pi 5.
- Designed in **KiCad** (version TODO).
- Manufacturable at **JLCPCB / PCBWay** with hand-solderable footprints (0805 minimum where possible).
- Bring-up checklist must pass before declaring v1 done.

## MCU choice — STM32 G4 / F4

| Criterion | Why STM32 |
|---|---|
| Industry standard | Strong CV signal vs. RP2040 / RP2350 for the kind of role I'm targeting |
| Mature toolchain | STM32CubeIDE / CubeMX, HAL drivers |
| Peripherals | Multiple I²C + SPI + UART, ≥ 12-bit ADC, plenty of timers for HC-SR04 input capture |
| Hand-solderable footprint available | LQFP-48 / LQFP-64 |

> TODO: pick exact part within the family. Candidates: STM32G431, STM32G474, STM32F411, STM32F446. Decision goes in `docs/10-design-decisions.md`.

## Functional blocks

### A. MCU block
- STM32 MCU
- 8 MHz HSE crystal (or use HSI initially) — TODO
- Reset circuit (10 kΩ pull-up + 100 nF + button)
- BOOT0 button + jumper for entering bootloader
- SWD debug header (4 + GND + 3V3)
- Decoupling caps per VDD pin (100 nF + 10 µF bulk)

### B. Power & monitoring block
- 5 V input from Pi 5 / external (header + protection)
- Reverse-polarity protection (P-MOSFET)
- 3.3 V LDO (e.g., AMS1117-3.3 or low-dropout part — TODO)
- Power LED + 3.3 V LED
- INA226 for shunt current + bus voltage measurement (I²C)
- TVS / ferrite bead on power input
- Test points on 5 V, 3.3 V, GND

### C. Sensor block
- IMU footprint: **MPU9250** (I²C, v1 end-product part; 9-DoF adds magnetometer for heading). MPU6050 is the Phase 1 bench prototype only and is **not** designed onto the v1 PCB.
- BME280 / SHT31 footprint (I²C)
- Header for HC-SR04 (5 V, GND, TRIG, ECHO with level shift to 3.3 V)
- Optional BME680 footprint (I²C, future air-quality upgrade)
- Optional ToF sensor (VL53L1X) footprint

### D. Communication block
- UART header to Pi 5 (TX, RX, GND, optional 3.3 V reference)
- I²C breakout header (SDA, SCL, 3V3, GND) for expansion
- SPI header for future use
- Programming / debug header (SWD)

### E. Support block
- Reset button
- Boot mode jumper
- 3+ status LEDs (power, heartbeat, error)
- Test points on every bus
- Mounting holes (M3, 4 corners)
- Silkscreen labels for everything

## I/O budget (preliminary)

| Function | Pins | Notes |
|---|---|---|
| I²C1 (sensors) | 2 | SDA, SCL |
| UART1 (Pi link) | 2 | TX, RX |
| HC-SR04 trigger | 1 | GPIO out |
| HC-SR04 echo | 1 | timer input capture, level-shifted |
| Discrete analog showcase | 2 | ADC channels reserved for the op-amp current-sense block (see ADR-0008) |
| Status LEDs | 3 | GPIO out |
| Boot button | 1 | GPIO in |
| SWD | 4 | dedicated |

> Total well within an LQFP-48. TODO: finalise and add to schematic.

## Power tree on the board

```
5V_IN ──(Reverse-polarity FET + fuse)── 5V_RAIL ── INA226 (shunt) ─── 5V (load)
                                                        │
                                                        └── LDO ── 3.3V_RAIL ── STM32 + sensors
```

## Layer stack (TODO)

- 2-layer is cheapest and adequate for this design.
- 4-layer (sig / GND / PWR / sig) gives a much cleaner power/ground and better EMC for the sensors. Probably worth the small upcharge.

> TODO: confirm choice once schematic is closed.

## Design rules

- Min trace: 0.2 mm
- Min via: 0.3 mm drill, 0.6 mm pad
- Min clearance: 0.2 mm
- Component side: SMD only where possible
- All headers on one edge for cable management

## Bring-up checklist (linked from `docs/09-test-and-validation.md`)

1. Visual inspection (solder bridges, missing parts)
2. Resistance check on 5 V → GND, 3.3 V → GND (no short)
3. Power up with current limit on bench PSU; check current draw is sane
4. Measure 5 V and 3.3 V rails
5. Connect SWD; verify STM32 ID detected
6. Flash blink-LED firmware; verify heartbeat LED
7. Probe each I²C bus; verify pull-ups
8. Run sensor scan; verify each device acks
9. Run UART loopback to Pi; verify framing
10. Run full firmware; verify telemetry

---

> TODO: insert KiCad project link once `hardware/pcb/` is populated.
> TODO: add 3D render of the board once layout is done → `assets/images/`.
