# 10 — Design Decisions Log

ADR-style log. Each entry: date, decision, context, alternatives considered, rationale.

The goal is to remember **why** something was chosen so future-me can revisit choices on real evidence rather than gut feel.

---

## ADR-0001 — Project re-framing as a sensing platform
**Date:** 2026-04-09
**Decision:** Re-position spyderrobot from "12-servo quadruped that performs spider motion" to "sensorised quadruped platform for remote environmental awareness and robot-state monitoring."
**Context:** The original framing showcased mechanical / motion-control work but did not foreground the embedded / PCB / sensor-integration skills that match the job pipeline (ADI, Qualcomm, GE Vernova, KAIST).
**Alternatives:**
1. Keep the original framing → does not address the CV gap.
2. Pivot to autonomous navigation → far too large in scope.
3. Reframe as a sensing platform with a custom MCU board (chosen).
**Rationale:** The pivot uses hardware I already own, builds on the existing mechanical work without removing it, and produces evidence of exactly the skills I need.

---

## ADR-0002 — Option A architecture (PCA9685 stays off-board in v1)
**Date:** 2026-04-09
**Decision:** v1 custom PCB does not integrate the PCA9685 servo driver. PCA9685 stays as an external module driven by the Pi 5.
**Context:** Trying to put everything on the v1 board increases complexity, risk of bring-up failures, and time to first working prototype.
**Alternatives:**
1. Integrate PCA9685 on v1 board → more impressive single board, but much higher risk and longer turnaround.
2. Keep PCA9685 external in v1, integrate in v2 (chosen).
**Rationale:** v1 must be finishable. v2 can extend it once v1 is proven. This is the standard "make it work, then make it better" pattern.

---

## ADR-0003 — STM32 over RP2350
**Date:** 2026-04-09
**Decision:** Use STM32 (G4 or F4 family) for the custom MCU board.
**Context:** Need to pick the MCU before starting PCB layout.
**Alternatives:**
1. STM32 G4/F4 — industry standard, mature toolchain, strong CV signal (chosen).
2. RP2350 — cheaper, dual-core, modern; weaker signal for industry roles I'm targeting.
3. ESP32 — has WiFi but I don't need WiFi on the MCU (Pi handles comms).
**Rationale:** STM32 maps directly to the kinds of roles in my job pipeline. CubeIDE / CubeMX / HAL is industry-standard tooling. Reusable knowledge.

---

## ADR-0004 — UART as primary Pi↔MCU link
**Date:** 2026-04-09
**Decision:** Pi 5 talks to the custom MCU board over UART with a framed protocol (sync bytes + length + payload + CRC16).
**Context:** Need a simple, robust, scope-able link.
**Alternatives:**
1. UART (chosen)
2. I²C — Pi as master, MCU as slave; messy when MCU wants to push asynchronous events
3. SPI — fast but adds chip-select / clock-line complexity
4. USB CDC — overkill for v1, fine for v2
**Rationale:** UART is dead-simple to debug with a logic analyser, and 115200–921600 baud is plenty for the planned telemetry rate. Can be revisited if throughput becomes the bottleneck.

---

## ADR-0005 — Waive Phase 1 30-minute endurance criterion
**Date:** 2026-04-09
**Decision:** Remove the "≥ 30 min uninterrupted" endurance requirement from the Phase 1 exit criterion. Phase 1 is closed on functional correctness alone — the drivers return plausible values, the OLED renders the live readings, the fault log has been exercised, and a representative CSV slice is committed.
**Context:** The original Phase 1 exit list inherited a "30-minute uninterrupted run" item from a generic bring-up checklist. On reflection, that criterion is the wrong thing to verify at this stage: Phase 1 is a one-evening bench proof-of-concept on a breadboard with jumper-wire connections. A 30-minute run on that rig proves nothing that isn't already evident from the first few minutes, because the failure modes an endurance test is meant to catch (thermal drift on a PCB, connector vibration, power-supply sag under sustained load, memory leaks in long-running firmware) are not present in a desktop breadboard session.
**Alternatives:**
1. Keep the criterion and run it on the current breadboard → low-signal, delays Phase 1 close for no real learning.
2. Move the criterion to a later phase where it is actually meaningful (chosen).
3. Remove endurance testing from the project entirely → wrong; endurance matters once the robot walks.
**Rationale:** Endurance testing is relocated to where it carries signal:
- **Phase 5** (integration on chassis) — run the full telemetry stack for ≥ 30 min while the robot moves under joystick control. Catches loose connectors, power-rail sag under servo current draw, and cable fatigue.
- **Phase 7** (field test) — the deployment-representative endurance run, ≥ 1 session, logged end-to-end.

