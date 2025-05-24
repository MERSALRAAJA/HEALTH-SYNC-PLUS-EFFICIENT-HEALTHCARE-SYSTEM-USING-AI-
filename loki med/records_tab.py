"""
Medical records tab UI
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
        tags_str = ",".join(tags) if isinstance(tags, list) else tags
        
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
            """SELECT file_name, record_type, record_date, provider, description, tags
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
            "tags": result[5].split(",") if result[5] else []
        }
        
        return record
        
    except Exception as e:
        print(f"Error getting record details: {str(e)}")
        return None

def create_records_tab(parent, username):
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
    
    # Left frame - Records list
    list_card = create_custom_card(left_frame, "Your Medical Records")
    
    # Create treeview for records
    records_frame = ttk.Frame(list_card)
    records_frame.pack(fill="both", expand=True)
    
    columns = ("Filename", "Type", "Date", "Provider", "Uploaded")
    records_tree = ttk.Treeview(records_frame, columns=columns, show="headings", height=15)
    
    # Configure columns
    records_tree.heading("Filename", text="Filename")
    records_tree.heading("Type", text="Type")
    records_tree.heading("Date", text="Date")
    records_tree.heading("Provider", text="Provider")
    records_tree.heading("Uploaded", text="Uploaded")
    
    records_tree.column("Filename", width=150)
    records_tree.column("Type", width=100)
    records_tree.column("Date", width=80)
    records_tree.column("Provider", width=120)
    records_tree.column("Uploaded", width=120)
    
    records_tree.pack(side="left", fill="both", expand=True)
    
    # Add scrollbar
    records_scrollbar = ttk.Scrollbar(records_frame, orient="vertical", command=records_tree.yview)
    records_scrollbar.pack(side="right", fill="y")
    records_tree.configure(yscrollcommand=records_scrollbar.set)
    
    # Load records
    load_medical_records(username, records_tree)
    
    # Button frame
    button_frame = ttk.Frame(list_card)
    button_frame.pack(fill="x", pady=(10, 0))
    
    # Refresh button
    refresh_button = ttk.Button(
        button_frame,
        text="Refresh",
        command=lambda: load_medical_records(username, records_tree)
    )
    refresh_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
    
    # View button
    view_button = ttk.Button(
        button_frame,
        text="View Selected",
        command=lambda: view_medical_record(
            username, 
            records_tree.selection()[0] if records_tree.selection() else None
        )
    )
    view_button.pack(side="left", fill="x", expand=True, padx=5)
    
    # Delete button
    delete_button = ttk.Button(
        button_frame,
        text="Delete Selected",
        command=lambda: delete_medical_record(
            username, 
            records_tree.selection()[0] if records_tree.selection() else None, 
            records_tree
        )
    )
    delete_button.pack(side="right", fill="x", expand=True)
    
    # Right frame - Add record
    upload_card = create_custom_card(right_frame, "Upload Medical Record")
    
    # File selection
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
    
    browse_button = ttk.Button(file_frame, text="Browse", command=browse_file)
    browse_button.pack(side="right")
    
    # Record type
    type_frame = ttk.Frame(upload_card)
    type_frame.pack(fill="x", pady=(0, 10))
    
    type_label = ttk.Label(type_frame, text="Record Type:")
    type_label.pack(side="left", padx=(0, 5))
    
    type_var = tk.StringVar()
    type_values = [
        "Lab Report", "Prescription", "Discharge Summary", 
        "Radiology Report", "Vaccination Record", "Other"
    ]
    type_combo = ttk.Combobox(type_frame, textvariable=type_var, values=type_values, width=15)
    type_combo.pack(side="left", fill="x", expand=True)
    
    # Record date
    date_frame = ttk.Frame(upload_card)
    date_frame.pack(fill="x", pady=(0, 10))
    
    date_label = ttk.Label(date_frame, text="Record Date:")
    date_label.pack(side="left", padx=(0, 5))
    
    date_var = tk.StringVar(value=datetime.now().strftime("%d-%m-%Y"))
    date_entry = ttk.Entry(date_frame, textvariable=date_var, width=12)
    date_entry.pack(side="left")
    
    # Provider
    provider_frame = ttk.Frame(upload_card)
    provider_frame.pack(fill="x", pady=(0, 10))
    
    provider_label = ttk.Label(provider_frame, text="Provider:")
    provider_label.pack(side="left", padx=(0, 5))
    
    provider_var = tk.StringVar()
    provider_entry = ttk.Entry(provider_frame, textvariable=provider_var, width=25)
    provider_entry.pack(side="left", fill="x", expand=True)
    
    # Description
    desc_label = ttk.Label(upload_card, text="Description:")
    desc_label.pack(anchor="w")
    
    desc_text = tk.Text(upload_card, height=4, width=40)
    desc_text.pack(fill="x", pady=(5, 10))
    
    # Tags
    tags_frame = ttk.Frame(upload_card)
    tags_frame.pack(fill="x", pady=(0, 10))
    
    tags_label = ttk.Label(tags_frame, text="Tags (comma separated):")
    tags_label.pack(side="left", padx=(0, 5))
    
    tags_var = tk.StringVar()
    tags_entry = ttk.Entry(tags_frame, textvariable=tags_var)
    tags_entry.pack(side="left", fill="x", expand=True)
    
    # Upload button
    upload_button = ttk.Button(
        upload_card,
        text="Upload Record",
        command=lambda: add_medical_record(
            username, 
            file_path_var.get(), 
            type_var.get(), 
            date_var.get(), 
            provider_var.get(), 
            desc_text.get("1.0", tk.END).strip(), 
            tags_var.get().split(","), 
            records_tree
        )
    )
    upload_button.pack(fill="x", pady=(10, 0), ipady=5)
    
    # Record details card
    details_card = create_custom_card(right_frame, "Record Details")
    
    # Create scrollable text area for details
    details_text = scrolledtext.ScrolledText(details_card, height=10, width=40, state="disabled")
    details_text.pack(fill="both", expand=True, pady=10)
    
    # Function to show record details when selected
    def on_record_select(event):
        selected = records_tree.selection()
        if not selected:
            return
        
        # Get the record ID
        record_id = selected[0]
        
        # Get record details
        record = get_record_details(record_id)
        if not record:
            return
        
        # Display details
        details_text.config(state="normal")
        details_text.delete("1.0", tk.END)
        
        details = f"""Filename: {record['file_name']}
Type: {record['record_type']}
Date: {record['record_date']}
Provider: {record['provider']}

Description:
{record['description']}

Tags: {', '.join(record['tags'])}
"""
        
        details_text.insert("1.0", details)
        details_text.config(state="disabled")
    
    # Bind selection event
    records_tree.bind("<<TreeviewSelect>>", on_record_select)
    
    # Information card
    info_card = create_custom_card(right_frame, "Record Management Information")
    
    info_text = ttk.Label(
        info_card, 
        text="• Keep digital copies of all your medical documents\n"
            "• Supported file types: PDF, JPG, PNG, TXT\n"
            "• Adding tags helps you find records easily\n"
            "• Regular backups of your records are recommended\n"
            "• Always keep original copies of important documents",
        wraplength=400,
        justify="left"
    )
    info_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    return main_frame

# For testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Medical Records Test")
    root.geometry("900x600")
    
    frame = create_records_tab(root, "test")
    
    root.mainloop()