# import os
# from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
# from rembg import remove
# from PIL import Image
# from io import BytesIO
#
# # Initialize the Flask app
# app = Flask(__name__)
# app.secret_key = 'your_secret_key'
#
# # Directories for uploads and outputs
# UPLOAD_FOLDER = 'uploads'
# OUTPUT_FOLDER = 'outputs'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
#
# # Ensure directories exist
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(OUTPUT_FOLDER, exist_ok=True)
#
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
#
#
# # Check if the file is allowed
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#
#
# # Home route
# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         # Check if a file is uploaded
#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#
#         file = request.files['file']
#
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
#
#         if file and allowed_file(file.filename):
#             # Save the uploaded file
#             input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
#             output_path = os.path.join(app.config['OUTPUT_FOLDER'], f'processed-{file.filename}')
#             file.save(input_path)
#
#             # Process the image and remove the background
#             with open(input_path, 'rb') as input_image:
#                 result = remove(input_image.read())
#                 image = Image.open(BytesIO(result))
#                 image.save(output_path)
#
#             # Redirect to download the processed file
#             return redirect(url_for('download_file', filename=f'processed-{file.filename}'))
#
#     return render_template('index.html')
#
#
# # Route to serve the processed file for download
# @app.route('/uploads/<filename>')
# def download_file(filename):
#     return send_from_directory(app.config['OUTPUT_FOLDER'], filename)
#
#
# # Run the app
# if __name__ == '__main__':
#     app.run(debug=True)
import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from rembg import remove
from PIL import Image
from io import BytesIO

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure directories for uploads and outputs
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp', 'tiff'}

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER


# Helper function to check file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Ensure a file is uploaded
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # Process only allowed files
        if file and allowed_file(file.filename):
            # Save the uploaded file
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(input_path)

            # Prepare the output filename
            output_filename = f'processed-{file.filename}'
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

            # Process the image and remove the background
            with open(input_path, 'rb') as input_image:
                result = remove(input_image.read())
                image = Image.open(BytesIO(result))

                # Get original format and handle transparency
                original_format = image.format or 'PNG'  # Default to PNG if format is not detected
                if image.mode == 'RGBA' and original_format.lower() in {'jpeg', 'jpg'}:
                    image = image.convert('RGB')  # Convert RGBA to RGB for JPEG compatibility

                # Save the image in its original format or as PNG
                output_format = original_format if original_format.lower() in ALLOWED_EXTENSIONS else 'PNG'
                output_filename = f'processed-{os.path.splitext(file.filename)[0]}.{output_format.lower()}'
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
                image.save(output_path, format=output_format.upper())

            # Redirect to the download page
            return redirect(url_for('download_file', filename=os.path.basename(output_path)))

    return render_template('index.html')


@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