Phase 1 already has a real failure mode documented: the OLED column off-by-one (see `docs/11-fault-record.md`, 2026-04-09 entry), which an endurance run would **not** have caught anyway — it was caught by visual sanity-checking the first few seconds of OLED output.

---

## ADR-0006 — Remove raindrop sensor from project scope
**Date:** 2026-04-10
**Decision:** The raindrop sensor is removed entirely from the project — from the BOM, from the firmware driver list, from the PCB spec, and from the Pi telemetry code. It is not "deferred" or "optional"; it is out of scope.
**Context:** The raindrop sensor was inherited from the original sensor kit and written into the docs as "surface wetness." On reflection it does not serve the project framing. The project is a **sensorised platform for remote environmental awareness and robot-state monitoring** whose engineering deliverable is a custom MCU PCB plus sensor integration. A binary wet/dry comparator-based module:
1. Adds noise to the BOM without adding signal — it's a single-comparator breakout, not a design element I can point to in an interview.
2. Displaces an ADC channel that is better spent on a proper analog showcase block (see ADR-0008).
3. Doesn't map cleanly to any of the target job roles (ADI / Qualcomm / GE Vernova analog, embedded, sensor-systems).
**Alternatives:**
1. Keep it as an optional deferred sensor → clutters every doc with "see: disabled" footnotes for zero payoff.
2. Replace with a better wetness sensor (capacitive soil moisture, dielectric) → still off-framing; the project is about platform-state + environment, not hydrology.
3. Remove entirely (chosen).
**Rationale:** "Make it work, then make it better" also means "cut things that don't earn their place." The raindrop sensor never earned its place. Removing it shrinks the BOM, simplifies the PCB sensor block, frees the ADC, and tightens the story. The Pi driver `pi/telemetry/sensors/raindrop.py` is deleted; the `wetness:` section in `config.yaml` is removed; the `wet` and `errors_wet` CSV columns are removed from the logger.

---

## ADR-0007 — MPU9250 is the v1 end-product IMU; MPU6050 is prototype only
**Date:** 2026-04-10
**Decision:** The v1 custom PCB is designed around the **MPU9250** (9-DoF). The MPU6050 (6-DoF) used on the Phase 1 breadboard is explicitly a **prototype-only** part and is not on the v1 BOM.
**Context:** The earlier BOM listed MPU6050 in the "Prototype" column and MPU9250 in the "Target v2" column, but the docs, firmware scaffolds, and PCB sensor block kept using "MPU6050 / MPU9250" as if they were interchangeable placeholders. They are not — the MPU9250 adds a magnetometer (AK8963 die in the same package) that is essential for heading estimation, and the v1 board has to actually commit to one footprint in KiCad.
**Alternatives:**
1. Keep the board IMU-agnostic with a pin-compatible footprint → the accel/gyro pinout is compatible but the mag I²C path (AK8963 passthrough / bypass) is not, so "agnostic" is a fiction once firmware actually has to run.
2. Defer the mag to a separate HMC5883L/QMC5883 breakout → adds BOM lines and I²C addresses for no reason when the MPU9250 already packages it.
3. Target MPU9250 on v1 and keep MPU6050 as a bench prototype reference only (chosen).
**Rationale:** Heading hold is a prerequisite for any interesting platform-state work (fall detection with recovery, operator-frame telemetry, closed-loop stance). The magnetometer is the cheapest path to it. Committing to MPU9250 in the v1 schematic unblocks the PCB layout without forcing a footprint-agnostic compromise. The MPU6050 remains in `pi/telemetry/sensors/mpu6050.py` as the Phase 1 bring-up reference driver, with a docstring that explicitly notes its prototype-only status. A new `pi/telemetry/sensors/mpu9250.py` stub holds the register map + AK8963 notes and will be fleshed out in Phase 2 against the NUCLEO-F411RE.

