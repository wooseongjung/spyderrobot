"""MPU9250 9-DoF IMU driver (I2C) — v1 end-product part.

This is the IMU the **v1 custom PCB is designed around**. The MPU6050 in
`mpu6050.py` is a Phase 1 bench prototype only; see ADR-0007 in
`docs/10-design-decisions.md`.

The MPU9250 is effectively an MPU6500 (accel + gyro, same register layout
as the MPU6050 at the accel/gyro level) plus an AK8963 magnetometer on a
secondary I²C bus inside the same package.

- Accel/gyro main die: I²C address 0x68 (AD0 low) / 0x69 (AD0 high)
- AK8963 mag die:      I²C address 0x0C, reached via the MPU9250's
                       I²C master bypass (PIN_CFG BYPASS_EN=1) or via
                       slave-passthrough mode

For now this file is a **stub**: register map + dataclass, no bus I/O.
Real body will be implemented in Phase 2 against the NUCLEO-F411RE
(firmware side) and re-used on the Pi only if we need a fallback.

Wiring on the breadboard is identical to the MPU6050 (VCC/GND/SDA/SCL),
so Phase 1 hardware can be reused to bench-test this driver without
changing any jumpers.
"""

from dataclasses import dataclass
from typing import Optional


# ---- Accel/gyro die (same as MPU6050 layout) ----
PWR_MGMT_1   = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H  = 0x43
TEMP_OUT_H   = 0x41
INT_PIN_CFG  = 0x37   # BYPASS_EN bit lives here
USER_CTRL    = 0x6A

# ---- AK8963 magnetometer die (visible at 0x0C via bypass) ----
AK8963_ADDR     = 0x0C
AK8963_WHO_AM_I = 0x00  # should read 0x48
AK8963_ST1      = 0x02
AK8963_HXL      = 0x03  # 6 bytes: HXL HXH HYL HYH HZL HZH
AK8963_ST2      = 0x09
AK8963_CNTL1    = 0x0A

# Full-scale defaults (identical to MPU6050 for accel/gyro; datasheet §5)
ACCEL_SCALE = 16384.0  # LSB/g for ±2 g
GYRO_SCALE  = 131.0    # LSB/(deg/s) for ±250 dps
MAG_SCALE   = 0.15     # µT/LSB in 16-bit mode (datasheet §4.3)


@dataclass
class Imu9Reading:
    accel_g:  tuple[float, float, float]
    gyro_dps: tuple[float, float, float]
    mag_ut:   tuple[float, float, float]
    temp_c:   float


class MPU9250:
    """Stub driver. Register map and dataclass are final; the I²C
    transactions are left as TODO until Phase 2."""

    def __init__(self, bus_id: int = 1, address: int = 0x68):
        self.bus_id = bus_id
        self.address = address
        self._bus = None
        self.error_count = 0

    def open(self) -> None:
        """TODO (Phase 2):
        1. Open SMBus.
        2. Clear PWR_MGMT_1 SLEEP bit.
        3. Set INT_PIN_CFG BYPASS_EN=1 and USER_CTRL I2C_MST_EN=0 so the
           AK8963 is visible directly at 0x0C on the same I²C bus.
        4. Put AK8963 in 16-bit continuous-measurement mode 2 (CNTL1=0x16).
        """
        raise NotImplementedError(
            "MPU9250 driver body is deferred to Phase 2 — the v1 PCB is "
            "designed around this part. Use sensors.mpu6050.MPU6050 for "
            "Phase 1 breadboard work."
        )

    def read(self) -> Optional[Imu9Reading]:
        """TODO (Phase 2): read accel/gyro/temp from 0x3B (14 bytes) and
        the mag X/Y/Z from AK8963 0x03 (6 bytes + ST2 to latch).

        AK8963 ST2 MUST be read after each measurement to unlatch the
        data register — otherwise subsequent reads return stale data.
        """
        raise NotImplementedError("MPU9250.read() — see Phase 2.")

    def close(self) -> None:
        if self._bus is not None:
            self._bus.close()
            self._bus = None


if __name__ == "__main__":
    # When implemented:
    #   python -m sensors.mpu9250
    imu = MPU9250()
    imu.open()
    try:
        for _ in range(10):
            print(imu.read())
    finally:
        imu.close()
