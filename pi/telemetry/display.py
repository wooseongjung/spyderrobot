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
    display.show({"dist_mm": 432, "temp_c": 21.4, "rh": 42})
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
        import board  # lazy imports so this module lints off-Pi
        import busio
        import adafruit_ssd1306
        from PIL import Image, ImageDraw, ImageFont

        i2c = busio.I2C(board.SCL, board.SDA)
        self._oled = adafruit_ssd1306.SSD1306_I2C(
            self.width, self.height, i2c, addr=self.address
        )
        self._oled.fill(0)
        self._oled.show()
        self._font = ImageFont.load_default()
        self._image_cls = Image
        self._draw_cls = ImageDraw

    def show(self, fields: dict) -> None:
        """Render a small status screen.

        Expected keys (all optional; missing values render as '--'):
            ax, ay, az        accel in g
            temp_c, rh        DHT11 environment
        """
        if self._oled is None:
            return

        image = self._image_cls.new("1", (self.width, self.height))
        draw = self._draw_cls.Draw(image)

        def fmt(v, spec):
            return format(v, spec) if isinstance(v, (int, float)) else "--"

        line_ax = f"ax {fmt(fields.get('ax'), '+.2f')}g"
        line_ay = f"ay {fmt(fields.get('ay'), '+.2f')}g"
        line_az = f"az {fmt(fields.get('az'), '+.2f')}g"
        line_env = (
            f"T {fmt(fields.get('temp_c'), '4.1f')}C  "
            f"H {fmt(fields.get('rh'), '>3')}%"
        )

        # Default PIL font is ~6x11; four lines fit comfortably in 64 px.
        draw.text((0,  0),  "spyderrobot P1",        font=self._font, fill=255)
        draw.text((0, 14),  line_ax,                 font=self._font, fill=255)
        draw.text((0, 26),  line_ay,                 font=self._font, fill=255)
        draw.text((0, 38),  line_az,                 font=self._font, fill=255)
        draw.text((0, 52),  line_env,                font=self._font, fill=255)

        self._oled.image(image)
        self._oled.show()

    def close(self) -> None:
        if self._oled is not None:
            self._oled.fill(0)
            self._oled.show()
            self._oled = None


if __name__ == "__main__":
    d = OledDisplay()
    d.open()
    d.show({"dist_mm": 432, "temp_c": 21.4, "rh": 42})