---

## ADR-0008 — Include a discrete op-amp current-sense block on the v1 PCB as an analog-design showcase
**Date:** 2026-04-10
**Decision:** The v1 custom PCB carries a **discrete op-amp current-sense amplifier** (op-amp + matched resistors + Kelvin-sensed shunt) **in addition to** the INA226. Both measure the same rail. The INA226 is the production monitoring path; the discrete block is an analog-design showcase that proves I can reason about CMRR, matched-resistor tolerance, bandwidth, and layout — not just drop in a chip.
**Context:** The project's target job pipeline (ADI, Qualcomm analog, GE Vernova power, KAIST analog/mixed-signal) specifically rewards evidence of **transistor- and op-amp-level analog design**, not "I integrated an I²C sensor." An INA226 alone is a chip drop-in. A discrete block next to it is a portfolio piece: the PCB, the schematic, and the bench measurements become something I can point to in an interview and say "here is how I reasoned about CMRR, here is how I specced the shunt, here is the bench data where I compared my block against the INA226."

The full-stack question (*"should I design every sensor at transistor level?"*) was answered in the earlier discussion: no, it's over-budget and most modern sensors (MEMS IMU, MEMS pressure) are foundry problems that discrete design can't touch. But a **single** well-chosen discrete block — current sense — is:
1. The cheapest path to a strong analog-design signal
2. Directly comparable to a commercial part on the same board, so the results are falsifiable
3. Small enough to not threaten Phase 4 bring-up
**Alternatives:**
1. INA226 only → convenient, zero analog-design signal.
2. Discrete block for *every* sensor (IMU, env, distance, power) → infeasible; IMU and env are foundry parts, not op-amp problems.
3. Discrete block for current sense only, parallel to INA226 (chosen).
4. Discrete block instead of INA226 → loses the "calibrate-against-known-good" property that makes the showcase actually credible.
**Rationale:** One showcase block, with a named commercial reference on the same board for sanity-check, is the maximum-signal / minimum-risk configuration. The block's detailed spec (op-amp selection, resistor tolerance target, Kelvin-sense layout, bandwidth budget, bench validation protocol) lives in `docs/04-pcb-design.md` § "Analog showcase block." The firmware samples it through a reserved ADC channel at 10 Hz, alongside the INA226 readings, and the telemetry frame carries `analog_showcase_ua` next to the INA226 `shunt_ua` so the comparison can be done in post-processing on the Pi.

A v1 solder-jumper fallback lets the block be depopulated if it is the root cause of any bring-up issue, so it cannot gate the Phase 4 exit criterion.

---

