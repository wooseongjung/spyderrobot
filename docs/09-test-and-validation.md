# 09 — Test & Validation

How each subsystem is tested and what counts as "passing." This is the document I'll appeal to when deciding whether a phase is done.

## Sensor calibration & sanity tests

| Sensor | Test | Pass criterion |
|---|---|---|
| DHT11 / BME280 | Compare to a reference thermometer/hygrometer at room temp | within ±2 °C, ±5 %RH (DHT11) / ±0.5 °C, ±3 %RH (BME280) |
| HC-SR04 | Range a wall at 0.1 / 0.5 / 1.0 / 2.0 m | within ±1 cm (close), ±3 cm (far) |
| Raindrop | Dry vs wet vs flood | three distinct ADC bands, > 200 counts apart |
| MPU6050 / 9250 | Stationary on flat surface | accel z ≈ 1 g ± 0.05; gyro ≈ 0 ± 0.5 dps |
| INA226 | Known load on bench PSU (e.g. 5 V × 0.5 A) | within ± 2 % of meter |

## PCB bring-up checklist (per-board)

Run **before** powering with the full sensor stack.

1. [ ] Visual inspection — no solder bridges, no missing parts, no swapped polarised parts
2. [ ] Resistance check 5 V → GND ≥ a few kΩ
3. [ ] Resistance check 3.3 V → GND ≥ a few kΩ
4. [ ] Apply 5 V from bench PSU at current limit ~ 200 mA
5. [ ] Verify 5 V rail = 5.0 ± 0.1 V
6. [ ] Verify 3.3 V rail = 3.3 ± 0.05 V
7. [ ] Verify quiescent current is sane (TODO: target value)
8. [ ] Connect SWD; verify STM32 ID detected by ST-Link
9. [ ] Flash blink-LED firmware; verify heartbeat LED toggles
10. [ ] I²C scan: every expected device acks
11. [ ] UART loopback to Pi: echo test passes
12. [ ] Run telemetry firmware: frames decode on Pi with CRC OK

## Firmware unit tests (host-side)

- Driver code compiled against a mock HAL
- CRC routine checked against known vectors (CCITT)
- Frame encode/decode round-trip
- State machine for telemetry assembler

> TODO: pick framework — Unity / CMock for embedded, or just plain `assert.h` initially.

## Integration tests

| Test | Method | Pass |
|---|---|---|
| End-to-end telemetry | Run firmware + Pi parser; capture 30 min | ≥ 99.9 % frames decoded, no CRC errors |
| Power load | Walk the robot for 10 min while logging INA226 | average current within design budget |
| Watchdog | Inject deliberate hang on a sensor task | board resets within 1 s, BOOT_AFTER_WDG event seen |
| Cable disconnect | Pull MCU↔Pi UART mid-run | Pi reports link loss ≤ 200 ms; recovers on reconnect |

## Field test protocol

1. Charge battery, log start voltage
2. Take robot to test location
3. Start dashboard recording
4. Walk the robot through a defined route
5. Periodically capture camera frames
6. Stop recording, log end voltage
7. Save dataset and notes
8. Append findings to `docs/11-fault-record.md` if anything went wrong
9. Update `RESULTS.md`

## Exit gates per phase

These are referenced from `docs/08-roadmap-milestones.md`. A phase is not complete until **all** exit-criterion checkboxes are ticked.

---

> TODO: capture the bring-up log from the first real PCB and link it here.
