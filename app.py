from flask import Flask, render_template, request, send_from_directory
from rembg import remove
from PIL import Image
import os
import cv2
import logging

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
STANDARD_SIZE = (500, 500)  # Example standard size, adjust as needed

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

if not os.path.exists(OUTPUT_FOLDER):
    os.mkdir(OUTPUT_FOLDER)

# Set up logging
logging.basicConfig(level=logging.DEBUG)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def resize_and_save(image_path):
    logging.debug(f"Resizing and saving image: {image_path}")
    image = cv2.imread(image_path)
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    size = min(center)  # Assuming the coin is centrally located
    cropped = image[center[1]-size:center[1] +
                    size, center[0]-size:center[0]+size]

    resized = cv2.resize(cropped, STANDARD_SIZE, interpolation=cv2.INTER_AREA)
    pil_image = Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))
    output_path = image_path.replace('uploads', 'outputs').rsplit('.', 1)[
        0] + '_resized.png'
    pil_image.save(output_path, 'PNG')
    logging.debug(f"Image saved: {output_path}")

    return output_path


def process_file(file, side):
    logging.debug(f"Processing file: {file.filename}, side: {side}")
    filename = file.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    resized_path = resize_and_save(file_path)
    input_image = Image.open(resized_path)
    output_image = remove(input_image)
    output_filename = f"no_bg_{side}_" + filename.rsplit('.', 1)[0] + '.png'
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    try:
        output_image.save(output_path, 'PNG')
    except ValueError as e:
        logging.error(f"Failed to save image: {e}")
        logging.error(f"Filename: {output_filename}")
        logging.error(f"File data: {output_image}")
        raise
    logging.debug(f"Output image saved: {output_path}")

    return output_image, output_filename


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        logging.debug("POST request received")
        if 'front' not in request.files or 'back' not in request.files:
            logging.error("No file part")
            return 'No file part'

        front_file = request.files['front']
        back_file = request.files['back']

        if front_file.filename == '' or back_file.filename == '':
            logging.error("No selected file")
            return 'No selected file'

        if front_file and back_file and allowed_file(front_file.filename) and allowed_file(back_file.filename):
            front_image, front_filename = process_file(front_file, 'front')
            back_image, back_filename = process_file(back_file, 'back')

            total_width = front_image.width + back_image.width
            max_height = max(front_image.height, back_image.height)
            combined = Image.new('RGBA', (total_width, max_height))
            combined.paste(front_image, (0, 0))
            combined.paste(back_image, (front_image.width, 0))

            combined_filename = "combined_" + \
                front_filename.split('_')[2] + ".png"
            combined_path = os.path.join(
                app.config['OUTPUT_FOLDER'], combined_filename)
            combined.save(combined_path)

            return render_template('download.html', front=front_filename, back=back_filename, combined=combined_filename)

    return render_template('upload.html')


@app.route('/outputs/<filename>')
def uploaded_file(filename):
    logging.debug(f"Serving file: {filename}")
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