## ADR-0009 — STM32F411RET6 as the v1 custom-board MCU
**Date:** 2026-04-10
**Decision:** The v1 custom MCU board uses the **STM32F411RET6** (LQFP-64, 100 MHz Cortex-M4F, 512 KB flash, 128 KB RAM). This is the identical die to the NUCLEO-F411RE development board already on order for Phase 2 bring-up.
**Context:** ADR-0003 narrowed the MCU to "STM32 G4 or F4 family" but left the exact part open. With the NUCLEO-F411RE now locked as the Phase 2 bring-up target, the v1 PCB part pick has to commit so that the CubeMX pin budget, the KiCad symbol/footprint work, and the BOM can all move forward in parallel with the Nucleo shipment.
**Alternatives:**
1. **STM32F411RET6** (LQFP-64, 512 KB flash) — identical die to the Nucleo. Firmware developed on the Nucleo in Phase 2 ports 1:1 to the custom board in Phase 4 with zero HAL changes, zero pin-map changes, zero clock-tree changes. Chosen.
2. **STM32F411CEU6** (UFQFPN-48) — same die, smaller package. Rejected: QFN is harder to hand-solder than LQFP-64's 0.5 mm-pitch gull-wing leads, and dropping 16 pins gives up breathing room for debug headers, status LEDs, and expansion that cost nothing at the LQFP-64 footprint.
3. **STM32G431RBT6** (LQFP-64, 128 KB flash) — newer family, better ADC, stronger "modern silicon" signal on a CV. Rejected for v1: a mismatch between Nucleo and custom board forces a firmware port at Phase 4 bring-up, which adds a failure mode without changing the interview story materially (a non-embedded interviewer reads "STM32F411" and "STM32G431" identically). Keep as a v2 / Phase 8 candidate.
4. **STM32F446RET6** (LQFP-64, 180 MHz, more peripherals) — same footprint as the F411RET6. Rejected: no matching Nucleo on order, introduces the same mismatch risk as (3) for capability the project does not need.
**Rationale:** The dominant trade in v1 is **de-risking Phase 4 bring-up**, not squeezing out the newest silicon. Matching the Nucleo part exactly means every line of firmware written against the dev board runs unchanged on the custom PCB: same clock tree, same HAL, same CubeMX pinout file, same DMA stream assignments. ADR-0007 already committed Phase 2 firmware to "the NUCLEO-F411RE"; this ADR just propagates that choice through Phase 3+ so the whole stack stays internally consistent.

The "newer silicon is a better CV story" argument loses on inspection: the portfolio signal comes from **what is built on top of the MCU** (discrete analog showcase, framed UART protocol, sensor integration, bring-up log), not from the model number. An F411 with a well-executed PCB and a working discrete op-amp block is a stronger artefact than a G431 with anything less.

---

## ADR-0010 — OPA333 as the analog-showcase op-amp
**Date:** 2026-04-10
**Decision:** The discrete current-sense amplifier (§ F of `docs/04-pcb-design.md`, authorised by ADR-0008) uses the **OPA333AIDBVR** (TI, SOT-23-5, single, zero-drift chopper).
**Context:** ADR-0008 enumerated OPA333 / OPA350 / TLV9062 and framed the pick as a trade between DC accuracy (V_os, drift) and bandwidth. At the 10 Hz firmware sample rate set by the telemetry frame, bandwidth is never the binding constraint, so the pick collapses to which part has the lowest input-referred DC error.
**Alternatives** (output-referred DC error at block gain G = 30, shunt 20 mΩ per ADR-0013):
1. **OPA333** — V_os,max 10 µV, TCV_os 50 nV/°C, GBW 350 kHz, I_q 17 µA, rail-to-rail I/O, 1.8–5.5 V single supply. Output offset: 10 µV × 30 = **300 µV** → input-referred **0.5 mA** static current offset. Offset drift across a 0–40 °C room sweep: 50 nV/°C × 40 × 30 = 60 µV → **0.1 mA**. Chosen.
2. **OPA350** — V_os,max 150 µV, TCV_os 4 µV/°C, GBW 38 MHz, I_q 5 mA. Output offset: 4.5 mV → **7.5 mA**. Drift over 40 °C: 4.8 mV → **8 mA**. Rejected: offset dominates the entire low-current operating regime, which is exactly the regime where the INA226 comparison has to hold up. 15× worse than OPA333 on initial offset.
3. **TLV9062** — V_os,max 300 µV, TCV_os 2 µV/°C, GBW 10 MHz, I_q 550 µA, dual channel, cheapest of the three. Output offset: 9 mV → **15 mA**. Rejected: even worse initial offset than OPA350.
**Rationale:** At G = 30 and 20 mΩ, every 1 µV of input-referred V_os becomes 50 µA of apparent current. Below the chopper-stabilised class, offset alone dominates every low-current reading and trashes the residual-vs-INA226 comparison that ADR-0008 exists to make. OPA333's 10 µV V_os gives ≤0.5 mA static offset, which is under the INA226 LSB at its default PGA setting — so the residual is bounded by resistor matching and CMRR, not by the op-amp, which is the analog-design story the showcase is supposed to tell.

