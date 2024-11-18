from flask import Flask, render_template, request, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
from processing import process_image
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/original/'
app.config['PROCESSED_FOLDER'] = 'static/uploads/processed/'
app.config['LOGO_FOLDER'] = 'static/uploads/logos'
app.config['DEFAULT_LOGO'] = 'static/logo/logo_bp.png'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.secret_key = 'your_secret_key'  # Necessary for session management

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle image upload
        if 'image' in request.files:
            file = request.files.get('image')
            if file and allowed_file(file.filename):
                # Save and track the original image
                filename = secure_filename(file.filename)
                original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(original_path)
                session['original_image'] = original_path
                session['processed_images'] = []  # Reset processed images list for a new upload

        if 'logo' in request.files:
            file = request.files.get('logo')
            if file and allowed_file(file.filename):
                # Save and track the logo
                filename = secure_filename(file.filename)
                logo_path = os.path.join(app.config['LOGO_FOLDER'], filename)
                file.save(logo_path)
                session['logo'] = logo_path
                if logo_path is None:
                    logo_path = app.config['DEFAULT_LOGO']

        # Retrieve existing data
        unique_id = uuid.uuid4()
        brightness = int(request.form.get('brightness', 0))
        image_padding = float(request.form.get('image_padding', 0))
        logo_padding = float(request.form.get('logo_padding', 0))
        sizes = request.form.getlist('sizes')  # List of selected sizes

        # Process the image if it exists in the session
        original_image = session.get('original_image')
        processed_images = session.get('processed_images', [])
        logo = session.get('logo', app.config['DEFAULT_LOGO'])
        print(logo)
        if original_image:
            for size in sizes:
                output_filename = f"{unique_id}-{size}.png"
                output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
                process_image(
                    input_path=original_image,
                    output_path=output_path,
                    size=int(size),
                    brightness=brightness,
                    logo_path=logo, 
                    image_padding=image_padding, 
                    logo_padding=logo_padding, 
                )
                # Add processed image to the list
                processed_images.append({
                    'size': size,
                    'filename': output_filename,
                    'filepath': output_path
                })
            session['processed_images'] = processed_images
            return redirect(url_for('index'))  # Redirect after processing to refresh the page

    # Load images for display
    original_image = session.get('original_image', None)
    processed_images = session.get('processed_images', [])
    logo = session.get('logo', app.config['DEFAULT_LOGO'])
    return render_template(
        'index.html',
        original_image=url_for('static', filename=f'uploads/original/{os.path.basename(original_image)}') if original_image else None,
        processed_images=processed_images, 
        logo=logo, 
    )

if __name__ == '__main__':
    app.run(debug=True)
