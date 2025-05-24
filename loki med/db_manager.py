"""
Database manager for SQLite operations.
Central module for database initialization and management.
"""

import os
import json
import sqlite3
from datetime import datetime

# Database file paths
DB_FOLDER = "database"
SQLITE_DB = os.path.join(DB_FOLDER, "medical_assistant.db")

def ensure_directories_exist():
    """Ensure all required directories exist"""
    directories = [
        "database",
        "preferences",
        "appointments",
        "medical_records",
        "emergency",
        "notifications",
        "carts",
        "reminders",
        "calls"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def initialize_database():
    """Initialize the SQLite database if it doesn't exist"""
    # Ensure the database directory exists
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
        print(f"Created database directory: {DB_FOLDER}")
    
    # Connect to the database (this will create it if it doesn't exist)
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        full_name TEXT,
        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create personal_info table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS personal_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        dob TEXT,
        gender TEXT,
        blood_group TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        zip_code TEXT,
        country TEXT,
        emergency_contact_name TEXT,
        emergency_contact_relation TEXT,
        emergency_contact_phone TEXT,
        allergies TEXT,
        chronic_illnesses TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    
    # Create appointments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        time TEXT,
        doctor TEXT,
        type TEXT,
        notes TEXT,
        reminder BOOLEAN,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    
    # Create medications table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        description TEXT,
        quantity INTEGER
    )
    """)
    
    # Create reminders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        medicine_id INTEGER,
        dose TEXT,
        date TEXT,
        time TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (medicine_id) REFERENCES medications(id)
    )
    """)
    
    # Create medical_records table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medical_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        file_name TEXT,
        file_path TEXT,
        record_type TEXT,
        record_date TEXT,
        provider TEXT,
        description TEXT,
        tags TEXT,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    
    # Create cart_items table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        medicine_id INTEGER,
        quantity INTEGER,
        price REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (medicine_id) REFERENCES medications(id)
    )
    """)
    
    # Create health_readings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS health_readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        reading_type TEXT,
        value TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    
    # Create notifications table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT,
        is_read BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()

def get_connection():
    """Get a connection to the SQLite database"""
    conn = sqlite3.connect(SQLITE_DB)
    # Enable dictionary results
    conn.row_factory = sqlite3.Row
    return conn

def check_database():
    """Check if the database exists and is properly initialized"""
    if not os.path.exists(SQLITE_DB):
        print("Database not found, initializing...")
        initialize_database()
        return False
    
    # Check if the database has the expected tables
    try:
        conn = sqlite3.connect(SQLITE_DB)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            "users", "personal_info", "appointments", "medications", 
            "reminders", "medical_records", "cart_items", "health_readings",
            "notifications"
        ]
        
        # Check if all expected tables exist
        all_tables_exist = all(table in tables for table in expected_tables)
        
        conn.close()
        
        if not all_tables_exist:
            print("Database schema incomplete, reinitializing...")
            initialize_database()
            return False
        
        return True
    except Exception as e:
        print(f"Error checking database: {e}")
        return False

def get_medications():
    """Get all medications from the database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM medications")
    
    medications = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return medications

# Initialize functions
if __name__ == "__main__":
    ensure_directories_exist()
    initialize_database()
    
    print("Database initialized successfully")
    
    # Pre-populate database with sample data
    populate_initial_data()

def populate_initial_data():
    """Populate the database with initial data"""
    # Add sample medications
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()
    
    # Check if medications table is empty
    cursor.execute("SELECT COUNT(*) FROM medications")
    count = cursor.fetchone()[0]
    
    if count == 0:
        medications = [
            ("Amoxicillin", 1079.73, "Antibiotic used to treat bacterial infections", 20),
            ("Ciprofloxacin", 1287.53, "Broad-spectrum antibiotic used for respiratory infections", 10),
            ("Metronidazole", 830.37, "Antibiotic effective against anaerobic bacteria", 15),
            ("Azithromycin", 1578.45, "Macrolide antibiotic used for respiratory infections", 12),
            ("Cephalexin", 1205.24, "First-generation cephalosporin antibiotic", 25),
            ("Amoxicillin + Clavulanate", 1910.93, "Combination antibiotic with beta-lactamase inhibitor", 18),
            ("Doxycycline", 996.61, "Tetracycline antibiotic effective against many bacteria", 30),
            ("Cloxacillin", 1142.90, "Penicillin antibiotic resistant to penicillinase", 20),
            ("Clarithromycin", 1661.57, "Macrolide antibiotic used for respiratory infections", 15),
            ("Paracetamol", 497.89, "Pain reliever and fever reducer", 50),
            ("Ibuprofen", 622.57, "Nonsteroidal anti-inflammatory drug", 40),
            ("Aspirin", 519.50, "Pain reliever, anti-inflammatory, and fever reducer", 45),
            ("Loratadine", 747.25, "Antihistamine for allergy relief", 25),
            ("Omeprazole", 1245.97, "Proton pump inhibitor for acid reflux", 30)
        ]
        
        cursor.executemany(
            "INSERT INTO medications (name, price, description, quantity) VALUES (?, ?, ?, ?)", 
            medications
        )
        
        print("Added sample medications")
    
    # Check if users table is empty and add test users if needed
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Add a test user (username: test, password: test123)
        cursor.execute(
            "INSERT INTO users (username, password, email, full_name, registration_date) VALUES (?, ?, ?, ?, ?)",
            ("test", "test123", "test@example.com", "Test User", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        
        # Add a second test user (username: batman, password: batman123)
        cursor.execute(
            "INSERT INTO users (username, password, email, full_name, registration_date) VALUES (?, ?, ?, ?, ?)",
            ("batman", "batman123", "batman@example.com", "Bruce Wayne", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        
        user_id = cursor.lastrowid  # Get batman's ID
        
        # Add personal info for batman
        cursor.execute(
            """INSERT INTO personal_info 
               (user_id, dob, gender, blood_group, allergies, chronic_illnesses, emergency_contact_name, emergency_contact_phone) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, "30-05-1985", "Male", "O+", "None", "None", "Alfred Pennyworth", "1234567890")
        )
        
        # Add some sample appointments
        now = datetime.now()
        current_date = now.strftime("%d-%m-%Y")
        next_date = (now + datetime.timedelta(days=3)).strftime("%d-%m-%Y")
        
        cursor.execute(
            """INSERT INTO appointments 
               (user_id, date, time, doctor, type, notes, reminder, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, current_date, "14:30", "Dr. Smith (General Physician)", 
             "Consultation", "Regular checkup", 1, "Scheduled", now.strftime("%Y-%m-%d %H:%M:%S"))
        )
        
        cursor.execute(
            """INSERT INTO appointments 
               (user_id, date, time, doctor, type, notes, reminder, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, next_date, "10:15", "Dr. Johnson (Cardiologist)", 
             "Follow-up", "Discuss test results", 1, "Confirmed", now.strftime("%Y-%m-%d %H:%M:%S"))
        )
        
        print("Added test users with sample data")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()