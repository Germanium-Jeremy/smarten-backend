import json, os
import threading
import time
from collections import defaultdict, deque
import paho.mqtt.client as mqtt
from django.utils import timezone
from django.db import transaction
from sensors.models import UserSensors
from summarization.models import SensorData
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from dotenv import load_dotenv
load_dotenv()

TOPIC = os.getenv('MQTT_TOPIC_SENSOR_SEND_CAPTURED_DATA', 'smarten/water_reading')
FLUSH_INTERVAL_SEC = 120
MAX_BUFFER_SIZE = 500
GLOBAL_MAX_MESSAGES = 5000

buffers = defaultdict(deque)
buffer_lock = threading.Lock()
last_flush_time = time.time()

def on_connect(client, userdata, flags, rc):
     print(f"MQTT on_connect rc={rc}")
     if rc == 0:
          if not TOPIC:
               print("MQTT TOPIC not configured; set MQTT_TOPIC_SENSOR_SEND_CAPTURED_DATA or use default.")
          else:
               client.subscribe(TOPIC, qos=0)
               print(f"Subscribed to {TOPIC}")
     else:
          print("Connect failed")

def on_message(client, userdata, msg):
     try:
          data = json.loads(msg.payload.decode())
          print("Received data: ", data)
          mac = data.get("mac_address")
          ts = data.get("timestamp")
          # Support both flowRate and flow_rate
          flow = data.get("flow_rate")
          if flow is None:
               flow = data.get("flowRate")
          volume = data.get("volume")
          if volume is None:
               volume = data.get("Volume")
          status = data.get("status", "UNKNOWN")

          try:
               flow_val = float(flow)
          except (TypeError, ValueError):
               flow_val = 0.0
          try:
               volume_val = float(volume)
          except (TypeError, ValueError):
               volume_val = 0.0

          channel_layer = get_channel_layer()
          if channel_layer:
               async_to_sync(channel_layer.group_send)(
                    f"sensor_{mac}",
                    {
                         "type": "sensor_message",
                         "message": {
                              "mac_address": mac,
                              "flow_rate": flow_val,
                              "timestamp": ts,
                              "volume": volume_val,
                              "status": status
                         }
                    }
               )

          row = {"mac_address": mac, "flow": flow_val, "volume": volume_val, "status": status, "timestamp": ts}
          with buffer_lock:
               buffers[mac].append(row)
               if len(buffers[mac]) >= MAX_BUFFER_SIZE:
                    _flush_locked([mac])
     except Exception as e:
          print("on_message error:", e)

def _flush_locked(keys=None):
     to_flush = []
     if keys is None:
          for mac, dq in list(buffers.items()):
               while dq:
                    row = dq.popleft()
                    to_flush.append(row)
     else:
          for mac in keys:
               dq = buffers.get(mac)
               if dq:
                    while dq:
                         row = dq.popleft()
                         to_flush.append(row)
     if not to_flush:
          return
     macs = list({r["mac_address"] for r in to_flush})
     # Map mac_address to all UserSensors (multiple users can have same sensor)
     sensors_map = {}
     for us in UserSensors.objects.select_related('sensor').filter(sensor__mac_address__in=macs):
          sensors_map.setdefault(us.sensor.mac_address, []).append(us)
     objs = []
     for r in to_flush:
          mac = r["mac_address"]
          user_sensors = sensors_map.get(mac, [])
          for user_sensor in user_sensors:
               objs.append(SensorData(
                    sensor=user_sensor,
                    flow_rate=r.get("flow", 0.0),
                    volume=r.get("volume", 0.0),
                    status=r.get("status", "UNKNOWN"),
               ))
     if not objs:
          return
     try:
          batch_size = 1000
          with transaction.atomic():
               SensorData.objects.bulk_create(objs, batch_size=batch_size)
          print(f"Flushed {len(objs)} SensorData records to DB for macs: {macs}")
     except Exception as e:
          print("bulk_create error:", e)

def flusher_loop():
     global last_flush_time
     while True:
          time.sleep(1)
          now = time.time()
          if now - last_flush_time >= FLUSH_INTERVAL_SEC:
               with buffer_lock:
                    _flush_locked()
               last_flush_time = now

def start_mqtt_service():
     client = mqtt.Client()
     client.on_connect = on_connect
     client.on_message = on_message
     client.reconnect_delay_set(1, 30)
     client.connect(os.getenv('MQTT_BROKER'), int(os.getenv('MQTT_PORT')), 60)
     client.loop_start()
     t = threading.Thread(target=flusher_loop, daemon=True)
     t.start()