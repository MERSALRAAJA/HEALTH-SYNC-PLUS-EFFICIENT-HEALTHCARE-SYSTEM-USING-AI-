"""
Enhanced Registration Form with scrolling support
This module creates a registration form with scrollable content for the Medical Assistant application.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sqlite3
import hashlib
from datetime import datetime

# Database path
DB_PATH = os.path.join("database", "medical_assistant.db")

def hash_password(password):
    """Create a hash of the password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def show_register_window(parent, login_callback=None):
    """Show the registration window with scrollable content"""
    register_window = tk.Toplevel(parent)
    register_window.title("Medical Assistant - Register")
    register_window.geometry("600x600")
    register_window.transient(parent)
    register_window.grab_set()
    
    # Create a canvas with scrollbar for scrollable content
    canvas = tk.Canvas(register_window)
    scrollbar = ttk.Scrollbar(register_window, orient="vertical", command=canvas.yview)
    
    # Configure the canvas to use scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Layout scrollbar and canvas
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    
    # Create main frame inside canvas
    main_frame = ttk.Frame(canvas, padding=30)
    
    # Create a window in the canvas to hold the main frame
    canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")
    
    # Configure the canvas to resize with the window
    def configure_canvas(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        # Make sure main_frame width matches canvas width
        canvas.itemconfig(canvas_window, width=event.width)
    
    main_frame.bind("<Configure>", configure_canvas)
    
    # Configure the canvas to be resized with the window
    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)
    
    canvas.bind("<Configure>", on_canvas_configure)
    
    # Add mouse wheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    # Registration form content
    title_label = ttk.Label(main_frame, text="Register New Account", font=("Segoe UI", 18, "bold"))
    title_label.pack(pady=(0, 20))
    
    # Required fields note
    note_label = ttk.Label(
        main_frame,
        text="Fields marked with * are required",
        font=("Segoe UI", 9, "italic"),
        foreground="#666666"
    )
    note_label.pack(pady=(0, 15), anchor="w")
    
    # Account Information section
    account_frame = ttk.LabelFrame(main_frame, text="Account Information")
    account_frame.pack(fill="x", pady=(0, 20))
    
    # Username
    username_label = ttk.Label(account_frame, text="Username*:")
    username_label.pack(fill='x', pady=(10, 5), anchor='w', padx=10)
    
    username_entry = ttk.Entry(account_frame)
    username_entry.pack(fill='x', pady=(0, 10), ipady=5, padx=10)
    
    # Email
    email_label = ttk.Label(account_frame, text="Email*:")
    email_label.pack(fill='x', pady=(0, 5), anchor='w', padx=10)
    
    email_entry = ttk.Entry(account_frame)
    email_entry.pack(fill='x', pady=(0, 10), ipady=5, padx=10)
    
    # Full name
    name_label = ttk.Label(account_frame, text="Full Name*:")
    name_label.pack(fill='x', pady=(0, 5), anchor='w', padx=10)
    
    name_entry = ttk.Entry(account_frame)
    name_entry.pack(fill='x', pady=(0, 10), ipady=5, padx=10)
    
    # Phone number
    phone_label = ttk.Label(account_frame, text="Phone Number:")
    phone_label.pack(fill='x', pady=(0, 5), anchor='w', padx=10)
    
    phone_entry = ttk.Entry(account_frame)
    phone_entry.pack(fill='x', pady=(0, 10), ipady=5, padx=10)
    
    # Password
    password_label = ttk.Label(account_frame, text="Password*:")
    password_label.pack(fill='x', pady=(0, 5), anchor='w', padx=10)
    
    password_entry = ttk.Entry(account_frame, show="•")
    password_entry.pack(fill='x', pady=(0, 10), ipady=5, padx=10)
    
    # Confirm password
    confirm_label = ttk.Label(account_frame, text="Confirm Password*:")
    confirm_label.pack(fill='x', pady=(0, 5), anchor='w', padx=10)
    
    confirm_entry = ttk.Entry(account_frame, show="•")
    confirm_entry.pack(fill='x', pady=(0, 15), ipady=5, padx=10)
    
    # Personal Information section
    personal_frame = ttk.LabelFrame(main_frame, text="Personal Information")
    personal_frame.pack(fill="x", pady=(0, 20))
    
    # Date of Birth
    dob_label = ttk.Label(personal_frame, text="Date of Birth (DD-MM-YYYY):")
    dob_label.pack(fill='x', pady=(10, 5), anchor='w', padx=10)
    
    dob_entry = ttk.Entry(personal_frame)
    dob_entry.pack(fill='x', pady=(0, 10), ipady=5, padx=10)
    
    # Gender
    gender_label = ttk.Label(personal_frame, text="Gender:")
    gender_label.pack(fill='x', pady=(0, 5), anchor='w', padx=10)
    
    gender_var = tk.StringVar()
    gender_frame = ttk.Frame(personal_frame)
    gender_frame.pack(fill='x', pady=(0, 10), padx=10)
    
    ttk.Radiobutton(gender_frame, text="Male", variable=gender_var, value="Male").pack(side="left", padx=(0, 10))
    ttk.Radiobutton(gender_frame, text="Female", variable=gender_var, value="Female").pack(side="left", padx=(0, 10))
    ttk.Radiobutton(gender_frame, text="Other", variable=gender_var, value="Other").pack(side="left")
    
    # Address
    address_label = ttk.Label(personal_frame, text="Address:")
    address_label.pack(fill='x', pady=(0, 5), anchor='w', padx=10)
    
    address_entry = ttk.Entry(personal_frame)
    address_entry.pack(fill='x', pady=(0, 10), ipady=5, padx=10)
    
    # City/State in one row
    location_frame = ttk.Frame(personal_frame)
    location_frame.pack(fill='x', pady=(0, 10), padx=10)
    
    city_label = ttk.Label(location_frame, text="City:")
    city_label.pack(side="left", padx=(0, 5))
    
    city_entry = ttk.Entry(location_frame, width=20)
    city_entry.pack(side="left", padx=(0, 15))
    
    state_label = ttk.Label(location_frame, text="State:")
    state_label.pack(side="left", padx=(0, 5))
    
    state_entry = ttk.Entry(location_frame, width=20)
    state_entry.pack(side="left")
    
    # Medical Information section
    medical_frame = ttk.LabelFrame(main_frame, text="Medical Information")
    medical_frame.pack(fill="x", pady=(0, 20))
    
    # Blood Group
    blood_label = ttk.Label(medical_frame, text="Blood Group:")
    blood_label.pack(fill='x', pady=(10, 5), anchor='w', padx=10)
    
    blood_var = tk.StringVar()
    blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Don't Know"]
    blood_combo = ttk.Combobox(medical_frame, textvariable=blood_var, values=blood_groups, state="readonly")
    blood_combo.pack(fill='x', pady=(0, 10), padx=10)
    
    # Allergies
    allergies_label = ttk.Label(medical_frame, text="Allergies (if any):")
    allergies_label.pack(fill='x', pady=(0, 5), anchor='w', padx=10)
    
    allergies_entry = ttk.Entry(medical_frame)
    allergies_entry.pack(fill='x', pady=(0, 10), ipady=5, padx=10)
    
    # Emergency Contact
    emergency_label = ttk.Label(medical_frame, text="Emergency Contact Name:")
    emergency_label.pack(fill='x', pady=(0, 5), anchor='w', padx=10)
    
    emergency_entry = ttk.Entry(medical_frame)
    emergency_entry.pack(fill='x', pady=(0, 10), ipady=5, padx=10)
    
    # Emergency Contact Phone
    emergency_phone_label = ttk.Label(medical_frame, text="Emergency Contact Phone:")
    emergency_phone_label.pack(fill='x', pady=(0, 5), anchor='w', padx=10)
    
    emergency_phone_entry = ttk.Entry(medical_frame)
    emergency_phone_entry.pack(fill='x', pady=(0, 15), ipady=5, padx=10)
    
    # Functions
    def validate_form():
        """Validate form fields"""
        # Required fields
        if not username_entry.get().strip():
            messagebox.showerror("Error", "Username is required")
            return False
        
        if not email_entry.get().strip():
            messagebox.showerror("Error", "Email is required")
            return False
        
        if not name_entry.get().strip():
            messagebox.showerror("Error", "Full Name is required")
            return False
        
        if not password_entry.get():
            messagebox.showerror("Error", "Password is required")
            return False
        
        if password_entry.get() != confirm_entry.get():
            messagebox.showerror("Error", "Passwords do not match")
            return False
        
        # Password strength
        if len(password_entry.get()) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long")
            return False
        
        # Email format validation
        email = email_entry.get().strip()
        if "@" not in email or "." not in email:
            messagebox.showerror("Error", "Please enter a valid email address")
            return False
        
        # All validations passed
        return True
    
    def register_user():
        """Register a new user"""
        if not validate_form():
            return
        
        try:
            # Connect to database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Check if username exists
            cursor.execute("SELECT username FROM users WHERE username = ?", (username_entry.get().strip(),))
            if cursor.fetchone():
                messagebox.showerror("Error", "Username already exists. Please choose another username.")
                conn.close()
                return
            
            # Hash password
            hashed_password = hash_password(password_entry.get())
            
            # Insert user
            cursor.execute(
                """INSERT INTO users 
                   (username, password, email, phone, full_name, registration_date) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    username_entry.get().strip(),
                    hashed_password,
                    email_entry.get().strip(),
                    phone_entry.get().strip(),
                    name_entry.get().strip(),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )
            
            # Get the user ID for personal info
            user_id = cursor.lastrowid
            
            # Insert personal info
            cursor.execute(
                """INSERT INTO personal_info 
                   (user_id, dob, gender, blood_group, address, city, state,
                    emergency_contact_name, emergency_contact_phone, allergies) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    user_id,
                    dob_entry.get().strip(),
                    gender_var.get(),
                    blood_var.get(),
                    address_entry.get().strip(),
                    city_entry.get().strip(),
                    state_entry.get().strip(),
                    emergency_entry.get().strip(),
                    emergency_phone_entry.get().strip(),
                    allergies_entry.get().strip()
                )
            )
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Registration Successful", 
                            "Your account has been created successfully. You can now log in.")
            
            register_window.destroy()
            
            # Call login callback if provided
            if login_callback:
                login_callback(username_entry.get().strip())
            
        except Exception as e:
            messagebox.showerror("Registration Error", f"An error occurred: {str(e)}")
    
    # Buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill="x", pady=20)
    
    register_button = ttk.Button(
        button_frame,
        text="Register",
        command=register_user
    )
    register_button.pack(side="left", padx=(0, 10), ipady=5, ipadx=10)
    
    cancel_button = ttk.Button(
        button_frame,
        text="Cancel",
        command=register_window.destroy
    )
    cancel_button.pack(side="left", ipady=5, ipadx=10)
    
    # Center window on parent
    register_window.update_idletasks()
    width = register_window.winfo_width()
    height = register_window.winfo_height()
    x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
    y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)
    register_window.geometry(f"+{x}+{y}")
    
    return register_window