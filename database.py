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
    # New table for issue statuses
    conn.execute('''
        CREATE TABLE IF NOT EXISTS issue_statuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status_name TEXT NOT NULL UNIQUE
        )
    ''')
    # Updated issues table with deadline
    conn.execute('''
        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    # Junction table to link issues with documents (for Documents page)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS issue_documents (
            issue_id INTEGER,
            document_id INTEGER,
            FOREIGN KEY (issue_id) REFERENCES issues(id),
            FOREIGN KEY (document_id) REFERENCES documents(id),
            PRIMARY KEY (issue_id, document_id)
        )
    ''')
    # New table for issue attachments (separate from documents)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS issue_attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            issue_id INTEGER,
            uploaded_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (issue_id) REFERENCES issues(id),
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

def get_issue_statuses():
    conn = get_db_connection()
    statuses = conn.execute('SELECT * FROM issue_statuses').fetchall()
    conn.close()
    return statuses

def insert_document(filename, file_path, document_type_id, project_id, site_id, status_id, uploaded_by):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO documents (filename, file_path, document_type_id, project_id, site_id, status_id, uploaded_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (filename, file_path, document_type_id, project_id, site_id, status_id, uploaded_by))
    conn.commit()
    conn.close()

def insert_issue_attachment(filename, file_path, issue_id, uploaded_by):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO issue_attachments (filename, file_path, issue_id, uploaded_by)
        VALUES (?, ?, ?, ?)
    ''', (filename, file_path, issue_id, uploaded_by))
    conn.commit()
    conn.close()

def insert_issue(title, description, project_id, site_id, status_id, reported_by, deadline, attachment_ids=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO issues (title, description, project_id, site_id, status_id, reported_by, deadline)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (title, description, project_id, site_id, status_id, reported_by, deadline))
    issue_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return issue_id

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

def get_all_issues(filters=None):
    conn = get_db_connection()
    query = '''
        SELECT i.id, i.title, i.description, p.project_name, s.site_name, st.status_name, u.username, i.deadline, i.created_at
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
            conditions.append('p.project_name = ?')
            params.append(filters['project'])
        if filters.get('site'):
            conditions.append('s.site_name = ?')
            params.append(filters['site'])
        if filters.get('status'):
            conditions.append('st.status_name = ?')
            params.append(filters['status'])
        if filters.get('date'):
            conditions.append('DATE(i.created_at) = ?')
            params.append(filters['date'])

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY i.created_at DESC'
    issues = conn.execute(query, params).fetchall()
    conn.close()
    return issues

def get_documents_for_issue(issue_id):
    conn = get_db_connection()
    documents = conn.execute('''
        SELECT ia.id, ia.filename
        FROM issue_attachments ia
        WHERE ia.issue_id = ?
    ''', (issue_id,)).fetchall()
    conn.close()
    return documents

def delete_document(document_id):
    conn = get_db_connection()
    document = conn.execute('SELECT file_path FROM documents WHERE id = ?', (document_id,)).fetchone()
    if document:
        conn.execute('DELETE FROM documents WHERE id = ?', (document_id,))
        conn.execute('DELETE FROM issue_documents WHERE document_id = ?', (document_id,))  # Clean up links
        conn.commit()
        conn.close()
        return document['file_path']
    conn.close()
    return None

def delete_issue_attachment(attachment_id):
    conn = get_db_connection()
    attachment = conn.execute('SELECT file_path FROM issue_attachments WHERE id = ?', (attachment_id,)).fetchone()
    if attachment:
        conn.execute('DELETE FROM issue_attachments WHERE id = ?', (attachment_id,))
        conn.commit()
        conn.close()
        return attachment['file_path']
    conn.close()
    return None

def delete_issue(issue_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM issues WHERE id = ?', (issue_id,))
    conn.execute('DELETE FROM issue_documents WHERE issue_id = ?', (issue_id,))  # Clean up links
    conn.execute('DELETE FROM issue_attachments WHERE issue_id = ?', (issue_id,))  # Clean up attachments
    conn.commit()
    conn.close()

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

def get_issue_stats():
    conn = get_db_connection()
    total_issues = conn.execute('SELECT COUNT(*) FROM issues').fetchone()[0]
    current_date = datetime(2025, 5, 15, 20, 58)  # 08:58 PM +03, May 15, 2025
    issues_with_deadlines = conn.execute('''
        SELECT i.title, p.project_name, s.site_name, i.deadline
        FROM issues i
        JOIN projects p ON i.project_id = p.id
        JOIN sites s ON i.site_id = s.id
        WHERE i.deadline IS NOT NULL
        ORDER BY i.deadline ASC
    ''').fetchall()
    # Add status to each issue by converting sqlite3.Row to dict
    for issue in issues_with_deadlines:
        issue_dict = dict(issue)
        if issue_dict['deadline']:
            deadline_date = datetime.strptime(issue_dict['deadline'], '%Y-%m-%d')
            if deadline_date.date() < current_date.date():
                issue_dict['status'] = 'Overdue'
            elif deadline_date.date() == current_date.date():
                issue_dict['status'] = 'Due Today'
            else:
                issue_dict['status'] = 'Upcoming'
        issues_with_deadlines[issues_with_deadlines.index(issue)] = issue_dict
    stats = {
        'total_issues': total_issues,
        'issues_by_status': conn.execute('''
            SELECT st.status_name, COUNT(i.id) as count
            FROM issues i
            JOIN issue_statuses st ON i.status_id = st.id
            GROUP BY st.id, st.status_name
        ''').fetchall(),
        'issues_by_project': conn.execute('''
            SELECT p.project_name, COUNT(i.id) as count
            FROM issues i
            JOIN projects p ON i.project_id = p.id
            GROUP BY p.id, p.project_name
        ''').fetchall(),
        'issues_with_deadlines': issues_with_deadlines,
        'deadlines_count': conn.execute('''
            SELECT deadline, COUNT(*) as count
            FROM issues
            WHERE deadline IS NOT NULL
            GROUP BY deadline
            ORDER BY deadline ASC
        ''').fetchall()
    }
    conn.close()
    return stats