GBW of 350 kHz is ~35 000× the 10 Hz sample rate so bandwidth is nowhere near the binding constraint. I_q of 17 µA is irrelevant to the 5 V current budget. The part is a TI jellybean, SOT-23-5, ~$2 single-unit, and is JLCPCB extended-parts stock.

**Fallback if OPA333 is unavailable at order time:** **OPA2333** (dual, same die, SOIC-8), using only one channel. Do NOT substitute OPA350 or TLV9062 — the substitution invalidates every number above.

---

## ADR-0011 — Shared shunt between INA226 and the discrete showcase
**Date:** 2026-04-10
**Decision:** The INA226 and the discrete current-sense showcase block **share a single Kelvin-sensed shunt** on the 5 V rail. Two independent differential pairs leave the shunt Kelvin pads — one pair to the INA226 inputs, one pair to the OPA333 diff-amp inputs.
**Context:** `docs/04-pcb-design.md` flagged "shared vs separate shunt" as a pending decision in two places. ADR-0008 specified that the discrete block exists to be **directly comparable** to the INA226 on the same board, and a shared shunt is the only topology where the comparison is apples-to-apples by construction.
**Alternatives:**
1. **Shared shunt (chosen).** Both sensors see literally the same current through the same physical element. The residual (discrete reading − INA226 reading) contains only topology and op-amp error, with zero contribution from current-path mismatch. Costs: four sense traces must leave the Kelvin pads of a single shunt instead of two — tighter layout, but manageable.
2. **Separate shunts, values matched from the same tape reel.** Slightly cleaner layout (two independent diff pairs, no crowding at the shunt), but introduces an RSS uncertainty of √(tol₁² + tol₂²) ≈ 1.4 % for 1 % parts (≈0.14 % for 0.1 %). That uncertainty lands directly inside the residual and has to be backed out of any comparison, and worse, gives the discrete block a built-in excuse — "it's resistor mismatch, not my circuit" — that weakens the interview story.
3. **Each block on its own current path** (e.g. discrete block on the 3.3 V branch only). Defeats the point of ADR-0008 entirely; the two blocks would measure different things and the residual would be physically meaningless.
**Rationale:** The showcase's credibility depends on the two measurements being apples-to-apples **by physics**, not by component matching. The layout constraint (four traces off one shunt's Kelvin pads) is real but bounded: place the shunt in a clear keep-out with the INA226 on one side and the OPA333 on the other, each with its own tight differential pair over the continuous inner ground plane enabled by ADR-0012. ADR-0008 § "Routing rules" already demands Kelvin routing and a tight differential pair; sharing simply adds a second pair to the same routing budget.

**Layout fallback if DRC cannot close on the shared topology:** two 20 mΩ shunts ordered from the same tape reel (same tolerance bin, same lot, same temperature coefficient), with the match caveat documented explicitly in the residual write-up and flagged in `docs/11-fault-record.md`.

---

