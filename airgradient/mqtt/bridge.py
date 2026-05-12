"""MQTT bridge — poll a local AirGradient device and publish to an MQTT broker.

Supports any broker (Mosquitto, HiveMQ, Home Assistant's built-in broker, etc.)

Usage::

    from airgradient.mqtt.bridge import MQTTBridge

    bridge = MQTTBridge(
        device_host="airgradient_3cdc75bcce40.local",
        broker_url="mqtt://localhost:1883",
        topic_prefix="airgradient/home/office",
        interval=30,
    )
    bridge.run()  # blocks, polls every `interval` seconds

Or from the CLI:
    python -m airgradient.mqtt.bridge \\
        --host airgradient_3cdc75bcce40.local \\
        --broker mqtt://localhost:1883 \\
        --topic airgradient/office \\
        --interval 30
"""
import json
import time
import logging
import argparse
from urllib.parse import urlparse

try:
    import paho.mqtt.client as mqtt
except ImportError:
    raise ImportError(
        "paho-mqtt is required for the MQTT bridge. "
        "Install it with: pip install paho-mqtt"
    )

from airgradient import LocalClient, AirGradientError

logger = logging.getLogger(__name__)


class MQTTBridge:
    """Poll a local AirGradient device and publish readings to MQTT.

    Args:
        device_host: IP or mDNS hostname of the AirGradient device.
        broker_url: MQTT broker URL, e.g. "mqtt://localhost:1883" or
                    "mqtts://user:pass@broker.example.com:8883".
        topic_prefix: Base MQTT topic. Readings published as subtopics
                      (e.g. "{prefix}/pm25", "{prefix}/co2") and as a
                      combined JSON payload at "{prefix}/state".
        interval: Polling interval in seconds (default: 30).
    """

    def __init__(
        self,
        device_host: str,
        broker_url: str,
        topic_prefix: str = "airgradient",
        interval: int = 30,
    ):
        self.device = LocalClient(device_host)
        self.topic_prefix = topic_prefix.rstrip("/")
        self.interval = interval
        self._client = self._build_mqtt_client(broker_url)

    def _build_mqtt_client(self, broker_url: str) -> mqtt.Client:
        parsed = urlparse(broker_url)
        client = mqtt.Client()

        if parsed.username:
            client.username_pw_set(parsed.username, parsed.password)
        if parsed.scheme == "mqtts":
            client.tls_set()

        host = parsed.hostname or "localhost"
        port = parsed.port or (8883 if parsed.scheme == "mqtts" else 1883)
        client.connect(host, port)
        return client

    def _publish(self, measures):
        """Publish individual metric topics + a combined state topic."""
        topic_map = {
            "co2":      measures.rco2,
            "pm01":     measures.pm01,
            "pm25":     measures.pm02,
            "pm10":     measures.pm10,
            "temp_c":   measures.atmp,
            "temp_f":   measures.atmp_f,
            "humidity": measures.rhum,
            "tvoc_raw": measures.tvoc_raw,
            "wifi":     measures.wifi,
        }
        for key, value in topic_map.items():
            if value is not None:
                self._client.publish(
                    f"{self.topic_prefix}/{key}",
                    payload=str(value),
                    retain=True,
                )

        # Combined JSON state (useful for Home Assistant MQTT sensor)
        state = {k: v for k, v in topic_map.items() if v is not None}
        state["aqi_category"] = measures.aqi_pm25_category
        self._client.publish(
            f"{self.topic_prefix}/state",
            payload=json.dumps(state),
            retain=True,
        )
        logger.info("Published to %s: CO2=%s ppm, PM2.5=%s µg/m³",
                    self.topic_prefix, measures.rco2, measures.pm02)

    def run(self):
        """Start polling loop. Blocks until interrupted."""
        logger.info(
            "Starting MQTT bridge: device=%s, topic=%s, interval=%ds",
            self.device.host, self.topic_prefix, self.interval,
        )
        self._client.loop_start()
        try:
            while True:
                try:
                    measures = self.device.get_current_measures()
                    self._publish(measures)
                except AirGradientError as e:
                    logger.warning("Failed to read from device: %s", e)
                time.sleep(self.interval)
        except KeyboardInterrupt:
            logger.info("Bridge stopped.")
        finally:
            self._client.loop_stop()
            self._client.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

    parser = argparse.ArgumentParser(description="AirGradient → MQTT bridge")
    parser.add_argument("--host", required=True, help="Device IP or mDNS hostname")
    parser.add_argument("--broker", required=True, help="MQTT broker URL")
    parser.add_argument("--topic", default="airgradient", help="MQTT topic prefix")
    parser.add_argument("--interval", type=int, default=30, help="Poll interval (seconds)")
    args = parser.parse_args()

    bridge = MQTTBridge(
        device_host=args.host,
        broker_url=args.broker,
        topic_prefix=args.topic,
        interval=args.interval,
    )
    bridge.run()
