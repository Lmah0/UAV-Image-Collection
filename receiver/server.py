import os
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import json
import sys

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

AMOUNT_OF_IMAGES = None

def fetch_amount_of_images():
    # Fetches the amount of images in the geodata directory
    geodata_directory = './geodata/'
    files = os.listdir(geodata_directory)
    jpg_files = [file for file in files if file.endswith('.jpg')]
    number_of_files = len(jpg_files)
    return number_of_files

@app.post('/submit/')
def submit_data():
    file = request.files["file"] #file must be attached in body with name "file"

    # Determine whether it is a jpg or json file
    capture_number = file.filename[6:]
    filename = f'capture{AMOUNT_OF_IMAGES + int(capture_number)}'

    if file.filename.endswith('.json'):
        filename = filename + '.json'
    else:
        filename = filename + '.jpg'
    
    file.save('./geodata/' + filename) #saves the image
    print('Saved file', file.filename)
    return 'ok'

if __name__ == '__main__':
    try:
        amount_of_images = fetch_amount_of_images()
        print(f"Amount of existing images: {amount_of_images}")
        AMOUNT_OF_IMAGES = amount_of_images
        if amount_of_images == None:
            sys.exit(1)
    
    except Exception as e:
        print("Failed to retrieve the amount of existing images.")

    app.run(debug=True, host='0.0.0.0', port=80)