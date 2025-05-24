"""
Enhanced Medication Reminder System with desktop notifications
This module provides a comprehensive medication reminder system with desktop notifications.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import threading
import time
from datetime import datetime, timedelta

# Try to import platform-specific notification libraries
try:
    # For Windows
    from win10toast import ToastNotifier
    WINDOWS_NOTIFICATIONS = True
except ImportError:
    WINDOWS_NOTIFICATIONS = False

try:
    # For Linux
    import notify2
    LINUX_NOTIFICATIONS = True
except ImportError:
    LINUX_NOTIFICATIONS = False

try:
    # For macOS
    import pync
    MACOS_NOTIFICATIONS = True
except ImportError:
    MACOS_NOTIFICATIONS = False

# Create custom notification Window as fallback
class CustomNotification:
    """Custom notification window for platforms without native notifications"""
    
    def __init__(self, parent=None):
        self.notifications = []
        self.parent = parent
    
    def show_notification(self, title, message, duration=10):
        """Show a notification window"""
        # Create a new top-level window
        notif_window = tk.Toplevel(self.parent)
        notif_window.title("")
        notif_window.geometry("300x100+{}+{}".format(
            notif_window.winfo_screenwidth() - 320,
            notif_window.winfo_screenheight() - 120
        ))
        notif_window.attributes("-topmost", True)
        
        # No resize and no minimize/maximize buttons
        notif_window.resizable(False, False)
        notif_window.overrideredirect(True)
        
        # Create frame with border
        frame = tk.Frame(notif_window, bg="#f0f0f0", borderwidth=2, relief="ridge")
        frame.pack(fill="both", expand=True)
        
        # Add title with background color
        title_frame = tk.Frame(frame, bg="#4a6fa5", height=25)
        title_frame.pack(fill="x")
        
        title_label = tk.Label(title_frame, text=title, font=("Segoe UI", 10, "bold"), 
                            bg="#4a6fa5", fg="white")
        title_label.pack(side="left", padx=10, pady=2)
        
        # Close button
        close_button = tk.Label(title_frame, text="×", font=("Segoe UI", 12, "bold"), 
                             bg="#4a6fa5", fg="white", cursor="hand2")
        close_button.pack(side="right", padx=10, pady=2)
        close_button.bind("<Button-1>", lambda e: notif_window.destroy())
        
        # Message
        message_label = tk.Label(frame, text=message, font=("Segoe UI", 10), 
                              bg="#f0f0f0", wraplength=280, justify="left")
        message_label.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Take button
        button_frame = tk.Frame(frame, bg="#f0f0f0")
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        take_button = tk.Button(button_frame, text="Take Now", bg="#4a6fa5", fg="white",
                            command=lambda: notif_window.destroy())
        take_button.pack(side="right")
        
        # Auto-close after duration seconds
        notif_window.after(duration * 1000, notif_window.destroy)
        
        # Store reference to prevent garbage collection
        self.notifications.append(notif_window)
        
        # Remove from list when closed
        def on_close():
            if notif_window in self.notifications:
                self.notifications.remove(notif_window)
        
        notif_window.protocol("WM_DELETE_WINDOW", on_close)
        
        return notif_window

# Database path
DB_PATH = os.path.join("database", "medical_assistant.db")

class MedicationReminderSystem:
    """Class to manage medication reminders and notifications"""
    
    def __init__(self, username, parent=None):
        self.username = username
        self.reminder_thread = None
        self.running = False
        self.due_reminders_callback = None
        self.parent = parent
        
        # Initialize platform-specific notification systems
        if WINDOWS_NOTIFICATIONS:
            self.toaster = ToastNotifier()
        
        if LINUX_NOTIFICATIONS:
            notify2.init("Medical Assistant")
            
        # Initialize custom notification as fallback
        self.custom_notifier = CustomNotification(parent)
    
    def start_reminder_service(self, due_reminders_callback=None):
        """Start the reminder service in a separate thread"""
        self.due_reminders_callback = due_reminders_callback
        
        if self.reminder_thread and self.running:
            return
        
        self.running = True
        self.reminder_thread = threading.Thread(target=self._check_reminders, daemon=True)
        self.reminder_thread.start()
        
        return True
    
    def stop_reminder_service(self):
        """Stop the reminder service"""
        self.running = False
        self.reminder_thread = None
    
    def _show_desktop_notification(self, title, message):
        """Show a platform-specific desktop notification"""
        try:
            # Try Windows notification first
            if WINDOWS_NOTIFICATIONS:
                self.toaster.show_toast(
                    title,
                    message,
                    icon_path=None,
                    duration=10,
                    threaded=True
                )
                return True
            
            # Try macOS notification
            elif MACOS_NOTIFICATIONS:
                pync.notify(
                    message,
                    title=title,
                    activate="com.example.medicationreminder",
                    sound=True
                )
                return True
            
            # Try Linux notification
            elif LINUX_NOTIFICATIONS:
                notification = notify2.Notification(title, message)
                notification.show()
                return True
            
            # Use custom notification as fallback
            else:
                self.custom_notifier.show_notification(title, message)
                return True
                
        except Exception as e:
            print(f"Error showing notification: {e}")
            
            # Final fallback - use messagebox if running in main thread
            try:
                if threading.current_thread() is threading.main_thread():
                    messagebox.showinfo(title, message)
            except:
                pass
            
            return False
    
    def _log_notification(self, user_id, medicine_name, dose, time):
        """Log the notification to the database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Insert into notifications table
            cursor.execute(
                """INSERT INTO notifications 
                   (user_id, message, is_read, created_at) 
                   VALUES (?, ?, ?, ?)""",
                (
                    user_id,
                    f"Reminder: Take {medicine_name} ({dose}) at {time}",
                    0,  # Not read
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error logging notification: {e}")
            return False
    
    def add_reminder(self, medicine_name, dose, date_str, time_str, frequency="Once only"):
        """Add a new medication reminder"""
        try:
            # Connect to database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get user ID
            cursor.execute("SELECT id FROM users WHERE username = ?", (self.username,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False
                
            user_id = result[0]
            
            # Get medicine ID
            cursor.execute("SELECT id FROM medications WHERE name = ?", (medicine_name,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False
                
            medicine_id = result[0]
            
            # Add reminder
            cursor.execute(
                """INSERT INTO reminders 
                   (user_id, medicine_id, dose, date, time, frequency, created_at) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    user_id,
                    medicine_id,
                    dose,
                    date_str,
                    time_str,
                    frequency,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error adding reminder: {e}")
            return False
    
    def get_reminders(self):
        """Get all reminders for the current user"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get user ID
            cursor.execute("SELECT id FROM users WHERE username = ?", (self.username,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return []
                
            user_id = result[0]
            
            # Get reminders
            cursor.execute("""
                SELECT r.id, m.name, r.dose, r.date, r.time, r.frequency
                FROM reminders r
                JOIN medications m ON r.medicine_id = m.id
                WHERE r.user_id = ?
                ORDER BY r.date, r.time
            """, (user_id,))
            
            reminders = cursor.fetchall()
            conn.close()
            
            return reminders
            
        except Exception as e:
            print(f"Error getting reminders: {e}")
            return []
    
    def _check_reminders(self):
        """Check for due reminders periodically"""
        while self.running:
            try:
                # Get current date and time
                now = datetime.now()
                current_date = now.strftime("%d-%m-%Y")
                current_time = now.strftime("%H:%M")
                
                # Check for reminders due in the next minute
                next_minute = (now + timedelta(minutes=1)).strftime("%H:%M")
                
                # Get user ID and due reminders
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                # Get user ID
                cursor.execute("SELECT id FROM users WHERE username = ?", (self.username,))
                result = cursor.fetchone()
                
                if not result:
                    # Sleep for 60 seconds before next check if user not found
                    conn.close()
                    time.sleep(60)
                    continue
                
                user_id = result[0]
                
                # Check for any reminders due in the next minute
                cursor.execute("""
                    SELECT r.id, m.name, r.dose, r.time
                    FROM reminders r
                    JOIN medications m ON r.medicine_id = m.id
                    WHERE r.user_id = ? AND r.date = ? AND r.time BETWEEN ? AND ?
                """, (user_id, current_date, current_time, next_minute))
                
                due_reminders = cursor.fetchall()
                conn.close()
                
                # Process due reminders
                for reminder in due_reminders:
                    reminder_id, medicine_name, dose, reminder_time = reminder
                    
                    # Create notification message
                    message = f"Time to take {medicine_name} ({dose})"
                    
                    # Show desktop notification based on platform
                    self._show_desktop_notification("Medication Reminder", message)
                    
                    # Show in-app notification if callback is set
                    if self.due_reminders_callback:
                        self.due_reminders_callback(message)
                    
                    # Log the notification
                    self._log_notification(user_id, medicine_name, dose, reminder_time)
                
                # Sleep for 30 seconds before the next check
                time.sleep(30)
                
            except Exception as e:
                print(f"Error checking reminders: {e}")
                # Sleep for 60 seconds before next check if an error occurs
                time.sleep(60)