"""0.96" SSD1306 OLED display (I2C, 128x64).

Wiring (Pi 5) — shares I2C1 with the MPU6050:
    VCC -> 3V3   (pin 1)
    GND -> GND   (pin 6)
    SDA -> GPIO2 (pin 3)
    SCL -> GPIO3 (pin 5)

Default I2C address: 0x3C.

Use as a sink for the latest reading from logger.py:
    display = OledDisplay()
    display.open()
    display.show({"dist_mm": 432, "wet": 0, "temp_c": 21.4})
"""

from typing import Optional


class OledDisplay:
    def __init__(self, address: int = 0x3C, width: int = 128, height: int = 64):
        self.address = address
        self.width = width
        self.height = height
        self._oled = None
        self._font = None

    def open(self) -> None:
        # TODO: on the Pi:
        #   import board, busio
        #   import adafruit_ssd1306
        #   from PIL import Image, ImageDraw, ImageFont
        #   i2c = busio.I2C(board.SCL, board.SDA)
        #   self._oled = adafruit_ssd1306.SSD1306_I2C(self.width, self.height, i2c, addr=self.address)
        #   self._oled.fill(0); self._oled.show()
        #   self._font = ImageFont.load_default()
        raise NotImplementedError("TODO: implement on-Pi")

    def show(self, fields: dict) -> None:
        """Render a small status screen.

        Layout (TODO: tune once on hardware):
            line 1:  dist 432 mm
            line 2:  temp 21.4 C
            line 3:  rh   42 %
            line 4:  wet  N
        """
        # TODO: build a PIL image, draw text, push to self._oled.image() and show()
        raise NotImplementedError("TODO: implement on-Pi")

    def close(self) -> None:
        if self._oled is not None:
            self._oled.fill(0)
            self._oled.show()
            self._oled = None


if __name__ == "__main__":
    d = OledDisplay()
    d.open()
    d.show({"dist_mm": 432, "wet": 0, "temp_c": 21.4, "rh": 42})
