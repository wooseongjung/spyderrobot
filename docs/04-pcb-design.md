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

### F. Analog showcase block (discrete current-sense amplifier)

**Purpose.** A deliberate, self-contained piece of discrete analog design on the v1 board that sits in parallel with the INA226 on the same rail. It exists to prove I can reason about op-amp topology, CMRR, resistor matching, bandwidth, and Kelvin layout — not just drop in a one-chip I²C monitor. Policy and rationale are recorded in [ADR-0008](10-design-decisions.md#adr-0008--include-a-discrete-op-amp-current-sense-block-on-the-v1-pcb-as-an-analog-design-showcase).

**Topology.**

```
                     R_SHUNT  (Kelvin-sensed)
     5V_RAIL ──────[ = = = ]────────────► 5V (to load)
                    │     │
                    │     │
                   R1     R1          (matched, 0.1 % — gain-setting high side)
                    │     │
                    ├─────┼───── V+ ──┐
                    │     │           │
                    R2    R2          │  rail-to-rail op-amp
                    │     │           │  (single 3.3 V supply)
                    │     │           │
                   GND   GND ── V− ───┘
                                      │
                                    V_OUT ──► STM32 ADC
```

- **Topology: classic difference amplifier** (4-resistor instrumentation-style). Matched pairs `R1` and `R2` set the gain `G = R2/R1`. Output referred to GND for a single-supply op-amp.
- **Input: true Kelvin sense** — two separate traces leave the shunt pads and route as a tight differential pair all the way to the op-amp inputs. No shared return with power current. This is the single most important layout rule for the whole block.
- **Shunt: `R_SHUNT` = TODO (candidate: 20 mΩ 1 % 2 W, 2512).** Selection criterion: worst-case full-scale current × R_SHUNT × G ≤ 3.0 V so the ADC input doesn't clip below 3.3 V. Revisit when the full-stack current budget is known (Phase 5 walking load).
- **Gain: `G` ≈ 50 (TODO).** With 20 mΩ shunt → 1 mV/A at the shunt → 50 mV/A at the op-amp output. 3.0 V full scale ⇒ 60 A full-scale, which is comfortably above any load the 12× MG996R servos can draw.

**Op-amp selection (TODO).** Candidates to compare in the design-decisions log when I pick one:
- **OPA333** — zero-drift, 10 µV Vos, single supply, ~350 kHz GBW. Excellent for DC accuracy. Headline CMRR ~130 dB.
- **OPA350** — rail-to-rail, 38 MHz GBW, 150 µV Vos. Better for bandwidth than DC accuracy.
- **TLV9062** — cheap, 10 MHz, 300 µV Vos. Acceptable fallback if the BOM needs trimming.

The pick is an explicit trade-off between **DC accuracy (Vos, drift)** and **bandwidth**. For a 10 Hz firmware sampling rate, bandwidth is never the binding constraint, so OPA333's DC numbers win. This trade will be documented as an ADR when finalised.

**Resistor matching and CMRR.** CMRR of a 4-resistor diff amp is dominated by resistor matching, not by the op-amp:

```
CMRR_diff_amp  ≈  (1 + G) / (4 · tol)
```

With `tol = 0.1 %` (matched 0.1 % thin-film) and `G = 50`: CMRR ≈ (51) / (0.004) ≈ 12,750 → ~82 dB. With `tol = 1 %`: drops to ~62 dB. **Target: ≥ 60 dB measured.** Use 0.1 % 25 ppm/°C thin-film resistors in a 2-pack matched array (e.g. Vishay MORN series) rather than four independent 0.1 % parts where available — matching is better than absolute tolerance suggests.

**Bandwidth / filter.** A single-pole RC low-pass at the op-amp output (`f_c` ≈ 100 Hz — well above the 10 Hz sample rate, well below any switching noise) both limits aliasing into the STM32 ADC and bounds the measurement bandwidth. `R_filt` sits in series with the ADC input and forms the pole with a small COG cap to GND.

**Routing rules (non-negotiable).**
1. Kelvin-sense traces leave the shunt from the pad centre, not the pad edge. They route as a tight differential pair, equal length, over a solid reference.
2. The shunt is placed on the load side of the reverse-polarity FET and **before** the INA226 shunt so both sensors see the same current (they can share the same shunt if layout permits — TODO: decide shared vs separate).
3. Op-amp supply pin decoupled with 100 nF directly at the pin, 10 µF bulk within 10 mm.
4. Output filter cap referenced to the same ground star point as the op-amp V− rail.
5. `R1`/`R2` matched pairs placed symmetrically and as close together as routing allows.

**Solder-jumper fallback.** The block's input, output, and supply are each brought to 0 Ω solder jumpers on the top layer, so the entire block can be depopulated if it is the root cause of any Phase 4 bring-up issue. **The analog showcase block must NOT be able to gate the Phase 4 exit criterion.**

**Validation protocol (extends `docs/09-test-and-validation.md` integration table).**
1. Stationary load sweep on the bench PSU (0.1 A, 0.5 A, 1.0 A, 2.0 A, 3.0 A), log both the INA226 reading and the ADC-sampled showcase output.
2. Compute: residual vs INA226 (expect ≤ 5 % at each point), offset at 0 A (expect ≤ ±5 mV referred to output), temperature sweep (if time permits).
3. Deliberate common-mode injection: float the shunt ground by 100 mV via a series resistor in the ground return and confirm the showcase output does not shift more than what the measured CMRR predicts. **This is the most interview-relevant single measurement on the whole board.**

**Firmware interface.** Two ADC channels are reserved in the I/O budget above: one for V_OUT, one for a bias / reference sanity-check point. The `analog_showcase.c` driver samples at 10 Hz and publishes `analog_showcase_ua` in the telemetry frame next to the INA226 `shunt_ua` for direct comparison on the Pi-side logger.

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
5V_IN ──(Reverse-polarity FET + fuse)── 5V_RAIL ──┬── INA226 (shunt)            ───┐
                                                  │                                 ├── 5V (load)
                                                  └── Discrete current-sense block ─┘
                                                          (shunt + diff amp,
                                                           ADR-0008 / § F)
                                                              │
                                                              └── LDO ── 3.3V_RAIL ── STM32 + sensors
```

> TODO: decide whether the INA226 and the discrete block share a single shunt (saves a part, simplifies layout, makes the comparison apples-to-apples) or use independent shunts (better isolation, costs an extra 2512 part). Document the choice in a follow-up ADR.

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
