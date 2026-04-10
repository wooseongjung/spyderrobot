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
