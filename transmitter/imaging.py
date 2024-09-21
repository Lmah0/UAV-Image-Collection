from flask import Flask, request, jsonify
from flask_cors import CORS
from math import ceil
import socket
import json
from picamera2 import Picamera2, Preview
import sys
import time
import requests
import threading
from os import path
from pymavlink import mavutil
from io import BytesIO


gcs_url = "http://192.168.1.64:80"
vehicle_port = "udp:127.0.0.1:5006"

DELAY = 1 # Amount of time between taking each picture
picam2 = None
vehicle_connection = None
UDP_PORT = 5005

vehicle_data = {
        "last_time": 0,
        "lat": 0,
        "lon": 0,
        "rel_alt": 0,
        "alt": 0,
        "roll": 0,
        "pitch": 0,
        "yaw": 0,
        "dlat": 0,
        "dlon": 0,
        "dalt": 0,
        "heading": 0
}

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/trigger_camera", methods=["POST"])
def trigger_camera():
    # Requires the amount of images wanting to be taken
    global picam2
    data = request.json
    
    try:
        amount_of_images_requested = int(data["amount_of_images"])
    except Exception as e:
        exit(1)

    if picam2 is None:
        picam2 = Picamera2()
        camera_config = picam2.create_still_configuration()
        picam2.configure(camera_config)
        picam2.start_preview(Preview.NULL)
        picam2.start()
        time.sleep(1)
    else:
        picam2.start()

    for i in range(amount_of_images_requested):
        delay_time_remaining = DELAY - take_picture(i, picam2)
        if delay_time_remaining > 0:
            time.sleep(delay_time_remaining)
    
    picam2.stop()
    return { "message": "Success!"}, 200

def take_picture(image_number, picam2):
    print(f"Beginning capturing capture{image_number}.jpg")
    start_time = time.time()

    # Capture image into a temporary BytesIO object
    image_stream = BytesIO()
    image = picam2.capture_image('main')
    image.save(image_stream, format='JPEG')
    image_stream.seek(0)

    # Serialize vehicle data into a JSON string
    vehicle_data_json = json.dumps(vehicle_data)

    # Send image to GCS
    headers = {} # API Request headers

    files = {
        'file': (f'capture.jpg', image_stream, 'image/jpeg'),
    }
    response = requests.request("POST", f"{gcs_url}/submit", headers=headers, files=files)

    # Send JSON to GCS (note that these need to be sent in a separate API request due to body datatype)
    json_stream = BytesIO(vehicle_data_json.encode('utf-8'))
    json_files = {
        'file': (f'capture.json', json_stream, 'application/json'),
    }
    response = requests.request("POST", f"{gcs_url}/submit", headers=headers, files=json_files)
    
    return time.time() - start_time


def http_error_present(response):
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return True
    return False

def receive_vehicle_position():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", UDP_PORT))

    data = sock.recvfrom(1024)
    items = data[0].decode()[1:-1].split(",")
    message_time = float(items[0])

    if message_time <= vehicle_data["last_time"]:
        return

    vehicle_data["last_time"] = message_time
    vehicle_data["lat"] = float(items[1])
    vehicle_data["lon"] = float(items[2])
    vehicle_data["rel_alt"] = float(items[3])
    vehicle_data["alt"] = float(items[4])
    vehicle_data["roll"] = float(items[5])
    vehicle_data["pitch"] = float(items[6])
    vehicle_data["yaw"] = float(items[7])
    vehicle_data["dlat"] = float(items[8])
    vehicle_data["dlon"] = float(items[9])
    vehicle_data["dalt"] = float(items[10])
    vehicle_data["heading"] = float(items[11])

if __name__ == "__main__":
    if len(sys.argv) == 2:
        gcs_url = sys.argv[1]

    position_thread = threading.Thread(target=receive_vehicle_position, daemon=True)
    position_thread.start()

    print("\nBeginning server with valid vehicle connection...")

    app.run(debug=True, host='0.0.0.0')