"""
Health monitoring tab UI with improved controls
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import sqlite3
import os
import threading
import time
import random
from datetime import datetime

# Database path
DB_PATH = os.path.join("database", "medical_assistant.db")

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

class PulseSimulation:
    """Class to manage pulse simulation state"""
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start(self, pulse_label, status_label, readings_text):
        """Start the pulse simulation"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(
            target=self.generate_readings,
            args=(pulse_label, status_label, readings_text),
            daemon=True
        )
        self.thread.start()
        return True
    
    def stop(self):
        """Stop the pulse simulation"""
        self.running = False
        self.thread = None
        return True
    
    def generate_readings(self, pulse_label, status_label, readings_text):
        """Generate simulated pulse readings"""
        try:
            while self.running:
                # Generate a random pulse value between 60 and 100 with some variation
                base_pulse = random.uniform(70, 85)
                variation = random.uniform(-5, 5)
                pulse_value = base_pulse + variation
                
                # Update pulse display
                pulse_label.config(text=f"{pulse_value:.1f} BPM")
                
                # Determine status and color based on pulse rate
                if pulse_value < 60:
                    status = "Low"
                    color = "#ffc107"  # Yellow
                elif pulse_value > 100:
                    status = "High"
                    color = "#dc3545"  # Red
                else:
                    status = "Normal"
                    color = "#28a745"  # Green
                
                pulse_label.config(foreground=color)
                
                # Update status label
                status_label.config(text=f"Current status: {status}")
                
                # Add to readings log
                current_time = datetime.now().strftime("%H:%M:%S")
                readings_text.config(state='normal')
                readings_text.insert(tk.END, f"Pulse: {pulse_value:.1f} BPM - {current_time}\n")
                readings_text.see(tk.END)
                readings_text.config(state='disabled')
                
                # Sleep for 3 seconds
                time.sleep(3)
        except Exception as e:
            print(f"Error in pulse simulation: {e}")

def connect_pulse_sensor(simulator, com_port, pulse_label, status_label, readings_text, connect_btn, end_btn):
    """Connect to pulse sensor (simulated)"""
    try:
        # In a real application, this would establish connection with the hardware
        # For simulation purposes, we'll just start the simulator
        
        # Clear current readings
        readings_text.config(state='normal')
        readings_text.delete('1.0', tk.END)
        readings_text.insert(tk.END, f"Connected to pulse sensor on {com_port}\n")
        readings_text.insert(tk.END, "Starting pulse monitoring...\n\n")
        readings_text.config(state='disabled')
        
        # Start simulation
        simulator.start(pulse_label, status_label, readings_text)
        
        # Update button states
        connect_btn.config(state="disabled")
        end_btn.config(state="normal")
        
        # Show success message
        messagebox.showinfo("Connected", f"Successfully connected to pulse sensor on {com_port}")
        
        return True
    except Exception as e:
        messagebox.showerror("Connection Error", f"Failed to connect to pulse sensor: {str(e)}")
        return False

def end_pulse_sensor(simulator, pulse_label, status_label, readings_text, connect_btn, end_btn):
    """End connection to pulse sensor"""
    try:
        # Stop the simulator
        simulator.stop()
        
        # Update UI
        pulse_label.config(text="-- BPM", foreground="#4a6fa5")
        status_label.config(text="Connect pulse sensor to start monitoring")
        
        # Add message to readings
        readings_text.config(state='normal')
        readings_text.insert(tk.END, "\nPulse monitoring stopped.\n")
        readings_text.see(tk.END)
        readings_text.config(state='disabled')
        
        # Update button states
        connect_btn.config(state="normal")
        end_btn.config(state="disabled")
        
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to end pulse sensor connection: {str(e)}")
        return False

