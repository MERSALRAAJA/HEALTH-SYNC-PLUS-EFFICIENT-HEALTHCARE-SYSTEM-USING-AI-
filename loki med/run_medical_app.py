#!/usr/bin/env python3
"""
Medical Assistant Application Launcher
This script starts the Medical Assistant application,
ensuring all dependencies and database setup are completed.
"""

import os
import sys
import time
from importlib import import_module
import traceback

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

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'tkinter',
        'sqlite3'
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
    try:
        # First try to import from db_manager
        sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
        from db_manager import ensure_directories_exist
        ensure_directories_exist()
        print("Directory structure verified using db_manager.")
        return True
    except ImportError:
        # Fallback: Create directories manually
        print("db_manager not found. Creating directories manually...")
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
        return True
    except Exception as e:
        print(f"Error ensuring directory structure: {e}")
        traceback.print_exc()
        return False

def check_database():
    """Check if the database exists and is properly initialized"""
    try:
        # First try to import from db_manager
        from db_manager import check_database
        result = check_database()
        if result:
            print("Database check successful.")
        else:
            print("Database initialized/reinitialized.")
        return True
    except ImportError:
        print("db_manager not found for database check.")
        return False
    except Exception as e:
        print(f"Error checking database: {e}")
        traceback.print_exc()
        return False

def start_application():
    """Start the main application"""
    try:
        # Import the main module and run the main function
        print("Starting Medical Assistant application...")
        from main import main
        main()
        return True
    except ImportError:
        print("Error: Could not import main module.")
        print("Make sure main.py exists and contains a main() function.")
        return False
    except Exception as e:
        print(f"Error starting application: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Show splash screen
    show_console_splash()
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Ensure directory structure
    print("\nChecking directory structure...")
    if not ensure_directory_structure():
        input("\nFailed to create necessary directories. Press Enter to exit...")
        sys.exit(1)
    
    # Check database
    print("\nChecking database...")
    if not check_database():
        print("\nWarning: Database check failed. The application may not function correctly.")
        proceed = input("Do you want to proceed anyway? (y/n): ")
        if proceed.lower() != 'y':
            sys.exit(1)
    
    # Start application
    print("\nAll checks complete. Starting application...")
    if not start_application():
        input("\nApplication failed to start. Press Enter to exit...")
        sys.exit(1)