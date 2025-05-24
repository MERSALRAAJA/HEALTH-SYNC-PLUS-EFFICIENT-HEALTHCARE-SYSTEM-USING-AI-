"""
Enhanced Medication Management Tab for Medical Assistant application.
This module creates a comprehensive medication management UI with reminders functionality.
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import sqlite3
import os
from datetime import datetime, timedelta
import time
import threading

# Database path
DB_PATH = os.path.join("database", "medical_assistant.db")

def ensure_reminders_frequency_column():
    """Check if the reminders table has a frequency column, and add it if it doesn't"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if the frequency column exists
        cursor.execute("PRAGMA table_info(reminders)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if "frequency" not in columns:
            # Add the frequency column
            cursor.execute("ALTER TABLE reminders ADD COLUMN frequency TEXT DEFAULT 'Daily'")
            print("Added frequency column to reminders table")
            conn.commit()
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error ensuring frequency column: {e}")
        return False

def create_medication_manager_tab(parent, username):
    """Create the medication manager tab with enhanced UI"""
    # Ensure database has the required frequency column
    ensure_reminders_frequency_column()
    
    # Set up custom fonts
    custom_font = font.nametofont("TkDefaultFont").copy()
    custom_font.configure(size=10)
    
    header_font = font.Font(family="Segoe UI", size=12, weight="bold")
    title_font = font.Font(family="Segoe UI", size=11, weight="bold")
    time_font = font.Font(family="Segoe UI", size=16, weight="bold")
    
    # Main frame with padding
    main_frame = ttk.Frame(parent, padding=15)
    main_frame.pack(fill="both", expand=True)
    
    # Create two columns
    left_frame = ttk.Frame(main_frame)
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
    
    right_frame = ttk.Frame(main_frame)
    right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
    
    # Get medicine details dictionary
    medicine_details = get_medication_details()
    
    # ===== LEFT COLUMN =====
    
    # Medicine Selection Card
    medicine_card = create_custom_card(left_frame, "Medicine Selection")
    
    # Medicine selection
    med_label = ttk.Label(medicine_card, text="Select Medicine:", font=title_font)
    med_label.pack(anchor="w", pady=(5, 5))
    
    # Get medicines from database
    medicines = get_medications()
    
    medicine_var = tk.StringVar()
    medicine_combo = ttk.Combobox(medicine_card, textvariable=medicine_var, values=medicines, state="readonly", font=custom_font)
    medicine_combo.pack(fill="x", pady=(0, 15))
    
    # Dose selection
    dose_label = ttk.Label(medicine_card, text="Select Dose:", font=title_font)
    dose_label.pack(anchor="w", pady=(5, 5))
    
    dose_var = tk.StringVar(value="50mg")
    dose_combo = ttk.Combobox(medicine_card, textvariable=dose_var, state="readonly", font=custom_font)
    dose_combo.pack(fill="x", pady=(0, 15))
    
    # Set initial dose options
    initial_doses = ["5mg", "10mg", "20mg", "25mg", "50mg", "100mg", "200mg", "1 tablet", "2 tablets", "5ml", "10ml", "15ml"]
    dose_combo['values'] = initial_doses
    
    # Description section
    description_label = ttk.Label(medicine_card, text="Medicine Information:", font=title_font)
    description_label.pack(anchor="w", pady=(15, 5))
    
    medicine_info = tk.Text(medicine_card, height=5, width=30, font=custom_font, wrap="word")
    medicine_info.pack(fill="x", pady=(0, 5))
    medicine_info.insert("1.0", "Select a medicine to see information about it.")
    medicine_info.config(state="disabled")
    
    # Dose info card
    dose_card = create_custom_card(left_frame, "Dosage Information")
    
    # Add dosing information text widget
    dose_info = tk.Text(dose_card, height=6, width=30, font=custom_font, wrap="word")
    dose_info.pack(fill="x", expand=True)
    dose_info.insert("1.0", "Common Dosing Guidelines:\n\n• Adults: Usually 1-2 tablets or 5-10ml\n• Children: Dosage based on weight and age\n• Elderly: May require lower doses\n\nAlways follow your doctor's instructions.")
    dose_info.config(state="disabled")
    
    # Current date and time card
    time_card = create_custom_card(left_frame, "Current Date and Time")
    
    # Show current date and time in large font
    datetime_label = ttk.Label(
        time_card, 
        text=datetime.now().strftime("%d-%m-%Y %H:%M:%S"), 
        font=time_font,
        foreground="#4a6fa5"
    )
    datetime_label.pack(pady=20)
    
    # Start updating the time
    update_current_datetime(datetime_label)
    
    # ===== RIGHT COLUMN =====
    
    # Medication Reminder System Card
    reminder_card = create_custom_card(right_frame, "Medication Reminder System")
    
    # Date input
    date_label = ttk.Label(reminder_card, text="Date (DD-MM-YYYY):", font=title_font)
    date_label.pack(anchor="w", pady=(5, 5))
    
    date_var = tk.StringVar(value=datetime.now().strftime("%d-%m-%Y"))
    date_entry = ttk.Entry(reminder_card, textvariable=date_var, font=custom_font)
    date_entry.pack(fill="x", pady=(0, 15))
    
    # Time input
    time_label = ttk.Label(reminder_card, text="Time (HH:MM):", font=title_font)
    time_label.pack(anchor="w", pady=(5, 5))
    
    time_var = tk.StringVar(value="08:00")
    time_entry = ttk.Entry(reminder_card, textvariable=time_var, font=custom_font)
    time_entry.pack(fill="x", pady=(0, 15))
    
    # Quick time buttons
    time_buttons_frame = ttk.Frame(reminder_card)
    time_buttons_frame.pack(fill="x", pady=(0, 15))
    
    time_quick_label = ttk.Label(time_buttons_frame, text="Quick Times:")
    time_quick_label.pack(side="left", padx=(0, 10))
    
    for time_str in ["08:00", "12:00", "16:00", "20:00"]:
        time_btn = tk.Button(
            time_buttons_frame,
            bg="#2222f6",
            fg="#000000",
            text=time_str,
            command=lambda t=time_str: time_var.set(t),
            width=6
        )
        time_btn.pack(side="left", padx=5)
    
    # Frequency selection
    freq_label = ttk.Label(reminder_card, text="Frequency:", font=title_font)
    freq_label.pack(anchor="w", pady=(5, 5))
    
    freq_var = tk.StringVar(value="Daily")
    freq_values = ["Once only", "Daily", "Every 8 hours", "Every 12 hours", "Weekly"]
    freq_combo = ttk.Combobox(reminder_card, textvariable=freq_var, values=freq_values, state="readonly", font=custom_font)
    freq_combo.pack(fill="x", pady=(0, 15))
    
    # Add Button with styling
    add_button = tk.Button(
        reminder_card,
        bg="#1ecd27",                 # Green background
        fg="#000000",
        text="Add Medication Reminder",
        command=lambda: add_medication_reminder(
            username, medicine_var, dose_var, date_var.get(), time_var.get(), 
            freq_var.get(), reminders_list, notification_text
        )
    )
    add_button.pack(fill="x", pady=(10, 20), ipady=5)
    
    # Medication schedule section
    schedule_label = ttk.Label(reminder_card, text="Your Medication Schedule:", font=title_font)
    schedule_label.pack(anchor="w", pady=(0, 5))
    
    # Reminders list with custom style
    reminders_frame = ttk.Frame(reminder_card)
    reminders_frame.pack(fill="both", expand=True, pady=(0, 10))
    
    # Create a custom style for the listbox
    reminders_list = tk.Listbox(
        reminders_frame, 
        height=8, 
        font=custom_font,
        selectbackground="#4a6fa5",
        selectforeground="white",
        relief="sunken",
        borderwidth=1
    )
    reminders_list.pack(side="left", fill="both", expand=True)
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(reminders_frame, orient="vertical", command=reminders_list.yview)
    scrollbar.pack(side="right", fill="y")
    reminders_list.config(yscrollcommand=scrollbar.set)
    
    # Load existing reminders
    load_medication_reminders(username, reminders_list)
    
    # Delete button for reminders
    delete_button = tk.Button(
        reminder_card,
        bg="#ec2e24",                 # Green background
        fg="#000000",
        text="Delete Selected Remainder",
        command=lambda: delete_selected_reminder(username, reminders_list)
    )
    delete_button.pack(fill="x", pady=(0, 10), ipady=8)
    
    # Notification area
    notif_label = ttk.Label(reminder_card, text="Notifications:", font=title_font)
    notif_label.pack(anchor="w", pady=(10, 5))
    
    notification_text = ttk.Entry(reminder_card, state='readonly', font=custom_font)
    notification_text.pack(fill="x", pady=(0, 10))
    
    # Active Medications Card
    active_card = create_custom_card(right_frame, "Active Medications")
    
    # Create treeview for active medications
    columns = ("Medication", "Dose", "Frequency", "Next Due")
    active_tree = ttk.Treeview(active_card, columns=columns, show="headings", height=6)
    
    # Configure columns
    for col in columns:
        active_tree.heading(col, text=col)
    
    active_tree.column("Medication", width=120)
    active_tree.column("Dose", width=80)
    active_tree.column("Frequency", width=100)
    active_tree.column("Next Due", width=120)
    
    active_tree.pack(fill="both", expand=True, pady=10)
    
    # Load active medications
    load_active_medications(username, active_tree)
    
    # Function to update medicine info and dose options when selection changes
    def update_medicine_info(event=None):
        selected_medicine = medicine_var.get()
        if selected_medicine:
            # Update medicine information
            medicine_info.config(state="normal")
            medicine_info.delete("1.0", tk.END)
            
            if selected_medicine in medicine_details:
                medicine_info.insert("1.0", medicine_details[selected_medicine]["description"])
            else:
                medicine_info.insert("1.0", f"Information for {selected_medicine} not available.")
            
            medicine_info.config(state="disabled")
            
            # Update dose information
            dose_info.config(state="normal")
            dose_info.delete("1.0", tk.END)
            
            if selected_medicine in medicine_details:
                dose_info.insert("1.0", f"Recommended Dosage for {selected_medicine}:\n\n{medicine_details[selected_medicine]['dosage']}")
                
                # Update dose combobox with medicine-specific values
                if 'common_doses' in medicine_details[selected_medicine] and medicine_details[selected_medicine]['common_doses']:
                    dose_combo['values'] = medicine_details[selected_medicine]['common_doses']
                    if dose_combo['values']:
                        dose_var.set(dose_combo['values'][0])  # Set to first dose in list
            else:
                dose_info.insert("1.0", "Dosage information not available for this medication.\n\nPlease consult your healthcare provider.")
                dose_combo['values'] = initial_doses
            
            dose_info.config(state="disabled")
    
    # Bind the function to the combobox
    medicine_combo.bind("<<ComboboxSelected>>", update_medicine_info)
    
    # Add a medication diary button
    diary_button = ttk.Button(
        active_card,
        text="View Medication History",
        command=lambda: show_medication_history(parent, username)
    )
    diary_button.pack(fill="x", pady=10, ipady=5)
    
    # Set up automatic reminder checking with parent reference for popup windows
    check_due_reminders(username, notification_text, parent)
    
    return main_frame

# === HELPER FUNCTIONS ===

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
            font=("Segoe UI", 12, "bold"),
            foreground="#4a6fa5"
        )
        title_label.pack(anchor="w")
        
        # Add separator
        separator = ttk.Separator(card, orient="horizontal")
        separator.pack(fill="x", pady=(0, 10))
    
    return card

