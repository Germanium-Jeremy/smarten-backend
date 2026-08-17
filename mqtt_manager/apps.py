from django.apps import AppConfig
import threading
import logging
import time

class MqttManagerConfig(AppConfig):
    name = 'mqtt_manager'

    def ready(self):
        # Start MQTT subscriber in a background thread when Django starts
        # We use a flag on the settings object to prevent the Django auto-reloader
        # from starting the service twice during development.
        from django.conf import settings
        if not hasattr(settings, '_mqtt_started'):
            settings._mqtt_started = True

            def start_with_delay():
                # Give Django a few seconds to fully load the AppRegistry
                # and database connections before starting the MQTT manager
                time.sleep(5)
                try:
                    from mqtt_manager.mqtt_subscriber import mqtt_manager
                    mqtt_manager.start()
                    logging.getLogger(__name__).info("[✓] MQTT Manager background thread started successfully after delay")
                except Exception as e:
                    logging.getLogger(__name__).error(f"[✗] Failed to start MQTT Manager after delay: {e}")

            t = threading.Thread(target=start_with_delay, daemon=True)
            t.start()
            logging.getLogger(__name__).info("MQTT Manager startup scheduled (delayed to avoid AppRegistryNotReady)")
