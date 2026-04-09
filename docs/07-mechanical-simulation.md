# 07 — Mechanical Model & Simulation

This document describes the existing **`spider/`** ROS / catkin package at the root of the repo. It is the mechanical / simulation subsystem of the project.

## What's in `spider/`

```
spider/
├── CMakeLists.txt
├── package.xml          (catkin manifest)
├── export.log
├── config/              (RViz / sim config)
├── launch/              (launch files)
├── meshes/              (3D models exported from SolidWorks)
└── urdf/                (robot description files)
```

This is a standard ROS package built around a SolidWorks → URDF export of the spyder quadruped chassis. It contains the geometry, joint definitions, and meshes needed to:

- Visualise the robot in **RViz**
- Simulate it in **Gazebo**
- Validate joint limits and reach before committing to hardware changes

The current URDF was iterated once (Aug 24 2025) to add motors and a bottom plate so the model wouldn't collapse on import to SDF/Gazebo.

## How it relates to the rest of the project

| Subsystem | Role | Where it lives |
|---|---|---|
| Mechanical model | Geometry, joints, simulation | `spider/` (this folder) |
| Electronics | Custom MCU board | `hardware/pcb/` |
| Embedded firmware | STM32 | `firmware/mcu/` |
| High-level / telemetry | Pi 5 | `pi/` |

The mechanical model is **not** the runtime control stack. It is a design and validation tool — the real robot is controlled by the Pi 5 + custom MCU board, not by ROS at runtime.

## How to use it

> TODO: verify these commands once a fresh ROS environment is set up.

### Visualise URDF in RViz

```bash
# In a catkin workspace with this package
roslaunch spider display.launch         # TODO: confirm exact launch file name
```

### Simulate in Gazebo

```bash
roslaunch spider gazebo.launch          # TODO: confirm
```

### Inspect the URDF tree

```bash
rosrun urdfdom check_urdf $(find spider)/urdf/spider.urdf   # TODO: confirm filename
```

## Future mechanical work

- 3D-printed brackets for the custom PCB and sensors → files go in `hardware/enclosure/`
- Cable channels for the MCU↔sensor harness
- Optional payload bay for additional environmental sensors (BME680 etc.)

## Why we keep this folder untouched

The mechanical / URDF work is real evidence of design effort and is part of the project narrative. The pivot from "spider motion demo" → "sensing platform" does **not** invalidate this work — it re-frames it as the carrier subsystem. Nothing here is removed.

---

> TODO: take a screenshot of the URDF in RViz and put it under `assets/images/`.
