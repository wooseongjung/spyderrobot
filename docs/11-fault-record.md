# 11 — Fault Record

A running log of bugs, failures, anomalies, and the fixes that resolved them. Anything that surprised me, broke, or wasted time gets an entry here. Future-me will thank present-me.

The point is twofold:
- **Operational:** if I see the same symptom again, I can find the previous root cause fast.
- **Interview / CV:** real, dated, documented debugging is one of the most credible signals in an interview. "Walk me through a tough bug you fixed" is much easier to answer with this in hand.

## How to use this file

Append new entries at the **top**. One entry per fault. Use the template below.

```
## YYYY-MM-DD — <subsystem>: <one-line symptom>

**Symptom:**
What I saw (sensor reading wrong, board didn't power up, frame CRC mismatched, etc.).

**Context:**
What I was doing when it appeared. Rev / commit / branch / hardware revision.

**Investigation:**
What I tried, in order. Include dead-ends — they save time later.

**Root cause:**
The actual cause. Be honest.

**Fix:**
What I changed. Link to commit if applicable.

**Lesson:**
What I'll do differently next time. (Optional but encouraged.)
```

---

## Example entry (delete or replace once a real fault is logged)

## 2026-04-09 — repo: GitHub repo not accessible during initial planning

**Symptom:**
`git clone` and `WebFetch` against `github.com/wooseongjung/spyderrobot` returned 404.

**Context:**
Phase 0 setup. Trying to read the existing repo state before restructuring.

**Investigation:**
Tried HTTPS clone, tried fetching the README via `raw.githubusercontent.com`, tried browsing the user profile. User profile listed only 3 public repos and `spyderrobot` was not among them.

**Root cause:**
The repository was set to private.

**Fix:**
Owner toggled the repo to public; subsequent fetches succeeded.

**Lesson:**
Before assuming a remote resource is missing, verify visibility. `gh repo view` would have surfaced the private status quickly with auth.

---

> Real entries start below this line. Newest first.

## 2026-04-09 — pi/telemetry: OLED showed "T 59.0C  H --%" in a 24 C / 62 %RH room

**Symptom:**
After wiring the SSD1306 into the Phase 1 logger, the OLED rendered
temperature as `59.0 C` and humidity as `--%`. The MPU6050 accel lines
were correct. The stdout debug line showed matching nonsense
(`env=59.0/None`).

**Context:**
Branch `feat/pi-oled-display-stacked`, stacked on
`feat/pi-imu-env-drivers` (PR #4). Phase 1 Step 6. DHT11 had already
been verified returning ~24 C / 62 %RH via direct driver prints in the
same session, so the sensor and driver were known good.

**Investigation:**
1. Suspected the DHT11 driver was returning a partial `EnvReading`
   (temp set, rh None). Re-read `sensors/dht11.py` — `read()` correctly
   returns `None` whenever either field is `None`, so a partial reading
   can't reach the logger row.
2. Suspected stale cached values from `adafruit_circuitpython_dht`
   between the two separate `.temperature` / `.humidity` property
   accesses. The library's `measure()` serves both from the same
   packet, so this was a dead end.
3. Re-read the CSV header in `logger.open_csv` and counted columns.
   Row layout is:
   `[0] iso_ts, [1] t_ms, [2..4] ax/ay/az, [5..7] gx/gy/gz,
    [8] imu_temp_c, [9] env_temp_c, [10] env_rh, [11] dist_mm, ...`
4. Checked the debug print and the OLED `show()` call in `logger.main`
   — both were reading `row[10]` as temperature and `row[11]` as
   humidity. `59.0` was humidity in %, and the "humidity" slot was
   pulling `dist_mm`, which is `None` because the HC-SR04 is disabled
   in `config.yaml` (deferred to Phase 2).

**Root cause:**
Off-by-one on the CSV column indices. The logger's own pre-existing
debug print was also wrong (`row[10]/row[11]`) and I copied that
mistake straight into the OLED call, which is why the mislabelling
survived earlier "first light" verification — the stdout line looked
self-consistent with the OLED.

**Fix:**
Use `row[9]` for `temp_c` and `row[10]` for `rh` in both the stdout
print and the `display.show()` dict. Also tagged the stdout units
(`env=24.6C/62%`) so a future units mix-up would be obvious at a
glance. Commit `20b44a1` on `feat/pi-oled-display-stacked`.

**Lesson:**
- Don't trust an existing debug print as an oracle when you're writing
  new code that reads the same data structure. Derive the indices from
  the source of truth (the CSV header in `open_csv`), not from a line
  that happened to look reasonable in the terminal.
- A room-temperature reading of "59 C" should have been treated as an
  obvious impossibility from the first glance, not rationalised as a
  "DHT11 first-read quirk" (which is how I initially mislabelled it in
  the drivers PR). Sanity-check units before blaming the sensor.