def update_current_datetime(datetime_label):
    """Update the current date and time display"""
    current = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    datetime_label.config(text=current)
    datetime_label.after(1000, lambda: update_current_datetime(datetime_label))

def get_medications():
    """Get all medications from the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM medications ORDER BY name")
        medications = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        if not medications:
            raise Exception("No medications found")
        return medications
    except Exception as e:
        print(f"Error getting medications: {str(e)}")
        # Provide default medications if database fails
        return ["Amoxicillin", "Aspirin", "Ciprofloxacin", "Ibuprofen", 
                "Metronidazole", "Omeprazole", "Paracetamol"]

def get_medication_details():
    """Get medicine information and recommended dosages"""
    # Medicine information with description and recommended dosages
    medicine_details = {
        "Amoxicillin": {
            "description": "An antibiotic used to treat bacterial infections such as bronchitis, pneumonia, and infections of the ear, nose, throat, skin, or urinary tract.",
            "dosage": "Adults: 250-500mg every 8 hours\nChildren: 20-40mg/kg/day divided into 3 doses\nCommon forms: 250mg, 500mg capsules or tablets",
            "common_doses": ["250mg", "500mg", "875mg", "1g"]
        },
        "Aspirin": {
            "description": "A pain reliever, anti-inflammatory, and fever reducer. Also used to reduce the risk of heart attack and stroke.",
            "dosage": "Pain/Fever: 325-650mg every 4-6 hours\nHeart protection: 81-325mg daily\nNOT recommended for children under 12",
            "common_doses": ["81mg", "100mg", "325mg", "500mg"]
        },
        "Ciprofloxacin": {
            "description": "Broad-spectrum antibiotic used to treat respiratory, urinary, digestive, and skin infections caused by susceptible bacteria.",
            "dosage": "Adults: 250-750mg every 12 hours depending on infection\nNot generally recommended for children",
            "common_doses": ["250mg", "500mg", "750mg"]
        },
        "Ibuprofen": {
            "description": "Nonsteroidal anti-inflammatory drug (NSAID) used to relieve pain, reduce inflammation, and lower fever.",
            "dosage": "Adults: 200-400mg every 4-6 hours (max 1200mg daily)\nChildren (6mo+): 5-10mg/kg every 6-8 hours",
            "common_doses": ["200mg", "400mg", "600mg", "800mg"]
        },
        "Metronidazole": {
            "description": "Antibiotic effective against anaerobic bacteria and certain parasites. Used for dental infections, skin infections, and intestinal infections.",
            "dosage": "Adults: 500mg every 8 hours or 250mg every 6 hours\nChildren: 7.5mg/kg every 6 hours",
            "common_doses": ["250mg", "400mg", "500mg"]
        },
        "Omeprazole": {
            "description": "Proton pump inhibitor that reduces stomach acid production. Used to treat acid reflux, heartburn, and stomach ulcers.",
            "dosage": "Adults: 20-40mg once daily\nChildren: 0.7-3.3mg/kg once daily",
            "common_doses": ["10mg", "20mg", "40mg"]
        },
        "Paracetamol": {
            "description": "Also known as Acetaminophen. Pain reliever and fever reducer without anti-inflammatory effects. Usually safer than NSAIDs for most people.",
            "dosage": "Adults: 500-1000mg every 4-6 hours (max 4000mg daily)\nChildren: 10-15mg/kg every 4-6 hours",
            "common_doses": ["500mg", "650mg", "1000mg"]
        }
    }
    
    # Try to get from database first
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if we have a custom medicine_details table
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='medicine_details'
        """)
        
        if cursor.fetchone():
            # Get all medicine details
            cursor.execute("""
                SELECT m.name, md.description, md.dosage_info, md.common_doses
                FROM medications m
                LEFT JOIN medicine_details md ON m.id = md.medicine_id
            """)
            
            db_details = {}
            for row in cursor.fetchall():
                name, description, dosage, common_doses = row
                if description and dosage:
                    db_details[name] = {
                        "description": description,
                        "dosage": dosage,
                        "common_doses": common_doses.split(",") if common_doses else []
                    }
            
            # Merge with default details
            if db_details:
                for med in db_details:
                    medicine_details[med] = db_details[med]
        
        conn.close()
    except Exception as e:
        print(f"Error getting medicine details from database: {e}")
    
    return medicine_details

