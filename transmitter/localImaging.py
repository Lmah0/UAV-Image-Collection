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


def trigger_camera(amount_of_pictures_requested):
    global picam2

    if picam2 is None:
        picam2 = Picamera2()
        camera_config = picam2.create_still_configuration()
        picam2.configure(camera_config)
        picam2.start_preview(Preview.NULL)
        picam2.start()
        time.sleep(1)
    else:
        picam2.start()

    for i in range(amount_of_pictures_requested):
        start_time = time.time()
        current_time = take_and_send_picture(i, picam2)
        time_elapsed_since_start = current_time - start_time
        delay_time = DELAY - time_elapsed_since_start
        if delay_time > 0:
            time.sleep(delay_time)  # 1 picture per second
    picam2.stop()

def take_and_send_picture(i, picam2):
    print('capturing image %i' % i)
    filepath = '/home/pi/Desktop/SUAV/picam/images/' + f'capture{i}.jpg'
    jsonpath = filepath.rsplit('.', 1)[0] + '.json'
    image = picam2.capture_image('main')

    image.save(filepath, None)

    with open(jsonpath, 'w') as json_file:
        json.dump(vehicle_data, json_file)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please enter the amount of images you want to take.")
        exit(1)
    amount_of_images = sys.argv[1]

    position_thread = threading.Thread(target=receive_vehicle_position, daemon=True)
    position_thread.start()
    trigger_camera(amount_of_images)
    print("Finished taking pictures!")
