#!/usr/bin/env python3
"""
Setup script to create and organize the Medical Assistant project structure.
This script will create the necessary directories and files for the application.
"""

import os
import shutil
import sys

def create_directory(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")
    else:
        print(f"Directory already exists: {directory}")

def create_file(file_path, content=""):
    """Create a file with optional content"""
    # Create the directory if needed
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    # Check if file exists
    if os.path.exists(file_path):
        print(f"File already exists: {file_path}")
        return
    
    # Create the file
    with open(file_path, 'w') as f:
        f.write(content)
    print(f"Created file: {file_path}")

def setup_project():
    """Set up the full project structure"""
    # Create main directories
    base_dir = "."
    directories = [
        os.path.join(base_dir, "database"),
        os.path.join(base_dir, "modules"),
        os.path.join(base_dir, "ui"),
        os.path.join(base_dir, "temp"),  # Temporary directory for user uploads
        os.path.join(base_dir, "preferences"),  # For user preferences
        os.path.join(base_dir, "appointments"),  # For appointments data
        os.path.join(base_dir, "medical_records"),  # For medical records
        os.path.join(base_dir, "emergency"),  # For emergency contacts
        os.path.join(base_dir, "notifications"),  # For notifications
        os.path.join(base_dir, "carts"),  # For shopping carts
        os.path.join(base_dir, "reminders"),  # For reminders
        os.path.join(base_dir, "calls")  # For call history
    ]
    
    for directory in directories:
        create_directory(directory)
    
    # Create __init__.py files in package directories
    packages = ["database", "modules", "ui"]
    for package in packages:
        init_path = os.path.join(base_dir, package, "__init__.py")
        create_file(init_path, f'"""\n{package.capitalize()} package for Medical Assistant application.\n"""')
    
    # Create database files
    database_files = {
        "db_manager.py": "Database manager for SQLite operations",
        "user_db.py": "User authentication and profile management",
        "appointment_db.py": "Appointment database operations",
        "medication_db.py": "Medication tracking and reminders",
        "medical_record_db.py": "Medical records management",
        "preferences_db.py": "User preferences storage"
    }
    
    for filename, description in database_files.items():
        file_path = os.path.join(base_dir, "database", filename)
        content = f'"""\n{description}\n"""\n\nimport sqlite3\nimport os\n\n# Implementation goes here\n'
        create_file(file_path, content)
    
    # Create module files
    module_files = {
        "login_manager.py": "Login and user authentication",
        "health_monitoring.py": "Health monitoring with pulse sensor",
        "appointment_manager.py": "Appointment scheduling",
        "medical_records.py": "Medical records management",
        "notification_system.py": "Notification and reminders",
        "medication_manager.py": "Medication management",
        "doctor_consultation.py": "Doctor consultation",
        "medicine_purchase.py": "Medicine purchase",
        "emergency_system.py": "Emergency SOS system",
        "ai_assistant.py": "AI assistant for medical advice",
        "user_auth.py": "User authentication utilities",
        "settings_manager.py": "Settings management"
    }
    
    for filename, description in module_files.items():
        file_path = os.path.join(base_dir, "modules", filename)
        content = f'"""\n{description}\n"""\n\nimport tkinter as tk\nfrom tkinter import ttk\n\n# Implementation goes here\n'
        create_file(file_path, content)
    
    # Create UI files
    ui_files = {
        "styles.py": "UI styles and themes",
        "widgets.py": "Custom widgets and UI components",
        "medication_tab.py": "Medication management tab UI",
        "consultation_tab.py": "Doctor consultation tab UI",
        "purchase_tab.py": "Medicine purchase tab UI",
        "health_tab.py": "Health monitoring tab UI",
        "appointment_tab.py": "Appointment management tab UI",
        "records_tab.py": "Medical records tab UI",
        "settings_menu.py": "Settings menu UI"
    }
    
    for filename, description in ui_files.items():
        file_path = os.path.join(base_dir, "ui", filename)
        content = f'"""\n{description}\n"""\n\nimport tkinter as tk\nfrom tkinter import ttk\n\n# Implementation goes here\n'
        create_file(file_path, content)
    
    # Create main application files
    create_file(os.path.join(base_dir, "main.py"), '"""\nMain application file for Medical Assistant application.\n"""\n\nimport tkinter as tk\nfrom tkinter import ttk\n\n# Main application implementation\n')
    create_file(os.path.join(base_dir, "run_app.py"), '"""\nApplication launcher for Medical Assistant application.\n"""\n\nimport sys\nimport os\n\n# Add parent directory to path for imports\nsys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))\n\n# Now we can import from our packages\nfrom main import main\n\nif __name__ == "__main__":\n    main()\n')
    
    # Create a README file
    readme_content = """# Medical Assistant Application

A comprehensive desktop application for healthcare management, built with Python and Tkinter.

## Features

- **Medication Management**: Set reminders for medications and track their schedules
- **Doctor Consultation**: Connect with doctors via Google Meet
- **Medicine Purchase**: Browse and purchase medicines with online payment
- **Health Monitoring**: Track vital signs like pulse rate
- **Medical Records**: Store and access your medical records
- **Emergency SOS**: Quick access to emergency services

## Getting Started

1. Make sure Python 3.8+ is installed
2. Run the application with:
   ```
   python run_app.py
   ```

## Directory Structure

```
medical/
├── database/    # Database operations
├── modules/     # Application modules
├── ui/          # User interface components
├── main.py      # Main application
└── run_app.py   # Application launcher
```
"""
    create_file(os.path.join(base_dir, "README.md"), readme_content)
    
    print("\nProject setup complete!")
    print("You can now start implementing the specific functionality in each file.")
    print("Run the application with: python run_app.py")

if __name__ == "__main__":
    setup_project()