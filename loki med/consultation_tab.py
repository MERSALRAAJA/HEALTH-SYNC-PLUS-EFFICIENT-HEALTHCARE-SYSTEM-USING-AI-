"""
Appointment tab UI
This tab allows users to schedule and manage medical appointments.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import calendar
from datetime import datetime, timedelta
from tkcalendar import Calendar

# Import UI components
from widgets import create_custom_card

# Database path
DB_PATH = os.path.join("database", "medical_assistant.db")

def add_appointment(username, date_entry, time_hour_var, time_minute_var, doctor_var, type_var, notes_text, appointments_tree):
    """Add a new appointment to the database"""
    try:
        # Get values from inputs
        date_str = date_entry.get()
        time_str = f"{time_hour_var.get()}:{time_minute_var.get()}"
        doctor = doctor_var.get()
        appointment_type = type_var.get()
        notes = notes_text.get("1.0", tk.END).strip()
        status = "Scheduled"  # Default status for new appointments
        
        # Validate inputs
        if not date_str or not time_str or not doctor or not appointment_type:
            messagebox.showerror("Error", "Please fill in all required fields (date, time, doctor, type)")
            return False
        
        # Get user ID from database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if not result:
            messagebox.showerror("Error", "User not found")
            conn.close()
            return False
        
        user_id = result[0]
        
        # Insert appointment
        cursor.execute(
            """INSERT INTO appointments 
               (user_id, date, time, doctor, type, notes, reminder, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                date_str,
                time_str,
                doctor,
                appointment_type,
                notes,
                1,  # Default reminder to True
                status,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )
        
        conn.commit()
        conn.close()
        
        # Refresh the appointments list
        load_appointments(username, appointments_tree)
        
        messagebox.showinfo("Success", "Appointment added successfully")
        return True
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        return False

def update_appointment(username, appointment_id, date_entry, time_hour_var, time_minute_var, doctor_var, type_var, notes_text, status_var, appointments_tree):
    """Update an existing appointment"""
    try:
        if not appointment_id:
            messagebox.showerror("Error", "No appointment selected for update")
            return False
        
        # Get values from inputs
        date_str = date_entry.get()
        time_str = f"{time_hour_var.get()}:{time_minute_var.get()}"
        doctor = doctor_var.get()
        appointment_type = type_var.get()
        notes = notes_text.get("1.0", tk.END).strip()
        status = status_var.get()
        
        # Validate inputs
        if not date_str or not time_str or not doctor or not appointment_type:
            messagebox.showerror("Error", "Please fill in all required fields (date, time, doctor, type)")
            return False
        
        # Get user ID from database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if not result:
            messagebox.showerror("Error", "User not found")
            conn.close()
            return False
        
        user_id = result[0]
        
        # Update appointment
        cursor.execute(
            """UPDATE appointments 
               SET date = ?, time = ?, doctor = ?, type = ?, notes = ?, status = ? 
               WHERE id = ? AND user_id = ?""",
            (
                date_str,
                time_str,
                doctor,
                appointment_type,
                notes,
                status,
                appointment_id,
                user_id
            )
        )
        
        if cursor.rowcount == 0:
            messagebox.showerror("Error", "Failed to update appointment. Appointment not found or not owned by current user.")
            conn.close()
            return False
        
        conn.commit()
        conn.close()
        
        # Refresh the appointments list
        load_appointments(username, appointments_tree)
        
        messagebox.showinfo("Success", "Appointment updated successfully")
        return True
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        return False

def delete_appointment(username, appointment_id, appointments_tree):
    """Delete an appointment"""
    try:
        if not appointment_id:
            messagebox.showerror("Error", "No appointment selected for deletion")
            return False
        
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this appointment?")
        if not confirm:
            return False
        
        # Get user ID from database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if not result:
            messagebox.showerror("Error", "User not found")
            conn.close()
            return False
        
        user_id = result[0]
        
        # Delete appointment
        cursor.execute(
            "DELETE FROM appointments WHERE id = ? AND user_id = ?",
            (appointment_id, user_id)
        )
        
        if cursor.rowcount == 0:
            messagebox.showerror("Error", "Failed to delete appointment. Appointment not found or not owned by current user.")
            conn.close()
            return False
        
        conn.commit()
        conn.close()
        
        # Refresh the appointments list
        load_appointments(username, appointments_tree)
        
        messagebox.showinfo("Success", "Appointment deleted successfully")
        return True
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        return False

def load_appointments(username, appointments_tree):
    """Load appointments from the database"""
    try:
        # Clear existing appointments
        for item in appointments_tree.get_children():
            appointments_tree.delete(item)
        
        # Get user ID from database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False
        
        user_id = result[0]
        
        # Get appointments
        cursor.execute(
            """SELECT id, date, time, doctor, type, status
               FROM appointments 
               WHERE user_id = ? 
               ORDER BY date, time""",
            (user_id,)
        )
        
        appointments = cursor.fetchall()
        conn.close()
        
        # Add appointments to tree
        for appointment in appointments:
            app_id, date, time, doctor, app_type, status = appointment
            
            appointments_tree.insert("", "end", iid=app_id, values=(
                date,
                time,
                doctor,
                app_type,
                status
            ))
        
        return True
        
    except Exception as e:
        print(f"Error loading appointments: {str(e)}")
        return False

