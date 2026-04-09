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
