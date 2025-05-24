"""
Settings menu for the Medical Assistant application.
This module implements a dropdown menu for the Settings button.
"""

import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, scrolledtext
import sqlite3
import os
from datetime import datetime
import json

# Database path
DB_PATH = os.path.join("database", "medical_assistant.db")

def create_settings_menu(parent, settings_button, username):
    """Create a dropdown menu for the settings button"""
    settings_menu = tk.Menu(parent, tearoff=0)
    
    # Add menu items
    settings_menu.add_command(
        label="Account Settings",
        command=lambda: show_settings_dialog(parent, username)
    )
    
    settings_menu.add_command(
        label="View Medicines List",
        command=lambda: show_medicines_list(parent, username)
    )
    
    settings_menu.add_command(
        label="Notification History",
        command=lambda: show_notification_history(parent, username)
    )
    
    settings_menu.add_command(
        label="Personal Information",
        command=lambda: show_personal_information(parent, username)
    )
    
    settings_menu.add_separator()
    
    settings_menu.add_command(
        label="About",
        command=lambda: show_about_dialog(parent)
    )
    
    # Function to show the menu when settings button is clicked
    def show_settings_menu(event=None):
        # Get the position of the settings button
        x = settings_button.winfo_rootx()
        y = settings_button.winfo_rooty() + settings_button.winfo_height()
        
        # Show the menu at the calculated position
        settings_menu.post(x, y)
    
    # Bind the button click to show the menu
    settings_button.config(command=show_settings_menu)
    
    return settings_menu

def center_window(window, parent=None):
    """Center a window on the parent or screen"""
    window.update_idletasks()
    
    width = window.winfo_width()
    height = window.winfo_height()
    
    if parent:
        # Center on parent
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)
    else:
        # Center on screen
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
    
    window.geometry(f'{width}x{height}+{x}+{y}')

