from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import cv2
import os
from math import pi, sin, cos, tan, atan2, hypot, floor
from numpy import clip
import sys
from PIL import Image

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def outImgToXYZ(i, j, face, edge):
    a = 2.0 * float(i) / edge
    b = 2.0 * float(j) / edge
    if face == 0:
        (x, y, z) = (-1.0, 1.0 - a, 3.0 - b)
    elif face == 1:  # left
        (x, y, z) = (a - 3.0, -1.0, 3.0 - b)
    elif face == 2:  # front
        (x, y, z) = (1.0, a - 5.0, 3.0 - b)
    elif face == 3:  # right
        (x, y, z) = (7.0 - a, 1.0, 3.0 - b)
    elif face == 4:  # top
        (x, y, z) = (b - 1.0, a - 5.0, 1.0)
    elif face == 5:  # bottom
        (x, y, z) = (5.0 - b, a - 5.0, -1.0)
    return (x, y, z)


def convertBack(imgIn, imgOut):
    inSize = imgIn.size
    outSize = imgOut.size
    inPix = imgIn.load()
    outPix = imgOut.load()
    edge = inSize[0] / 4   # the length of each edge in pixels
    for i in range(outSize[0]):
        face = int(i / edge)  # 0 - back, 1 - left 2 - front, 3 - right
        if face == 2:
            rng = range(0, int(edge * 3))
        else:
            rng = range(int(edge), int(edge) * 2)

        for j in rng:
            if j < edge:
                face2 = 4  # top
            elif j >= 2 * edge:
                face2 = 5  # bottom
            else:
                face2 = face

            (x, y, z) = outImgToXYZ(i, j, face2, edge)
            theta = atan2(y, x)  # range -pi to pi
            r = hypot(x, y)
            phi = atan2(z, r)  # range -pi/2 to pi/2
            # source img coords
            uf = (2.0 * edge * (theta + pi) / pi)
            vf = (2.0 * edge * (pi / 2 - phi) / pi)
            # Use bilinear interpolation between the four surrounding pixels
            ui = floor(uf)  # coord of pixel to bottom left
            vi = floor(vf)
            u2 = ui + 1       # coords of pixel to top right
            v2 = vi + 1
            mu = uf - ui      # fraction of way across pixel
            nu = vf - vi
            # Pixel values of four corners
            A = inPix[ui % inSize[0], int(clip(vi, 0, inSize[1] - 1))]
            B = inPix[u2 % inSize[0], int(clip(vi, 0, inSize[1] - 1))]
            C = inPix[ui % inSize[0], int(clip(v2, 0, inSize[1] - 1))]
            D = inPix[u2 % inSize[0], int(clip(v2, 0, inSize[1] - 1))]
            # interpolate
            (r, g, b) = (
                A[0] * (1 - mu) * (1 - nu) + B[0] * (mu) * (1 - nu) + C[0] * (1 - mu) * nu + D[0] * mu * nu,
                A[1] * (1 - mu) * (1 - nu) + B[1] * (mu) * (1 - nu) + C[1] * (1 - mu) * nu + D[1] * mu * nu,
                A[2] * (1 - mu) * (1 - nu) + B[2] * (mu) * (1 - nu) + C[2] * (1 - mu) * nu + D[2] * mu * nu)

            outPix[i, j] = (int(round(r)), int(round(g)), int(round(b)))


def convert_to_cubemap(image_path):
    imgIn = Image.open(image_path)
    inSize = imgIn.size
    imgOut = Image.new("RGB", (inSize[0], int(inSize[0] * 3 / 4)), "black")
    convertBack(imgIn, imgOut)
    output_path = os.path.splitext(image_path)[0] + "_out.png"
    imgOut.save(output_path)
    return output_path

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        print("Uploaded filename:", filename)  # Add this line for debugging
        file.save(filename)
        output_path = convert_to_cubemap(filename)
        return send_file(output_path, as_attachment=True)
    else:
        return "No file uploaded!"


if __name__ == '__main__':
    app.run(debug=True)
