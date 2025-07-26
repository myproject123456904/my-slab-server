from flask import Flask, request, jsonify, send_from_directory
import os
import json

app = Flask(__name__)

UPLOAD_FOLDER = '/tmp/images' if os.path.exists('/tmp') else 'images'
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
            file_url = f"http://localhost:5000/images/{file.filename}" if 'localhost' in request.host else f"https://my-slab-server.onrender.com/images/{file.filename}"
            print(f"File saved successfully: {file_url}")
            return jsonify({"url": file_url}), 200
        except Exception as e:
            print(f"Error saving file: {str(e)}")
            return jsonify({"error": f"Upload failed: {str(e)}"}), 500
    return jsonify({"error": "Upload failed"}), 500

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/slab', methods=['GET'])
def show_slab():
    data = request.args.get('data')
    if not data:
        return "No data provided", 400
    try:
        data_dict = json.loads(data)
        slab_image = data_dict.get('slab_image', 'images/1.jpg')
        block_image = data_dict.get('block_image', 'images/2.jpg')
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head><meta charset="UTF-8"><title>Slab Details - {data_dict.get('slab_no', 'N/A')}</title></head>
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
    except json.JSONDecodeError as e:
        return f"Invalid JSON data: {str(e)}", 400
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/')
def home():
    return "Server is running! Use /upload for file uploads or /slab for slab details.", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
