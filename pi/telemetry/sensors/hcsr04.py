"""HC-SR04 ultrasonic distance sensor.

The HC-SR04 runs at 5 V logic. The TRIG line is fine to drive from a
3.3 V GPIO, but the ECHO line MUST be level-shifted down to 3.3 V before
hitting the Pi (typical: 1 kohm + 2 kohm divider, or a level-shifter IC).
DO NOT connect ECHO directly to a Pi GPIO.

Wiring (Pi 5):
    VCC  -> 5V    (pin 2)
    GND  -> GND   (pin 6)
    TRIG -> GPIO23 (pin 16)
    ECHO -> GPIO24 (pin 18) via voltage divider

Speed of sound: 343 m/s at 20 C.
Distance = (echo_pulse_width_s * 343) / 2  -> metres
"""

from dataclasses import dataclass
from typing import Optional


SPEED_OF_SOUND_MPS = 343.0
TIMEOUT_S = 0.04   # ~ 6.8 m max range; sensor's spec is ~ 4 m


@dataclass
class DistanceReading:
    distance_mm: float


class HCSR04:
    def __init__(self, trig_pin: int = 23, echo_pin: int = 24):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self._gpio = None
        self.error_count = 0

    def open(self) -> None:
        # TODO: on the Pi 5 use gpiozero (it abstracts libgpiod):
        #   from gpiozero import DistanceSensor
        #   self._device = DistanceSensor(echo=self.echo_pin, trigger=self.trig_pin,
        #                                  max_distance=4.0)
        # gpiozero handles the trigger pulse, echo capture, and unit conversion.
        raise NotImplementedError("TODO: implement on-Pi")

    def read(self) -> Optional[DistanceReading]:
        """Single ping. Returns None on timeout."""
        # TODO:
        #   d_m = self._device.distance        # gpiozero returns metres
        #   return DistanceReading(d_m * 1000.0)
        raise NotImplementedError("TODO: implement on-Pi")

    def close(self) -> None:
        if self._gpio is not None:
            self._gpio.close()
            self._gpio = None


if __name__ == "__main__":
    import time
    s = HCSR04()
    s.open()
    try:
        for _ in range(10):
            print(s.read())
            time.sleep(0.2)
    finally:
        s.close()
