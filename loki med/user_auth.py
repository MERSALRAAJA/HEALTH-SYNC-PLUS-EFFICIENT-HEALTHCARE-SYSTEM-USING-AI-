"""
Enhanced User Authentication System for Medical Assistant application.
This module provides a comprehensive login, registration, and password recovery system.
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import os
import sqlite3
import hashlib
import re
from datetime import datetime
import random
import string

# Database path
DB_PATH = os.path.join("database", "medical_assistant.db")

def center_window(window):
    """Center a window on the screen"""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def setup_styles():
    """Configure styles for all windows"""
    style = ttk.Style()
    
    # Try to use a modern theme
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    
    # Define colors
    bg_color = "#D7C0C0"  # Light blue background
    accent_color = "#000000"
    hover_color = "#ff1e00"
    text_color = "#000000"
    light_bg = "#00FFEAF0"
    
    # Configure frame styles
    style.configure("TFrame", background=bg_color)
    style.configure("Card.TFrame", background=bg_color, relief="solid", borderwidth=1)
    
    # Configure label styles
    style.configure("TLabel", background=bg_color, foreground=text_color, font=("Segoe UI", 10))
    style.configure("Title.TLabel", background=bg_color, foreground=text_color, font=("Segoe UI", 24, "bold"))
    style.configure("Header.TLabel", background=bg_color, foreground=text_color, font=("Segoe UI", 16, "bold"))
    style.configure("Tab.TLabel", background=bg_color, foreground=text_color, font=("Segoe UI", 12))
    
    # Configure button styles
    style.configure("TButton", background=bg_color, font=("Segoe UI", 10))
    
    # Modern blue button style (matches screenshot)
    style.configure("Blue.TButton", 
                   font=("Segoe UI", 12),
                   background=accent_color,
                   foreground="#ffffff",
                   padding=10)
    style.map("Blue.TButton",
             background=[("active", hover_color)],
             foreground=[("active", "#ffffff")])
    
    # Link button style
    style.configure("Link.TButton", 
                   font=("Segoe UI", 10),
                   background=bg_color,
                   foreground=accent_color,
                   borderwidth=0)
    style.map("Link.TButton",
             foreground=[("active", hover_color)])
    
    # Tab button style
    style.configure("Tab.TButton",
                    font=("Segoe UI", 12),
                    background=light_bg,
                    foreground=text_color,
                    padding=10,
                    borderwidth=0)
    style.map("Tab.TButton",
              background=[("active", bg_color)],
              foreground=[("active", accent_color)])
    
    # Active tab button style
    style.configure("ActiveTab.TButton",
                    font=("Segoe UI", 12, "bold"),
                    background=bg_color,
                    foreground=accent_color,
                    padding=10,
                    borderwidth=0)
    
    # Entry style
    style.configure("TEntry", font=("Segoe UI", 12))
    
    # Combobox style
    style.configure("TCombobox", font=("Segoe UI", 12))
    
    return style

def hash_password(password):
    """Create a hash of the password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    """Validate email format using regex"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def create_entry_with_label(parent, label_text, show=None, required=False):
    """Create a labeled entry field with optional required indicator"""
    # Create frame to hold label and entry
    frame = ttk.Frame(parent)
    frame.pack(fill='x', pady=(0, 10), anchor='w')
    
    # Add required asterisk if needed
    if required:
        label_text = f"{label_text}*:"
    else:
        label_text = f"{label_text}:"
    
    # Create label
    label = ttk.Label(frame, text=label_text, font=("Segoe UI", 11))
    label.pack(fill='x', pady=(0, 5), anchor='w')
    
    # Create entry
    entry = ttk.Entry(frame, font=("Segoe UI", 12), show=show)
    entry.pack(fill='x', ipady=5)
    
    return entry

def create_combobox_with_label(parent, label_text, values=None, required=False):
    """Create a labeled combobox with optional required indicator"""
    # Create frame to hold label and combobox
    frame = ttk.Frame(parent)
    frame.pack(fill='x', pady=(0, 10), anchor='w')
    
    # Add required asterisk if needed
    if required:
        label_text = f"{label_text}*:"
    else:
        label_text = f"{label_text}:"
    
    # Create label
    label = ttk.Label(frame, text=label_text, font=("Segoe UI", 11))
    label.pack(fill='x', pady=(0, 5), anchor='w')
    
    # Create variable and combobox
    var = tk.StringVar()
    combo = ttk.Combobox(frame, textvariable=var, values=values, font=("Segoe UI", 12), state="readonly")
    combo.pack(fill='x')
    
    return combo, var

def show_register_window(parent):
    """Show the multi-tab registration window based on screenshots"""
    register_window = tk.Toplevel(parent)
    register_window.title("Medical App Registration")
    register_window.geometry("600x600")
    register_window.transient(parent)
    register_window.grab_set()
    
    # Set window icon if available
    try:
        register_window.iconbitmap("icon.ico")
    except:
        pass
    
    # Main frame to hold everything
    main_frame = ttk.Frame(register_window, padding=0)
    main_frame.pack(expand=True, fill="both")
    
    # Tabs bar at the top
    tabs_frame = ttk.Frame(main_frame, padding=0)
    tabs_frame.pack(fill="x")
    
    # Create a canvas with scrollbar for scrollable content
    canvas = tk.Canvas(main_frame, highlightthickness=0)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    
    # Configure canvas to use scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Layout scrollbar and canvas
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
    
    # Content frame inside canvas (will contain the changing content)
    content_frame = ttk.Frame(canvas)
    
    # Create a window in the canvas to hold the content frame
    canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
    
    # Configure the canvas to resize with the window
    def configure_canvas(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        # Make sure content_frame width matches canvas width
        canvas.itemconfig(canvas_window, width=event.width-4)
    
    content_frame.bind("<Configure>", configure_canvas)
    
    # Configure the canvas to be resized with the window
    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)
    
    canvas.bind("<Configure>", on_canvas_configure)
    
    # Add mouse wheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    # Border frame with blue outline (matches screenshot)
    border_frame = ttk.Frame(content_frame, style="Card.TFrame", padding=20)
    border_frame.pack(expand=True, fill="both")
    
    # Dictionary to store all form data
    form_data = {}
    
    # Function to handle tab switching and content updating
    def show_tab(tab_index):
        # Update active tab visual status
        for i, btn in enumerate(tab_buttons):
            if i == tab_index:
                btn.configure(style="ActiveTab.TButton")
            else:
                btn.configure(style="Tab.TButton")
        
        # Clear current content
        for widget in border_frame.winfo_children():
            widget.destroy()
        
        # Create new content based on tab index
        if tab_index == 0:
            create_account_tab(border_frame, form_data)
        elif tab_index == 1:
            create_personal_tab(border_frame, form_data)
        elif tab_index == 2:
            create_medical_tab(border_frame, form_data)
        elif tab_index == 3:
            create_insurance_tab(border_frame, form_data)
    
    # Create tab buttons
    tab_names = ["Account Info", "Personal Info", "Medical Info", "Insurance & Em"]
    tab_buttons = []
    
    for i, name in enumerate(tab_names):
        style = "ActiveTab.TButton" if i == 0 else "Tab.TButton"
        tab_btn = ttk.Button(tabs_frame, text=name, style=style, command=lambda idx=i: show_tab(idx))
        tab_btn.pack(side="left", padx=2)
        tab_buttons.append(tab_btn)
    
    # Function to handle form submission
    def submit_registration():
        # Validate form data
        if not validate_registration(form_data):
            return
        
        try:
            # Connect to database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Insert user data
            hashed_password = hash_password(form_data.get('password', ''))
            
            cursor.execute(
                """INSERT INTO users 
                   (username, password, email, phone, full_name, registration_date) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    form_data.get('username', ''),
                    hashed_password,
                    form_data.get('email', ''),
                    form_data.get('phone', ''),
                    form_data.get('full_name', ''),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )
            
            # Get the new user ID
            user_id = cursor.lastrowid
            
            # Insert personal info
            cursor.execute(
                """INSERT INTO personal_info 
                   (user_id, dob, gender, blood_group, address, city, state, zip_code, country, 
                    allergies, chronic_illnesses) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    user_id,
                    form_data.get('dob', ''),
                    form_data.get('gender', ''),
                    form_data.get('blood_group', ''),
                    form_data.get('address', ''),
                    form_data.get('city', ''),
                    form_data.get('state', ''),
                    form_data.get('zip_code', ''),
                    form_data.get('country', ''),
                    form_data.get('allergies', ''),
                    form_data.get('chronic_illnesses', '')
                )
            )
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo(
                "Registration Successful", 
                "Your account has been created successfully. You can now log in with your credentials."
            )
            register_window.destroy()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Registration Error", "Username already exists. Please choose another username.")
        except Exception as e:
            messagebox.showerror("Registration Error", f"An error occurred: {str(e)}")
    
    def validate_registration(data):
        """Validate registration data"""
        # Check required account fields
        if not data.get('username') or not data.get('password') or not data.get('email'):
            messagebox.showerror("Validation Error", "Please fill all required fields in Account Info tab")
            return False
        
        # Check password match
        if data.get('password') != data.get('confirm_password'):
            messagebox.showerror("Validation Error", "Passwords do not match")
            return False
        
        # Check email format
        if not validate_email(data.get('email')):
            messagebox.showerror("Validation Error", "Please enter a valid email address")
            return False
        
        # Check required personal fields
        if not data.get('full_name'):
            messagebox.showerror("Validation Error", "Please fill all required fields in Personal Info tab")
            return False
        
        return True
    
    # Add buttons at the bottom (Cancel and Submit)
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill="x", pady=10, padx=20)
    
    # Spacer to push buttons to the right
    spacer = ttk.Frame(button_frame)
    spacer.pack(side="left", fill="x", expand=True)
    
    # Cancel button
    cancel_button = ttk.Button(
        button_frame,
        bg="#ffffff",
        fg="#000000",
        text="Cancel",
        command=register_window.destroy
    )
    cancel_button.pack(side="left", padx=(0, 10))
    
    # Submit button
    submit_button = ttk.Button(
        button_frame,
        text="Submit Registration",
        command=submit_registration
    )
    submit_button.pack(side="left")
    
    # Initialize with Account Info tab
    show_tab(0)
    
    # Center window on parent
    center_window(register_window)

def create_account_tab(parent, form_data):
    """Create the Account Info tab content"""
    # Title
    title_label = ttk.Label(parent, text="Create Your Account", font=("Segoe UI", 16, "bold"))
    title_label.pack(anchor="w", pady=(0, 20))
    
    # Username
    username_entry = create_entry_with_label(parent, "Username", required=True)
    if 'username' in form_data:
        username_entry.insert(0, form_data['username'])
    
    # Password
    password_entry = create_entry_with_label(parent, "Password", show="•", required=True)
    if 'password' in form_data:
        password_entry.insert(0, form_data['password'])
    
    # Confirm Password
    confirm_entry = create_entry_with_label(parent, "Confirm Password", show="•", required=True)
    if 'confirm_password' in form_data:
        confirm_entry.insert(0, form_data['confirm_password'])
    
    # Email
    email_entry = create_entry_with_label(parent, "Email", required=True)
    if 'email' in form_data:
        email_entry.insert(0, form_data['email'])
    
    # Phone Number
    phone_entry = create_entry_with_label(parent, "Phone Number", required=True)
    if 'phone' in form_data:
        phone_entry.insert(0, form_data['phone'])
    
    # Security Question
    security_combo, security_var = create_combobox_with_label(
        parent, 
        "Security Question", 
        values=["What is your favorite color?", "What was your first pet's name?", "What city were you born in?"],
        required=True
    )
    if 'security_question' in form_data:
        security_var.set(form_data['security_question'])
    
    # Security Answer
    security_answer = create_entry_with_label(parent, "Security Answer", required=True)
    if 'security_answer' in form_data:
        security_answer.insert(0, form_data['security_answer'])
    
    # Required fields note
    note_label = ttk.Label(
        parent,
        text="* Required fields",
        font=("Segoe UI", 9, "italic"),
        foreground="#666666"
    )
    note_label.pack(anchor="w", pady=(10, 0))
    
    # Update form data on tab change
    def save_data(*args):
        form_data['username'] = username_entry.get()
        form_data['password'] = password_entry.get()
        form_data['confirm_password'] = confirm_entry.get()
        form_data['email'] = email_entry.get()
        form_data['phone'] = phone_entry.get()
        form_data['security_question'] = security_var.get()
        form_data['security_answer'] = security_answer.get()
    
    # Bind save function to field changes
    parent.bind("<FocusOut>", save_data)

def create_personal_tab(parent, form_data):
    """Create the Personal Info tab content"""
    # Title
    title_label = ttk.Label(parent, text="Personal Information", font=("Segoe UI", 16, "bold"))
    title_label.pack(anchor="w", pady=(0, 20))
    
    # Full Name
    name_entry = create_entry_with_label(parent, "Full Name", required=True)
    if 'full_name' in form_data:
        name_entry.insert(0, form_data['full_name'])
    
    # Date of Birth
    dob_entry = create_entry_with_label(parent, "Date of Birth (DD-MM-YYYY)", required=True)
    if 'dob' in form_data:
        dob_entry.insert(0, form_data['dob'])
    
    # Gender
    gender_combo, gender_var = create_combobox_with_label(
        parent, 
        "Gender", 
        values=["Male", "Female", "Other"],
        required=True
    )
    if 'gender' in form_data:
        gender_var.set(form_data['gender'])
    
    # Marital Status
    marital_combo, marital_var = create_combobox_with_label(
        parent, 
        "Marital Status", 
        values=["Single", "Married", "Divorced", "Widowed"]
    )
    if 'marital_status' in form_data:
        marital_var.set(form_data['marital_status'])
    
    # Address frame
    address_frame = ttk.Frame(parent)
    address_frame.pack(fill='x', pady=(0, 10), anchor='w')
    
    address_label = ttk.Label(address_frame, text="Address*:", font=("Segoe UI", 11))
    address_label.pack(fill='x', pady=(0, 5), anchor='w')
    
    # Street Address
    street_label = ttk.Label(address_frame, text="Street Address*:", font=("Segoe UI", 10))
    street_label.pack(anchor="w")
    
    street_entry = ttk.Entry(address_frame, font=("Segoe UI", 12))
    street_entry.pack(fill='x', pady=(0, 10))
    
    if 'address' in form_data:
        street_entry.insert(0, form_data['address'])
    
    # City
    city_label = ttk.Label(address_frame, text="City*:", font=("Segoe UI", 10))
    city_label.pack(anchor="w")
    
    city_entry = ttk.Entry(address_frame, font=("Segoe UI", 12))
    city_entry.pack(fill='x', pady=(0, 10))
    
    if 'city' in form_data:
        city_entry.insert(0, form_data['city'])
    
    # State/Province
    state_label = ttk.Label(address_frame, text="State/Province*:", font=("Segoe UI", 10))
    state_label.pack(anchor="w")
    
    state_entry = ttk.Entry(address_frame, font=("Segoe UI", 12))
    state_entry.pack(fill='x', pady=(0, 10))
    
    if 'state' in form_data:
        state_entry.insert(0, form_data['state'])
    
    # ZIP/Postal Code
    zip_label = ttk.Label(address_frame, text="ZIP/Postal Code*:", font=("Segoe UI", 10))
    zip_label.pack(anchor="w")
    
    zip_entry = ttk.Entry(address_frame, font=("Segoe UI", 12))
    zip_entry.pack(fill='x', pady=(0, 10))
    
    if 'zip_code' in form_data:
        zip_entry.insert(0, form_data['zip_code'])
    
    # Country
    country_label = ttk.Label(address_frame, text="Country*:", font=("Segoe UI", 10))
    country_label.pack(anchor="w")
    
    country_var = tk.StringVar()
    country_combo = ttk.Combobox(
        address_frame, 
        textvariable=country_var,
        values=["United States", "Canada", "United Kingdom", "Australia", "India", "Other"],
        font=("Segoe UI", 12),
        state="readonly"
    )
    country_combo.pack(fill='x')
    
    if 'country' in form_data:
        country_var.set(form_data['country'])
    
    # Occupation
    occupation_entry = create_entry_with_label(parent, "Occupation")
    if 'occupation' in form_data:
        occupation_entry.insert(0, form_data['occupation'])
    
    # Preferred Language
    language_combo, language_var = create_combobox_with_label(
        parent, 
        "Preferred Language", 
        values=["English", "Spanish", "French", "German", "Chinese", "Other"]
    )
    if 'language' in form_data:
        language_var.set(form_data['language'])
    
    # Required fields note
    note_label = ttk.Label(
        parent,
        text="* Required fields",
        font=("Segoe UI", 9, "italic"),
        foreground="#666666"
    )
    note_label.pack(anchor="w", pady=(10, 0))
    
    # Update form data on tab change
    def save_data(*args):
        form_data['full_name'] = name_entry.get()
        form_data['dob'] = dob_entry.get()
        form_data['gender'] = gender_var.get()
        form_data['marital_status'] = marital_var.get()
        form_data['address'] = street_entry.get()
        form_data['city'] = city_entry.get()
        form_data['state'] = state_entry.get()
        form_data['zip_code'] = zip_entry.get()
        form_data['country'] = country_var.get()
        form_data['occupation'] = occupation_entry.get()
        form_data['language'] = language_var.get()
    
    # Bind save function to field changes
    parent.bind("<FocusOut>", save_data)

def create_medical_tab(parent, form_data):
    """Create the Medical Info tab content"""
    # Title
    title_label = ttk.Label(parent, text="Medical Information", font=("Segoe UI", 16, "bold"))
    title_label.pack(anchor="w", pady=(0, 20))
    
    # Height frame with unit selection
    height_frame = ttk.Frame(parent)
    height_frame.pack(fill='x', pady=(0, 10), anchor='w')
    
    height_label = ttk.Label(height_frame, text="Height:", font=("Segoe UI", 11))
    height_label.pack(side="left", padx=(0, 10))
    
    height_entry = ttk.Entry(height_frame, width=10, font=("Segoe UI", 12))
    height_entry.pack(side="left", padx=(0, 10))
    
    if 'height' in form_data:
        height_entry.insert(0, form_data['height'])
    
    height_unit_var = tk.StringVar(value="cm")
    height_unit = ttk.Combobox(
        height_frame,
        textvariable=height_unit_var,
        values=["cm", "in"],
        width=5,
        font=("Segoe UI", 12),
        state="readonly"
    )
    height_unit.pack(side="left")
    
    if 'height_unit' in form_data:
        height_unit_var.set(form_data['height_unit'])
    
    # Weight frame with unit selection
    weight_frame = ttk.Frame(parent)
    weight_frame.pack(fill='x', pady=(0, 10), anchor='w')
    
    weight_label = ttk.Label(weight_frame, text="Weight:", font=("Segoe UI", 11))
    weight_label.pack(side="left", padx=(0, 10))
    
    weight_entry = ttk.Entry(weight_frame, width=10, font=("Segoe UI", 12))
    weight_entry.pack(side="left", padx=(0, 10))
    
    if 'weight' in form_data:
        weight_entry.insert(0, form_data['weight'])
    
    weight_unit_var = tk.StringVar(value="kg")
    weight_unit = ttk.Combobox(
        weight_frame,
        textvariable=weight_unit_var,
        values=["kg", "lb"],
        width=5,
        font=("Segoe UI", 12),
        state="readonly"
    )
    weight_unit.pack(side="left")
    
    if 'weight_unit' in form_data:
        weight_unit_var.set(form_data['weight_unit'])
    
    # Blood Group
    blood_combo, blood_var = create_combobox_with_label(
        parent, 
        "Blood Group", 
        values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Don't Know"]
    )
    if 'blood_group' in form_data:
        blood_var.set(form_data['blood_group'])
    
    # Allergies
    allergies_label = ttk.Label(parent, text="Allergies:", font=("Segoe UI", 11))
    allergies_label.pack(fill='x', pady=(0, 5), anchor='w')
    
    allergies_entry = ttk.Entry(parent, font=("Segoe UI", 12))
    allergies_entry.pack(fill='x', pady=(0, 10))
    
    if 'allergies' in form_data:
        allergies_entry.insert(0, form_data['allergies'])
    
    # Chronic Illnesses
    chronic_label = ttk.Label(parent, text="Chronic Illnesses:", font=("Segoe UI", 11))
    chronic_label.pack(fill='x', pady=(0, 5), anchor='w')
    
    chronic_entry = ttk.Entry(parent, font=("Segoe UI", 12))
    chronic_entry.pack(fill='x', pady=(0, 10))
    
    if 'chronic_illnesses' in form_data:
        chronic_entry.insert(0, form_data['chronic_illnesses'])
    
    # Current Medications
    meds_label = ttk.Label(parent, text="Current Medications:", font=("Segoe UI", 11))
    meds_label.pack(fill='x', pady=(0, 5), anchor='w')
    
    meds_entry = ttk.Entry(parent, font=("Segoe UI", 12))
    meds_entry.pack(fill='x', pady=(0, 10))
    
    if 'medications' in form_data:
        meds_entry.insert(0, form_data['medications'])
    
    # Previous Surgeries
    surgeries_label = ttk.Label(parent, text="Previous Surgeries:", font=("Segoe UI", 11))
    surgeries_label.pack(fill='x', pady=(0, 5), anchor='w')
    
    surgeries_entry = ttk.Entry(parent, font=("Segoe UI", 12))
    surgeries_entry.pack(fill='x', pady=(0, 10))
    
    if 'surgeries' in form_data:
        surgeries_entry.insert(0, form_data['surgeries'])
    
    # Family Medical History
    history_label = ttk.Label(parent, text="Family Medical History:", font=("Segoe UI", 11))
    history_label.pack(fill='x', pady=(0, 5), anchor='w')
    
    history_entry = ttk.Entry(parent, font=("Segoe UI", 12))
    history_entry.pack(fill='x', pady=(0, 10))
    
    if 'family_history' in form_data:
        history_entry.insert(0, form_data['family_history'])
    
    # Update form data on tab change
    def save_data(*args):
        form_data['height'] = height_entry.get()
        form_data['height_unit'] = height_unit_var.get()
        form_data['weight'] = weight_entry.get()
        form_data['weight_unit'] = weight_unit_var.get()
        form_data['blood_group'] = blood_var.get()
        form_data['allergies'] = allergies_entry.get()
        form_data['chronic_illnesses'] = chronic_entry.get()
        form_data['medications'] = meds_entry.get()
        form_data['surgeries'] = surgeries_entry.get()
        form_data['family_history'] = history_entry.get()
    
    # Bind save function to field changes
    parent.bind("<FocusOut>", save_data)

def create_insurance_tab(parent, form_data):
    """Create the Insurance & Emergency tab content"""
    # Title
    title_label = ttk.Label(parent, text="Insurance & Emergency Contacts", font=("Segoe UI", 16, "bold"))
    title_label.pack(anchor="w", pady=(0, 20))
    
    # Insurance section
    insurance_label = ttk.Label(parent, text="Insurance Information", font=("Segoe UI", 14, "bold"))
    insurance_label.pack(anchor="w", pady=(0, 10))
    
    # Insurance Provider
    provider_entry = create_entry_with_label(parent, "Insurance Provider", required=True)
    if 'insurance_provider' in form_data:
        provider_entry.insert(0, form_data['insurance_provider'])
    
    # Policy Number
    policy_entry = create_entry_with_label(parent, "Policy Number", required=True)
    if 'policy_number' in form_data:
        policy_entry.insert(0, form_data['policy_number'])
    
    # Group Number
    group_entry = create_entry_with_label(parent, "Group Number")
    if 'group_number' in form_data:
        group_entry.insert(0, form_data['group_number'])
    
    # Insurance Contact
    ins_contact_entry = create_entry_with_label(parent, "Insurance Contact Number")
    if 'insurance_contact' in form_data:
        ins_contact_entry.insert(0, form_data['insurance_contact'])

    # Emergency contacts section
    emergency_label = ttk.Label(parent, text="Emergency Contacts", font=("Segoe UI", 14, "bold"))
    emergency_label.pack(anchor="w", pady=(20, 10))
    
    # Primary Contact Name
    primary_name_entry = create_entry_with_label(parent, "Primary Contact Name", required=True)
    if 'emergency_name' in form_data:
        primary_name_entry.insert(0, form_data['emergency_name'])
    
    # Relationship
    relation_combo, relation_var = create_combobox_with_label(
        parent, 
        "Relationship", 
        values=["Spouse", "Parent", "Child", "Sibling", "Friend", "Other"],
        required=True
    )
    if 'emergency_relation' in form_data:
        relation_var.set(form_data['emergency_relation'])
    
    # Contact Number
    contact_entry = create_entry_with_label(parent, "Contact Number", required=True)
    if 'emergency_contact' in form_data:
        contact_entry.insert(0, form_data['emergency_contact'])
    
    # Secondary Contact (optional)
    secondary_label = ttk.Label(parent, text="Secondary Emergency Contact (Optional)", 
                              font=("Segoe UI", 11, "bold"))
    secondary_label.pack(anchor="w", pady=(10, 5))
    
    # Secondary Contact Name
    secondary_name_entry = create_entry_with_label(parent, "Contact Name")
    if 'emergency_name2' in form_data:
        secondary_name_entry.insert(0, form_data['emergency_name2'])
    
    # Secondary Relationship
    secondary_relation_combo, secondary_relation_var = create_combobox_with_label(
        parent, 
        "Relationship", 
        values=["Spouse", "Parent", "Child", "Sibling", "Friend", "Other"]
    )
    if 'emergency_relation2' in form_data:
        secondary_relation_var.set(form_data['emergency_relation2'])
    
    # Secondary Contact Number
    secondary_contact_entry = create_entry_with_label(parent, "Contact Number")
    if 'emergency_contact2' in form_data:
        secondary_contact_entry.insert(0, form_data['emergency_contact2'])
    
    # Required fields note
    note_label = ttk.Label(
        parent,
        text="* Required fields",
        font=("Segoe UI", 9, "italic"),
        foreground="#666666"
    )
    note_label.pack(anchor="w", pady=(10, 0))
    
    # Update form data on tab change
    def save_data(*args):
        form_data['insurance_provider'] = provider_entry.get()
        form_data['policy_number'] = policy_entry.get()
        form_data['group_number'] = group_entry.get()
        form_data['insurance_contact'] = ins_contact_entry.get()
        form_data['emergency_name'] = primary_name_entry.get()
        form_data['emergency_relation'] = relation_var.get()
        form_data['emergency_contact'] = contact_entry.get()
        form_data['emergency_name2'] = secondary_name_entry.get()
        form_data['emergency_relation2'] = secondary_relation_var.get()
        form_data['emergency_contact2'] = secondary_contact_entry.get()
    
    # Bind save function to field changes
    parent.bind("<FocusOut>", save_data)

def create_personal_tab(parent, form_data):
    """Create the Personal Info tab content"""
    # Title
    title_label = ttk.Label(parent, text="Personal Information", font=("Segoe UI", 16, "bold"))
    title_label.pack(anchor="w", pady=(0, 20))
    
    # Full Name
    name_entry = create_entry_with_label(parent, "Full Name", required=True)
    if 'full_name' in form_data:
        name_entry.insert(0, form_data['full_name'])
    
    # Date of Birth
    dob_entry = create_entry_with_label(parent, "Date of Birth (DD-MM-YYYY)", required=True)
    if 'dob' in form_data:
        dob_entry.insert(0, form_data['dob'])
    
    # Gender
    gender_combo, gender_var = create_combobox_with_label(
        parent, 
        "Gender", 
        values=["Male", "Female", "Other"],
        required=True
    )
    if 'gender' in form_data:
        gender_var.set(form_data['gender'])
    
    # Marital Status
    marital_combo, marital_var = create_combobox_with_label(
        parent, 
        "Marital Status", 
        values=["Single", "Married", "Divorced", "Widowed"]
    )
    if 'marital_status' in form_data:
        marital_var.set(form_data['marital_status'])
    
    # Address frame
    address_frame = ttk.Frame(parent)
    address_frame.pack(fill='x', pady=(0, 10), anchor='w')
    
    address_label = ttk.Label(address_frame, text="Address*:", font=("Segoe UI", 11))
    address_label.pack(fill='x', pady=(0, 5), anchor='w')
    
    # Street Address
    street_label = ttk.Label(address_frame, text="Street Address*:", font=("Segoe UI", 10))
    street_label.pack(anchor="w")
    
    street_entry = ttk.Entry(address_frame, font=("Segoe UI", 12))
    street_entry.pack(fill='x', pady=(0, 10))
    
    if 'address' in form_data:
        street_entry.insert(0, form_data['address'])
    
    # City
    city_label = ttk.Label(address_frame, text="City*:", font=("Segoe UI", 10))
    city_label.pack(anchor="w")
    
    city_entry = ttk.Entry(address_frame, font=("Segoe UI", 12))
    city_entry.pack(fill='x', pady=(0, 10))
    
    if 'city' in form_data:
        city_entry.insert(0, form_data['city'])
    
    # State/Province
    state_label = ttk.Label(address_frame, text="State/Province*:", font=("Segoe UI", 10))
    state_label.pack(anchor="w")
    
    state_entry = ttk.Entry(address_frame, font=("Segoe UI", 12))
    state_entry.pack(fill='x', pady=(0, 10))
    
    if 'state' in form_data:
        state_entry.insert(0, form_data['state'])
    
    # ZIP/Postal Code
    zip_label = ttk.Label(address_frame, text="ZIP/Postal Code*:", font=("Segoe UI", 10))
    zip_label.pack(anchor="w")
    
    zip_entry = ttk.Entry(address_frame, font=("Segoe UI", 12))
    zip_entry.pack(fill='x', pady=(0, 10))
    
    if 'zip_code' in form_data:
        zip_entry.insert(0, form_data['zip_code'])
    
    # Country
    country_label = ttk.Label(address_frame, text="Country*:", font=("Segoe UI", 10))
    country_label.pack(anchor="w")
    
    country_var = tk.StringVar()
    country_combo = ttk.Combobox(
        address_frame, 
        textvariable=country_var,
        values=["United States", "Canada", "United Kingdom", "Australia", "India", "Other"],
        font=("Segoe UI", 12),
        state="readonly"
    )
    country_combo.pack(fill='x')
    
    if 'country' in form_data:
        country_var.set(form_data['country'])
    
    # Occupation
    occupation_entry = create_entry_with_label(parent, "Occupation")
    if 'occupation' in form_data:
        occupation_entry.insert(0, form_data['occupation'])
    
    # Preferred Language
    language_combo, language_var = create_combobox_with_label(
        parent, 
        "Preferred Language", 
        values=["English", "Spanish", "French", "German", "Chinese", "Other"]
    )
    if 'language' in form_data:
        language_var.set(form_data['language'])
    
    # Required fields note
    note_label = ttk.Label(
        parent,
        text="* Required fields",
        font=("Segoe UI", 9, "italic"),
        foreground="#666666"
    )
    note_label.pack(anchor="w", pady=(10, 0))
    
    # Update form data on tab change
    def save_data(*args):
        form_data['full_name'] = name_entry.get()
        form_data['dob'] = dob_entry.get()
        form_data['gender'] = gender_var.get()
        form_data['marital_status'] = marital_var.get()
        form_data['address'] = street_entry.get()
        form_data['city'] = city_entry.get()
        form_data['state'] = state_entry.get()
        form_data['zip_code'] = zip_entry.get()
        form_data['country'] = country_var.get()
        form_data['occupation'] = occupation_entry.get()
        form_data['language'] = language_var.get()
    
    # Bind save function to field changes
    parent.bind("<FocusOut>", save_data)

def create_medical_tab(parent, form_data):
    """Create the Medical Info tab content"""
    # Title
    title_label = ttk.Label(parent, text="Medical Information", font=("Segoe UI", 16, "bold"))
    title_label.pack(anchor="w", pady=(0, 20))
    
    # Height frame with unit selection
    height_frame = ttk.Frame(parent)
    height_frame.pack(fill='x', pady=(0, 10), anchor='w')
    
    height_label = ttk.Label(height_frame, text="Height:", font=("Segoe UI", 11))
    height_label.pack(side="left", padx=(0, 10))
    
    height_entry = ttk.Entry(height_frame, width=10, font=("Segoe UI", 12))
    height_entry.pack(side="left", padx=(0, 10))
    
    if 'height' in form_data:
        height_entry.insert(0, form_data['height'])
    
    height_unit_var = tk.StringVar(value="cm")
    height_unit = ttk.Combobox(
        height_frame,
        textvariable=height_unit_var,
        values=["cm", "in"],
        width=5,
        font=("Segoe UI", 12),
        state="readonly"
    )
    height_unit.pack(side="left")
    
    if 'height_unit' in form_data:
        height_unit_var.set(form_data['height_unit'])
    
    # Weight frame with unit selection
    weight_frame = ttk.Frame(parent)
    weight_frame.pack(fill='x', pady=(0, 10), anchor='w')
    
    weight_label = ttk.Label(weight_frame, text="Weight:", font=("Segoe UI", 11))
    weight_label.pack(side="left", padx=(0, 10))
    
    weight_entry = ttk.Entry(weight_frame, width=10, font=("Segoe UI", 12))
    weight_entry.pack(side="left", padx=(0, 10))
    
    if 'weight' in form_data:
        weight_entry.insert(0, form_data['weight'])
    
    weight_unit_var = tk.StringVar(value="kg")
    weight_unit = ttk.Combobox(
        weight_frame,
        textvariable=weight_unit_var,
        values=["kg", "lb"],
        width=5,
        font=("Segoe UI", 12),
        state="readonly"
    )
    weight_unit.pack(side="left")
    
    if 'weight_unit' in form_data:
        weight_unit_var.set(form_data['weight_unit'])
    
    # Blood Group
    blood_combo, blood_var = create_combobox_with_label(
        parent, 
        "Blood Group", 
        values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Don't Know"]
    )
    if 'blood_group' in form_data:
        blood_var.set(form_data['blood_group'])
    
    # Allergies
    allergies_label = ttk.Label(parent, text="Allergies:", font=("Segoe UI", 11))
    allergies_label.pack(fill='x', pady=(0, 5), anchor='w')
    
    allergies_entry = ttk.Entry(parent, font=("Segoe UI", 12))
    allergies_entry.pack(fill='x', pady=(0, 10))
    
    if 'allergies' in form_data:
        allergies_entry.insert(0, form_data['allergies'])
    
    # Chronic Illnesses
    chronic_label = ttk.Label(parent, text="Chronic Illnesses:", font=("Segoe UI", 11))
    chronic_label.pack(fill='x', pady=(0, 5), anchor='w')
    
    chronic_entry = ttk.Entry(parent, font=("Segoe UI", 12))
    chronic_entry.pack(fill='x', pady=(0, 10))
    
    if 'chronic_illnesses' in form_data:
        chronic_entry.insert(0, form_data['chronic_illnesses'])
    
    # Current Medications
    meds_label = ttk.Label(parent, text="Current Medications:", font=("Segoe UI", 11))
    meds_label.pack(fill='x', pady=(0, 5), anchor='w')
    
    meds_entry = ttk.Entry(parent, font=("Segoe UI", 12))
    meds_entry.pack(fill='x', pady=(0, 10))
    
    if 'medications' in form_data:
        meds_entry.insert(0, form_data['medications'])
    
    # Previous Surgeries
    surgeries_label = ttk.Label(parent, text="Previous Surgeries:", font=("Segoe UI", 11))
    surgeries_label.pack(fill='x', pady=(0, 5), anchor='w')
    
    surgeries_entry = ttk.Entry(parent, font=("Segoe UI", 12))
    surgeries_entry.pack(fill='x', pady=(0, 10))
    
    if 'surgeries' in form_data:
        surgeries_entry.insert(0, form_data['surgeries'])
    
    # Family Medical History
    history_label = ttk.Label(parent, text="Family Medical History:", font=("Segoe UI", 11))
    history_label.pack(fill='x', pady=(0, 5), anchor='w')
    
    history_entry = ttk.Entry(parent, font=("Segoe UI", 12))
    history_entry.pack(fill='x', pady=(0, 10))
    
    if 'family_history' in form_data:
        history_entry.insert(0, form_data['family_history'])
    
    # Update form data on tab change
    def save_data(*args):
        form_data['height'] = height_entry.get()
        form_data['height_unit'] = height_unit_var.get()
        form_data['weight'] = weight_entry.get()
        form_data['weight_unit'] = weight_unit_var.get()
        form_data['blood_group'] = blood_var.get()
        form_data['allergies'] = allergies_entry.get()
        form_data['chronic_illnesses'] = chronic_entry.get()
        form_data['medications'] = meds_entry.get()
        form_data['surgeries'] = surgeries_entry.get()
        form_data['family_history'] = history_entry.get()
    
    # Bind save function to field changes
    parent.bind("<FocusOut>", save_data)

def create_insurance_tab(parent, form_data):
    """Create the Insurance & Emergency tab content"""
    # Title
    title_label = ttk.Label(parent, text="Insurance & Emergency Contacts", font=("Segoe UI", 16, "bold"))
    title_label.pack(anchor="w", pady=(0, 20))
    
    # Insurance section
    insurance_label = ttk.Label(parent, text="Insurance Information", font=("Segoe UI", 14, "bold"))
    insurance_label.pack(anchor="w", pady=(0, 10))
    
    # Insurance Provider
    provider_entry = create_entry_with_label(parent, "Insurance Provider", required=True)
    if 'insurance_provider' in form_data:
        provider_entry.insert(0, form_data['insurance_provider'])
    
    # Policy Number
    policy_entry = create_entry_with_label(parent, "Policy Number", required=True)
    if 'policy_number' in form_data:
        policy_entry.insert(0, form_data['policy_number'])
    
    # Group Number
    group_entry = create_entry_with_label(parent, "Group Number")
    if 'group_number' in form_data:
        group_entry.insert(0, form_data['group_number'])
    
    # Insurance Contact
    ins_contact_entry = create_entry_with_label(parent, "Insurance Contact Number")
    if 'insurance_contact' in form_data:
        ins_contact_entry.insert(0, form_data['insurance_contact'])

    # Emergency contacts section
    emergency_label = ttk.Label(parent, text="Emergency Contacts", font=("Segoe UI", 14, "bold"))
    emergency_label.pack(anchor="w", pady=(20, 10))
    
    # Primary Contact Name
    primary_name_entry = create_entry_with_label(parent, "Primary Contact Name", required=True)
    if 'emergency_name' in form_data:
        primary_name_entry.insert(0, form_data['emergency_name'])
    
    # Relationship
    relation_combo, relation_var = create_combobox_with_label(
        parent, 
        "Relationship", 
        values=["Spouse", "Parent", "Child", "Sibling", "Friend", "Other"],
        required=True
    )
    if 'emergency_relation' in form_data:
        relation_var.set(form_data['emergency_relation'])
    
    # Contact Number
    contact_entry = create_entry_with_label(parent, "Contact Number", required=True)
    if 'emergency_contact' in form_data:
        contact_entry.insert(0, form_data['emergency_contact'])
    
    # Secondary Contact (optional)
    secondary_label = ttk.Label(parent, text="Secondary Emergency Contact (Optional)", 
                              font=("Segoe UI", 11, "bold"))
    secondary_label.pack(anchor="w", pady=(10, 5))
    
    # Secondary Contact Name
    secondary_name_entry = create_entry_with_label(parent, "Contact Name")
    if 'emergency_name2' in form_data:
        secondary_name_entry.insert(0, form_data['emergency_name2'])
    
    # Secondary Relationship
    secondary_relation_combo, secondary_relation_var = create_combobox_with_label(
        parent, 
        "Relationship", 
        values=["Spouse", "Parent", "Child", "Sibling", "Friend", "Other"]
    )
    if 'emergency_relation2' in form_data:
        secondary_relation_var.set(form_data['emergency_relation2'])
    
    # Secondary Contact Number
    secondary_contact_entry = create_entry_with_label(parent, "Contact Number")
    if 'emergency_contact2' in form_data:
        secondary_contact_entry.insert(0, form_data['emergency_contact2'])
    
    # Required fields note
    note_label = ttk.Label(
        parent,
        text="* Required fields",
        font=("Segoe UI", 9, "italic"),
        foreground="#666666"
    )
    note_label.pack(anchor="w", pady=(10, 0))
    
    # Update form data on tab change
    def save_data(*args):
        form_data['insurance_provider'] = provider_entry.get()
        form_data['policy_number'] = policy_entry.get()
        form_data['group_number'] = group_entry.get()
        form_data['insurance_contact'] = ins_contact_entry.get()
        form_data['emergency_name'] = primary_name_entry.get()
        form_data['emergency_relation'] = relation_var.get()
        form_data['emergency_contact'] = contact_entry.get()
        form_data['emergency_name2'] = secondary_name_entry.get()
        form_data['emergency_relation2'] = secondary_relation_var.get()
        form_data['emergency_contact2'] = secondary_contact_entry.get()
    
    # Bind save function to field changes
    parent.bind("<FocusOut>", save_data)

def show_register_window(parent):
    """Show the registration window"""
    register_window = tk.Toplevel(parent)
    register_window.title("Medical Assistant - Register")
    register_window.geometry("600x600")
    register_window.transient(parent)  # Set as child of parent
    register_window.grab_set()  # Make modal
    
    # Set window icon if available
    try:
        register_window.iconbitmap("icon.ico")
    except:
        pass
    
    # Main frame
    main_frame = ttk.Frame(register_window, padding=30)
    main_frame.pack(expand=True, fill="both")
    
    # Title
    title_label = ttk.Label(main_frame, text="Register New Account", style="Title.TLabel")
    title_label.pack(pady=(0, 20))
    
    # Create registration form
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill="both", expand=True)
    
    # Username field
    username_label = ttk.Label(form_frame, text="Username*:", font=("Segoe UI", 11))
    username_label.pack(fill='x', pady=(0, 5), anchor='w')
    
    username_entry = ttk.Entry(form_frame, font=("Segoe UI", 12))
    username_entry.pack(fill='x', pady=(0, 15), ipady=5)
    
    # Email field
    email_label = ttk.Label(form_frame, text="Email*:", font=("Segoe UI", 11))
    email_label.pack(fill='x', pady=(0, 5), anchor='w')
    
    email_entry = ttk.Entry(form_frame, font=("Segoe UI", 12))
    email_entry.pack(fill='x', pady=(0, 15), ipady=5)
    
    # Full name field
    name_label = ttk.Label(form_frame, text="Full Name*:", font=("Segoe UI", 11))
    name_label.pack(fill='x', pady=(0, 5), anchor='w')
    
    name_entry = ttk.Entry(form_frame, font=("Segoe UI", 12))
    name_entry.pack(fill='x', pady=(0, 15), ipady=5)
    
    # Phone number field
    phone_label = ttk.Label(form_frame, text="Phone Number:", font=("Segoe UI", 11))
    phone_label.pack(fill='x', pady=(0, 5), anchor='w')
    
    phone_entry = ttk.Entry(form_frame, font=("Segoe UI", 12))
    phone_entry.pack(fill='x', pady=(0, 15), ipady=5)
    
    # Password field
    password_label = ttk.Label(form_frame, text="Password*:", font=("Segoe UI", 11))
    password_label.pack(fill='x', pady=(0, 5), anchor='w')
    
    password_entry = ttk.Entry(form_frame, show="•", font=("Segoe UI", 12))
    password_entry.pack(fill='x', pady=(0, 15), ipady=5)
    
    # Confirm password field
    confirm_label = ttk.Label(form_frame, text="Confirm Password*:", font=("Segoe UI", 11))
    confirm_label.pack(fill='x', pady=(0, 5), anchor='w')
    
    confirm_entry = ttk.Entry(form_frame, show="•", font=("Segoe UI", 12))
    confirm_entry.pack(fill='x', pady=(0, 15), ipady=5)
    
    # Error message (hidden initially)
    error_var = tk.StringVar()
    error_label = ttk.Label(form_frame, textvariable=error_var, foreground="red", font=("Segoe UI", 10))
    error_label.pack(pady=(0, 10))
    
    # Function to handle registration
    def register():
        username = username_entry.get().strip()
        email = email_entry.get().strip()
        full_name = name_entry.get().strip()
        phone = phone_entry.get().strip()
        password = password_entry.get()
        confirm = confirm_entry.get()
        
        # Validate inputs
        if not username or not email or not full_name or not password or not confirm:
            error_var.set("Required fields (*) cannot be empty")
            return
        
        if not validate_email(email):
            error_var.set("Please enter a valid email address")
            return
        
        if password != confirm:
            error_var.set("Passwords do not match")
            return
        
        if len(password) < 6:
            error_var.set("Password must be at least 6 characters long")
            return
        
        # Check if username exists
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                error_var.set("Username already exists")
                conn.close()
                return
            
            # Insert new user
            hashed_password = hash_password(password)
            cursor.execute(
                """INSERT INTO users 
                   (username, password, email, phone, full_name, registration_date) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    username,
                    hashed_password,
                    email,
                    phone,
                    full_name,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )
            
            conn.commit()
            conn.close()
            
            # Show success message
            messagebox.showinfo(
                "Registration Successful", 
                "Your account has been created successfully. You can now login with your credentials."
            )
            register_window.destroy()
            
        except Exception as e:
            error_var.set(f"Error: {str(e)}")
    
    # Required fields note
    note_label = ttk.Label(
        form_frame,
        text="Fields marked with * are required",
        font=("Segoe UI", 9, "italic"),
        foreground="#666666"
    )
    note_label.pack(pady=5)
    
    # Buttons
    button_frame = ttk.Frame(form_frame)
    button_frame.pack(fill='x', pady=(10, 0))
    
    register_button = tk.Button(
        button_frame,
        bg="#ffffff",
        fg="#000000",
        text="Register",
        command=register,
        
    )
    register_button.pack(side="left", padx=(0, 10), ipady=5, ipadx=10)
    
    cancel_button = tk.Button(
        button_frame,
        bg="#ffffff",
        fg="#000000",
        text="Cancel",
        command=register_window.destroy
    )
    cancel_button.pack(side="left", ipady=5, ipadx=10)
    
    # Center window on parent
    center_window(register_window)

