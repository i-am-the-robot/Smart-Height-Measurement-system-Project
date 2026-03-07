import paho.mqtt.client as mqtt
import csv
import os
from datetime import datetime


broker = "broker.hivemq.com" 
port = 1883

csv_file = "patientHeights.csv"

temp_data = {}

def initializeCsv():
    if not os.path.exists(csv_file):
        with open(csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Email', 'Height (cm)'])
        print(f"Created new CSV file: {csv_file}")

def save_to_csv(email, height):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(csv_file, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, email, height])
    print(f"Data saved: {timestamp} | Email: {email} | Height: {height} cm")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully to MQTT Broker")
        client.subscribe("newJob/email")
        client.subscribe("newJob/height")
        print("Subscribed to topics: newJob/email and newJob/height")
    else:
        print(f"Failed to connect, return code: {rc}")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode('utf-8')
    
    print(f"Received message on topic '{topic}': {payload}")
    
    if topic == "newJob/email":
        temp_data['email'] = payload
        print(f"Email stored: {payload}")
        
    elif topic == "newJob/height":
        temp_data['height'] = payload
        print(f"Height stored: {payload} cm")
    
        save_to_csv(temp_data['email'], temp_data['height'])
        temp_data.clear()
        print("Data pair saved and cleared\n")

def on_log(client, userdata, level, buf):
    """Callback for logging"""
    print(f"Log: {buf}")

def on_disconnect(client, userdata, rc):
    """Callback when client disconnects"""
    if rc != 0:
        print(f"Unexpected disconnection. Return code: {rc}")
    else:
        print("Disconnected successfully")

def main():
    """Main function to run the MQTT server"""
    
    initializeCsv()
    
    client = mqtt.Client("height_measurement_server")
    
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_log = on_log
    client.on_disconnect = on_disconnect
    
    try:
        print(f"Connecting to broker at {broker}:{port}")
        client.connect(broker, port, keepalive=60)
        
        
        print("Server is running. Press Ctrl+C to stop.\n")
        client.loop_forever()
        
    except KeyboardInterrupt:
        print("\nShutting down server...")
        client.disconnect()
        print("Server stopped")
    except Exception as e:
        print(f"Error: {e}")
        client.disconnect()

if __name__ == "__main__":
    main()
