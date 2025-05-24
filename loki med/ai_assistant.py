"""
Enhanced AI assistant implementation for Medical Assistant application.
This module creates a floating AI button that appears across all tabs and
provides assistant capabilities with scroll wheel support in the chat window.
"""

import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, scrolledtext
import time
import threading
import os
import sqlite3

# Import theme styles
from theme_styles import COLORS, FONTS

# Database path
DB_PATH = os.path.join("database", "medical_assistant.db")

# Enhanced AI responses database with task-specific responses
AI_RESPONSES = {
    "default": "I'm your Medical Assistant AI. How can I help you with your healthcare needs today?",
    "hello": "Hello! I'm here to assist you with your medical needs. How can I help you today?",
    "medication": "Medications should be taken as prescribed by your doctor. Would you like me to help you manage your medications or search for specific medication information?",
    "appointment": "To schedule an appointment, you can use the Appointments tab. Would you like me to help you navigate to that section and set up an appointment?",
    "headache": "Headaches can be caused by various factors including stress, dehydration, or lack of sleep. Over-the-counter pain relievers may help, but persistent headaches should be evaluated by a doctor. Would you like me to help you schedule an appointment?",
    "fever": "A fever is generally considered a temperature above 38°C (100.4°F). If you have a fever, rest and drink plenty of fluids. Contact your doctor if your fever persists more than a few days or is accompanied by severe symptoms. Would you like me to help you schedule a consultation?",
    "doctor": "You can connect with doctors through our Doctor Consultation tab. Would you like me to help you set up a consultation?",
    "buy medicine": "I can help you purchase medications through our Purchase Medicine tab. Would you like me to assist you with finding and ordering medications?",
    "health": "Monitoring your health regularly is important. You can track vital signs like pulse rate in our Health Monitoring tab. Would you like me to help you navigate to this section?",
    "records": "You can access and manage your medical records in the Medical Records tab. Would you like me to help you upload or view your records?",
    "reminder": "I can help you set medication reminders. Would you like me to assist you with setting up a new reminder?",
    "purchase": "You can purchase medicines through our Purchase Medicine tab. Would you like me to help you find and order medications?"
}

def simulate_ai_thinking(progress_bar):
    """Simulate AI thinking with progress bar animation"""
    for i in range(101):
        time.sleep(0.02)  # Adjust speed of animation
        progress_bar["value"] = i
        progress_bar.update()

def get_ai_response(query, root=None, notebook=None):
    """Get response from AI based on query keywords and perform actions if needed"""
    query = query.lower()
    
    # Handle navigation and action requests
    if root and notebook:
        # Switch to appropriate tab based on keywords
        if "medication" in query or "medicine" in query or "reminder" in query:
            if "manage" in query or "reminder" in query or "schedule" in query:
                notebook.select(1)  # Switch to Medication tab
                return "I've opened the Medication Management tab for you. Here you can manage your medications and set reminders."
            
        if "doctor" in query or "consult" in query:
            notebook.select(2)  # Switch to Doctor Consultation tab
            return "I've opened the Doctor Consultation tab for you. Here you can connect with doctors via video call."
            
        if "buy" in query or "purchase" in query or "order" in query:
            notebook.select(3)  # Switch to Purchase Medicine tab
            return "I've opened the Purchase Medicine tab for you. Here you can browse and purchase medications."
            
        if "health" in query or "monitor" in query or "pulse" in query:
            notebook.select(4)  # Switch to Health Monitoring tab
            return "I've opened the Health Monitoring tab for you. Here you can track your health metrics."
            
        if "appointment" in query or "schedule" in query or "book" in query:
            notebook.select(5)  # Switch to Appointments tab
            return "I've opened the Appointments tab for you. Here you can schedule and manage your appointments."
            
        if "record" in query or "document" in query or "history" in query:
            notebook.select(6)  # Switch to Medical Records tab
            return "I've opened the Medical Records tab for you. Here you can manage your medical records."
    
    # Check for keywords in the query for standard responses
    for keyword, response in AI_RESPONSES.items():
        if keyword != "default" and keyword in query:
            return response
    
    # If no specific match, return default response
    return AI_RESPONSES["default"]

def create_ai_button(parent, notebook=None):
    """Create a persistent AI button that floats above all tabs"""
    
    # Create a floating frame for the AI button
    ai_frame = tk.Frame(
        parent,
        bg=COLORS["card_bg"],           # Card background
        bd=2,                           # Border width
        relief="raised"                 # Raised appearance
    )
    
    # Position in bottom right corner with padding
    parent.update_idletasks()
    
    # Create the AI button with a distinctive look
    ai_button = tk.Button(
        ai_frame,
        text="AI Assistant",
        font=FONTS["body_bold"],
        bg=COLORS["primary"],           # Primary color background
        fg=COLORS["background"],        # White text
        activebackground=COLORS["primary_dark"],  # Darker when clicked
        activeforeground=COLORS["background"],    # White text when clicked
        padx=15,
        pady=10,
        relief="raised",
        bd=2,
        cursor="hand2",                 # Hand cursor on hover
        command=lambda: show_ai_assistant(parent, notebook)
    )
    ai_button.pack(padx=2, pady=2)
    
    # Function to position the button in the corner
    def position_button():
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # Bottom right with padding
        x = parent_width - ai_frame.winfo_reqwidth() - 20
        y = parent_height - ai_frame.winfo_reqheight() - 20
        
        ai_frame.place(x=x, y=y)
    
    # Position initially
    parent.update_idletasks()
    position_button()
    
    # Reposition when window is resized
    parent.bind("<Configure>", lambda e: position_button())
    
    return ai_frame

