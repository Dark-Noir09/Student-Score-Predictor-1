import sqlite3
import bcrypt
from datetime import datetime
import pandas as pd

def init_database():
    """Initialize database tables"""
    conn = sqlite3.connect('data/users.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            school_name TEXT NOT NULL,
            grade TEXT,
            email TEXT,
            role TEXT DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Predictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            hours_studied REAL,
            attendance REAL,
            previous_score REAL,
            tutoring_sessions INTEGER,
            sleep_hours REAL,
            distance_from_home REAL,
            physical_activity INTEGER,
            health INTEGER,
            motivation_level TEXT,
            teacher_quality TEXT,
            school_type TEXT,
            internet_access TEXT,
            family_income TEXT,
            parental_involvement TEXT,
            parent_education TEXT,
            peer_influence TEXT,
            learning_resources TEXT,
            extracurricular TEXT,
            study_environment TEXT,
            predicted_score INTEGER,
            recommendations TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Admin user (create if not exists)
    hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute('''
            INSERT INTO users (username, password, full_name, school_name, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', hashed_password, 'Administrator', 'System', 'admin'))
    except sqlite3.IntegrityError:
        pass  # Admin already exists
    
    conn.commit()
    conn.close()

def register_user(username, password, full_name, school_name, grade, email):
    """Register a new user"""
    conn = sqlite3.connect('data/users.db')
    cursor = conn.cursor()
    
    # Check if username exists
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        conn.close()
        return False, "Username already exists"
    
    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Insert user
    cursor.execute('''
        INSERT INTO users (username, password, full_name, school_name, grade, email, role)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (username, hashed_password, full_name, school_name, grade, email, 'student'))
    
    conn.commit()
    conn.close()
    return True, "Registration successful"

def login_user(username, password):
    """Authenticate user"""
    conn = sqlite3.connect('data/users.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, password, full_name, school_name, grade, email, role FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user[2]):
        return {
            'id': user[0],
            'username': user[1],
            'full_name': user[3],
            'school_name': user[4],
            'grade': user[5],
            'email': user[6],
            'role': user[7]
        }
    return None

def save_prediction(user_id, username, input_data, predicted_score, recommendations):
    """Save prediction to database"""
    conn = sqlite3.connect('data/users.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO predictions (
            user_id, username, hours_studied, attendance, previous_score,
            tutoring_sessions, sleep_hours, distance_from_home, physical_activity,
            health, motivation_level, teacher_quality, school_type, internet_access,
            family_income, parental_involvement, parent_education, peer_influence,
            learning_resources, extracurricular, study_environment, predicted_score,
            recommendations
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id, username,
        input_data['Hours_Studied'], input_data['Attendance'],
        input_data['Previous_Scores'], input_data['Tutoring_Sessions'],
        input_data['Sleep_Hours'], input_data['Distance_from_Home'],
        input_data['Physical_Activity'], input_data['Health'],
        input_data['Motivation_Level'], input_data['Teacher_Quality'],
        input_data['School_Type'], input_data['Internet_Access'],
        input_data['Family_Income'], input_data['Parental_Involvement'],
        input_data['Parental_Education_Level'], input_data['Peer_Influence'],
        input_data['Learning_Resources'], input_data['Extracurricular_Activities'],
        input_data['Study_Environment'], predicted_score, recommendations
    ))
    
    conn.commit()
    conn.close()

def get_all_predictions():
    """Get all predictions for admin panel"""
    conn = sqlite3.connect('data/users.db')
    df = pd.read_sql_query('''
        SELECT p.id, p.username, p.prediction_date, p.predicted_score,
               u.full_name, u.school_name, u.grade, u.email
        FROM predictions p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.prediction_date DESC
    ''', conn)
    conn.close()
    return df

def get_user_predictions(user_id):
    """Get predictions for specific user"""
    conn = sqlite3.connect('data/users.db')
    df = pd.read_sql_query('''
        SELECT prediction_date, predicted_score, hours_studied, attendance, sleep_hours
        FROM predictions
        WHERE user_id = ?
        ORDER BY prediction_date DESC
    ''', conn, params=(user_id,))
    conn.close()
    return df
