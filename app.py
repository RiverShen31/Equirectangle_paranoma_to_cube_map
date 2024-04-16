from flask import Flask, render_template, send_file, request, jsonify
from io import BytesIO
from PIL import Image
import zipfile
import base64

app = Flask(__name__)

# Route to render the index.html template
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint to process the merged image sent from the client
@app.route('/process_merged_image', methods=['POST'])
def process_merged_image():
    data = request.json
    merged_image_url = data.get('mergedImageUrl')

    # Download the merged image from the URL and process/save it as needed
    # Here you would typically download the image using a library like requests
    # and then process/save it using PIL or any other image processing library.
    # For demonstration purposes, let's just return the received URL.
    return jsonify({'message': 'Merged image received.', 'mergedImageUrl': merged_image_url}), 200

if __name__ == '__main__':
    app.run(debug=True)
