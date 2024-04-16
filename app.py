from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import os
import shutil
import zipfile
from PIL import Image

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    uploaded_files = {
        'top': request.files['top_image'],
        'down': request.files['down_image'],
        'back': request.files['back_image'],
        'front': request.files['front_image'],
        'right': request.files['right_image'],
        'left': request.files['left_image']
    }

    # Check if all files are uploaded
    if all(file.filename for file in uploaded_files.values()):
        # Create a folder to store uploaded images
        uploads_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
        os.makedirs(uploads_path, exist_ok=True)

        # Save each uploaded image
        for face_name, file in uploaded_files.items():
            if file.filename != '':
                # Create folders for each face (top, down, back, front, right, left)
                face_folder_path = os.path.join(uploads_path, face_name, '0')
                os.makedirs(face_folder_path, exist_ok=True)
                # Save the original image inside the '0' subfolder
                filename = secure_filename(file.filename)
                original_file_path = os.path.join(face_folder_path, filename)
                file.save(original_file_path)

                # Generate level 1, level 2, and level 3 images from the original image
                generate_level_images(original_file_path, os.path.join(uploads_path, face_name))

        # Zip the uploaded images
        media_zip_filename = os.path.join(app.root_path, 'media.zip')
        with zipfile.ZipFile(media_zip_filename, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for face_name in uploaded_files.keys():
                face_folder_path = os.path.join(uploads_path, face_name)
                for level in ['0', '1', '2', '3']:
                    for root, _, files in os.walk(os.path.join(face_folder_path, level)):
                        for file in files:
                            zip_file.write(
                                os.path.join(root, file),
                                arcname=os.path.join('media', face_name, level, file)
                            )

        # Clean up the uploads folder
        shutil.rmtree(uploads_path)

        # Send the zip file for download and remove it afterwards
        response = send_file(media_zip_filename, as_attachment=True, mimetype='application/zip')
        return response
    else:
        return 'Error: Please upload all images.'

def generate_level_images(input_image_path, output_folder_path):
    input_image = Image.open(input_image_path)
    width, height = input_image.size

    # Generate level 1 (grid 2x2) images
    generate_level(input_image, output_folder_path, '1', 2, width, height)

    # Generate level 2 (grid 3x3) images
    generate_level(input_image, output_folder_path, '2', 3, width, height)

    # Generate level 3 (grid 5x5) images
    generate_level(input_image, output_folder_path, '3', 5, width, height)

def generate_level(input_image, output_folder_path, level, grid_size, width, height):
    tile_width = width // grid_size
    tile_height = height // grid_size

    os.makedirs(os.path.join(output_folder_path, level), exist_ok=True)  # Create subfolder for the level

    for i in range(grid_size):
        for j in range(grid_size):
            x1 = i * tile_width
            y1 = j * tile_height
            x2 = (i + 1) * tile_width
            y2 = (j + 1) * tile_height
            region = input_image.crop((x1, y1, x2, y2))
            output_image_path = os.path.join(output_folder_path, level, f'{i}{j}.png')
            region.save(output_image_path)

if __name__ == '__main__':
    app.run(debug=True)
