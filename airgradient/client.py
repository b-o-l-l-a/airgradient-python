"""AirGradient cloud API client."""
import requests
from typing import List, Optional

from .models import Measures, Location
from .exceptions import AuthenticationError, NotFoundError, AirGradientError

BASE_URL = "https://api.airgradient.com/public/api/v1"


class AirGradientClient:
    """Client for the AirGradient cloud API.

    Args:
        token: Your API token from the AirGradient dashboard
                (General Settings → Connectivity).

    Example::

        client = AirGradientClient(token="your_token")
        measures = client.get_current_measures("your_location_id")
        print(f"CO2: {measures.rco2} ppm")
        print(f"PM2.5: {measures.pm02} µg/m³ ({measures.aqi_pm25_category})")
    """

    def __init__(self, token: str, timeout: int = 10):
        if not token:
            raise AuthenticationError("API token is required.")
        self.token = token
        self.timeout = timeout
        self.session = requests.Session()

    def _get(self, path: str, params: dict = None) -> dict | list:
        params = params or {}
        params["token"] = self.token
        url = f"{BASE_URL}{path}"
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
        except requests.exceptions.ConnectionError as e:
            raise AirGradientError(f"Could not connect to AirGradient API: {e}") from e

        if resp.status_code == 401:
            raise AuthenticationError("Invalid or missing API token.")
        if resp.status_code == 404:
            raise NotFoundError(f"Resource not found: {path}")
        resp.raise_for_status()
        return resp.json()

    def get_locations(self) -> List[Location]:
        """Return all locations registered to your account."""
        data = self._get("/locations")
        return [Location.from_dict(loc) for loc in data]

    def get_current_measures(self, location_id: str) -> Measures:
        """Return the latest measurements for a location."""
        data = self._get(f"/locations/{location_id}/measures/current")
        return Measures.from_dict(data)

    def get_measures_history(
        self,
        location_id: str,
        from_time: str,
        to_time: str,
    ) -> List[Measures]:
        """Return historical measurements for a location.

        Args:
            location_id: Your location ID.
            from_time: ISO 8601 start time, e.g. "2024-01-01T00:00:00Z".
            to_time: ISO 8601 end time.
        """
        data = self._get(
            f"/locations/{location_id}/measures",
            params={"from": from_time, "to": to_time},
        )
        return [Measures.from_dict(d) for d in data]

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
