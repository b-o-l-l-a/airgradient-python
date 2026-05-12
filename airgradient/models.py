"""Data models for AirGradient sensor readings."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Measures:
    """Air quality measurements from a sensor."""

    # Particulate matter (µg/m³)
    pm01: Optional[float] = None
    pm02: Optional[float] = None  # PM2.5
    pm10: Optional[float] = None
    pm003_count: Optional[int] = None  # particle count >0.3µm

    # Gas
    rco2: Optional[int] = None       # CO2 ppm
    tvoc_raw: Optional[int] = None   # raw VOC index
    nox_raw: Optional[int] = None    # raw NOx index

    # Environment
    atmp: Optional[float] = None     # temperature °C
    rhum: Optional[float] = None     # relative humidity %

    # Device
    wifi: Optional[int] = None       # RSSI dBm
    boot: Optional[int] = None       # boot count
    serialno: Optional[str] = None

    @property
    def atmp_f(self) -> Optional[float]:
        """Temperature in Fahrenheit."""
        if self.atmp is not None:
            return round(self.atmp * 9 / 5 + 32, 2)
        return None

    @property
    def pm25(self) -> Optional[float]:
        """Alias for pm02 (PM2.5)."""
        return self.pm02

    @property
    def aqi_pm25_category(self) -> Optional[str]:
        """EPA AQI category for PM2.5."""
        if self.pm02 is None:
            return None
        pm = self.pm02
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
        fields = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in fields})


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
