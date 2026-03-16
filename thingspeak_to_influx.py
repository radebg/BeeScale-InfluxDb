import requests
import os
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timezone

INFLUX_URL    = os.environ["INFLUX_URL"]
INFLUX_TOKEN  = os.environ["INFLUX_TOKEN"]
INFLUX_ORG    = os.environ["INFLUX_ORG"]
INFLUX_BUCKET = os.environ["INFLUX_BUCKET"]
CHANNEL_ID    = os.environ["TS_CHANNEL_ID"]
TS_API_KEY    = os.environ["TS_API_KEY"]

def fetch_and_write():
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={TS_API_KEY}&results=24"
    resp = requests.get(url, timeout=10)
    feeds = resp.json()["feeds"]

    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    for entry in feeds:
        point = Point("BeeScale").tag("channel", CHANNEL_ID)
        has_data = False

        # Tip 1 — senzorski podaci
        if entry.get("field1") is not None:
            point.field("tezina",     float(entry["field1"]))
            point.field("baterija",   float(entry["field2"]))
            point.field("temperatura", float(entry["field3"]))
            point.field("vlaznost",   float(entry["field4"]))
            point.field("rssi",       float(entry["field5"]))
            point.field("snr",        float(entry["field6"]))
            has_data = True

        # Tip 2 — korigovana težina
        if entry.get("field7") is not None:
            point.field("tezina_k", float(entry["field7"]))
            has_data = True

        if has_data:
            # Koristi ThingSpeak timestamp
            ts = datetime.strptime(entry["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            ts = ts.replace(tzinfo=timezone.utc)
            point.time(ts)
            write_api.write(bucket=INFLUX_BUCKET, record=point)
            print(f"Upisano entry {entry['entry_id']}: {entry['created_at']}")

fetch_and_write()