def get_appointment_details(appointment_id):
    """Get details of a specific appointment"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT date, time, doctor, type, notes, status
               FROM appointments 
               WHERE id = ?""",
            (appointment_id,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        # Create a dictionary with appointment details
        appointment = {
            "date": result[0],
            "time": result[1],
            "doctor": result[2],
            "type": result[3],
            "notes": result[4],
            "status": result[5]
        }
        
        return appointment
        
    except Exception as e:
        print(f"Error getting appointment details: {str(e)}")
        return None

def create_appointment_tab(parent, username):
    """Create the appointments tab"""
    # Create main frame
    main_frame = ttk.Frame(parent)
    main_frame.pack(fill="both", expand=True)
    
    # Create two columns
    left_frame = ttk.Frame(main_frame)
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
    
    right_frame = ttk.Frame(main_frame)
    right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
    
    # Left column - Calendar and new appointment
    calendar_card = create_custom_card(left_frame, "Appointment Calendar")
    
    # Create calendar widget
    current_date = datetime.now()
    cal = Calendar(calendar_card, selectmode='day', year=current_date.year, month=current_date.month, day=current_date.day, locale='en_US')
    cal.pack(pady=10, fill="both", expand=True)
    
    # New appointment section
    appointment_card = create_custom_card(left_frame, "Schedule New Appointment")
    
    # Date selection
    date_frame = ttk.Frame(appointment_card)
    date_frame.pack(fill="x", pady=(0, 10))
    
    date_label = ttk.Label(date_frame, text="Date:")
    date_label.pack(side="left", padx=(0, 5))
    
    date_var = tk.StringVar()
    date_entry = ttk.Entry(date_frame, textvariable=date_var, width=20)
    date_var.set(current_date.strftime("%d-%m-%Y"))
    date_entry.pack(side="left")
    
    # Function to update date entry when selecting date in calendar
    def on_date_select():
        selected_date = cal.get_date()
        date_var.set(selected_date)
    
    cal.bind("<<CalendarSelected>>", lambda e: on_date_select())
    
    # Time selection
    time_frame = ttk.Frame(appointment_card)
    time_frame.pack(fill="x", pady=(0, 10))
    
    time_label = ttk.Label(time_frame, text="Time:")
    time_label.pack(side="left", padx=(0, 5))
    
    time_hour_var = tk.StringVar(value="09")
    time_hour_values = [f"{h:02d}" for h in range(9, 18)]
    time_hour_combo = ttk.Combobox(time_frame, textvariable=time_hour_var, values=time_hour_values, width=5)
    time_hour_combo.pack(side="left")
    
    separator = ttk.Label(time_frame, text=":")
    separator.pack(side="left")
    
    time_minute_var = tk.StringVar(value="00")
    time_minute_values = ["00", "15", "30", "45"]
    time_minute_combo = ttk.Combobox(time_frame, textvariable=time_minute_var, values=time_minute_values, width=5)
    time_minute_combo.pack(side="left")
    
    # Doctor selection
    doctor_frame = ttk.Frame(appointment_card)
    doctor_frame.pack(fill="x", pady=(0, 10))
    
    doctor_label = ttk.Label(doctor_frame, text="Doctor:")
    doctor_label.pack(side="left", padx=(0, 5))
    
    doctor_var = tk.StringVar()
    doctor_values = [
        "Johnson (Cardiologist)", 
        "Smith (General Physician)", 
        "Williams (Pediatrician)", 
        "Davis (Neurologist)", 
        "Miller (Dermatologist)", 
        "Wilson (Psychiatrist)"
    ]
    doctor_combo = ttk.Combobox(doctor_frame, textvariable=doctor_var, values=doctor_values, width=25)
    doctor_combo.pack(side="left")
    
    # Type selection
    type_frame = ttk.Frame(appointment_card)
    type_frame.pack(fill="x", pady=(0, 10))
    
    type_label = ttk.Label(type_frame, text="Type:")
    type_label.pack(side="left", padx=(0, 5))
    
    type_var = tk.StringVar()
    type_values = ["Consultation", "Follow-up", "Test", "Procedure", "Other"]
    type_combo = ttk.Combobox(type_frame, textvariable=type_var, values=type_values, width=15)
    type_combo.pack(side="left")
    
    # Notes
    notes_label = ttk.Label(appointment_card, text="Notes:")
    notes_label.pack(anchor="w")
    
    notes_text = tk.Text(appointment_card, height=4, width=40)
    notes_text.pack(fill="x", pady=(5, 10))
    
    # Variable to track the currently selected appointment ID
    current_appointment_id = None
    
    # Right column - Appointments list and details
    appointments_card = create_custom_card(right_frame, "Your Appointments")
    
    # Create treeview for appointments
    appointments_frame = ttk.Frame(appointments_card)
    appointments_frame.pack(fill="both", expand=True)
    
    columns = ("Date", "Time", "Doctor", "Type", "Status")
    appointments_tree = ttk.Treeview(appointments_frame, columns=columns, show="headings", height=15)
    
    # Configure columns
    for col in columns:
        appointments_tree.heading(col, text=col)
        appointments_tree.column(col, width=80)
    
    appointments_tree.pack(side="left", fill="both", expand=True)
    
    # Add scrollbar
    appointments_scrollbar = ttk.Scrollbar(appointments_frame, orient="vertical", command=appointments_tree.yview)
    appointments_scrollbar.pack(side="right", fill="y")
    appointments_tree.configure(yscrollcommand=appointments_scrollbar.set)
    
    # Load appointments
    load_appointments(username, appointments_tree)
    
    # Appointment details card
    details_card = create_custom_card(right_frame, "Appointment Details")
    
    # Details frame
    details_frame = ttk.Frame(details_card)
    details_frame.pack(fill="both", expand=True)
    
    # Create labels for details
    detail_labels = {}
    detail_values = {}
    
    for i, field in enumerate(["Date:", "Time:", "Doctor:", "Type:", "Status:"]):
        # Label
        label = ttk.Label(details_frame, text=field)
        label.grid(row=i, column=0, sticky="w", padx=5, pady=2)
        detail_labels[field.replace(":", "")] = label
        
        # Value
        value = ttk.Label(details_frame, text="")
        value.grid(row=i, column=1, sticky="w", padx=5, pady=2)
        detail_values[field.replace(":", "")] = value
    
    # Status variable for updating
    status_var = tk.StringVar()
    status_values = ["Scheduled", "Confirmed", "Completed", "Cancelled", "Rescheduled"]
    
    # Replace status label with dropdown for editing
    status_combo = ttk.Combobox(details_frame, textvariable=status_var, values=status_values, width=15)
    status_combo.grid(row=4, column=1, sticky="w", padx=5, pady=2)
    
    # Button frame for appointments list
    button_frame = ttk.Frame(appointments_card)
    button_frame.pack(fill="x", pady=(10, 0))
    
    # Buttons for appointments
    delete_button = ttk.Button(
        button_frame,
        text="Delete Selected",
        command=lambda: delete_appointment(username, 
                                       current_appointment_id, 
                                       appointments_tree)
    )
    delete_button.pack(side="right", fill="x", expand=True)
    
    # Buttons for appointment card
    action_frame = ttk.Frame(appointment_card)
    action_frame.pack(fill="x", pady=(10, 0))
    
    save_button = ttk.Button(
        action_frame,
        text="Add New Appointment",
        command=lambda: add_appointment(
            username, date_entry, time_hour_var, time_minute_var, doctor_var, type_var, 
            notes_text, appointments_tree
        )
    )
    save_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
    
    update_button = ttk.Button(
        action_frame,
        text="Update Selected",
        command=lambda: update_appointment(
            username, current_appointment_id, date_entry, time_hour_var, time_minute_var, 
            doctor_var, type_var, notes_text, status_var, appointments_tree
        )
    )
    update_button.pack(side="right", fill="x", expand=True)
    
    # Function to handle appointment selection
    def on_appointment_select(event):
        nonlocal current_appointment_id
        
        selected = appointments_tree.selection()
        if not selected:
            return
        
        # Get the appointment ID
        appointment_id = selected[0]
        current_appointment_id = appointment_id
        
        # Get appointment details
        appointment = get_appointment_details(appointment_id)
        if not appointment:
            return
        
        # Populate form with appointment details
        date_var.set(appointment["date"])
        
        # Split time into hour and minute
        time_parts = appointment["time"].split(":")
        if len(time_parts) == 2:
            time_hour_var.set(time_parts[0])
            time_minute_var.set(time_parts[1])
        
        doctor_var.set(appointment["doctor"])
        type_var.set(appointment["type"])
        status_var.set(appointment["status"])
        
        # Set notes
        notes_text.delete("1.0", tk.END)
        if appointment["notes"]:
            notes_text.insert("1.0", appointment["notes"])
        
        # Update detail values
        detail_values["Date"].config(text=appointment["date"])
        detail_values["Time"].config(text=appointment["time"])
        detail_values["Doctor"].config(text=appointment["doctor"])
        detail_values["Type"].config(text=appointment["type"])
        detail_values["Status"].config(text=appointment["status"])
    
    # Bind selection event
    appointments_tree.bind("<<TreeviewSelect>>", on_appointment_select)
    
    return main_frame

# For testing
if __name__ == "__main__":
    # If tkcalendar is not installed, display a message
    try:
        from tkcalendar import Calendar
    except ImportError:
        print("This module requires the tkcalendar package. Please install it using:")
        print("pip install tkcalendar")
        exit(1)
        
    root = tk.Tk()
    root.title("Appointments Test")
    root.geometry("900x600")
    
    frame = create_appointment_tab(root, "test")
    
    root.mainloop()