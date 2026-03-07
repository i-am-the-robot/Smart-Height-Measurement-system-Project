#include <ESP8266WiFi.h>
#include <PubSubClient.h>

const char* ssid = "AcessPoint1";
const char* password = "********";

const char* mqtt_server = "broker.hivemq.com";
const char* sensorTopic = "newJob/sensor";

const int TRIG_PIN = 1;
const int ECHO_PIN = 3; 
const int LED_PIN = LED_BUILTIN;


const float SENSOR_HEIGHT = 194;

WiFiClient espClient;
PubSubClient client(espClient12345);

void setup() {
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    delay(500);
  }
  digitalWrite(LED_PIN, LOW); 
  
  client.setServer(mqtt_server, 1883);
}

void loop() {
  if (!client.connected()) {
    digitalWrite(LED_PIN, HIGH);
    if (client.connect("NodeMCU_Height_Sensor")) {
      digitalWrite(LED_PIN, LOW);
    }
  }
  client.loop();
  

  float height = measureHeight();
  if (height > 0) {
    String heightStr = String(height, 1);
    client.publish(sensorTopic, heightStr.c_str());
  }
  
  delay(1000); 
}

float measureHeight() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  float distance = (duration * 0.0343) / 2.0;
  
 
  if (distance > 0 && distance < 210) {
    return SENSOR_HEIGHT - distance;
  }
  return -1;  
}