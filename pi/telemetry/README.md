# pi/telemetry/

Phase 1 telemetry stack: read **MPU6050 (IMU)** and **DHT11 (temp/humidity)** directly from the Pi 5, log to CSV, show on the **SSD1306 OLED**. Phase 2 will replace the per-sensor reads with a UART parser for the custom MCU board.

> **Wiring cheat sheet:** [`../../docs/phase1-wiring.md`](../../docs/phase1-wiring.md) — keep it open while wiring.

> **Deferred to Phase 2 (STM32):** HC-SR04 ultrasonic (needs 5 V → 3.3 V level shift on ECHO) and the raindrop sensor (needs an ADC). Their driver scaffolds remain in `sensors/` but are disabled in `config.yaml`.

## Current layout

```
telemetry/
├── logger.py            entry point: poll sensors -> CSV + stdout
├── display.py           SSD1306 OLED rendering (Phase 1, optional)
├── config.yaml          rate, pins, output path
├── requirements.txt
├── sensors/             individual driver skeletons
│   ├── mpu6050.py       I2C IMU
│   ├── dht11.py         1-wire temp / humidity
│   ├── hcsr04.py        ultrasonic distance
│   └── raindrop.py      digital wetness (Phase 1) / analog (later)
└── sample_data/         CSVs from real runs (committed selectively)
```

> All driver `.read()` methods currently raise `NotImplementedError` with a `TODO` pointing at the exact lines to fill in. The combined `logger.py` swallows `NotImplementedError` so it runs end-to-end even before any sensor is wired — useful for sanity-checking the loop on a desk Pi.

## How to bring this up on the Pi

```bash
# 1. Clone & enter
git clone https://github.com/wooseongjung/spyderrobot.git
cd spyderrobot/pi/telemetry

# 2. Enable I2C & SPI
sudo raspi-config            # Interface Options -> I2C: enable, SPI: enable
sudo reboot

# 3. Verify wiring
i2cdetect -y 1               # MPU6050 should appear at 0x68; OLED at 0x3C

# 4. Python env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 5. Run
python -m logger
# Ctrl-C to stop. CSV written to sample_data/run.csv.
```

## Bring-up order (recommended)

1. **MPU6050** first — I²C is the cleanest path. Verify with `i2cdetect -y 1` (expect `0x68`), then implement `MPU6050.open()` / `read()` in `sensors/mpu6050.py`.
2. **OLED** next — same I²C bus (`0x3C`). Implement `display.py`. Showing live IMU values on the OLED is a satisfying first milestone.
3. **DHT11** last — known to be flaky on Pi 5. Use `adafruit-circuitpython-dht`, not the legacy `RPi.GPIO` driver. If misses are frequent, that's normal — the logger retries on the next loop.

After each sensor: rerun `python -m logger` and confirm its column in `sample_data/run.csv` is no longer `None`.

## Wiring summary

| Sensor | Pi 5 pins | Notes |
|---|---|---|
| MPU6050 | 3V3 (pin 1), GND (pin 6), GPIO2 SDA (pin 3), GPIO3 SCL (pin 5) | shares I²C1 with OLED, address `0x68` |
| OLED SSD1306 | 3V3, GND, GPIO2 SDA, GPIO3 SCL | shares I²C1 with MPU6050, address `0x3C` |
| DHT11 (3-pin module) | 3V3, GND, GPIO4 (pin 7) | 4-pin variant needs a 10 kΩ pull-up DATA → 3V3 |

Full step-by-step: [`../../docs/phase1-wiring.md`](../../docs/phase1-wiring.md).

## Phase 1 exit criterion (from `docs/08-roadmap-milestones.md`)

- [ ] MPU6050 and DHT11 return plausible values for ≥ 30 min uninterrupted
- [ ] CSV log committed under `sample_data/`
- [ ] OLED displays IMU + temp + humidity
- [ ] Photo of breadboard rig in `assets/images/`

## Looking ahead (Phase 2)

When the STM32 dev board arrives, this folder gains a `parser.py` that decodes the UART frame format from [`../../docs/05-firmware-architecture.md`](../../docs/05-firmware-architecture.md). The per-sensor drivers in `sensors/` stay as a fallback / reference implementation, but the runtime data path moves to: **MCU → UART → parser → logger → CSV / dashboard**.
