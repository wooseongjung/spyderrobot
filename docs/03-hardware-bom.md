# 03 — Hardware BOM

Two-column BOM: what's used in the **breadboard prototype** vs. what's planned for the **target v2** custom-board build.

> TODO: fill in part numbers, suppliers, and unit prices as parts are ordered.

## Compute & control

| Item | Prototype | v1 custom PCB | Notes |
|---|---|---|---|
| SBC | Raspberry Pi 5 (8 GB) | Raspberry Pi 5 (8 GB) | unchanged |
| MCU dev board (Phase 2) | NUCLEO-F411RE | — | on order; firmware bring-up target |
| MCU IC (Phase 3+) | — | **STM32F411RET6** (LQFP-64) | identical die to Nucleo, locked by [ADR-0009](10-design-decisions.md#adr-0009--stm32f411ret6-as-the-v1-custom-board-mcu) |
| HSE crystal | — | 8 MHz, 20 pF, ±20 ppm, HC-49S or 3225 SMD | e.g. ABM3B-8.000MHZ-B2T |
| Servo driver | PCA9685 module | PCA9685 module (off-board, ADR-0002) → integrated v2 | |

## Environmental sensing

| Item | Phase 1 prototype | v1 custom PCB | Notes |
|---|---|---|---|
| Temp / humidity / pressure | DHT11 | **BME280** (Bosch, LGA-8 metal-lid) | BME280 over SHT31 because pressure adds altitude/state-monitoring axis for free; same I²C bus as IMU |
| Distance | HC-SR04 ultrasonic (off-board) | HC-SR04 via header (5 V, level-shifted ECHO) | ToF (VL53L1X) deferred to v2 |
| Air quality / VOC | — | BME680 | optional, Phase 8 stretch only |

## Robot-state sensing

| Item | Phase 1 prototype | v1 custom PCB | Notes |
|---|---|---|---|
| IMU | MPU6050 (6-DoF, prototype only) | **MPU9250** (9-DoF, QFN-24) | locked by [ADR-0007](10-design-decisions.md#adr-0007--mpu9250-is-the-v1-end-product-imu-mpu6050-is-prototype-only). **Stock check needed at order time** — MPU9250 is end-of-life from InvenSense; secondary distributors and JLCPCB extended-parts still carry it, but verify before BOM lock. Drop-in fallback: ICM-20948. |
| Power monitor IC | — | **INA226** (TI, VSSOP-10) | I²C, ±0.1 % gain error, 16-bit; production monitoring path |
| Power monitor — analog showcase | — | **OPA333AIDBVR** (TI, SOT-23-5) + 0.1 % matched R-array | discrete op-amp current sense in parallel with INA226, locked by [ADR-0008](10-design-decisions.md#adr-0008--include-a-discrete-op-amp-current-sense-block-on-the-v1-pcb-as-an-analog-design-showcase) and [ADR-0010](10-design-decisions.md#adr-0010--opa333-as-the-analog-showcase-op-amp). Fallback: OPA2333 (dual). |
| Current shunt | — | **20 mΩ, 1 %, 2 W, 2512** (Vishay WSL2512R0200FEA) | shared between INA226 and OPA333 block per [ADR-0011](10-design-decisions.md#adr-0011--shared-shunt-between-ina226-and-the-discrete-showcase) |
| Matched R-pair (gain set) | — | R1 = 1 kΩ, R2 = 30 kΩ, **0.1 % thin-film, 25 ppm/°C, matched-pair array** | Vishay MORN / Susumu RM3216 series. G = 30, full-scale 5 A — locked by [ADR-0013](10-design-decisions.md#adr-0013--custom-board-sits-in-the-pi-5-v-power-path-not-the-servo-rail) |
| Battery fuel gauge | — | — | not in v1; revisit when battery cell is chosen |

## User / operator interface

| Item | Prototype | Target v2 | Notes |
|---|---|---|---|
| Display | 0.96" OLED (SSD1306) or LCD1602 | (kept) | local status |
| Manual control | PS2 joystick module | (kept) | for bench testing |
| Camera | Raspberry Pi AI Camera | (kept) | Sony IMX500 |

## Actuation

| Item | Prototype | Target v2 | Notes |
|---|---|---|---|
| Servos | 12× MG996R | (kept) | already owned |
| Servo driver | PCA9685 | (kept; integrated on v2 PCB) | |

## Power

| Item | Prototype | v1 custom PCB | Notes |
|---|---|---|---|
| Battery | Bench PSU during prototyping | LiPo 3S (11.1 V nominal), exact cell TBD | sizing depends on Phase 5 walk-current measurement |
| 5 V buck (battery → 5 V_IN) | — | external module, ≥ 5 A continuous, ≤ 50 mV ripple | candidate: Pololu D24V50F5 (5 A) or RECOM R-78E5.0-1.0 ×2 in parallel. **Not on the custom PCB** — feeds the custom board's 5V_IN header per [ADR-0013](10-design-decisions.md#adr-0013--custom-board-sits-in-the-pi-5-v-power-path-not-the-servo-rail) |
| Reverse-polarity FET | — | **P-channel MOSFET**, R_ds(on) ≤ 15 mΩ at V_gs = 4.5 V | candidate: SiA457DJ (6.5 mΩ, PowerPAK 1212-8). Critical part for ADR-0013 voltage budget. |
| 3.3 V LDO | on-Nucleo regulator | **MCP1700-3302E/TT** (Microchip, SOT-23-3, 250 mA, 178 mV dropout, 1.6 µA I_q) | supplies STM32 + sensors (~50 mA peak), not the Pi |
| Bypass / decoupling | — | 100 nF + 10 µF per V_DD pin (4× on F411RET6) | X7R 0805 / X5R 1210 |
| Analog supply filter (V_DDA) | — | ferrite bead + 1 µF + 100 nF | between V_DD and V_DDA pin |
| Fuse / protection | — | PTC resettable fuse, ~6 A trip | upstream of FET on 5V_IN; specs along with ADR-0013 voltage budget |

## Mechanical

| Item | Prototype | Target v2 | Notes |
|---|---|---|---|
| Chassis | Existing spyder chassis (SolidWorks design, see `spider/`) | (kept) | |
| Sensor mounts | TBD | 3D-printed brackets | files → `hardware/enclosure/` |

## PCB

| Item | Prototype | v1 custom PCB | Notes |
|---|---|---|---|
| Custom MCU board (v1) | — | **KiCad 8+, 4-layer SIG/GND/PWR/SIG** | locked by [ADR-0012](10-design-decisions.md#adr-0012--4-layer-pcb-stack-sig--gnd--pwr--sig). Files → `hardware/pcb/` |
| Fab | — | **JLCPCB**, 4-layer 1.6 mm, HASL-LF, 1 oz copper | quantity 5, expect ~$5–30 depending on promo |
| Assembly | — | hand assembly initially | LCSC parts ordered alongside fab order; JLCPCB SMT assembly considered if hand soldering of OPA333 SOT-23-5 / INA226 VSSOP-10 proves painful |

---

## Order tracker

| Date | Vendor | Item | Qty | Cost | Status |
|---|---|---|---|---|---|
| TBD | RS / Mouser / Farnell | NUCLEO-F411RE | 1 | — | **ordered, awaiting delivery** (Phase 2 bring-up target) |

### To order before Phase 3 schematic close

Grouped by likely vendor. Stock-check every part on the chosen vendor before placing the order — especially the MPU9250 (EOL).

**LCSC / JLCPCB (for the assembled board run):**
- STM32F411RET6 — 1
- MPU9250 — 1 (or fallback ICM-20948)
- BME280 — 1
- INA226AIDGSR — 1
- OPA333AIDBVR — 1 (fallback OPA2333)
- WSL2512R0200FEA — 2 (one spare; ADR-0011 fallback uses 2 matched units)
- SiA457DJ — 1 (or DMP3056L-7 as secondary)
- MCP1700-3302E/TT — 1
- 8 MHz crystal (ABM3B-8.000MHZ-B2T or similar) — 1
- Matched R-pair, 0.1 % thin-film, 1 kΩ + 30 kΩ — 2 sets
- Passives kit (0805 R/C in standard values, 4.7 kΩ pull-ups, decoupling caps, status LED resistors) — bulk
- 0805 LEDs ×3 (red / yellow / green)
- Ferrite bead for V_DDA filter
- PTC resettable fuse, 6 A trip — 1
- Pin headers, JST connectors, BOOT0 jumper

**External (likely Pi Hut / Pimoroni / Pololu):**
- 5 V buck module ≥ 5 A continuous (Pololu D24V50F5 candidate)
- 3S LiPo + balance lead + battery monitor — sizing TBD after Phase 5
- Quality 5 V → Pi 5V-pin pigtail / harness

**Already owned (per memory `user_hardware_owned.md`):**
- NI myDAQ — used for I²C scoping and analog showcase bench validation
- Existing sensor kit (DHT11, MPU6050, OLED, HC-SR04) — Phase 1 prototype, partially reused