def show_settings_dialog(parent, username):
    """Show the settings dialog"""
    settings_window = Toplevel(parent)
    settings_window.title("Settings")
    settings_window.geometry("500x400")
    settings_window.transient(parent)  # Make window modal
    settings_window.grab_set()
    
    # Main frame
    main_frame = ttk.Frame(settings_window, padding=20)
    main_frame.pack(fill="both", expand=True)
    
    # Title
    title_label = tk.Label(
        main_frame,
        fg="#030303",
        text="Settings",
        font=("Segoe UI", 16, "bold")
    )
    title_label.pack(pady=(0, 20))
    
    # Create tabs for different settings
    tab_control = ttk.Notebook(main_frame)
    
    # Account settings tab
    account_tab = ttk.Frame(tab_control, padding=10)
    tab_control.add(account_tab, text="Account")
    
    # Account settings fields
    ttk.Label(account_tab, text="Username:").grid(row=0, column=0, sticky="w", pady=5)
    username_entry = ttk.Entry(account_tab, width=30)
    username_entry.insert(0, username)
    username_entry.configure(state="readonly")
    username_entry.grid(row=0, column=1, sticky="w", pady=5)
    
    ttk.Label(account_tab, text="Email:").grid(row=1, column=0, sticky="w", pady=5)
    email_entry = ttk.Entry(account_tab, width=30)
    ttk.Label(account_tab, text="Change Password:").grid(row=2, column=0, sticky="w", pady=5)
    
    # Get user email from database
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data and user_data[0]:
            email_entry.insert(0, user_data[0])
    except:
        pass
    
    email_entry.grid(row=1, column=1, sticky="w", pady=5)
    
    def change_password():
        """Function to change password"""
        # Create password change window
        password_window = Toplevel(settings_window)
        password_window.title("Change Password")
        password_window.geometry("400x250")
        password_window.transient(settings_window)
        password_window.grab_set()
        
        # Frame
        pw_frame = ttk.Frame(password_window, padding=20)
        pw_frame.pack(fill="both", expand=True)
        
        # Title
        pw_title = ttk.Label(pw_frame, text="Change Password", font=("Segoe UI", 14, "bold"))
        pw_title.pack(pady=(0, 20))
        
        # Current password
        current_pw_frame = ttk.Frame(pw_frame)
        current_pw_frame.pack(fill="x", pady=5)
        ttk.Label(current_pw_frame, text="Current Password:").pack(side="left")
        current_pw = ttk.Entry(current_pw_frame, show="•", width=20)
        current_pw.pack(side="right", fill="x", expand=True)
        
        # New password
        new_pw_frame = ttk.Frame(pw_frame)
        new_pw_frame.pack(fill="x", pady=5)
        ttk.Label(new_pw_frame, text="New Password:").pack(side="left")
        new_pw = ttk.Entry(new_pw_frame, show="•", width=20)
        new_pw.pack(side="right", fill="x", expand=True)
        
        # Confirm new password
        confirm_pw_frame = ttk.Frame(pw_frame)
        confirm_pw_frame.pack(fill="x", pady=5)
        ttk.Label(confirm_pw_frame, text="Confirm Password:").pack(side="left")
        confirm_pw = ttk.Entry(confirm_pw_frame, show="•", width=20)
        confirm_pw.pack(side="right", fill="x", expand=True)
        
        # Buttons
        pw_buttons = ttk.Frame(pw_frame)
        pw_buttons.pack(fill="x", pady=(20, 0))
        
        def save_password():
            """Process password change"""
            cur = current_pw.get()
            new = new_pw.get()
            confirm = confirm_pw.get()
            
            if not cur or not new or not confirm:
                messagebox.showerror("Error", "All fields are required")
                return
                
            if new != confirm:
                messagebox.showerror("Error", "New passwords do not match")
                return
                
            if len(new) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters long")
                return
                
            # Verify current password
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
                result = cursor.fetchone()
                
                if not result or result[0] != cur:
                    messagebox.showerror("Error", "Current password is incorrect")
                    conn.close()
                    return
                
                # Update password
                cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new, username))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Password updated successfully")
                password_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update password: {str(e)}")
        
        save_pw_btn = ttk.Button(pw_buttons, text="Save", command=save_password)
        save_pw_btn.pack(side="left", padx=(0, 5))
        
        cancel_pw_btn = ttk.Button(pw_buttons, text="Cancel", command=password_window.destroy)
        cancel_pw_btn.pack(side="left")
        
        # Center window
        center_window(password_window, settings_window)
    
    password_button = tk.Button(account_tab,bg="#1F40FF",fg="#000000",text="Change Password", command=change_password)
    password_button.grid(row=2, column=1, sticky="w", pady=5)
    
    # Notification settings tab
    notifications_tab = ttk.Frame(tab_control, padding=10)
    tab_control.add(notifications_tab, text="Notifications")
    
    # Add checkboxes for notification settings
    email_var = tk.BooleanVar(value=True)
    app_var = tk.BooleanVar(value=True)
    
    ttk.Checkbutton(notifications_tab, text="Email Notifications", variable=email_var).pack(anchor="w", pady=5)
    ttk.Checkbutton(notifications_tab, text="App Notifications", variable=app_var).pack(anchor="w", pady=5)
    
    # Add notification type options
    ttk.Label(notifications_tab, text="Notify me about:").pack(anchor="w", pady=(15, 5))
    
    types = ["Appointments", "Medication Reminders", "Doctor Messages", "Health Readings"]
    notif_vars = {}
    for notification_type in types:
        var = tk.BooleanVar(value=True)
        notif_vars[notification_type] = var
        ttk.Checkbutton(notifications_tab, text=notification_type, variable=var).pack(anchor="w", pady=2)
    
    # Appearance settings tab
    appearance_tab = ttk.Frame(tab_control, padding=10)
    tab_control.add(appearance_tab, text="Appearance")
    
    # Theme selection
    ttk.Label(appearance_tab, text="Theme:").pack(anchor="w", pady=(0, 5))
    theme_var = tk.StringVar(value="Light")
    themes = ["Light", "Dark", "System Default"]
    theme_combo = ttk.Combobox(appearance_tab, textvariable=theme_var, values=themes, state="readonly")
    theme_combo.pack(anchor="w", pady=(0, 15))
    
    # Font size
    ttk.Label(appearance_tab, text="Font Size:").pack(anchor="w", pady=(0, 5))
    font_var = tk.StringVar(value="Medium")
    font_sizes = ["Small", "Medium", "Large"]
    font_combo = ttk.Combobox(appearance_tab, textvariable=font_var, values=font_sizes, state="readonly")
    font_combo.pack(anchor="w", pady=(0, 15))
    
    tab_control.pack(fill="both", expand=True)
    
    # Buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill="x", pady=(20, 0))
    
    def save_settings():
        """Save all settings"""
        # Save email and notification preferences
        try:
            # Save email
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET email = ? WHERE username = ?", (email_entry.get(), username))
            conn.commit()
            conn.close()
            
            # Save notification preferences
            prefs = {
                "email_notifications": email_var.get(),
                "app_notifications": app_var.get(),
                "notification_types": {k: v.get() for k, v in notif_vars.items()},
                "theme": theme_var.get(),
                "font_size": font_var.get()
            }
            
            # Ensure preferences directory exists
            prefs_dir = "preferences"
            if not os.path.exists(prefs_dir):
                os.makedirs(prefs_dir)
            
            # Save preferences to file
            with open(os.path.join(prefs_dir, f"{username}.json"), "w") as f:
                json.dump(prefs, f, indent=4)
            
            messagebox.showinfo("Settings", "Settings saved successfully")
            settings_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    save_button = tk.Button(
        button_frame,
        bg="#0bff07",
        fg="#000000",
        text="Save Changes",
        command=save_settings
    )
    save_button.pack(side="left", padx=(0, 10))
    
    cancel_button = tk.Button(
        button_frame,
        bg="#fa1b1b",
        fg="#000000",
        text="Cancel",
        command=settings_window.destroy
    )
    cancel_button.pack(side="left")
    
    # Load existing preferences if available
    try:
        prefs_file = os.path.join("preferences", f"{username}.json")
        if os.path.exists(prefs_file):
            with open(prefs_file, "r") as f:
                prefs = json.load(f)
                
                if "email_notifications" in prefs:
                    email_var.set(prefs["email_notifications"])
                if "app_notifications" in prefs:
                    app_var.set(prefs["app_notifications"])
                if "notification_types" in prefs:
                    for k, v in prefs["notification_types"].items():
                        if k in notif_vars:
                            notif_vars[k].set(v)
                if "theme" in prefs:
                    theme_var.set(prefs["theme"])
                if "font_size" in prefs:
                    font_var.set(prefs["font_size"])
    except:
        pass
    
    # Center window on parent
    center_window(settings_window, parent)

