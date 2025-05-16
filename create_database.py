import psycopg2
from psycopg2.extras import DictCursor

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="document_control",
    user="doc_user",
    password="asdfgh123!@#",
    host="localhost",
    port="5432",
    cursor_factory=DictCursor
)
cursor = conn.cursor()

# Drop old tables if they exist
cursor.execute('DROP TABLE IF EXISTS issue_documents')
cursor.execute('DROP TABLE IF EXISTS issue_attachments')
cursor.execute('DROP TABLE IF EXISTS issues')
cursor.execute('DROP TABLE IF EXISTS documents')
cursor.execute('DROP TABLE IF EXISTS issue_statuses')
cursor.execute('DROP TABLE IF EXISTS document_types')
cursor.execute('DROP TABLE IF EXISTS projects')
cursor.execute('DROP TABLE IF EXISTS sites')
cursor.execute('DROP TABLE IF EXISTS statuses')
cursor.execute('DROP TABLE IF EXISTS users')

# Create document_types table
cursor.execute('''
    CREATE TABLE document_types (
        id SERIAL PRIMARY KEY,
        type_name TEXT NOT NULL UNIQUE
    )
''')

# Create projects table
cursor.execute('''
    CREATE TABLE projects (
        id SERIAL PRIMARY KEY,
        project_name TEXT NOT NULL UNIQUE
    )
''')

# Create sites table
cursor.execute('''
    CREATE TABLE sites (
        id SERIAL PRIMARY KEY,
        site_name TEXT NOT NULL UNIQUE
    )
''')

# Create statuses table
cursor.execute('''
    CREATE TABLE statuses (
        id SERIAL PRIMARY KEY,
        status_name TEXT NOT NULL UNIQUE
    )
''')

# Create users table
cursor.execute('''
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username TEXT NOT NULL UNIQUE
    )
''')

# Create documents table with foreign keys
cursor.execute('''
    CREATE TABLE documents (
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
    CREATE TABLE issue_statuses (
        id SERIAL PRIMARY KEY,
        status_name TEXT NOT NULL UNIQUE
    )
''')

# Create issues table with deadline
cursor.execute('''
    CREATE TABLE issues (
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
    CREATE TABLE issue_documents (
        issue_id INTEGER,
        document_id INTEGER,
        FOREIGN KEY (issue_id) REFERENCES issues(id),
        FOREIGN KEY (document_id) REFERENCES documents(id),
        PRIMARY KEY (issue_id, document_id)
    )
''')

# Create issue_attachments table
cursor.execute('''
    CREATE TABLE issue_attachments (
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

# Insert sample data
# Document Types
cursor.executemany('INSERT INTO document_types (type_name) VALUES (%s) ON CONFLICT (type_name) DO NOTHING',
                   [('Blueprint',), ('Permit',), ('Contract',)])

# Projects
cursor.executemany('INSERT INTO projects (project_name) VALUES (%s) ON CONFLICT (project_name) DO NOTHING',
                   [('Downtown Tower',), ('River Bridge',)])

# Sites
cursor.executemany('INSERT INTO sites (site_name) VALUES (%s) ON CONFLICT (site_name) DO NOTHING',
                   [('Site A',), ('Site B',)])

# Statuses (for documents)
cursor.executemany('INSERT INTO statuses (status_name) VALUES (%s) ON CONFLICT (status_name) DO NOTHING',
                   [('Draft',), ('Approved',), ('Rejected',)])

# Issue Statuses
cursor.executemany('INSERT INTO issue_statuses (status_name) VALUES (%s) ON CONFLICT (status_name) DO NOTHING',
                   [('Open',), ('In Progress',), ('Closed',)])

# Users
cursor.executemany('INSERT INTO users (username) VALUES (%s) ON CONFLICT (username) DO NOTHING',
                   [('john_doe',), ('jane_smith',)])

# Commit changes
conn.commit()

# Verify data
print("Database Setup Complete. Sample Data:")
print("\nDocument Types:")
cursor.execute('SELECT * FROM document_types')
for row in cursor.fetchall():
    print(row)

print("\nProjects:")
cursor.execute('SELECT * FROM projects')
for row in cursor.fetchall():
    print(row)

print("\nSites:")
cursor.execute('SELECT * FROM sites')
for row in cursor.fetchall():
    print(row)

print("\nStatuses:")
cursor.execute('SELECT * FROM statuses')
for row in cursor.fetchall():
    print(row)

print("\nIssue Statuses:")
cursor.execute('SELECT * FROM issue_statuses')
for row in cursor.fetchall():
    print(row)

print("\nUsers:")
cursor.execute('SELECT * FROM users')
for row in cursor.fetchall():
    print(row)

print("\nDocuments:")
cursor.execute('''
    SELECT d.id, d.filename, dt.type_name, p.project_name, s.site_name, st.status_name, u.username, d.created_at
    FROM documents d
    JOIN document_types dt ON d.document_type_id = dt.id
    JOIN projects p ON d.project_id = p.id
    JOIN sites s ON d.site_id = s.id
    JOIN statuses st ON d.status_id = st.id
    JOIN users u ON d.uploaded_by = u.id
''')
for row in cursor.fetchall():
    print(row)

print("\nIssues:")
cursor.execute('''
    SELECT i.id, i.title, i.description, p.project_name, s.site_name, st.status_name, u.username, i.deadline, i.created_at
    FROM issues i
    JOIN projects p ON i.project_id = p.id
    JOIN sites s ON i.site_id = s.id
    JOIN issue_statuses st ON i.status_id = st.id
    JOIN users u ON i.reported_by = u.id
''')
for row in cursor.fetchall():
    print(row)

# Additional check for document count
cursor.execute('SELECT COUNT(*) FROM documents')
doc_count = cursor.fetchone()[0]
print(f"\nTotal documents in database after setup: {doc_count}")

# Close connection
conn.close()