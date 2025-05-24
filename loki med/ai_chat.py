"""
Enhanced AI Chat Window Implementation
Creates a floating chat window that allows users to interact with the AI assistant,
with a scrollable suggestions section.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, font
import time
import threading
import random
import os
import sys

class AIChatWindow:
    """Class to manage the AI chat window functionality"""
    
    def __init__(self, parent):
        self.parent = parent
        self.chat_window = None
        self.suggestions = [
            "Help me manage my medications",
            "I need to see a doctor",
            "How do I buy medicine?",
            "Set up a health reminder",
            "Book an appointment",
            "What are normal pulse rates?",
            "How do I upload medical records?",
            "When should I take my medication?",
            "What are the side effects of Paracetamol?",
            "How can I track my health readings?",
            "What are the symptoms of high blood pressure?",
            "How do I find a specialist doctor?",
            "Can you explain my prescription?",
            "What's the difference between Ibuprofen and Paracetamol?",
            "How often should I check my blood pressure?"
        ]
        
    def show_window(self):
        """Display the AI chat window"""
        if self.chat_window is not None:
            # If window exists but is destroyed, recreate it
            if not self.chat_window.winfo_exists():
                self._create_window()
            # If window exists and is minimized, restore it
            else:
                self.chat_window.deiconify()
                self.chat_window.lift()
            return
            
        # Create new window if it doesn't exist
        self._create_window()
        
    def _create_window(self):
        """Create the chat window UI"""
        self.chat_window = tk.Toplevel(self.parent)
        self.chat_window.title("AI Medical Assistant")
        self.chat_window.geometry("500x600")
        self.chat_window.minsize(300, 400)
        
        # Apply theme colors
        bg_color = "#ffffff"
        primary_color = "#4a6fa5"
        accent_color = "#ff4081"
        
        # Configure window background
        self.chat_window.configure(bg=bg_color)
        
        # Create main frame with padding
        main_frame = ttk.Frame(self.chat_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title with primary color
        title_label = ttk.Label(
            main_frame, 
            text="AI Medical Assistant", 
            font=("Segoe UI", 16, "bold"),
            foreground=primary_color
        )
        title_label.pack(pady=(0, 20))
        
        # Create chat display area with scrollbar
        chat_frame = ttk.Frame(main_frame)
        chat_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg="#f8f9fa",
            relief="flat",
            state="disabled"
        )
        self.chat_display.pack(fill="both", expand=True)
        
        # Add mouse wheel scrolling support
        def _on_mousewheel(event):
            self.chat_display.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bind mouse wheel event to the chat display
        self.chat_display.bind("<MouseWheel>", _on_mousewheel)
        
        # Progress bar (initially hidden)
        self.progress_bar = ttk.Progressbar(
            main_frame,
            orient="horizontal",
            length=200,
            mode="determinate"
        )
        
        # Initial welcome message
        self._add_ai_message("I'm your Medical Assistant AI. How can I help you with your healthcare needs today?")
        
        # Input area
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill="x", pady=(10, 0))
        
        self.user_input = ttk.Entry(
            input_frame,
            font=("Segoe UI", 10)
        )
        self.user_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.user_input.focus_set()
        
        # Send button
        send_button = ttk.Button(
            input_frame,
            text="Send",
            style="Primary.TButton",
            command=self._send_message
        )
        send_button.pack(side="right")
        
        # Bind Enter key to send message
        self.user_input.bind("<Return>", lambda event: self._send_message())
        
        # Suggested queries section with scrollable frame
        suggestions_frame = ttk.LabelFrame(main_frame, text="Suggested Questions")
        suggestions_frame.pack(fill="x", pady=(10, 10))
        
        # Create canvas for scrolling
        suggestion_canvas = tk.Canvas(suggestions_frame, height=100, highlightthickness=0, bg=bg_color)
        suggestion_scrollbar = ttk.Scrollbar(suggestions_frame, orient="vertical", command=suggestion_canvas.yview)
        
        # Configure scrollbar with canvas
        suggestion_canvas.configure(yscrollcommand=suggestion_scrollbar.set)
        
        # Pack canvas and scrollbar
        suggestion_scrollbar.pack(side="right", fill="y")
        suggestion_canvas.pack(side="left", fill="both", expand=True)
        
        # Create inner frame for suggestions
        suggestions_inner = ttk.Frame(suggestion_canvas)
        
        # Create window in canvas
        canvas_window = suggestion_canvas.create_window((0, 0), window=suggestions_inner, anchor="nw", width=suggestion_canvas.winfo_width())
        
        # Update canvas scrollregion when inner frame changes size
        def configure_scroll_region(event):
            suggestion_canvas.configure(scrollregion=suggestion_canvas.bbox("all"))
        
        suggestions_inner.bind("<Configure>", configure_scroll_region)
        
        # Update inner frame width when canvas changes size
        def configure_canvas_window(event):
            suggestion_canvas.itemconfig(canvas_window, width=event.width)
        
        suggestion_canvas.bind("<Configure>", configure_canvas_window)
        
        # Add mouse wheel scrolling to suggestions canvas
        def _on_suggestion_mousewheel(event):
            suggestion_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        suggestion_canvas.bind("<MouseWheel>", _on_suggestion_mousewheel)
        suggestions_inner.bind("<MouseWheel>", _on_suggestion_mousewheel)
        
        # Add suggestion buttons
        for suggestion in self.suggestions:
            # Create a style for the suggestion button
            suggestion_btn = ttk.Button(
                suggestions_inner,
                text=suggestion,
                style="Link.TButton",
                command=lambda s=suggestion: (self._set_input_text(s))
            )
            suggestion_btn.pack(anchor="w", padx=5, pady=2, fill="x")
            
            # Also add mousewheel binding to each button
            suggestion_btn.bind("<MouseWheel>", _on_suggestion_mousewheel)
        
        # Close button
        close_button = ttk.Button(
            main_frame,
            text="Close",
            command=self.chat_window.destroy
        )
        close_button.pack(pady=(10, 0))
        
        # Center window on parent
        self._center_window()
    
    def _center_window(self):
        """Center window on parent"""
        self.chat_window.update_idletasks()
        width = self.chat_window.winfo_width()
        height = self.chat_window.winfo_height()
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() // 2) - (width // 2)
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() // 2) - (height // 2)
        self.chat_window.geometry(f"+{x}+{y}")
    
    def _set_input_text(self, text):
        """Set the input text field and send the message"""
        self.user_input.delete(0, tk.END)
        self.user_input.insert(0, text)
        self._send_message()
    
    def _send_message(self):
        """Process user input and generate AI response"""
        query = self.user_input.get().strip()
        if not query:
            return
        
        # Clear input field
        self.user_input.delete(0, tk.END)
        
        # Display user message
        self._add_user_message(query)
        
        # Show thinking progress bar
        self.progress_bar.pack(pady=(5, 5))
        
        # Simulate AI thinking in a separate thread
        thinking_thread = threading.Thread(
            target=lambda: self._simulate_thinking_and_respond(query)
        )
        thinking_thread.daemon = True
        thinking_thread.start()
    
    def _add_user_message(self, message):
        """Add a user message to the chat display"""
        self.chat_display.configure(state="normal")
        self.chat_display.insert(tk.END, f"You: {message}\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see(tk.END)
    
    def _add_ai_message(self, message):
        """Add an AI message to the chat display"""
        self.chat_display.configure(state="normal")
        self.chat_display.insert(tk.END, f"AI Assistant: {message}\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see(tk.END)
    
    def _simulate_thinking_and_respond(self, query):
        """Simulate AI thinking and then respond"""
        # Simulate thinking with progress bar
        for i in range(101):
            time.sleep(0.02)  # Adjust speed of animation
            self.progress_bar["value"] = i
            self.chat_window.update_idletasks()
        
        # Hide progress bar
        self.progress_bar.pack_forget()
        
        # Get AI response (simple keyword matching for this example)
        response = self._get_ai_response(query)
        
        # Display AI response
        self._add_ai_message(response)
    
    def _get_ai_response(self, query):
        """Get response from AI based on query keywords"""
        query = query.lower()
        
        # Simple keyword-based responses
        if "medication" in query or "medicine" in query:
            return "Medications should be taken as prescribed by your doctor. Always check the dosage and timing instructions on your prescription. Is there a specific medication you need information about?"
        
        elif "appointment" in query or "book" in query or "schedule" in query:
            return "To schedule an appointment, you can use the Appointments tab. Would you like me to help you navigate to that section?"
        
        elif "doctor" in query or "physician" in query:
            return "You can connect with doctors through our Doctor Consultation tab. Would you like me to help you set up a consultation?"
        
        elif "buy" in query or "purchase" in query:
            return "You can purchase medications through our Purchase Medicine tab. Would you like me to help you find and order medications?"
        
        elif "health" in query or "monitor" in query or "reading" in query:
            return "Monitoring your health regularly is important. You can track vital signs like pulse rate in our Health Monitoring tab. Would you like me to help you navigate to this section?"
        
        elif "record" in query or "document" in query:
            return "You can access and manage your medical records in the Medical Records tab. Would you like me to help you upload or view your records?"
        
        elif "reminder" in query or "alert" in query:
            return "I can help you set medication reminders. Would you like me to assist you with setting up a new reminder?"
        
        elif "hello" in query or "hi" in query:
            return "Hello! I'm here to assist you with your medical needs. How can I help you today?"
            
        elif "headache" in query or "pain" in query:
            return "Headaches can be caused by various factors including stress, dehydration, or lack of sleep. Over-the-counter pain relievers may help, but persistent headaches should be evaluated by a doctor. Would you like me to help you schedule an appointment?"
            
        elif "fever" in query or "temperature" in query:
            return "A fever is generally considered a temperature above 38°C (100.4°F). If you have a fever, rest and drink plenty of fluids. Contact your doctor if your fever persists more than a few days or is accompanied by severe symptoms."
            
        else:
            return "I'm here to help with your healthcare needs. You can ask me about medications, appointments, health monitoring, or medical records. How can I assist you today?"

def create_ai_button(parent):
    """Create a floating AI button"""
    # Create AI chat manager
    ai_chat = AIChatWindow(parent)
    
    # Create a floating frame for the AI button
    ai_frame = tk.Frame(
        parent,
        bg="#ffffff",           # Card background
        bd=2,                   # Border width
        relief="raised"         # Raised appearance
    )
    
    # Create the AI button with a distinctive look
    ai_button = tk.Button(
        ai_frame,
        text="AI Chat",
        font=("Segoe UI", 12, "bold"),
        bg="#ff4081",           # Accent color background
        fg="#ffffff",           # White text
        activebackground="#c60055",  # Darker accent when clicked
        activeforeground="#ffffff",  # White text when clicked
        padx=15,
        pady=10,
        relief="raised",
        bd=2,
        cursor="hand2",         # Hand cursor on hover
        command=ai_chat.show_window    # Show AI chat window
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

# For standalone testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("AI Chat Test")
    root.geometry("800x600")
    
    # Configure ttk styles
    style = ttk.Style()
    style.configure("TButton", font=("Segoe UI", 10))
    style.configure("Primary.TButton", background="#4a6fa5", foreground="#ffffff")
    style.configure("Link.TButton", background="#ffffff", foreground="#4a6fa5", 
                   borderwidth=0, font=("Segoe UI", 10, "underline"))
    
    # Add AI button
    ai_btn = create_ai_button(root)
    
    root.mainloop()