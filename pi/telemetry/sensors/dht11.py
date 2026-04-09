"""DHT11 temperature & humidity sensor.

DHT11 is a single-wire protocol with strict timing. On the Pi 5 use the
adafruit-circuitpython-dht library which goes via libgpiod (the legacy
RPi.GPIO timing-based driver does NOT work reliably on Pi 5).

Wiring (Pi 5):
    VCC  -> 3V3   (pin 1)
    GND  -> GND   (pin 6)
    DATA -> GPIO4 (pin 7)  + a 10k pull-up to 3V3

Notes:
- DHT11 is slow (~ 1 Hz max) and coarse (1 C / 1 %RH resolution).
- Replace with BME280 / SHT31 in target v2 (see docs/03-hardware-bom.md).
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class EnvReading:
    temp_c: float
    rh: float


class DHT11:
    def __init__(self, pin: int = 4):
        self.pin = pin
        self._device = None
        self.error_count = 0

    def open(self) -> None:
        import board  # lazy import so the module lints off-Pi
        import adafruit_dht
        self._device = adafruit_dht.DHT11(getattr(board, f"D{self.pin}"))

    def read(self) -> Optional[EnvReading]:
        """Read temperature and humidity. Returns None on a checksum miss
        (DHT11 misses are common; the caller should retry rather than
        treat one None as a hard failure)."""
        if self._device is None:
            return None
        try:
            t = self._device.temperature
            rh = self._device.humidity
        except RuntimeError:
            self.error_count += 1
            return None
        if t is None or rh is None:
            self.error_count += 1
            return None
        return EnvReading(t, rh)

    def close(self) -> None:
        if self._device is not None:
            self._device.exit()
            self._device = None


if __name__ == "__main__":
    import time
    s = DHT11()
    s.open()
    try:
        for _ in range(10):
            print(s.read())
            time.sleep(2)
    finally:
        s.close()
