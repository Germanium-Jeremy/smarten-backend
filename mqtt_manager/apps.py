from django.apps import AppConfig
import threading
import logging

class MqttManagerConfig(AppConfig):
    name = 'mqtt_manager'

    def ready(self):
        # Only start the MQTT manager if we are running the ASGI server (Gunicorn/Daphne)
        # and NOT during management commands (like migrate or collectstatic)
        import sys
        if 'manage.py' in sys.argv[0] or 'wsgi' in sys.argv[0]:
            return

        from django.conf import settings
        if not hasattr(settings, '_mqtt_started'):
            settings._mqtt_started = True

            def start_with_delay():
                import time
                # Give Django ample time to fully load the AppRegistry
                time.sleep(10)
                try:
                    from mqtt_manager.mqtt_subscriber import mqtt_manager
                    mqtt_manager.start()
                    logging.getLogger(__name__).info("[✓] MQTT Manager background thread started successfully")
                except Exception as e:
                    logging.getLogger(__name__).error(f"[✗] Failed to start MQTT Manager: {e}")

            t = threading.Thread(target=start_with_delay, daemon=True)
            t.start()
            logging.getLogger(__name__).info("MQTT Manager startup scheduled (preventing AppRegistryNotReady)")
