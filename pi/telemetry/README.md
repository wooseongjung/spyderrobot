# pi/telemetry/

Phase 1 telemetry stack: read every prototype sensor directly from the Pi 5, log to CSV, optionally show on the OLED. Phase 2 will replace the per-sensor reads with a UART parser for the custom MCU board.

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

1. **MPU6050** first — I2C is the cleanest path. Verify with `i2cdetect`, then implement `MPU6050.open()` / `read()`.
2. **HC-SR04** second — uses `gpiozero.DistanceSensor`. *Voltage-divide the ECHO line; do not connect 5 V logic to a GPIO directly.*
3. **Raindrop** third — single GPIO read; trivial once wiring is right.
4. **DHT11** last — known to be flaky on Pi 5; if it fights you, skip and rely on the planned BME280 upgrade.

After each sensor: rerun `python -m logger` and confirm its column in `sample_data/run.csv` is no longer `None`.

## Wiring summary

| Sensor | Pi 5 pins | Notes |
|---|---|---|
| MPU6050 | 3V3, GND, GPIO2 (SDA), GPIO3 (SCL) | shares I2C1 with OLED |
| DHT11 | 3V3, GND, GPIO4 (DATA) | 10 kΩ pull-up DATA → 3V3 |
| HC-SR04 | 5 V, GND, GPIO23 (TRIG), GPIO24 (ECHO) | **divide ECHO to 3.3 V** |
| Raindrop | 3V3, GND, GPIO17 (DO) | DO is active-low when wet |
| OLED | 3V3, GND, GPIO2 (SDA), GPIO3 (SCL) | shares I2C1 with MPU6050 |

## Phase 1 exit criterion (from `docs/08-roadmap-milestones.md`)

- [ ] Each sensor returns plausible values for ≥ 30 min uninterrupted
- [ ] CSV log committed under `sample_data/`
- [ ] OLED displays at least temp, humidity, distance
- [ ] Photo of breadboard rig in `assets/images/`

## Looking ahead (Phase 2)

When the STM32 dev board arrives, this folder gains a `parser.py` that decodes the UART frame format from [`../../docs/05-firmware-architecture.md`](../../docs/05-firmware-architecture.md). The per-sensor drivers in `sensors/` stay as a fallback / reference implementation, but the runtime data path moves to: **MCU → UART → parser → logger → CSV / dashboard**.
