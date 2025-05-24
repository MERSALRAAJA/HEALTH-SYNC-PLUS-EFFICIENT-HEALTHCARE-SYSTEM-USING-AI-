"""
Main application file for Medical Assistant application.
This version uses all the created tabs and modules.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Add current directory to Python path
current_dir = os.path.abspath(os.path.dirname(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import modules
from styles import setup_styles, COLORS
from widgets import center_window, create_custom_card
from user_auth import show_login_window
from db_manager import check_database, ensure_directories_exist

# Import tabs
from medication_management_tab import create_medication_manager_tab
from doctor_consultation_tab import create_doctor_consultation_tab
from purchase_medicine_tab import create_purchase_medicine_tab
from health_monitoring_tab import create_health_monitoring_tab
from appointment_tab import create_appointment_tab
from medical_records_tab import create_medical_records_tab

def create_main_window(username):
    """Create the main application window after successful login"""
    root = tk.Tk()
    root.title("Medical Assistant")
    root.geometry("1000x700")
    
    # Setup styles
    setup_styles()
    
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
        fg="#ffffff",        # White text (changed from black for better contrast)
        text="Settings",
        relief="raised",     # Add this to give button a raised appearance
        borderwidth=2,       # Add this to make border more visible
        activebackground="#1f0cbe", # Slightly darker color when clicked
        command=lambda: messagebox.showinfo("Settings", "Settings functionality will be implemented.")
    )
    settings_button.pack(side="left", padx=5)   
    
    # Logout Button
    logout_button = tk.Button(
        user_frame, 
        bg="#2910eb",        # Blue background
        fg="#ffffff",        # White text (changed from black for better contrast)
        text="Logout",
        relief="raised",     # Add this to give button a raised appearance
        borderwidth=2,       # Add this to make border more visible
        activebackground="#1f0cbe", # Slightly darker color when clicked
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
    
    # Create tabs using our created tab functions
    medication_tab = ttk.Frame(tab_control)
    tab_control.add(medication_tab, text="Medication Management")
    create_medication_manager_tab(medication_tab, username)
    
    """consultation_tab = ttk.Frame(tab_control)
    tab_control.add(consultation_tab, text="Doctor Consultation")
    create_doctor_consultation_tab(consultation_tab, username)
    
    purchase_tab = ttk.Frame(tab_control)
    tab_control.add(purchase_tab, text="Purchase Medicines")
    create_purchase_medicine_tab(purchase_tab, username)
    
    health_tab = ttk.Frame(tab_control)
    tab_control.add(health_tab, text="Health Monitoring")
    create_health_monitoring_tab(health_tab, username)
    
    appointment_tab = ttk.Frame(tab_control)
    tab_control.add(appointment_tab, text="Appointments")
    create_appointment_tab(appointment_tab, username)
    
    records_tab = ttk.Frame(tab_control)
    tab_control.add(records_tab, text="Medical Records")
    create_medical_records_tab(records_tab, username)"""
    
    tab_control.pack(expand=1, fill="both")
    
    # Center window on screen
    center_window(root)
    
    # Start the main loop
    root.mainloop()

def main():
    """Main application function"""
    # Initialize database and directories
    ensure_directories_exist()
    db_initialized = check_database()
    
    # Start the login process
    show_login_window()

if __name__ == "__main__":
    main()