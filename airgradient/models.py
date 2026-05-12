"""Data models for AirGradient sensor readings."""
from dataclasses import dataclass
from typing import Optional

# Maps camelCase device field names → snake_case model field names
_CAMEL_TO_SNAKE = {
    "pm003Count": "pm003_count",
    "pm005Count": "pm005_count",
    "pm01Count": "pm01_count",
    "pm02Count": "pm02_count",
    "pm50Count": "pm50_count",
    "pm10Count": "pm10_count",
    "pm01Standard": "pm01_standard",
    "pm02Standard": "pm02_standard",
    "pm10Standard": "pm10_standard",
    "pm02Compensated": "pm02_compensated",
    "atmpCompensated": "atmp_compensated",
    "rhumCompensated": "rhum_compensated",
    "tvocIndex": "tvoc_index",
    "tvocRaw": "tvoc_raw",
    "noxIndex": "nox_index",
    "noxRaw": "nox_raw",
    "bootCount": "boot_count",
    "ledMode": "led_mode",
}


@dataclass
class Measures:
    """Air quality measurements from a sensor."""

    # Particulate matter — standard (µg/m³)
    pm01: Optional[float] = None
    pm02: Optional[float] = None
    pm10: Optional[float] = None

    # Particulate matter — ATM-corrected duplicates the device also sends
    pm01_standard: Optional[float] = None
    pm02_standard: Optional[float] = None
    pm10_standard: Optional[float] = None

    # Corrected PM2.5 (humidity-compensated, closer to dashboard value)
    pm02_compensated: Optional[float] = None

    # Particle counts per 100mL
    pm003_count: Optional[float] = None
    pm005_count: Optional[float] = None
    pm01_count: Optional[float] = None
    pm02_count: Optional[float] = None
    pm50_count: Optional[float] = None
    pm10_count: Optional[float] = None

    # Gas
    rco2: Optional[float] = None
    tvoc_index: Optional[float] = None   # processed VOC index (1–500)
    tvoc_raw: Optional[float] = None     # raw Sensirion ticks
    nox_index: Optional[float] = None    # processed NOx index (1–500)
    nox_raw: Optional[float] = None      # raw Sensirion ticks

    # Environment
    atmp: Optional[float] = None
    atmp_compensated: Optional[float] = None
    rhum: Optional[float] = None
    rhum_compensated: Optional[float] = None

    # Device
    wifi: Optional[int] = None
    boot: Optional[int] = None
    boot_count: Optional[int] = None
    serialno: Optional[str] = None
    firmware: Optional[str] = None
    model: Optional[str] = None
    led_mode: Optional[str] = None

    @property
    def atmp_f(self) -> Optional[float]:
        """Temperature in Fahrenheit (uses compensated value if available)."""
        t = self.atmp_compensated if self.atmp_compensated is not None else self.atmp
        if t is not None:
            return round(t * 9 / 5 + 32, 2)
        return None

    @property
    def pm25(self) -> Optional[float]:
        """PM2.5 — compensated if available, otherwise raw."""
        return self.pm02_compensated if self.pm02_compensated is not None else self.pm02

    @property
    def aqi_pm25_category(self) -> Optional[str]:
        """EPA AQI category based on pm25 (compensated when available)."""
        pm = self.pm25
        if pm is None:
            return None
        if pm <= 12.0:
            return "Good"
        elif pm <= 35.4:
            return "Moderate"
        elif pm <= 55.4:
            return "Unhealthy for Sensitive Groups"
        elif pm <= 150.4:
            return "Unhealthy"
        elif pm <= 250.4:
            return "Very Unhealthy"
        else:
            return "Hazardous"

    @classmethod
    def from_dict(cls, data: dict) -> "Measures":
        normalized = {_CAMEL_TO_SNAKE.get(k, k): v for k, v in data.items()}
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in normalized.items() if k in known})


@dataclass
class Location:
    """A registered AirGradient location/device."""
    location_id: str
    name: Optional[str] = None
    timezone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Location":
        return cls(
            location_id=str(data.get("id", "")),
            name=data.get("name"),
            timezone=data.get("timezone"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
        )
