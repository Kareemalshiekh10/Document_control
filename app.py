# app.py

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, make_response
import os
from database import get_document_types, get_projects, get_sites, get_statuses, get_users, insert_document, get_all_documents, delete_document, get_dashboard_stats, init_db, get_issue_statuses, insert_issue, get_all_issues, delete_issue, get_documents_for_issue, get_db_connection, insert_issue_attachment, delete_issue_attachment, get_issue_stats

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
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print(f"Attempting to serve file: {file_path}")  # Debug log
    if os.path.exists(file_path):
        print(f"File found, serving: {file_path}")
        response = make_response(send_from_directory(app.config['UPLOAD_FOLDER'], filename))
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        print(f"File not found: {file_path}")
        return "File not found", 404

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

@app.route('/issues', methods=['GET', 'POST'])
def issues():
    filters = {}
    if request.method == 'POST' and 'filter' in request.form:
        project = request.form.get('project')
        site = request.form.get('site')
        status = request.form.get('status')
        date = request.form.get('date')
        if project:
            filters['project'] = project
        if site:
            filters['site'] = site
        if status:
            filters['status'] = status
        if date:
            filters['date'] = date

    projects = get_projects()
    sites = get_sites()
    issue_statuses = get_issue_statuses()
    users = get_users()
    issues = get_all_issues(filters)
    return render_template('issues.html',
                         projects=projects,
                         sites=sites,
                         issue_statuses=issue_statuses,
                         users=users,
                         issues=issues,
                         filters=filters,
                         get_documents_for_issue=get_documents_for_issue)

@app.route('/report_issue', methods=['POST'])
def report_issue():
    title = request.form['title']
    description = request.form.get('description', '')
    project_id = request.form['project']
    site_id = request.form['site']
    status_id = request.form['status']
    reported_by = request.form['reported_by']
    deadline = request.form.get('deadline', None)  # Optional deadline field
    attachment_ids = []

    # Handle multiple file uploads as attachments
    if 'files' in request.files:
        files = request.files.getlist('files')
        issue_id = insert_issue(title, description, project_id, site_id, status_id, reported_by, deadline)
        for file in files:
            if file and file.filename != '':
                filename = file.filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                print(f"Inserting attachment: {filename}, path: {file_path}, issue_id: {issue_id}")
                insert_issue_attachment(filename, file_path, issue_id, reported_by)
                # Fetch the new attachment's ID
                conn = get_db_connection()
                new_attachment = conn.execute('SELECT id FROM issue_attachments WHERE filename = ?', (filename,)).fetchone()
                conn.close()
                if new_attachment:
                    attachment_ids.append(str(new_attachment['id']))
                else:
                    print(f"Failed to find attachment in database: {filename}")

    return redirect(url_for('issues', success='Issue reported successfully'))

@app.route('/delete_issue/<int:issue_id>', methods=['POST'])
def delete_issue_route(issue_id):
    conn = get_db_connection()
    # Delete attachments first
    attachments = conn.execute('SELECT id, file_path FROM issue_attachments WHERE issue_id = ?', (issue_id,)).fetchall()
    for attachment in attachments:
        file_path = attachment['file_path']
        if os.path.exists(file_path):
            os.remove(file_path)
        delete_issue_attachment(attachment['id'])
    # Then delete the issue
    delete_issue(issue_id)
    conn.close()
    return redirect(url_for('issues', success='Issue deleted successfully'))

@app.route('/dashboard')
def dashboard():
    doc_stats = get_dashboard_stats()
    issue_stats = get_issue_stats()
    return render_template('dashboard.html', doc_stats=doc_stats, issue_stats=issue_stats)

if __name__ == '__main__':
    app.run(debug=True)