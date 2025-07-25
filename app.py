import os
import json
import time
from tkinter import Tk, Label, Entry, Button, messagebox, ttk, Toplevel
from tkinter import filedialog
from PIL import Image
from datetime import datetime
import qrcode
from weasyprint import HTML
from tkcalendar import DateEntry
import shutil
import requests

# Function to load name mapping from JSON
def load_name_mapping():
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BundleData")
    try:
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        filepath = os.path.join(data_dir, 'item_name_mapping.json')
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            default_mapping = {}
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(default_mapping, f, ensure_ascii=False, indent=4)
            return default_mapping
    except PermissionError:
        messagebox.showwarning("Error", "Cannot access program directory. Using temporary directory.")
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        filepath = os.path.join(temp_dir, 'item_name_mapping.json')
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            default_mapping = {}
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(default_mapping, f, ensure_ascii=False, indent=4)
            return default_mapping
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load name mapping: {str(e)}")
        return {}

# Function to save name mapping to JSON
def save_name_mapping(mapping):
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BundleData")
    try:
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        with open(os.path.join(data_dir, 'item_name_mapping.json'), 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=4)
    except PermissionError:
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        with open(os.path.join(temp_dir, 'item_name_mapping.json'), 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=4)

# Function to check admin password
def check_admin_access():
    def verify_password():
        password = entry_password.get().strip()
        if password == "admin123":
            password_window.destroy()
            show_data_entry()
        else:
            messagebox.showerror("Error", "Incorrect password!")
    
    password_window = Toplevel(root)
    password_window.title("Admin Access")
    password_window.geometry("300x150")
    
    Label(password_window, text="Password", font=("Arial", 12)).pack(pady=10)
    entry_password = Entry(password_window, show="*", width=20, font=("Arial", 12))
    entry_password.pack(pady=5)
    Button(password_window, text="Submit", command=verify_password, bg="#4682B4", fg="white", font=("Arial", 12)).pack(pady=10)

