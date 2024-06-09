# MQTT-Sensor-Boxes
A simple enclosure and code for MQTT/Home Assistant connected Sensor Boxes. Powered by Pico W or ESP32 Devices.
---
This project involves setting up multiple temperature and humidity sensors using both Raspberry Pi Pico W and ESP32 devices. The sensors will send data to Home Assistant via an MQTT broker, allowing you to monitor environmental conditions from a central dashboard.

Below is the setup process for Pico W and ESP32 based devices. More information on the 3D Printed Cases is avilable on Printables: 

# Step-by-Step Guide

## Install and Configure Mosquitto MQTT Broker on a Raspberry Pi

1. Install Mosquitto MQTT Broker via SSH/Terminal
```
sudo apt update
sudo apt install -y mosquitto mosquitto-clients
```
2. Start and Enable Mosquitto Service:
``` 
sudo systemctl start mosquitto
sudo systemctl enable mosquitto
```
3. Edit Mosquitto Configuration (if necessary):

Open the Configuration File
```
sudo nano /etc/mosquitto/mosquitto.conf
```

Add the following lines to ensure it listens on all interfaces:
```
listener 1883
allow_anonymous true
```

Save and close the file, then restart Mosquitto:
```
sudo systemctl restart mosquitto
```

## Setup Home Assistant 

1. Install Home Assistant:

