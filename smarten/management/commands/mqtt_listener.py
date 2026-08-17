from django.core.management.base import BaseCommand
import time

class Command(BaseCommand):
    help = 'Start MQTT subscriber service'
    print("[✓] MQTT Listener command initialized")

    def handle(self, *args, **options):
        # Import here, after Django has initialized its app registry.  The
        # subscriber imports Django models to persist sensor readings.
        from mqtt_manager.mqtt_subscriber import mqtt_manager

        self.stdout.write("Starting MQTT Listener...")
        try:
            mqtt_manager.start()
            # Keep running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('MQTT Listener stopped'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {e}'))
            raise
