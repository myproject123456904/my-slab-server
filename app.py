from flask import Flask, render_template, request, send_from_directory
import json
import os  # این خط رو اضافه کردم

app = Flask(__name__)

UPLOAD_FOLDER = 'images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def welcome():
    return "Welcome to Slab Info Server! Use /slab endpoint with data parameter."

@app.route('/slab')
def slab_details():
    data_param = request.args.get('data')
    if not data_param:
        return "No data provided", 400

    try:
        data = json.loads(data_param)  # فقط یک بار لود کن
        slab_no = data.get('slab_no', 'N/A')
        width = data.get('width', 'N/A')
        length = data.get('length', 'N/A')
        thickness = data.get('thickness', 'N/A')
        stone = data.get('stone', 'N/A')
        processing = data.get('processing', 'N/A')
        product_code = data.get('product_code', 'N/A')
        description = data.get('description', 'N/A')
        warehouse = data.get('warehouse', 'N/A')
        slab_image = data.get('slab_image', '')  # عکس اسلب
        if slab_image and not slab_image.startswith('http'):
            slab_image = f"/images/{os.path.basename(slab_image)}"  # فقط اسم فایل
        block_image = data.get('block_image', '')  # عکس کوپ
        if block_image and not block_image.startswith('http'):
            block_image = f"/images/{os.path.basename(block_image)}"  # فقط اسم فایل

        return render_template('slab_detail.html', 
                              slab_no=slab_no,
                              width=width,
                              length=length,
                              thickness=thickness,
                              stone=stone,
                              processing=processing,
                              product_code=product_code,
                              description=description,
                              warehouse=warehouse,
                              slab_image=slab_image,  # عکس اسلب
                              block_image=block_image)  # عکس کوپ
    except json.JSONDecodeError:
        return "Invalid data format", 400
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)