#!/usr/bin/env python3
"""
Medical Assistant Application Launcher
This script sets up and launches the Medical Assistant application.
"""

import os
import sys
import time
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# Constants for database
DB_FOLDER = "database"
SQLITE_DB = os.path.join(DB_FOLDER, "medical_assistant.db")

def ensure_directories_exist():
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

def initialize_database():
    """Initialize the SQLite database if it doesn't exist"""
    # Ensure the database directory exists
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
    
    # Connect to the database (this will create it if it doesn't exist)
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()
    
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
    
    # Commit changes and close connection
    conn.commit()
    conn.close()

def get_medications():
    """Get all medications from the database"""
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM medications")
    
    medications = []
    for row in cursor.fetchall():
        medications.append({
            "id": row[0],
            "name": row[1],
            "price": row[2],
            "description": row[3],
            "quantity": row[4]
        })
    
    conn.close()
    
    return medications

def center_window(window):
    """Center a window on the screen"""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def create_custom_card(parent, title=None, padding=10):
    """Create a custom card widget with a title"""
    # Main card frame
    card = ttk.Frame(parent, padding=padding)
    card.pack(fill="both", expand=True, pady=10)
    
    # Add title if provided
    if title:
        title_frame = ttk.Frame(card)
        title_frame.pack(fill="x", pady=(0, 10))
        
        title_label = ttk.Label(
            title_frame, 
            text=title, 
            font=("Segoe UI", 12, "bold")
        )
        title_label.pack(anchor="w")
        
        # Add separator
        separator = ttk.Separator(card, orient="horizontal")
        separator.pack(fill="x", pady=(0, 10))
    
    return card

def show_login_window():
    """Create the login window for the application"""
    login_window = tk.Tk()
    login_window.title("Medical Assistant - Login")
    login_window.geometry("400x500")
    
    # Create main frame
    main_frame = ttk.Frame(login_window, padding=20)
    main_frame.pack(expand=True, fill="both", padx=40, pady=40)
    
    # App title
    title_label = ttk.Label(main_frame, text="Medical Assistant", font=("Segoe UI", 18, "bold"))
    title_label.pack(pady=(0, 30))
    
    # Login form
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill="both", expand=True)
    
    # Username
    username_label = ttk.Label(form_frame, text="Username", font=("Segoe UI", 10))
    username_label.pack(fill='x', pady=(0, 5), anchor='w')
    username_entry = ttk.Entry(form_frame, font=("Segoe UI", 10))
    username_entry.pack(fill='x', pady=(0, 15), ipady=5)
    
    # Password
    password_label = ttk.Label(form_frame, text="Password", font=("Segoe UI", 10))
    password_label.pack(fill='x', pady=(0, 5), anchor='w')
    password_entry = ttk.Entry(form_frame, show="•", font=("Segoe UI", 10))
    password_entry.pack(fill='x', pady=(0, 20), ipady=5)
    
    # Pre-fill with test user
    username_entry.insert(0, "test")
    password_entry.insert(0, "test123")
    
    # Login function
    def login():
        username = username_entry.get()
        password = password_entry.get()
        
        # Connect to database
        conn = sqlite3.connect(SQLITE_DB)
        cursor = conn.cursor()
        
        # Check credentials
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        
        conn.close()
        
        if user:
            login_window.destroy()
            create_main_window(username)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
    
    # Buttons
    buttons_frame = ttk.Frame(form_frame)
    buttons_frame.pack(fill='x', pady=15)
    
    login_button = ttk.Button(buttons_frame, text="Login", command=login)
    login_button.pack(fill='x', pady=5, ipady=5)
    
    # Bind Enter key to login
    login_window.bind('<Return>', lambda event: login())
    
    # Center window on screen
    center_window(login_window)
    
    login_window.mainloop()

def create_main_window(username):
    """Create the main application window after successful login"""
    root = tk.Tk()
    root.title("Medical Assistant")
    root.geometry("900x700")
    
    # Create a header frame
    header_frame = ttk.Frame(root)
    header_frame.pack(fill="x", padx=15, pady=(15, 0))
    
    # App title
    app_title = ttk.Label(header_frame, text="Medical Assistant", font=("Segoe UI", 18, "bold"))
    app_title.pack(side="left", padx=10)
    
    # User info and logout frame
    user_frame = ttk.Frame(header_frame)
    user_frame.pack(side="right", padx=10)
    
    # Username display
    user_label = ttk.Label(user_frame, text=f"Welcome, {username}", font=("Segoe UI", 10))
    user_label.pack(side="left", padx=(0, 10))
    
    # Settings button
    settings_button = tk.Button(
        user_frame,
        bg="#2910eb",        # Blue background
        fg="#ffffff",
        text="Settings",
        command=lambda: messagebox.showinfo("Settings", "Settings functionality will be implemented.")
    )
    settings_button.pack(side="left", padx=5)    
    
    # Logout Button
    logout_button = tk.Button(
        user_frame,
        bg="#2910eb",        # Blue background
        fg="#ffffff", 
        text="Logout", 
        command=lambda: logout(root)
    )
    logout_button.pack(side="left")
    
    def logout(root):
        root.destroy()
        show_login_window()
    
    # Main content area
    main_frame = ttk.Frame(root)
    main_frame.pack(fill="both", expand=True, padx=15, pady=15)
    
    # Create tabs
    tab_control = ttk.Notebook(main_frame)
    
    # Create tabs for the application
    tab_names = [
        "Medication Management", 
        "Doctor Consultation", 
        "Purchase Medicines", 
        "Health Monitoring",
        "Appointments",
        "Medical Records"
    ]
    
    for tab_name in tab_names:
        tab = ttk.Frame(tab_control, padding=15)
        tab_control.add(tab, text=tab_name)
        
        # Add placeholder content
        card = create_custom_card(tab, f"{tab_name} Tab")
        
        message = ttk.Label(
            card,
            text=f"This is the {tab_name} tab.\nImplementation will be added here.",
            font=("Segoe UI", 12),
            justify="center"
        )
        message.pack(pady=50)
    
    tab_control.pack(expand=1, fill="both")
    
    # Center window on screen
    center_window(root)
    
    # Show a medication list to demonstrate database functionality
    try:
        medications = get_medications()
        if medications:
            medication_window = tk.Toplevel(root)
            medication_window.title("Available Medications")
            medication_window.geometry("600x400")
            
            med_frame = ttk.Frame(medication_window, padding=20)
            med_frame.pack(fill="both", expand=True)
            
            title = ttk.Label(med_frame, text="Available Medications", font=("Segoe UI", 16, "bold"))
            title.pack(pady=(0, 20))
            
            # Create treeview
            columns = ("Name", "Price", "Description", "In Stock")
            tree = ttk.Treeview(med_frame, columns=columns, show="headings", height=15)
            
            # Configure columns
            for col in columns:
                tree.heading(col, text=col)
            
            tree.column("Name", width=150)
            tree.column("Price", width=80)
            tree.column("Description", width=250)
            tree.column("In Stock", width=80)
            
            # Add data
            for med in medications:
                tree.insert("", "end", values=(
                    med["name"],
                    f"₹{med['price']:.2f}",
                    med["description"],
                    med["quantity"]
                ))
            
            tree.pack(fill="both", expand=True)
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(tree, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            
            center_window(medication_window)
    except Exception as e:
        messagebox.showwarning("Database Warning", f"Could not retrieve medications: {e}")
    
    # Start the main loop
    root.mainloop()

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
    
    # Set up the application
    ensure_directories_exist()
    initialize_database()
    
    # Start the application
    show_login_window()
    
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