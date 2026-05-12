"""Log AirGradient readings to a CSV file."""
import csv
import os
import time
from datetime import datetime, timezone
from airgradient import LocalClient

DEVICE_HOST = os.environ["AIRGRADIENT_HOST"]
OUTPUT_FILE = os.environ.get("AIRGRADIENT_CSV", "readings.csv")
INTERVAL = int(os.environ.get("AIRGRADIENT_INTERVAL", "60"))

FIELDS = ["timestamp", "rco2", "pm01", "pm02", "pm10", "atmp", "atmp_f", "rhum", "tvoc_raw", "wifi"]

client = LocalClient(DEVICE_HOST)

write_header = not os.path.exists(OUTPUT_FILE)
with open(OUTPUT_FILE, "a", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS)
    if write_header:
        writer.writeheader()

    print(f"Logging to {OUTPUT_FILE} every {INTERVAL}s. Ctrl+C to stop.")
    while True:
        m = client.get_current_measures()
        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rco2": m.rco2,
            "pm01": m.pm01,
            "pm02": m.pm02,
            "pm10": m.pm10,
            "atmp": m.atmp,
            "atmp_f": m.atmp_f,
            "rhum": m.rhum,
            "tvoc_raw": m.tvoc_raw,
            "wifi": m.wifi,
        }
        writer.writerow(row)
        f.flush()
        print(row)
        time.sleep(INTERVAL)
