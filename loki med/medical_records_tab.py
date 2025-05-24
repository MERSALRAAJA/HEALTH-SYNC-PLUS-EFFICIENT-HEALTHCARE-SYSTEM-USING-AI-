"""
Medical records tab UI - Modified version without file preview section
This tab allows users to upload and manage their medical records.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import sqlite3
import os
import shutil
from datetime import datetime
import json

# Import UI components
from widgets import create_custom_card

# Database path
DB_PATH = os.path.join("database", "medical_assistant.db")

# Medical Records directory
RECORDS_DIR = "medical_records"

def add_medical_record(username, file_path, record_type, record_date, provider, description, tags, records_tree):
    """Add a new medical record to the database and file system"""
    try:
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "File does not exist")
            return False
        
        # Validate inputs
        if not record_type or not record_date or not provider:
            messagebox.showerror("Error", "Please fill in all required fields (Type, Date, Provider)")
            return False
        
        # Get file details
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # Create user directory if it doesn't exist
        user_dir = os.path.join(RECORDS_DIR, username)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        
        # Copy file to user directory
        dest_path = os.path.join(user_dir, file_name)
        shutil.copy2(file_path, dest_path)
        
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
        
        # Convert tags list to comma-separated string
        tags_str = tags if isinstance(tags, str) else ",".join(tags)
        
        # Insert record into database
        cursor.execute(
            """INSERT INTO medical_records 
               (user_id, file_name, file_path, record_type, record_date, 
                provider, description, tags, upload_date)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                file_name,
                dest_path,
                record_type,
                record_date,
                provider,
                description,
                tags_str,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )
        
        conn.commit()
        conn.close()
        
        # Refresh the records list
        load_medical_records(username, records_tree)
        
        messagebox.showinfo("Success", "Medical record added successfully")
        return True
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        return False

def delete_medical_record(username, record_id, records_tree):
    """Delete a medical record"""
    try:
        if not record_id:
            messagebox.showerror("Error", "No record selected for deletion")
            return False
        
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this medical record?")
        if not confirm:
            return False
        
        # Get user ID and file details from database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if not result:
            messagebox.showerror("Error", "User not found")
            conn.close()
            return False
        
        user_id = result[0]
        
        # Get file path before deleting record
        cursor.execute(
            "SELECT file_path FROM medical_records WHERE id = ? AND user_id = ?",
            (record_id, user_id)
        )
        
        result = cursor.fetchone()
        if not result:
            messagebox.showerror("Error", "Record not found or not owned by current user")
            conn.close()
            return False
        
        file_path = result[0]
        
        # Delete record from database
        cursor.execute(
            "DELETE FROM medical_records WHERE id = ? AND user_id = ?",
            (record_id, user_id)
        )
        
        if cursor.rowcount == 0:
            messagebox.showerror("Error", "Failed to delete record from database")
            conn.close()
            return False
        
        conn.commit()
        conn.close()
        
        # Delete file if it exists
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                print(f"Warning: Could not delete file {file_path}")
        
        # Refresh the records list
        load_medical_records(username, records_tree)
        
        messagebox.showinfo("Success", "Medical record deleted successfully")
        return True
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        return False

def view_medical_record(username, record_id):
    """Open a medical record file"""
    try:
        if not record_id:
            messagebox.showerror("Error", "No record selected for viewing")
            return False
        
        # Get file path from database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if not result:
            messagebox.showerror("Error", "User not found")
            conn.close()
            return False
        
        user_id = result[0]
        
        cursor.execute(
            "SELECT file_path FROM medical_records WHERE id = ? AND user_id = ?",
            (record_id, user_id)
        )
        
        result = cursor.fetchone()
        if not result:
            messagebox.showerror("Error", "Record not found or not owned by current user")
            conn.close()
            return False
        
        file_path = result[0]
        conn.close()
        
        # Check if file exists
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "File not found on disk")
            return False
        
        # Try to open the file with the default application
        try:
            import subprocess
            import platform
            
            system = platform.system()
            
            if system == 'Windows':
                os.startfile(file_path)
            elif system == 'Darwin':  # macOS
                subprocess.call(('open', file_path))
            else:  # Linux and other Unix-like
                subprocess.call(('xdg-open', file_path))
                
            return True
        except:
            messagebox.showerror("Error", "Could not open file with default application")
            return False
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        return False

