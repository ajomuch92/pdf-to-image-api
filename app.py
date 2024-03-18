from flask import Flask, request, jsonify
import tempfile
import os
import fitz  # PyMuPDF
import base64

app = Flask(__name__)

UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def pdf_to_images(pdf_path):
    pdf_document = fitz.open(pdf_path)
    images = []

    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        pix = page.get_pixmap()
        image_bytes = pix.tobytes()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        images.append(image_base64)

    return images


@app.route('/upload', methods=['POST'])
def upload_file():
    print('Calling endpoint')
    if 'file' not in request.files:
        return jsonify({'error': 'No se proporcionó ningún archivo'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Nombre de archivo vacío'}), 400

    if file and allowed_file(file.filename):
        temp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(temp_file_path)
        print('Temporal file ' + temp_file_path)
        images = pdf_to_images(temp_file_path)
        os.remove(temp_file_path)
        return jsonify({'images': images}), 200

    return jsonify({'error': 'Formato de archivo no permitido'}), 400

@app.route('/msg', methods=['GET'])
def msg():
    return jsonify({'msg': 'Hello'})

@app.route('/')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(debug=True)
