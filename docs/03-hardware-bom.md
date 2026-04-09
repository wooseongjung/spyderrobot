# 03 — Hardware BOM

Two-column BOM: what's used in the **breadboard prototype** vs. what's planned for the **target v2** custom-board build.

> TODO: fill in part numbers, suppliers, and unit prices as parts are ordered.

## Compute & control

| Item | Prototype | Target v2 | Notes |
|---|---|---|---|
| SBC | Raspberry Pi 5 (8 GB) | Raspberry Pi 5 (8 GB) | unchanged |
| MCU | STM32 Nucleo dev board | STM32G4 / F4 on custom PCB | exact part TODO |
| Servo driver | PCA9685 module | PCA9685 module (off-board v1) → integrated v2 | |

## Environmental sensing

| Item | Prototype | Target v2 | Notes |
|---|---|---|---|
| Temp / humidity | DHT11 | BME280 or SHT31 | DHT11 is too coarse for the final build |
| Wetness / rain | Generic raindrop module | (kept) | analog + digital output |
| Distance | HC-SR04 ultrasonic | (kept) | considering ToF (VL53L1X) as stretch |
| Air quality / VOC | — | BME680 | optional, Phase 8 |

## Robot-state sensing

| Item | Prototype | Target v2 | Notes |
|---|---|---|---|
| IMU | MPU6050 | MPU9250 | 9-DoF for heading |
| Power monitor | — | INA226 | I²C, current shunt + bus voltage |
| Battery fuel gauge | — | TODO | optional |

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

| Item | Prototype | Target v2 | Notes |
|---|---|---|---|
| Battery | Bench PSU during prototyping | LiPo (2S or 3S) | exact cell TODO |
| 5 V buck | TODO | TODO (≥ 5 A continuous) | feeds Pi + MCU board |
| 3.3 V LDO | on-MCU dev board | discrete LDO on custom PCB | |
| Fuse / protection | — | inline fuse + reverse-polarity protection | |

## Mechanical

| Item | Prototype | Target v2 | Notes |
|---|---|---|---|
| Chassis | Existing spyder chassis (SolidWorks design, see `spider/`) | (kept) | |
| Sensor mounts | TBD | 3D-printed brackets | files → `hardware/enclosure/` |

## PCB

| Item | Prototype | Target v2 | Notes |
|---|---|---|---|
| Custom MCU board (v1) | — | KiCad, 2-layer or 4-layer | files → `hardware/pcb/` |
| Fab | — | JLCPCB / PCBWay | TODO: pick fab + assembly option |

---

## Order tracker

| Date | Vendor | Item | Qty | Cost | Status |
|---|---|---|---|---|---|
| TODO | | | | | |
