from django.core.management.base import BaseCommand
from mqtt_manager.mqtt_subscriber import mqtt_manager
import time

class Command(BaseCommand):
    help = 'Start MQTT subscriber service'

    def handle(self, *args, **options):
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
