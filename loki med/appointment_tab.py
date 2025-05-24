"""
Appointment tab UI
This module implements the Appointments tab in the Medical Assistant application.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from datetime import datetime
from tkcalendar import Calendar

# Database path
DB_PATH = os.path.join("database", "medical_assistant.db")

def create_appointment_tab(parent, username):
    """Create the appointments tab"""
    # Create main frame
    main_frame = ttk.Frame(parent)
    main_frame.pack(fill="both", expand=True)
    
    # Create two columns with adjusted weights (40% left, 60% right)
    left_frame = ttk.Frame(main_frame, width=400)
    left_frame.pack(side="left", fill="both", expand=False, padx=(0, 10))
    left_frame.pack_propagate(False)  # Prevent the frame from shrinking
    
    # Add scrolling capability to left frame
    left_canvas = tk.Canvas(left_frame, borderwidth=0, highlightthickness=0)
    left_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=left_canvas.yview)
    left_scrollable_frame = ttk.Frame(left_canvas)
    
    left_scrollable_frame.bind(
        "<Configure>",
        lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all"))
    )
    
    left_canvas.create_window((0, 0), window=left_scrollable_frame, anchor="nw")
    left_canvas.configure(yscrollcommand=left_scrollbar.set)
    
    left_canvas.pack(side="left", fill="both", expand=True)
    left_scrollbar.pack(side="right", fill="y")
    
    # Add mouse wheel scrolling
    def _on_mousewheel(event):
        left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    left_canvas.bind("<MouseWheel>", _on_mousewheel)
    
    # Right frame with increased width and weight
    right_frame = ttk.Frame(main_frame)
    right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
    
    # Left column - Calendar and new appointment with improved spacing
    calendar_card = create_custom_card(left_scrollable_frame, "Appointment Calendar")
    
    # Create calendar widget with fixed height
    current_date = datetime.now()
    cal = Calendar(calendar_card, selectmode='day', 
                 year=current_date.year, month=current_date.month, day=current_date.day,
                 locale='en_US')
    cal.pack(pady=10, fill="x")
    
    # New appointment section - with better spacing
    appointment_card = create_custom_card(left_scrollable_frame, "Schedule New Appointment")

    # Date field
    date_label = ttk.Label(appointment_card, text="Date:")
    date_label.pack(anchor="w", pady=(0, 5))

    date_var = tk.StringVar(value=current_date.strftime("%d-%m-%Y"))
    date_entry = ttk.Entry(appointment_card, textvariable=date_var)
    date_entry.pack(fill="x", pady=(0, 10))

    # Time field with hour and minute selection
    time_frame = ttk.Frame(appointment_card)
    time_frame.pack(fill="x", pady=(0, 10))

    time_label = ttk.Label(time_frame, text="Time:")
    time_label.pack(side="left", padx=(0, 5))

    # Hour selector
    hour_var = tk.StringVar(value="09")
    hour_values = [f"{h:02d}" for h in range(9, 18)]
    hour_combo = ttk.Combobox(time_frame, textvariable=hour_var, values=hour_values, width=5)
    hour_combo.pack(side="left")

    # Separator
    separator = ttk.Label(time_frame, text=":")
    separator.pack(side="left")

    # Minute selector
    minute_var = tk.StringVar(value="00")
    minute_values = ["00", "15", "30", "45"]
    minute_combo = ttk.Combobox(time_frame, textvariable=minute_var, values=minute_values, width=5)
    minute_combo.pack(side="left")

    # Doctor selection
    doctor_label = ttk.Label(appointment_card, text="Doctor:")
    doctor_label.pack(anchor="w", pady=(0, 5))

    doctor_var = tk.StringVar()
    doctor_values = [
        "Johnson (Cardiologist)", 
        "Smith (General Physician)", 
        "Williams (Pediatrician)", 
        "Davis (Neurologist)", 
        "Miller (Dermatologist)", 
        "Wilson (Psychiatrist)"
    ]
    doctor_combo = ttk.Combobox(appointment_card, textvariable=doctor_var, values=doctor_values)
    doctor_combo.pack(fill="x", pady=(0, 10))

    # Type selection
    type_label = ttk.Label(appointment_card, text="Type:")
    type_label.pack(anchor="w", pady=(0, 5))

    type_var = tk.StringVar(value="Consultation")
    type_values = ["Consultation", "Follow-up", "Test", "Procedure", "Other"]
    type_combo = ttk.Combobox(appointment_card, textvariable=type_var, values=type_values)
    type_combo.pack(fill="x", pady=(0, 10))

    # Notes field
    notes_label = ttk.Label(appointment_card, text="Notes:")
    notes_label.pack(anchor="w", pady=(0, 5))

    notes_text = tk.Text(appointment_card, height=4, width=40)
    notes_text.pack(fill="x", pady=(0, 5))

    # Add button with more visible styling
    add_button = tk.Button(
        appointment_card,
        text="Add New Appointment",
        command=lambda: add_appointment(
            username, date_entry, hour_var, minute_var, doctor_var, type_var, 
            notes_text, appointments_tree
        ),
        font=("Segoe UI", 11, "bold"),
        bg="#1ecd27",                 # Green background
        fg="#000000",    # black text
        padx=15,
        pady=8,
        cursor="hand2",
        relief=tk.RAISED
    )
    add_button.pack(fill="x", pady=(10, 0), ipady=5)
    
    # Right column top - Appointments list with more space
    appointments_card = create_custom_card(right_frame, "Your Appointments")
    
    # Create treeview for appointments
    appointments_frame = ttk.Frame(appointments_card)
    appointments_frame.pack(fill="both", expand=True)
    
    columns = ("Date", "Time", "Doctor", "Type", "Status")
    appointments_tree = ttk.Treeview(appointments_frame, columns=columns, show="headings", height=10)
    
    # Configure columns with better widths for larger right panel
    column_widths = {"Date": 120, "Time": 80, "Doctor": 180, "Type": 120, "Status": 100}
    for col in columns:
        appointments_tree.heading(col, text=col)
        appointments_tree.column(col, width=column_widths.get(col, 100))
    
    appointments_tree.pack(side="left", fill="both", expand=True)
    
    # Add scrollbar
    appointments_scrollbar = ttk.Scrollbar(appointments_frame, orient="vertical", command=appointments_tree.yview)
    appointments_scrollbar.pack(side="right", fill="y")
    appointments_tree.configure(yscrollcommand=appointments_scrollbar.set)
    
    # Right column bottom - Appointment details
    details_card = create_custom_card(right_frame, "Appointment Details")
    
    # Create labels for appointment details with better layout
    details_frame = ttk.Frame(details_card)
    details_frame.pack(fill="x", pady=(0, 10))
    
    # Fields for details
    fields = ["Date:", "Time:", "Doctor:", "Type:", "Status:"]
    detail_labels = {}
    detail_values = {}
    
    for i, field in enumerate(fields):
        # Label
        label = ttk.Label(details_frame, text=field, width=10, anchor="e")
        label.grid(row=i, column=0, sticky="e", padx=5, pady=2)
        detail_labels[field.replace(":", "")] = label
        
        # Value
        value = ttk.Label(details_frame, text="", width=40, anchor="w")
        value.grid(row=i, column=1, sticky="w", padx=5, pady=2)
        detail_values[field.replace(":", "")] = value
    
    # Status variable for updating
    status_var = tk.StringVar()
    status_values = ["Scheduled", "Confirmed", "Completed", "Cancelled", "Rescheduled"]
    
    # Status combo box (added for user convenience)
    status_frame = ttk.Frame(details_card)
    status_frame.pack(fill="x", pady=(0, 10))
    
    status_label = ttk.Label(status_frame, text="Update Status:")
    status_label.pack(side="left", padx=(0, 5))
    
    status_combo = ttk.Combobox(status_frame, textvariable=status_var, values=status_values, width=15)
    status_combo.pack(side="left")
    
    # Notes section
    notes_label = ttk.Label(details_card, text="Notes:")
    notes_label.pack(anchor="w", pady=(10, 5))
    
    details_notes = tk.Text(details_card, height=3, width=40)
    details_notes.pack(fill="x", pady=(0, 10))
    
    # Button frame
    button_frame = ttk.Frame(details_card)
    button_frame.pack(fill="x", pady=(0, 10))
    
    update_button = ttk.Button(
        button_frame,
        text="Update",
        command=lambda: update_appointment(
            username, selected_appointment_id, date_entry, hour_var, minute_var,
            doctor_var, type_var, notes_text, status_var, appointments_tree
        )
    )
    update_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
    
    delete_button = ttk.Button(
        button_frame,
        text="Delete",
        command=lambda: delete_appointment(
            username, selected_appointment_id, appointments_tree
        )
    )
    delete_button.pack(side="right", fill="x", expand=True)
    
    # Variable to track selected appointment
    selected_appointment_id = None
    
    # Function to update date entry when selecting date in calendar
    def on_date_select():
        selected_date = cal.get_date()
        date_var.set(selected_date)
    
    cal.bind("<<CalendarSelected>>", lambda e: on_date_select())
    
    # Function to handle appointment selection
    def on_appointment_select(event):
        nonlocal selected_appointment_id
        
        selected = appointments_tree.selection()
        if not selected:
            return
        
        # Get the appointment ID
        appointment_id = selected[0]
        selected_appointment_id = appointment_id
        
        # Get appointment details
        appointment = get_appointment_details(appointment_id)
        if not appointment:
            return
        
        # Update detail values
        detail_values["Date"].config(text=appointment["date"])
        detail_values["Time"].config(text=appointment["time"])
        detail_values["Doctor"].config(text=appointment["doctor"])
        detail_values["Type"].config(text=appointment["type"])
        detail_values["Status"].config(text=appointment["status"])
        
        # Update status variable
        status_var.set(appointment["status"])
        
        # Update notes text
        details_notes.delete("1.0", tk.END)
        if appointment["notes"]:
            details_notes.insert("1.0", appointment["notes"])
        
        # Also update the form fields for editing
        date_var.set(appointment["date"])
        
        # Split time into hour and minute
        time_parts = appointment["time"].split(":")
        if len(time_parts) == 2:
            hour_var.set(time_parts[0])
            minute_var.set(time_parts[1])
        
        doctor_var.set(appointment["doctor"])
        type_var.set(appointment["type"])
        
        # Update notes for editing
        notes_text.delete("1.0", tk.END)
        if appointment["notes"]:
            notes_text.insert("1.0", appointment["notes"])
    
    # Bind selection event
    appointments_tree.bind("<<TreeviewSelect>>", on_appointment_select)
    
    # Load existing appointments
    load_appointments(username, appointments_tree)
    
    return main_frame

def create_custom_card(parent, title=None, padding=10):
    """Create a custom card widget with a title"""
    # Main card frame with visual styling
    card = ttk.Frame(parent, padding=padding)
    card.pack(fill="both", expand=True, pady=10)
    
    # Add a border effect
    inner_frame = ttk.Frame(card, relief="solid", borderwidth=1)
    inner_frame.pack(fill="both", expand=True, padx=1, pady=1)
    
    # Add title if provided
    if title:
        title_frame = ttk.Frame(inner_frame, padding=(5, 5, 5, 0))
        title_frame.pack(fill="x")
        
        title_label = ttk.Label(
            title_frame, 
            text=title, 
            font=("Segoe UI", 12, "bold"),
            foreground="#4a6fa5"
        )
        title_label.pack(anchor="w")
        
        # Add separator with custom color
        separator = ttk.Separator(inner_frame, orient="horizontal")
        separator.pack(fill="x", padx=5, pady=(5, 10))
    
    # Create a content frame
    content_frame = ttk.Frame(inner_frame, padding=(10, 5, 10, 10))
    content_frame.pack(fill="both", expand=True)
    
    return content_frame

def add_appointment(username, date_entry, hour_var, minute_var, doctor_var, type_var, notes_text, appointments_tree):
    """Add a new appointment to the database"""
    try:
        # Get values from inputs
        date_str = date_entry.get()
        time_str = f"{hour_var.get()}:{minute_var.get()}"
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
        
        # Clear inputs (except date)
        notes_text.delete("1.0", tk.END)
        
        messagebox.showinfo("Success", "Appointment added successfully")
        return True
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        return False

def update_appointment(username, appointment_id, date_entry, hour_var, minute_var, doctor_var, type_var, notes_text, status_var, appointments_tree):
    """Update an existing appointment"""
    try:
        if not appointment_id:
            messagebox.showerror("Error", "No appointment selected for update")
            return False
        
        # Get values from inputs
        date_str = date_entry.get()
        time_str = f"{hour_var.get()}:{minute_var.get()}"
        doctor = doctor_var.get()
        appointment_type = type_var.get()
        notes = notes_text.get("1.0", tk.END).strip()
        status = status_var.get()
        
        # Validate inputs
        if not date_str or not time_str or not doctor or not appointment_type or not status:
            messagebox.showerror("Error", "Please fill in all required fields")
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

if __name__ == "__main__":
    # If tkcalendar is not installed, display a message
    try:
        from tkcalendar import Calendar
    except ImportError:
        print("This module requires the tkcalendar package. Please install it using:")
        print("pip install tkcalendar")
        exit(1)
    
    # For standalone testing
    root = tk.Tk()
    root.title("Appointments Test")
    root.geometry("1000x700")
    
    # Create the appointment tab
    create_appointment_tab(root, "test")
    
    root.mainloop()