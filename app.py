from flask import Flask, render_template, request, send_from_directory
from rembg import remove
from PIL import Image
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

if not os.path.exists(OUTPUT_FOLDER):
    os.mkdir(OUTPUT_FOLDER)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        # if user does not select file, browser also submit an empty part without filename
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Remove background
            file_extension = filename.rsplit('.', 1)[1].lower()
            if file_extension in ['jpeg', 'jpg']:
                output_extension = 'png'
            else:
                output_extension = file_extension
            output_filename = "no_bg_" + \
                filename.rsplit('.', 1)[0] + '.' + output_extension
            output_path = os.path.join(
                app.config['OUTPUT_FOLDER'], output_filename)

            input_image = Image.open(file_path)
            output_image = remove(input_image)
            output_image.save(output_path)

            return render_template('download.html', filename=output_filename)

    return render_template('upload.html')


@app.route('/outputs/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
