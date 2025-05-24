"""
Doctor consultation tab UI implementation with improved doctor selection
This tab allows users to connect with doctors via Google Meet.
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import sqlite3
import os
import webbrowser
from datetime import datetime
import json

# Database path
DB_PATH = os.path.join("database", "medical_assistant.db")

# Doctor Google Meet links (would be in a database in a real app)
DOCTOR_MEET_LINKS = {
    "Johnson": "https://meet.google.com/gxd-fyyf-ska",
    "Smith": "https://meet.google.com/qdu-ibba-bvv", 
    "Williams": "https://meet.google.com/pjo-ivxb-pzc",
    "Davis": "https://meet.google.com/ksp-xqxj-ogs",
    "Miller": "https://meet.google.com/cop-mmoi-phh",
    "Wilson": "https://meet.google.com/axc-snkb-fpv"
}

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

def start_consultation(username, doctor_var, status_label, call_btn, end_btn, video_frame):
    """Start a consultation with the selected doctor"""
    # Get selected doctor
    doctor = doctor_var.get()
    
    if not doctor:
        messagebox.showerror("Error", "Please select a doctor")
        return
    
    # Extract doctor's first name
    doctor_first_name = doctor.split(" ")[0]
    
    # Check if we have a meet link for this doctor
    if doctor_first_name not in DOCTOR_MEET_LINKS:
        messagebox.showerror("Error", f"No Google Meet link found for Dr. {doctor_first_name}")
        return
    
    # Update UI
    status_label.config(text=f"Connecting to Dr. {doctor_first_name}'s Google Meet...")
    call_btn.config(state="disabled")
    end_btn.config(state="normal")
    
    # Clear video frame
    for widget in video_frame.winfo_children():
        widget.destroy()
    
    # Create Google Meet info display
    meet_info_frame = ttk.Frame(video_frame)
    meet_info_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Display Google Meet connection info
    meet_link = DOCTOR_MEET_LINKS[doctor_first_name]
    link_label = ttk.Label(
        meet_info_frame, 
        text=f"Google Meet Link: {meet_link}",
        font=("Segoe UI", 10)
    )
    link_label.pack(pady=10)
    
    # Create a button to open Google Meet
    open_meet_btn = tk.Button(
        meet_info_frame, 
        bg="#5327F6",
        fg="#000000",
        text="Join Google Meet Call", 
        command=lambda: webbrowser.open(meet_link),
        
    )
    open_meet_btn.pack(pady=10, ipady=5, ipadx=10)
    
    # Create a frame for call status
    status_frame = ttk.Frame(meet_info_frame)
    status_frame.pack(fill="x", pady=10)
    
    status_info = ttk.Label(
        status_frame, 
        text="Click 'Join Google Meet Call' to open the meeting in your browser\n"
             "You can end the call by closing the browser tab and clicking 'End Call' below",
        wraplength=400,
        justify="center"
    )
    status_info.pack(pady=10)
    
    # Update status
    status_label.config(text=f"Google Meet call ready for Dr. {doctor_first_name}")
    
    # Save call info
    save_call_info(username, {
        "doctor": doctor,
        "link": meet_link,
        "status": "active",
        "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M"),
        "duration": "In progress"
    })

def end_consultation(doctor_var, status_label, call_btn, end_btn, video_frame, username):
    """End the current consultation"""
    # Clear video frame
    for widget in video_frame.winfo_children():
        widget.destroy()
    
    # Add back placeholder
    no_call_label = ttk.Label(
        video_frame, 
        text="No active call\nSelect a doctor and click 'Call' to begin a Google Meet session", 
        font=("Segoe UI", 12), 
        anchor="center",
        justify="center"
    )
    no_call_label.pack(fill="both", expand=True, padx=50, pady=50)
    
    # Reset UI
    status_label.config(text="Select a doctor and click 'Call' to start a consultation")
    call_btn.config(state="normal")
    end_btn.config(state="disabled")
    
    # Update call status
    update_call_status(username, "ended")
    
    messagebox.showinfo("Call Ended", "The video call session has been ended.")

def save_call_info(username, call_info):
    """Save call information to history"""
    # Ensure calls directory exists
    if not os.path.exists("calls"):
        os.makedirs("calls")
    
    # User's call history file
    call_file = f"calls/{username}.json"
    
    # Load existing call history
    calls = []
    if os.path.exists(call_file):
        try:
            with open(call_file, "r") as f:
                calls = json.load(f)
        except json.JSONDecodeError:
            calls = []
    
    # Add new call info
    calls.append(call_info)
    
    # Save back to file
    with open(call_file, "w") as f:
        json.dump(calls, f, indent=4)

def update_call_status(username, status):
    """Update the status of the most recent call"""
    # User's call history file
    call_file = f"calls/{username}.json"
    
    if os.path.exists(call_file):
        try:
            with open(call_file, "r") as f:
                calls = json.load(f)
            
            if calls:
                # Update the most recent call
                calls[-1]["status"] = status
                calls[-1]["end_time"] = datetime.now().strftime("%d-%m-%Y %H:%M")
                
                # Calculate duration
                start_time = datetime.strptime(calls[-1]["timestamp"], "%d-%m-%Y %H:%M")
                end_time = datetime.strptime(calls[-1]["end_time"], "%d-%m-%Y %H:%M")
                duration_minutes = int((end_time - start_time).total_seconds() / 60)
                calls[-1]["duration"] = f"{duration_minutes} minutes"
                
                # Save back to file
                with open(call_file, "w") as f:
                    json.dump(calls, f, indent=4)
        except Exception as e:
            print(f"Error updating call status: {e}")

def get_doctors():
    """Get list of doctors from database or return default list"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if doctors table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='doctors'
        """)
        
        if cursor.fetchone():
            # Get doctors from database
            cursor.execute("SELECT name, specialty FROM doctors ORDER BY name")
            doctors = [f"{row[0]} ({row[1]})" for row in cursor.fetchall()]
            conn.close()
            
            if doctors:
                return doctors
    except Exception as e:
        print(f"Error getting doctors: {e}")
    
    # Return default list if database failed or no doctors found
    return [
        "Johnson (Cardiologist)", 
        "Smith (General Physician)", 
        "Williams (Pediatrician)", 
        "Davis (Neurologist)", 
        "Miller (Dermatologist)", 
        "Wilson (Psychiatrist)"
    ]

def create_doctor_consultation_tab(parent, username):
    """Create the doctor consultation tab"""
    # Set up custom fonts
    custom_font = font.nametofont("TkDefaultFont").copy()
    custom_font.configure(size=10)
    
    header_font = font.Font(family="Segoe UI", size=12, weight="bold")
    title_font = font.Font(family="Segoe UI", size=11, weight="bold")
    
    # Main frame
    main_frame = ttk.Frame(parent, padding=15)
    main_frame.pack(fill="both", expand=True)
    
    # Create doctor selection card
    doctor_card = create_custom_card(main_frame, "Connect with a Doctor via Google Meet")
    
    # Doctor selection section
    selection_frame = ttk.Frame(doctor_card)
    selection_frame.pack(fill="x", pady=(0, 15))
    
    # Doctor selection label
    doctor_label = ttk.Label(selection_frame, text="Select Doctor:", font=title_font)
    doctor_label.pack(side="left", padx=(0, 10))
    
    # Get list of doctors
    doctor_list = get_doctors()
    
    # Create the doctor selection dropdown
    doctor_var = tk.StringVar()
    doctor_combo = ttk.Combobox(
        selection_frame, 
        textvariable=doctor_var, 
        values=doctor_list, 
        state="readonly", 
        font=custom_font,
        width=30
    )
    doctor_combo.pack(side="left", fill="x", expand=True)
    
    # Add a select button to force selection
    doctor_select_btn = tk.Button(
        selection_frame,
        bg="#0C05E4",
        fg="#000000",
        text="Select",
        command=lambda: doctor_var.set(doctor_combo.get())
    )
    doctor_select_btn.pack(side="left", padx=(10, 0))
    
    # Instructions
    instructions_label = ttk.Label(
        doctor_card,
        text="Select a doctor from the dropdown and click 'Call' to start a Google Meet consultation",
        wraplength=500
    )
    instructions_label.pack(anchor="w", pady=(0, 15))
    
    # Status label
    status_label = ttk.Label(
        doctor_card, 
        text="Select a doctor and click 'Call' to start a Google Meet consultation",
        font=custom_font
    )
    status_label.pack(anchor="w", pady=(0, 15))
    
    # Doctor specialty information
    specialty_frame = ttk.Frame(doctor_card)
    specialty_frame.pack(fill="x", pady=(0, 15))
    
    specialty_label = ttk.Label(specialty_frame, text="Specialty:", font=("Segoe UI", 10, "bold"))
    specialty_label.pack(side="left", padx=(0, 5))
    
    specialty_value = ttk.Label(specialty_frame, text="Select a doctor to see their specialty")
    specialty_value.pack(side="left")
    
    # Update specialty when doctor is selected
    def update_specialty(event=None):
        selected_doctor = doctor_var.get()
        if selected_doctor:
            # Extract specialty from format: "Name (Specialty)"
            start_idx = selected_doctor.find("(")
            end_idx = selected_doctor.find(")")
            if start_idx > 0 and end_idx > start_idx:
                specialty = selected_doctor[start_idx+1:end_idx]
                specialty_value.config(text=specialty)
            else:
                specialty_value.config(text="Unknown specialty")
        else:
            specialty_value.config(text="Select a doctor to see their specialty")
    
    # Bind the event to the combobox
    doctor_combo.bind("<<ComboboxSelected>>", update_specialty)
    
    # Button frame
    button_frame = ttk.Frame(doctor_card)
    button_frame.pack(fill="x", pady=(10, 0))
    
    # Video frame for displaying call info
    video_card = create_custom_card(main_frame, "Google Meet Call")
    video_frame = ttk.Frame(video_card)
    video_frame.pack(fill="both", expand=True)
    
    # Video placeholder when no call is active
    no_call_label = ttk.Label(
        video_frame, 
        text="No active call\nSelect a doctor and click 'Call' to begin a Google Meet session", 
        font=("Segoe UI", 12), 
        anchor="center",
        justify="center"
    )
    no_call_label.pack(fill="both", expand=True, padx=50, pady=50)
    
    # Call and End Call buttons
    call_btn = tk.Button(
        button_frame, 
        bg="#1ecd27",                 # Green background
        fg="#000000",
        text="Call Doctor", 
        command=lambda: start_consultation(username, doctor_var, status_label, call_btn, end_btn, video_frame),
        
    )
    call_btn.pack(side="left", padx=(0, 5), ipady=5, ipadx=10, fill="x", expand=True)
    
    end_btn = tk.Button(
        button_frame, 
        bg="#FF0000",
        fg="#000000",
        text="End Call", 
        state="disabled",
        command=lambda: end_consultation(doctor_var, status_label, call_btn, end_btn, video_frame, username)
    )
    end_btn.pack(side="left", ipady=5, ipadx=10, fill="x", expand=True)
    
    # Recent calls section
    calls_card = create_custom_card(main_frame, "Recent Calls")
    
    # Create a treeview for recent calls
    columns = ("Doctor", "Date & Time", "Duration", "Status")
    calls_tree = ttk.Treeview(calls_card, columns=columns, show="headings", height=5)
    
    # Configure columns
    for col in columns:
        calls_tree.heading(col, text=col)
    
    calls_tree.column("Doctor", width=150)
    calls_tree.column("Date & Time", width=150)
    calls_tree.column("Duration", width=100)
    calls_tree.column("Status", width=100)
    
    calls_tree.pack(fill="both", expand=True, pady=(0, 10))
    
    # Load recent calls
    try:
        # User's call history file
        call_file = f"calls/{username}.json"
        
        if os.path.exists(call_file):
            with open(call_file, "r") as f:
                calls = json.load(f)
            
            # Add calls to treeview (most recent first)
            for i, call in enumerate(reversed(calls)):
                calls_tree.insert("", "end", iid=i, values=(
                    call.get("doctor", "Unknown"),
                    call.get("timestamp", "Unknown"),
                    call.get("duration", "Unknown"),
                    call.get("status", "Unknown")
                ))
    except Exception as e:
        print(f"Error loading call history: {e}")
        # Add sample data
        sample_calls = [
            ("Dr. Johnson (Cardiologist)", "15-04-2025 10:30", "15 minutes", "Completed"),
            ("Dr. Smith (General Physician)", "14-04-2025 14:45", "30 minutes", "Completed"),
            ("Dr. Williams (Pediatrician)", "10-04-2025 09:15", "20 minutes", "Completed")
        ]
        for i, call in enumerate(sample_calls):
            calls_tree.insert("", "end", iid=i, values=call)
    
    # Help information
    info_card = create_custom_card(main_frame, "Google Meet Information")
    
    info_text = ttk.Label(
        info_card, 
        text="When you click 'Join Google Meet Call', your web browser will open.\n"
            "You may need to allow camera and microphone access in your browser.\n"
            "To end the call, close the browser tab and click 'End Call' below.",
        wraplength=500,
        justify="center"
    )
    info_text.pack(padx=10, pady=10)
    
    return main_frame
    
# Configure ttk styles for better appearance
def setup_styles():
    style = ttk.Style()
    
    # Try to use a modern theme
    try:
        style.theme_use("clam")  # Alternative: "vista" on Windows or "alt" on Linux
    except tk.TclError:
        pass  # Fallback to default theme
    
    # Configure colors
    style.configure("TFrame", background="#ffffff")
    style.configure("TLabel", background="#ffffff", font=("Segoe UI", 10))
    style.configure("TButton", font=("Segoe UI", 10))
    style.map("TButton", background=[("active", "#e1e1e1")])
    
    # Special button style
    style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), foreground="#ffffff", background="#4a6fa5")
    style.map("Accent.TButton", background=[("active", "#954c3a"), ("pressed", "#2a4f85")])
    
    return style