def show_medicines_list(parent, username):
    """Show the medicines list window"""
    medicines_window = Toplevel(parent)
    medicines_window.title("Medicines List")
    medicines_window.geometry("600x400")
    medicines_window.transient(parent)  # Set parent window
    medicines_window.grab_set()  # Make window modal
    
    # Create main frame
    main_frame = ttk.Frame(medicines_window, padding=20)
    main_frame.pack(expand=True, fill="both")
    
    # Add title
    title_label = ttk.Label(main_frame, text="Medicines List", font=("Segoe UI", 16, "bold"))
    title_label.pack(pady=(0, 20))
    
    # Search frame
    search_frame = ttk.Frame(main_frame)
    search_frame.pack(fill="x", pady=(0, 10))
    
    ttk.Label(search_frame, text="Search:").pack(side="left", padx=(0, 5))
    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
    search_entry.pack(side="left", fill="x", expand=True)
    
    # Create a treeview for the medicines
    med_frame = ttk.Frame(main_frame)
    med_frame.pack(fill="both", expand=True, pady=(10, 0))
    
    columns = ("Name", "Price", "Description", "In Stock")
    tree = ttk.Treeview(med_frame, columns=columns, show="headings", height=15)
    
    # Configure columns
    for col in columns:
        tree.heading(col, text=col)
    
    tree.column("Name", width=150)
    tree.column("Price", width=80)
    tree.column("Description", width=250)
    tree.column("In Stock", width=80)
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(med_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    # Pack the treeview and scrollbar
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Get medicines from database and populate the tree
    all_medicines = []
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, price, description, quantity FROM medications ORDER BY name")
        for row in cursor.fetchall():
            name, price, description, quantity = row
            item_values = (
                name,
                f"₹{price:.2f}",
                description,
                quantity
            )
            tree.insert("", "end", values=item_values)
            all_medicines.append(item_values)
        
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load medicines: {str(e)}")
        # Add some dummy data if database fails
        sample_data = [
            ("Amoxicillin", "₹1079.73", "Antibiotic used to treat bacterial infections", 20),
            ("Ciprofloxacin", "₹1287.53", "Broad-spectrum antibiotic", 10),
            ("Ibuprofen", "₹622.57", "Nonsteroidal anti-inflammatory drug", 40),
            ("Paracetamol", "₹497.89", "Pain reliever and fever reducer", 50)
        ]
        all_medicines = sample_data
        for item in sample_data:
            tree.insert("", "end", values=item)
    
    # Function to filter medicines based on search
    def filter_medicines(*args):
        search_term = search_var.get().lower()
        
        # Clear treeview
        for item in tree.get_children():
            tree.delete(item)
        
        # Add matching items
        for item in all_medicines:
            if (search_term in item[0].lower() or 
                search_term in item[2].lower()):
                tree.insert("", "end", values=item)
    
    # Bind search entry to filter function
    search_var.trace("w", filter_medicines)
    
    # Buttons frame
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill="x", pady=(10, 0))
    
    # Export button
    def export_medicines():
        """Export medicines list to a text file"""
        export_path = os.path.join("medical_records", "medicines_list.txt")
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            
            with open(export_path, "w") as f:
                f.write("MEDICINES LIST\n")
                f.write("=============\n\n")
                
                for item in all_medicines:
                    f.write(f"Name: {item[0]}\n")
                    f.write(f"Price: {item[1]}\n")
                    f.write(f"Description: {item[2]}\n")
                    f.write(f"In Stock: {item[3]}\n")
                    f.write("\n" + "-"*50 + "\n\n")
            
            messagebox.showinfo("Export Successful", f"Medicines list exported to {export_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export medicines list: {str(e)}")
    
    export_button = tk.Button(
        button_frame,
        bg="#4043eb",
        fg="#000000",
        text="Export List",
        command=export_medicines
    )
    export_button.pack(side="left", padx=(0,10))
    
    # Close button
    close_button = tk.Button(
        button_frame,
        bg="#ee2424",
        fg="#000000",
        text="Close",
        command=medicines_window.destroy
    )
    close_button.pack(side="right")
    
    # Center the window on the parent
    center_window(medicines_window, parent)

