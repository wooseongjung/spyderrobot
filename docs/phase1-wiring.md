# Phase 1 — Wiring Cheat Sheet

Keep this open while wiring. Three devices, one shared I²C bus, one GPIO. Total wiring time: ~10 minutes.

## What we're wiring (and what we're NOT)

| Device | Phase 1? | Notes |
|---|---|---|
| **MPU6050** (IMU) | YES | I²C, 3.3 V |
| **DHT11** (temp/humidity) | YES | 1-wire, 3.3 V |
| **SSD1306 OLED 0.96"** | YES | I²C, 3.3 V, shares bus with MPU6050 |
| ~~HC-SR04 ultrasonic~~ | **NO** — deferred | level-shifting hassle, deferred to STM32 |
| ~~Raindrop sensor~~ | **NO** — deferred | needs an ADC; deferred to STM32 |

The two deferred sensors stay as scaffold files in `pi/telemetry/sensors/` — disabled in `config.yaml`, ready to enable later.

---

## Pi 5 header pins we'll use

```
Pin 1  [ 3V3 ] o o [ 5V  ]  Pin 2
Pin 3  [ SDA ] o o [ 5V  ]  Pin 4   <- GPIO2  I2C1 SDA
Pin 5  [ SCL ] o o [ GND ]  Pin 6   <- GPIO3  I2C1 SCL
Pin 7  [ G4  ] o o [ GND ]  Pin 9   <- GPIO4  (DHT11 DATA)
Pin 9  ...
```

Only six pins are used: **1 (3V3)**, **3 (SDA)**, **5 (SCL)**, **6 (GND)**, **7 (GPIO4)**, **9 (GND)**.

---

## Step 0 — Enable I²C on the Pi

```bash
sudo raspi-config        # Interface Options -> I2C -> Enable
sudo reboot
```

Verify:

```bash
ls /dev/i2c-*            # should list /dev/i2c-1
i2cdetect -y 1           # empty grid until you wire something
```

---

## Step 1 — Power & ground rails on the breadboard

Run two jumpers from the Pi to the breadboard rails:

| Pi pin | Breadboard rail |
|---|---|
| Pin 1 (3V3) | red rail (+) |
| Pin 6 (GND) | blue rail (−) |

**Use pin 1 for 3V3, NOT pin 17.** Pin 17 is also 3V3 but pin 1 is by convention "the" 3V3 pin.
**Do NOT use pin 2 or pin 4** (those are 5 V — will fry the MPU6050 and OLED if connected by mistake).

---

## Step 2 — MPU6050 (I²C, address 0x68)

```
MPU6050              Pi 5
-------              ----
VCC   ----- red rail (3V3)
GND   ----- blue rail (GND)
SCL   ----- Pin 5  (GPIO3, I2C1 SCL)
SDA   ----- Pin 3  (GPIO2, I2C1 SDA)
XDA   --- not connected
XCL   --- not connected
ADO   --- not connected   (leaves address as 0x68; tie to 3V3 to use 0x69)
INT   --- not connected
```

**Verify:**

```bash
i2cdetect -y 1
# expect to see: 68 in the grid
```