def add_manual_reading(username, pulse_value, notes, readings_text, pulse_label, status_label):
    """Add a manual pulse reading"""
    try:
        # Validate pulse value
        pulse = float(pulse_value)
        if pulse <= 0:
            messagebox.showerror("Error", "Please enter a positive pulse value")
            return
        
        # Save to database
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
        
        # Insert reading
        cursor.execute(
            "INSERT INTO health_readings (user_id, reading_type, value, notes) VALUES (?, ?, ?, ?)",
            (user_id, "pulse", str(pulse), notes)
        )
        
        conn.commit()
        conn.close()
        
        # Update display
        pulse_label.config(text=f"{pulse:.1f} BPM")
        
        # Determine status and color based on pulse rate
        if pulse < 60:
            status = "Low"
            color = "#ffc107"  # Yellow
        elif pulse > 100:
            status = "High"
            color = "#dc3545"  # Red
        else:
            status = "Normal"
            color = "#28a745"  # Green
        
        pulse_label.config(foreground=color)
        status_label.config(text=f"Current status: {status}")
        
        # Add to readings log
        current_time = datetime.now().strftime("%H:%M:%S")
        readings_text.config(state='normal')
        readings_text.insert(tk.END, f"Pulse (Manual): {pulse:.1f} BPM - {current_time} - Note: {notes}\n")
        readings_text.see(tk.END)
        readings_text.config(state='disabled')
        
        messagebox.showinfo("Success", "Manual reading added successfully")
        
        return True
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid numeric value for pulse")
        return False
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        return False

def load_pulse_history(username, readings_text):
    """Load pulse reading history from database"""
    try:
        readings_text.config(state='normal')
        readings_text.delete('1.0', tk.END)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if not result:
            # If user not found, add sample data
            sample_readings = [
                "Pulse: 72.5 BPM - 09:15:30 - Morning reading",
                "Pulse: 78.3 BPM - 12:30:45 - After lunch",
                "Pulse: 68.7 BPM - 15:45:20 - Afternoon rest",
                "Pulse: 82.1 BPM - 18:20:10 - After exercise"
            ]
            for reading in sample_readings:
                readings_text.insert(tk.END, f"{reading}\n")
            
            readings_text.config(state='disabled')
            conn.close()
            return False
        
        user_id = result[0]
        
        # Get readings
        cursor.execute("""
            SELECT value, timestamp, notes
            FROM health_readings
            WHERE user_id = ? AND reading_type = 'pulse'
            ORDER BY timestamp DESC
            LIMIT 50
        """, (user_id,))
        
        readings = cursor.fetchall()
        conn.close()
        
        # Add readings to text widget
        for reading in readings:
            value, timestamp, notes = reading
            note_text = f" - {notes}" if notes else ""
            readings_text.insert(tk.END, f"Pulse: {value} BPM - {timestamp}{note_text}\n")
        
        # If no readings found, add sample data
        if not readings:
            sample_readings = [
                "Pulse: 72.5 BPM - 09:15:30 - Morning reading",
                "Pulse: 78.3 BPM - 12:30:45 - After lunch",
                "Pulse: 68.7 BPM - 15:45:20 - Afternoon rest",
                "Pulse: 82.1 BPM - 18:20:10 - After exercise"
            ]
            for reading in sample_readings:
                readings_text.insert(tk.END, f"{reading}\n")
        
        readings_text.config(state='disabled')
        return True
        
    except Exception as e:
        print(f"Error loading pulse history: {str(e)}")
        readings_text.config(state='disabled')
        return False

