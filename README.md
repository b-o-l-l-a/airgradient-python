# airgradient-python

A Python client library for [AirGradient](https://www.airgradient.com/) air quality monitors.

Supports the **cloud API**, **local device API**, an **MQTT bridge**, and a **CLI tool**.

## Features

- 📡 **Local API** — poll your device directly over LAN (no cloud, no token)
- ☁️ **Cloud API** — pull current and historical data from the AirGradient dashboard API
- 🔌 **MQTT bridge** — publish readings to any broker (Home Assistant, Node-RED, InfluxDB via Telegraf, etc.)
- 🖥️ **CLI** — read data from your terminal with `ag read` or `ag cloud`
- 📊 **EPA AQI categories** — PM2.5 levels interpreted automatically
- 🌡️ **°F conversion** built in (useful for Colorado winters)

## Installation

```bash
pip install airgradient

# With MQTT support
pip install airgradient[mqtt]
```

## Quick Start

### Local device (same network, no token needed)

```python
from airgradient import LocalClient

# Use your device's IP or its mDNS name (shown on device screen during setup)
client = LocalClient("airgradient_3cdc75bcce40.local")
m = client.get_current_measures()

print(f"CO2:   {m.rco2} ppm")
print(f"PM2.5: {m.pm02} µg/m³  ({m.aqi_pm25_category})")
print(f"Temp:  {m.atmp_f}°F")
```

### Cloud API

```python
from airgradient import AirGradientClient

with AirGradientClient(token="your_token") as client:
    # List your locations
    for loc in client.get_locations():
        print(loc.location_id, loc.name)

    # Get latest readings
    m = client.get_current_measures("your_location_id")
    print(f"CO2: {m.rco2} ppm")
```

> **Getting your token:** AirGradient dashboard → hamburger menu → General Settings → Connectivity tab → enable API access.

### MQTT Bridge

Publish readings to a local MQTT broker every 30 seconds:

```python
from airgradient.mqtt.bridge import MQTTBridge

bridge = MQTTBridge(
    device_host="airgradient_3cdc75bcce40.local",
    broker_url="mqtt://localhost:1883",
    topic_prefix="airgradient/office",
    interval=30,
)
bridge.run()
```

Topics published:
```
airgradient/office/co2        → "422"
airgradient/office/pm25       → "5.2"
airgradient/office/temp_f     → "71.6"
airgradient/office/humidity   → "38"
airgradient/office/state      → {"co2": 422, "pm25": 5.2, ...}
```

Or from the command line:
```bash
python -m airgradient.mqtt.bridge \
  --host airgradient_3cdc75bcce40.local \
  --broker mqtt://localhost:1883 \
  --topic airgradient/office \
  --interval 30
```

### CLI

```bash
# Read from a local device
ag read --host airgradient_3cdc75bcce40.local

# Read from cloud
ag cloud --token YOUR_TOKEN --location YOUR_LOCATION_ID

# List your cloud locations
ag locations --token YOUR_TOKEN

# JSON output
ag read --host 192.168.1.42 --json
```

## Data Fields

| Field | Description | Unit |
|---|---|---|
| `rco2` | CO2 concentration | ppm |
| `pm02` / `pm25` | PM2.5 particulate matter | µg/m³ |
| `pm01` | PM1.0 | µg/m³ |
| `pm10` | PM10 | µg/m³ |
| `atmp` | Temperature | °C |
| `atmp_f` | Temperature | °F |
| `rhum` | Relative humidity | % |
| `tvoc_raw` | Raw TVOC index | — |
| `wifi` | WiFi signal strength | dBm |

## EPA AQI Categories (PM2.5)

| µg/m³ | Category |
|---|---|
| 0–12 | Good |
| 12.1–35.4 | Moderate |
| 35.5–55.4 | Unhealthy for Sensitive Groups |
| 55.5–150.4 | Unhealthy |
| 150.5–250.4 | Very Unhealthy |
| 250.5+ | Hazardous |

## Development

```bash
git clone https://github.com/yourusername/airgradient-python
cd airgradient-python
pip install -e ".[dev,mqtt]"
pytest
```

## Planned Integrations

- [ ] InfluxDB exporter
- [ ] Prometheus metrics endpoint
- [ ] Home Assistant MQTT auto-discovery config generator
- [ ] CSV logger (see `examples/log_to_csv.py`)
- [ ] Alerting (PM2.5 / CO2 threshold notifications)

## License

MIT
