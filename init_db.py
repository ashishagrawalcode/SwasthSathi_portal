import sqlite3
import os
from werkzeug.security import generate_password_hash

DATABASE = 'aroghub.db'
ROLES = {'patient': 1, 'doctor': 2, 'admin': 99}

# This script will delete the old database and create a new one with the correct structure.
if os.path.exists(DATABASE):
    os.remove(DATABASE)
    print(f"Removed old database file: {DATABASE}")

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

print("Creating new database and tables...")

# --- Create users Table (with profile photo column) ---
cursor.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role_id INTEGER NOT NULL,
    specialty TEXT, 
    hospital TEXT,
    phone_number TEXT,
    abha_id TEXT,
    profile_photo_filename TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')
print("- 'users' table created with profile photo column.")

# --- Create consultations Table ---
cursor.execute('''
CREATE TABLE consultations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER,
    patient_name TEXT NOT NULL,
    patient_age INTEGER,
    patient_gender TEXT,
    symptoms TEXT NOT NULL,
    photo_filename TEXT,
    audio_note_filename TEXT,
    doctor_response TEXT,
    category TEXT,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users (id),
    FOREIGN KEY (doctor_id) REFERENCES users (id)
);
''')
print("- 'consultations' table created.")

# --- Create chat_threads & chat_messages Tables ---
cursor.execute('''
CREATE TABLE chat_threads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users (id),
    FOREIGN KEY (doctor_id) REFERENCES users (id)
);
''')
cursor.execute('''
CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    message_text TEXT,
    file_path TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (thread_id) REFERENCES chat_threads (id),
    FOREIGN KEY (sender_id) REFERENCES users (id)
);
''')
print("- Chat tables created.")
print("Tables created successfully.")

# --- Insert Sample Data ---
print("\nSeeding database with demo data...")
demo_pass_hash = generate_password_hash('password')

users_to_add = [
    # (name, email, password_hash, role_id, phone_number, abha_id)
    ('Test Patient', 'patient@test.com', demo_pass_hash, ROLES['patient'], '9876543210', '11-2222-3333-4444'),
    ('Rina Devi', 'rina.devi@test.com', demo_pass_hash, ROLES['patient'], '9876543211', '11-2222-3333-5555'),
    ('Amit Kumar', 'amit.kumar@test.com', demo_pass_hash, ROLES['patient'], '9876543212', '11-2222-3333-6666'),
    ('Dr. Sharma', 'doctor@test.com', demo_pass_hash, ROLES['doctor'], '8765432109', None),
    ('Admin User', 'admin@test.com', demo_pass_hash, ROLES['admin'], '6543210987', None)
]
for user in users_to_add:
    name, email, phash, rid, phone, abha = user
    cursor.execute(
        'INSERT INTO users (name, email, password_hash, role_id, phone_number, abha_id) VALUES (?, ?, ?, ?, ?, ?)',
        (name, email, phash, rid, phone, abha)
    )
    print(f" - Added {name} ({email})")

conn.commit()
conn.close()

print("\nDatabase initialization complete!")
print("You can now run your main app: python app.py")