def show_forgot_password_window(parent):
    """Show the forgot password window"""
    forgot_window = tk.Toplevel(parent)
    forgot_window.title("Medical Assistant - Forgot Password")
    forgot_window.geometry("600x400")
    forgot_window.transient(parent)  # Set as child of parent
    forgot_window.grab_set()  # Make modal
    
    # Set window icon if available
    try:
        forgot_window.iconbitmap("icon.ico")
    except:
        pass
    
    # Main frame
    main_frame = ttk.Frame(forgot_window, padding=30)
    main_frame.pack(expand=True, fill="both")
    
    # Title
    title_label = ttk.Label(main_frame,text="Reset Password")
    title_label.pack(pady=(0, 20))
    
    # Instructions
    instructions = ttk.Label(
        main_frame, 
        text="Please enter your username and email address to reset your password.",
        wraplength=500,
        font=("Segoe UI", 11)
    )
    instructions.pack(pady=(0, 20))
    
    # Username field
    username_label = ttk.Label(main_frame, text="Username:", font=("Segoe UI", 11))
    username_label.pack(fill='x', pady=(0, 5), anchor='w')
    
    username_entry = ttk.Entry(main_frame, font=("Segoe UI", 12))
    username_entry.pack(fill='x', pady=(0, 15), ipady=5)
    
    # Email field
    email_label = ttk.Label(main_frame, text="Email:", font=("Segoe UI", 11))
    email_label.pack(fill='x', pady=(0, 5), anchor='w')
    
    email_entry = ttk.Entry(main_frame, font=("Segoe UI", 12))
    email_entry.pack(fill='x', pady=(0, 20), ipady=5)
    
    # Error message (hidden initially)
    error_var = tk.StringVar()
    error_label = ttk.Label(main_frame, textvariable=error_var, foreground="red", font=("Segoe UI", 10))
    error_label.pack(pady=(0, 10))
    
    # Function to handle password reset
    def reset_password():
        username = username_entry.get().strip()
        email = email_entry.get().strip()
        
        if not username or not email:
            error_var.set("Please enter both username and email")
            return
        
        if not validate_email(email):
            error_var.set("Please enter a valid email address")
            return
        
        # Check if user exists with this email
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id FROM users WHERE username = ? AND email = ?",
                (username, email)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                # Generate new random password (in a real app, send email with reset link)
                import random
                import string
                new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                
                # Update password in database
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                hashed_password = hash_password(new_password)
                cursor.execute(
                    "UPDATE users SET password = ? WHERE username = ?",
                    (hashed_password, username)
                )
                
                conn.commit()
                conn.close()
                
                # Show success message with new password
                messagebox.showinfo(
                    "Password Reset", 
                    f"Your password has been reset. Your new password is:\n\n{new_password}\n\nPlease login with this password and change it immediately."
                )
                forgot_window.destroy()
            else:
                error_var.set("No matching account found with this username and email")
        except Exception as e:
            error_var.set(f"Error: {str(e)}")
    
    # Buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill='x', pady=(10, 0))
    
    reset_button = tk.Button(
        button_frame,
        bg="#ffffff",
        fg="#000000",
        text="Reset Password",
        command=reset_password,
        
    )
    reset_button.pack(side="left", padx=(0, 10), ipady=5, ipadx=10)
    
    cancel_button = tk.Button(
        button_frame,
        bg="#ffffff",
        fg="#000000",
        text="Cancel",
        command=forgot_window.destroy
    )
    cancel_button.pack(side="left", ipady=5, ipadx=10)
    
    # Center window on parent
    center_window(forgot_window)

