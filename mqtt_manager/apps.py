from django.apps import AppConfig
import threading
import logging

class MqttManagerConfig(AppConfig):
    name = 'mqtt_manager'

    def ready(self):
        # COMPLETELY DISABLE automatic startup in apps.py
        # The AppRegistryNotReady error indicates that even delayed startup
        # in ready() is too early or interfering with the Gunicorn worker boot.
        pass
