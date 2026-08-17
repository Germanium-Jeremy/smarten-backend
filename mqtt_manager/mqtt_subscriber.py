import json, os, asyncio, threading, time
from collections import defaultdict, deque
import paho.mqtt.client as mqtt
from django.utils import timezone
from django.db import transaction
from sensors.models import UserSensors
from summarization.models import SensorData
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from dotenv import load_dotenv

load_dotenv()

# Configuration
MQTT_TOPIC = os.getenv('MQTT_TOPIC_SENSOR_READ', 'smarten/sensor/+/read')
FLUSH_INTERVAL_SEC = 120
MAX_BUFFER_SIZE = 500

class MQTTManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.buffers = defaultdict(deque)
        self.buffer_lock = threading.Lock()
        self.last_flush_time = time.time()
        self.client = None
        self.running = False
        self._initialized = True

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            if MQTT_TOPIC:
                client.subscribe(MQTT_TOPIC, qos=1)
                print(f"[✓] MQTT subscribed to {MQTT_TOPIC}")
        else:
            print(f"[✗] MQTT connection failed with rc={rc}")

    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            mac = data.get("mac_address")
            ts = data.get("timestamp")
            flow = data.get("flow_rate") or data.get("flowRate")
            volume = data.get("volume") or data.get("Volume")
            status = data.get("status", "UNKNOWN")

            try:
                flow_val = float(flow) if flow else 0.0
            except (TypeError, ValueError):
                flow_val = 0.0

            try:
                volume_val = float(volume) if volume else 0.0
            except (TypeError, ValueError):
                volume_val = 0.0

            # Send via WebSocket (non-blocking, handles errors)
            self._send_websocket_message(mac, {
                "mac_address": mac,
                "flow_rate": flow_val,
                "timestamp": ts,
                "volume": volume_val,
                "status": status
            })

            # Buffer for database
            row = {
                "mac_address": mac,
                "flow": flow_val,
                "volume": volume_val,
                "status": status,
                "timestamp": ts
            }

            with self.buffer_lock:
                self.buffers[mac].append(row)
                if len(self.buffers[mac]) >= MAX_BUFFER_SIZE:
                    self._flush_locked([mac])

        except Exception as e:
            print(f"[✗] MQTT message processing error: {e}")

    def _send_websocket_message(self, mac, message):
        """Send message to WebSocket clients without blocking"""
        try:
            channel_layer = get_channel_layer()
            if not channel_layer:
                print(f"[!] Channel layer unavailable, buffering for {mac}")
                return

            group_name = f"sensor_{mac}"

            # Use async_to_sync for thread-safe channel layer access
            async def send_group():
                await channel_layer.group_send(
                    group_name,
                    {
                        "type": "sensor_message",
                        "message": message
                    }
                )

            # Run in a thread pool to avoid blocking the MQTT network thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(async_to_sync(send_group))
                future.result(timeout=5)

        except Exception as e:
            print(f"[✗] Failed to send WebSocket message for {mac}: {e}")

    def _flush_locked(self, keys=None):
        to_flush = []
        if keys is None:
            for mac, dq in list(self.buffers.items()):
                while dq:
                    to_flush.append(dq.popleft())
        else:
            for mac in keys:
                dq = self.buffers.get(mac)
                if dq:
                    while dq:
                        to_flush.append(dq.popleft())

        if not to_flush:
            return

        macs = list({r["mac_address"] for r in to_flush})
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
            with transaction.atomic():
                SensorData.objects.bulk_create(objs, batch_size=1000)
            print(f"Flushed {len(objs)} SensorData records to DB for macs: {macs}")
        except Exception as e:
            print(f"bulk_create error: {e}")

    def flusher_loop(self):
        while self.running:
            time.sleep(1)
            now = time.time()
            if now - self.last_flush_time >= FLUSH_INTERVAL_SEC:
                with self.buffer_lock:
                    self._flush_locked()
                self.last_flush_time = now

    def start(self):
        if self.running:
            return

        self.running = True
        self.client = mqtt.Client()

        # Authentication
        username = os.getenv('MQTT_USERNAME')
        password = os.getenv('MQTT_PASSWORD')
        if username and password:
            self.client.username_pw_set(username, password)

        # TLS
        if os.getenv('MQTT_USE_TLS', 'False').lower() in ('true', '1', 'yes'):
            self.client.tls_set()
            self.client.tls_insecure = False

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.reconnect_delay_set(1, 30)

        try:
            mqtt_broker = os.getenv('MQTT_BROKER', 'localhost')
            mqtt_port = int(os.getenv('MQTT_PORT', '1883'))
            self.client.connect(mqtt_broker, mqtt_port, 60)
            self.client.loop_start()

            flusher_thread = threading.Thread(target=self.flusher_loop, daemon=True)
            flusher_thread.start()

            print("[✓] MQTT Manager started successfully")
        except Exception as e:
            print(f"[✗] Failed to start MQTT Manager: {e}")
            self.running = False
            raise

# Global instance
mqtt_manager = MQTTManager()

def start_mqtt_service():
    mqtt_manager.start()
