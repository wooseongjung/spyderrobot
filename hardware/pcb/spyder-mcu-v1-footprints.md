# spyder-mcu-v1 Footprint Assignment Guide

**Date:** 2026-04-12
**Board:** spyder-mcu-v1 (STM32F411RET6 custom MCU board)
**KiCad version:** 10.0.0

Use **Tools > Edit Symbol Fields** in KiCad to bulk-assign footprints via the spreadsheet view.

---

## Quick Reference: Footprint by Package Size

| Package | KiCad Footprint |
|---------|----------------|
| 0805 resistor | `Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder` |
| 2512 resistor (shunt) | `Resistor_SMD:R_2512_6332Metric_Pad1.40x3.35mm_HandSolder` |
| 0805 capacitor | `Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder` |
| 1210 capacitor | `Capacitor_SMD:C_1210_3216Metric_Pad1.33x1.80mm_HandSolder` |
| Electrolytic (radial) | `Capacitor_THT:CP_Radial_D5.0mm_P2.50mm` |

---

## ICs

| Ref Des | Component | Package | Footprint |
|---------|-----------|---------|-----------|
| U1 | STM32F411RET6 | LQFP-64 | `Package_QFP:LQFP-64_10x10mm_P0.5mm` |
| U_BUCK | TPS5430DDA | SO-8 PowerPAD | `Package_SO:TI_SO-PowerPAD-8_ThermalVias` |
| U_LDO | MCP1700-3302E/TT | SOT-23-3 | `Package_TO_SOT_SMD:SOT-23-3` |
| U_OPA | OPA333AID | SOIC-8 | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` |
| U_INA | INA226AIDGSR | VSSOP-10 | `Package_SO:VSSOP-10_3.0x3.0mm_P0.5mm` |
| U_IMU | MPU9250 | QFN-24 | `Sensor_Motion:InvenSense_QFN-24_3x3mm_P0.4mm` |
| U_ENV | BME280 | LGA-8 | `Package_LGA:Bosch_LGA-8_2.5x2.5mm_P0.65mm` |
| U_ESD1 | PRTR5V0U2X | SOT-363 (SC-70-6) | `Package_TO_SOT_SMD:SOT-363_SC-70-6` |
| U_ESD2 | PRTR5V0U2X | SOT-363 (SC-70-6) | `Package_TO_SOT_SMD:SOT-363_SC-70-6` |

---

## Resistors (0805)

All standard 0805 resistors use: `Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder`

| Ref Des | Value | Notes |
|---------|-------|-------|
| R_FB1 | 10k 1% | Buck feedback divider top |
| R_FB2 | 3.24k 1% | Buck feedback divider bottom (VREF = 1.221V) |
| R_GATE | 100k | Q1 gate damping to GND |
| R_RST | 10k | NRST pull-up |
| R_SCL | 4.7k | I2C clock pull-up |
| R_SDA | 4.7k | I2C data pull-up |
| R_ALERT | 10k | INA226 ALERT pull-up |
| R_IMU_INT | 10k | MPU9250 INT pull-up |
| R_ECHO_TOP | 1k | HC-SR04 level shift divider |
| R_ECHO_BOT | 2k | HC-SR04 level shift divider |
| R_FILT | 10k | OPA333 output RC filter |
| R_REF1 | 10k | ADC reference divider |
| R_REF2 | 10k | ADC reference divider |
| R_LED1 | 470R | Heartbeat LED |
| R_LED2 | 470R | Telemetry LED |
| R_LED3 | 470R | Error LED |
| R_LED_PWR | 470R | Power LED |
| R1_NI | 1k 0.1% | Diff amp gain (NI path) |
| R1_INV | 1k 0.1% | Diff amp gain (INV path) |
| R2_NI | 30k 0.1% | Diff amp gain (NI path) |
| R2_INV | 30k 0.1% | Diff amp feedback |
| JP1 | 0R | Shunt bypass jumper |
| JP_OPA1 | 0R | OPA333 supply isolation |
| JP_OPA2 | 0R | OPA333 input HI isolation |
| JP_OPA3 | 0R | OPA333 input LO isolation |
| JP_OPA4 | 0R | OPA333 output isolation |

### Shunt Resistor (2512)

| Ref Des | Value | Footprint |
|---------|-------|-----------|
| R_SHUNT | WSK2512R0200FEA (20 mOhm) | `Resistor_SMD:R_2512_6332Metric_Pad1.40x3.35mm_HandSolder` |

---

## Capacitors

### 0805 Capacitors

All use: `Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder`

| Ref Des / Location | Value | Dielectric |
|---------------------|-------|------------|
| C_BOOT | 100nF | X7R (>=16V) |
| C_HSE1 | 20pF | COG/NP0 |
| C_HSE2 | 20pF | COG/NP0 |
| C_RST | 100nF | X7R |
| C_FILT | 150nF | COG/NP0 |
| STM32 VDD (x4) | 100nF | X7R |
| STM32 VBAT | 100nF | X7R |
| STM32 VCAP_1 | 4.7uF | X5R |
| STM32 VDDA | 100nF + 1uF | X7R / X5R |
| MCP1700 input | 100nF + 1uF | X7R / X5R |
| MCP1700 output | 100nF | X7R |
| MPU9250 VDD | 100nF | X7R |
| MPU9250 VDDIO | 100nF | X7R |
| MPU9250 REGOUT | 100nF | X7R |
| BME280 VDD | 100nF | X7R |
| BME280 VDDIO | 100nF | X7R |
| INA226 VS | 100nF | X7R |
| OPA333 V+ | 100nF | X7R |

### 1210 Capacitors

All use: `Capacitor_SMD:C_1210_3216Metric_Pad1.33x1.80mm_HandSolder`

| Ref Des | Value | Notes |
|---------|-------|-------|
| C_IN1 | 22uF X5R | Buck input (>=25V rated) |
| C_IN2 | 22uF X5R | Buck input (>=25V rated) |
| C_OUT1 | 22uF X5R | Buck output (>=10V rated) |
| C_OUT2 | 22uF X5R | Buck output (>=10V rated) |
| STM32 VDD bulk | 10uF X5R | Shared near VDD cluster |
| MCP1700 output | 10uF X5R | Near VOUT pin |
| OPA333 V+ bulk | 10uF X5R | Near pin 7 |

### Electrolytic (Through-Hole)

| Ref Des | Value | Footprint |
|---------|-------|-----------|
| C_BULK | 100uF 10V | `Capacitor_THT:CP_Radial_D5.0mm_P2.50mm` |

---

## Discrete Semiconductors

| Ref Des | Component | Package | Footprint |
|---------|-----------|---------|-----------|
| Q1 | SiA457DJ (P-ch MOSFET) | PowerPAK SO-8 | `Package_SO:PowerPAK_SO-8_Single` |
| D_TVS | SMBJ12CA (bidirectional) | SMB | `Diode_SMD:D_SMB_Handsoldering` |
| D_CLAMP | BAT54 (Schottky) | SOT-23 | `Package_TO_SOT_SMD:SOT-23-3` |
| D1 | Green LED | 0805 | `LED_SMD:LED_0805_2012Metric_Pad1.15x1.40mm_HandSolder` |
| D2 | Yellow LED | 0805 | `LED_SMD:LED_0805_2012Metric_Pad1.15x1.40mm_HandSolder` |
| D3 | Red LED | 0805 | `LED_SMD:LED_0805_2012Metric_Pad1.15x1.40mm_HandSolder` |
| D_PWR | Green LED | 0805 | `LED_SMD:LED_0805_2012Metric_Pad1.15x1.40mm_HandSolder` |

---

## Inductors & Ferrites

| Ref Des | Component | Footprint |
|---------|-----------|-----------|
| L1 | 22uH 4A shielded (Bourns SRN6045TA-220M) | `Inductor_SMD:L_Bourns_SRN6045TA` |
| FB1 | Ferrite bead 600R@100MHz | `Inductor_SMD:L_0805_2012Metric_Pad1.15x1.40mm_HandSolder` |
| FB2 | Ferrite bead 30R@100MHz | `Inductor_SMD:L_0805_2012Metric_Pad1.15x1.40mm_HandSolder` |

---

## Crystal

| Ref Des | Component | Footprint |
|---------|-----------|-----------|
| Y1 | 8 MHz HC-49S | `Crystal:Crystal_SMD_HC49-SD_HandSoldering` |

> **Note:** Verify crystal C_L (load capacitance) from datasheet before ordering.
> C_HSE1/C_HSE2 = 20 pF assumes C_L ~ 20 pF. Adjust if needed.

---

## Connectors

| Ref Des | Type | Pitch | Footprint |
|---------|------|-------|-----------|
| J_BAT | 1x02 header | 2.54mm | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` |
| J_PI | 1x02 header | 2.54mm | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` |
| JP_BOOT | 1x03 header | 2.54mm | `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical` |
| J_HCSR04 | 1x04 header | 2.54mm | `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical` |
| J_UART | 1x04 header | 2.54mm | `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical` |
| J_I2C | 1x04 header | 2.54mm | `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical` |
| J_GPIO | 1x06 header | 2.54mm | `Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical` |
| J_SWD | 2x05 header | 1.27mm | `Connector_PinHeader_1.27mm:PinHeader_2x05_P1.27mm_Vertical_SMD` |
| SW_RST | Tact switch | — | `Button_Switch_SMD:SW_SPST_CK_RS282G05A3` |

---

## Test Points

| Ref Des | Type | Net | Footprint |
|---------|------|-----|-----------|
| TP1 | Through-hole loop | VBAT_PROT | `TestPoint:TestPoint_Loop_D2.50mm_Drill1.0mm` |
| TP2 | Through-hole loop | 5V_BUCK | `TestPoint:TestPoint_Loop_D2.50mm_Drill1.0mm` |
| TP3_5V | Through-hole loop | 5V_RAIL | `TestPoint:TestPoint_Loop_D2.50mm_Drill1.0mm` |
| TP3 | Through-hole loop | 3V3_RAIL | `TestPoint:TestPoint_Loop_D2.50mm_Drill1.0mm` |
| TP4 | Through-hole loop | GND | `TestPoint:TestPoint_Loop_D2.50mm_Drill1.0mm` |
| TP5 | SMD pad | I2C_SCL | `TestPoint:TestPoint_Pad_D1.5mm` |
| TP6 | SMD pad | I2C_SDA | `TestPoint:TestPoint_Pad_D1.5mm` |
| TP7 | SMD pad | UART_TX | `TestPoint:TestPoint_Pad_D1.5mm` |
| TP8 | SMD pad | UART_RX | `TestPoint:TestPoint_Pad_D1.5mm` |
| TP9 | SMD pad | ADC_VOUT | `TestPoint:TestPoint_Pad_D1.5mm` |
| TP10 | SMD pad | SENSE_HI | `TestPoint:TestPoint_Pad_D1.5mm` |
| TP11 | SMD pad | SENSE_LO | `TestPoint:TestPoint_Pad_D1.5mm` |

---

## Mounting Holes

| Ref Des | Type | Footprint |
|---------|------|-----------|
| H1-H4 | M3 plated | `MountingHole:MountingHole_3.2mm_M3_Pad_Via` |

---

## Fuse

| Ref Des | Component | Footprint |
|---------|-----------|-----------|
| F1 | PTC 6A resettable | `Fuse:Fuse_1812_4532Metric_Pad1.30x3.40mm_HandSolder` |

---

## Component Count Summary

| Category | Count |
|----------|-------|
| ICs | 9 (U1, U_BUCK, U_LDO, U_OPA, U_INA, U_IMU, U_ENV, U_ESD1, U_ESD2) |
| Resistors (0805) | 25 |
| Shunt resistor (2512) | 1 |
| Capacitors (0805) | ~24 |
| Capacitors (1210) | ~7 |
| Capacitors (electrolytic) | 1 |
| Discrete (FET, TVS, diodes, LEDs) | 7 |
| Inductors/ferrites | 3 |
| Crystal | 1 |
| Connectors | 8 |
| Test points | 11 |
| Switches | 1 |
| Fuse | 1 |
| Mounting holes | 4 |
| **Total** | **~103** |
