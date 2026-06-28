# Smart Height Measurement System

An IoT-based height measurement system that uses an ultrasonic sensor on a NodeMCU to measure a person's height and publish it wirelessly over MQTT. A web interface displays the live reading and lets the user submit it alongside their email for logging. A Python data monitor subscribes to the same MQTT broker and saves all submissions to a CSV file.

---

## Overview

The Smart Height Measurement System is designed to automate the process of recording patient or user heights. The NodeMCU continuously measures the distance from a fixed sensor mount to the top of a person's head, calculates the height, and publishes the result over MQTT via WiFi. The web interface receives the live sensor reading in real time, allows the user to enter their email, and submits the measurement. The Python data monitor runs on a PC or server, listens for submissions, and appends each entry with a timestamp to a CSV file for record keeping.

---

## System Architecture

```
[HC-SR04 Sensor]
       |
[NodeMCU V3 (ESP8266)]
       | WiFi / MQTT
[HiveMQ Public Broker]
       |
   ┌───┴────────────────┐
   |                    |
[Web Interface]   [Data Monitor]
(HTML + JS)       (Python)
   |                    |
[User submits     [Saves to
 email + height]   CSV file]
```

---

## Features

- Real-time height measurement via HC-SR04 ultrasonic sensor
- Wireless data transmission over MQTT (HiveMQ public broker)
- Live height display on a web interface — no page refresh needed
- Email-linked measurement submission
- Manual height entry mode — allows height to be entered manually if the sensor is unavailable
- Python data monitor — logs all submissions to a timestamped CSV file
- LED status indicator on the NodeMCU for WiFi and MQTT connection state

---

## Hardware Components

| Component | Quantity | Purpose |
|---|---|---|
| NodeMCU V3 (ESP8266) | 1 | Main microcontroller and WiFi client |
| HC-SR04 Ultrasonic Sensor | 1 | Measures distance to top of head |
| LED | 1 | WiFi / MQTT connection status indicator |
| Power Supply | 1 | Powers the NodeMCU and sensor |
| Mounting Frame | 1 | Holds sensor at a fixed known height |

---

## Circuit Diagram

![Circuit Diagram](Height_Measusuring%20circuit.bmp)

---

## Pin Mapping (NodeMCU V3)

| NodeMCU Pin | Connected To | Role |
|---|---|---|
| TX (GPIO1) | HC-SR04 TRIG | Ultrasonic trigger output |
| RX (GPIO3) | HC-SR04 ECHO | Ultrasonic echo input |
| LED_BUILTIN | — | WiFi / MQTT status indicator |

---

## MQTT Topics

| Topic | Publisher | Subscriber | Content |
|---|---|---|---|
| `newJob/sensor` | NodeMCU | Web interface | Raw height reading in cm |
| `newJob/email` | Web interface | Data Monitor | User's email address |
| `newJob/height` | Web interface | Data Monitor | Confirmed height in cm |

---

## Repository Structure

```
Smart-Height-Measurement-system-Project/
├── height_Measurement.ino        # Arduino sketch for NodeMCU
├── Ultrasonic Measurement....html # Web interface
├── Data_Monitor.py               # Python MQTT subscriber and CSV logger
├── Height_Measusuring circuit.bmp # Circuit schematic
├── LICENSE
└── README.md
```

---

## Getting Started

### Prerequisites

- [Arduino IDE](https://www.arduino.cc/en/software) with the ESP8266 board package installed
- The following Arduino libraries (install via Library Manager):
  - `ESP8266WiFi` (included with ESP8266 board package)
  - `PubSubClient` by Nick O'Leary
- Python 3.x with the `paho-mqtt` library:
  ```bash
  pip install paho-mqtt
  ```
- A modern web browser (Chrome, Firefox, Edge) for the web interface

### 1. Configure and Upload the Arduino Sketch

1. Open `height_Measurement.ino` in Arduino IDE
2. Update your WiFi credentials:
   ```cpp
   const char* ssid = "YourNetworkName";
   const char* password = "YourPassword";
   ```
3. Set the sensor mount height in centimetres:
   ```cpp
   const float SENSOR_HEIGHT = 194;
   ```
   This should be the exact height of the sensor from the floor. The sketch subtracts the measured distance from this value to calculate the person's height.
4. Select your board: Tools > Board > `NodeMCU 1.0 (ESP-12E Module)`
5. Upload the sketch

### 2. Run the Data Monitor

```bash
python Data_Monitor.py
```

The script connects to the HiveMQ public broker, subscribes to `newJob/email` and `newJob/height`, and saves each submission to `patientHeights.csv` in the same directory. The CSV is created automatically if it does not exist.

### 3. Open the Web Interface

Open `Ultrasonic Measurement....html` in a web browser. The page connects automatically to the HiveMQ broker over WebSocket and begins displaying live height readings from the sensor. Enter an email address and click Submit to log the measurement.

---

## How It Works

### NodeMCU (height_Measurement.ino)

The NodeMCU connects to WiFi on startup, indicated by the onboard LED blinking during connection and turning solid once connected. It then connects to the HiveMQ public MQTT broker.

Every second, the `measureHeight()` function triggers the HC-SR04 sensor and calculates the person's height:

```
distance (cm) = pulse duration (us) * 0.0343 / 2
height (cm) = SENSOR_HEIGHT - distance
```

Valid readings (between 0 and 210 cm distance) are published to the `newJob/sensor` topic as a string. Invalid readings (no echo or out of range) return `-1` and are not published.

### Web Interface (Ultrasonic Measurement....html)

The web page connects to the HiveMQ broker over a secure WebSocket (`wss://`) on load. It subscribes to `newJob/sensor` and updates the height display in real time as readings arrive. When the user enters their email and clicks Submit, the page publishes the email to `newJob/email` and the current height to `newJob/height`. A manual mode checkbox allows the user to type in a height value instead of using the live sensor reading.

### Data Monitor (Data_Monitor.py)

The Python script connects to the HiveMQ broker and subscribes to both `newJob/email` and `newJob/height`. It uses a temporary dictionary (`temp_data`) to pair the two values — when the height arrives, it assumes the email has already been received, writes both to `patientHeights.csv` with a timestamp, and clears the buffer.

CSV format:

```
Timestamp, Email, Height (cm)
2025-01-26 16:40:06, user@example.com, 172.3
```

---

## Sensor Height Calibration

The `SENSOR_HEIGHT` constant in the sketch must match the actual height of the sensor from the floor. To calibrate:

1. Mount the sensor at a fixed position directly above where the person will stand
2. Measure the distance from the sensor to the floor in centimetres
3. Set `SENSOR_HEIGHT` to that value before uploading

---

## Known Limitations

- Uses the HiveMQ public broker — not suitable for sensitive or private data in a production environment
- The data monitor assumes email always arrives before height; if messages arrive out of order, a record may be saved with a missing email
- No authentication on the MQTT topics — anyone subscribed to the same broker and topics can see the data

---

## Future Improvements

- Use a private or authenticated MQTT broker for data privacy
- Add message ordering protection in the data monitor
- Display a history of recent measurements on the web interface
- Send a confirmation email to the user after their height is logged

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
