#!/usr/bin/env python3
"""
Fix imports and directory structure for the Medical Assistant application.
"""

import os
import shutil

def main():
    print("Fixing Medical Assistant application structure...")
    
    # Create database directory if it doesn't exist
    if not os.path.exists("database"):
        os.makedirs("database")
        print("Created database directory")
    
    # Create ui directory if it doesn't exist
    if not os.path.exists("ui"):
        os.makedirs("ui")
        print("Created ui directory")
    
    # Create modules directory if it doesn't exist
    if not os.path.exists("modules"):
        os.makedirs("modules")
        print("Created modules directory")
    
    # Move db_manger.py to database/db_manager.py (fixing the typo)
    if os.path.exists("db_manger.py"):
        shutil.copy2("db_manger.py", "database/db_manager.py")
        print("Copied db_manger.py to database/db_manager.py (fixed typo)")
    
    # Move UI-related files to ui directory
    ui_files = ["styles.py", "widgets.py"]
    for file in ui_files:
        if os.path.exists(file):
            shutil.copy2(file, f"ui/{file}")
            print(f"Copied {file} to ui/{file}")
    
    # Move module files to modules directory
    module_files = [
        "medication_manager.py",
        "doctor_consultation.py",
        "medicine_purchase.py",
        "health_monitoring.py",
        "emergency_system.py",
        "ai_assistant.py",
        "user_auth.py",
        "settings_manager.py"
    ]
    
    for file in module_files:
        if os.path.exists(file):
            shutil.copy2(file, f"modules/{file}")
            print(f"Copied {file} to modules/{file}")
    
    print("\nFiles have been copied to their proper directories.")
    print("You'll need to update imports in the code to reflect the new structure.")
    print("For example:")
    print("  from database.db_manager import get_medications")
    print("  from ui.styles import COLORS")
    print("  from modules.user_auth import login_user")
    
    print("\nFinished fixing directory structure.")

if __name__ == "__main__":
    main()