import json, asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from mqtt_manager.mqtt_subscriber import mqtt_manager
import json

class SensorDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Start MQTT service when first WebSocket connects
        mqtt_manager.start()

        self.mac_address = self.scope['url_route']['kwargs']['mac_address']
        self.group_name = f'sensor_{self.mac_address}'

        # Join room group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from room group
    async def sensor_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'data': message
        }))

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f'notify_{self.user_id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def notify_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))
