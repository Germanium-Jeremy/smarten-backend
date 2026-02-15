from django.apps import AppConfig
import threading

class MqttManagerConfig(AppConfig):
    name = 'mqtt_manager'
    import threading

    def ready(self):
        # Start MQTT subscriber only once (avoid multiple starts in dev server reloads)
        from django.conf import settings
        if not hasattr(settings, '_mqtt_started'):
            settings._mqtt_started = True
            try:
                from mqtt_manager.mqtt_subscriber import start_mqtt_service
                t = threading.Thread(target=start_mqtt_service, daemon=True)
                t.start()
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Failed to start MQTT subscriber: {e}")
