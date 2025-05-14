import sqlite3
import os
from datetime import datetime

DATABASE = r'c:\Users\alshi\OneDrive\Desktop\Document_control\documents.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS document_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_name TEXT NOT NULL UNIQUE
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL UNIQUE
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_name TEXT NOT NULL UNIQUE
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS statuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status_name TEXT NOT NULL UNIQUE
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    conn.commit()
    conn.close()

def get_document_types():
    conn = get_db_connection()
    document_types = conn.execute('SELECT * FROM document_types').fetchall()
    conn.close()
    return document_types

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

def insert_document(filename, file_path, document_type_id, project_id, site_id, status_id, uploaded_by):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO documents (filename, file_path, document_type_id, project_id, site_id, status_id, uploaded_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (filename, file_path, document_type_id, project_id, site_id, status_id, uploaded_by))
    conn.commit()
    conn.close()

def get_all_documents(filters=None):
    conn = get_db_connection()
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
            conditions.append('dt.type_name = ?')
            params.append(filters['document_type'])
        if filters.get('project'):
            conditions.append('p.project_name = ?')
            params.append(filters['project'])
        if filters.get('site'):
            conditions.append('s.site_name = ?')
            params.append(filters['site'])
        if filters.get('status'):
            conditions.append('st.status_name = ?')
            params.append(filters['status'])
        if filters.get('date'):
            conditions.append('DATE(d.created_at) = ?')
            params.append(filters['date'])

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY d.created_at DESC'
    documents = conn.execute(query, params).fetchall()
    conn.close()
    return documents

def delete_document(document_id):
    conn = get_db_connection()
    document = conn.execute('SELECT file_path FROM documents WHERE id = ?', (document_id,)).fetchone()
    if document:
        conn.execute('DELETE FROM documents WHERE id = ?', (document_id,))
        conn.commit()
        conn.close()
        return document['file_path']
    conn.close()
    return None

def get_dashboard_stats():
    conn = get_db_connection()
    total_docs = conn.execute('SELECT COUNT(*) FROM documents').fetchone()[0]
    print(f"Total documents in database: {total_docs}")  # Debug log
    stats = {
        'total_documents': total_docs,
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