def create_health_monitoring_tab(parent, username):
    """Create the health monitoring tab"""
    # Create pulse simulator
    pulse_simulator = PulseSimulation()
    
    # Set up custom fonts
    custom_font = font.nametofont("TkDefaultFont").copy()
    custom_font.configure(size=10)
    
    header_font = font.Font(family="Segoe UI", size=12, weight="bold")
    title_font = font.Font(family="Segoe UI", size=11, weight="bold")
    pulse_font = font.Font(family="Segoe UI", size=40, weight="bold")
    
    # Main frame
    main_frame = ttk.Frame(parent, padding=15)
    main_frame.pack(fill="both", expand=True)
    
    # Create two columns
    left_frame = ttk.Frame(main_frame)
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
    
    right_frame = ttk.Frame(main_frame)
    right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
    
    # Left frame - Current pulse display
    pulse_card = create_custom_card(left_frame, "Current Pulse Rate")
    
    # Main pulse display area
    pulse_display_frame = ttk.Frame(pulse_card)
    pulse_display_frame.pack(fill="both", expand=True, padx=30, pady=30)
    
    # Pulse value in large font
    pulse_label = ttk.Label(
        pulse_display_frame, 
        text="-- BPM", 
        font=pulse_font,
        foreground="#4a6fa5"
    )
    pulse_label.pack(pady=20)
    
    # Status text
    status_label = ttk.Label(
        pulse_display_frame,
        text="Connect pulse sensor to start monitoring",
        font=custom_font,
        wraplength=300,
        justify="center"
    )
    status_label.pack(pady=10)
    
    # Connection controls
    connection_frame = ttk.Frame(pulse_card)
    connection_frame.pack(fill="x", pady=10)
    
    # COM Port selection
    port_frame = ttk.Frame(connection_frame)
    port_frame.pack(side="left", fill="x", expand=True)
    
    port_label = ttk.Label(port_frame, text="COM Port:")
    port_label.pack(side="left", padx=(0, 5))
    
    port_var = tk.StringVar(value="COM3")
    port_entry = ttk.Entry(port_frame, textvariable=port_var, width=10)
    port_entry.pack(side="left")
    
    # Create buttons frame
    button_frame = ttk.Frame(pulse_card)
    button_frame.pack(fill="x", pady=5)

    # Connect button
    connect_button = tk.Button(
    button_frame,
    bg="#1ecd27",                 # Green background
    fg="#000000",
    text="Connect Pulse Sensor"
    )
    connect_button.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=5)

    # End button (initially disabled)
    end_button = tk.Button(
    button_frame,
    bg="#f41e1e",
    fg="#000000",
    text="End Connection",
    state="disabled"
    )
    end_button.pack(side="right", fill="x", expand=True, padx=(5, 0), ipady=5)
    
    # Right frame - Pulse readings history
    readings_card = create_custom_card(right_frame, "Pulse Readings History")
    
    # Create a Text widget for readings with scrollbar
    readings_frame = ttk.Frame(readings_card)
    readings_frame.pack(fill="both", expand=True, pady=(0, 10))
    
    readings_text = tk.Text(
        readings_frame, 
        height=15, 
        wrap="word",
        font=custom_font,
        state="disabled"
    )
    readings_text.pack(side="left", fill="both", expand=True)
    
    readings_scrollbar = ttk.Scrollbar(readings_frame, orient="vertical", command=readings_text.yview)
    readings_scrollbar.pack(side="right", fill="y")
    readings_text.config(yscrollcommand=readings_scrollbar.set)
    
    # Load initial pulse history
    load_pulse_history(username, readings_text)
    
    # Manual reading entry
    manual_card = create_custom_card(right_frame, "Manual Reading Entry")
    
    # Manual entry form
    manual_frame = ttk.Frame(manual_card)
    manual_frame.pack(fill="x", pady=10)
    
    # BPM entry
    bpm_label = ttk.Label(manual_frame, text="Enter BPM:")
    bpm_label.pack(side="left", padx=(0, 5))
    
    bpm_var = tk.StringVar()
    bpm_entry = ttk.Entry(manual_frame, textvariable=bpm_var, width=10)
    bpm_entry.pack(side="left", padx=(0, 10))
    
    # Notes entry
    notes_frame = ttk.Frame(manual_card)
    notes_frame.pack(fill="x", pady=(0, 10))
    
    notes_label = ttk.Label(notes_frame, text="Notes:")
    notes_label.pack(side="left", padx=(0, 5))
    
    notes_entry = ttk.Entry(notes_frame)
    notes_entry.pack(side="left", fill="x", expand=True)
    
    # Description text
    desc_text = ttk.Label(
        manual_card,
        text="Use this section to manually record pulse readings from external devices.",
        wraplength=400,
        justify="left"
    )
    desc_text.pack(fill="x", pady=(0, 10))
    
    # Add manual reading button
    add_button = tk.Button(
        manual_card,
        bg="#1ecd27",                 # Green background
        fg="#000000",
        text="Add Manual Reading",
        command=lambda: add_manual_reading(
            username, 
            bpm_var.get(), 
            notes_entry.get(), 
            readings_text, 
            pulse_label,
            status_label
        )
    )
    add_button.pack(fill="x", pady=(5, 0), ipady=5)
    
    # Configure the connect button
    connect_button.config(
        command=lambda: connect_pulse_sensor(
            pulse_simulator,
            port_var.get(), 
            pulse_label, 
            status_label, 
            readings_text,
            connect_button,
            end_button
        )
    )
    
    # Configure the end button
    end_button.config(
        command=lambda: end_pulse_sensor(
            pulse_simulator,
            pulse_label,
            status_label,
            readings_text,
            connect_button,
            end_button
        )
    )
    
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
    style.map("Accent.TButton", background=[("active", "#3a5f95"), ("pressed", "#2a4f85")])
    
    return style