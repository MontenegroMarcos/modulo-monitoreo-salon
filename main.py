import dotenv
import os
import time
import threading
from datetime import datetime, timedelta
from awsiot import mqqtt_connection_builder
import json
from ultralytics import YOLO
from people_counting import count_people

endpoint = os.getenv("AWS_IOT_ENDPOINT")
cert_path = os.getenv("AWS_IOT_CERT_PATH")
key_path = os.getenv("AWS_IOT_PRIVATE_KEY_PATH")
ca_path = os.getenv("AWS_IOT_CA_PATH")
client_id = os.getenv("AWS_IOT_CLIENT_ID")

def create_mqtt_connection():
    """Create a connection MQTT using .env variable and credentials"""
    if not all([endpoint, cert_path, key_path, ca_path, client_id]):
        missing_vars = [var for var, val in {
            "AWS_IOT_ENDPOINT": endpoint,
            "AWS_IOT_CERT_PATH": cert_path,
            "AWS_IOT_PRIVATE_KEY_PATH": key_path,
            "AWS_IOT_CA_PATH": ca_path,
            "AWS_IOT_CLIENT_ID": client_id
        }.items() if not val]
        
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=endpoint,
        cert_filepath=cert_path,
        pri_key_filepath=key_path,
        ca_filepath=ca_path,
        client_id=client_id,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed
    )

    mqtt_connection.connect()




def on_connection_interrupted(connection, error, **kwargs):
    """Callback when connection is accidentally lost"""
    print("Connection interrupted. error: {}".format(error))

def on_connection_resumed(connection, return_code, session_present, **kwargs):
    """# Callback when an interrupted connection is re-established"""
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

def main_loop():
    """Main Loop that sends each 15 minutes the amount of people and each 5 minutes the enviromental measures"""
    last_people_count_time = datetime.now() - timedelta(minutes=15)
    last_enviroment_time = datetime.now() - timedelta(minutes=5)
    
    while True:
        try:
            current_time = datetime.now()
            
            if (current_time - last_people_count_time).total_seconds() >= 15 * 60:

                people_count:int = count_people(model)
                timestamp_people = current_time.isoformat()

                print(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] People count: {people_count}")

                mqtt_connection.publish(topic="sensors/people", payload=json.dumps({
                     "count": people_count,
                     "timestamp": timestamp_people
                 }))
                
                last_people_count_time = current_time
            
            if (current_time - last_enviroment_time).total_seconds() >= 5 * 60:

                enviroment_measure: List[float] = [12,12,1,3]
                timestamp_env = current_time.isoformat()

                mqtt_connection.publish(topic="sensors/enviroment", payload=json.dumps({
                     "count": enviroment_measure,
                     "timestamp": timestamp_env
                 }))

                print(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] Temperature: {enviroment_measure}°C")
                
                last_enviroment_time = current_time
            
            
            
        except Exception as e:
            print(f"Error in main loop: {e}")
            #Hay que pensar como resolver esta exepcion, si es por falta de conexión mandarla a una DB local.


model = YOLO("yolov8n.pt")

if __name__ == '__main__':
    print("Hello World")
    mqqtt_connection = create_mqtt_connection()
    
    main_loop()

