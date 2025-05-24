"""
Medication management tab UI
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import sqlite3
import os
import threading
import time
from datetime import datetime, timedelta

# Import UI components
from widgets import create_custom_card, center_window

# Database path
DB_PATH = os.path.join("database", "medical_assistant.db")

def add_reminder(date_entry, time_entry, medicine_combo, dose_entry, reminder_list, username):
    """Add a new medication reminder"""
    try:
        # Get values from inputs
        date_str = date_entry.get()
        time_str = time_entry.get()
        medicine = medicine_combo.get()
        dose = dose_entry.get()
        
        # Validate inputs
        if not date_str or not time_str or not medicine or not dose:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        # Validate date format (DD-MM-YYYY)
        try:
            datetime.strptime(date_str, "%d-%m-%Y")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use DD-MM-YYYY")
            return
        
        # Validate time format (HH:MM)
        try:
            datetime.strptime(time_str, "%H:%M")
        except ValueError:
            messagebox.showerror("Error", "Invalid time format. Use HH:MM")
            return
        
        # Add to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if not result:
            messagebox.showerror("Error", "User not found")
            conn.close()
            return
        
        user_id = result[0]
        
        # Get medicine ID
        cursor.execute("SELECT id FROM medications WHERE name = ?", (medicine,))
        result = cursor.fetchone()
        if not result:
            messagebox.showerror("Error", "Medicine not found")
            conn.close()
            return
        
        medicine_id = result[0]
        
        # Insert reminder
        cursor.execute(
            "INSERT INTO reminders (user_id, medicine_id, dose, date, time, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, medicine_id, dose, date_str, time_str, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        
        conn.commit()
        conn.close()
        
        # Add to list display
        reminder_text = f"{date_str} {time_str} - {medicine} ({dose})"
        reminder_list.insert(tk.END, reminder_text)
        
        # Clear inputs
        time_entry.delete(0, tk.END)
        dose_entry.delete(0, tk.END)
        
        # Set default time to next hour
        next_hour = (datetime.now() + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        time_entry.insert(0, next_hour.strftime("%H:%M"))
        
        messagebox.showinfo("Success", "Medication reminder added successfully")
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def load_reminders(reminder_list, username):
    """Load medication reminders from database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return
        
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
        
        # Clear existing items
        reminder_list.delete(0, tk.END)
        
        # Add reminders to list
        for reminder in reminders:
            date_str, time_str, medicine, dose = reminder
            reminder_text = f"{date_str} {time_str} - {medicine} ({dose})"
            reminder_list.insert(tk.END, reminder_text)
        
    except Exception as e:
        print(f"Error loading reminders: {str(e)}")

def delete_reminder(reminder_list, username):
    """Delete a selected reminder"""
    try:
        # Get selected reminder
        selected_indices = reminder_list.curselection()
        if not selected_indices:
            messagebox.showinfo("Info", "Please select a reminder to delete")
            return
        
        selected_index = selected_indices[0]
        reminder_text = reminder_list.get(selected_index)
        
        # Parse reminder text to get date, time, and medicine
        parts = reminder_text.split(" - ")
        datetime_part = parts[0].split()
        date_str = datetime_part[0]
        time_str = datetime_part[1]
        
        medicine_part = parts[1].split(" (")
        medicine = medicine_part[0]
        dose = medicine_part[1].rstrip(")")
        
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if not result:
            messagebox.showerror("Error", "User not found")
            conn.close()
            return
        
        user_id = result[0]
        
        # Get medicine ID
        cursor.execute("SELECT id FROM medications WHERE name = ?", (medicine,))
        result = cursor.fetchone()
        if not result:
            messagebox.showerror("Error", "Medicine not found")
            conn.close()
            return
        
        medicine_id = result[0]
        
        # Delete reminder
        cursor.execute(
            "DELETE FROM reminders WHERE user_id = ? AND medicine_id = ? AND date = ? AND time = ? AND dose = ?",
            (user_id, medicine_id, date_str, time_str, dose)
        )
        
        conn.commit()
        conn.close()
        
        # Remove from list
        reminder_list.delete(selected_index)
        
        messagebox.showinfo("Success", "Reminder deleted successfully")
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def check_due_reminders(username, notification_callback=None):
    """Check for due reminders in a separate thread"""
    def generate_readings():
        while True:
            try:
                now = datetime.now()
                current_date = now.strftime("%d-%m-%Y")
                current_time = now.strftime("%H:%M")
                
                # Connect to database
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                # Get user ID
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                result = cursor.fetchone()
                if not result:
                    conn.close()
                    time.sleep(60)  # Check every minute
                    continue
                
                user_id = result[0]
                
                # Get due reminders
                cursor.execute("""
                    SELECT r.id, m.name, r.dose
                    FROM reminders r
                    JOIN medications m ON r.medicine_id = m.id
                    WHERE r.user_id = ? AND r.date = ? AND r.time = ?
                """, (user_id, current_date, current_time))
                
                due_reminders = cursor.fetchall()
                conn.close()
                
                # Show notifications for due reminders
                for reminder in due_reminders:
                    reminder_id, medicine, dose = reminder
                    message = f"Time to take {medicine} ({dose})"
                    
                    # Call notification callback if provided
                    if notification_callback:
                        notification_callback(message)
                    
                    # Show system notification
                    messagebox.showinfo("Medication Reminder", message)
            
            except Exception as e:
                print(f"Error checking reminders: {str(e)}")
            
            # Check every minute
            time.sleep(60)
    
    # Start the simulation thread
    thread = threading.Thread(target=generate_readings, daemon=True)
    thread.start()
    
    return thread

