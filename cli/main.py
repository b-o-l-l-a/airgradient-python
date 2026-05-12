"""Command-line interface for AirGradient.

Usage:
    ag read --host 192.168.1.42
    ag read --host airgradient_3cdc75bcce40.local
    ag cloud --token YOUR_TOKEN --location YOUR_LOCATION_ID
    ag locations --token YOUR_TOKEN
"""
import argparse
import json
import os
import sys

from airgradient import AirGradientClient, LocalClient, AirGradientError


def cmd_read(args):
    """Read from local device."""
    client = LocalClient(args.host)
    m = client.get_current_measures()

    if args.json:
        print(json.dumps(m.__dict__, indent=2))
        return

    print(f"\n📡 AirGradient — {args.host}")
    print("─" * 35)
    if m.rco2 is not None:
        print(f"  CO2:       {m.rco2} ppm")
    if m.pm02 is not None:
        print(f"  PM2.5:     {m.pm02} µg/m³  ({m.aqi_pm25_category})")
    if m.pm01 is not None:
        print(f"  PM1.0:     {m.pm01} µg/m³")
    if m.pm10 is not None:
        print(f"  PM10:      {m.pm10} µg/m³")
    if m.atmp is not None:
        print(f"  Temp:      {m.atmp}°C  /  {m.atmp_f}°F")
    if m.rhum is not None:
        print(f"  Humidity:  {m.rhum}%")
    if m.tvoc_raw is not None:
        print(f"  TVOC raw:  {m.tvoc_raw}")
    if m.wifi is not None:
        print(f"  WiFi RSSI: {m.wifi} dBm")
    print()


def cmd_cloud(args):
    """Read latest measures from cloud API."""
    token = args.token or os.environ.get("AIRGRADIENT_TOKEN")
    if not token:
        print("Error: provide --token or set AIRGRADIENT_TOKEN env var.")
        sys.exit(1)

    with AirGradientClient(token) as client:
        m = client.get_current_measures(args.location)

    if args.json:
        print(json.dumps(m.__dict__, indent=2))
        return

    print(f"\n☁️  AirGradient Cloud — location {args.location}")
    print("─" * 40)
    if m.rco2 is not None:
        print(f"  CO2:       {m.rco2} ppm")
    if m.pm02 is not None:
        print(f"  PM2.5:     {m.pm02} µg/m³  ({m.aqi_pm25_category})")
    if m.atmp is not None:
        print(f"  Temp:      {m.atmp}°C  /  {m.atmp_f}°F")
    if m.rhum is not None:
        print(f"  Humidity:  {m.rhum}%")
    print()


def cmd_locations(args):
    """List all locations on your account."""
    token = args.token or os.environ.get("AIRGRADIENT_TOKEN")
    if not token:
        print("Error: provide --token or set AIRGRADIENT_TOKEN env var.")
        sys.exit(1)

    with AirGradientClient(token) as client:
        locations = client.get_locations()

    if not locations:
        print("No locations found.")
        return

    print(f"\n{'ID':<15} {'Name':<30} {'Timezone'}")
    print("─" * 60)
    for loc in locations:
        print(f"{loc.location_id:<15} {loc.name or '—':<30} {loc.timezone or '—'}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="ag",
        description="AirGradient CLI — read air quality data from your device or the cloud.",
    )
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Local read
    read_parser = subparsers.add_parser("read", help="Read from a local device")
    read_parser.add_argument(
        "--host", required=True,
        help='Device IP or mDNS hostname (e.g. "airgradient_SERIAL.local")'
    )
    read_parser.set_defaults(func=cmd_read)

    # Cloud read
    cloud_parser = subparsers.add_parser("cloud", help="Read from cloud API")
    cloud_parser.add_argument("--token", help="API token (or set AIRGRADIENT_TOKEN)")
    cloud_parser.add_argument("--location", required=True, help="Location ID")
    cloud_parser.set_defaults(func=cmd_cloud)

    # List locations
    locs_parser = subparsers.add_parser("locations", help="List your cloud locations")
    locs_parser.add_argument("--token", help="API token (or set AIRGRADIENT_TOKEN)")
    locs_parser.set_defaults(func=cmd_locations)

    args = parser.parse_args()
    try:
        args.func(args)
    except AirGradientError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
