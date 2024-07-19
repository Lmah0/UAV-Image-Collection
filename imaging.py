from picamera2 import Picamera2, Preview
import sys
import time
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import requests
import socket
import types
import json
from os import path
from picamera2 import Picamera2, Preview
import argparse
import sys
import time
import requests
from threading import Thread

gcs_url = "http://192.168.1.65:80"
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

UDP_PORT = 5005
DELAY = 1

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/trigger_camera", methods=["POST"])
def trigger_camera():
    pass

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

    position_thread = Thread(target=receive_vehicle_position, daemon=True)
    position_thread.start()

    app.run(debug=True, host='0.0.0.0')