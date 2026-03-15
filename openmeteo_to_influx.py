import requests
import os
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timezone

INFLUX_URL    = os.environ["INFLUX_URL"]
INFLUX_TOKEN  = os.environ["INFLUX_TOKEN"]
INFLUX_ORG    = os.environ["INFLUX_ORG"]
INFLUX_BUCKET = os.environ["INFLUX_BUCKET"]

def fetch_and_write():
    url = "https://api.open-meteo.com/v1/forecast?latitude=44.5718&longitude=20.60488&current=temperature_2m,wind_speed_10m&timezone=Europe%2FBerlin&forecast_days=1"

    resp = requests.get(url, timeout=10)
    current = resp.json()["current"]

    point = (
        Point("weather")
        .tag("location", "Sopot")
        .field("temperatura", float(current["temperature_2m"]))
        .field("vetar",       float(current["wind_speed_10m"]))
        .time(datetime.now(timezone.utc))
    )

    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    client.write_api(write_options=SYNCHRONOUS).write(bucket=INFLUX_BUCKET, record=point)
    print(f"Upisano: {current['temperature_2m']}°C, vetar {current['wind_speed_10m']} km/h")

fetch_and_write()
