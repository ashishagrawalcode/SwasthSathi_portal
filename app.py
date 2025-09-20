from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import sqlite3
import os
import time
import requests

# --- App Configuration ---
app = Flask(__name__)
app.secret_key = 'super_secret_key_for_aroghub'
DATABASE = 'swasthsathi.db'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Database, Roles, and Login Decorator ---
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Roles definition
ROLES = {'patient': 1, 'doctor': 2, 'asha': 3, 'admin': 99}
# Create a reverse mapping to get role name from role ID
ROLE_NAMES = {v: k for k, v in ROLES.items()}

def login_required(role_ids):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'danger')
                return redirect(url_for('login'))
            if session.get('user_role') not in role_ids:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- Database Initialization ---
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    print("Initializing database...")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            role_id INTEGER NOT NULL,
            specialty TEXT,
            hospital TEXT,
            age INTEGER,
            gender TEXT,
            phone_number TEXT,
            abha_id TEXT,
            profile_photo_filename TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("- 'users' table checked/created.")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS consultations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            doctor_id INTEGER,
            patient_name TEXT,
            patient_age INTEGER,
            patient_gender TEXT,
            symptoms TEXT,
            photo_filename TEXT,
            doctor_response TEXT,
            audio_note_filename TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES users(id),
            FOREIGN KEY (doctor_id) REFERENCES users(id)
        )
    ''')
    print("- 'consultations' table checked/created.")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_threads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            doctor_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES users(id),
            FOREIGN KEY (doctor_id) REFERENCES users(id)
        )
    ''')
    print("- 'chat_threads' table checked/created.")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id INTEGER,
            sender_id INTEGER,
            message_text TEXT,
            file_path TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (thread_id) REFERENCES chat_threads(id),
            FOREIGN KEY (sender_id) REFERENCES users(id)
        )
    ''')
    print("- 'chat_messages' table checked/created.")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS households (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asha_id INTEGER,
            household_name TEXT NOT NULL,
            address TEXT,
            members_count INTEGER,
            is_verified BOOLEAN DEFAULT 0,
            FOREIGN KEY (asha_id) REFERENCES users(id)
        )
    ''')
    print("- 'households' table checked/created.")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mch_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asha_id INTEGER,
            patient_id INTEGER,
            record_type TEXT, -- e.g., 'pregnancy', 'immunization', 'growth'
            record_details TEXT,
            record_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (asha_id) REFERENCES users(id),
            FOREIGN KEY (patient_id) REFERENCES users(id)
        )
    ''')
    print("- 'mch_records' table checked/created.")
    
    conn.commit()
    conn.close()
    print("Database initialization complete.")

def seed_db():
    conn = get_db()
    cursor = conn.cursor()
    
    user_count = cursor.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    if user_count > 0:
        print("Database already contains users. Skipping seeding.")
        conn.close()
        return

    print("\nSeeding database with demo data...")
    demo_pass_hash = generate_password_hash('password')
    
    users_to_add = [
        ('Test Patient', 'patient@test.com', None, demo_pass_hash, ROLES['patient'], '9876543210', '11-2222-3333-4444'),
        ('Rina Devi', 'rina.devi@test.com', None, demo_pass_hash, ROLES['patient'], '9876543211', '11-2222-3333-5555'),
        ('Amit Kumar', 'amit.kumar@test.com', None, demo_pass_hash, ROLES['patient'], '9876543212', '11-2222-3333-6666'),
        ('Rekha Kumari', 'rekha.kumari@asha.com', 'rekha_kumari', demo_pass_hash, ROLES['asha'], '9988776655', None),
        ('Bhavya Devi', 'bhavya.devi@asha.com', 'bhavya_devi', demo_pass_hash, ROLES['asha'], '9988776655', None),
        ('Dr. Sharma', 'sharma@doctor.com', None, demo_pass_hash, ROLES['doctor'], '8765432109', None),
        ('Admin User', 'admin@gov.com', None, demo_pass_hash, ROLES['admin'], '6543210987', None)
    ]
    for user in users_to_add:
        name, email, username, phash, rid, phone, abha = user
        cursor.execute(
            'INSERT INTO users (name, email, username, password_hash, role_id, phone_number, abha_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (name, email, username, phash, rid, phone, abha)
        )
        print(f" - Added {name} ({email})")
    conn.commit()

    asha_users = conn.execute("SELECT id FROM users WHERE role_id = ?", (ROLES['asha'],)).fetchall()
    if asha_users:
        for asha_user in asha_users:
            asha_id = asha_user['id']
            households_to_add = [
                (asha_id, f'Verma Household ({asha_user["id"]})', 'Ward 10, Kapriwas', 5),
                (asha_id, f'Singh Household ({asha_user["id"]})', 'Ward 11, Kapriwas', 3)
            ]
            for hh in households_to_add:
                cursor.execute(
                    'INSERT INTO households (asha_id, household_name, address, members_count) VALUES (?, ?, ?, ?)',
                    hh
                )
            print(" - Added demo households.")
            conn.commit()

            patient_id_for_asha = conn.execute("SELECT id FROM users WHERE email = 'rina.devi@test.com'").fetchone()['id']
            mch_records_to_add = [
                (asha_id, patient_id_for_asha, 'pregnancy', 'ANC visit 1 completed. Due date: 2026-06-01'),
                (asha_id, patient_id_for_asha, 'growth', 'Child weight: 12.5 kg')
            ]
            for record in mch_records_to_add:
                cursor.execute(
                    'INSERT INTO mch_records (asha_id, patient_id, record_type, record_details) VALUES (?, ?, ?, ?)',
                    record
                )
            print(" - Added demo MCH records.")
            conn.commit()
    
    conn.close()
    print("\nDatabase seeding complete.")

# --- General & Auth Routes ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/contact')
def contact_us():
    return render_template('contact_us.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        if session['user_role'] == ROLES['patient']: return redirect(url_for('patient_dashboard'))
        elif session['user_role'] == ROLES['doctor']: return redirect(url_for('doctor_dashboard'))
        elif session['user_role'] == ROLES['asha']: return redirect(url_for('asha_dashboard'))
        elif session['user_role'] == ROLES['admin']: return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        login_input = request.form['email']
        password = request.form['password']
        db = get_db()
        
        if '@' in login_input:
            user = db.execute('SELECT * FROM users WHERE email = ?', (login_input,)).fetchone()
        else:
            user = db.execute('SELECT * FROM users WHERE username = ?', (login_input,)).fetchone()
            
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role_id']
            flash('Logged in successfully!', 'success')
            if user['role_id'] == ROLES['patient']: return redirect(url_for('patient_dashboard'))
            elif user['role_id'] == ROLES['doctor']: return redirect(url_for('doctor_dashboard'))
            elif user['role_id'] == ROLES['asha']: return redirect(url_for('asha_dashboard'))
            elif user['role_id'] == ROLES['admin']: return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role_id = request.form.get('role_id')
        username = request.form.get('username')

        if not name or not email or not password or not role_id:
            flash('All required fields must be filled.', 'danger')
            return redirect(url_for('register'))

        password_hash = generate_password_hash(password)
        db = get_db()
        try:
            db.execute('INSERT INTO users (name, email, username, password_hash, role_id) VALUES (?, ?, ?, ?, ?)',
                       (name, email, username, password_hash, role_id))
            db.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Error: That email or username is already registered.', 'danger')
            return redirect(url_for('register'))
            
    roles_for_reg = {k: v for k, v in ROLES.items() if k != 'admin'}
    return render_template('register.html', roles=roles_for_reg)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# --- About Pages ---
@app.route('/about/patient')
@login_required(role_ids=[ROLES['patient']])
def about_patient(): return render_template('about_patient.html')

@app.route('/about/doctor')
@login_required(role_ids=[ROLES['doctor']])
def about_doctor(): return render_template('about_doctor.html')

@app.route('/about/asha')
@login_required(role_ids=[ROLES['asha']])
def about_asha(): return render_template('about_asha.html')


# --- Patient Feature Routes ---
@app.route('/dashboard/patient')
@login_required(role_ids=[ROLES['patient']])
def patient_dashboard():
    db = get_db()
    consultations = db.execute(
        'SELECT c.*, d.name as doctor_name FROM consultations c LEFT JOIN users d ON c.doctor_id = d.id WHERE c.patient_id = ? ORDER BY c.created_at DESC',
        (session['user_id'],)
    ).fetchall()
    return render_template('patient_dashboard.html', consultations=consultations)

@app.route('/find-doctor')
@login_required(role_ids=[ROLES['patient']])
def find_doctor():
    db = get_db()
    doctors = db.execute('SELECT id, name, specialty, hospital FROM users WHERE role_id = ?', (ROLES['doctor'],)).fetchall()
    # The patient_id is retrieved from the session in the start_chat route
    return render_template('find_doctor.html', doctors=doctors)

@app.route('/submit-symptoms', methods=['POST'])
@login_required(role_ids=[ROLES['patient']])
def submit_symptoms():
    name = request.form.get('name')
    age = request.form.get('age')
    gender = request.form.get('gender')
    symptoms = request.form.get('symptoms')
    photo = request.files.get('photo')
    photo_filename = None
    if photo and photo.filename != '':
        filename = secure_filename(photo.filename)
        timestamp = int(time.time())
        photo_filename = f"{timestamp}_{filename}"
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
    db = get_db()
    db.execute(
        'INSERT INTO consultations (patient_id, patient_name, patient_age, patient_gender, symptoms, photo_filename, status) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (session['user_id'], name, age, gender, symptoms, photo_filename, 'Pending')
    )
    db.commit()
    flash('Your case has been submitted. A doctor will review it shortly.', 'success')
    return redirect(url_for('patient_dashboard'))

@app.route('/lab-reports')
@login_required(role_ids=[ROLES['patient']])
def lab_report_assessment(): return render_template('lab_report_assessment.html')

@app.route('/health-awareness')
@login_required(role_ids=[ROLES['patient']])
def health_awareness(): return render_template('health_awareness.html')

@app.route('/search-medicines')
@login_required(role_ids=[ROLES['patient']])
def search_medicines(): return render_template('search_medicines.html')

@app.route('/patient-history')
@login_required(role_ids=[ROLES['patient']])
def patient_history():
    db = get_db()
    patient_id = session['user_id']
    consultations = db.execute(
        'SELECT c.*, d.name as doctor_name FROM consultations c LEFT JOIN users d ON c.doctor_id = d.id WHERE c.patient_id = ? ORDER BY c.created_at DESC',
        (patient_id,)
    ).fetchall()
    
    return render_template('patient_history.html', consultations=consultations, lab_reports=[])

@app.route('/government-schemes')
@login_required(role_ids=[ROLES['patient']])
def government_schemes(): return render_template('government_schemes.html')

@app.route('/chatbot')
@login_required(role_ids=[ROLES['patient'], ROLES['doctor'], ROLES['asha']])
def chatbot(): return render_template('chatbot.html')

@app.route('/symptom-checker')
@login_required(role_ids=[ROLES['patient']])
def symptom_checker(): return render_template('symptom_checker.html')

# --- CHAT WORKFLOW ROUTES ---
@app.route('/chat/start/<int:doctor_id>')
@login_required(role_ids=[ROLES['patient']])
def start_chat(doctor_id):
    patient_id = session.get('user_id')
    db = get_db()
    thread = db.execute(
        'SELECT * FROM chat_threads WHERE patient_id = ? AND doctor_id = ?',
        (patient_id, doctor_id)
    ).fetchone()
    
    if not thread:
        cursor = db.execute('INSERT INTO chat_threads (patient_id, doctor_id) VALUES (?, ?)', (patient_id, doctor_id))
        db.commit()
        thread_id = cursor.lastrowid
    else:
        thread_id = thread['id']
    return redirect(url_for('chat_page', thread_id=thread_id))

@app.route('/chat/view/<int:thread_id>')
@login_required(role_ids=[ROLES['patient'], ROLES['doctor'], ROLES['asha']])
def chat_page(thread_id):
    db = get_db()
    thread = db.execute('SELECT * FROM chat_threads WHERE id = ?', (thread_id,)).fetchone()
    
    if not thread or session['user_id'] not in [thread['patient_id'], thread['doctor_id']]:
        flash('You do not have access to this chat.', 'danger')
        return redirect(url_for('home'))

    current_user_role_id = session.get('user_role')
    other_user_id = thread['doctor_id'] if current_user_role_id == ROLES['patient'] else thread['patient_id']
    other_user = db.execute('SELECT name, id FROM users WHERE id = ?', (other_user_id,)).fetchone()

    user_role_name = ROLE_NAMES.get(current_user_role_id, 'unknown')

    return render_template('chat.html', 
        thread=thread, 
        other_user=other_user, 
        user_role=user_role_name
    )

@app.route('/chat/<int:thread_id>/messages')
@login_required(role_ids=[ROLES['patient'], ROLES['doctor'], ROLES['asha']])
def get_messages(thread_id):
    db = get_db()
    messages = db.execute(
        'SELECT * FROM chat_messages WHERE thread_id = ? ORDER BY sent_at ASC',
        (thread_id,)
    ).fetchall()
    message_list = [dict(row) for row in messages]
    return jsonify(message_list)

@app.route('/chat/<int:thread_id>/send', methods=['POST'])
@login_required(role_ids=[ROLES['patient'], ROLES['doctor'], ROLES['asha']])
def send_message(thread_id):
    message_text = request.form.get('message_text')
    file = request.files.get('file')
    file_path = None

    if file and file.filename != '':
        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join('uploads', unique_filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))

    if not message_text and not file_path:
        return jsonify({'status': 'error', 'message': 'Cannot send an empty message.'}), 400

    db = get_db()
    db.execute(
        'INSERT INTO chat_messages (thread_id, sender_id, message_text, file_path) VALUES (?, ?, ?, ?)',
        (thread_id, session['user_id'], message_text, file_path)
    )
    db.commit()
    return jsonify({'status': 'success'})

# --- Doctor Feature Routes ---
@app.route('/doctor/available-patients')
@login_required(role_ids=[ROLES['doctor']])
def available_patients():
    db = get_db()
    pending_cases = db.execute("SELECT * FROM consultations WHERE status = 'Pending' ORDER BY created_at ASC").fetchall()
    return render_template('available_patients.html', cases=pending_cases)

@app.route('/dashboard/doctor')
@login_required(role_ids=[ROLES['doctor']])
def doctor_dashboard():
    db = get_db()
    doctor_id = session['user_id']
    assigned_cases = db.execute("SELECT * FROM consultations c WHERE c.doctor_id = ? AND c.status = 'Under Review' ORDER BY c.created_at ASC", (doctor_id,)).fetchall()
    return render_template('doctor_dashboard.html', cases=assigned_cases)

@app.route('/doctor/chats')
@login_required(role_ids=[ROLES['doctor']])
def doctor_chats():
    db = get_db()
    doctor_id = session['user_id']
    threads = db.execute(
        '''
        SELECT ct.id, u.name as patient_name
        FROM chat_threads ct
        JOIN users u ON ct.patient_id = u.id
        WHERE ct.doctor_id = ?
        ''',
        (doctor_id,)
    ).fetchall()
    return render_template('doctor_chats.html', threads=threads)

@app.route('/doctor/accept-case/<int:case_id>', methods=['POST'])
@login_required(role_ids=[ROLES['doctor']])
def accept_case(case_id):
    db = get_db()
    case = db.execute("SELECT * FROM consultations WHERE id = ? AND status = 'Pending'", (case_id,)).fetchone()
    if case:
        db.execute("UPDATE consultations SET doctor_id = ?, status = 'Under Review' WHERE id = ?", (session['user_id'], case_id))
        db.commit()
        flash(f'Case #{case_id} has been assigned to you. It is now in your "My Schedule".', 'success')
        return redirect(url_for('doctor_dashboard'))
    else:
        flash('This case has already been accepted by another doctor.', 'warning')
        return redirect(url_for('available_patients'))

@app.route('/doctor/consultation/<int:case_id>')
@login_required(role_ids=[ROLES['doctor']])
def view_consultation(case_id):
    db = get_db()
    case = db.execute("SELECT * FROM consultations WHERE id = ?", (case_id,)).fetchone()
    if not case or case['doctor_id'] != session['user_id']:
        flash('Consultation case not found or not assigned to you.', 'danger')
        return redirect(url_for('doctor_dashboard'))
    
    return render_template('view_consultation.html', case=case)

@app.route('/doctor/respond/<int:case_id>', methods=['POST'])
@login_required(role_ids=[ROLES['doctor']])
def submit_response(case_id):
    response_text = request.form.get('response')
    audio_note = request.files.get('audio_note')
    audio_filename = None
    if audio_note and audio_note.filename != '':
        filename = secure_filename(audio_note.filename)
        timestamp = int(time.time())
        audio_filename = f"{timestamp}_{filename}"
        audio_note.save(os.path.join(app.config['UPLOAD_FOLDER'], audio_filename))
    db = get_db()
    db.execute("UPDATE consultations SET doctor_response = ?, audio_note_filename = ?, status = 'Reviewed' WHERE id = ?",
              (response_text, audio_filename, case_id))
    db.commit()
    flash('Your response has been sent to the patient.', 'success')
    return redirect(url_for('doctor_dashboard'))

@app.route('/doctor/patient-history')
@login_required(role_ids=[ROLES['doctor']])
def view_patient_history():
    db = get_db()
    reviewed_cases = db.execute(
        "SELECT c.*, p.name as patient_name FROM consultations c JOIN users p ON c.patient_id = p.id WHERE c.status = 'Reviewed' AND c.doctor_id = ? ORDER BY c.created_at DESC",
        (session['user_id'],)
    ).fetchall()
    return render_template('view_patient_history.html', cases=reviewed_cases)

# --- ASHA Feature Routes ---
@app.route('/asha/dashboard')
@login_required(role_ids=[ROLES['asha']])
def asha_dashboard():
    db = get_db()
    asha_id = session['user_id']
    households = db.execute('SELECT * FROM households WHERE asha_id = ?', (asha_id,)).fetchall()
    
    mch_summary = {'total_pregnancies': 2, 'immunization_due': 1}
    return render_template('asha_dashboard.html', households=households, mch_summary=mch_summary)

@app.route('/asha/households')
@login_required(role_ids=[ROLES['asha']])
def asha_household_list():
    db = get_db()
    asha_id = session['user_id']
    households = db.execute('SELECT * FROM households WHERE asha_id = ?', (asha_id,)).fetchall()
    return render_template('asha_household_list.html', households=households)
    
@app.route('/search', methods=['GET'])
@login_required(role_ids=[ROLES['asha']])
def search_households():
    query = request.args.get('query', '')
    db = get_db()
    asha_id = session['user_id']
    
    all_households = db.execute(
        "SELECT * FROM households WHERE asha_id = ? AND (household_name LIKE ? OR id LIKE ?)",
        (asha_id, f'%{query}%', f'%{query}%')
    ).fetchall()
    
    return render_template('asha_household_list.html', households=all_households)

@app.route('/add_new_household', methods=['GET', 'POST'])
@login_required(role_ids=[ROLES['asha']])
def add_new_household():
    if request.method == 'POST':
        household_name = request.form['household_name']
        address = request.form['address']
        members_count = request.form['members_count']
        db = get_db()
        db.execute(
            "INSERT INTO households (asha_id, household_name, address, members_count) VALUES (?, ?, ?, ?)",
            (session['user_id'], household_name, address, members_count)
        )
        db.commit()
        flash('New household added successfully!', 'success')
        return redirect(url_for('asha_household_list'))
        
    return render_template('add_household_form.html')

@app.route('/household/<int:household_id>')
@login_required(role_ids=[ROLES['asha']])
def household_details(household_id):
    db = get_db()
    household = db.execute('SELECT * FROM households WHERE id = ? AND asha_id = ?', (household_id, session['user_id'])).fetchone()
    
    if not household:
        flash('Household not found or you do not have permission to view it.', 'danger')
        return redirect(url_for('asha_household_list'))
    
    return render_template('household_details.html', household=household)

@app.route('/edit_household/<int:household_id>', methods=['GET', 'POST'])
@login_required(role_ids=[ROLES['asha']])
def edit_household(household_id):
    db = get_db()
    household = db.execute('SELECT * FROM households WHERE id = ? AND asha_id = ?', (household_id, session['user_id'])).fetchone()
    
    if not household:
        flash('Household not found or you do not have permission to edit it.', 'danger')
        return redirect(url_for('asha_household_list'))

    if request.method == 'POST':
        household_name = request.form['household_name']
        address = request.form['address']
        members_count = request.form['members_count']
        
        db.execute(
            "UPDATE households SET household_name = ?, address = ?, members_count = ? WHERE id = ?",
            (household_name, address, members_count, household_id)
        )
        db.commit()
        flash('Household updated successfully!', 'success')
        return redirect(url_for('household_details', household_id=household_id))
    
    return render_template('edit_household.html', household=household)


@app.route('/asha/mch')
@login_required(role_ids=[ROLES['asha']])
def asha_mch(): return render_template('asha_mch.html')

@app.route('/asha/mch/pregnancy')
@login_required(role_ids=[ROLES['asha']])
def asha_pregnancy_tracking():
    pregnancies_data = [
        {'patient_name': 'Priya Singh', 'edd': '2026-03-15', 'anc_visits_completed': 1, 'status': 'Active', 'status_class': 'info'},
        {'patient_name': 'Seema Patel', 'edd': '2025-11-20', 'anc_visits_completed': 3, 'status': 'High Risk', 'status_class': 'danger'}
    ]
    return render_template('asha_pregnancy_tracking.html', pregnancies=pregnancies_data)

@app.route('/asha/mch/immunization')
@login_required(role_ids=[ROLES['asha']])
def asha_immunization():
    children_data = [
        {'name': 'Rohan Kumar', 'dob': '2022-04-10', 'next_vaccine': 'DPT-1', 'next_vaccine_date': '2025-10-10'},
        {'name': 'Ananya Sharma', 'dob': '2024-01-25', 'next_vaccine': 'OPV-3', 'next_vaccine_date': '2025-11-05'}
    ]
    return render_template('asha_immunization.html', children=children_data)

@app.route('/asha/reporting')
@login_required(role_ids=[ROLES['asha']])
def asha_reporting(): return render_template('asha_reporting.html')

@app.route('/asha/submit_birth_form')
@login_required(role_ids=[ROLES['asha']])
def asha_submit_birth_form(): return render_template('asha_birth_form.html')

@app.route('/asha/submit_death_form')
@login_required(role_ids=[ROLES['asha']])
def asha_submit_death_form(): return render_template('asha_death_form.html')

@app.route('/asha/submit_disease_form')
@login_required(role_ids=[ROLES['asha']])
def asha_submit_disease_form(): return render_template('asha_disease_form.html')

@app.route('/asha/incentives')
@login_required(role_ids=[ROLES['asha']])
def asha_incentives():
    total_incentives = 5500
    pending_incentives = 1200
    incentives_data = [
        {'task_description': 'Completed ANC visit', 'date_completed': '2025-09-17', 'patient_id': 12, 'amount': 250, 'status': 'Paid', 'status_class': 'success'},
        {'task_description': 'Child immunization', 'date_completed': '2025-09-18', 'patient_id': 8, 'amount': 150, 'status': 'Pending', 'status_class': 'warning'},
    ]
    return render_template('asha_incentives.html', total_incentives=total_incentives, pending_incentives=pending_incentives, incentives=incentives_data)

@app.route('/asha/communication')
@login_required(role_ids=[ROLES['asha']])
def asha_communication():
    alerts = [
        {'title': 'New Govt Scheme', 'message': 'New family planning scheme has been launched. Check resources.', 'date': '2025-09-19', 'type': 'info'},
        {'title': 'Cholera Outbreak', 'message': 'A few cases of Cholera reported in neighboring village. Stay vigilant.', 'date': '2025-09-18', 'type': 'danger'}
    ]
    return render_template('asha_communication.html', alerts=alerts)

@app.route('/asha/educational_resources')
@login_required(role_ids=[ROLES['asha']])
def asha_educational_resources():
    resources = [
        {'title': 'Maternal Nutrition', 'description': 'Video guide on proper diet for pregnant women.', 'type': 'video', 'url': '#'},
        {'title': 'Handwashing Guide', 'description': 'A detailed PDF guide on effective handwashing.', 'type': 'pdf', 'url': '#'},
    ]
    return render_template('asha_educational_resources.html', resources=resources)

# --- Admin Dashboard ---
@app.route('/dashboard/admin')
@login_required(role_ids=[ROLES['admin']])
def admin_dashboard():
    return render_template('admin_dashboard.html')

# --- Main Execution ---
if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    seed_db()
    # Use use_reloader=False if you are on Windows and experience crashes
    app.run(debug=True)


