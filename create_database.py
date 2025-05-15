import sqlite3

# Connect to SQLite database with absolute path
conn = sqlite3.connect(r'c:\Users\alshi\OneDrive\Desktop\Document_control\documents.db')
cursor = conn.cursor()

# Drop the old tables if they exist
cursor.execute('DROP TABLE IF EXISTS documents')
cursor.execute('DROP TABLE IF EXISTS issue_documents')
cursor.execute('DROP TABLE IF EXISTS issues')
cursor.execute('DROP TABLE IF EXISTS issue_statuses')
cursor.execute('DROP TABLE IF EXISTS document_types')
cursor.execute('DROP TABLE IF EXISTS projects')
cursor.execute('DROP TABLE IF EXISTS sites')
cursor.execute('DROP TABLE IF EXISTS statuses')
cursor.execute('DROP TABLE IF EXISTS users')

# Create document_types table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS document_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type_name TEXT NOT NULL UNIQUE
    )
''')

# Create projects table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT NOT NULL UNIQUE
    )
''')

# Create sites table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site_name TEXT NOT NULL UNIQUE
    )
''')

# Create statuses table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS statuses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        status_name TEXT NOT NULL UNIQUE
    )
''')

# Create users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE
    )
''')

# Create documents table with foreign keys
cursor.execute('''
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

# Create issue_statuses table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS issue_statuses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        status_name TEXT NOT NULL UNIQUE
    )
''')

# Create issues table with deadline
cursor.execute('''
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

# Insert sample data
# Document Types
cursor.executemany('INSERT OR IGNORE INTO document_types (type_name) VALUES (?)',
                   [('Blueprint',), ('Permit',), ('Contract',)])

# Projects
cursor.executemany('INSERT OR IGNORE INTO projects (project_name) VALUES (?)',
                   [('Downtown Tower',), ('River Bridge',)])

# Sites
cursor.executemany('INSERT OR IGNORE INTO sites (site_name) VALUES (?)',
                   [('Site A',), ('Site B',)])

# Statuses (for documents)
cursor.executemany('INSERT OR IGNORE INTO statuses (status_name) VALUES (?)',
                   [('Draft',), ('Approved',), ('Rejected',)])

# Issue Statuses
cursor.executemany('INSERT OR IGNORE INTO issue_statuses (status_name) VALUES (?)',
                   [('Open',), ('In Progress',), ('Closed',)])

# Users
cursor.executemany('INSERT OR IGNORE INTO users (username) VALUES (?)',
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