If you see `--` in every cell:
- Check 3V3 and GND first (multimeter on the module's VCC/GND pins)
- Swap SDA / SCL (most common mistake)
- Check the ribbon / jumpers aren't broken

---

## Step 3 — SSD1306 OLED (I²C, address 0x3C)

The OLED rides the **same I²C bus** as the MPU6050. They have different addresses, so no conflict.

```
OLED                 Pi 5  (or breadboard rails)
-------              ----
VCC / VDD ----- red rail (3V3)
GND       ----- blue rail (GND)
SCL / SCK ----- Pin 5 (same SCL as MPU6050)
SDA / SDI ----- Pin 3 (same SDA as MPU6050)
```

You can either:
- daisy-chain: Pi → MPU6050 → OLED on the same SDA/SCL wires, or
- run two pairs of jumpers from the Pi to each module — both work.

**Verify both devices appear:**

```bash
i2cdetect -y 1
# expect to see BOTH:  3c   and   68
```

If only one shows:
- Check the missing module's wiring in isolation (unplug the other one).
- Some OLED modules use address `0x3D` instead of `0x3C` — `i2cdetect` will still show it; just note which.
- I²C pull-ups are built into both modules; **do not add external pull-ups** unless `i2cdetect` reliably misses devices.

---

## Step 4 — DHT11 (1-wire, GPIO4)

DHT11 modules come in two flavours: 3-pin (with the pull-up already on the PCB) and 4-pin (raw sensor; needs an external pull-up). Look at yours.

### 3-pin module (most common, with PCB)

```
DHT11 module         Pi 5
------------         ----
+  / VCC  ----- red rail (3V3)
-  / GND  ----- blue rail (GND)
S  / OUT  ----- Pin 7 (GPIO4)
```

Done. No external resistor needed.

### 4-pin raw sensor (no PCB)

Looking at the **front** (the side with the holes), pins are numbered 1–4 left to right:

```
DHT11 (front)        Pi 5
-------------        ----
1  VCC  ----- red rail (3V3)
2  DATA ----- Pin 7 (GPIO4)   AND  10 kohm to 3V3 (red rail)
3  NC   --- not connected
4  GND  ----- blue rail (GND)
```

The 10 kΩ pull-up between DATA and 3V3 is **mandatory** for the 4-pin variant.

**Verify:** DHT11 doesn't show up on `i2cdetect` (it's not I²C). You'll only know it works when `python -m logger` returns a temperature instead of `None`.

---

## Step 5 — Final breadboard sanity check

Before powering on:

- [ ] **No 5 V anywhere on the breadboard.** Trace every red wire back to Pi pin **1**, not 2 or 4.
- [ ] **3V3 and GND not shorted.** Multimeter, continuity mode, between red and blue rails — should beep when a module is in, not beep when rails are bare.
- [ ] **No two GPIO pins jumpered together.**
- [ ] **MPU6050 SDA/SCL not swapped** (most common mistake).
- [ ] **DHT11 polarity right** — `+` to 3V3, `−` to GND. Backwards = magic smoke.

Then plug the Pi power in.

---

## Step 6 — First-light test

```bash
cd ~/spyderrobot/pi/telemetry
source .venv/bin/activate

# I2C devices visible?
i2cdetect -y 1
# should show 0x3C (OLED) and 0x68 (MPU6050)

# Run the logger
python -m logger
```

Expected output for a fresh Pi with sensors wired but drivers not yet implemented:

```
[2026-04-09T15:23:01.123+00:00] dist=None wet=None env=None/None
```

(All `None` because the driver bodies are still `TODO`. The logger runs end-to-end. Good.)

Then implement `MPU6050.open()` and `read()` in `pi/telemetry/sensors/mpu6050.py` and rerun:

```
[2026-04-09T15:24:11.456+00:00] dist=None wet=None env=None/None  ax=0.02 ay=-0.01 az=0.99
```

Now you have a real reading. Repeat for DHT11. When both are returning real data, Phase 1 is functionally complete.

---

## Troubleshooting cheat sheet

| Symptom | Likely cause | Fix |
|---|---|---|
| `i2cdetect` shows nothing | I²C not enabled, or SDA/SCL swapped | `raspi-config`; swap wires |
| `i2cdetect` shows only `0x68`, no `0x3C` | OLED not powered, or address is `0x3D` | check OLED 3V3/GND; rerun |
| `i2cdetect` shows only `0x3C`, no `0x68` | MPU6050 not powered, or VCC backwards | check MPU6050 wiring |
| `i2cdetect` shows weird ghost addresses everywhere | shorted SDA or SCL to GND | unplug everything, re-do |
| MPU6050 reads all zeros | forgot to wake it (clear `PWR_MGMT_1`) | the driver does this in `open()` |
| DHT11 returns `None` every read | timing-based driver instead of CircuitPython | `pip install adafruit-circuitpython-dht` |
| DHT11 returns `None` ~ half the time | normal — DHT11 misses checksums often | retry on next loop, accept the loss |
| Pi resets when wiring touches | shorted 3V3 to GND | unplug, fix, plug back in |

---

## When Phase 1 is done

Update `docs/08-roadmap-milestones.md` Phase 1 checkboxes, commit a CSV slice from `sample_data/run.csv`, take a photo of the breadboard rig and drop it in `assets/images/`. Then move on to Phase 2 (MCU dev board).
