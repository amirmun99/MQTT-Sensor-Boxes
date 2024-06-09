import time
import network
import dht
from machine import Pin, reset
from umqtt.simple import MQTTClient
import ujson

# Replace with your WiFi credentials
WIFI_SSID = 'your_wifi_ssid'
WIFI_PASSWORD = 'your_wifi_password'

# Replace with your MQTT broker details
MQTT_BROKER = 'your_mqtt_broker_ip'
MQTT_PORT = 1883
MQTT_TOPIC = 'home/bedroom_sensor'

# Constants
RECONNECT_DELAY = 5  # seconds

# Initialize DHT11
dht_sensor = dht.DHT11(Pin(15))

# Connect to WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    print('Connecting to WiFi...')
    while not wlan.isconnected():
        time.sleep(RECONNECT_DELAY)
        print('Retrying WiFi connection...')
    print('Connected to WiFi:', wlan.ifconfig())

# Connect to MQTT broker
def connect_mqtt():
    client = MQTTClient('PicoW', MQTT_BROKER, port=MQTT_PORT)
    while True:
        try:
            client.connect()
            print('Connected to MQTT broker')
            return client
        except OSError as e:
            print('Failed to connect to MQTT broker:', e)
            time.sleep(RECONNECT_DELAY)
            print('Retrying MQTT connection...')

def publish_config(client):
    temp_config = {
        "name": "Bedroom Temperature",
        "state_topic": MQTT_TOPIC,
        "value_template": "{{ value_json.temperature }}",
        "unit_of_measurement": "°C",
        "unique_id": "bedroom_temperature",
        "device": {
            "identifiers": ["bedroom_sensor"],
            "name": "Bedroom Sensor",
            "model": "Pico W",
            "manufacturer": "Raspberry Pi"
        }
    }
    
    hum_config = {
        "name": "Bedroom Humidity",
        "state_topic": MQTT_TOPIC,
        "value_template": "{{ value_json.humidity }}",
        "unit_of_measurement": "%",
        "unique_id": "bedroom_humidity",
        "device": {
            "identifiers": ["bedroom_sensor"],
            "name": "Bedroom Sensor",
            "model": "Pico W",
            "manufacturer": "Raspberry Pi"
        }
    }
    
    client.publish('homeassistant/sensor/bedroom_temperature/config', ujson.dumps(temp_config), retain=True)
    client.publish('homeassistant/sensor/bedroom_humidity/config', ujson.dumps(hum_config), retain=True)

def main():
    connect_wifi()
    mqtt_client = connect_mqtt()
    publish_config(mqtt_client)
    
    while True:
        try:
            dht_sensor.measure()
            temp = dht_sensor.temperature()
            hum = dht_sensor.humidity()
            
            payload = '{{"temperature": {}, "humidity": {}}}'.format(temp, hum)
            mqtt_client.publish(MQTT_TOPIC, payload)
            
            print('Published:', payload)
        except OSError as e:
            print('Error publishing data:', e)
            mqtt_client = connect_mqtt()  # Reconnect MQTT if publish fails
        
        time.sleep(60)  # Delay between readings

if __name__ == '__main__':
    main()
