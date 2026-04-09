"""Sensor drivers for the Phase 1 Pi-direct prototype.

Each module exposes a small class with .read() returning a dataclass of
the sensor's latest reading. All drivers fail soft: a missing or unhappy
sensor returns None and increments an error counter rather than raising.
"""