## ADR-0012 — 4-layer PCB stack (SIG / GND / PWR / SIG)
**Date:** 2026-04-10
**Decision:** v1 custom MCU board is built on a **4-layer stack** at JLCPCB: top SIG, inner GND plane, inner PWR plane, bottom SIG. 2-layer is not considered further.
**Context:** `docs/04-pcb-design.md` "Layer stack (TODO)" flagged 2-layer vs 4-layer as a pending call. JLCPCB pricing for a 5-off 100 × 100 mm run: 2-layer ≈ $2, 4-layer ≈ $5–30 depending on active promo. For a single prototype run the delta is small in absolute terms and negligible against the rest of the project cost.
**Alternatives:**
1. **2-layer.** Cheapest. Adequate for a pure-digital STM32 + I²C sensors board. Fatal flaw for v1: the board carries a deliberate analog showcase block whose CMRR budget and Kelvin-sense routing depend on a solid, uninterrupted ground reference under the differential pair. On 2-layer, the bottom layer is both the ground pour and the return-trace plane, creating loop area and ground bounce that couple directly into the diff-amp inputs and invalidate any measured CMRR number.
2. **4-layer SIG / GND / PWR / SIG (chosen).** Dedicated inner GND plane gives a continuous reference under every top-layer trace. The Kelvin-sense differential pair from the shunt to the OPA333 inputs can run over unbroken ground for its entire length. Inner PWR plane gives low-impedance power distribution and implicit supply decoupling. Standard JLCPCB stack-up.
3. **4-layer SIG / PWR / GND / SIG.** Puts power directly under the top signals, slightly worse for EMI. Rejected.
4. **4-layer SIG / GND / GND / SIG.** Double ground plane, ultra-clean, but the 5 V power distribution would then rely on surface-layer pours only, which is worse for the 2–5 A Pi power path this board is in (see ADR-0013). Rejected for v1.
**Rationale:** This is the decision that most directly underwrites the credibility of the analog showcase. On 4-layer with a dedicated GND plane, the differential pair from the shunt Kelvin pads to the OPA333 inputs runs over solid ground for its entire length, and the measured CMRR can be honestly compared to the theoretical `(1 + G) / (4 · tol)` bound. On 2-layer, any CMRR number the board produces comes with an implicit asterisk. For a board whose entire *purpose* is a falsifiable analog measurement, paying the upcharge to remove that asterisk is free.

Secondary benefit: the Pi + board 5 V distribution path (ADR-0013) gets a continuous inner PWR plane as its main conductor rather than a wide surface trace, reducing IR drop at 2–5 A and making the FET + shunt thermal dissipation easier to route.

---

## ADR-0013 — Custom board sits in the Pi 5 V power path (not the servo rail)
**Date:** 2026-04-10
**Decision:** The v1 custom PCB is the **power entry point for the Raspberry Pi 5 V rail**. External 5 V (from the battery-side buck) enters the custom board at the 5V_IN header, passes through reverse-polarity protection and the shared Kelvin shunt (ADR-0011), and leaves via a 2-pin header to the Pi 5's 40-pin 5 V / GND pins. The board is **not** in the servo power path — the PCA9685 is fed directly from the battery-side buck and its servo current never crosses the custom board.
**Context:** ADR-0008 specified that the analog showcase measures "worst-case full-scale current" but deferred the actual number to "Phase 5 walking load," and its draft math ("≈60 A full scale") implicitly assumed the shunt was in the full servo rail. With ADR-0011 now committing to a shared shunt, the shunt value and op-amp gain have to be pinned down — which requires committing to exactly what current the shunt sees. ADR-0002 (PCA9685 off-board in v1) rules out the servo-rail assumption, and running 24+ A of servo current through the custom board anyway would put the Phase 4 bring-up story on much thinner ice than the rest of the project.
**Alternatives** (the shunt sees…):
1. **Custom board only (~70 mA typical).** Safe. Trivial trace widths. But the shunt reads the same few tens of mA forever, the ADC dynamic range is wasted, and the ADR-0008 bench validation sweep (0.1 / 0.5 / 1 / 2 / 3 A) becomes untriggerable at a bench station. Rejected as under-reach.
2. **Pi + custom board (~2–3 A typical, ~5 A boot/USB-host peak) (chosen).** Pi 5 is documented drawing 2–3 A sustained and up to 5 A peak on its 5 V rail. Powering the Pi via the 5 V pins on the 40-pin header is a Raspberry Pi-supported path, provided the feed is clean ≥ 5 A-capable 5 V. This current range exercises the ADC to ~60 % of full scale at typical Pi load and hits full scale at boot peaks — exactly the range the ADR-0008 validation sweep is designed for.
3. **Full robot rail including servo current (~0–24 A, stall peaks far higher).** Matches the original ADR-0008 draft math but forces the v1 board to carry tens of amps of switching servo current through its 4-layer copper, plus the FET, plus the shunt — heavy copper, 100-mil+ traces, thermal design that directly gates Phase 4 bring-up. And because PCA9685 is off-board (ADR-0002), a "servo-rail pass-through" topology saves no wiring, it only adds a failure mode. Rejected as over-reach for v1. Revisit for v2 / Phase 8, which is when ADR-0002 says PCA9685 moves on-board — *that* is the right phase to own the servo rail.
**Rationale:** The 2–5 A Pi power range is the sweet spot: meaningful enough that the bench sweep produces credible residual-vs-INA226 numbers, and low enough that trace-width / FET / shunt sizing stays comfortable on a first-spin 4-layer board without exotic copper weight.

