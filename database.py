import psycopg2
from psycopg2.extras import DictCursor
import os
from datetime import datetime
import urllib.parse

# Use DATABASE_URL from environment (set by Render)
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Parse the DATABASE_URL
    parsed_url = urllib.parse.urlparse(DATABASE_URL)
    DATABASE = {
        'dbname': parsed_url.path[1:],  # Remove the leading '/'
        'user': parsed_url.username,
        'password': parsed_url.password,
        'host': parsed_url.hostname,
        'port': parsed_url.port,
        'sslmode': 'require'
    }
else:
    # Fallback for local development
    DATABASE = {
        'dbname': 'document_control',
        'user': 'doc_user',
        'password': 'asdfgh123!@#',
        'host': 'localhost',
        'port': '5432'
    }

def get_db_connection():
    conn = psycopg2.connect(**DATABASE, cursor_factory=DictCursor)
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create document_types table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS document_types (
            id SERIAL PRIMARY KEY,
            type_name TEXT NOT NULL UNIQUE
        )
    ''')

    # Create projects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            project_name TEXT NOT NULL UNIQUE
        )
    ''')

    # Create sites table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sites (
            id SERIAL PRIMARY KEY,
            site_name TEXT NOT NULL UNIQUE
        )
    ''')

    # Create statuses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS statuses (
            id SERIAL PRIMARY KEY,
            status_name TEXT NOT NULL UNIQUE
        )
    ''')

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE
        )
    ''')

    # Create documents table with foreign keys
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            document_type_id INTEGER,
            project_id INTEGER,
            site_id INTEGER,
            status_id INTEGER,
            uploaded_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_type_id) REFERENCES document_types(id),
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (site_id) REFERENCES sites(id),
            FOREIGN KEY (status_id) REFERENCES statuses(id),
            FOREIGN KEY (uploaded_by) REFERENCES users(id)
        )
    ''')

    # Create issue_statuses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS issue_statuses (
            id SERIAL PRIMARY KEY,
            status_name TEXT NOT NULL UNIQUE
        )
    ''')

    # Create issues table with deadline
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS issues (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            project_id INTEGER,
            site_id INTEGER,
            status_id INTEGER,
            reported_by INTEGER,
            deadline DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (site_id) REFERENCES sites(id),
            FOREIGN KEY (status_id) REFERENCES issue_statuses(id),
            FOREIGN KEY (reported_by) REFERENCES users(id)
        )
    ''')

    # Create issue_documents junction table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS issue_documents (
            issue_id INTEGER,
            document_id INTEGER,
            FOREIGN KEY (issue_id) REFERENCES issues(id),
            FOREIGN KEY (document_id) REFERENCES documents(id),
            PRIMARY KEY (issue_id, document_id)
        )
    ''')

    # Create issue_attachments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS issue_attachments (
            id SERIAL PRIMARY KEY,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            issue_id INTEGER,
            uploaded_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (issue_id) REFERENCES issues(id),
            FOREIGN KEY (uploaded_by) REFERENCES users(id)
        )
    ''')

    # Insert default data if tables are empty
    # Check and insert document_types
    cursor.execute('SELECT COUNT(*) FROM document_types')
    doc_type_count = cursor.fetchone()[0]
    if doc_type_count == 0:
        cursor.execute('INSERT INTO document_types (type_name) VALUES (%s) ON CONFLICT (type_name) DO NOTHING', ('Type A',))
        cursor.execute('INSERT INTO document_types (type_name) VALUES (%s) ON CONFLICT (type_name) DO NOTHING', ('Type B',))

    # Check and insert statuses (for documents)
    cursor.execute('SELECT COUNT(*) FROM statuses')
    status_count = cursor.fetchone()[0]
    if status_count == 0:
        cursor.execute('INSERT INTO statuses (status_name) VALUES (%s) ON CONFLICT (status_name) DO NOTHING', ('Draft',))
        cursor.execute('INSERT INTO statuses (status_name) VALUES (%s) ON CONFLICT (status_name) DO NOTHING', ('Final',))

    # Check and insert projects
    cursor.execute('SELECT COUNT(*) FROM projects')
    project_count = cursor.fetchone()[0]
    if project_count == 0:
        cursor.execute('INSERT INTO projects (project_name) VALUES (%s) ON CONFLICT (project_name) DO NOTHING', ('Project A',))
        cursor.execute('INSERT INTO projects (project_name) VALUES (%s) ON CONFLICT (project_name) DO NOTHING', ('Project B',))

    # Check and insert sites
    cursor.execute('SELECT COUNT(*) FROM sites')
    site_count = cursor.fetchone()[0]
    if site_count == 0:
        cursor.execute('INSERT INTO sites (site_name) VALUES (%s) ON CONFLICT (site_name) DO NOTHING', ('Site 1',))
        cursor.execute('INSERT INTO sites (site_name) VALUES (%s) ON CONFLICT (site_name) DO NOTHING', ('Site 2',))

    # Check and insert issue statuses
    cursor.execute('SELECT COUNT(*) FROM issue_statuses')
    issue_status_count = cursor.fetchone()[0]
    if issue_status_count == 0:
        cursor.execute('INSERT INTO issue_statuses (status_name) VALUES (%s) ON CONFLICT (type_name) DO NOTHING', ('Open',))
        cursor.execute('INSERT INTO issue_statuses (status_name) VALUES (%s) ON CONFLICT (type_name) DO NOTHING', ('Closed',))

    # Check and insert users
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    if user_count == 0:
        cursor.execute('INSERT INTO users (username) VALUES (%s) ON CONFLICT (username) DO NOTHING', ('user1',))

    # Check and insert test documents
    cursor.execute('SELECT COUNT(*) FROM documents')
    document_count = cursor.fetchone()[0]
    if document_count == 0:
        uploads_dir = os.path.join(os.getcwd(), 'uploads')
        cursor.execute('''
            INSERT INTO documents (filename, file_path, document_type_id, project_id, site_id, status_id, uploaded_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', ('doc1.pdf', os.path.join(uploads_dir, 'doc1.pdf'), 1, 1, 1, 1, 1))
        cursor.execute('''
            INSERT INTO documents (filename, file_path, document_type_id, project_id, site_id, status_id, uploaded_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', ('doc2.pdf', os.path.join(uploads_dir, 'doc2.pdf'), 2, 2, 2, 2, 1))

    # Check and insert test issues with deadlines
    cursor.execute('SELECT COUNT(*) FROM issues')
    issue_count = cursor.fetchone()[0]
    if issue_count == 0:
        cursor.execute('''
            INSERT INTO issues (title, description, project_id, site_id, status_id, reported_by, deadline)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', ('Test Issue 1', 'Description 1', 1, 1, 1, 1, '2025-05-14'))
        cursor.execute('''
            INSERT INTO issues (title, description, project_id, site_id, status_id, reported_by, deadline)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', ('Test Issue 2', 'Description 2', 1, 1, 1, 1, '2025-05-15'))
        cursor.execute('''
            INSERT INTO issues (title, description, project_id, site_id, status_id, reported_by, deadline)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', ('Test Issue 3', 'Description 3', 2, 2, 2, 1, '2025-05-16'))

    conn.commit()
    conn.close()

def get_document_types():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM document_types')
    document_types = cursor.fetchall()
    conn.close()
    return document_types

def get_projects():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projects')
    projects = cursor.fetchall()
    conn.close()
    return projects

def get_sites():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sites')
    sites = cursor.fetchall()
    conn.close()
    return sites

def get_statuses():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM statuses')
    statuses = cursor.fetchall()
    conn.close()
    return statuses

def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return users

def get_issue_statuses():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM issue_statuses')
    statuses = cursor.fetchall()
    conn.close()
    return statuses

def insert_document(filename, file_path, document_type_id, project_id, site_id, status_id, uploaded_by):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO documents (filename, file_path, document_type_id, project_id, site_id, status_id, uploaded_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (filename, file_path, document_type_id, project_id, site_id, status_id, uploaded_by))
    conn.commit()
    conn.close()

def insert_issue_attachment(filename, file_path, issue_id, uploaded_by):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO issue_attachments (filename, file_path, issue_id, uploaded_by)
        VALUES (%s, %s, %s, %s)
    ''', (filename, file_path, issue_id, uploaded_by))
    conn.commit()
    conn.close()

def insert_issue(title, description, project_id, site_id, status_id, reported_by, deadline, attachment_ids=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO issues (title, description, project_id, site_id, status_id, reported_by, deadline)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    ''', (title, description, project_id, site_id, status_id, reported_by, deadline))
    issue_id = cursor.fetchone()['id']
    conn.commit()
    conn.close()
    return issue_id

def get_all_documents(filters=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = '''
        SELECT d.id, d.filename, d.file_path, dt.type_name, p.project_name, s.site_name, st.status_name, u.username, d.created_at
        FROM documents d
        JOIN document_types dt ON d.document_type_id = dt.id
        JOIN projects p ON d.project_id = p.id
        JOIN sites s ON d.site_id = s.id
        JOIN statuses st ON d.status_id = st.id
        JOIN users u ON d.uploaded_by = u.id
    '''
    params = []
    conditions = []

    if filters:
        if filters.get('document_type'):
            conditions.append('dt.type_name = %s')
            params.append(filters['document_type'])
        if filters.get('project'):
            conditions.append('p.project_name = %s')
            params.append(filters['project'])
        if filters.get('site'):
            conditions.append('s.site_name = %s')
            params.append(filters['site'])
        if filters.get('status'):
            conditions.append('st.status_name = %s')
            params.append(filters['status'])
        if filters.get('date'):
            conditions.append('DATE(d.created_at) = %s')
            params.append(filters['date'])

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY d.created_at DESC'
    cursor.execute(query, params)
    documents = cursor.fetchall()
    conn.close()
    return documents

def get_all_issues(filters=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = '''
        SELECT i.id, i.title, i.description, p.project_name, s.site_name, st.status_name, st.id as status_id,
               u.username, i.deadline, i.created_at
        FROM issues i
        JOIN projects p ON i.project_id = p.id
        JOIN sites s ON i.site_id = s.id
        JOIN issue_statuses st ON i.status_id = st.id
        JOIN users u ON i.reported_by = u.id
    '''
    params = []
    conditions = []

    if filters:
        if filters.get('project'):
            conditions.append('p.project_name = %s')
            params.append(filters['project'])
        if filters.get('site'):
            conditions.append('s.site_name = %s')
            params.append(filters['site'])
        if filters.get('status'):
            conditions.append('st.status_name = %s')
            params.append(filters['status'])
        if filters.get('date'):
            conditions.append('DATE(i.created_at) = %s')
            params.append(filters['date'])

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY i.created_at DESC'
    cursor.execute(query, params)
    issues = cursor.fetchall()
    conn.close()
    return issues

def get_documents_for_issue(issue_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT ia.id, ia.filename
        FROM issue_attachments ia
        WHERE ia.issue_id = %s
    ''', (issue_id,))
    documents = cursor.fetchall()
    conn.close()
    return documents

def delete_document(document_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT file_path FROM documents WHERE id = %s', (document_id,))
    document = cursor.fetchone()
    if document:
        cursor.execute('DELETE FROM documents WHERE id = %s', (document_id,))
        cursor.execute('DELETE FROM issue_documents WHERE document_id = %s', (document_id,))
        conn.commit()
        conn.close()
        return document['file_path']
    conn.close()
    return None

def delete_issue_attachment(attachment_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT file_path FROM issue_attachments WHERE id = %s', (attachment_id,))
    attachment = cursor.fetchone()
    if attachment:
        cursor.execute('DELETE FROM issue_attachments WHERE id = %s', (attachment_id,))
        conn.commit()
        conn.close()
        return attachment['file_path']
    conn.close()
    return None

def delete_issue(issue_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM issues WHERE id = %s', (issue_id,))
    cursor.execute('DELETE FROM issue_documents WHERE issue_id = %s', (issue_id,))
    cursor.execute('DELETE FROM issue_attachments WHERE issue_id = %s', (issue_id,))
    conn.commit()
    conn.close()

def update_issue_status(issue_id, status_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE issues SET status_id = %s WHERE id = %s', (status_id, issue_id))
        conn.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        conn.close()
        return affected_rows > 0  # Returns True if the update was successful
    except Exception as e:
        print(f"Error updating issue status: {e}")
        return False

def get_dashboard_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM documents')
    total_docs = cursor.fetchone()[0]
    print(f"Total documents in database: {total_docs}")
    cursor.execute('''
        SELECT dt.type_name, COUNT(d.id) as count
        FROM documents d
        JOIN document_types dt ON d.document_type_id = dt.id
        GROUP BY dt.id, dt.type_name
    ''')
    documents_by_type = [{'type_name': row['type_name'], 'count': row['count']} for row in cursor.fetchall()]
    print(f"Documents by type: {documents_by_type}")
    cursor.execute('''
        SELECT p.project_name, COUNT(d.id) as count
        FROM documents d
        JOIN projects p ON d.project_id = p.id
        GROUP BY p.id, p.project_name
    ''')
    documents_by_project = [{'project_name': row['project_name'], 'count': row['count']} for row in cursor.fetchall()]
    print(f"Documents by project: {documents_by_project}")
    cursor.execute('''
        SELECT st.status_name, COUNT(d.id) as count
        FROM documents d
        JOIN statuses st ON d.status_id = st.id
        GROUP BY st.id, st.status_name
    ''')
    documents_by_status = [{'status_name': row['status_name'], 'count': row['count']} for row in cursor.fetchall()]
    print(f"Documents by status: {documents_by_status}")
    stats = {
        'total_documents': total_docs,
        'documents_by_type': documents_by_type,
        'documents_by_project': documents_by_project,
        'documents_by_status': documents_by_status
    }
    conn.close()
    return stats

def get_issue_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM issues')
    total_issues = cursor.fetchone()[0]
    print(f"Total issues in database: {total_issues}")
    current_date = datetime(2025, 5, 16, 14, 53)  # 05:53 PM +03, May 16, 2025
    cursor.execute('''
        SELECT i.id, i.title, p.project_name, s.site_name, i.deadline
        FROM issues i
        JOIN projects p ON i.project_id = p.id
        JOIN sites s ON i.site_id = s.id
        WHERE i.deadline IS NOT NULL
        ORDER BY i.deadline ASC
    ''')
    issues_with_deadlines = cursor.fetchall()
    print("Issues with deadlines:", [dict(issue) for issue in issues_with_deadlines])
    issues_with_deadlines_list = []
    for issue in issues_with_deadlines:
        issue_dict = dict(issue)
        if issue_dict['deadline']:
            deadline_date = issue_dict['deadline']  # Already a datetime.date object
            if deadline_date < current_date.date():
                issue_dict['status'] = 'Overdue'
            elif deadline_date == current_date.date():
                issue_dict['status'] = 'Due Today'
            else:
                issue_dict['status'] = 'Upcoming'
        issues_with_deadlines_list.append(issue_dict)
    cursor.execute('''
        SELECT st.status_name, COUNT(i.id) as count
        FROM issues i
        JOIN issue_statuses st ON i.status_id = st.id
        GROUP BY st.id, st.status_name
    ''')
    issues_by_status = [{'status_name': row['status_name'], 'count': row['count']} for row in cursor.fetchall()]
    print(f"Issues by status: {issues_by_status}")
    cursor.execute('''
        SELECT p.project_name, COUNT(i.id) as count
        FROM issues i
        JOIN projects p ON i.project_id = p.id
        GROUP BY p.id, p.project_name
    ''')
    issues_by_project = [{'project_name': row['project_name'], 'count': row['count']} for row in cursor.fetchall()]
    print(f"Issues by project: {issues_by_project}")
    cursor.execute('''
        SELECT deadline, COUNT(*) as count
        FROM issues
        WHERE deadline IS NOT NULL
        GROUP BY deadline
        ORDER BY deadline ASC
    ''')
    deadlines_count = [{'deadline': str(row['deadline']), 'count': row['count']} for row in cursor.fetchall()]
    print(f"Deadlines count: {deadlines_count}")
    stats = {
        'total_issues': total_issues,
        'issues_by_status': issues_by_status,
        'issues_by_project': issues_by_project,
        'issues_with_deadlines': issues_with_deadlines_list,
        'deadlines_count': deadlines_count
    }
    conn.close()
    return stats