# Smarten Backend ⚙️

The Smarten backend is a robust Django-based system that acts as the bridge between IoT water sensors and the mobile application. It handles data ingestion via MQTT, real-time broadcasting via WebSockets, and device management via a REST API.

## Architecture
- **API Layer**: Django Rest Framework (DRF) providing JWT-secured endpoints.
- **Real-time Layer**: Django Channels using Redis as the channel layer for low-latency WebSocket communication.
- **IoT Layer**: MQTT integration for asynchronous communication with hardware sensors and valves.
- **Database**: PostgreSQL (via Neon.tech) for persistent storage of sensor readings and user data.
- **Storage**: Supabase for handling image uploads and static assets.

## Key Components
- `mqtt_manager`: Handles the MQTT subscriber (ingesting sensor data) and publisher (sending device commands).
- `sensors`: Manages sensor metadata and provides the WebSocket consumers for live data streaming.
- `authentication`: Custom User model and JWT-based security.

## Deployment (Render)
The application is designed to be deployed on Render using Docker.

### Infrastructure Requirements
- **Redis**: Required for the Django Channels layer.
- **PostgreSQL**: Required for the primary database (Neon.tech recommended).
- **MQTT Broker**: Required for IoT connectivity (HiveMQ Cloud recommended).

### Setup Instructions
1.  **Environment Variables**: Configure all variables listed in `.env.example` in the Render dashboard.
2.  **Runtime**: Set the Render runtime to **Docker**.
3.  **Deploy**: Push code to GitHub to trigger the automatic build and deployment.

## Local Development
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Configure `.env` file.
3.  Run migrations:
    ```bash
    python manage.py migrate
    ```
4.  Start the server:
    ```bash
    python manage.py runserver
    ```