def show_login_window():
    """Show the modern login window matching the screenshot"""
    login_window = tk.Tk()
    login_window.title("Medical Assistant - Login")
    login_window.geometry("800x600")
    
    # Set window icon if available
    try:
        login_window.iconbitmap("icon.ico")
    except:
        pass
    
    # Setup styles
    setup_styles()
    
    # Main frame
    main_frame = ttk.Frame(login_window, padding=80)
    main_frame.pack(expand=True, fill="both", padx=150, pady=100)
    
    # Title - aligned with screenshot
    title_label = ttk.Label(
        main_frame, 
        text="Medical Assistant", 
        style="Title.TLabel"
    )
    title_label.pack(pady=(0, 40))
    
    # Username field
    username_label = ttk.Label(main_frame, text="Username", font=("Segoe UI", 11))
    username_label.pack(fill='x', pady=(0, 5), anchor='w')
    
    username_entry = ttk.Entry(main_frame, font=("Segoe UI", 12))
    username_entry.pack(fill='x', pady=(0, 25), ipady=8)
    
    # Password field
    password_label = ttk.Label(main_frame, text="Password", font=("Segoe UI", 11))
    password_label.pack(fill='x', pady=(0, 5), anchor='w')
    
    password_entry = ttk.Entry(main_frame, show="•", font=("Segoe UI", 12))
    password_entry.pack(fill='x', pady=(0, 25), ipady=8)
    
    # Error message (hidden initially)
    error_var = tk.StringVar()
    error_label = ttk.Label(main_frame, textvariable=error_var, foreground="red", font=("Segoe UI", 10))
    error_label.pack(pady=(0, 10))
    
    # Login function
    def login():
        username = username_entry.get().strip()
        password = password_entry.get()
        
        if not username or not password:
            error_var.set("Please enter both username and password")
            return
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get stored password
            cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            
            if result:
                stored_password = result[0]
                
                # Check password (allow plain text for testing)
                if stored_password == hash_password(password) or stored_password == password:
                    conn.close()
                    login_window.destroy()
                    
                    # Import here to avoid circular imports
                    from main import create_main_window
                    create_main_window(username)
                    return
            
            # If we get here, login failed
            error_var.set("Invalid username or password")
            conn.close()
            
        except Exception as e:
            error_var.set(f"Error: {str(e)}")
            
            # For testing - allow any login if database not available
            if not os.path.exists(DB_PATH):
                login_window.destroy()
                from main import create_main_window
                create_main_window(username)
    
    # Login button
    login_button = tk.Button(
        main_frame,
        bg="#FFFFFF",
        fg="#000000",
        text="Login",
        command=login,
        
    )
    login_button.pack(fill='x', pady=(10, 20), ipady=8)
    
    # Additional buttons frame
    links_frame = ttk.Frame(main_frame)
    links_frame.pack(fill='x', pady=5)
    
    # Register link
    register_button = tk.Button(
        links_frame,
        bg="#FFFFFF",
        fg="#000000",
        text="Register New Account",
        command=lambda: show_register_window(login_window),
        
    )
    register_button.pack(side="left", pady=5)
    
    # Forgot password link
    forgot_button = tk.Button(
        links_frame,
        bg="#FFFFFF",
        fg="#000000",
        text="Forgot Password?",
        command=lambda: show_forgot_password_window(login_window),
        
    )
    forgot_button.pack(side="right", pady=5)
    
    # Bind enter key to login
    login_window.bind("<Return>", lambda event: login())
    
    # For testing, pre-fill with test account
    username_entry.insert(0, "test")
    password_entry.insert(0, "test123")
    
    # Center on screen
    center_window(login_window)
    
    login_window.mainloop()

if __name__ == "__main__":
    # Run the login window if script is executed directly
    show_login_window()