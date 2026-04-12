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
              WSK2512  (4-terminal Kelvin shunt, diagonal pad arrangement)
              Pin layout (top view):    I2 ←──────── E1
                                        E2 ──────────► I1

     5V_RAIL ─────► I2 (current in, pad 1)          I1 (current out, pad 4) ──► 5V_LOAD
                    E2 (sense+, pad 2)               E1 (sense−, pad 3)
                         │                                │
                         ├────── branch ──────────────────┤
                         │                │               │
                    ┌────┘        ┌───────┘       ┌───────┘
                    ▼             ▼               ▼
                  INA226       OPA333           INA226
                   IN+         sense+            IN−       ◄── I²C path
                               sense−
                                 │
                                 ▼
                   R1           R1    (matched, 0.1 % — gain-setting high side)
                    │            │
                    ├────────────┼────── V+ ──┐
                    │            │            │
                   R2           R2            │  OPA333 (SOIC-8, ADR-0014)
                    │            │            │  zero-drift, single 3.3 V supply
                    │            │            │
                   GND          GND ── V− ────┘
                                              │
                                            V_OUT ──► STM32 ADC
```

The WSK2512 has current (I1, I2) and sense (E1, E2) pads on **opposite diagonal corners** — not inline like the WSLP. Both INA226 and the OPA333 difference amplifier tap the **same sense pair** (E1, E2). The branch happens as physically close to the sense pads as the layout allows so the two downstream devices see geometrically identical Kelvin taps — this is what makes the residual comparison apples-to-apples (preserved from ADR-0011).

- **Topology: classic difference amplifier** (4-resistor instrumentation-style). Matched pairs `R1` and `R2` set the gain `G = R2/R1`. Output referred to GND for a single-supply op-amp.
- **Input: true Kelvin sense, enforced by the part.** The shunt is a **4-terminal Kelvin** package (Vishay WSK series, [ADR-0015](10-design-decisions.md#adr-0015--wsk2512-4-terminal-kelvin-shunt-supersedes-the-wsl2512-part-choice-in-adr-0011--0013)) — two diagonal "current" pads (I1, I2) carry the load current, two opposite-corner "voltage" pads (E1, E2) tap the voltage drop directly across the resistive element. The Kelvin commitment is in the part geometry, not in the layout. The shared sense pair branches to both INA226 and OPA333 inputs at the sense pads.
- **Shunt:** `R_SHUNT` = **20 mΩ, 1 %, 1 W, 2512, 4-terminal Kelvin** (Vishay **WSK2512R0200FEA**). Locked by [ADR-0013](10-design-decisions.md#adr-0013--custom-board-sits-in-the-pi-5-v-power-path-not-the-servo-rail) for the topology, refined by [ADR-0015](10-design-decisions.md#adr-0015--wsk2512-4-terminal-kelvin-shunt-supersedes-the-wsl2512-part-choice-in-adr-0011--0013) for the part. Pi 5 V rail expected current 2–3 A typical, 5 A peak. Dissipation at 5 A full scale: `5² × 0.02 = 0.5 W` (50 % of 1 W rating, ample headroom). KiCad: symbol `Device:R_Shunt`, footprint `Resistor_SMD:R_Shunt_Vishay_WSK2512_6332Metric_T1.19mm`.
- **Gain:** G = **30** (R1 = 1 kΩ, R2 = 30 kΩ, 0.1 % thin-film matched pairs). With 20 mΩ shunt: `0.6 V/A` at the op-amp output. **Full-scale current at the 3.0 V ADC headroom limit = 5.0 A** (matches the Pi 5 boot/USB-host peak). ADC LSB at 12-bit, 3.3 V V_ref: `0.806 mV / (30 × 20 mΩ) ≈ 1.34 mA / LSB`. The earlier `G ≈ 50` placeholder is superseded by this calculation; see ADR-0013 for the full derivation.

**Op-amp selection — locked: OPA333AID** (TI, **SOIC-8**, single, zero-drift chopper). See [ADR-0010](10-design-decisions.md#adr-0010--opa333-as-the-analog-showcase-op-amp) for the electrical trade-off and [ADR-0014](10-design-decisions.md#adr-0014--opa333-package-deviates-to-soic-8-for-v1-build-follow-up-to-adr-0010) for the package deviation from the originally-specified SOT-23-5. Same die, easier hand-assembly and bench probing. Headline numbers at G = 30:
- **V_os 10 µV** → 300 µV output offset → **0.5 mA** static current offset (under the INA226 LSB at default PGA, so the op-amp does not bound the residual).
- **TCV_os 50 nV/°C** → ≈ 0.1 mA drift over a 0–40 °C bench sweep.
- **GBW 350 kHz**, ~35 000× the 10 Hz sample rate — bandwidth is not the binding constraint.
- I_q 17 µA, rail-to-rail I/O, single 1.8–5.5 V supply.

**Fallback:** OPA2333 (dual, same die, SOIC-8) using only one channel. **Do not** substitute OPA350 or TLV9062 — those introduce 7–15 mA static offset that invalidates the residual-vs-INA226 comparison.

**Resistor matching and CMRR.** CMRR of a 4-resistor diff amp is dominated by resistor matching, not by the op-amp:

```
CMRR_diff_amp  ≈  (1 + G) / (4 · tol)
```

With `tol = 0.1 %` (matched 0.1 % thin-film) and `G = 30` (locked by ADR-0013): CMRR ≈ 31 / 0.004 ≈ 7 750 → **~78 dB**. With `tol = 1 %`: drops to ~58 dB. **Target: ≥ 60 dB measured.** Use 0.1 % 25 ppm/°C thin-film resistors in a 2-pack matched array (e.g. Vishay MORN / Susumu RM3216 matched-pair series) rather than four independent 0.1 % parts where available — matching tracks better than absolute tolerance suggests, especially over temperature.

**Bandwidth / filter.** A single-pole RC low-pass at the op-amp output (`f_c` ≈ 100 Hz — well above the 10 Hz sample rate, well below any switching noise) both limits aliasing into the STM32 ADC and bounds the measurement bandwidth. `R_filt` sits in series with the ADC input and forms the pole with a small COG cap to GND.

**Routing rules (non-negotiable).**
1. The shunt's **sense pair branches happen as close to the WSK2512 sense pads as physically possible**, with equal trace lengths from the branch point to the INA226 inputs and to the OPA333 inputs. The Kelvin connection itself is enforced by the part geometry ([ADR-0015](10-design-decisions.md#adr-0015--wsk2512-4-terminal-kelvin-shunt-supersedes-the-wsl2512-part-choice-in-adr-0011--0013)) — the layout's job is to preserve symmetry between the two downstream devices, not to create the Kelvin tap.
2. The shunt is placed on the load side of the reverse-polarity FET. **The INA226 and the discrete block share this single shunt** (locked by [ADR-0011](10-design-decisions.md#adr-0011--shared-shunt-between-ina226-and-the-discrete-showcase)). Both devices tap the same sense pair at the same physical point, so the residual is purely topology error with zero current-path mismatch.
3. Sense pair routes as a tight differential pair over a solid GND reference (L2), equal length, no via-stitched gaps.
4. Op-amp supply pin decoupled with 100 nF directly at the pin, 10 µF bulk within 10 mm.
5. Output filter cap referenced to the same ground star point as the op-amp V− rail.
6. `R1`/`R2` matched pairs placed symmetrically and as close together as routing allows.

**Solder-jumper fallback.** The block's input, output, and supply are each brought to 0 Ω solder jumpers on the top layer, so the entire block can be depopulated if it is the root cause of any Phase 4 bring-up issue. **The analog showcase block must NOT be able to gate the Phase 4 exit criterion.**

**Validation protocol (extends `docs/09-test-and-validation.md` integration table).**
1. Stationary load sweep on the bench PSU (0.1 A, 0.5 A, 1.0 A, 2.0 A, 3.0 A), log both the INA226 reading and the ADC-sampled showcase output.
2. Compute: residual vs INA226 (expect ≤ 5 % at each point), offset at 0 A (expect ≤ ±5 mV referred to output), temperature sweep (if time permits).
3. Deliberate common-mode injection: float the shunt ground by 100 mV via a series resistor in the ground return and confirm the showcase output does not shift more than what the measured CMRR predicts. **This is the most interview-relevant single measurement on the whole board.**

**Firmware interface.** Two ADC channels are reserved in the I/O budget above: one for V_OUT, one for a bias / reference sanity-check point. The `analog_showcase.c` driver samples at 10 Hz and publishes `analog_showcase_ua` in the telemetry frame next to the INA226 `shunt_ua` for direct comparison on the Pi-side logger.

## I/O budget (STM32F411RET6, LQFP-64 — locked by ADR-0009)

Paper pin budget. To be validated in CubeMX against the Phase 2 NUCLEO-F411RE before KiCad schematic capture begins — no silicon validation yet.

| Signal | Pin | AF | Peripheral | DMA | Notes |
|---|---|---|---|---|---|
| HSE_IN | PH0 | — | RCC | — | 8 MHz crystal, dedicated oscillator pin |
| HSE_OUT | PH1 | — | RCC | — | 8 MHz crystal, dedicated oscillator pin |
| NRST | NRST | — | — | — | 10 kΩ pull-up + 100 nF + momentary button |
| BOOT0 | BOOT0 | — | — | — | jumper to GND (run) / V_DD (bootloader) |
| SWDIO | PA13 | AF0 | SYS | — | SWD header |
| SWCLK | PA14 | AF0 | SYS | — | SWD header |
| USART1_TX | PA9 | AF7 | USART1 | DMA2_Stream7_Ch4 | Pi UART uplink |
| USART1_RX | PA10 | AF7 | USART1 | DMA2_Stream2_Ch4 | Pi UART downlink |
| I2C1_SCL | PB8 | AF4 | I2C1 | — | sensor bus, 4.7 kΩ pull-up to 3.3 V |
| I2C1_SDA | PB9 | AF4 | I2C1 | — | sensor bus, 4.7 kΩ pull-up to 3.3 V |
| HC-SR04 TRIG | PA5 | — | GPIO_OUT | — | push-pull, 10 µs pulse in software |
| HC-SR04 ECHO | PA6 | AF2 | TIM3_CH1 | — | input capture, 3.3 V side of level shifter |
| Analog showcase V_OUT | PA0 | — | ADC1_IN0 | DMA2_Stream0_Ch0 | OPA333 output (see ADR-0010, § F) |
| Analog showcase V_REF | PA1 | — | ADC1_IN1 | same | bias / reference sanity channel |
| Status LED — heartbeat | PC6 | — | GPIO_OUT | — | 470 Ω → LED → GND, 1 Hz toggle |
| Status LED — telemetry activity | PC7 | — | GPIO_OUT | — | toggles on every UART frame sent |
| Status LED — error / fault | PC8 | — | GPIO_OUT | — | asserted on any sensor or frame fault |

**Pin count.** 12 user I/O (I²C + UART + timer capture + ADC + GPIO) + 3 status LEDs + 4 debug/clock (SWD + HSE) + 2 reset/boot = 21 pins committed. F411RET6 exposes 50 GPIO on LQFP-64, so ~58 % of the I/O count is headroom for expansion headers, extra sensors, or Phase-2 surprises.

**DMA conflict check.** USART1 uses DMA2 streams 2 and 7; ADC1 uses DMA2 stream 0. The stream indices are disjoint — no conflict. TIM3 input capture can run off DMA1 if capture rate demands it, but the HC-SR04 round-trip cadence is ~50 Hz and a capture-compare interrupt is cheaper than enabling a DMA stream for it. Plan: no DMA on TIM3.

**Bootstrap pin check.** STM32F411 selects boot mode from BOOT0 + an option byte only; PB2 (BOOT1 on some other STM32 parts) is a free GPIO on F411 and is not used in this budget either way. PA13 / PA14 are reserved for SWD and MUST NOT be reassigned. No other pin in the budget above collides with alternate boot paths.

**Alternate-function source.** All AF numbers above are from the STM32F411xC/xE datasheet (DS10314) Table 9 "Alternate function mapping." Validate in CubeMX before committing to schematic — if CubeMX flags any conflict, update this table and the ADR trail, don't silently rework the schematic.

> **Phase 2 task:** create the CubeMX `.ioc` file for this exact allocation against the NUCLEO-F411RE, save it to `firmware/cubemx/spyder-v1.ioc`, and verify zero pinmux or DMA conflicts. Only then proceed to schematic capture.

## Power tree on the board

The custom board sits **in the Pi 5 V power path** ([ADR-0013](10-design-decisions.md#adr-0013--custom-board-sits-in-the-pi-5-v-power-path-not-the-servo-rail)) and uses a **single shared 4-terminal Kelvin shunt** for both the INA226 and the discrete showcase block ([ADR-0011](10-design-decisions.md#adr-0011--shared-shunt-between-ina226-and-the-discrete-showcase) + [ADR-0015](10-design-decisions.md#adr-0015--wsk2512-4-terminal-kelvin-shunt-supersedes-the-wsl2512-part-choice-in-adr-0011--0013)).

```
                  ┌── 0Ω bypass jumper (cut after Phase 4 protection-block validation) ──┐
                  │                                                                        │
