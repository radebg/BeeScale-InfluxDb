import requests
import os
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timezone

INFLUX_URL    = os.environ["https://eu-central-1-1.aws.cloud2.influxdata.com"]
INFLUX_TOKEN  = os.environ["UsgwX6tr72Z_1Txvr2sTQQFPmz-f3cjnKrJfBOTrn9yf9g2mwlw-elPNPIaMyU9y-3zIhR-FT9T-Y6wwptCu2Q=="]
INFLUX_ORG    = os.environ["BeeScale]
INFLUX_BUCKET = os.environ["ThingSpeak"]
CHANNEL_ID    = os.environ["1283707"]
TS_API_KEY    = os.environ["1YWFEWQU964Y353Z"]

def fetch_and_write():
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds/last.json?api_key={TS_API_KEY}"
    resp = requests.get(url, timeout=10)
    data = resp.json()

    # Proveri da li postoje podaci
    if "field1" not in data or data["field1"] is None:
        print("Nema novih podataka")
        return

    point = (
        Point("beehive")
        .tag("channel", CHANNEL_ID)
        .field("weight",      float(data["field1"] or 0))
        .field("temperature", float(data["field2"] or 0))
        .field("humidity",    float(data["field3"] or 0))
        .field("battery",     float(data["field4"] or 0))
        .time(datetime.now(timezone.utc))
    )

    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    client.write_api(write_options=SYNCHRONOUS).write(bucket=INFLUX_BUCKET, record=point)
    print(f"Upisano: {data}")

fetch_and_write()
```

---

### `requirements.txt`
```
influxdb-client
requests