def create_medication_tab(parent, username):
    """Create the medication management tab"""
    # Create main frame
    main_frame = ttk.Frame(parent)
    main_frame.pack(fill="both", expand=True)
    
    # Create two columns
    left_frame = ttk.Frame(main_frame)
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
    
    right_frame = ttk.Frame(main_frame)
    right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
    
    # Left frame - Add new reminders
    add_reminder_card = create_custom_card(left_frame, "Add Medication Reminder")
    
    # Medicine selection
    med_label = ttk.Label(add_reminder_card, text="Select Medicine:")
    med_label.pack(anchor="w", pady=(0, 5))
    
    # Get medicines from database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM medications ORDER BY name")
    medicines = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    medicine_var = tk.StringVar()
    medicine_combo = ttk.Combobox(add_reminder_card, textvariable=medicine_var, values=medicines)
    medicine_combo.pack(fill="x", pady=(0, 15))
    
    # Dose
    dose_label = ttk.Label(add_reminder_card, text="Dose (e.g., '1 tablet', '5ml'):")
    dose_label.pack(anchor="w", pady=(0, 5))
    
    dose_entry = ttk.Entry(add_reminder_card)
    dose_entry.pack(fill="x", pady=(0, 15))
    
    # Date
    date_label = ttk.Label(add_reminder_card, text="Date (DD-MM-YYYY):")
    date_label.pack(anchor="w", pady=(0, 5))
    
    date_entry = ttk.Entry(add_reminder_card)
    date_entry.pack(fill="x", pady=(0, 15))
    date_entry.insert(0, datetime.now().strftime("%d-%m-%Y"))
    
    # Time
    time_label = ttk.Label(add_reminder_card, text="Time (HH:MM):")
    time_label.pack(anchor="w", pady=(0, 5))
    
    time_entry = ttk.Entry(add_reminder_card)
    time_entry.pack(fill="x", pady=(0, 15))
    
    # Set default to next hour
    next_hour = (datetime.now() + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    time_entry.insert(0, next_hour.strftime("%H:%M"))
    
    # Right frame - Reminders list
    reminders_card = create_custom_card(right_frame, "Medication Schedule")
    
    # Create listbox for reminders
    reminder_list = tk.Listbox(reminders_card, height=15, font=("Segoe UI", 10))
    reminder_list.pack(side="left", fill="both", expand=True)
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(reminders_card, orient="vertical", command=reminder_list.yview)
    scrollbar.pack(side="right", fill="y")
    reminder_list.config(yscrollcommand=scrollbar.set)
    
    # Load existing reminders
    load_reminders(reminder_list, username)
    
    # Buttons frame
    buttons_frame = ttk.Frame(add_reminder_card)
    buttons_frame.pack(fill="x", pady=(15, 0))
    
    # Add button
    add_button = tk.Button(
        buttons_frame, 
        bg="#1ecd27",                 # Green background
        fg="#000000",
        text="Add Reminder",
        command=lambda: add_reminder(date_entry, time_entry, medicine_combo, dose_entry, reminder_list, username)
    )
    add_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
    
    # Delete button
    delete_button = tk.Button(
        buttons_frame,
        # bg="#fb1818",                
        # fg="#000000",
        text="Delete Selected",
        command=lambda: delete_reminder(reminder_list, username)
    )
    delete_button.pack(side="left", fill="x", expand=True, padx=(5, 0))
    
    # Refresh button
    refresh_button = ttk.Button(
        right_frame,
        text="Refresh Reminders",
        command=lambda: load_reminders(reminder_list, username)
    )
    refresh_button.pack(fill="x", pady=(10, 0))
    
    # Start reminder checker thread
    check_due_reminders(username)
    
    return main_frame

# For testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Medication Management Test")
    root.geometry("900x600")
    
    frame = create_medication_tab(root, "test")
    
    root.mainloop()