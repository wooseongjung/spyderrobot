"""Phase 1 telemetry logger.

Polls every sensor at the rate set in config.yaml, writes one CSV row
per cycle, prints a one-line status to stdout, and (optionally) updates
the OLED display.

Run on the Pi:
    cd ~/spyderrobot/pi/telemetry
    python -m logger

Stop with Ctrl-C; the CSV file is closed cleanly.
"""

from __future__ import annotations

import csv
import signal
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

from sensors.dht11 import DHT11
from sensors.hcsr04 import HCSR04
from sensors.mpu6050 import MPU6050
from sensors.raindrop import Raindrop


CONFIG_PATH = Path(__file__).parent / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def open_csv(path: Path) -> tuple:
    """Open the output CSV and write the header row."""
    path.parent.mkdir(parents=True, exist_ok=True)
    f = open(path, "w", newline="")
    writer = csv.writer(f)
    writer.writerow([
        "iso_ts", "t_ms",
        "ax_g", "ay_g", "az_g",
        "gx_dps", "gy_dps", "gz_dps",
        "imu_temp_c",
        "env_temp_c", "env_rh",
        "dist_mm",
        "wet",
        "errors_imu", "errors_env", "errors_dist", "errors_wet",
    ])
    return f, writer


def main() -> int:
    cfg = load_config()
    period_s = 1.0 / cfg.get("rate_hz", 5)
    out_path = Path(cfg.get("output_csv", "sample_data/run.csv"))

    imu  = MPU6050()
    env  = DHT11()
    dist = HCSR04()
    wet  = Raindrop()

    for s in (imu, env, dist, wet):
        try:
            s.open()
        except NotImplementedError as e:
            print(f"[skip] {type(s).__name__}: {e}", file=sys.stderr)

    t0 = time.monotonic()
    f, writer = open_csv(out_path)

    stopping = False
    def _stop(_signum, _frame):
        nonlocal stopping
        stopping = True
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    try:
        while not stopping:
            cycle_start = time.monotonic()
            t_ms = int((cycle_start - t0) * 1000)
            iso_ts = datetime.now(timezone.utc).isoformat(timespec="milliseconds")

            imu_r  = _safe_read(imu)
            env_r  = _safe_read(env)
            dist_r = _safe_read(dist)
            wet_r  = _safe_read(wet)

            row = [
                iso_ts, t_ms,
                *(imu_r.accel_g if imu_r else (None, None, None)),
                *(imu_r.gyro_dps if imu_r else (None, None, None)),
                imu_r.temp_c if imu_r else None,
                env_r.temp_c if env_r else None,
                env_r.rh if env_r else None,
                dist_r.distance_mm if dist_r else None,
                int(wet_r.wet) if wet_r else None,
                imu.error_count, env.error_count, dist.error_count, wet.error_count,
            ]
            writer.writerow(row)
            f.flush()

            print(f"[{iso_ts}] dist={row[12]} wet={row[13]} env={row[10]}/{row[11]}")

            sleep_s = period_s - (time.monotonic() - cycle_start)
            if sleep_s > 0:
                time.sleep(sleep_s)
    finally:
        f.close()
        for s in (imu, env, dist, wet):
            try:
                s.close()
            except Exception:
                pass

    return 0


def _safe_read(sensor):
    """Call .read() and swallow NotImplementedError so the logger can run
    even when only some drivers are wired up. Real exceptions still pass
    through."""
    try:
        return sensor.read()
    except NotImplementedError:
        return None


if __name__ == "__main__":
    raise SystemExit(main())
