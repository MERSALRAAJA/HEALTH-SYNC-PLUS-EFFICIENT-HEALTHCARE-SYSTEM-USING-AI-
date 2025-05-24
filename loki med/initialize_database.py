"""
Database initialization script for the Medical Assistant application.
This script creates and populates the database with initial data.
"""

import os
import sqlite3
from datetime import datetime, timedelta
import hashlib

# Database path
DB_FOLDER = "database"
SQLITE_DB = os.path.join(DB_FOLDER, "medical_assistant.db")

def hash_password(password):
    """Create a SHA-256 hash of the password"""
    return hashlib.sha256(password.encode()).hexdigest()

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
    """Initialize the SQLite database with tables and sample data"""
    print("Initializing database...")
    
    # Ensure the database directory exists
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
        print(f"Created database directory: {DB_FOLDER}")
    
    # Connect to the database (this will create it if it doesn't exist)
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()
    
    print("Creating tables...")
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        full_name TEXT,
        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create personal_info table
    cursor.execute('''
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
    ''')
    
    # Create appointments table
    cursor.execute('''
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
    ''')
    
    # Create medications table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS medications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        description TEXT,
        quantity INTEGER
    )
    ''')
    
    # Create reminders table
    cursor.execute('''
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
    ''')
    
    # Create medical_records table
    cursor.execute('''
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
    ''')
    
    # Create cart_items table
    cursor.execute('''
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
    ''')
    
    # Create health_readings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS health_readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        reading_type TEXT,
        value TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # Create notifications table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT,
        is_read BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    print("Tables created successfully")
    
    # Check if users table is empty and add default users if needed
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("Adding default users...")
        
        # Add test users (both with plain and hashed passwords for testing)
        # In a real app, you'd always use hashed passwords
        
        # User: batman, Password: batman123
        cursor.execute(
            "INSERT INTO users (username, password, email, full_name, registration_date) VALUES (?, ?, ?, ?, ?)",
            ("batman", "batman123", "batman@example.com", "Bruce Wayne", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        
        # User: test, Password: test123 (hashed)
        cursor.execute(
            "INSERT INTO users (username, password, email, full_name, registration_date) VALUES (?, ?, ?, ?, ?)",
            ("test", hash_password("test123"), "test@example.com", "Test User", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        
        # Add personal info for batman
        user_id = cursor.lastrowid - 1  # Get batman's ID
        cursor.execute(
            """INSERT INTO personal_info 
               (user_id, dob, gender, blood_group, allergies, chronic_illnesses, emergency_contact_name, emergency_contact_phone) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, "10-05-1985", "Male", "O+", "None", "None", "Alfred Pennyworth", "+1234567890")
        )
        
        print("Default users added")
    
    # Check if medications table is empty and add sample data if needed
    cursor.execute("SELECT COUNT(*) FROM medications")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("Adding sample medications...")
        
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
        
        print("Sample medications added")
    
    # Add sample appointments if none exist
    cursor.execute("SELECT COUNT(*) FROM appointments")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("Adding sample appointments...")
        
        # Get user ID for batman
        cursor.execute("SELECT id FROM users WHERE username = ?", ("batman",))
        result = cursor.fetchone()
        if result is None:
            print("User 'batman' not found, skipping sample appointments")
        else:
            user_id = result[0]
            
            # Current date
            now = datetime.now()
            
            # Create some appointments
            appointments = [
                (user_id, now.strftime("%d-%m-%Y"), "14:30", "Dr. Smith (General Physician)", "Consultation", 
                 "Regular checkup", 1, "Scheduled", (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")),
                
                (user_id, (now + timedelta(days=3)).strftime("%d-%m-%Y"), "10:15", "Dr. Johnson (Cardiologist)", 
                 "Follow-up", "Discuss test results", 1, "Confirmed", (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")),
                
                (user_id, (now + timedelta(days=10)).strftime("%d-%m-%Y"), "16:00", "Dr. Williams (Pediatrician)", 
                 "Test", "Annual physical", 1, "Scheduled", (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"))
            ]
            
            cursor.executemany(
                """INSERT INTO appointments 
                   (user_id, date, time, doctor, type, notes, reminder, status, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                appointments
            )
            
            print("Sample appointments added")
    
    # Add sample reminders if none exist
    cursor.execute("SELECT COUNT(*) FROM reminders")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("Adding sample medication reminders...")
        
        # Get user ID for batman
        cursor.execute("SELECT id FROM users WHERE username = ?", ("batman",))
        result = cursor.fetchone()
        if result is None:
            print("User 'batman' not found, skipping sample reminders")
        else:
            user_id = result[0]
            
            # Get medication IDs
            paracetamol_id = None
            ibuprofen_id = None
            
            cursor.execute("SELECT id FROM medications WHERE name = ?", ("Paracetamol",))
            result = cursor.fetchone()
            if result:
                paracetamol_id = result[0]
                
            cursor.execute("SELECT id FROM medications WHERE name = ?", ("Ibuprofen",))
            result = cursor.fetchone()
            if result:
                ibuprofen_id = result[0]
            
            if paracetamol_id and ibuprofen_id:
                # Current date
                now = datetime.now()
                today = now.strftime("%d-%m-%Y")
                tomorrow = (now + timedelta(days=1)).strftime("%d-%m-%Y")
                
                # Create reminders
                reminders = [
                    (user_id, paracetamol_id, "500mg", today, "08:00", now.strftime("%Y-%m-%d %H:%M:%S")),
                    (user_id, paracetamol_id, "500mg", today, "20:00", now.strftime("%Y-%m-%d %H:%M:%S")),
                    (user_id, ibuprofen_id, "200mg", tomorrow, "08:00", now.strftime("%Y-%m-%d %H:%M:%S")),
                    (user_id, ibuprofen_id, "200mg", tomorrow, "14:00", now.strftime("%Y-%m-%d %H:%M:%S")),
                    (user_id, ibuprofen_id, "200mg", tomorrow, "20:00", now.strftime("%Y-%m-%d %H:%M:%S"))
                ]
                
                cursor.executemany(
                    """INSERT INTO reminders 
                       (user_id, medicine_id, dose, date, time, created_at)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    reminders
                )
                
                print("Sample medication reminders added")
            else:
                print("Required medications not found, skipping sample reminders")
    
    # Add sample health readings if none exist
    cursor.execute("SELECT COUNT(*) FROM health_readings")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("Adding sample health readings...")
        
        # Get user ID for batman
        cursor.execute("SELECT id FROM users WHERE username = ?", ("batman",))
        result = cursor.fetchone()
        if result is None:
            print("User 'batman' not found, skipping sample health readings")
        else:
            user_id = result[0]
            
            # Current date and previous days
            now = datetime.now()
            
            # Create health readings (pulse)
            readings = [
                (user_id, "pulse", "72", (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"), "Morning reading"),
                (user_id, "pulse", "78", (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"), "After lunch"),
                (user_id, "pulse", "68", (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"), "Evening reading"),
                (user_id, "pulse", "75", now.strftime("%Y-%m-%d %H:%M:%S"), "Morning reading")
            ]
            
            cursor.executemany(
                """INSERT INTO health_readings 
                   (user_id, reading_type, value, timestamp, notes)
                   VALUES (?, ?, ?, ?, ?)""",
                readings
            )
            
            print("Sample health readings added")
    
    # Add sample notifications if none exist
    cursor.execute("SELECT COUNT(*) FROM notifications")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("Adding sample notifications...")
        
        # Get user ID for batman
        cursor.execute("SELECT id FROM users WHERE username = ?", ("batman",))
        result = cursor.fetchone()
        if result is None:
            print("User 'batman' not found, skipping sample notifications")
        else:
            user_id = result[0]
            
            # Current date and previous times
            now = datetime.now()
            
            # Create notifications
            notifications = [
                (user_id, "Reminder: Take Paracetamol 500mg", 0, (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")),
                (user_id, "Appointment with Dr. Smith tomorrow at 14:30", 0, (now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")),
                (user_id, "Your order has been delivered", 1, (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")),
                (user_id, "Please update your medical records", 0, (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"))
            ]
            
            cursor.executemany(
                """INSERT INTO notifications 
                   (user_id, message, is_read, created_at)
                   VALUES (?, ?, ?, ?)""",
                notifications
            )
            
            print("Sample notifications added")
    
    # Commit changes and close
    conn.commit()
    conn.close()
    
    print("Database initialization complete!")
    return True

if __name__ == "__main__":
    print("Medical Assistant Database Initialization")
    print("----------------------------------------")
    
    ensure_directories_exist()
    initialize_database()
    
    print("\nSetup complete! You can now run the application with 'python main.py'")
    print("\nDefault login credentials:")
    print("  Username: batman")
    print("  Password: batman123")
    print("\nOr:")
    print("  Username: test")
    print("  Password: test123")