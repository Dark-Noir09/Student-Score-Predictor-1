import sqlite3
import hashlib
import os
from datetime import datetime
import pandas as pd
import streamlit as st

# Simple password hashing
def hash_password(password):
    """Simple password hashing using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

@st.cache_resource
def init_database():
    """Initialize database tables"""
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
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
    
    # Check if admin exists
    cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        # Create admin user
        admin_password = hash_password('admin123')
        cursor.execute('''
            INSERT INTO users (username, password, full_name, school_name, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', admin_password, 'Administrator', 'System', 'admin'))
    
    conn.commit()
    conn.close()

def register_user(username, password, full_name, school_name, grade, email):
    """Register a new user"""
    try:
        conn = sqlite3.connect('data/users.db')
        cursor = conn.cursor()
        
        # Check if username exists
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Username already exists"
        
        # Hash password
        hashed_password = hash_password(password)
        
        # Insert user
        cursor.execute('''
            INSERT INTO users (username, password, full_name, school_name, grade, email, role)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, hashed_password, full_name, school_name, grade, email, 'student'))
        
        conn.commit()
        conn.close()
        return True, "Registration successful"
    except Exception as e:
        return False, f"Registration error: {str(e)}"

def login_user(username, password):
    """Authenticate user"""
    try:
        conn = sqlite3.connect('data/users.db')
        cursor = conn.cursor()
        
        hashed_password = hash_password(password)
        cursor.execute('SELECT id, username, password, full_name, school_name, grade, email, role FROM users WHERE username = ? AND password = ?', 
                       (username, hashed_password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'full_name': user[3],
                'school_name': user[4],
                'grade': user[5] if user[5] else "",
                'email': user[6] if user[6] else "",
                'role': user[7]
            }
        return None
    except Exception as e:
        return None

def save_prediction(user_id, username, input_data, predicted_score, recommendations):
    """Save prediction to database"""
    try:
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
        return True
    except Exception as e:
        print(f"Error saving prediction: {e}")
        return False

def get_all_predictions():
    """Get all predictions for admin panel"""
    try:
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
    except Exception as e:
        return pd.DataFrame()

def get_user_predictions(user_id):
    """Get predictions for specific user"""
    try:
        conn = sqlite3.connect('data/users.db')
        df = pd.read_sql_query('''
            SELECT prediction_date, predicted_score, hours_studied, attendance, sleep_hours
            FROM predictions
            WHERE user_id = ?
            ORDER BY prediction_date DESC
        ''', conn, params=(user_id,))
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()
