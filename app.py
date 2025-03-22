from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import pdfplumber
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Mengizinkan akses dari frontend
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_data_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text() + "\n" if page.extract_text() else ''
    
    # Contoh parsing sederhana (sesuaikan dengan format dokumen PDF yang diunggah)
    lines = text.split("\n")
    extracted_data = {
        "File Name": os.path.basename(pdf_path),
        "Name": lines[0] if len(lines) > 0 else "Unknown",
        "Place of Birth": lines[1] if len(lines) > 1 else "Unknown",
        "Date of Birth": lines[2] if len(lines) > 2 else "Unknown",
        "Passport No": lines[3] if len(lines) > 3 else "Unknown",
        "Passport Expiry": lines[4] if len(lines) > 4 else "Unknown"
    }
    return extracted_data

@app.route("/")
def index():
    return render_template("upload.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    files = request.files.getlist("file")
    extracted_results = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            extracted_data = extract_data_from_pdf(file_path)
            extracted_results.append(extracted_data)

    return jsonify(extracted_results)

if __name__ == "__main__":
    app.run(debug=True)