5V_IN ──┬─────────┴─[ P-FET ]──[ WSK2512 20 mΩ ]──┬─────────────────────────────────────┴──── 5V_RAIL ──┬── Pi 5 (40-pin header, 5V/GND)
        │           reverse-pol    I2        I1    │                                                       │
        │           protection     E2        E1    │                                                       ├── HC-SR04 (5 V VCC)
        │                          │         │     │                                                       │
        │                          ├──┬──────┼──┬──┤                                                       └── LDO (MCP1700-3302) ── 3V3_RAIL ──┬── STM32F411
        │                          │  │      │  │  │                                                                                             ├── MPU9250
        │                          ▼  ▼      ▼  ▼  │                                                                                             ├── BME280
        │                       INA226     OPA333  │                                                                                             ├── INA226 V_S
        │                       IN+/IN−    + R1/R2 │                                                                                             └── OPA333 V+ (SOIC-8)
        │                          │      diff amp │
        │                          │         │     │
        │                          │         ▼     │
        │                          │   ADC1_IN0 (V_OUT)
        │                          │   ADC1_IN1 (V_REF)
        │                          │         │     │
        │                          ▼         ▼     │
        │                       I²C1 SDA/SCL ◄─────┘
        └─────────────────────────────────────────────
                                       (GND return — inner GND plane L2, ADR-0012)
