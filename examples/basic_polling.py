"""Poll a local AirGradient device every 60 seconds and print readings."""
import os
import time
from airgradient import LocalClient

DEVICE_HOST = os.environ["AIRGRADIENT_HOST"]  # e.g. airgradient_3cdc75bcce40.local

client = LocalClient(DEVICE_HOST)

while True:
    m = client.get_current_measures()
    print(
        f"CO2: {m.rco2} ppm | "
        f"PM2.5: {m.pm02} µg/m³ ({m.aqi_pm25_category}) | "
        f"Temp: {m.atmp_f}°F | "
        f"Humidity: {m.rhum}%"
    )
    time.sleep(60)
