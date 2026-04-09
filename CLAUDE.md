# Claude Code — instructions for the spyderrobot project

This file is read automatically by every Claude Code session that opens this
repo. It bootstraps a new session with the project's framing, the active
phase, and the standing rules. If you are a Claude agent and you're reading
this: do the three reads in the next section before doing anything else.

---

## What this project is (read first)

A **sensorised quadruped platform for remote environmental awareness and
robot-state monitoring.** The engineering deliverable is a custom STM32-based
sensor/monitoring PCB integrated with a Raspberry Pi 5. The quadruped chassis
is the *carrier*; the PCB + firmware + sensor integration is the *story*.

The original 1-line framing of the repo was "Quadruped robot performs spider
motion using 12 servo motors, Rpi5, and several sensors." The project has
since been re-scoped to foreground custom PCB design, MCU firmware, and
sensor integration skills. The mechanical/URDF work from the original scope
is preserved intact in `spider/` as the Mechanical & Simulation subsystem.

## At the start of every session, read these three files

1. **[`docs/12-ultimate-vision.md`](docs/12-ultimate-vision.md)** — the
   long-term north-star spec. Grounds every decision in where the project
   is ultimately heading. Explicitly out of scope for v1, but sets the
   direction of travel.
2. **[`docs/08-roadmap-milestones.md`](docs/08-roadmap-milestones.md)** —
   phased plan (Phase 0 through Phase 7, plus a stretch Phase 8) with
   deliverables and exit criteria. The checkboxes tell you which phase is
   currently active and what "done" looks like for it.
3. **[`docs/11-fault-record.md`](docs/11-fault-record.md)** — running fault
   and debug log. Scan it for unresolved issues before starting work, and
   append to it whenever something breaks or a non-obvious root cause is
   identified.

## Standing rules (do not violate)

1. **Never remove or modify `spider/`.** It's the existing ROS/URDF
   mechanical package and is part of the project's evidence trail. Verify
   with `git diff main -- spider/` before every PR — the output must be
   empty. If it isn't, something is wrong, stop and investigate.
2. **Append to [`docs/11-fault-record.md`](docs/11-fault-record.md)** for
   every hardware fault, wiring mistake, firmware bug, or non-trivial debug
   session. Use the template at the top of that file. This is the project's
   institutional memory and must grow, not atrophy. Interviewers will
   specifically look at this file.
3. **Respect the phased roadmap.** Work inside the phase currently active
   per `docs/08-roadmap-milestones.md`. Do not skip phases. If a proposed
   change crosses a phase boundary, update the roadmap first and explain
   the re-ordering in `docs/10-design-decisions.md` as a new ADR.
4. **Documentation style = structured outlines with explicit `TODO:`
   markers** wherever a real number, part choice, or measurement is needed.
   Do not invent technical specs the user would have to later correct.
5. **MCU target = STM32 G4/F4 family.** Phase 2 dev board is a
   NUCLEO-F411RE. This is locked in ADR-0003 in `docs/10-design-decisions.md`.
6. **Architecture = Option A**: Pi 5 + custom MCU board + external PCA9685.
   The PCA9685 stays off-board until a stretch v2 PCB. This is locked in
   ADR-0002.
7. **Git workflow:** feature branches + pull requests, never direct commits
   to `main`. Show diffs to the user before pushing. **Never merge a PR
   without explicit user approval** — the user reviews and merges on GitHub
   themselves.

## Where things live

| Concern | Path |
|---|---|
| Project overview & scope | `docs/01-project-overview.md` |
| System architecture | `docs/02-system-architecture.md` |
| Hardware BOM | `docs/03-hardware-bom.md` |
| Custom PCB design spec | `docs/04-pcb-design.md` |
| Firmware architecture | `docs/05-firmware-architecture.md` |
| Pi 5 software | `docs/06-pi-software.md` |
| Mechanical / simulation cross-ref | `docs/07-mechanical-simulation.md` |
| **Phased roadmap & exit criteria** | `docs/08-roadmap-milestones.md` |
| Test & validation plans | `docs/09-test-and-validation.md` |
| Design decisions (ADR log) | `docs/10-design-decisions.md` |
| **Running fault / debug log** | `docs/11-fault-record.md` |
| **Long-term north-star vision** | `docs/12-ultimate-vision.md` |
| Phase 1 wiring cheat sheet | `docs/phase1-wiring.md` |
| Pi telemetry scaffold (Python) | `pi/telemetry/` |
| KiCad PCB project | `hardware/pcb/` *(empty until Phase 3)* |
| MCU firmware project | `firmware/mcu/` *(empty until Phase 2)* |
| Photos, renders, diagrams | `assets/images/`, `assets/diagrams/` |
| Mechanical / URDF (ROS package) | `spider/` — **preserved, do not modify** |

## Bench hardware the user has available

When suggesting debugging, bring-up, or sensor-characterisation steps,
assume the user has:

- Raspberry Pi 5 (8 GB) — high-level compute
- **NI myDAQ** — DMM, oscilloscope (scope mode for I²C/SPI/UART debug),
  function generator, ±15 V and +5 V bench supplies, 2× 16-bit AI at up to
  200 kS/s, 2× AO, 8× 0–5 V DIO (not fast enough for sub-µs timing)
- Breadboard + jumper kit
- Sensor kit: MPU6050, DHT11, HC-SR04, raindrop sensor, SSD1306 OLED,
  LCD1602, PS2 joystick, PCA9685, 12× MG996R servos, Raspberry Pi AI Camera
- The existing spyder quadruped chassis (SolidWorks-designed; URDF in
  `spider/`)

Suggest the myDAQ specifically for:
- I²C / SPI / UART scoping before swapping cables blindly
- Rail continuity and voltage checks before powering the Pi
- Analog sensor characterisation (raindrop curve, thermistors, photodiodes)
- PCB bring-up rail verification in Phase 4

Do NOT assume a handheld multimeter or a standalone oscilloscope — the
myDAQ is the user's primary bench instrument.

## When the user asks for changes to the repo

1. Confirm which branch to base off. For Phase 1 work, stack on
   `phase1/pi-prototype`. For new phases, branch off `main` (after merge)
   or off the most recent merged phase branch.
2. Make changes on a feature branch, never on `main`.
3. Show a diff or a file tree before pushing.
4. Use descriptive commit messages (`docs:`, `feat(pi):`, `feat(mcu):`,
   `chore:`, `fix:`) — see recent commits for the established style.
5. Push the branch, open a PR via `gh pr create` with a summary + test plan,
   return the PR URL to the user.
6. Do not merge. The user merges on GitHub.

## When something breaks

Record it in [`docs/11-fault-record.md`](docs/11-fault-record.md). The
template is at the top of the file. Minimum fields: date, phase, subsystem,
symptom, root cause, fix, lesson learned. Even "silly" mistakes (wrong pin,
swapped SDA/SCL, forgot to enable I²C) go in — they're the most useful
entries because they save future-you hours.
