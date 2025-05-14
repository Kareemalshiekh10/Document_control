from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from database import get_document_types, get_projects, get_sites, get_statuses, get_users, insert_document, get_all_documents, delete_document, get_dashboard_stats, init_db

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize database (run once)
init_db()

@app.route('/uploads/<path:filename>')
def serve_uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/', methods=['GET', 'POST'])
def index():
    # Handle filter form submission
    filters = {}
    if request.method == 'POST' and 'filter' in request.form:
        document_type = request.form.get('document_type')
        project = request.form.get('project')
        site = request.form.get('site')
        status = request.form.get('status')
        date = request.form.get('date')  # New date filter
        if document_type:
            filters['document_type'] = document_type
        if project:
            filters['project'] = project
        if site:
            filters['site'] = site
        if status:
            filters['status'] = status
        if date:
            filters['date'] = date

    document_types = get_document_types()
    projects = get_projects()
    sites = get_sites()
    statuses = get_statuses()
    users = get_users()
    documents = get_all_documents(filters)
    return render_template('index.html', 
                         document_types=document_types,
                         projects=projects,
                         sites=sites,
                         statuses=statuses,
                         users=users,
                         documents=documents,
                         filters=filters)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        print("No file part in request")
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        print("No file selected")
        return redirect(url_for('index'))
    
    document_type_id = request.form['document_type']
    project_id = request.form['project']
    site_id = request.form['site']
    status_id = request.form['status']
    uploaded_by = request.form['user']
    
    if file:
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        print(f"Inserting document: {filename}, path: {file_path}")
        insert_document(filename, file_path, document_type_id, project_id, site_id, status_id, uploaded_by)
        return redirect(url_for('index', success='Document uploaded successfully'))

@app.route('/delete/<int:document_id>', methods=['POST'])
def delete_file(document_id):
    file_path = delete_document(document_id)
    if file_path and os.path.exists(file_path):
        print(f"Deleting file: {file_path}")
        os.remove(file_path)
    else:
        print(f"File not found for deletion: {file_path}")
    return redirect(url_for('index', success='Document deleted successfully'))

@app.route('/dashboard')
def dashboard():
    stats = get_dashboard_stats()
    return render_template('dashboard.html', stats=stats)

if __name__ == '__main__':
    app.run(debug=True)