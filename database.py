import sqlite3
from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect('documents.db')
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn

def get_document_types():
    conn = get_db_connection()
    types = conn.execute('SELECT * FROM document_types').fetchall()
    conn.close()
    return types

def get_projects():
    conn = get_db_connection()
    projects = conn.execute('SELECT * FROM projects').fetchall()
    conn.close()
    return projects

def get_sites():
    conn = get_db_connection()
    sites = conn.execute('SELECT * FROM sites').fetchall()
    conn.close()
    return sites

def get_statuses():
    conn = get_db_connection()
    statuses = conn.execute('SELECT * FROM statuses').fetchall()
    conn.close()
    return statuses

def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return users

def insert_document(file_name, file_path, document_type_id, project_id, site_id, status_id, uploaded_by):
    conn = get_db_connection()
    upload_date = datetime.now().strftime('%Y-%m-%d')
    conn.execute('''
        INSERT INTO documents (file_name, file_path, upload_date, document_type_id, project_id, site_id, status_id, uploaded_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (file_name, file_path, upload_date, document_type_id, project_id, site_id, status_id, uploaded_by))
    conn.commit()
    conn.close()

def get_all_documents(filters=None):
    conn = get_db_connection()
    query = '''
        SELECT d.id, d.file_name, d.file_path, dt.type_name, p.project_name, s.site_name, st.status_name, u.username
        FROM documents d
        JOIN document_types dt ON d.document_type_id = dt.id
        JOIN projects p ON d.project_id = p.id
        JOIN sites s ON d.site_id = s.id
        JOIN statuses st ON d.status_id = st.id
        JOIN users u ON d.uploaded_by = u.id
    '''
    params = []
    if filters:
        conditions = []
        if filters.get('document_type'):
            conditions.append('d.document_type_id = ?')
            params.append(filters['document_type'])
        if filters.get('project'):
            conditions.append('d.project_id = ?')
            params.append(filters['project'])
        if filters.get('site'):
            conditions.append('d.site_id = ?')
            params.append(filters['site'])
        if filters.get('status'):
            conditions.append('d.status_id = ?')
            params.append(filters['status'])
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
    
    documents = conn.execute(query, params).fetchall()
    conn.close()
    return documents

def delete_document(document_id):
    conn = get_db_connection()
    cursor = conn.execute('SELECT file_path FROM documents WHERE id = ?', (document_id,))
    result = cursor.fetchone()
    file_path = result['file_path'] if result else None
    conn.execute('DELETE FROM documents WHERE id = ?', (document_id,))
    conn.commit()
    conn.close()
    return file_path

def get_dashboard_stats():
    conn = get_db_connection()
    stats = {
        'total_documents': conn.execute('SELECT COUNT(*) FROM documents').fetchone()[0],
        'documents_by_type': conn.execute('''
            SELECT dt.type_name, COUNT(d.id) as count
            FROM documents d
            JOIN document_types dt ON d.document_type_id = dt.id
            GROUP BY dt.id, dt.type_name
        ''').fetchall(),
        'documents_by_project': conn.execute('''
            SELECT p.project_name, COUNT(d.id) as count
            FROM documents d
            JOIN projects p ON d.project_id = p.id
            GROUP BY p.id, p.project_name
        ''').fetchall(),
        'documents_by_status': conn.execute('''
            SELECT st.status_name, COUNT(d.id) as count
            FROM documents d
            JOIN statuses st ON d.status_id = st.id
            GROUP BY st.id, st.status_name
        ''').fetchall()
    }
    conn.close()
    return stats