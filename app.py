from flask import Flask, render_template, request, send_from_directory
import json  # این خط رو اضافه کن

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
        data = json.loads(data_param)  # اینجا از json استفاده می‌کنه
        slab_no = data.get('slab_no', 'N/A')
        width = data.get('width', 'N/A')
        length = data.get('length', 'N/A')
        thickness = data.get('thickness', 'N/A')
        stone = data.get('stone', 'N/A')
        processing = data.get('processing', 'N/A')
        product_code = data.get('product_code', 'N/A')
        description = data.get('description', 'N/A')
        warehouse = data.get('warehouse', 'N/A')
        block_image = data.get('block_image', '')
        if block_image and not block_image.startswith('http'):
            block_image = f"/images/{block_image}"
        
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
                              block_image=block_image)
    except json.JSONDecodeError:  # اینجا هم از json استفاده می‌کنه
        return "Invalid data format", 400
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)