```

`I1`/`I2` are the WSK2512 current pads (force, load current); `E1`/`E2` are the voltage sense pads (Kelvin tap). Current and sense pads sit on **opposite diagonal corners** per the WSK2512 package. The single sense pair branches to **both** INA226 inputs and **both** OPA333 inputs at the sense pads, so the residual comparison sees a geometrically identical Kelvin tap on both sides ([ADR-0011](10-design-decisions.md#adr-0011--shared-shunt-between-ina226-and-the-discrete-showcase) topology, [ADR-0015](10-design-decisions.md#adr-0015--wsk2512-4-terminal-kelvin-shunt-supersedes-the-wsl2512-part-choice-in-adr-0011--0013) part).

**Key features captured by this diagram:**
- 5V_IN comes from an external buck on the battery side (out of scope for v1 PCB; lives on the order tracker in `docs/03-hardware-bom.md`).
- The full 2–5 A Pi 5 current crosses the shunt, giving the analog showcase a meaningful current range to measure.
- Servo current is **not** in this path — PCA9685 is fed directly from the buck (ADR-0002).
- The `0 Ω bypass jumper` across the (FET + shunt) series block is the Phase 4 bring-up safety net mandated by ADR-0013: cut only after the protection block is validated.
- **JP1 layout rule:** the bypass trace must be **short and wide** (≥ 1 mm / 40 mil, matching the main 5 V power pour width). The Q1 + R_SHUNT series path is ~32 mΩ (12 mΩ Rds(on) + 20 mΩ shunt); a long thin JP1 trace could exceed this and defeat the bypass. When JP1 is the sole power path (Phase 1–3, Q1 not yet validated), it carries the full load current (up to 3 A).
- The 3.3 V LDO supplies only the on-board STM32 + sensors (~50 mA peak); the Pi has its own internal regulators on the 5 V → 3.3 V/1.8 V/etc. path.

## Layer stack — locked: 4-layer SIG / GND / PWR / SIG

Locked by [ADR-0012](10-design-decisions.md#adr-0012--4-layer-pcb-stack-sig--gnd--pwr--sig). JLCPCB standard 4-layer 1.6 mm stack-up.

| Layer | Function | Notes |
|---|---|---|
| L1 (top) | Signals | All component placement; analog showcase block on the analog side, digital on the other |
| L2 | GND plane | Continuous, unbroken under the Kelvin-sense differential pair from the shunt to the OPA333 inputs |
| L3 | PWR plane | 5 V on one half, 3.3 V on the other, single split with no signals crossing the boundary |
| L4 (bottom) | Signals | Routing escape, mostly digital; no analog returns here |

**Why this and not the alternatives:** the analog showcase block's measured CMRR depends on a solid ground reference under the differential pair. On 2-layer, any CMRR number comes with an asterisk and the showcase loses its credibility — see ADR-0012 for the full reasoning. The PWR plane on L3 also gives the 5 V Pi-power path (ADR-0013) a low-impedance distribution conductor that handles 5 A peaks comfortably without surface-trace heroics.

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