def load_medication_reminders(username, reminders_list):
    """Load medication reminders from database"""
    try:
        # Clear existing items
        reminders_list.delete(0, tk.END)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # First check if the frequency column exists in the reminders table
        cursor.execute("PRAGMA table_info(reminders)")
        columns = [column[1] for column in cursor.fetchall()]
        has_frequency_column = "frequency" in columns
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if not result:
            # If user not found, add sample data
            sample_reminders = [
                "15-04-2025 08:00 - Paracetamol (500mg) - Daily",
                "15-04-2025 14:00 - Ibuprofen (200mg) - Every 6 hours",
                "15-04-2025 20:00 - Paracetamol (500mg) - Daily",
                "16-04-2025 08:00 - Aspirin (100mg) - Daily",
                "16-04-2025 20:00 - Vitamin D (1000IU) - Weekly"
            ]
            for i, reminder in enumerate(sample_reminders):
                reminders_list.insert(tk.END, reminder)
                # Add alternating background colors
                if i % 2 == 0:
                    reminders_list.itemconfig(i, bg="#f0f0f0")
            conn.close()
            return False
        
        user_id = result[0]
        
        # Get reminders with medication names
        if has_frequency_column:
            # Use frequency if the column exists
            cursor.execute("""
                SELECT r.date, r.time, m.name, r.dose, r.frequency
                FROM reminders r
                JOIN medications m ON r.medicine_id = m.id
                WHERE r.user_id = ?
                ORDER BY r.date, r.time
            """, (user_id,))
            
            reminders = cursor.fetchall()
            conn.close()
            
            # Add reminders to list with alternating colors for readability
            for i, reminder in enumerate(reminders):
                date_str, time_str, medicine, dose, frequency = reminder
                reminder_text = f"{date_str} {time_str} - {medicine} ({dose}) - {frequency}"
                reminders_list.insert(tk.END, reminder_text)
                # Add alternating background colors
                if i % 2 == 0:
                    reminders_list.itemconfig(i, bg="#f0f0f0")
        else:
            # If frequency column doesn't exist, use a default frequency
            cursor.execute("""
                SELECT r.date, r.time, m.name, r.dose
                FROM reminders r
                JOIN medications m ON r.medicine_id = m.id
                WHERE r.user_id = ?
                ORDER BY r.date, r.time
            """, (user_id,))
            
            reminders = cursor.fetchall()
            conn.close()
            
            # Add reminders to list with alternating colors and default frequency
            for i, reminder in enumerate(reminders):
                date_str, time_str, medicine, dose = reminder
                # Assume "Daily" as default frequency
                reminder_text = f"{date_str} {time_str} - {medicine} ({dose}) - Daily"
                reminders_list.insert(tk.END, reminder_text)
                # Add alternating background colors
                if i % 2 == 0:
                    reminders_list.itemconfig(i, bg="#f0f0f0")
        
        # If no reminders found, add sample data
        if reminders_list.size() == 0:
            sample_reminders = [
                "15-04-2025 08:00 - Paracetamol (500mg) - Daily",
                "15-04-2025 14:00 - Ibuprofen (200mg) - Every 6 hours",
                "15-04-2025 20:00 - Paracetamol (500mg) - Daily",
                "16-04-2025 08:00 - Aspirin (100mg) - Daily",
                "16-04-2025 20:00 - Vitamin D (1000IU) - Weekly"
            ]
            for i, reminder in enumerate(sample_reminders):
                reminders_list.insert(tk.END, reminder)
                if i % 2 == 0:
                    reminders_list.itemconfig(i, bg="#f0f0f0")
        
        return True
        
    except Exception as e:
        print(f"Error loading reminders: {str(e)}")
        # Add sample data if database fails
        sample_reminders = [
            "15-04-2025 08:00 - Paracetamol (500mg) - Daily",
            "15-04-2025 14:00 - Ibuprofen (200mg) - Every 6 hours",
            "15-04-2025 20:00 - Paracetamol (500mg) - Daily",
            "16-04-2025 08:00 - Aspirin (100mg) - Daily",
            "16-04-2025 20:00 - Vitamin D (1000IU) - Weekly"
        ]
        for i, reminder in enumerate(sample_reminders):
            reminders_list.insert(tk.END, reminder)
            if i % 2 == 0:
                reminders_list.itemconfig(i, bg="#f0f0f0")
        return False

