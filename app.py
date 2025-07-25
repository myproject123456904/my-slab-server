from flask import Flask, request, jsonify
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'images'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        try:
            filename = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filename)
            file_url = f"https://my-slab-server.onrender.com/images/{file.filename}"
            print(f"File saved successfully: {file_url}")  # For debugging
            return jsonify({"url": file_url}), 200
        except Exception as e:
            print(f"Error saving file: {str(e)}")  # For debugging
            return jsonify({"error": f"Upload failed: {str(e)}"}), 500
    return jsonify({"error": "Upload failed"}), 500

@app.route('/slab', methods=['GET'])
def show_slab():
    data = request.args.get('data')
    if not data:
        return "No data provided", 400
    try:
        data_dict = eval(data)
        slab_image = data_dict.get('slab_image', 'images/1.jpg')
        block_image = data_dict.get('block_image', 'images/2.jpg')
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head><meta charset="UTF-8"><title>Slab Details</title></head>
        <body>
            <h1>Slab No: {data_dict.get('slab_no', 'N/A')}</h1>
            <img src="{slab_image}" alt="Slab Image" style="max-width: 300px;">
            <br><img src="{block_image}" alt="Block Image" style="max-width: 300px;">
            <p>Width: {data_dict.get('width', '-')}, Length: {data_dict.get('length', '-')}, Thickness: {data_dict.get('thickness', '-')}</p>
            <p>Stone: {data_dict.get('stone', '-')}, Processing: {data_dict.get('processing', '-')}, Product Code: {data_dict.get('product_code', '-')}</p>
        </body>
        </html>
        """
        return html, 200
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/')
def home():
    return "Server is running! Use /upload for file uploads or /slab for slab details.", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use Render's PORT or default to 5000
    app.run(host='0.0.0.0', port=port)
