from flask import Flask, request, jsonify, render_template
from ultralytics import YOLO
from PIL import Image
import io
import os
import requests

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Load YOLO model
MODEL_PATH = 'static/models/yolo11_best.pt'  # Ensure the model file is correctly placed
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

model = YOLO(MODEL_PATH)

# Home route
@app.route("/")
def home():
    user_logged_in = is_user_logged_in()
    return render_template("index1.html", user_logged_in=user_logged_in)

# Live route
@app.route('/live')
def live():
    return render_template('index1.html')  


# Upload route
@app.route('/upload')
def upload():
    return render_template('upload.html')

def is_user_logged_in():
    try:
        response = requests.get("http://127.0.0.1:8000/check-auth/", cookies=request.cookies)
        return response.json().get("authenticated", False)
    except Exception as e:
        return False

# Object detection route
@app.route('/detect', methods=['POST'])
def detect_objects():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        # Read and process image
        image = Image.open(io.BytesIO(image_file.read()))

        # Perform object detection
        results = model(image)

        # Extract detection results
        detections = []
        for result in results[0].boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = result
            detections.append({
                'class': model.names[int(class_id)],
                'confidence': round(float(score), 3),
                'box': [x1, y1, x2, y2]
            })

        return jsonify({'detections': detections})

    except Exception as e:
        return jsonify({'error': f"Detection failed: {str(e)}"}), 500

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