def load_medical_records(username, records_tree):
    """Load medical records from the database"""
    try:
        # Clear existing records
        for item in records_tree.get_children():
            records_tree.delete(item)
        
        # Get user ID from database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False
        
        user_id = result[0]
        
        # Get records
        cursor.execute(
            """SELECT id, file_name, record_type, record_date, provider, upload_date
               FROM medical_records 
               WHERE user_id = ? 
               ORDER BY upload_date DESC""",
            (user_id,)
        )
        
        records = cursor.fetchall()
        conn.close()
        
        # Add records to tree
        for record in records:
            rec_id, file_name, record_type, record_date, provider, upload_date = record
            
            records_tree.insert("", "end", iid=rec_id, values=(
                file_name,
                record_type,
                record_date,
                provider,
                upload_date
            ))
        
        return True
        
    except Exception as e:
        print(f"Error loading medical records: {str(e)}")
        return False

def get_record_details(record_id):
    """Get details of a specific medical record"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT file_name, record_type, record_date, provider, description, tags, upload_date, file_path
               FROM medical_records 
               WHERE id = ?""",
            (record_id,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        # Create a dictionary with record details
        record = {
            "file_name": result[0],
            "record_type": result[1],
            "record_date": result[2],
            "provider": result[3],
            "description": result[4],
            "tags": result[5].split(",") if result[5] else [],
            "upload_date": result[6],
            "file_path": result[7]
        }
        
        return record
        
    except Exception as e:
        print(f"Error getting record details: {str(e)}")
        return None

def create_medical_records_tab(parent, username):
    """Create the medical records tab"""
    # Ensure medical records directory exists
    if not os.path.exists(RECORDS_DIR):
        os.makedirs(RECORDS_DIR)
    
    # Create main frame
    main_frame = ttk.Frame(parent)
    main_frame.pack(fill="both", expand=True)
    
    # Create two columns
    left_frame = ttk.Frame(main_frame)
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
    
    right_frame = ttk.Frame(main_frame)
    right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
    
    # Left frame - Upload record
    upload_card = create_custom_card(left_frame, "Upload Medical Record")
    
    # File selection
    file_label = ttk.Label(upload_card, text="Selected File:")
    file_label.pack(anchor="w", pady=(0, 5))
    
    file_frame = ttk.Frame(upload_card)
    file_frame.pack(fill="x", pady=(0, 10))
    
    file_path_var = tk.StringVar()
    file_entry = ttk.Entry(file_frame, textvariable=file_path_var, width=30)
    file_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
    
    def browse_file():
        file_path = filedialog.askopenfilename(
            title="Select Medical Record",
            filetypes=(
                ("PDF files", "*.pdf"),
                ("Image files", "*.jpg *.jpeg *.png"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            )
        )
        if file_path:
            file_path_var.set(file_path)
    
    browse_button = tk.Button(file_frame, text="Browse Files",
        bg="#354aea",                 
        fg="#000000", command=browse_file)
    browse_button.pack(side="right")
    
    # Record type
    type_label = ttk.Label(upload_card, text="Record Type:")
    type_label.pack(anchor="w", pady=(0, 5))
    
    type_var = tk.StringVar()
    type_values = [
        "Lab Report", "Prescription", "Discharge Summary", 
        "Radiology Report", "Vaccination Record", "Other"
    ]
    type_combo = ttk.Combobox(upload_card, textvariable=type_var, values=type_values, width=25)
    type_combo.pack(fill="x", pady=(0, 10))
    
    # Record date
    date_label = ttk.Label(upload_card, text="Record Date:")
    date_label.pack(anchor="w", pady=(0, 5))
    
    date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
    date_entry = ttk.Entry(upload_card, textvariable=date_var, width=15)
    date_entry.pack(fill="x", pady=(0, 10))
    
    # Provider/Source
    provider_label = ttk.Label(upload_card, text="Provider/Source:")
    provider_label.pack(anchor="w", pady=(0, 5))
    
    provider_var = tk.StringVar()
    provider_entry = ttk.Entry(upload_card, textvariable=provider_var, width=25)
    provider_entry.pack(fill="x", pady=(0, 10))
    
    # Description
    desc_label = ttk.Label(upload_card, text="Description:")
    desc_label.pack(anchor="w", pady=(0, 5))
    
    desc_text = tk.Text(upload_card, height=6, width=40)
    desc_text.pack(fill="x", pady=(0, 10))
    
    # Tags
    tags_label = ttk.Label(upload_card, text="Tags (comma separated):")
    tags_label.pack(anchor="w", pady=(0, 5))
    
    tags_var = tk.StringVar()
    tags_entry = ttk.Entry(upload_card, textvariable=tags_var)
    tags_entry.pack(fill="x", pady=(0, 10))
    
    # Variable to track the currently selected record ID
    current_record_id = None
    
    # Upload button
    upload_button = tk.Button(
        upload_card,
        bg="#1ecd27",                 # Green background
        fg="#000000",
        text="Upload Record",
        command=lambda: add_medical_record(
            username, 
            file_path_var.get(), 
            type_var.get(), 
            date_var.get(), 
            provider_var.get(), 
            desc_text.get("1.0", tk.END).strip(), 
            tags_var.get(), 
            records_tree
        )
    )
    upload_button.pack(fill="x", pady=(10, 0), ipady=5)
    
    # Right frame - Record details
    details_card = create_custom_card(right_frame, "Record Details")
    
    # Details fields
    details_frame = ttk.Frame(details_card)
    details_frame.pack(fill="x", pady=(0, 10))
    
    # Create labels for details
    detail_labels = {}
    detail_values = {}
    
    for i, field in enumerate(["Filename:", "Type:", "Date:", "Provider:", "Uploaded:"]):
        # Label
        label = ttk.Label(details_frame, text=field, font=("Segoe UI", 10, "bold"))
        label.grid(row=i, column=0, sticky="w", padx=5, pady=2)
        detail_labels[field.replace(":", "")] = label
        
        # Value
        value = ttk.Label(details_frame, text="")
        value.grid(row=i, column=1, sticky="w", padx=5, pady=2)
        detail_values[field.replace(":", "")] = value
    
    # Description
    desc_label = ttk.Label(details_card, text="Description:", font=("Segoe UI", 10, "bold"))
    desc_label.pack(anchor="w", pady=(0, 5))
    
    desc_display = scrolledtext.ScrolledText(details_card, height=5, width=40, state="disabled")
    desc_display.pack(fill="x", pady=(0, 10))
    
    # Tags
    tags_display_label = ttk.Label(details_card, text="Tags:", font=("Segoe UI", 10, "bold"))
    tags_display_label.pack(anchor="w", pady=(0, 5))
    
    tags_display = ttk.Label(details_card, text="")
    tags_display.pack(anchor="w", pady=(0, 10))
    
    # Action buttons
    action_frame = ttk.Frame(details_card)
    action_frame.pack(fill="x", pady=(10, 0))
    
    view_button = tk.Button(
        action_frame,
        bg="#354aea",                 # Green background
        fg="#000000",
        text="View",
        command=lambda: view_medical_record(username, current_record_id)
    )
    view_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
    
    delete_button = tk.Button(
        action_frame,
        bg="#354aea",                 # Green background
        fg="#000000",
        text="Delete",
        command=lambda: delete_medical_record(username, current_record_id, records_tree)
    )
    delete_button.pack(side="left", fill="x", expand=True, padx=(5, 0))
    
    # Records list
    records_card = create_custom_card(right_frame, "Your Medical Records")
    
    # Create treeview for records
    records_frame = ttk.Frame(records_card)
    records_frame.pack(fill="both", expand=True)
    
    columns = ("Filename", "Type", "Date", "Provider", "Uploaded")
    records_tree = ttk.Treeview(records_frame, columns=columns, show="headings", height=8)
    
    # Configure columns
    for col in columns:
        records_tree.heading(col, text=col)
        records_tree.column(col, width=100)
    
    records_tree.pack(side="left", fill="both", expand=True)
    
    # Add scrollbar
    records_scrollbar = ttk.Scrollbar(records_frame, orient="vertical", command=records_tree.yview)
    records_scrollbar.pack(side="right", fill="y")
    records_tree.configure(yscrollcommand=records_scrollbar.set)
    
    # Load records
    load_medical_records(username, records_tree)
    
    # Function to handle record selection
    def on_record_select(event):
        nonlocal current_record_id
        
        selected = records_tree.selection()
        if not selected:
            return
        
        # Get the record ID
        record_id = selected[0]
        current_record_id = record_id
        
        # Get record details
        record = get_record_details(record_id)
        if not record:
            return
        
        # Update detail values
        detail_values["Filename"].config(text=record["file_name"])
        detail_values["Type"].config(text=record["record_type"])
        detail_values["Date"].config(text=record["record_date"])
        detail_values["Provider"].config(text=record["provider"])
        detail_values["Uploaded"].config(text=record["upload_date"])
        
        # Update description
        desc_display.config(state="normal")
        desc_display.delete("1.0", tk.END)
        desc_display.insert("1.0", record["description"])
        desc_display.config(state="disabled")
        
        # Update tags
        tags_display.config(text=", ".join(record["tags"]))
    
    # Bind selection event
    records_tree.bind("<<TreeviewSelect>>", on_record_select)
    
    return main_frame

# For testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Medical Records Test")
    root.geometry("900x600")
    
    frame = create_medical_records_tab(root, "test")
    
    root.mainloop()