Follow the installation guide from the [Home Assistant website](https://www.home-assistant.io/getting-started/). I have Home Assistant running in docker container on my Unraid server, you can run it on a dedicated RPI, Old laptop .etc

2. Add MQTT Integration

- Go to Settings > Devices & Services > Add Integration.
- Search for MQTT and configure it to connect to your MQTT broker (e.g., 192.168.x.xx).

3. Verify MQTT Integration:

- Ensure Home Assistant shows the MQTT integration as connected.

4. Add MQTT Sensor Configuration

- Edit "Configuration.yaml". This can be done via terminal, or the file-editor add-on in Home Assistant
- Add the following code to the end of your Config file, Adjusting the fields as necessary (Changing sensor names is explained later in this guide)

```
mqtt:
  sensor:
    - name: "Bedroom Temperature"
      state_topic: "home/bedroom_sensor"
      value_template: "{{ value_json.temperature }}"
      unit_of_measurement: "°C"
    - name: "Bedroom Humidity"
      state_topic: "home/bedroom_sensor"
      value_template: "{{ value_json.humidity }}"
      unit_of_measurement: "%"
```

5. Validate Configuration and Restart Home Assistant:

- Go to Settings > System > Configuration Validation.
- Restart Home Assistant.

## Setting Up Raspberry Pi Pico W with MicroPython

1. Install MicroPython on Pico W

- Download MicroPython Firmware
- Connect Pico W via USB, hold the BOOTSEL button, and drag the UF2 file to the RPI-RP2 drive.

2. Set Up Thonny IDE

- Download and Install Thonny IDE.
- Go to Tools > Options > Interpreter and select MicroPython (Raspberry Pi Pico).

3. Upload the Required Libraries

- Download simple.py from the MicroPython repository [here](https://github.com/micropython/micropython-lib/tree/master/micropython/umqtt.simple).
- Upload simple.py to Pico W using Thonny.

4. Upload the MicroPython Script

- Download Main.py from this repository
- Update WIFI_SSID, WIFI_PASSWORD, MQTT_BROKER, and MQTT_TOPIC with your details.
- Upload Main.py to the Pico W using Thonny
- Power Cycle the Pico W to ensure the script is running correctly
  
Script Features:
- Auto-reconnects for WiFi and MQTT.
- Publishes sensor data to MQTT.
- Configures sensors via MQTT Discovery for Home Assistant.

## Setting up ESP32 with Arduino IDE

1. Install ESP32 Board Manager in Arduino IDE

- Go to File > Preferences.
- Add the following URL to the Additional Board Manager URLs field:
```
https://dl.espressif.com/dl/package_esp32_index.json
```
- Go to Tools > Board > Boards Manager, search for esp32, and install.

2. Install Required Libraries:

- Go to Sketch > Include Library > Manage Libraries.
- Install DHT sensor library by Adafruit, Adafruit Unified Sensor, and PubSubClient.

3. Download and Upload the Script

- Download the ESP32Code file from this repository
- Update WIFI_SSID, WIFI_PASSWORD, MQTT_BROKER, and MQTT_TOPIC with your details.
- Change the sensor name in the publish_config function as needed.
- Connect your ESP32 to your computer via USB.
- Go to Tools > Board and select ESP32 Dev Module.
- Go to Tools > Port and select the appropriate COM port.
- Click on the Upload button to compile and upload the script to the ESP32.

## Changing Sensor Names for Different Rooms

For both the Pico W and ESP32 scripts, you can change the sensor names by modifying the MQTT_TOPIC and the configuration publishing section:

1. Update "MQTT_TOPIC"

For example, to set up a sensor for the living room, change:

```
# For Pico W
MQTT_TOPIC = 'home/living_room_sensor'
```
```
// For ESP32
#define MQTT_TOPIC "home/living_room_sensor"
```

2. Update Configuration Publishing:

Modify the publish_config function to use new names and unique IDs:
```
# For Pico W
def publish_config(client):
    temp_config = {
        "name": "Living Room Temperature",
        "state_topic": MQTT_TOPIC,
        "value_template": "{{ value_json.temperature }}",
        "unit_of_measurement": "°C",
        "unique_id": "living_room_temperature",
        "device": {
            "identifiers": ["living_room_sensor"],
            "name": "Living Room Sensor",
            "model": "Pico W",
            "manufacturer": "Raspberry Pi"
        }
    }
    
    hum_config = {
        "name": "Living Room Humidity",
        "state_topic": MQTT_TOPIC,
        "value_template": "{{ value_json.humidity }}",
        "unit_of_measurement": "%",
        "unique_id": "living_room_humidity",
        "device": {
            "identifiers": ["living_room_sensor"],
            "name": "Living Room Sensor",
            "model": "Pico W",
            "manufacturer": "Raspberry Pi"
        }
    }
    
    client.publish('homeassistant/sensor/living_room_temperature/config', ujson.dumps(temp_config), retain=True)
    client.publish('homeassistant/sensor/living_room_humidity/config', ujson.dumps(hum_config), retain=True)
```
```
// For ESP32
void publish_config() {
    String tempConfig = "{\"name\": \"Living Room Temperature\", \"state_topic\": \"" + String(MQTT_TOPIC) + "\", \"value_template\": \"{{ value_json.temperature }}\", \"unit_of_measurement\": \"°C\", \"unique_id\": \"living_room_temperature\", \"device\": {\"identifiers\": [\"living_room_sensor\"], \"name\": \"Living Room Sensor\", \"model\": \"ESP32\", \"manufacturer\": \"Espressif\"}}";
    String humConfig = "{\"name\": \"Living Room Humidity\", \"state_topic\": \"" + String(MQTT_TOPIC) + "\", \"value_template\": \"{{ value_json.humidity }}\", \"unit_of_measurement\": \"%\", \"unique_id\": \"living_room_humidity\", \"device\": {\"identifiers\": [\"living_room_sensor\"], \"name\": \"Living Room Sensor\", \"model\": \"ESP32\", \"manufacturer\": \"Espressif\"}}";

    client.publish("homeassistant/sensor/living_room_temperature/config", tempConfig.c_str(), true);
    client.publish("homeassistant/sensor/living_room_humidity/config", humConfig.c_str(), true);
}
```

By following these steps, you will have a robust setup for monitoring temperature and humidity across different rooms using Pico W and ESP32 devices, with data seamlessly integrated into Home Assistant via MQTT.