**Locked component values downstream of this decision:**
- **Shunt:** R_SHUNT = **20 mΩ, 1 %, 2 W, 2512** (Vishay WSL2512 family).
- **Gain:** G = **30** (R1 = 1 kΩ, R2 = 30 kΩ, 0.1 % thin-film matched pairs). Replaces the `G ≈ 50` placeholder in ADR-0008 / § F.
- **Full-scale current** at the 3.0 V ADC headroom limit: `3.0 V / (30 × 20 mΩ) =` **5.0 A**.
- **ADC LSB** (12-bit, 3.3 V V_ref): `0.806 mV / (30 × 20 mΩ) ≈` **1.34 mA / LSB**.
- **Theoretical CMRR** at 0.1 % matched resistors: `(1 + 30) / (4 × 0.001) ≈` **77 dB**. Target measured: ≥ 60 dB (unchanged from ADR-0008).
- **Shunt dissipation** at 5 A full scale: `5² × 0.02 =` **0.5 W** (25 % of 2 W part rating, comfortable thermal margin).
- **Reverse-polarity FET:** P-channel, R_ds(on) ≤ 15 mΩ at V_gs = 4.5 V. Candidates: SiA457DJ (6.5 mΩ, PowerPAK 1212-8), DMP3056L-7 (35 mΩ — borderline, secondary choice).
- **Worst-case Pi-side 5 V at 5 A peak:** `5.00 V − 75 mV (FET) − 100 mV (shunt) − 30 mV (trace) =` **4.80 V**, inside the Pi 5 minimum of 4.75 V. Tight; a lower-R_ds(on) FET moves this comfortably to ≥ 4.85 V and is preferred.

**Firmware implication:** the ADR-0008 / § F plan for two reserved ADC channels (V_out + reference-sanity) stands. The `analog_showcase_ua` telemetry field now carries a 0–6 000 mA range at ~1.34 mA LSB quantisation.

**Phase 4 bring-up risk:** the Pi now depends on the custom board for power, so a failure on the protection/sense block means the Pi will not boot from battery. The ADR-0008 solder-jumper fallback is **extended**: a 0 Ω bypass jumper must be placed across the series (FET + shunt) path so the 5 V can be restored to direct 5V_IN → Pi if the protection block is the root cause of a bring-up issue. This bypass jumper is populated 0 Ω at assembly and cut *only* after the protection block has been validated end-to-end. Document the cut in `docs/11-fault-record.md` when it happens.

---

## Template for new entries

```
## ADR-XXXX — <short title>
**Date:** YYYY-MM-DD
**Decision:** <one sentence>
**Context:** <why was this even a question>
**Alternatives:** <bulleted list>
**Rationale:** <why this won>
```

> Add new entries at the bottom. Never edit historical entries — append a follow-up ADR if a decision changes.
