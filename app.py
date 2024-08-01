from flask import Flask, request, jsonify, render_template
import os
import re
from paddleocr import PaddleOCR

# Initialize the PaddleOCR model
ocr_model = PaddleOCR(lang='en')

app = Flask(__name__)

# Define the upload folder and allowed extensions
UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_organization_and_person_names(text):
    organization_match = re.search(r'@([A-Za-z]+)\.com', text)
    organization_name = organization_match.group(1).capitalize() if organization_match else ""

    person_name_match = re.search(r'([A-Za-z\.]+)@', text)
    person_name = person_name_match.group(1).replace('.', ' ').strip().title() if person_name_match else ""

    return organization_name, person_name

@app.route('/')
def upload_file():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    if file and allowed_file(file.filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        
        # Perform OCR on the image
        result = ocr_model.ocr(filename)
        
        # Extract text from OCR result
        ocr_text = ""
        for line in result:
            ocr_text += ' '.join([word_info[1][0] for word_info in line]) + '\n'
        
        # Extract organization and person names
        organization_name, person_name = extract_organization_and_person_names(ocr_text)
        
        return render_template('index.html', organization_names=[organization_name], person_names=[person_name])
    
    return jsonify({'error': 'File not allowed'})

if __name__ == '__main__':
    app.run(debug=True)
