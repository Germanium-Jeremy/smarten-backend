import paho.mqtt.client as mqtt
import json, os
from django.utils import timezone
from dotenv import load_dotenv
load_dotenv()

class MQTTPublisher:
    def __init__(self):
        self.client = mqtt.Client()
        self.mqtt_broker = os.getenv('MQTT_BROKER', 'localhost')
        self.mqtt_port = int(os.getenv('MQTT_PORT', '1883'))
        self.mqtt_username = os.getenv('MQTT_USERNAME')
        self.mqtt_password = os.getenv('MQTT_PASSWORD')
        self.mqtt_use_tls = os.getenv('MQTT_USE_TLS', 'False').lower() in ('true', '1', 'yes')
        self.command_topic = os.getenv('MQTT_TOPIC_DEVICE_COMMAND', 'smarten/device_command')

        if self.mqtt_username and self.mqtt_password:
            self.client.username_pw_set(self.mqtt_username, self.mqtt_password)

        if self.mqtt_use_tls:
            self.client.tls_set()
            self.client.tls_insecure = False

        self.client.on_publish = self.on_publish
        self.client.on_connect = self.on_connect
        self.connect()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("[MQTT_PUB] Connected to MQTT Broker")
        else:
            print(f"[MQTT_PUB] Failed to connect to MQTT Broker: rc={rc}")

    def on_publish(self, client, userdata, mid):
        print(f"[MQTT_PUB] Message published mid={mid}")

    def connect(self):
        try:
            self.client.reconnect_delay_set(1, 30)
            self.client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"[MQTT_PUB] Connection error: {e}")
            return False

    def publish_command(self, mac_address, command):
        payload = json.dumps({
            "mac_address": mac_address,
            "command": command,
            "timestamp": timezone.now().isoformat()
        })
        try:
            if not self.client.is_connected():
                self.connect()
            result = self.client.publish(self.command_topic, payload, qos=1, retain=False)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"[MQTT_PUB] Command '{command}' sent to {mac_address} on {self.command_topic}")
                return True, "Command sent successfully"
            else:
                error_msg = f"[MQTT_PUB] Publish failed rc={result.rc}"
                print(error_msg)
                return False, error_msg
        except Exception as e:
            error_msg = f"[MQTT_PUB] Publish error: {str(e)}"
            print(error_msg)
            return False, error_msg

# Singleton instance
mqtt_publisher = MQTTPublisher()
