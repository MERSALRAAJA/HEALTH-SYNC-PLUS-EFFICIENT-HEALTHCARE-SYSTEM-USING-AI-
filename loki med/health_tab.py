"""
Health monitoring tab UI
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import sqlite3
import os
import threading
import time
import random
from datetime import datetime

# Import UI components
from widgets import create_custom_card

# Database path
DB_PATH = os.path.join("database", "medical_assistant.db")

def simulate_pulse_reading(pulse_label, readings_text):
    """Simulate pulse sensor readings for demonstration"""
    def generate_readings():
        try:
            while True:
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
                
                # Add to readings log
                current_time = datetime.now().strftime("%H:%M:%S")
                readings_text.configure(state='normal')
                readings_text.insert(tk.END, f"Pulse: {pulse_value:.1f} BPM - {current_time}\n")
                readings_text.see(tk.END)
                readings_text.configure(state='disabled')
                
                # Sleep for 3 seconds
                time.sleep(3)
        except Exception as e:
            print(f"Error in pulse simulation: {e}")
    
    # Start the simulation thread
    thread = threading.Thread(target=generate_readings, daemon=True)
    thread.start()
    
    return thread

def add_manual_reading(username, pulse_value, notes, readings_text, pulse_label):
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
        
        # Add to readings log
        current_time = datetime.now().strftime("%H:%M:%S")
        readings_text.configure(state='normal')
        readings_text.insert(tk.END, f"Pulse (Manual): {pulse:.1f} BPM - {current_time} - Note: {notes}\n")
        readings_text.see(tk.END)
        readings_text.configure(state='disabled')
        
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
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return
        
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
        
        # Clear text widget
        readings_text.configure(state='normal')
        readings_text.delete('1.0', tk.END)
        
        # Add readings to text widget
        for reading in readings:
            value, timestamp, notes = reading
            note_text = f" - Note: {notes}" if notes else ""
            readings_text.insert(tk.END, f"Pulse: {value} BPM - {timestamp}{note_text}\n")
        
        readings_text.configure(state='disabled')
        
    except Exception as e:
        print(f"Error loading pulse history: {str(e)}")

def calculate_pulse_statistics(username):
    """Calculate statistics for pulse readings"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return None
        
        user_id = result[0]
        
        # Get readings
        cursor.execute("""
            SELECT value
            FROM health_readings
            WHERE user_id = ? AND reading_type = 'pulse'
            ORDER BY timestamp DESC
        """, (user_id,))
        
        readings = cursor.fetchall()
        conn.close()
        
        if not readings:
            return {
                "avg": "--",
                "min": "--",
                "max": "--",
                "latest": "--",
                "count": 0
            }
        
        # Calculate statistics
        values = []
        for reading in readings:
            try:
                values.append(float(reading[0]))
            except (ValueError, TypeError):
                pass
        
        if not values:
            return {
                "avg": "--",
                "min": "--",
                "max": "--",
                "latest": "--",
                "count": 0
            }
        
        stats = {
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "latest": values[0],
            "count": len(values)
        }
        
        return stats
        
    except Exception as e:
        print(f"Error calculating pulse statistics: {str(e)}")
        return None

