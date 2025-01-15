from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import os

app = Flask(__name__)

ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'root')


def get_abs_path(relative_path):
    return os.path.join(ROOT_DIR, relative_path)

@app.route('/')
@app.route('/root/')
@app.route('/root/<path:subpath>')
def index(subpath=""):
    # Show the contents of the specified directory
    abs_path = get_abs_path(subpath)
    if not os.path.isdir(abs_path):
        return "Invalid directory path", 404

    # List items in the current directory
    items = os.listdir(abs_path)
    
    # Determine the parent path for the 'Go Up' functionality
    parent_path = '/'.join(subpath.split('/')[:-1]) if subpath else ""
    
    return render_template('index.html', items=items, current_path=subpath, parent_path=parent_path)

@app.route('/create', methods=['POST'])
def create():
    item_type = request.form['item_type']
    item_name = request.form['item_name']
    current_path = request.form['current_path']
    
    abs_path = get_abs_path(current_path)
    success = False
    
    if item_type == 'folder':
        try:
            os.makedirs(os.path.join(abs_path, item_name), exist_ok=True)
            success = True
        except Exception as e:
            print(f"Error creating folder: {e}")
    elif item_type == 'file':
        try:
            with open(os.path.join(abs_path, item_name), 'w') as f:
                f.write("")  # Create an empty file
            success = True
        except Exception as e:
            print(f"Error creating file: {e}")

    # Return JSON response to indicate success or failure
    return jsonify(success=success)

@app.route('/delete/<path:subpath>')
def delete(subpath):
    abs_path = get_abs_path(subpath)
    if os.path.isdir(abs_path):
        os.rmdir(abs_path)  # Only deletes empty folders
    elif os.path.isfile(abs_path):
        os.remove(abs_path)
    return redirect(url_for('index'))

@app.route('/open/<path:subpath>')
def open_file(subpath):
    abs_path = get_abs_path(subpath)
    if os.path.isfile(abs_path):
        with open(abs_path, 'r') as f:
            content = f.read()
        return render_template('file_view.html', content=content, file_path=subpath)
    return redirect(url_for('index'))

@app.route('/rename', methods=['POST'])
def rename():
    current_path = request.form['current_path']
    old_name = request.form['old_name']
    new_name = request.form['new_name']
    
    abs_path = get_abs_path(current_path)
    old_path = os.path.join(abs_path, old_name)
    new_path = os.path.join(abs_path, new_name)
    
    if not os.path.exists(old_path):
        return jsonify(success=False, error="Original item not found")
    
    try:
        os.rename(old_path, new_path)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

@app.route('/write', methods=['POST'])
def write():
    file_path = request.form['file_path']
    content = request.form['content']
    abs_path = get_abs_path(file_path)
    with open(abs_path, 'w') as f:
        f.write(content)
    return redirect(url_for('open_file', subpath=file_path))

@app.route('/close/<path:subpath>')
def close(subpath):
    # Redirect back to the file explorer after "closing" the file
    return redirect(url_for('index', subpath=os.path.dirname(subpath)))

if __name__ == '__main__':
    app.run(debug=True)