def show_ai_assistant(parent, notebook=None):
    """Show the AI assistant window when button is clicked"""
    assistant_window = Toplevel(parent)
    assistant_window.title("AI Medical Assistant")
    assistant_window.geometry("600x500")
    assistant_window.minsize(400, 400)
    
    # Apply same colors from theme
    assistant_window.configure(bg=COLORS["background"])
    
    # Make window appear on top
    assistant_window.transient(parent)
    assistant_window.grab_set()
    
    # Create main frame
    main_frame = ttk.Frame(assistant_window, padding=20)
    main_frame.pack(fill="both", expand=True)
    
    # Title with primary color
    title_label = ttk.Label(
        main_frame, 
        text="AI Medical Assistant", 
        font=FONTS["title"],
        foreground=COLORS["primary"]
    )
    title_label.pack(pady=(0, 20))
    
    # Create chat display area with scrollbar
    chat_frame = ttk.Frame(main_frame)
    chat_frame.pack(fill="both", expand=True, pady=(0, 10))
    
    chat_display = scrolledtext.ScrolledText(
        chat_frame,
        wrap=tk.WORD,
        font=FONTS["body"],
        bg=COLORS["background_light"],
        relief="flat",
        state="disabled"
    )
    chat_display.pack(fill="both", expand=True)
    
    # Add mouse wheel scrolling support
    def _on_mousewheel(event):
        chat_display.yview_scroll(int(-1*(event.delta/120)), "units")
    
    # Bind mouse wheel event to the chat display
    chat_display.bind("<MouseWheel>", _on_mousewheel)
    
    # Progress bar (initially hidden)
    progress_bar = ttk.Progressbar(
        main_frame,
        orient="horizontal",
        length=200,
        mode="determinate"
    )
    
    # Initial welcome message
    chat_display.configure(state="normal")
    chat_display.insert(tk.END, "AI Assistant: " + AI_RESPONSES["default"] + "\n\n")
    chat_display.configure(state="disabled")
    chat_display.see(tk.END)
    
    # Input area
    input_frame = ttk.Frame(main_frame)
    input_frame.pack(fill="x", pady=(10, 0))
    
    user_input = ttk.Entry(
        input_frame,
        font=FONTS["body"]
    )
    user_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
    user_input.focus_set()
    
    def send_message(event=None):
        """Process user input and generate AI response"""
        query = user_input.get().strip()
        if not query:
            return
        
        # Clear input field
        user_input.delete(0, tk.END)
        
        # Display user message
        chat_display.configure(state="normal")
        chat_display.insert(tk.END, f"You: {query}\n\n")
        chat_display.configure(state="disabled")
        chat_display.see(tk.END)
        
        # Show thinking progress bar
        progress_bar.pack(pady=(5, 5))
        
        # Simulate AI thinking in a separate thread
        thinking_thread = threading.Thread(
            target=lambda: simulate_thinking_and_respond(query)
        )
        thinking_thread.daemon = True
        thinking_thread.start()
    
    def simulate_thinking_and_respond(query):
        """Simulate AI thinking and then respond"""
        # Simulate thinking
        simulate_ai_thinking(progress_bar)
        
        # Get AI response
        response = get_ai_response(query, parent, notebook)
        
        # Hide progress bar
        progress_bar.pack_forget()
        
        # Display AI response
        chat_display.configure(state="normal")
        chat_display.insert(tk.END, f"AI Assistant: {response}\n\n")
        chat_display.configure(state="disabled")
        chat_display.see(tk.END)
    
    # Suggested queries section
    suggestions_frame = ttk.LabelFrame(main_frame, text="Suggested Questions")
    suggestions_frame.pack(fill="x", pady=(0, 10))
    
    suggestions = [
        "Help me manage my medications",
        "I need to see a doctor",
        "How do I buy medicine?",
        "Set up a health reminder",
        "Book an appointment"
    ]
    
    for suggestion in suggestions:
        suggestion_btn = ttk.Button(
            suggestions_frame,
            text=suggestion,
            style="Link.TButton",
            command=lambda s=suggestion: (user_input.delete(0, tk.END), 
                                        user_input.insert(0, s),
                                        send_message())
        )
        suggestion_btn.pack(anchor="w", padx=5, pady=2)
    
    # Send button
    send_button = ttk.Button(
        input_frame,
        text="Send",
        command=send_message,
        style="Primary.TButton"
    )
    send_button.pack(side="right")
    
    # Bind Enter key to send message
    user_input.bind("<Return>", send_message)
    
    # Close button
    close_button = ttk.Button(
        main_frame,
        text="Close",
        command=assistant_window.destroy
    )
    close_button.pack(pady=(10, 0))
    
    # Center window on parent
    assistant_window.update_idletasks()
    width = assistant_window.winfo_width()
    height = assistant_window.winfo_height()
    x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
    y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)
    assistant_window.geometry(f"+{x}+{y}")