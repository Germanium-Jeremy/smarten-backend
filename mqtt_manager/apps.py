from django.apps import AppConfig
import threading
import logging

class MqttManagerConfig(AppConfig):
    name = 'mqtt_manager'

    def ready(self):
        # Start MQTT subscriber in a background thread when Django starts
        # We use a flag on the settings object to prevent the Django auto-reloader
        # from starting the service twice during development.
        from django.conf import settings
        if not hasattr(settings, '_mqtt_started'):
            settings._mqtt_started = True
            try:
                from mqtt_manager.mqtt_subscriber import mqtt_manager
                # Start the manager in a separate thread to avoid blocking the server boot
                t = threading.Thread(target=mqtt_manager.start, daemon=True)
                t.start()
                logging.getLogger(__name__).info("[✓] MQTT Manager background thread started")
            except Exception as e:
                logging.getLogger(__name__).error(f"[✗] Failed to start MQTT Manager in ready(): {e}")
