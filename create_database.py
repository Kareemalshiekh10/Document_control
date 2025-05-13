import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('documents.db')
cursor = conn.cursor()

# Drop the old documents table if it exists
cursor.execute('DROP TABLE IF EXISTS documents')

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
        project_name TEXT NOT NULL UNIQUE,
        start_date TEXT
    )
''')

# Create sites table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site_name TEXT NOT NULL UNIQUE,
        location TEXT
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
        username TEXT NOT NULL UNIQUE,
        role TEXT NOT NULL
    )
''')

# Create documents table with foreign keys
cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        upload_date TEXT NOT NULL,
        document_type_id INTEGER NOT NULL,
        project_id INTEGER NOT NULL,
        site_id INTEGER NOT NULL,
        status_id INTEGER NOT NULL,
        uploaded_by INTEGER NOT NULL,
        FOREIGN KEY (document_type_id) REFERENCES document_types(id),
        FOREIGN KEY (project_id) REFERENCES projects(id),
        FOREIGN KEY (site_id) REFERENCES sites(id),
        FOREIGN KEY (status_id) REFERENCES statuses(id),
        FOREIGN KEY (uploaded_by) REFERENCES users(id)
    )
''')

# Insert sample data
# Document Types
cursor.executemany('INSERT OR IGNORE INTO document_types (type_name) VALUES (?)',
                   [('Blueprint',), ('Permit',), ('Contract',)])

# Projects
cursor.executemany('INSERT OR IGNORE INTO projects (project_name, start_date) VALUES (?, ?)',
                   [('Downtown Tower', '2025-01-01'), ('River Bridge', '2025-03-15')])

# Sites
cursor.executemany('INSERT OR IGNORE INTO sites (site_name, location) VALUES (?, ?)',
                   [('Site A', '123 Main St'), ('Site B', '456 River Rd')])

# Statuses
cursor.executemany('INSERT OR IGNORE INTO statuses (status_name) VALUES (?)',
                   [('Draft',), ('Approved',), ('Rejected',)])

# Users
cursor.executemany('INSERT OR IGNORE INTO users (username, role) VALUES (?, ?)',
                   [('john_doe', 'Manager'), ('jane_smith', 'Worker')])

# Documents (sample document)
cursor.execute('''
    INSERT INTO documents (file_name, file_path, upload_date, document_type_id, project_id, site_id, status_id, uploaded_by)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', ('site_plan.pdf', 'uploads/site_plan.pdf', '2025-05-14',
      1, 1, 1, 1, 1))  # Blueprint, Downtown Tower, Site A, Draft, john_doe

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

print("\nUsers:")
cursor.execute('SELECT * FROM users')
for row in cursor.fetchall():
    print(row)

print("\nDocuments:")
cursor.execute('''
    SELECT d.id, d.file_name, dt.type_name, p.project_name, s.site_name, st.status_name, u.username
    FROM documents d
    JOIN document_types dt ON d.document_type_id = dt.id
    JOIN projects p ON d.project_id = p.id
    JOIN sites s ON d.site_id = s.id
    JOIN statuses st ON d.status_id = st.id
    JOIN users u ON d.uploaded_by = u.id
''')
for row in cursor.fetchall():
    print(row)

# Close connection
conn.close()