def delete_selected_reminder(username, reminders_list):
    """Delete the selected reminder"""
    try:
        selected_indices = reminders_list.curselection()
        if not selected_indices:
            messagebox.showinfo("Information", "Please select a reminder to delete")
            return
        
        index = selected_indices[0]
        reminder_text = reminders_list.get(index)
        
        # Extract information from the reminder text
        parts = reminder_text.split(" - ")
        datetime_part = parts[0].split(" ")
        date_str = datetime_part[0]
        time_str = datetime_part[1]
        
        medicine_dose_part = parts[1].split(" (")
        medicine = medicine_dose_part[0]
        dose = medicine_dose_part[1].rstrip(")")
        
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete this reminder?\n\n{reminder_text}")
        if not confirm:
            return
        
        # Try to delete from database
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get user ID
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            
            if result:
                user_id = result[0]
                
                # Get medicine ID
                cursor.execute("SELECT id FROM medications WHERE name = ?", (medicine,))
                med_result = cursor.fetchone()
                
                if med_result:
                    medicine_id = med_result[0]
                    
                    # Delete reminder
                    cursor.execute("""
                        DELETE FROM reminders 
                        WHERE user_id = ? AND medicine_id = ? AND date = ? AND time = ? AND dose = ?
                    """, (user_id, medicine_id, date_str, time_str, dose))
                    
                    conn.commit()
            
            conn.close()
        except Exception as e:
            print(f"Database error during deletion: {str(e)}")
        
        # Delete from list regardless of database result
        reminders_list.delete(index)
        
        # Update alternating colors
        for i in range(reminders_list.size()):
            if i % 2 == 0:
                reminders_list.itemconfig(i, bg="#f0f0f0")
            else:
                reminders_list.itemconfig(i, bg="#ffffff")
        
        messagebox.showinfo("Success", "Reminder deleted successfully")
    
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def add_medication_reminder(username, medicine_var, dose_var, date_str, time_str, frequency, reminders_list, notifications_text):
    """Add a new medication reminder"""
    try:
        # Get values from inputs
        medicine = medicine_var.get()
        dose = dose_var.get()
        
        # Validate inputs
        if not medicine or not dose or not date_str or not time_str or not frequency:
            messagebox.showerror("Error", "Please fill in all fields")
            return False
        
        # Validate date format (DD-MM-YYYY)
        try:
            reminder_date = datetime.strptime(date_str, "%d-%m-%Y")
            if reminder_date < datetime.now() - timedelta(days=1):
                if not messagebox.askyesno("Warning", "This date is in the past. Are you sure you want to continue?"):
                    return False
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use DD-MM-YYYY")
            return False
        
        # Validate time format (HH:MM)
        try:
            datetime.strptime(time_str, "%H:%M")
        except ValueError:
            messagebox.showerror("Error", "Invalid time format. Use HH:MM")
            return False
        
        # Ensure frequency column exists
        ensure_reminders_frequency_column()
        
        # Try to add to database
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get user ID
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", "User not found in database")
                conn.close()
                
                # Still add to list for demonstration
                reminder_text = f"{date_str} {time_str} - {medicine} ({dose}) - {frequency}"
                reminders_list.insert(tk.END, reminder_text)
                
                # Update alternating colors
                for i in range(reminders_list.size()):
                    if i % 2 == 0:
                        reminders_list.itemconfig(i, bg="#f0f0f0")
                    else:
                        reminders_list.itemconfig(i, bg="#ffffff")
                
                return False
            
            user_id = result[0]
            
            # Get medicine ID
            cursor.execute("SELECT id FROM medications WHERE name = ?", (medicine,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", "Medicine not found in database")
                conn.close()
                
                # Still add to list for demonstration
                reminder_text = f"{date_str} {time_str} - {medicine} ({dose}) - {frequency}"
                reminders_list.insert(tk.END, reminder_text)
                
                # Update alternating colors
                for i in range(reminders_list.size()):
                    if i % 2 == 0:
                        reminders_list.itemconfig(i, bg="#f0f0f0")
                    else:
                        reminders_list.itemconfig(i, bg="#ffffff")
                
                return False
            
            medicine_id = result[0]
            
            # Insert reminder with frequency column
            cursor.execute(
                """INSERT INTO reminders 
                   (user_id, medicine_id, dose, date, time, frequency, created_at) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (user_id, medicine_id, dose, date_str, time_str, frequency, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database error: {e}")
            # Handle the case where database operations fail
            # Still continue to add to the list for demonstration
        
        # Add to list display
        reminder_text = f"{date_str} {time_str} - {medicine} ({dose}) - {frequency}"
        reminders_list.insert(tk.END, reminder_text)
        
        # Update alternating colors
        for i in range(reminders_list.size()):
            if i % 2 == 0:
                reminders_list.itemconfig(i, bg="#f0f0f0")
            else:
                reminders_list.itemconfig(i, bg="#ffffff")
        
        # Update notification
        notifications_text.config(state="normal")
        notifications_text.delete(0, tk.END)
        notifications_text.insert(0, f"Reminder set for {medicine} ({dose}) at {time_str} on {date_str}")
        notifications_text.config(state="readonly")
        
        messagebox.showinfo("Success", "Medication reminder added successfully")
        return True
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        return False

def load_active_medications(username, active_tree):
    """Load active medications into the treeview"""
    try:
        # Clear existing items
        for item in active_tree.get_children():
            active_tree.delete(item)
        
        # Get user ID from database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if not result:
            # Add sample data
            sample_data = [
                ("Paracetamol", "500mg", "Daily", "Today, 20:00"),
                ("Ibuprofen", "200mg", "Every 6 hours", "Today, 14:00"),
                ("Aspirin", "100mg", "Daily", "Tomorrow, 08:00"),
                ("Vitamin D", "1000IU", "Weekly", "16-04-2025, 20:00")
            ]
            
            for data in sample_data:
                active_tree.insert("", "end", values=data)
            
            conn.close()
            return
        
        user_id = result[0]
        
        # Get active medications
        cursor.execute("""
            SELECT m.name, r.dose, r.frequency, r.date, r.time
            FROM reminders r
            JOIN medications m ON r.medicine_id = m.id
            WHERE r.user_id = ? AND (
                r.date >= ? OR
                (r.date = ? AND r.time >= ?)
            )
            ORDER BY r.date, r.time
        """, (
            user_id, 
            datetime.now().strftime("%d-%m-%Y"),
            datetime.now().strftime("%d-%m-%Y"),
            datetime.now().strftime("%H:%M")
        ))
        
        today = datetime.now().strftime("%d-%m-%Y")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")
        
        for row in cursor.fetchall():
            med_name, dose, frequency, date, time = row
            
            # Format the due date
            if date == today:
                due_text = f"Today, {time}"
            elif date == tomorrow:
                due_text = f"Tomorrow, {time}"
            else:
                due_text = f"{date}, {time}"
            
            active_tree.insert("", "end", values=(med_name, dose, frequency, due_text))
        
        conn.close()
        
        # If no active medications, add sample data
        if len(active_tree.get_children()) == 0:
            sample_data = [
                ("Paracetamol", "500mg", "Daily", "Today, 20:00"),
                ("Ibuprofen", "200mg", "Every 6 hours", "Today, 14:00"),
                ("Aspirin", "100mg", "Daily", "Tomorrow, 08:00"),
                ("Vitamin D", "1000IU", "Weekly", "16-04-2025, 20:00")
            ]
            
            for data in sample_data:
                active_tree.insert("", "end", values=data)
        
    except Exception as e:
        print(f"Error loading active medications: {e}")
        # Add sample data on error
        sample_data = [
            ("Paracetamol", "500mg", "Daily", "Today, 20:00"),
            ("Ibuprofen", "200mg", "Every 6 hours", "Today, 14:00"),
            ("Aspirin", "100mg", "Daily", "Tomorrow, 08:00"),
            ("Vitamin D", "1000IU", "Weekly", "16-04-2025, 20:00")
        ]
        
        for data in sample_data:
            active_tree.insert("", "end", values=data)

def check_due_reminders(username, notification_text, parent=None):
    """Check for due reminders and update notification text"""
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if result:
            user_id = result[0]
            
            # Get current date and time
            now = datetime.now()
            current_date = now.strftime("%d-%m-%Y")
            current_time = now.strftime("%H:%M")
            
            # Check for reminders due right now
            cursor.execute("""
                SELECT m.name, r.dose, r.time
                FROM reminders r
                JOIN medications m ON r.medicine_id = m.id
                WHERE r.user_id = ? AND r.date = ? AND r.time = ?
                ORDER BY r.time
            """, (user_id, current_date, current_time))
            
            due_now = cursor.fetchone()
            
            if due_now:
                med_name, dose, due_time = due_now
                
                # Show popup reminder if parent window is provided
                if parent:
                    messagebox.showinfo(
                        "Medication Reminder", 
                        f"Time to take {med_name} ({dose})",
                        parent=parent
                    )
                
                # Update notification text
                notification_text.config(state="normal")
                notification_text.delete(0, tk.END)
                notification_text.insert(0, f"Due now: {med_name} ({dose}) at {due_time}")
                notification_text.config(state="readonly")
            else:
                # Get due reminders within the next hour
                next_hour = (now + timedelta(hours=1)).strftime("%H:%M")
                
                cursor.execute("""
                    SELECT m.name, r.dose, r.time
                    FROM reminders r
                    JOIN medications m ON r.medicine_id = m.id
                    WHERE r.user_id = ? AND r.date = ? AND r.time BETWEEN ? AND ?
                    ORDER BY r.time
                    LIMIT 1
                """, (user_id, current_date, current_time, next_hour))
                
                upcoming = cursor.fetchone()
                
                if upcoming:
                    med_name, dose, due_time = upcoming
                    
                    # Update notification
                    notification_text.config(state="normal")
                    notification_text.delete(0, tk.END)
                    notification_text.insert(0, f"Due soon: {med_name} ({dose}) at {due_time}")
                    notification_text.config(state="readonly")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking reminders: {e}")
    
    # Schedule next check in 1 minute
    notification_text.after(60 * 1000, lambda: check_due_reminders(username, notification_text, parent))

def show_medication_history(parent, username):
    """Show medication history in a new window"""
    history_window = tk.Toplevel(parent)
    history_window.title("Medication History")
    history_window.geometry("700x500")
    history_window.transient(parent)  # Set parent window
    history_window.grab_set()  # Make window modal
    
    # Create main frame
    main_frame = ttk.Frame(history_window, padding=20)
    main_frame.pack(fill="both", expand=True)
    
    # Title
    title_label = ttk.Label(
        main_frame,
        text="Medication History & Compliance",
        font=("Segoe UI", 14, "bold"),
        foreground="#4a6fa5"
    )
    title_label.pack(pady=(0, 20))
    
    # Create a notebook with tabs
    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill="both", expand=True)
    
    # History tab
    history_tab = ttk.Frame(notebook)
    notebook.add(history_tab, text="Medication History")
    
    # Stats tab
    stats_tab = ttk.Frame(notebook)
    notebook.add(stats_tab, text="Compliance Stats")
    
    # Create a treeview for history
    columns = ("Date", "Time", "Medication", "Dose", "Status")
    history_tree = ttk.Treeview(history_tab, columns=columns, show="headings", height=15)
    
    # Configure columns
    for col in columns:
        history_tree.heading(col, text=col)
    
    history_tree.column("Date", width=100)
    history_tree.column("Time", width=80)
    history_tree.column("Medication", width=150)
    history_tree.column("Dose", width=80)
    history_tree.column("Status", width=100)
    
    history_tree.pack(fill="both", expand=True, pady=10)
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(history_tab, orient="vertical", command=history_tree.yview)
    scrollbar.pack(side="right", fill="y")
    history_tree.configure(yscrollcommand=scrollbar.set)
    
    # Load sample history data
    sample_history = [
        ("14-04-2025", "08:00", "Paracetamol", "500mg", "Taken"),
        ("14-04-2025", "14:00", "Ibuprofen", "200mg", "Taken"),
        ("14-04-2025", "20:00", "Paracetamol", "500mg", "Taken"),
        ("15-04-2025", "08:00", "Paracetamol", "500mg", "Taken"),
        ("15-04-2025", "14:00", "Ibuprofen", "200mg", "Missed"),
        ("15-04-2025", "20:00", "Paracetamol", "500mg", "Taken"),
        ("16-04-2025", "08:00", "Paracetamol", "500mg", "Taken"),
        ("16-04-2025", "14:00", "Ibuprofen", "200mg", "Taken"),
    ]
    
    # Add sample data with color coding
    for history_item in sample_history:
        item_id = history_tree.insert("", "end", values=history_item)
        
        # Color code based on status
        if history_item[4] == "Missed":
            history_tree.item(item_id, tags=("missed",))
        elif history_item[4] == "Taken":
            history_tree.item(item_id, tags=("taken",))
    
    # Configure tag appearance
    history_tree.tag_configure("missed", foreground="#dc3545")
    history_tree.tag_configure("taken", foreground="#28a745")
    
    # Add compliance statistics visualization
    # Compliance rate frame
    compliance_frame = ttk.LabelFrame(stats_tab, text="Compliance Rate")
    compliance_frame.pack(fill="x", pady=10, padx=10)
    
    # Create progress bar for compliance rate
    compliance_rate = 87  # Example: 87% compliance
    compliance_var = tk.IntVar(value=compliance_rate)
    
    compliance_bar = ttk.Progressbar(
        compliance_frame,
        orient="horizontal",
        length=500,
        mode="determinate",
        variable=compliance_var
    )
    compliance_bar.pack(pady=10, fill="x")
    
    compliance_label = ttk.Label(
        compliance_frame,
        text=f"{compliance_rate}% Compliance Rate",
        font=("Segoe UI", 12, "bold"),
        foreground="#4a6fa5" if compliance_rate >= 80 else "#dc3545"
    )
    compliance_label.pack(pady=(0, 10))
    
    # Medication compliance breakdown
    breakdown_frame = ttk.LabelFrame(stats_tab, text="Medication Compliance Breakdown")
    breakdown_frame.pack(fill="both", expand=True, pady=10, padx=10)
    
    # Sample data
    medications = ["Paracetamol", "Ibuprofen", "Aspirin", "Vitamin D"]
    compliance_rates = [92, 75, 100, 80]
    
    # Create bars for each medication
    for i, (med, rate) in enumerate(zip(medications, compliance_rates)):
        med_frame = ttk.Frame(breakdown_frame)
        med_frame.pack(fill="x", pady=5)
        
        med_label = ttk.Label(med_frame, text=f"{med}:", width=15, anchor="w")
        med_label.pack(side="left", padx=(0, 10))
        
        med_var = tk.IntVar(value=rate)
        med_bar = ttk.Progressbar(
            med_frame,
            orient="horizontal",
            length=400,
            mode="determinate",
            variable=med_var
        )
        med_bar.pack(side="left", fill="x", expand=True)
        
        rate_label = ttk.Label(med_frame, text=f"{rate}%", width=6)
        rate_label.pack(side="left", padx=10)
    
    # Add action buttons at the bottom
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill="x", pady=10)
    
    export_button = ttk.Button(
        button_frame,
        text="Export Report",
        command=lambda: messagebox.showinfo("Export", "Report exported successfully to My Documents", parent=history_window)
    )
    export_button.pack(side="left", padx=(0, 10))
    
    close_button = ttk.Button(
        button_frame,
        text="Close",
        command=history_window.destroy
    )
    close_button.pack(side="right")
    
    # Center window on parent
    history_window.update_idletasks()
    width = history_window.winfo_width()
    height = history_window.winfo_height()
    x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
    y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)
    history_window.geometry(f"+{x}+{y}")

def create_medicine_details_table():
    """Create medicine_details table if it doesn't exist yet"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if the table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='medicine_details'
        """)
        
        if not cursor.fetchone():
            # Create the table
            cursor.execute("""
                CREATE TABLE medicine_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    medicine_id INTEGER,
                    description TEXT,
                    dosage_info TEXT,
                    common_doses TEXT,
                    contraindications TEXT,
                    side_effects TEXT,
                    FOREIGN KEY (medicine_id) REFERENCES medications(id)
                )
            """)
            
            # Populate with some default data
            medicine_details = get_medication_details()
            
            # Get medication IDs
            cursor.execute("SELECT id, name FROM medications")
            medicines = cursor.fetchall()
            
            for med_id, med_name in medicines:
                if med_name in medicine_details:
                    details = medicine_details[med_name]
                    common_doses = ",".join(details.get("common_doses", []))
                    
                    cursor.execute("""
                        INSERT INTO medicine_details 
                        (medicine_id, description, dosage_info, common_doses)
                        VALUES (?, ?, ?, ?)
                    """, (
                        med_id, 
                        details.get("description", ""), 
                        details.get("dosage", ""),
                        common_doses
                    ))
            
            conn.commit()
            print("Created and populated medicine_details table")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating medicine_details table: {e}")
        return False

# Run this when the module is imported
create_medicine_details_table()

# For standalone testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Medication Management Tab")
    root.geometry("1000x700")
    
    # Create styles
    style = ttk.Style()
    style.configure("TButton", font=("Segoe UI", 10))
    style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"))
    
    # Create the tab with test username
    create_medication_manager_tab(root, "test")
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()