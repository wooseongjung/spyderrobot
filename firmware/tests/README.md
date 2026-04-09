# firmware/tests/

Host-side unit tests for the firmware.

> Populated alongside Phase 2.

Targets:
- CRC routine (CCITT vectors)
- Telemetry frame encode / decode round-trip
- Scheduler dispatch under simulated time
- Sensor driver state machines (mocked I²C)

Framework: TBD (likely Unity + CMock, or plain `assert.h` to start).