def show_notification_history(parent, username):
    """Show the notification history window"""
    notification_window = Toplevel(parent)
    notification_window.title("Notification History")
    notification_window.geometry("500x400")
    notification_window.transient(parent)  # Set parent window
    notification_window.grab_set()  # Make window modal
    
    # Create main frame
    main_frame = ttk.Frame(notification_window, padding=20)
    main_frame.pack(expand=True, fill="both")
    
    # Add title
    title_label = ttk.Label(main_frame, text="Notification History", font=("Segoe UI", 16, "bold"))
    title_label.pack(pady=(0, 20))
    
    # Create a listbox for notifications
    notification_list = tk.Listbox(main_frame, font=("Segoe UI", 10), height=12)
    notification_list.pack(fill="both", expand=True, pady=10)
    
    # Add a scrollbar
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=notification_list.yview)
    notification_list.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    
    # Get notifications from database
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if result:
            user_id = result[0]
            
            # Get notifications
            cursor.execute("""
                SELECT message, created_at
                FROM notifications
                WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))
            
            for row in cursor.fetchall():
                message, created_at = row
                notification_list.insert(tk.END, f"{created_at}: {message}")
        
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load notifications: {str(e)}")
    
    # If no notifications, show sample data
    if notification_list.size() == 0:
        sample_data = [
            "2025-04-15 08:00: Reminder for Paracetamol (500mg)",
            "2025-04-14 14:30: Appointment with Dr. Johnson confirmed",
            "2025-04-13 09:15: New message from Dr. Smith",
            "2025-04-12 18:00: Order #12345 has been delivered",
            "2025-04-10 11:30: Reminder to update your medical record"
        ]
        for item in sample_data:
            notification_list.insert(tk.END, item)
    
    # Add a clear button
    clear_button = tk.Button(
        main_frame,
        bg="#0b07ff",
        fg="#000000",
        text="Clear Notifications",
        command=lambda: clear_notifications(notification_list, username)
    )
    clear_button.pack(pady=10)
    
    # Add a close button
    close_button = tk.Button(
        notification_window,
        bg="#f21c1c",
        fg="#000000",
        text="Close",
        command=notification_window.destroy
    )
    close_button.pack(pady=15)
    
    # Center the window on the parent
    center_window(notification_window, parent)

def clear_notifications(notification_list, username):
    """Clear all notifications for the user"""
    # Confirm with the user
    confirm = messagebox.askyesno("Confirm", "Are you sure you want to clear all notifications?")
    if not confirm:
        return
    
    # Clear from database
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if result:
            user_id = result[0]
            
            # Delete notifications
            cursor.execute("DELETE FROM notifications WHERE user_id = ?", (user_id,))
            conn.commit()
        
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to clear notifications: {str(e)}")
    
    # Clear the listbox
    notification_list.delete(0, tk.END)
    messagebox.showinfo("Success", "All notifications have been cleared.")

def show_personal_information(parent, username):
    """Show the personal information window"""
    personal_info_window = Toplevel(parent)
    personal_info_window.title("Personal Information")
    personal_info_window.geometry("500x500")
    personal_info_window.transient(parent)  # Set parent window
    personal_info_window.grab_set()  # Make window modal
    
    # Create main frame
    main_frame = ttk.Frame(personal_info_window, padding=20)
    main_frame.pack(expand=True, fill="both")
    
    # Add title
    title_label = ttk.Label(main_frame, text="Personal Information", font=("Segoe UI", 16, "bold"))
    title_label.pack(pady=(0, 20))
    
    # Create form for personal info
    # User info section
    user_frame = ttk.LabelFrame(main_frame, text="User Information")
    user_frame.pack(fill="x", pady=10)
    
    # Get user data from database
    user_data = {
        "username": username,
        "email": "",
        "phone": "",
        "full_name": "",
        "dob": "",
        "gender": "",
        "blood_group": "",
        "address": "",
        "city": "",
        "state": "",
        "country": "",
        "emergency_contact_name": "",
        "emergency_contact_phone": "",
        "allergies": "",
        "chronic_illnesses": ""
    }
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Allow dictionary access to rows
        cursor = conn.cursor()
        
        # Get user data
        cursor.execute("""
            SELECT u.email, u.phone, u.full_name, p.*
            FROM users u
            LEFT JOIN personal_info p ON u.id = p.user_id
            WHERE u.username = ?
        """, (username,))
        
        result = cursor.fetchone()
        
        if result:
            # Update user data with database values
            for key in user_data:
                if key in result.keys():
                    user_data[key] = result[key] or ""
        
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load user data: {str(e)}")
    
    # Basic info
    basic_info_frame = ttk.Frame(user_frame)
    basic_info_frame.pack(fill="x", padx=10, pady=10)
    
    # Full name
    name_label = ttk.Label(basic_info_frame, text="Full Name:")
    name_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
    name_entry = ttk.Entry(basic_info_frame, width=30)
    name_entry.insert(0, user_data["full_name"])
    name_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
    
    # Email
    email_label = ttk.Label(basic_info_frame, text="Email:")
    email_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
    email_entry = ttk.Entry(basic_info_frame, width=30)
    email_entry.insert(0, user_data["email"])
    email_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
    
    # Phone
    phone_label = ttk.Label(basic_info_frame, text="Phone:")
    phone_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
    phone_entry = ttk.Entry(basic_info_frame, width=30)
    phone_entry.insert(0, user_data["phone"])
    phone_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
    
    # Date of birth
    dob_label = ttk.Label(basic_info_frame, text="Date of Birth:")
    dob_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)
    dob_entry = ttk.Entry(basic_info_frame, width=30)
    dob_entry.insert(0, user_data["dob"])
    dob_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)
    
    # Gender
    gender_label = ttk.Label(basic_info_frame, text="Gender:")
    gender_label.grid(row=4, column=0, sticky="w", padx=5, pady=5)
    gender_var = tk.StringVar(value=user_data["gender"])
    gender_combo = ttk.Combobox(basic_info_frame, textvariable=gender_var, values=["Male", "Female", "Other"], width=15)
    gender_combo.grid(row=4, column=1, sticky="w", padx=5, pady=5)
    
    # Blood group
    blood_label = ttk.Label(basic_info_frame, text="Blood Group:")
    blood_label.grid(row=5, column=0, sticky="w", padx=5, pady=5)
    blood_var = tk.StringVar(value=user_data["blood_group"])
    blood_combo = ttk.Combobox(basic_info_frame, textvariable=blood_var, 
                              values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], width=15)
    blood_combo.grid(row=5, column=1, sticky="w", padx=5, pady=5)
    
    # Medical info section
    medical_frame = ttk.LabelFrame(main_frame, text="Medical Information")
    medical_frame.pack(fill="x", pady=10)
    
    medical_info_frame = ttk.Frame(medical_frame)
    medical_info_frame.pack(fill="x", padx=10, pady=10)
    
    # Allergies
    allergies_label = ttk.Label(medical_info_frame, text="Allergies:")
    allergies_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
    allergies_entry = ttk.Entry(medical_info_frame, width=30)
    allergies_entry.insert(0, user_data["allergies"])
    allergies_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
    
    # Chronic illnesses
    chronic_label = ttk.Label(medical_info_frame, text="Chronic Illnesses:")
    chronic_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
    chronic_entry = ttk.Entry(medical_info_frame, width=30)
    chronic_entry.insert(0, user_data["chronic_illnesses"])
    chronic_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
    
    # Emergency contact section
    emergency_frame = ttk.LabelFrame(main_frame, text="Emergency Contact")
    emergency_frame.pack(fill="x", pady=10)
    
    emergency_info_frame = ttk.Frame(emergency_frame)
    emergency_info_frame.pack(fill="x", padx=10, pady=10)
    
    # Contact name
    contact_name_label = ttk.Label(emergency_info_frame, text="Contact Name:")
    contact_name_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
    contact_name_entry = ttk.Entry(emergency_info_frame, width=30)
    contact_name_entry.insert(0, user_data["emergency_contact_name"])
    contact_name_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
    
    # Contact phone
    contact_phone_label = ttk.Label(emergency_info_frame, text="Contact Phone:")
    contact_phone_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
    contact_phone_entry = ttk.Entry(emergency_info_frame, width=30)
    contact_phone_entry.insert(0, user_data["emergency_contact_phone"])
    contact_phone_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
    
    # Buttons
    button_frame = ttk.Frame(personal_info_window)
    button_frame.pack(fill="x", pady=15)
    
    save_button = tk.Button(
        button_frame,
        bg="#0bff07",
        fg="#000000",
        text="Save Changes",
        command=lambda: save_personal_info(
            username,
            {
                "full_name": name_entry.get(),
                "email": email_entry.get(),
                "phone": phone_entry.get(),
                "dob": dob_entry.get(),
                "gender": gender_var.get(),
                "blood_group": blood_var.get(),
                "allergies": allergies_entry.get(),
                "chronic_illnesses": chronic_entry.get(),
                "emergency_contact_name": contact_name_entry.get(),
                "emergency_contact_phone": contact_phone_entry.get()
            }
        )
    )
    save_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
    
    close_button = tk.Button(
        button_frame,
        bg="#fd1e1e",
        fg="#000000",
        text="Close",
        command=personal_info_window.destroy
    )
    close_button.pack(side="right", fill="x", expand=True)
    
    # Center the window on the parent
    center_window(personal_info_window, parent)

def save_personal_info(username, data):
    """Save personal information to the database"""
    import sqlite3
    import os
    
    DB_PATH = os.path.join("database", "medical_assistant.db")
    
    try:
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
        
        # Update user info
        cursor.execute(
            "UPDATE users SET email = ?, phone = ?, full_name = ? WHERE id = ?",
            (data["email"], data["phone"], data["full_name"], user_id)
        )
        
        # Check if personal_info record exists
        cursor.execute("SELECT id FROM personal_info WHERE user_id = ?", (user_id,))
        personal_info_exists = cursor.fetchone() is not None
        
        if personal_info_exists:
            # Update existing record
            cursor.execute(
                """UPDATE personal_info SET 
                   dob = ?, gender = ?, blood_group = ?, allergies = ?, 
                   chronic_illnesses = ?, emergency_contact_name = ?, emergency_contact_phone = ?
                   WHERE user_id = ?""",
                (
                    data["dob"], data["gender"], data["blood_group"], data["allergies"],
                    data["chronic_illnesses"], data["emergency_contact_name"], data["emergency_contact_phone"],
                    user_id
                )
            )
        else:
            # Insert new record
            cursor.execute(
                """INSERT INTO personal_info 
                   (user_id, dob, gender, blood_group, allergies, chronic_illnesses, emergency_contact_name, emergency_contact_phone)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    user_id, data["dob"], data["gender"], data["blood_group"], data["allergies"],
                    data["chronic_illnesses"], data["emergency_contact_name"], data["emergency_contact_phone"]
                )
            )
        
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", "Personal information saved successfully")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save personal information: {str(e)}")

