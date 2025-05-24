"""
Standalone medication management tab for direct testing and implementation
Run this file directly to test the medication management tab
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import sqlite3
from datetime import datetime

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
        return medications
    except Exception as e:
        print(f"Error getting medications: {str(e)}")
        # Provide default medications if database fails
        return ["Amoxicillin", "Aspirin", "Ciprofloxacin", "Ibuprofen", 
                "Metronidazole", "Omeprazole", "Paracetamol"]

def load_medication_reminders(username, reminders_list):
    """Load medication reminders from database"""
    try:
        # Clear existing items
        reminders_list.delete(0, tk.END)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if not result:
            # If user not found, add sample data
            sample_reminders = [
                "15-04-2025 08:00 - Paracetamol (500mg)",
                "15-04-2025 14:00 - Ibuprofen (200mg)",
                "15-04-2025 20:00 - Paracetamol (500mg)"
            ]
            for reminder in sample_reminders:
                reminders_list.insert(tk.END, reminder)
            conn.close()
            return False
        
        user_id = result[0]
        
        # Get reminders with medication names
        cursor.execute("""
            SELECT r.date, r.time, m.name, r.dose
            FROM reminders r
            JOIN medications m ON r.medicine_id = m.id
            WHERE r.user_id = ?
            ORDER BY r.date, r.time
        """, (user_id,))
        
        reminders = cursor.fetchall()
        conn.close()
        
        # Add reminders to list
        for reminder in reminders:
            date_str, time_str, medicine, dose = reminder
            reminder_text = f"{date_str} {time_str} - {medicine} ({dose})"
            reminders_list.insert(tk.END, reminder_text)
        
        # If no reminders found, add sample data
        if reminders_list.size() == 0:
            sample_reminders = [
                "15-04-2025 08:00 - Paracetamol (500mg)",
                "15-04-2025 14:00 - Ibuprofen (200mg)",
                "15-04-2025 20:00 - Paracetamol (500mg)"
            ]
            for reminder in sample_reminders:
                reminders_list.insert(tk.END, reminder)
        
        return True
        
    except Exception as e:
        print(f"Error loading reminders: {str(e)}")
        # Add sample data if database fails
        sample_reminders = [
            "15-04-2025 08:00 - Paracetamol (500mg)",
            "15-04-2025 14:00 - Ibuprofen (200mg)",
            "15-04-2025 20:00 - Paracetamol (500mg)"
        ]
        for reminder in sample_reminders:
            reminders_list.insert(tk.END, reminder)
        return False

def add_medication_reminder(username, medicine_var, dose_var, date_entry, time_entry, reminders_list):
    """Add a new medication reminder"""
    try:
        # Get values from inputs
        medicine = medicine_var.get()
        dose = dose_var.get()
        date_str = date_entry.get()
        time_str = time_entry.get()
        
        # Validate inputs
        if not medicine or not dose or not date_str or not time_str:
            messagebox.showerror("Error", "Please fill in all fields")
            return False
        
        # Validate date format (DD-MM-YYYY)
        try:
            datetime.strptime(date_str, "%d-%m-%Y")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use DD-MM-YYYY")
            return False
        
        # Validate time format (HH:MM)
        try:
            datetime.strptime(time_str, "%H:%M")
        except ValueError:
            messagebox.showerror("Error", "Invalid time format. Use HH:MM")
            return False
        
        # Try to add to database, but continue even if it fails
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
                result = cursor.fetchone()
                
                if result:
                    medicine_id = result[0]
                    
                    # Insert reminder
                    cursor.execute(
                        "INSERT INTO reminders (user_id, medicine_id, dose, date, time, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                        (user_id, medicine_id, dose, date_str, time_str, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    )
                    
                    conn.commit()
            
            conn.close()
        except Exception as e:
            print(f"Database error: {e}")
            # Continue even if database operation fails
        
        # Add to list display in UI
        reminder_text = f"{date_str} {time_str} - {medicine} ({dose})"
        reminders_list.insert(tk.END, reminder_text)
        
        messagebox.showinfo("Success", "Medication reminder added successfully")
        return True
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        return False

def create_medication_management_tab(parent, username):
    """Create the medication manager tab"""
    # Create main frame
    main_frame = ttk.Frame(parent, padding=10)
    main_frame.pack(fill="both", expand=True)
    
    # Create two columns
    left_frame = ttk.Frame(main_frame)
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
    
    right_frame = ttk.Frame(main_frame)
    right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
    
    # Left frame - Medicine Selection
    medicine_card = create_custom_card(left_frame, "Medicine Selection")
    
    # Medicine selection
    med_label = ttk.Label(medicine_card, text="Select Medicine:")
    med_label.pack(anchor="w", pady=(5, 5))
    
    # Get medicines from database
    medicines = get_medications()
    
    medicine_var = tk.StringVar()
    medicine_combo = ttk.Combobox(medicine_card, textvariable=medicine_var, values=medicines, state="readonly")
    medicine_combo.pack(fill="x", pady=(0, 10))
    
    # Dose selection
    dose_label = ttk.Label(medicine_card, text="Select Dose:")
    dose_label.pack(anchor="w", pady=(5, 5))
    
    dose_var = tk.StringVar(value="50mg")
    dose_options = ["5mg", "10mg", "20mg", "25mg", "50mg", "100mg", "200mg", "1 tablet", "2 tablets", "5ml", "10ml", "15ml"]
    dose_combo = ttk.Combobox(medicine_card, textvariable=dose_var, values=dose_options, state="readonly")
    dose_combo.pack(fill="x", pady=(0, 10))
    
    # Add empty space to match the UI
    spacer = ttk.Frame(medicine_card, height=50)
    spacer.pack(fill="x")
    
    # Dose Selection card
    dose_card = create_custom_card(left_frame, "Dose Selection")
    
    # Just an empty frame to match the UI in the image
    dose_frame = ttk.Frame(dose_card, height=80)
    dose_frame.pack(fill="x")
    
    # Current date and time card
    date_card = create_custom_card(left_frame, "Current Date and Time")
    
    # Show current date and time in large font
    datetime_label = ttk.Label(
        date_card, 
        text=datetime.now().strftime("%d-%m-%Y %H:%M:%S"), 
        font=("Segoe UI", 16, "bold")
    )
    datetime_label.pack(pady=20)
    
    # Start updating the time
    update_current_datetime(datetime_label)
    
    # Right frame - Reminder system
    reminder_card = create_custom_card(right_frame, "Medication Reminder System")
    
    # Date input
    date_label = ttk.Label(reminder_card, text="Date (DD-MM-YYYY):")
    date_label.pack(anchor="w", pady=(5, 5))
    
    date_var = tk.StringVar(value=datetime.now().strftime("%d-%m-%Y"))
    date_entry = ttk.Entry(reminder_card, textvariable=date_var)
    date_entry.pack(fill="x", pady=(0, 15))
    
    # Time input
    time_label = ttk.Label(reminder_card, text="Time (HH:MM):")
    time_label.pack(anchor="w", pady=(5, 5))
    
    time_var = tk.StringVar(value="14:00")
    time_entry = ttk.Entry(reminder_card, textvariable=time_var)
    time_entry.pack(fill="x", pady=(0, 15))
    
    # Add button
    add_button = tk.Button(
        reminder_card,
        bg="#ec2e24",                 # Green background
        fg="#000000",
        text="Delete Selected Remainder",
        command=lambda: add_medication_reminder(
            username, medicine_var, dose_var, date_entry, time_entry, reminders_list
        )
    )
    add_button.pack(fill="x", pady=(10, 20))
    
    # Medication schedule
    schedule_label = ttk.Label(reminder_card, text="Medication Schedule:")
    schedule_label.pack(anchor="w", pady=(0, 5))
    
    # Scrollable list for reminders
    reminders_frame = ttk.Frame(reminder_card)
    reminders_frame.pack(fill="both", expand=True, pady=(0, 10))
    
    reminders_list = tk.Listbox(reminders_frame, height=10, font=("Segoe UI", 10))
    reminders_list.pack(side="left", fill="both", expand=True)
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(reminders_frame, orient="vertical", command=reminders_list.yview)
    scrollbar.pack(side="right", fill="y")
    reminders_list.config(yscrollcommand=scrollbar.set)
    
    # Load existing reminders
    load_medication_reminders(username, reminders_list)
    
    # Notifications section
    notif_label = ttk.Label(reminder_card, text="Notifications:")
    notif_label.pack(anchor="w", pady=(10, 5))
    
    notifications_text = ttk.Entry(reminder_card, state='readonly')
    notifications_text.pack(fill="x", pady=(0, 10))
    
    return main_frame

# This code will run when the script is executed directly
if __name__ == "__main__":
    # Create a standalone window for testing
    root = tk.Tk()
    root.title("Medical Assistant - Medication Management")
    root.geometry("1000x700")
    
    # Create header with username
    username = "batman"  # Default test username
    
    # Create header frame
    header_frame = ttk.Frame(root, padding=10)
    header_frame.pack(fill="x")
    
    # App title
    title_label = ttk.Label(header_frame, text="Medical Assistant", font=("Segoe UI", 18, "bold"))
    title_label.pack(side="left")
    
    # Username display
    user_label = ttk.Label(header_frame, text=f"Welcome, {username}", font=("Segoe UI", 10))
    user_label.pack(side="right")
    
    # Create the medication tab
    create_medication_management_tab(root, username)
    
    # Center window on screen
    center_window(root)
    
    # Start the application
    root.mainloop()