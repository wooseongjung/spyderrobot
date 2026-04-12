# spyder-mcu-v1 Wiring & PCB Design Review

**Date:** 2026-04-12
**Reviewed files:**
- `hardware/pcb/spyder-mcu-v1-wiring.csv`
- `hardware/pcb/spyder-mcu-v1-symbols.csv`
- `hardware/pcb/spyder-mcu-v1.net` (KiCad netlist, Eeschema 10.0.0)
- `docs/04-pcb-design.md`
- `docs/10-design-decisions.md` (ADR-0008 through ADR-0015)
- `docs/03-hardware-bom.md`

---

## Action Items by Priority

| Priority | Item | Section | Action |
|----------|------|---------|--------|
| **CRITICAL** | TPS5430 feedback divider | [1.1](#11-tps5430-feedback-divider-values-are-wrong) | Fix R_FB2 to 3.24k (reference is 1.221V, not 0.8V) |
| **HIGH** | On-board buck undocumented | [1](#1-critical-on-board-buck-converter--undocumented-scope-expansion) | Update docs/ADRs to record scope expansion, or revert to external buck |
| **MEDIUM** | Missing output isolation jumper | [3](#3-missing-analog-showcase-output-isolation-jumper) | Add JP_OPA4 between OPA_OUT and R_FILT |
| **MEDIUM** | I/O budget table stale | [4](#4-io-budget-table-is-stale) | Update `docs/04-pcb-design.md` with PB0, PB1, PB5-7, PA2 |
| **MEDIUM** | JP1 bypass scope mismatch | [2](#2-bypass-jumper-jp1-scope-mismatch) | Align JP1 with docs (FET+shunt bypass) or update docs |
| **LOW** | Symbols CSV stale | [5](#5-symbols-csv-vs-wiring-csv-divergence) | Regenerate from current schematic |
| **LOW** | C_BOOT cross-ref typo | [6](#6-c_boot-cross-reference-typo) | Fix "pin 7" to "pin 8" in Connects To column |
| **LOW** | Q1 gate resistor | [7](#7-reverse-polarity-fet-gate--no-resistor) | Add 100k between gate and GND |
| **LOW** | Crystal load caps | [9c](#9c-crystal-load-cap-verification) | Verify 20 pF against actual crystal C_L spec |
| **LOW** | SWO debug trace | [9d](#9d-swo-trace-output) | Wire SWD pin 6 to PB3 for ITM debug |
| **LOW** | 5V power LED | [9b](#9b-power-led-rail) | Consider adding LED on 5V_RAIL |

---

## 1. CRITICAL: On-Board Buck Converter -- Undocumented Scope Expansion

**What the wiring CSV does:** Includes a full TPS5430DDA buck converter block (rows 14-39) -- battery input J_BAT (7.4-12V), TVS diode (SMBJ12CA), PTC fuse, reverse-polarity FET Q1, TPS5430 buck with external L/C/R, producing 5V_BUCK.

**What the docs say:**
- `docs/04-pcb-design.md` line 205: *"5V_IN comes from an external buck on the battery side (out of scope for v1 PCB)"*
- `docs/03-hardware-bom.md` line 56: *"5 V buck -- external module, >= 5 A continuous... **Not on the custom PCB**"*
- ADR-0013 describes: `5V_IN -> FET -> Shunt -> 5V_RAIL`, with 5V_IN from an external buck.

**KiCad netlist confirms the buck IS in the schematic:** U2 = TPS5430DDA, J_BAT1, L1, C_IN1/C_IN2, C_OUT1/C_OUT2, R_FB1/R_FB2 all present.

**Verdict:** The schematic/wiring have evolved past the documented architecture. The PCB design doc, BOM, and ADR-0013 all need a new ADR to record this scope expansion -- or the buck converter should be removed from the schematic and reverted to the external-buck architecture.

### 1.1. TPS5430 Feedback Divider Values Are Wrong

The wiring CSV (rows 36-39) uses:
- R_FB1 = 10k, R_FB2 = 1.91k
- Note says: `VOUT = 0.8V * (1 + 10k/1.91k) = 5.0V`

**The TPS5430 internal reference is 1.221V, not 0.8V** (TI datasheet SLVS632). With these resistor values:

```
VOUT = 1.221 * (1 + 10/1.91) = 1.221 * 6.236 = 7.61V   <-- NOT 5V
```

**If built with R_FB2 = 1.91k, the buck will output ~7.6V and likely damage the Pi 5 and all 5V-rated downstream components.**

For a correct 5V output:
```
R_FB2 = R_FB1 / ((VOUT / VREF) - 1) = 10k / ((5.0 / 1.221) - 1) = 3.23k
```
Use standard value: **R_FB2 = 3.24k, 1%**.

The 0.8V reference in the CSV note appears to come from a different TI regulator family (e.g. TPS54331 or TPS62xxx).

---

## 2. Bypass Jumper JP1 Scope Mismatch

- **PCB design doc** (`04-pcb-design.md:179-180`): JP1 bypasses the entire FET + shunt series block (`5V_IN -> 5V_RAIL`)
- **ADR-0013** (`10-design-decisions.md:202`): *"0 Ohm bypass jumper across the series (FET + shunt) path"*
- **Wiring CSV** (rows 42-43): JP1 bridges `5V_BUCK -> 5V_RAIL` -- across the shunt only, after the buck, NOT across the FET

If the on-board buck is intentional, decide:
1. JP1 bridges the full protection block (FET + shunt) as documented, or
2. Update the docs to reflect the new narrower bypass scope and add a rationale

---

## 3. Missing Analog Showcase Output Isolation Jumper

**PCB design doc** (`04-pcb-design.md:131`):
> *"The block's **input, output, and supply** are each brought to 0 Ohm solder jumpers"*

**Wiring CSV** (rows 194-199) provides three jumpers:
- JP_OPA1: supply isolation (3V3 -> OPA333 V+)
- JP_OPA2: input HI isolation (SENSE_HI -> R1_NI)
- JP_OPA3: input LO isolation (SENSE_LO -> R1_INV)

**Missing:** Output isolation jumper (OPA_OUT -> R_FILT). Without it, a misbehaving OPA333 (oscillation, latch-up) can still drive the STM32 ADC pin PA0 even when inputs and supply are disconnected.

**Fix:** Add JP_OPA4 (0 Ohm 0805) between OPA_OUT and R_FILT pin 1.

---

## 4. I/O Budget Table Is Stale

`docs/04-pcb-design.md` I/O budget (lines 140-163) lists 12 user I/O + 3 LEDs. The wiring CSV adds pins not in the budget:

| New pin | Function | Notes |
|---------|----------|-------|
| PB0 | INA226 ALERT (EXTI0) | Over-current interrupt -- important for safety |
| PB1 | MPU9250 INT (EXTI1) | Data-ready interrupt -- essential for high-rate IMU reads |
| PB5 | GPIO breakout (spare) | TIM3_CH2 / SPI1_MOSI / I2C1_SMBA |
| PB6 | GPIO breakout (spare) | TIM4_CH1 / USART1_TX (alt) |
| PB7 | GPIO breakout (spare) | TIM4_CH2 / USART1_RX (alt) |
| PA2 | GPIO breakout (spare) | USART2_TX / ADC1_IN2 -- future servo bus TX |

PB0 and PB1 are especially important additions. The I/O budget table needs updating to reflect these 6 new pins.

---

## 5. Symbols CSV vs Wiring CSV Divergence

The symbols CSV (`spyder-mcu-v1-symbols.csv`) appears to be from an earlier design stage and does not match the current schematic:

| Item | Symbols CSV | Wiring CSV / Netlist |
|------|:-----------:|:--------------------:|
| Power input | J_PWR (5V input header) | J_BAT (7.4-12V battery) |
| Buck converter | Not listed | U_BUCK / U2 (TPS5430DDA) |
| TVS diode | Not listed | D_TVS (SMBJ12CA) |
| Echo clamp diode | Not listed | D_CLAMP (BAT54) |
| ESD protection | Not listed | U_ESD1/U_ESD2 (PRTR5V0U2X) |
| LDO input ferrite | Not listed | FB2 (30R@100MHz) |
| Interrupt pull-ups | Not listed | R_ALERT, R_IMU_INT |
| GPIO breakout | Not listed | J_GPIO / J1 (6-pin) |
| Test points | Not listed | TP1-TP11 |

**Fix:** Regenerate the symbols CSV from the current schematic to avoid confusion.

---

## 6. C_BOOT Cross-Reference Typo

Wiring CSV row 25: C_BOOT pin 2 "Connects To" says `U_BUCK pin 7 / L1 pin 1`.

Pin 7 is VIN; the switch node (SW_NODE) is **pin 8 (PH)**. The net name `SW_NODE` is correct, so this is a documentation-only error in the "Connects To" column -- not a wiring error.

**Fix:** Change "U_BUCK pin 7" to "U_BUCK pin 8 (PH)" in the Connects To cell.

---

## 7. Reverse-Polarity FET Gate -- No Resistor

Q1 gate connects directly to GND (wiring CSV row 10). The circuit is functionally correct: normal polarity gives Vgs = -VBAT (-7.4 to -12V), well within the SiA457DJ's +/-20V abs max; reverse polarity keeps the FET OFF.

However, a 10k-100k resistor between Q1 gate and GND is standard practice to:
- Damp gate ringing during fast battery insertion transients
- Provide a defined impedance for the gate node

Minor concern -- works without it, but cheap insurance for a first-spin board.

---

## 8. Things That Are Correct and Well-Done

The wiring CSV is impressively thorough and mostly correct. Items that check out:

- **I2C address map** (rows 284-289): 0x68 (MPU9250), 0x76 (BME280), 0x40 (INA226), 0x3C (off-board OLED) -- no conflicts
- **INA226 pin wiring** (rows 148-157): all 10 pins correctly mapped; IN+/IN- connected to SENSE_HI/SENSE_LO Kelvin sense nets; VBUS to 5V_RAIL
- **OPA333 SOIC-8 pinout** (rows 160-167): matches TI datasheet exactly (pin 2 = IN-, pin 3 = IN+, pin 4 = V-, pin 6 = VOUT, pin 7 = V+)
- **Difference amplifier gain network** (rows 170-177): R1_NI/R1_INV from sense pair to op-amp inputs, R2_NI to GND (NI bias), R2_INV feedback from output to IN- -- classic 4-resistor diff-amp, correctly wired
- **Output filter** (rows 180-183): R_FILT=10k + C_FILT=150nF gives f_c = 1/(2*pi*10k*150nF) = 106 Hz -- correctly computed, well above 10 Hz sample rate
- **HC-SR04 level shifter** (rows 208-213): 1k/2k resistive divider (5V * 2k/(1k+2k) = 3.33V) plus BAT54 Schottky clamp to 3V3 -- double protection for PA6
- **Kelvin shunt 4-terminal wiring** (rows 46-49): I1/I2 force pads for load current, E1/E2 sense pads branching to both INA226 and OPA333 -- matches ADR-0011/0015
- **Decoupling** (rows 326-342): comprehensive per-device, correct dielectric choices (X7R for 100nF bypass, X5R for bulk, COG for filter)
- **ESD protection** (rows 216-223): PRTR5V0U2X on UART and I2C breakout headers -- good addition not in the original PCB spec
- **Test points** (rows 245-257): 11 TPs covering VBAT_PROT, 5V_BUCK, 5V_RAIL, 3V3, GND, I2C, UART, ADC_VOUT, SENSE_HI/LO -- excellent for bench bring-up with myDAQ
- **LDO input ferrite FB2** (rows 228-229): isolates LDO from Pi switching noise on 5V_RAIL
- **SWD header** (rows 92-101): standard ARM 10-pin 1.27mm, NRST correctly on pin 10
- **Boot jumper** (rows 85-87): 3-pin header, centre pin to BOOT0, default jumper to GND (normal run)
- **Net summary** (rows 292-324): complete, voltage domains clearly documented with types

---

## 9. Suggested Upgrades / Improvements

### 9a. MCP1700 Current Headroom

MCP1700-3302E/TT is rated 250 mA max. Estimated 3.3V load:
- STM32F411 at 100 MHz: ~40 mA
- MPU9250: 3.5 mA
- BME280: 0.7 mA
- INA226: 0.3 mA
- OPA333: 0.02 mA
- Pull-ups (I2C, INT, ALERT, NRST): ~2 mA
- 4 LEDs (470 Ohm from 3.3V, Vf ~2V): ~11 mA
- **Total: ~60-80 mA** (plenty of margin)

But the I2C breakout header (J_I2C) could source external modules. Consider:
- Documenting the 250 mA budget cap in the PCB spec
- Or sizing up to AP2112K-3.3 (600 mA, SOT-23-5, pin-compatible drop-in) if expansion is expected

### 9b. Power LED Rail

D_PWR is on 3V3_RAIL (rows 275-278). This indicates the LDO is running but does NOT indicate whether 5V_RAIL is healthy. For Phase 4 bring-up, a 5V indicator is more useful.

Options:
1. Add a second LED on 5V_RAIL (separate resistor -- use 680 Ohm for similar brightness at 5V)
2. Move D_PWR to 5V_RAIL if only one power LED is desired

### 9c. Crystal Load Cap Verification

C_HSE1 = C_HSE2 = 20 pF. The formula is:
```
C_load_each = 2 * (C_L_crystal - C_stray)
```
With C_stray ~ 3-5 pF (typical PCB + MCU pin capacitance):
- If crystal C_L = 12.5 pF: need ~15 pF caps
- If crystal C_L = 18 pF (e.g. ABM3B-8.000MHZ-B2T): need ~26-30 pF caps
- If crystal C_L = 20 pF: 20 pF caps would be marginally low

**Verify 20 pF against the actual crystal datasheet before ordering.** Wrong load caps shift the oscillator frequency and affect UART baud rate accuracy.

### 9d. SWO Trace Output

SWD header pin 6 (SWO) is currently NC. On the STM32F411, SWO is on PB3. Connecting SWD pin 6 to PB3 would enable ITM printf-style debugging -- very useful for firmware bring-up, zero runtime overhead when disabled.

Low effort, high value addition.

### 9e. I2C Bus Capacitance Check

On-board I2C devices: MPU9250, BME280, INA226, plus external breakout header and ESD protection (PRTR5V0U2X adds ~5 pF per line). Each device + trace adds roughly 10-15 pF.

Estimated total: ~80-120 pF -- well under the 400 pF limit for 100 kHz standard mode. Safe, but worth a quick tally against datasheets before layout, especially if fast-mode (400 kHz, 400 pF limit) is planned.
