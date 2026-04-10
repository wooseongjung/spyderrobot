"""MPU6050 6-DoF IMU driver (I2C).

NOTE — Phase 1 prototype only. The v1 custom PCB is designed around the
MPU9250 (9-DoF) as the end-product IMU; see ADR-0007 in
`docs/10-design-decisions.md`. This driver stays in the repo as the
breadboard bring-up reference, but the Phase 2+ firmware and Pi-side
code target `sensors/mpu9250.py` once that driver is fleshed out.

Default I2C address: 0x68 (AD0 low) or 0x69 (AD0 high).

Wiring (Pi 5):
    VCC  -> 3V3   (pin 1)
    GND  -> GND   (pin 6)
    SDA  -> GPIO2 (pin 3, I2C1_SDA)
    SCL  -> GPIO3 (pin 5, I2C1_SCL)

Enable I2C first:
    sudo raspi-config -> Interface Options -> I2C -> enable
    i2cdetect -y 1     # should show 0x68
"""

from dataclasses import dataclass
from typing import Optional


# MPU6050 register map (subset)
PWR_MGMT_1   = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H  = 0x43
TEMP_OUT_H   = 0x41

ACCEL_SCALE = 16384.0  # LSB/g  for ±2g (default)
GYRO_SCALE  = 131.0    # LSB/(deg/s) for ±250 dps (default)


@dataclass
class ImuReading:
    accel_g: tuple[float, float, float]
    gyro_dps: tuple[float, float, float]
    temp_c: float


class MPU6050:
    def __init__(self, bus_id: int = 1, address: int = 0x68):
        self.bus_id = bus_id
        self.address = address
        self._bus = None
        self.error_count = 0

    def open(self) -> None:
        """Open the I2C bus and wake the device."""
        from smbus2 import SMBus  # lazy import so the module lints off-Pi
        self._bus = SMBus(self.bus_id)
        # Clear SLEEP bit in PWR_MGMT_1 so the device starts sampling.
        self._bus.write_byte_data(self.address, PWR_MGMT_1, 0x00)

    def read(self) -> Optional[ImuReading]:
        """Read accel + gyro + temp. Returns None on bus error."""
        if self._bus is None:
            return None
        try:
            raw = self._bus.read_i2c_block_data(self.address, ACCEL_XOUT_H, 14)
        except OSError:
            self.error_count += 1
            return None

        ax = _to_int16(raw[0],  raw[1])  / ACCEL_SCALE
        ay = _to_int16(raw[2],  raw[3])  / ACCEL_SCALE
        az = _to_int16(raw[4],  raw[5])  / ACCEL_SCALE
        temp_raw = _to_int16(raw[6], raw[7])
        temp_c = temp_raw / 340.0 + 36.53  # per MPU6050 datasheet
        gx = _to_int16(raw[8],  raw[9])  / GYRO_SCALE
        gy = _to_int16(raw[10], raw[11]) / GYRO_SCALE
        gz = _to_int16(raw[12], raw[13]) / GYRO_SCALE
        return ImuReading((ax, ay, az), (gx, gy, gz), temp_c)

    def close(self) -> None:
        if self._bus is not None:
            self._bus.close()
            self._bus = None


def _to_int16(hi: int, lo: int) -> int:
    """Two big-endian bytes -> signed 16-bit int."""
    val = (hi << 8) | lo
    return val - 0x10000 if val & 0x8000 else val


if __name__ == "__main__":
    # Quick smoke test on the Pi:
    #   python -m sensors.mpu6050
    imu = MPU6050()
    imu.open()
    try:
        for _ in range(10):
            print(imu.read())
    finally:
        imu.close()
