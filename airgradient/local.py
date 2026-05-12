"""Local network API client for AirGradient devices.

Communicates directly with the device over your LAN —
no cloud, no token required.
"""
import requests
from typing import Optional

from .models import Measures
from .exceptions import LocalAPIError, ConnectionError as AGConnectionError


class LocalClient:
    """Poll an AirGradient device directly on your local network.

    Args:
        host: IP address or mDNS hostname of the device.
              mDNS format: "airgradient_SERIALNO.local"
              e.g. "airgradient_3cdc75bcce40.local"

    Example::

        # By IP
        client = LocalClient("192.168.1.42")

        # By mDNS (no need to know the IP)
        client = LocalClient("airgradient_3cdc75bcce40.local")

        measures = client.get_current_measures()
        print(f"Temp: {measures.atmp_f}°F, CO2: {measures.rco2} ppm")
    """

    def __init__(self, host: str, timeout: int = 5):
        self.host = host.rstrip("/")
        self.timeout = timeout
        # Ensure no scheme prefix
        if not self.host.startswith("http"):
            self.host = f"http://{self.host}"

    def get_current_measures(self) -> Measures:
        """Fetch the latest readings directly from the device."""
        url = f"{self.host}/measures/current"
        try:
            resp = requests.get(url, timeout=self.timeout)
            resp.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            raise AGConnectionError(
                f"Could not reach device at {self.host}. "
                "Is it powered on and on the same network?"
            ) from e
        except requests.exceptions.HTTPError as e:
            raise LocalAPIError(f"Device returned an error: {e}") from e

        return Measures.from_dict(resp.json())

    def get_config(self) -> dict:
        """Fetch current device configuration."""
        url = f"{self.host}/config"
        try:
            resp = requests.get(url, timeout=self.timeout)
            resp.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            raise AGConnectionError(f"Could not reach device at {self.host}") from e
        return resp.json()

    def set_config(self, config: dict) -> dict:
        """Update device configuration via local API.

        Args:
            config: Dict of config values, e.g. {"mqttBrokerUrl": "mqtt://..."}
        """
        url = f"{self.host}/config"
        try:
            resp = requests.put(url, json=config, timeout=self.timeout)
            resp.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            raise AGConnectionError(f"Could not reach device at {self.host}") from e
        return resp.json()
