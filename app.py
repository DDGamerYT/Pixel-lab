from flask import Flask, render_template, request, send_file
from PIL import Image
import os
import qrcode
from io import BytesIO
from rembg import remove

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/image-compressor', methods=['GET', 'POST'])
def image_compresser():
    if request.method == 'POST':
        file = request.files['image']
        quality_input = int(request.form['quality'])
        format_choice = request.form['format']

        if file:
            filename = file.filename

            # Save original
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            img = Image.open(filepath)

            name, ext = os.path.splitext(filename)

            # 🎯 Convert based on format choice
            if format_choice == "jpg":
                img = img.convert("RGB")
                compressed_filename = f"compressed_{name}.jpg"
                compressed_path = os.path.join(UPLOAD_FOLDER, compressed_filename)

                # Target size logic
                original_size = os.path.getsize(filepath)
                target_size = int(original_size * (quality_input / 100))

                quality = 95
                step = 2

                while quality > 10:
                    img.save(compressed_path, "JPEG", quality=quality)
                    current_size = os.path.getsize(compressed_path)

                    if abs(current_size - target_size) < target_size * 0.05:
                        break

                    quality -= step

            else:  # PNG
                compressed_filename = f"compressed_{name}.png"
                compressed_path = os.path.join(UPLOAD_FOLDER, compressed_filename)

                img.save(compressed_path, "PNG", optimize=True)

            return send_file(compressed_path, as_attachment=True)

    return render_template('compressor.html')

@app.route('/qr-generator', methods=['GET', 'POST'])
def qr_generator():
    if request.method == 'POST':
        data = request.form['data']
        filename_input = request.form.get('filename')

        if data:
            qr = qrcode.make(data)

            img_io = BytesIO()
            qr.save(img_io, 'PNG')
            img_io.seek(0)

            # ✅ Use custom filename if given
            if filename_input and filename_input.strip() != "":
                filename = filename_input.strip() + ".png"
            else:
                filename = "qr_code.png"

            return send_file(
                img_io,
                mimetype='image/png',
                as_attachment=True,
                download_name=filename
            )

    return render_template('qr.html')

@app.route('/remove-bg', methods=['GET', 'POST'])
def remove_bg():
    if request.method == 'POST':
        file = request.files['image']

        if file:
            # 👉 Get original filename
            original_name = file.filename
            name, ext = os.path.splitext(original_name)

            # 👉 Read file bytes
            input_bytes = file.read()

            # 👉 Remove background
            output_bytes = remove(input_bytes)

            # 👉 Create new filename
            new_filename = f"remove_bg_{name}.png"

            return send_file(
                BytesIO(output_bytes),
                mimetype='image/png',
                as_attachment=True,
                download_name=new_filename
            )

    return render_template('remove_bg.html')

@app.route('/converter', methods=['GET', 'POST'])
def converter():
    if request.method == 'POST':
        file = request.files['image']
        format_choice = request.form['format']
        filename_input = request.form.get('filename')

        if file:
            # open image
            img = Image.open(file)

            # original name
            original_name = file.filename
            name, ext = os.path.splitext(original_name)

            # 🧠 handle transparency (important)
            if format_choice == "jpg":
                img = img.convert("RGB")  # remove alpha

            # save in memory
            img_io = BytesIO()

            if format_choice == "jpg":
                img.save(img_io, format='JPEG', quality=90)
                ext_out = "jpg"

            elif format_choice == "png":
                img.save(img_io, format='PNG')
                ext_out = "png"

            elif format_choice == "webp":
                img.save(img_io, format='WEBP', quality=90)
                ext_out = "webp"

            img_io.seek(0)

            # ✅ filename handling
            if filename_input and filename_input.strip() != "":
                final_name = filename_input.strip()
            else:
                final_name = name

            final_name = final_name.replace(" ", "_")

            download_name = f"converted_{final_name}.{ext_out}"

            return send_file(
                img_io,
                mimetype=f'image/{ext_out}',
                as_attachment=True,
                download_name=download_name
            )

    return render_template('converter.html')

@app.route('/resize', methods=['GET', 'POST'])
def image_resize():
    if request.method == 'POST':
        file = request.files['image']
        width = request.form.get('width')
        height = request.form.get('height')
        filename_input = request.form.get('filename')

        if file:
            img = Image.open(file)

            # original size
            orig_width, orig_height = img.size

            # convert inputs
            width = int(width) if width else None
            height = int(height) if height else None

            # 🔥 maintain aspect ratio
            if width and not height:
                height = int((width / orig_width) * orig_height)
            elif height and not width:
                width = int((height / orig_height) * orig_width)
            elif not width and not height:
                width, height = orig_width, orig_height

            # 🔥 high-quality resize
            img = img.resize((width, height), Image.LANCZOS)

            # filename handling
            original_name = file.filename
            name, ext = os.path.splitext(original_name)

            if filename_input and filename_input.strip() != "":
                final_name = filename_input.strip()
            else:
                final_name = name

            final_name = final_name.replace(" ", "_")

            # save in memory
            img_io = BytesIO()

            # keep original format
            format = ext.replace(".", "").upper()
            if format == "JPG":
                format = "JPEG"

            img.save(img_io, format=format, quality=95)
            img_io.seek(0)

            download_name = f"resized_{final_name}.{format.lower()}"

            return send_file(
                img_io,
                as_attachment=True,
                download_name=download_name,
                mimetype=f'image/{format.lower()}'
            )

    return render_template('resize.html')

@app.route('/tools')
def tools():
    return render_template('tools.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/googleccbe93b3e1abf06e')
def google_verify():
    return send_file('googleccbe93b3e1abf06e')

if __name__ == "__main__":
    app.run(debug=True)
