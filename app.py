from flask import Flask, render_template, request, redirect, url_for, send_from_directory, make_response
import os
import database as db  # Use alias 'db' to avoid name collision

app = Flask(__name__, template_folder='templates', static_folder='static')
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize database (run once)
db.init_db()

@app.route('/uploads/<path:filename>')
def serve_uploaded_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print(f"Attempting to serve file: {file_path}")
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
    filters = {}
    if request.method == 'POST' and 'filter' in request.form:
        document_type = request.form.get('document_type')
        project = request.form.get('project')
        site = request.form.get('site')
        status = request.form.get('status')
        date = request.form.get('date')
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

    document_types = db.get_document_types()
    projects = db.get_projects()
    sites = db.get_sites()
    statuses = db.get_statuses()
    users = db.get_users()
    documents = db.get_all_documents(filters)
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
        db.insert_document(filename, file_path, document_type_id, project_id, site_id, status_id, uploaded_by)
        return redirect(url_for('index', success='Document uploaded successfully'))

@app.route('/delete/<int:document_id>', methods=['POST'])
def delete_file(document_id):
    file_path = db.delete_document(document_id)
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
        return redirect(url_for('issues', **filters))
    else:
        filters['project'] = request.args.get('project', '')
        filters['site'] = request.args.get('site', '')
        filters['status'] = request.args.get('status', '')
        filters['date'] = request.args.get('date', '')

    projects = db.get_projects()
    sites = db.get_sites()
    issue_statuses = db.get_issue_statuses()
    users = db.get_users()
    issues = db.get_all_issues(filters)
    # Debug logging to verify data
    print("Issues:", [dict(issue) for issue in issues])
    print("Issue Statuses:", [dict(status) for status in issue_statuses])
    return render_template('issues.html',
                         projects=projects,
                         sites=sites,
                         issue_statuses=issue_statuses,
                         users=users,
                         issues=issues,
                         filters=filters,
                         get_documents_for_issue=db.get_documents_for_issue)

@app.route('/report_issue', methods=['POST'])
def report_issue():
    title = request.form['title']
    description = request.form.get('description', '')
    project_id = request.form['project']
    site_id = request.form['site']
    status_id = request.form['status']
    reported_by = request.form['reported_by']
    deadline = request.form.get('deadline', None)
    attachment_ids = []

    if 'files' in request.files:
        files = request.files.getlist('files')
        issue_id = db.insert_issue(title, description, project_id, site_id, status_id, reported_by, deadline)
        for file in files:
            if file and file.filename != '':
                filename = file.filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                print(f"Inserting attachment: {filename}, path: {file_path}, issue_id: {issue_id}")
                db.insert_issue_attachment(filename, file_path, issue_id, reported_by)
                conn = db.get_db_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM issue_attachments WHERE filename = %s', (filename,))
                new_attachment = cursor.fetchone()
                conn.close()
                if new_attachment:
                    attachment_ids.append(str(new_attachment['id']))
                else:
                    print(f"Failed to find attachment in database: {filename}")

    filters = {
        'project': request.args.get('project', ''),
        'site': request.args.get('site', ''),
        'status': request.args.get('status', ''),
        'date': request.args.get('date', '')
    }
    return redirect(url_for('issues', success='Issue reported successfully', **filters))

@app.route('/delete_issue/<int:issue_id>', methods=['POST'])
def delete_issue_route(issue_id):
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, file_path FROM issue_attachments WHERE issue_id = %s', (issue_id,))
    attachments = cursor.fetchall()
    for attachment in attachments:
        file_path = attachment['file_path']
        if os.path.exists(file_path):
            os.remove(file_path)
        db.delete_issue_attachment(attachment['id'])
    db.delete_issue(issue_id)
    conn.close()
    filters = {
        'project': request.args.get('project', ''),
        'site': request.args.get('site', ''),
        'status': request.args.get('status', ''),
        'date': request.args.get('date', '')
    }
    return redirect(url_for('issues', success='Issue deleted successfully', **filters))

@app.route('/update_issue_status', methods=['POST'])
def update_issue_status():
    issue_id = request.form.get('issue_id')
    status_id = request.form.get('status')
    
    if not issue_id or not status_id:
        filters = {
            'project': request.args.get('project', ''),
            'site': request.args.get('site', ''),
            'status': request.args.get('status', ''),
            'date': request.args.get('date', '')
        }
        return redirect(url_for('issues', error='Missing issue_id or status', **filters))
    
    success = db.update_issue_status(issue_id, status_id)
    filters = {
        'project': request.args.get('project', ''),
        'site': request.args.get('site', ''),
        'status': request.args.get('status', ''),
        'date': request.args.get('date', '')
    }
    filters['status'] = ''
    if success:
        return redirect(url_for('issues', success='Status updated successfully', **filters))
    else:
        return redirect(url_for('issues', error='Failed to update status', **filters))

@app.route('/dashboard')
def dashboard():
    doc_stats = db.get_dashboard_stats()
    issue_stats = db.get_issue_stats()
    return render_template('dashboard.html', doc_stats=doc_stats, issue_stats=issue_stats)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=not os.environ.get('RENDER'))