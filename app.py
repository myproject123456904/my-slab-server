from flask import Flask, render_template, request
import json

app = Flask(__name__)

@app.route('/')
def welcome():
    return "Welcome to Slab Info Server! Use /slab endpoint with data parameter."

@app.route('/slab')
def slab_details():
    # Get data from QR code URL parameter
    data_param = request.args.get('data')
    if not data_param:
        return "No data provided", 400
    
    try:
        # Parse JSON data from QR code
        data = json.loads(data_param)
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
    except json.JSONDecodeError:
        return "Invalid data format", 400
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)