def show_about_dialog(parent):
    """Show the about dialog"""
    about_window = Toplevel(parent)
    about_window.title("About Medical Assistant")
    about_window.geometry("400x300")
    about_window.transient(parent)  # Set parent window
    about_window.grab_set()  # Make window modal
    
    # Create main frame
    main_frame = ttk.Frame(about_window, padding=20)
    main_frame.pack(expand=True, fill="both")
    
    # Add app title
    title_label = ttk.Label(main_frame, text="Medical Assistant", font=("Segoe UI", 18, "bold"))
    title_label.pack(pady=(0, 5))
    
    # Add version
    version_label = ttk.Label(main_frame, text="Version 1.0.0", font=("Segoe UI", 10, "italic"))
    version_label.pack(pady=(0, 20))
    
    # Add description
    description = """
Medical Assistant is a comprehensive desktop application for healthcare management, built with Python and Tkinter.

Features:
• Medication Management
• Doctor Consultation
• Medicine Purchase
• Health Monitoring
• Appointment Scheduling
• Medical Records Management
    """
    
    desc_label = ttk.Label(main_frame, text=description, wraplength=350, justify="center")
    desc_label.pack(pady=10)
    
    # Add developer info
    dev_label = ttk.Label(main_frame, text="© 2025 Medical Assistant Team", font=("Segoe UI", 8))
    dev_label.pack(side="bottom", pady=10)
    
    # Add a close button
    close_button = tk.Button(
        about_window,
        bg="#f91d1d",
        fg="#000000",
        text="Close",
        command=about_window.destroy
    )
    close_button.pack(pady=10)
    
    # Center the window on the parent
    center_window(about_window, parent)