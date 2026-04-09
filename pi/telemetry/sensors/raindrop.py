"""Raindrop / wetness sensor.

The cheap raindrop module has TWO outputs:
  - DO (digital): goes LOW when wetness exceeds the on-board pot threshold
  - AO (analog) : raw analog voltage proportional to surface conductance

The Pi 5 has NO native ADC, so the analog output cannot be read directly.
Three options:
  (a) v1: use only the DO line into a GPIO  -> binary wet/dry
  (b) add an MCP3008 SPI ADC                -> 10-bit analog reading
  (c) wait until the custom MCU board       -> STM32 reads analog directly

For Phase 1 we use option (a). Threshold is set with the on-board pot.

Wiring (Pi 5):
    VCC -> 3V3   (pin 1)
    GND -> GND   (pin 6)
    DO  -> GPIO17 (pin 11)
    AO  -> not connected (Phase 1)
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class WetReading:
    wet: bool
    raw: Optional[int] = None  # populated only if an ADC is wired


class Raindrop:
    def __init__(self, do_pin: int = 17):
        self.do_pin = do_pin
        self._device = None
        self.error_count = 0

    def open(self) -> None:
        # TODO: on the Pi:
        #   from gpiozero import DigitalInputDevice
        #   self._device = DigitalInputDevice(self.do_pin, pull_up=True)
        raise NotImplementedError("TODO: implement on-Pi")

    def read(self) -> Optional[WetReading]:
        """DO is active-low when wet on most modules. Confirm with a
        screwdriver-and-water bench test before trusting the polarity."""
        # TODO:
        #   wet = (self._device.value == 0)
        #   return WetReading(wet=wet, raw=None)
        raise NotImplementedError("TODO: implement on-Pi")

    def close(self) -> None:
        if self._device is not None:
            self._device.close()
            self._device = None


if __name__ == "__main__":
    import time
    s = Raindrop()
    s.open()
    try:
        for _ in range(20):
            print(s.read())
            time.sleep(0.5)
    finally:
        s.close()
