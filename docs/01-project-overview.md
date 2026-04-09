# 01 — Project Overview

## Problem statement

Many environmental and infrastructure inspection tasks require getting a sensor package into a location that is **hazardous, confined, or hard to access** for humans — flooded basements, post-fire debris fields, contaminated industrial sites, collapsed structures. Static sensor stations cannot be moved on demand, and full inspection robots are expensive and operationally heavy.

**spyderrobot** is a small, low-cost quadruped that carries a custom embedded sensing/monitoring board into such environments and streams environmental + platform-state telemetry back to an operator via a Raspberry Pi 5.

## Target use case

A single operator deploys the robot into a target area. The robot:

1. Walks under operator control (or following a simple path).
2. Continuously samples local **temperature, humidity, distance to obstacles, surface wetness**.
3. Continuously monitors its own **tilt, shock, vibration, battery voltage and current draw**.
4. Captures camera frames on demand (Pi AI Camera).
5. Streams everything back to the operator's screen and logs to disk.

If the robot tips, takes damage, runs low on battery, or loses comms, the system records the event and surfaces it.

## Why this framing

The original "12-servo quadruped" framing positioned the project as a mechanical / motion-control demo. The new framing positions it as a **mobile sensing & monitoring platform with a custom embedded board at its heart**, which:

- Aligns with the engineering disciplines I want to be hired into (analog/mixed-signal, embedded, sensor systems).
- Foregrounds the skill that is currently weak in my CV: **end-to-end custom PCB design and bring-up**.
- Reframes the existing mechanical work (`spider/` ROS package) as one *subsystem* in a larger system, instead of being the whole project.

## Scope — what this project IS

- A custom STM32-based PCB for sensor acquisition and platform monitoring
- A Raspberry Pi 5 telemetry / logging / camera / interface layer
- Integration on the existing spyder quadruped chassis
- A repeatable bring-up + test process, documented
- A field demo with recorded data

## Scope — what this project IS NOT

- A full autonomous-navigation rescue robot
- A ROS-heavy multi-node system (the existing `spider/` ROS package is for simulation only, not the runtime stack)
- A custom motor-driver development project (PCA9685 stays as the servo driver)
- An ML / computer-vision project (the camera is for telemetry, not perception)

## Success criteria

- Custom PCB designed in KiCad, fabricated, and brought up
- STM32 firmware streams sensor + platform-state telemetry to the Pi over UART without dropouts for ≥ 30 min continuous
- Robot walks under operator control while telemetry streams live
- Documented design decisions, test results, and a recorded field-test video
- The repo is presentable as a single coherent CV artefact

## Audience for this repo

- **Recruiters / interviewers** — for the README, top-level architecture, and demo video
- **My future self** — for the engineering log: design decisions, fault record, test results, BOM choices

---

> TODO: insert a hero photo or render of the robot once Phase 1 is underway → `assets/images/`.
