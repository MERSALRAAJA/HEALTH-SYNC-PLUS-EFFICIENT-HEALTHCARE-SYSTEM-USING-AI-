#!/usr/bin/env python3
# Medical Assistant Application Launcher

"""
This is the main entry point for the Medical Assistant application.
It launches the application and ensures all necessary components are loaded.
"""

import os
import sys
import time

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'tkinter',
        'sqlite3',
        'threading',
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
    # Import db_manager module
    from db_manager import ensure_directories_exist
    ensure_directories_exist()

def check_database():
    """Check if the database exists and is properly initialized"""
    try:
        # Import db_manager
        from db_manager import check_database
        result = check_database()
        if result:
            print("Database check successful.")
        else:
            print("Database initialized/reinitialized.")
        return True
    except ImportError as e:
        print(f"Error importing database module: {e}")
        print("\nPlease ensure the db_manager.py file exists in the current directory")
        return False
    except Exception as e:
        print(f"Error checking database: {e}")
        return False

def create_dummy_main():
    """Create a dummy main.py file if it doesn't exist"""
    if not os.path.exists("main.py"):
        print("Creating a basic main.py file...")
        with open("main.py", "w") as f:
            f.write('''"""
Basic main function for Medical Assistant application.
"""

import tkinter as tk
from tkinter import ttk, messagebox

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
        text="Application is initializing...\nThe database has been set up successfully.",
        font=("Segoe UI", 12),
        justify="center"
    )
    info.pack(pady=20)
    
    messagebox.showinfo(
        "Setup Complete", 
        "The Medical Assistant application structure has been created successfully.\\n\\n"
        "You can now start implementing the specific functionality for each module."
    )
    
    root.mainloop()

if __name__ == "__main__":
    main()
''')
        print("Created basic main.py file")

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
        import traceback
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
    try:
        ensure_directory_structure()
    except ImportError:
        print("Error: Could not import db_manager module.")
        print("Please make sure the db_manager.py file exists in the current directory")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Check database
    if not check_database():
        input("Database initialization failed. Press Enter to exit...")
        sys.exit(1)
    
    # Start application
    if not start_application():
        input("Application failed to start. Press Enter to exit...")
        sys.exit(1)