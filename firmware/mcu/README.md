# firmware/mcu/

STM32 firmware project (G4 / F4 family, exact part TBD).

> Populated in **Phase 2** of [`../../docs/08-roadmap-milestones.md`](../../docs/08-roadmap-milestones.md).

Expected layout:

```
mcu/
├── Core/                   (CubeMX-generated HAL setup)
├── Drivers/                (STM32 HAL — vendor)
├── App/                    (application source)
│   ├── main.c
│   ├── scheduler.c
│   ├── uart_link.c
│   ├── telemetry.c
│   └── sensors/
│       ├── imu.c
│       ├── env.c
│       ├── ultrasonic.c
│       ├── raindrop.c
│       └── ina226.c
├── spyder-mcu.ioc          (CubeMX project)
└── README.md
```

Toolchain: STM32CubeIDE (initial). Build flags: `-Wall -Wextra -Wpedantic`.
