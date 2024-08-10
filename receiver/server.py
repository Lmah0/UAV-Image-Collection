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

# @app.post('/submit/')
# def submit_data():
#     file = request.files["file"] #file must be attached in body with name "file"

#     # Determine whether it is a jpg or json file
#     capture_number = file.filename[6:]
#     filename = f'capture{AMOUNT_OF_IMAGES + int(capture_number)}'

#     if file.filename.endswith('.json'):
#         filename = filename + '.json'
#     else:
#         filename = filename + '.jpg'
    
#     file.save('./geodata/' + filename) #saves the image
#     print('Saved file', file.filename)
#     return 'ok'

# @app.post('/submit/')
# def submit_data():
#     file = request.files["file"] #file must be attached in body with name "file"
#     file.save('./geodata/' + file.filename) #saves the image
#     print('Saved file', file.filename)
#     #Perform YOLO detections - all detections should be moved to a queue and handled by seperate thread at some point
#     #yolo.image_detections(file.filename)
#     return 'ok'

@app.post('/submit/')
def submit_data():
    file = request.files["file"]

    if not file:
        return jsonify({"error": "No file uploaded"})
    
    geodata_directory = './geodata/'
    if not os.path.exists(geodata_directory):
        os.makedirs(geodata_directory)
    
    filename = file.filename
    if not (filename.endswith('.jpg') or filename.endswith('.json')):
        return jsonify({"error": "Unsupported file type. Only .jpg and .json are allowed"}), 400
    
    file_extension = os.path.splitext(filename)[1]
    base_filename = 'capture'

    existing_files = [f for f in os.listdir(geodata_directory) if f.startswith(base_filename) and f.endswith(file_extension)]

    max_number = 0
    for existing_filename in existing_files:
        try:
            number = int(existing_filename[len(base_filename):-len(file_extension)])
            max_number = max(max_number, number)
        except ValueError:
            continue
    
    new_number = max_number + 1
    new_filename = f"{base_filename}{new_number}{file_extension}"

    file.save(os.path.join(geodata_directory, new_filename))
    print('Saved file', new_filename)
    
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