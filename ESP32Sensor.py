#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

#define WIFI_SSID "your_wifi_ssid"
#define WIFI_PASSWORD "your_wifi_password"
#define MQTT_BROKER "your_mqtt_broker_ip"
#define MQTT_TOPIC "home/bedroom_sensor"
#define DHTPIN 4      // GPIO pin where the DHT11 is connected
#define DHTTYPE DHT11 // DHT 11

DHT dht(DHTPIN, DHTTYPE);
WiFiClient espClient;
PubSubClient client(espClient);

const int RECONNECT_DELAY = 5000;  // milliseconds

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void publish_config() {
  String tempConfig = "{\"name\": \"Bedroom Temperature\", \"state_topic\": \"" + String(MQTT_TOPIC) + "\", \"value_template\": \"{{ value_json.temperature }}\", \"unit_of_measurement\": \"°C\", \"unique_id\": \"bedroom_temperature\", \"device\": {\"identifiers\": [\"bedroom_sensor\"], \"name\": \"Bedroom Sensor\", \"model\": \"ESP32\", \"manufacturer\": \"Espressif\"}}";
  String humConfig = "{\"name\": \"Bedroom Humidity\", \"state_topic\": \"" + String(MQTT_TOPIC) + "\", \"value_template\": \"{{ value_json.humidity }}\", \"unit_of_measurement\": \"%\", \"unique_id\": \"bedroom_humidity\", \"device\": {\"identifiers\": [\"bedroom_sensor\"], \"name\": \"Bedroom Sensor\", \"model\": \"ESP32\", \"manufacturer\": \"Espressif\"}}";

  client.publish("homeassistant/sensor/bedroom_temperature/config", tempConfig.c_str(), true);
  client.publish("homeassistant/sensor/bedroom_humidity/config", humConfig.c_str(), true);
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32Client")) {
      Serial.println("connected");
      publish_config();  // Publish the config on connect/reconnect
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(RECONNECT_DELAY);
    }
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  setup_wifi();
  client.setServer(MQTT_BROKER, 1883);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    setup_wifi();
  }

  if (!client.connected()) {
    reconnect();
  }

  client.loop();

  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (isnan(h) || isnan(t)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  String payload = "{\"temperature\": ";
  payload += String(t);
  payload += ", \"humidity\": ";
  payload += String(h);
  payload += "}";

  Serial.print("Publishing message: ");
  Serial.println(payload);
  client.publish(MQTT_TOPIC, payload.c_str());

  delay(60000);  // Delay for 60 seconds before sending the next reading
}
