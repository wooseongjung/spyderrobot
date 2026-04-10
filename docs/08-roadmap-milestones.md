# 08 — Roadmap & Milestones

Each phase has a clear **deliverable** and **exit criterion**. A phase is "done" only when its exit criterion is checked off.

## Phase 0 — Repo restructure & documentation
**Deliverable:** Updated README, `docs/` folder, scaffold folders pushed to GitHub on a feature branch and merged via PR.
**Exit criterion:**
- [ ] README rewritten, original 1-liner preserved
- [ ] `docs/01..12` files in place as outlines
- [ ] `hardware/`, `firmware/`, `pi/`, `assets/` scaffold folders exist with stub READMEs
- [ ] `spider/` ROS package untouched (verified by `git diff main -- spider/` → empty)
- [ ] Branch merged to `main`

## Phase 1 — Breadboard prototype (Pi-only, IMU + env + display)
**Goal:** Prove the I²C path and a non-trivial sensor work end-to-end on the Pi before introducing the MCU.
**In scope:** MPU6050 (IMU, I²C), DHT11 (temp/humidity, 1-wire), SSD1306 OLED (I²C, shares the bus with the MPU6050).
**Out of scope (deferred to Phase 2 / STM32):** HC-SR04 ultrasonic (needs 5 V → 3.3 V level shift on ECHO). Its driver scaffold remains in `pi/telemetry/sensors/` but is disabled in `config.yaml`.
**Wiring cheat sheet:** [`phase1-wiring.md`](phase1-wiring.md)
**Deliverable:** Pi 5 reads MPU6050 + DHT11 directly via Python, logs to CSV, OLED shows live values.
**Exit criterion:**
- [x] MPU6050 and DHT11 return plausible values end-to-end (gravity magnitude within 1 % of 1 g; env readings match a room thermometer). **30-min endurance run waived** — see [ADR-0005](10-design-decisions.md#adr-0005--waive-phase-1-30-minute-endurance-criterion) — the endurance test is relocated to Phase 5 (integration on chassis) and Phase 7 (field test) where it carries more signal.
- [x] CSV log committed under `pi/telemetry/sample_data/`
- [x] OLED displays IMU + env temp + env humidity (see `pi/telemetry/display.py`)
- [x] Photo of breadboard rig in `assets/images/phase1-breadboard.jpg`
- [x] Notes added to `docs/11-fault-record.md` (OLED column off-by-one entry, 2026-04-09)

## Phase 2 — MCU firmware on STM32 dev board
**Goal:** Move the sensor frontend off the Pi and onto a real MCU, with a framed UART link.
**Deliverable:** STM32 Nucleo runs firmware that polls IMU + environmental sensor + ultrasonic and streams frames to the Pi over UART. Pi-side parser logs them.
**Exit criterion:**
- [ ] Firmware builds clean (`-Wall -Wextra`), flashes to Nucleo
- [ ] Telemetry frames stream at ≥ 10 Hz with CRC validation passing on Pi
- [ ] No frame drops over a 30 min run
- [ ] Frame format documented in `docs/05-firmware-architecture.md`
- [ ] First-cut Pi parser committed to `pi/telemetry/`

## Phase 3 — Custom PCB design (KiCad)
**Goal:** Translate the dev-board prototype into a custom 2-/4-layer PCB.
**Deliverable:** KiCad schematic + layout for the custom MCU board, ERC + DRC clean, gerbers exported.
**Exit criterion:**
- [ ] Schematic complete, ERC clean
- [ ] Layout complete, DRC clean
- [ ] BOM exported and matches `docs/03-hardware-bom.md`
- [ ] Gerbers exported under `hardware/pcb/gerbers/`
- [ ] 3D render saved under `assets/images/`
- [ ] Self-review against `docs/04-pcb-design.md` checklist

## Phase 4 — PCB fabrication & bring-up
**Goal:** Order, assemble, and bring up the v1 PCB.
**Deliverable:** Working assembled board, bring-up checklist completed.
**Exit criterion:**
- [ ] Boards received from fab (JLCPCB / PCBWay)
- [ ] Visual inspection + power-on test passed
- [ ] STM32 detected via SWD, blink firmware running
- [ ] All sensors enumerated on I²C
- [ ] Bring-up log appended to `docs/11-fault-record.md`
- [ ] Photo of working board in `assets/images/`

## Phase 5 — Integration on quadruped chassis
**Goal:** Mount the custom board on the existing spyder mechanical platform and run end-to-end.
**Deliverable:** Robot stands and reports telemetry while moving under operator control.
**Exit criterion:**
- [ ] Custom board mechanically mounted
- [ ] Wired to PCA9685 + servos + Pi 5
- [ ] Robot stands stably
- [ ] Robot walks under joystick control
- [ ] Live telemetry dashboard visible on operator device while walking
- [ ] Walk-with-telemetry video saved to `assets/`

## Phase 6 — Power & robot-state monitoring upgrade
**Goal:** Add INA226 and finish the robot-state monitoring story.
**Deliverable:** Battery voltage / current logged; tilt / shock / fall detection on the MCU; alerts surfaced to dashboard.
**Exit criterion:**
- [ ] INA226 reports bus V and shunt I to within ±2 % of bench meter
- [ ] Fall test triggers fall flag in telemetry
- [ ] Power-draw profile during walking captured and documented in `docs/09`
- [ ] Low-battery alert path tested

## Phase 7 — Field test & write-up
**Goal:** Take the robot out, run a representative deployment, and turn it into a CV-ready artefact.
**Deliverable:** Recorded field test, write-up, demo video.
**Exit criterion:**
- [ ] Robot deployed in a representative environment (TBD)
- [ ] Telemetry recorded for ≥ 1 session
- [ ] `RESULTS.md` written: sensor latencies, power consumption, range, anomalies
- [ ] Demo video linked from README
- [ ] LinkedIn / CV updated with project link

## (Stretch) Phase 8 — v2 PCB
**Deliverable:** v2 board with PCA9685 integrated and BME280 / BME680 in place of DHT11.
**Exit criterion:**
- [ ] v2 schematic + layout
- [ ] v2 fab'd and brought up
- [ ] v2 replaces v1 on the chassis
- [ ] `docs/10-design-decisions.md` updated with what changed and why

---

## Tracking

Use GitHub Issues with one issue per phase, and link sub-tasks to the checkboxes above.

> TODO: open Phase 1 issue once Phase 0 (this PR) is merged.