def create_health_tab(parent, username):
    """Create the health monitoring tab"""
    # Create main frame
    main_frame = ttk.Frame(parent)
    main_frame.pack(fill="both", expand=True)
    
    # Create two columns
    left_frame = ttk.Frame(main_frame)
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
    
    right_frame = ttk.Frame(main_frame)
    right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
    
    # Left frame - Current pulse display
    pulse_card = create_custom_card(left_frame, "Current Pulse Rate")
    
    pulse_display_frame = ttk.Frame(pulse_card)
    pulse_display_frame.pack(fill="both", expand=True, padx=30, pady=20)
    
    pulse_label = ttk.Label(
        pulse_display_frame, 
        text="-- BPM", 
        font=("Segoe UI", 36, "bold"),
        foreground="#4a6fa5"
    )
    pulse_label.pack(pady=20)
    
    # Status frame
    status_frame = ttk.Frame(pulse_display_frame)
    status_frame.pack(fill="x", pady=10)
    
    status_label = ttk.Label(
        status_frame, 
        text="Pulse monitoring is active",
        font=("Segoe UI", 12),
        justify="center"
    )
    status_label.pack(pady=10)
    
    # Create a temporary text widget (will update later)
    temp_text = scrolledtext.ScrolledText(
        right_frame, 
        height=1, 
        state='disabled',
        font=("Segoe UI", 10)
    )
    
    # Start simulated monitoring
    pulse_thread = simulate_pulse_reading(pulse_label, temp_text)
    
    # Statistics card
    stats_card = create_custom_card(left_frame, "Pulse Statistics")
    
    # Create statistics display
    stats_frame = ttk.Frame(stats_card)
    stats_frame.pack(fill="x", pady=10)
    
    stats_grid = ttk.Frame(stats_frame)
    stats_grid.pack(fill="x")
    
    # Create labels for statistics
    avg_label = ttk.Label(stats_grid, text="Average:")
    avg_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
    avg_value = ttk.Label(stats_grid, text="--")
    avg_value.grid(row=0, column=1, sticky="w", padx=5, pady=2)
    
    min_label = ttk.Label(stats_grid, text="Minimum:")
    min_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
    min_value = ttk.Label(stats_grid, text="--")
    min_value.grid(row=1, column=1, sticky="w", padx=5, pady=2)
    
    max_label = ttk.Label(stats_grid, text="Maximum:")
    max_label.grid(row=2, column=0, sticky="w", padx=5, pady=2)
    max_value = ttk.Label(stats_grid, text="--")
    max_value.grid(row=2, column=1, sticky="w", padx=5, pady=2)
    
    last_label = ttk.Label(stats_grid, text="Latest:")
    last_label.grid(row=3, column=0, sticky="w", padx=5, pady=2)
    last_value = ttk.Label(stats_grid, text="--")
    last_value.grid(row=3, column=1, sticky="w", padx=5, pady=2)
    
    count_label = ttk.Label(stats_grid, text="Readings:")
    count_label.grid(row=4, column=0, sticky="w", padx=5, pady=2)
    count_value = ttk.Label(stats_grid, text="0")
    count_value.grid(row=4, column=1, sticky="w", padx=5, pady=2)
    
    # Function to update statistics
    def update_statistics():
        stats = calculate_pulse_statistics(username)
        if stats:
            avg_value.config(text=f"{stats['avg']:.1f} BPM" if stats['avg'] != '--' else '--')
            min_value.config(text=f"{stats['min']:.1f} BPM" if stats['min'] != '--' else '--')
            max_value.config(text=f"{stats['max']:.1f} BPM" if stats['max'] != '--' else '--')
            last_value.config(text=f"{stats['latest']:.1f} BPM" if stats['latest'] != '--' else '--')
            count_value.config(text=str(stats['count']))
        
        return True
    
    # Refresh button
    refresh_stats_btn = ttk.Button(
        stats_card,
        text="Refresh Statistics",
        command=update_statistics
    )
    refresh_stats_btn.pack(fill="x", pady=10, ipady=5)
    
    # Right frame - Readings history
    readings_card = create_custom_card(right_frame, "Pulse Readings History")
    
    # Readings text
    readings_text = scrolledtext.ScrolledText(
        readings_card, 
        height=15, 
        state='disabled',
        font=("Segoe UI", 10)
    )
    readings_text.pack(fill="both", expand=True, pady=10)
    
    # Update the pulse thread to use the readings text widget
    pulse_thread = simulate_pulse_reading(pulse_label, readings_text)
    
    # Refresh button
    refresh_history_btn = ttk.Button(
        readings_card,
        text="Load History",
        command=lambda: load_pulse_history(username, readings_text)
    )
    refresh_history_btn.pack(fill="x", pady=(0, 10), ipady=5)
    
    # Manual reading card
    manual_card = create_custom_card(right_frame, "Manual Reading Entry")
    
    # Pulse value
    pulse_entry_frame = ttk.Frame(manual_card)
    pulse_entry_frame.pack(fill="x", pady=10)
    
    pulse_entry_label = ttk.Label(pulse_entry_frame, text="Enter BPM:")
    pulse_entry_label.pack(side="left", padx=(0, 10))
    
    pulse_entry_var = tk.StringVar()
    pulse_entry = ttk.Entry(pulse_entry_frame, textvariable=pulse_entry_var, width=10)
    pulse_entry.pack(side="left", padx=(0, 10))
    
    # Notes
    notes_label = ttk.Label(manual_card, text="Notes:")
    notes_label.pack(anchor="w", pady=(5, 0))
    
    notes_entry = ttk.Entry(manual_card)
    notes_entry.pack(fill="x", pady=5)
    
    # Add button
    manual_add_btn = ttk.Button(
        manual_card,
        text="Add Manual Reading",
        command=lambda: add_manual_reading(
            username, 
            pulse_entry_var.get(), 
            notes_entry.get(), 
            readings_text, 
            pulse_label
        )
    )
    manual_add_btn.pack(fill="x", pady=10, ipady=5)
    
    # Information card
    info_card = create_custom_card(right_frame, "Pulse Rate Information")
    
    info_text = ttk.Label(
        info_card, 
        text="Normal resting heart rate for adults: 60-100 BPM\n"
            "• Below 60 BPM: May indicate bradycardia\n"
            "• Above 100 BPM: May indicate tachycardia\n\n"
            "Always consult your doctor for medical advice.",
        wraplength=400,
        justify="left"
    )
    info_text.pack(padx=10, pady=10, anchor="w")
    
    # Load initial history and statistics
    load_pulse_history(username, readings_text)
    update_statistics()
    
    return main_frame

# For testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Health Monitoring Test")
    root.geometry("900x600")
    
    frame = create_health_tab(root, "test")
    
    root.mainloop()