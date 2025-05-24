#!/usr/bin/env python3
# Medical Assistant Application Launcher

"""
This is the main entry point for the Medical Assistant application.
It launches the application and ensures all necessary components are loaded.
"""

import os
import sys
import time
import traceback

# Ensure the current directory is in the Python path
current_dir = os.path.abspath(os.path.dirname(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'tkinter',
        'sqlite3',
        'datetime',
        'json',
        'os',
        'time',
        'random'
    ]
    
    missing_packages = []
    
    # Try to import each package
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    # If there are missing packages, ask the user if they want to install them
    if missing_packages:
        print("The following required packages are missing:")
        for package in missing_packages:
            print(f"  - {package}")
        
        try:
            response = input("Would you like to install them now? (y/n): ")
            if response.lower() == 'y':
                import subprocess
                for package in missing_packages:
                    print(f"Installing {package}...")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print("All dependencies installed successfully.")
            else:
                print("Dependencies not installed. Application may not function correctly.")
                return False
        except Exception as e:
            print(f"Error installing dependencies: {e}")
            return False
    
    return True

def ensure_directory_structure():
    """Ensure all required directories exist"""
    directories = [
        "database",
        "modules",
        "ui",
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

def create_db_manager():
    """Create or update the db_manager.py file"""
    db_manager_path = "db_manager.py"
    
    # Basic db_manager.py content
    db_manager_content = '''"""
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
    
    print("Database initialized successfully")
    
    # Pre-populate database with sample data if needed
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
    
    # Check if users table is empty and add a test user if needed
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Add a test user (username: test, password: test123)
        cursor.execute(
            "INSERT INTO users (username, password, email, full_name, registration_date) VALUES (?, ?, ?, ?, ?)",
            ("test", "test123", "test@example.com", "Test User", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        print("Added test user: username=test, password=test123")
    
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
'''
    
    # Create the db_manager.py file if it doesn't exist
    if not os.path.exists(db_manager_path):
        with open(db_manager_path, "w", encoding="utf-8") as f:
            f.write(db_manager_content)
        print(f"Created database manager at {db_manager_path}")
    
    return True

def create_dummy_main():
    """Create a dummy main.py file if it doesn't exist"""
    if not os.path.exists("main.py"):
        print("Creating a basic main.py file...")
        with open("main.py", "w", encoding="utf-8") as f:
            f.write('''"""
Basic main function for Medical Assistant application.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Ensure the current directory is in the Python path
current_dir = os.path.abspath(os.path.dirname(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Try to import from our packages
try:
    from db_manager import check_database, ensure_directories_exist
except ImportError as e:
    print(f"Error importing database module: {e}")
    print("Please ensure the db_manager.py file exists in the current directory.")
    sys.exit(1)

def main():
    """Main application function"""
    root = tk.Tk()
    root.title("Medical Assistant")
    root.geometry("800x600")
    
    # Setup a basic UI
    frame = ttk.Frame(root, padding=20)
    frame.pack(fill="both", expand=True)
    
    label = ttk.Label(
        frame, 
        text="Medical Assistant Application", 
        font=("Segoe UI", 18, "bold")
    )
    label.pack(pady=20)
    
    info = ttk.Label(
        frame,
        text="Application is initializing...\\nThe database has been set up successfully.",
        font=("Segoe UI", 12),
        justify="center"
    )
    info.pack(pady=20)
    
    # Initialize database
    try:
        ensure_directories_exist()
        check_database()
        
        success_text = ttk.Label(
            frame,
            text="Database connection successful!",
            font=("Segoe UI", 12),
            foreground="green"
        )
        success_text.pack(pady=20)
        
        messagebox.showinfo(
            "Setup Complete", 
            "The Medical Assistant application structure has been created successfully.\\n\\n"
            "You can now start implementing the specific functionality for each module."
        )
    except Exception as e:
        error_text = ttk.Label(
            frame,
            text=f"Error connecting to database: {e}",
            font=("Segoe UI", 12),
            foreground="red"
        )
        error_text.pack(pady=20)
        
        messagebox.showerror(
            "Setup Error",
            f"There was an error setting up the database: {e}"
        )
    
    root.mainloop()

if __name__ == "__main__":
    main()
''')
        print("Created basic main.py file")

def check_module_import():
    """Check if we can import the db_manager module"""
    try:
        # Try to import the module
        import importlib
        spec = importlib.util.find_spec("db_manager")
        
        if spec is None:
            print("Module db_manager cannot be found. Creating/fixing it...")
            create_db_manager()
            # Reload the module finder to pick up the new module
            importlib.invalidate_caches()
            # Try again
            spec = importlib.util.find_spec("db_manager")
            if spec is None:
                return False
        
        # Now try to actually import it
        import db_manager
        return True
    except ImportError as e:
        print(f"Import error: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        return False

def start_application():
    """Start the main application"""
    try:
        # First, check if main.py exists, and create a dummy if not
        create_dummy_main()
        
        # Now import and run the main function
        print("Starting Medical Assistant application...")
        from main import main
        main()
        return True
    except ImportError as e:
        print(f"Error importing main module: {e}")
        print("Please ensure main.py exists with a 'main()' function.")
        return False
    except Exception as e:
        print(f"Error starting application: {e}")
        traceback.print_exc()
        return False

def show_console_splash():
    """Show a console splash screen"""
    splash = r"""
    __  __          _ _           _    _                 _     _              _   
    |  \/  |        | (_)         | |  | |               (_)   | |            | |  
    | \  / | ___  __| |_  ___ __ _| |  | |  ___ ___ ___   _ ___| |_ __ _ _ __ | |_ 
    | |\/| |/ _ \/ _` | |/ __/ _` | |  | | / __/ __/ __| | / __| __/ _` | '_ \| __|
    | |  | |  __/ (_| | | (_| (_| | |__| | \__ \__ \__ \ | \__ \ || (_| | | | | |_ 
    |_|  |_|\___|\__,_|_|\___\__,_|\____/  |___/___/___/ |_|___/\__\__,_|_| |_|\__|
                                                       _/ |                        
                                                      |__/                         
    
    Version 1.0.0
    Initializing...
    """
    print(splash)
    
    # Animated loading
    steps = [".", "..", "...", "....", "....."]
    for _ in range(3):  # Repeat animation 3 times
        for step in steps:
            sys.stdout.write(f"\rLoading{step}      ")
            sys.stdout.flush()
            time.sleep(0.2)
    
    print("\n\nWelcome to Medical Assistant!\n")

if __name__ == "__main__":
    # Show splash screen
    show_console_splash()
    
    # Check dependencies
    if not check_dependencies():
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Ensure directory structure
    ensure_directory_structure()
    
    # Create or update the db_manager module
    create_db_manager()
    
    # Verify that we can import the module
    if not check_module_import():
        print("Failed to import db_manager module even after creating it.")
        print("This could be due to Python path issues or file permissions.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Import the module and initialize the database
    try:
        from db_manager import check_database
        
        # Check/initialize database
        print("Checking database...")
        if not check_database():
            print("Database initialized.")
        else:
            print("Database check successful.")
    except ImportError as e:
        print(f"Import error after creating module: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Start application
    if not start_application():
        input("Application failed to start. Press Enter to exit...")
        sys.exit(1)