# Function to show data entry window (admin only)
def show_data_entry():
    data_window = Toplevel(root)
    data_window.title("Data Entry - Add Item Codes and Names")
    data_window.geometry("800x500")
    
    tree = ttk.Treeview(data_window, columns=("Code", "Local Name", "Iran Name"), show="headings")
    tree.heading("Code", text="Code")
    tree.heading("Local Name", text="Local Name")
    tree.heading("Iran Name", text="Iran Name")
    tree.pack(pady=10, padx=10, fill="both", expand=True)
    
    name_mapping = load_name_mapping()
    for code, data in name_mapping.items():
        tree.insert("", "end", values=(code, data["local_name"], data["iran_name"]))
    
    Label(data_window, text="Add/Edit Mapping", font=("Arial", 14, "bold")).pack(pady=10)
    
    frame = ttk.Frame(data_window)
    frame.pack(pady=10, padx=10)
    
    Label(frame, text="Code:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5)
    entry_code = Entry(frame, width=15, font=("Arial", 12))
    entry_code.grid(row=0, column=1, padx=10, pady=5)
    
    Label(frame, text="Local Name:", font=("Arial", 12)).grid(row=0, column=2, padx=10, pady=5)
    entry_local_name = Entry(frame, width=25, font=("Arial", 12))
    entry_local_name.grid(row=0, column=3, padx=10, pady=5)
    
    Label(frame, text="Iran Name:", font=("Arial", 12)).grid(row=0, column=4, padx=10, pady=5)
    entry_iran_name = Entry(frame, width=25, font=("Arial", 12))
    entry_iran_name.grid(row=0, column=5, padx=10, pady=5)
    
    def add_or_update_mapping():
        code = entry_code.get().strip()
        local_name = entry_local_name.get().strip()
        iran_name = entry_iran_name.get().strip()
        
        if not all([code, local_name, iran_name]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        name_mapping[code] = {"local_name": local_name, "iran_name": iran_name}
        save_name_mapping(name_mapping)
        tree.delete(*tree.get_children())
        for code, data in name_mapping.items():
            tree.insert("", "end", values=(code, data["local_name"], data["iran_name"]))
        
        iran_names = [data["iran_name"] for data in name_mapping.values()]
        entry_iran_name_dropdown["values"] = iran_names
        
        for entry in [entry_code, entry_local_name, entry_iran_name]:
            entry.delete(0, "end")
    
    def delete_mapping():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Error", "Please select a row to delete!")
            return
        code = tree.item(selected_item)["values"][0]
        if code in name_mapping:
            del name_mapping[code]
            save_name_mapping(name_mapping)
            tree.delete(selected_item)
        iran_names = [data["iran_name"] for data in name_mapping.values()]
        entry_iran_name_dropdown["values"] = iran_names
    
    def edit_mapping():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Error", "Please select a row to edit!")
            return
        code, local_name, iran_name = tree.item(selected_item)["values"]
        entry_code.delete(0, "end")
        entry_code.insert(0, code)
        entry_local_name.delete(0, "end")
        entry_local_name.insert(0, local_name)
        entry_iran_name.delete(0, "end")
        entry_iran_name.insert(0, iran_name)
        tree.delete(selected_item)
    
    button_frame = ttk.Frame(data_window)
    button_frame.pack(pady=10)
    
    Button(button_frame, text="Add/Update", command=add_or_update_mapping, bg="#4682B4", fg="white", font=("Arial", 12)).pack(side="left", padx=5)
    Button(button_frame, text="Delete", command=delete_mapping, bg="#4682B4", fg="white", font=("Arial", 12)).pack(side="left", padx=5)
    Button(button_frame, text="Edit", command=edit_mapping, bg="#4682B4", fg="white", font=("Arial", 12)).pack(side="left", padx=5)

# Function to update Item Code and Local Name based on selected Iran Name
def update_item_details(event):
    selected_iran_name = entry_iran_name_dropdown.get()
    name_mapping = load_name_mapping()
    for code, data in name_mapping.items():
        if data["iran_name"] == selected_iran_name:
            entry_code.delete(0, "end")
            entry_code.insert(0, code)
            entry_name.delete(0, "end")
            entry_name.insert(0, data["local_name"])
            break

# Function to move focus to next field with Enter
def focus_next(widget, event=None):
    next_widget = widget.tk_focusNext()
    if next_widget and next_widget.winfo_exists():
        next_widget.focus()
    return "break"

# Function to select slab images in a single window
def select_slab_images():
    global slab_counter, pending_slab_images
    if 'slab_counter' not in globals():
        slab_counter = 1
    if 'pending_slab_images' not in globals():
        pending_slab_images = []
    
    quantity = int(entry_quantity.get().strip()) if entry_quantity.get().strip() else 0
    if not quantity:
        messagebox.showwarning("Warning", "Please enter a quantity first!")
        return
    
    if not all([stone, processing, product_code, description, warehouse]):
        messagebox.showwarning("Warning", "Please fill Mine Details first!")
        return
    
    image_window = Toplevel(root)
    image_window.title("Select Slab Images")
    image_window.geometry(f"600x{150 + 60 * quantity}")
    image_window.attributes('-topmost', True)
    image_window.update_idletasks()
    
    slab_entries = []
    for i in range(quantity):
        frame = ttk.Frame(image_window)
        frame.pack(pady=5, padx=10, fill="x")
        Label(frame, text=f"Slab {slab_counter + i} Image:", font=("Arial", 12)).pack(side="left", padx=5)
        entry = Entry(frame, width=40, font=("Arial", 12))
        entry.pack(side="left", padx=5, expand=True, fill="x")
        Button(frame, text="Select", command=lambda idx=i, e=entry: select_image(e, idx, image_window), bg="#4682B4", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        slab_entries.append(entry)
    
    def confirm_images():
        slab_images = [e.get().strip() for e in slab_entries]
        if any(not img for img in slab_images):
            messagebox.showerror("Error", "Please select an image for all slabs!")
            return
        pending_slab_images.clear()
        pending_slab_images.extend(slab_images)
        print(f"Selected images: {pending_slab_images}")
        image_window.destroy()
    
    Button(image_window, text="Confirm", command=confirm_images, bg="#32CD32", fg="white", font=("Arial", 12)).pack(pady=10, padx=10)
    image_window.update()

def select_image(entry, idx, parent_window):
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
    if file_path:
        try:
            Image.open(file_path)
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BundleData")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            timestamp = int(time.time() * 1000)
            slab_image_name = f"slab_{timestamp}_{idx}.png"
            slab_image_path = os.path.join(data_dir, slab_image_name)
            shutil.copy(file_path, slab_image_path)
            entry.delete(0, "end")
            entry.insert(0, slab_image_path)
        except Exception as e:
            messagebox.showerror("Error", f"Invalid slab image: {str(e)}")

# Function to add size with confirmed images
def add_size():
    global slab_counter, pending_slab_images, sizes_list
    if not pending_slab_images:
        messagebox.showwarning("Warning", "Please select slab images first!")
        print(f"pending_slab_images is empty: {pending_slab_images}")
        return
    
    if not all([stone, processing, product_code, description, warehouse]):
        messagebox.showwarning("Warning", "Please fill Mine Details first!")
        return
    
    size_data = {
        "width": entry_width.get().strip(),
        "length": entry_length.get().strip(),
        "thickness": entry_thickness.get().strip(),
        "quantity": entry_quantity.get().strip(),
        "stone": stone,
        "processing": processing,
        "product_code": product_code,
    }
    
    for key, value in size_data.items():
        if not value and key not in ["stone", "processing", "product_code"]:
            messagebox.showerror("Error", f"The field '{key}' cannot be empty!")
            return
    
    quantity = int(size_data["quantity"])
    if len(pending_slab_images) != quantity:
        messagebox.showerror("Error", "Number of images must match the quantity!")
        return
    
    start_from = int(entry_start_from.get().strip()) if entry_start_from.get().strip() and slab_counter == 1 else slab_counter
    for i in range(quantity):
        current_slab_no = start_from + i
        sizes_list.append({
            "width": size_data["width"],
            "length": size_data["length"],
            "thickness": size_data["thickness"],
            "quantity": "1",
            "stone": size_data["stone"],
            "processing": size_data["processing"],
            "product_code": size_data["product_code"],
            "slab_no": str(current_slab_no),
            "slab_image": pending_slab_images[i]
        })
        tree.insert("", "end", values=(
            size_data["width"],
            size_data["length"],
            size_data["thickness"],
            "1",
            size_data["stone"],
            size_data["processing"],
            size_data["product_code"],
            str(current_slab_no),
            pending_slab_images[i]
        ))
    slab_counter = start_from + quantity
    
    for entry in [entry_width, entry_length, entry_thickness, entry_quantity]:
        entry.delete(0, "end")
    pending_slab_images.clear()
    print(f"Added sizes, slab_counter now: {slab_counter}")
    entry_width.focus_set()

# Function to select block image
def select_block_image():
    global block_image_path
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
    if file_path:
        try:
            Image.open(file_path)
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BundleData")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            timestamp = int(time.time() * 1000)
            block_image_name = f"block_{timestamp}.png"
            block_image_path = os.path.join(data_dir, block_image_name)
            shutil.copy(file_path, block_image_path)
            entry_block_image.delete(0, "end")
            entry_block_image.insert(0, block_image_path)
        except Exception as e:
            messagebox.showerror("Error", f"Invalid block image: {str(e)}")

# Function to add mine and extra details
def add_mine_details():
    mine_window = Toplevel(root)
    mine_window.title("Mine Details")
    mine_window.geometry("450x400")
    
    entries = []
    labels = [("Stone", "stone"), ("Processing", "processing"), ("Product Code", "product_code"), ("Description", "description"), ("Warehouse", "warehouse")]
    
    for i, (label_text, var_name) in enumerate(labels):
        Label(mine_window, text=label_text, font=("Arial", 12)).grid(row=i, column=0, padx=10, pady=10, sticky="e")
        entry = Entry(mine_window, width=30, font=("Arial", 12))
        entry.grid(row=i, column=1, padx=10, pady=10, sticky="w")
        entries.append(entry)
    
    def save_details():
        global mine_name, extra_info, stone, processing, product_code, description, warehouse
        values = [entry.get().strip() for entry in entries]
        if not all(values):
            messagebox.showerror("Error", "All fields are required!")
            return
        stone = values[0]
        processing = values[1]
        product_code = values[2]
        description = values[3]
        warehouse = values[4]
        mine_name = stone
        extra_info = f"{processing} | {product_code} | {description}"
        mine_window.destroy()
    
    def on_enter(event, current_entry, next_entry=None):
        if next_entry:
            next_entry.focus()
        else:
            save_details()
        return "break"

    for i, entry in enumerate(entries):
        if i < len(entries) - 1:
            entry.bind("<Return>", lambda e, ce=entry, ne=entries[i+1]: on_enter(e, ce, ne))
        else:
            entry.bind("<Return>", lambda e, ce=entry: on_enter(e, ce))
    
    Button(mine_window, text="Save", command=save_details, bg="#4682B4", fg="white", font=("Arial", 12)).grid(row=len(labels), column=0, columnspan=2, pady=20)

mine_name = ""
extra_info = ""
stone = ""
processing = ""
product_code = ""
description = ""
warehouse = ""
selected_date = ""
block_image_path = ""
temp_qr_path = ""
sticker_width = "5cm"
sticker_height = "15cm"
qr_size = "15mm"
font_size = "22px"
slab_counter = 1
pending_slab_images = []
sizes_list = []

# Function to generate QR Code, main PDF, and slab stickers
def generate_qr_and_html():
    global selected_date, block_image_path, stone, processing, product_code, description, warehouse, temp_qr_path, sticker_width, sticker_height, qr_size, font_size, sizes_list, slab_counter, save_location
    try:
        selected_date = entry_date.get().strip()
        bundle_no = entry_bundle_no.get().strip()
        sticker_width = entry_sticker_width.get().strip() or "5cm"
        sticker_height = entry_sticker_height.get().strip() or "15cm"
        qr_size = entry_qr_size.get().strip() or "15mm"
        font_size = entry_font_size.get().strip() or "12px"
        server_base_url = "https://my-slab-server.onrender.com"
        
        if not all([stone, processing, product_code, description, warehouse]):
            messagebox.showwarning("Warning", "Please fill Mine Details first!")
            return
        
        bundle_data = {
            "code": entry_code.get().strip(),
            "name": entry_name.get().strip(),
            "bundle_no": bundle_no,
            "shipment_no": entry_shipment_no.get().strip(),
            "sizes": sizes_list,
            "mine_name": mine_name,
            "extra_info": extra_info,
            "stone": stone,
            "processing": processing,
            "product_code": product_code,
            "description": description,
            "warehouse": warehouse,
            "date": selected_date,
            "block_image": block_image_path
        }
    
        for key, value in bundle_data.items():
            if key not in ["sizes", "shipment_no", "mine_name", "extra_info", "stone", "processing", "product_code", "description", "warehouse", "date", "block_image"] and not value:
                messagebox.showerror("Error", f"The field '{key}' cannot be empty!")
                return
        if not sizes_list:
            messagebox.showerror("Error", "Please add at least one size!")
            return
        if not selected_date:
            messagebox.showerror("Error", "Please select a date!")
            return
        if not block_image_path:
            messagebox.showerror("Error", "Please select a block image!")
            return
        
        name_mapping = load_name_mapping()
        if bundle_data["code"] not in name_mapping or bundle_data["name"] != name_mapping[bundle_data["code"]]["local_name"]:
            messagebox.showerror("Error", "Invalid code or name mismatch!")
            return
        
        # Upload block image
        upload_url = f"{server_base_url}/upload"
        try:
            with open(block_image_path, "rb") as block_file:
                files = {"file": (block_image_path, block_file)}
                response = requests.post(upload_url, files=files, timeout=30)
                if response.status_code != 200:
                    messagebox.showerror("Error", f"Failed to upload block image: {response.text}")
                    return
                block_image_url = response.json().get("url", "")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open or upload block image: {str(e)}")
            return

        # Upload slab images
        slab_image_urls = []
        for size in sizes_list:
            try:
                with open(size["slab_image"], "rb") as slab_file:
                    files = {"file": (size["slab_image"], slab_file)}
                    response = requests.post(upload_url, files=files, timeout=30)
                    if response.status_code != 200:
                        messagebox.showerror("Error", f"Failed to upload slab image {size['slab_image']}: {response.text}")
                        return
                    slab_image_urls.append(response.json().get("url", ""))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open or upload slab image {size['slab_image']}: {str(e)}")
                return
        for size, url in zip(sizes_list, slab_image_urls):
            size["slab_image"] = url
        
        # Group sizes by width, length, and thickness, summing quantities
        merged_sizes = {}
        for size in sizes_list:
            key = (size["width"], size["length"], size["thickness"])
            if key in merged_sizes:
                merged_sizes[key]["quantity"] = str(int(merged_sizes[key]["quantity"]) + int(size["quantity"]))
                merged_sizes[key]["slab_no"] = f"{min(int(s['slab_no']) for s in sizes_list if s['width'] == size['width'] and s['length'] == size['length'] and s['thickness'] == size['thickness'])}-{max(int(s['slab_no']) for s in sizes_list if s['width'] == size['width'] and s['length'] == size['length'] and s['thickness'] == size['thickness'])}"
            else:
                merged_sizes[key] = size.copy()
                merged_sizes[key]["quantity"] = size["quantity"]
                merged_sizes[key]["slab_no"] = size["slab_no"]
        sizes_list = list(merged_sizes.values())
        
        for size in sizes_list:
            for k, v in size.items():
                size[k] = str(v) if v is not None else "-"
        
        size_strings = [f"Width:{s['width']}cm,Length:{s['length']}cm,Thickness:{s['thickness']},Qty:{s['quantity']},Slab No:{s['slab_no']}" for s in sizes_list]
        qr_content = f"Code:{bundle_data['code']},Name:{bundle_data['name']},Iran Name:{name_mapping.get(bundle_data['code'], {}).get('iran_name', '-')},Bundle No:{bundle_data['bundle_no']},Shipment No:{bundle_data['shipment_no'] if bundle_data['shipment_no'] else '-'},Stone:{bundle_data['stone'] if bundle_data['stone'] else '-'},Processing:{bundle_data['processing'] if bundle_data['processing'] else '-'},Product Code:{bundle_data['product_code'] if bundle_data['product_code'] else '-'},Description:{bundle_data['description'] if bundle_data['description'] else '-'},Warehouse:{bundle_data['warehouse'] if bundle_data['warehouse'] else '-'},Date:{bundle_data['date']},Block Image:{block_image_url},Sizes:" + ";".join(size_strings)
        
        qr = qrcode.QRCode(version=5, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=5, border=4)
        qr.add_data(qr_content)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BundleData")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        timestamp = int(time.time() * 1000)
        temp_qr_path = os.path.join(data_dir, f"temp_qr_{timestamp}.png")
        qr_img.save(temp_qr_path)
        
        save_location = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], initialfile=f"{bundle_no}.pdf", title="Save Main PDF")
        if not save_location:
            if os.path.exists(temp_qr_path):
                os.remove(temp_qr_path)
            messagebox.showwarning("Warning", "Save location not selected. Operation cancelled.")
            return
        
        sticker_dir = os.path.join(os.path.dirname(save_location), "stickers")
        if not os.path.exists(sticker_dir):
            os.makedirs(sticker_dir)
        
        safe_name = "".join(c for c in bundle_data["name"] if c.isalnum() or c in (' ', '_')).replace(" ", "_")
        html_filename = os.path.join(data_dir, f"bundle_{bundle_data['code']}_{safe_name}_{bundle_data['bundle_no']}.html")
        pdf_filename = save_location
        
        total_quantity = sum(int(size["quantity"]) for size in sizes_list)
        total_area = sum(float(size["width"]) * float(size["length"]) * int(size["quantity"]) / 10000 for size in sizes_list)
        sqm_list = [float(size["width"]) * float(size["length"]) * int(size["quantity"]) / 10000 for size in sizes_list]
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Bundle Details</title>
            <style>
                @page {{ size: A5 portrait; margin: 0; }}
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; color: #333; position: relative; }}
                .header {{ background-color: #4682B4; padding: 10px; display: flex; align-items: center; height: 80px; }}
                .header .logo {{ height: 80px; max-height: 80px; margin-right: 10px; }}
                .header .title {{ color: white; font-size: 18px; font-weight: bold; text-align: center; flex-grow: 1; }}
                .date-container {{ margin: 10px 0 10px 40px; font-size: 12px; color: #4682B4; text-align: left; }}
                .container {{ max-width: 100%; margin: 0 10px; background: white; padding: 10px; border-radius: 5px; display: flex; flex-direction: column; }}
                .details {{ display: flex; justify-content: flex-start; gap: 0; margin-top: 5px; margin-bottom: 15px; font-size: 12px; position: relative; }}
                .details .column {{ flex: 0 1 150px; display: grid; grid-template-columns: 1fr; gap: 5px; }}
                .details .column div {{ padding: 5px; background: #E0F7FA; border-radius: 3px; font-weight: bold; min-height: 15px; }}
                .details .column:first-child {{ padding-right: 5px; }}
                .details .column:last-child {{ margin-left: -10px; }}
                .separator {{ position: absolute; top: 0; left: 50%; width: 1px; height: 100%; background: transparent; }}
                .qr-code {{ position: absolute; right: 50px; top: 142px; height: 155px; }}
                .qr-code img {{ max-width: 155px; border: 2px solid #4682B4; border-radius: 5px; }}
                .table-container {{ width: 90%; border-radius: 10px; overflow: hidden; border: 1px solid #ddd; margin: 50px auto; }}
                .table-container table {{ width: 100%; border-collapse: collapse; font-size: 16px; }}
                .table-container th, .table-container td {{ padding: 10px; text-align: center; border: 1px solid #ddd; }}
                .table-container th {{ background-color: #4682B4; color: white; }}
                .table-container tr:nth-child(even) {{ background-color: #f8f8f8; }}
                .table-container tr.total-row {{ font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <img src="logo.png" alt="Logo" class="logo">
                <span class="title">ETIFAQ GLOBAL NATURAL STONE TRADING LLC</span>
            </div>
            <div class="date-container">Date: {bundle_data['date']}</div>
            <div class="container">
                <div class="details">
                    <div class="column">
                        <div>Item Code: {bundle_data['code']}</div>
                        <div>Item Name: {bundle_data['name']}</div>
                        <div>Iran Name: {name_mapping.get(bundle_data['code'], {}).get('iran_name', '-')}</div>
                        <div>Bundle No: {bundle_data['bundle_no']}</div>
                        <div>Shipment No: {bundle_data['shipment_no'] if bundle_data['shipment_no'] else '-'}</div>
                    </div>
                    <div class="column">
                        <div>Stone: {bundle_data['stone'] if bundle_data['stone'] else '-'}</div>
                        <div>Processing: {bundle_data['processing'] if bundle_data['processing'] else '-'}</div>
                        <div>Product Code: {bundle_data['product_code'] if bundle_data['product_code'] else '-'}</div>
                        <div>Description: {bundle_data['description'] if bundle_data['description'] else '-'}</div>
                        <div>Warehouse: {bundle_data['warehouse'] if bundle_data['warehouse'] else '-'}</div>
                    </div>
                    <div class="separator"></div>
                </div>
                <div class="qr-code"><img src="{block_image_url}" alt="QR Code"></div>
                <div class="table-container">
                    <table>
                        <tr><th>No</th><th>Width (cm)</th><th>Length (cm)</th><th>Thickness</th><th>Qty</th><th>SQM</th></tr>
                        {"".join([f'<tr><td>{i+1}</td><td>{size["width"]}</td><td>{size["length"]}</td><td>{size["thickness"]}</td><td>{size["quantity"]}</td><td>{sqm_list[i]:.2f}</td></tr>' for i, size in enumerate(sizes_list)])}
                        <tr class="total-row"><td colspan="4">Total</td><td>{total_quantity}</td><td>{total_area:.2f}</td></tr>
                    </table>
                </div>
            </div>
        </body>
        </html>
        """
        with open(html_filename, "w", encoding="utf-8") as f:
            f.write(html_content)

        try:
            HTML(html_filename).write_pdf(pdf_filename)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate main PDF: {str(e)}")
            if os.path.exists(temp_qr_path):
                os.remove(temp_qr_path)
            return

        sticker_dir = os.path.join(os.path.dirname(save_location), "stickers")
        if not os.path.exists(sticker_dir):
            os.makedirs(sticker_dir)
        
        for size in sizes_list:
            quantity = int(size["quantity"])
            slab_no_range = size["slab_no"].split('-')
            start_slab_no = int(slab_no_range[0])
            for i in range(quantity):
                current_slab_no = start_slab_no + i
                data = {
                    "slab_no": str(current_slab_no),
                    "width": size["width"],
                    "length": size["length"],
                    "thickness": size["thickness"],
                    "stone": bundle_data["stone"],
                    "processing": bundle_data["processing"],
                    "product_code": bundle_data["product_code"],
                    "description": bundle_data["description"],
                    "warehouse": bundle_data["warehouse"],
                    "slab_image": size["slab_image"],
                    "block_image": block_image_url
                }
                slab_qr_content = f"{server_base_url}/slab?data={json.dumps(data)}"
                slab_qr = qrcode.QRCode(version=3, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=3, border=2)
                slab_qr.add_data(slab_qr_content)
                slab_qr.make(fit=True)
                slab_qr_img = slab_qr.make_image(fill_color="black", back_color="white")
                
                slab_qr_path = os.path.join(sticker_dir, f"slab_qr_{current_slab_no}_{timestamp}.png")
                slab_qr_img.save(slab_qr_path)
                
                dimensions = f"{size['width']} × {size['length']}"
                vertical_dimensions = "".join([f"<div>{c}</div>" for c in dimensions if c != " "])
                vertical_product_code = "".join([f"<div>{c}</div>" for c in bundle_data['product_code']]) if bundle_data['product_code'] else "<div>-</div>"
                
                sticker_html = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Slab Sticker {current_slab_no}</title>
                    <style>
                        @page {{ size: {sticker_width} {sticker_height}; margin: 0; }}
                        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; width: {sticker_width}; height: {sticker_height}; border: 1px dashed black; display: flex; flex-direction: column; align-items: center; }}
                        .sticker-container {{ display: flex; flex-direction: column; align-items: center; gap: 4mm; width: 2cm; height: 100%; justify-content: space-between; margin: 0 auto; border: 1px solid black; padding: 2mm; }}
                        .slab-no {{ background-color: black; color: white; font-size: {font_size}; font-weight: bold; padding: 2mm; width: 100%; text-align: center; }}
                        .separator {{ width: 90%; border-bottom: 1px solid #333; }}
                        .vertical-text div {{ line-height: 1.2; font-size: {font_size}; font-weight: bold; text-align: center; }}
                        .qr-code img {{ width: {qr_size}; height: {qr_size}; border: 1px solid #4682B4; }}
                    </style>
                </head>
                <body>
                    <div class="sticker-container">
                        <div class="slab-no">{current_slab_no}</div>
                        <div class="separator"></div>
                        <div class="vertical-text">{vertical_dimensions}</div>
                        <div class="separator"></div>
                        <div class="vertical-text">{vertical_product_code}</div>
                        <div class="separator"></div>
                        <div class="qr-code"><img src="{os.path.basename(slab_qr_path)}" alt="Slab QR Code"></div>
                    </div>
                </body>
                </html>
                """
                sticker_html_filename = os.path.join(sticker_dir, f"sticker_{current_slab_no}_{timestamp}.html")
                sticker_pdf_filename = os.path.join(sticker_dir, f"sticker_{current_slab_no}_{bundle_no}.pdf")
                
                with open(sticker_html_filename, "w", encoding="utf-8") as f:
                    f.write(sticker_html)
                
                try:
                    HTML(sticker_html_filename).write_pdf(sticker_pdf_filename)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to generate sticker for slab {current_slab_no}: {str(e)}")
                    if os.path.exists(slab_qr_path):
                        os.remove(slab_qr_path)
                    continue
                
                if os.path.exists(slab_qr_path):
                    os.remove(slab_qr_path)
        
        if os.path.exists(temp_qr_path):
            os.remove(temp_qr_path)
        
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BundleData")
        try:
            history = []
            try:
                with open(os.path.join(data_dir, 'qr_history.json'), 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except FileNotFoundError:
                pass
            
            history.append({
                "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "code": bundle_data["code"],
                "name": bundle_data["name"],
                "iran_name": name_mapping.get(bundle_data["code"], {}).get("iran_name", "-"),
                "bundle_no": bundle_data["bundle_no"],
                "sizes": sizes_list,
                "shipment_no": bundle_data["shipment_no"],
                "stone": bundle_data["stone"],
                "processing": bundle_data["processing"],
                "product_code": bundle_data["product_code"],
                "description": bundle_data["description"],
                "warehouse": bundle_data["warehouse"],
                "date": bundle_data["date"],
                "block_image": block_image_url
            })
            
            with open(os.path.join(data_dir, 'qr_history.json'), 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save history: {str(e)}")
        
        messagebox.showinfo("Success", f"Main PDF saved in: {pdf_filename}\nStickers saved in: {sticker_dir}")
        
        for entry in [entry_code, entry_name, entry_bundle_no, entry_shipment_no, entry_block_image, entry_start_from, entry_sticker_width, entry_sticker_height, entry_qr_size, entry_font_size]:
            entry.delete(0, "end")
        for entry in [entry_width, entry_length, entry_thickness, entry_quantity]:
            entry.delete(0, "end")
        entry_iran_name_dropdown.set("")
        entry_date.delete(0, "end")
        sizes_list.clear()
        pending_slab_images.clear()
        block_image_path = ""
        slab_counter = 1
        for child in tree.get_children():
            tree.delete(child)
        entry_iran_name_dropdown.focus_set()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        if os.path.exists(temp_qr_path):
            os.remove(temp_qr_path)

# Function to show history
def show_history():
    history_window = Toplevel(root)
    history_window.title("QR Code History")
    history_window.geometry("1200x500")
    
    tree = ttk.Treeview(history_window, columns=("Date", "Code", "Name", "Iran Name", "Bundle No", "Sizes", "Shipment No", "Stone", "Processing", "Product Code", "Description", "Warehouse", "Date", "Block Image"), show="headings", height=10)
    tree.heading("Date", text="Date")
    tree.heading("Code", text="Code")
    tree.heading("Name", text="Name")
    tree.heading("Iran Name", text="Iran Name")
    tree.heading("Bundle No", text="Bundle No")
    tree.heading("Sizes", text="Sizes")
    tree.heading("Shipment No", text="Shipment No")
    tree.heading("Stone", text="Stone")
    tree.heading("Processing", text="Processing")
    tree.heading("Product Code", text="Product Code")
    tree.heading("Description", text="Description")
    tree.heading("Warehouse", text="Warehouse")
    tree.heading("Date", text="Date")
    tree.heading("Block Image", text="Block Image")
    tree.pack(pady=10, fill="both", expand=True)
    
    history = []
    try:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BundleData")
        if not os.path.exists(data_dir):
            messagebox.showinfo("Info", "No history found.")
            return
        
        with open(os.path.join(data_dir, "qr_history.json"), "r", encoding="utf-8") as f:
            history = json.load(f)
        
        for row in history:
            tree.insert("", "end", values=(
                row["timestamp"],
                row["code"],
                row["name"],
                row["iran_name"],
                row["bundle_no"],
                str(row["sizes"]),
                row["shipment_no"],
                row.get("stone", "-"),
                row.get("processing", "-"),
                row.get("product_code", "-"),
                row.get("description", "-"),
                row.get("warehouse", "-"),
                row.get("date", "-"),
                row.get("block_image", "-")
            ))
    except FileNotFoundError:
        messagebox.showinfo("Info", "No history found.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load history: {str(e)}")

    def regenerate_pdf(event):
        global sizes_list, mine_name, extra_info, stone, processing, product_code, description, warehouse, selected_date, block_image_path, sticker_width, sticker_height, qr_size, font_size
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Error", "Please select a row to regenerate!")
            return
        item = tree.item(selected_item)
        values = item["values"]
        
        bundle_data = {
            "code": values[1],
            "name": values[2],
            "bundle_no": values[4],
            "shipment_no": values[6],
            "sizes": eval(values[5]),
            "stone": values[7],
            "processing": values[8],
            "product_code": values[9],
            "description": values[10],
            "warehouse": values[11],
            "date": values[12],
            "block_image": values[13]
        }
        
        sizes_list = bundle_data["sizes"]
        stone = bundle_data["stone"]
        processing = bundle_data["processing"]
        product_code = bundle_data["product_code"]
        description = bundle_data["description"]
        warehouse = bundle_data["warehouse"]
        mine_name = stone
        extra_info = f"{processing} | {product_code} | {description}"
        selected_date = bundle_data["date"]
        block_image_path = bundle_data["block_image"]
        sticker_width = "5cm"
        sticker_height = "15cm"
        qr_size = "15mm"
        font_size = "12px"
        
        entry_code.delete(0, "end")
        entry_code.insert(0, bundle_data["code"])
        entry_name.delete(0, "end")
        entry_name.insert(0, bundle_data["name"])
        entry_bundle_no.delete(0, "end")
        entry_bundle_no.insert(0, bundle_data["bundle_no"])
        entry_shipment_no.delete(0, "end")
        entry_shipment_no.insert(0, bundle_data["shipment_no"])
        entry_date.delete(0, "end")
        entry_date.insert(0, bundle_data["date"])
        entry_block_image.delete(0, "end")
        entry_block_image.insert(0, block_image_path)
        entry_sticker_width.delete(0, "end")
        entry_sticker_width.insert(0, sticker_width)
        entry_sticker_height.delete(0, "end")
        entry_sticker_height.insert(0, sticker_height)
        entry_qr_size.delete(0, "end")
        entry_qr_size.insert(0, qr_size)
        entry_font_size.delete(0, "end")
        entry_font_size.insert(0, font_size)
        
        generate_qr_and_html()

    tree.bind("<Double-1>", regenerate_pdf)

# Function to close the program
def on_closing():
    root.destroy()

# Set up the GUI
root = Tk()
root.title("Generate QR Codes for Items")
root.geometry("1000x700")
root.configure(bg="#F0F0F5")

# Title
Label(root, text="Generate QR Codes for Items", font=("Arial", 16, "bold"), bg="#F0F0F5", fg="#333333").pack(pady=10)

# Bundle Info Frame
bundle_frame = ttk.LabelFrame(root, text="Bundle Information", padding=10)
bundle_frame.pack(fill="x", padx=10, pady=5)

# Iran Name and Date
bundle_row1 = ttk.Frame(bundle_frame)
bundle_row1.pack(fill="x", pady=5)

Label(bundle_row1, text="Iran Name", font=("Arial", 12), bg="#F0F0F5").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_iran_name_dropdown = ttk.Combobox(bundle_row1, width=15, font=("Arial", 12))
name_mapping = load_name_mapping()
iran_names = [data["iran_name"] for data in name_mapping.values()]
entry_iran_name_dropdown["values"] = iran_names
entry_iran_name_dropdown.bind("<<ComboboxSelected>>", update_item_details)
entry_iran_name_dropdown.grid(row=0, column=1, padx=10, pady=5, sticky="w")

Label(bundle_row1, text="Date", font=("Arial", 12), bg="#F0F0F5").grid(row=0, column=2, padx=10, pady=5, sticky="e")
entry_date = DateEntry(bundle_row1, width=15, font=("Arial", 12), date_pattern="dd-mm-yyyy")
entry_date.grid(row=0, column=3, padx=10, pady=5, sticky="w")

# Block Image
bundle_row2 = ttk.Frame(bundle_frame)
bundle_row2.pack(fill="x", pady=5)

Label(bundle_row2, text="Block Image", font=("Arial", 12), bg="#F0F0F5").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_block_image = Entry(bundle_row2, width=25, font=("Arial", 12))
entry_block_image.grid(row=0, column=1, padx=10, pady=5, sticky="w")
Button(bundle_row2, text="Select", command=select_block_image, bg="#4682B4", fg="white", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5)

# Bundle Details
bundle_row3 = ttk.Frame(bundle_frame)
bundle_row3.pack(fill="x", pady=5)

fields_row1 = [
    ("Item Code", "code"),
    ("Item Name", "name"),
    ("Bundle No", "bundle_no"),
    ("Shipment No", "shipment_no"),
    ("Start From", "start_from"),
]

entries = {}
for col, (label_text, var_name) in enumerate(fields_row1):
    Label(bundle_row3, text=label_text, font=("Arial", 12), bg="#F0F0F5").grid(row=0, column=col*2, padx=10, pady=5, sticky="e")
    entry = Entry(bundle_row3, width=15, font=("Arial", 12))
    entry.grid(row=0, column=col*2+1, padx=10, pady=5, sticky="w")
    entries[var_name] = entry

# Sticker Size Settings
sticker_frame = ttk.LabelFrame(root, text="Sticker Settings", padding=10)
sticker_frame.pack(fill="x", padx=10, pady=5)

sticker_row1 = ttk.Frame(sticker_frame)
sticker_row1.pack(fill="x", pady=5)

Label(sticker_row1, text="Sticker Width", font=("Arial", 12), bg="#F0F0F5").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_sticker_width = Entry(sticker_row1, width=15, font=("Arial", 12))
entry_sticker_width.grid(row=0, column=1, padx=10, pady=5, sticky="w")
entry_sticker_width.insert(0, sticker_width)

Label(sticker_row1, text="Sticker Height", font=("Arial", 12), bg="#F0F0F5").grid(row=0, column=2, padx=10, pady=5, sticky="e")
entry_sticker_height = Entry(sticker_row1, width=15, font=("Arial", 12))
entry_sticker_height.grid(row=0, column=3, padx=10, pady=5, sticky="w")
entry_sticker_height.insert(0, sticker_height)

sticker_row2 = ttk.Frame(sticker_frame)
sticker_row2.pack(fill="x", pady=5)

Label(sticker_row2, text="QR Size", font=("Arial", 12), bg="#F0F0F5").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_qr_size = Entry(sticker_row2, width=15, font=("Arial", 12))
entry_qr_size.grid(row=0, column=1, padx=10, pady=5, sticky="w")
entry_qr_size.insert(0, qr_size)

Label(sticker_row2, text="Font Size", font=("Arial", 12), bg="#F0F0F5").grid(row=0, column=2, padx=10, pady=5, sticky="e")
entry_font_size = Entry(sticker_row2, width=15, font=("Arial", 12))
entry_font_size.grid(row=0, column=3, padx=10, pady=5, sticky="w")
entry_font_size.insert(0, font_size)

# Slab Info Frame
slab_frame = ttk.LabelFrame(root, text="Slab Information", padding=10)
slab_frame.pack(fill="x", padx=10, pady=5)

slab_row1 = ttk.Frame(slab_frame)
slab_row1.pack(fill="x", pady=5)

fields_row2 = [
    ("Width (cm)", "width"),
    ("Length (cm)", "length"),
    ("Thickness", "thickness"),
    ("Quantity", "quantity"),
]

for col, (label_text, var_name) in enumerate(fields_row2):
    Label(slab_row1, text=label_text, font=("Arial", 12), bg="#F0F0F5").grid(row=0, column=col*2, padx=10, pady=5, sticky="e")
    entry = Entry(slab_row1, width=15, font=("Arial", 12))
    entry.grid(row=0, column=col*2+1, padx=10, pady=5, sticky="w")
    entries[var_name] = entry

# Add Select Images and Add Size Buttons
slab_row2 = ttk.Frame(slab_frame)
slab_row2.pack(fill="x", pady=5)
Button(slab_row2, text="Select Slab Images", command=select_slab_images, bg="#4682B4", fg="white", font=("Arial", 12), width=15).pack(side="left", padx=5)
Button(slab_row2, text="Add Size", command=add_size, bg="#4682B4", fg="white", font=("Arial", 12), width=15).pack(side="left", padx=5)

# Sizes List Frame
sizes_frame = ttk.LabelFrame(root, text="Sizes List", padding=10)
sizes_frame.pack(fill="both", expand=True, padx=10, pady=5)

tree = ttk.Treeview(sizes_frame, columns=("Width", "Length", "Thickness", "Quantity", "Stone", "Processing", "Product Code", "Slab No", "Slab Image"), show="headings", height=8)
tree.heading("Width", text="Width (cm)")
tree.heading("Length", text="Length (cm)")
tree.heading("Thickness", text="Thickness")
tree.heading("Quantity", text="Quantity")
tree.heading("Stone", text="Stone")
tree.heading("Processing", text="Processing")
tree.heading("Product Code", text="Product Code")
tree.heading("Slab No", text="Slab No")
tree.heading("Slab Image", text="Slab Image")
tree.column("Width", width=80, anchor="center")
tree.column("Length", width=80, anchor="center")
tree.column("Thickness", width=80, anchor="center")
tree.column("Quantity", width=80, anchor="center")
tree.column("Stone", width=100, anchor="center")
tree.column("Processing", width=100, anchor="center")
tree.column("Product Code", width=100, anchor="center")
tree.column("Slab No", width=100, anchor="center")
tree.column("Slab Image", width=150, anchor="center")
tree.pack(fill="both", expand=True, padx=10, pady=10)

# Button Frame
button_frame = ttk.Frame(root)
button_frame.pack(fill="x", pady=10)

Button(button_frame, text="Mine Details", command=add_mine_details, bg="#4682B4", fg="white", font=("Arial", 12), width=15).pack(side="left", padx=5)
Button(button_frame, text="Data Entry (Admin)", command=check_admin_access, bg="#4682B4", fg="white", font=("Arial", 12), width=15).pack(side="left", padx=5)
Button(button_frame, text="Generate PDF", command=generate_qr_and_html, bg="#32CD32", fg="white", font=("Arial", 12), width=15).pack(side="left", padx=5)
Button(button_frame, text="Show History", command=show_history, bg="#4682B4", fg="white", font=("Arial", 12), width=15).pack(side="left", padx=5)

entry_code = entries["code"]
entry_name = entries["name"]
entry_bundle_no = entries["bundle_no"]
entry_shipment_no = entries["shipment_no"]
entry_start_from = entries["start_from"]
entry_width = entries["width"]
entry_length = entries["length"]
entry_thickness = entries["thickness"]
entry_quantity = entries["quantity"]

# Bind Enter key for navigation
entry_iran_name_dropdown.bind("<Return>", lambda e: focus_next(entry_iran_name_dropdown))
entry_date.bind("<Return>", lambda e: focus_next(entry_date))
entry_block_image.bind("<Return>", lambda e: focus_next(entry_block_image))
entry_code.bind("<Return>", lambda e: focus_next(entry_code))
entry_name.bind("<Return>", lambda e: focus_next(entry_name))
entry_bundle_no.bind("<Return>", lambda e: focus_next(entry_bundle_no))
entry_shipment_no.bind("<Return>", lambda e: focus_next(entry_shipment_no))
entry_start_from.bind("<Return>", lambda e: focus_next(entry_start_from))
entry_width.bind("<Return>", lambda e: focus_next(entry_width))
entry_length.bind("<Return>", lambda e: focus_next(entry_length))
entry_thickness.bind("<Return>", lambda e: focus_next(entry_thickness))
entry_quantity.bind("<Return>", lambda e: focus_next(entry_quantity))
entry_sticker_width.bind("<Return>", lambda e: focus_next(entry_sticker_width))
entry_sticker_height.bind("<Return>", lambda e: focus_next(entry_sticker_height))
entry_qr_size.bind("<Return>", lambda e: focus_next(entry_qr_size))
entry_font_size.bind("<Return>", lambda e: focus_next(entry_font_size))

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
