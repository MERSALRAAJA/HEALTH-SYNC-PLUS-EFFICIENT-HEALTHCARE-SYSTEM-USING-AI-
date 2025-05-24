
"""
Enhanced main.py file with AI assistant integration and medication tab.
This is the main entry point for the Medical Assistant application.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from PIL import Image, ImageTk
import time

def show_splash_screen():
    """
    Shows a splash screen with the medical.jpg image for 3 seconds,
    then destroys the window.
    """
    # Create splash window
    root = tk.Tk()
    
    # Remove window decorations
    root.overrideredirect(True)
    
    # Make it appear on top of everything
    root.attributes("-topmost", True)
    
    try:
        # Load the medical.jpg image
        img = Image.open("medical.jpg")
        img = img.resize((300, 300))  # Resize as needed
    except Exception as e:
        print(f"Error loading image: {e}")
        # Create a basic placeholder if image not found
        img = Image.new('RGB', (300, 300), color='white')
    
    # Convert to Tkinter format
    photo = ImageTk.PhotoImage(img)
    
    # Calculate window size and position (centered)
    width, height = 400, 450
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    # Create a frame with white background
    frame = tk.Frame(root, bg="white")
    frame.pack(fill=tk.BOTH, expand=True)
    
    # Display the image
    img_label = tk.Label(frame, image=photo, bg="white")
    img_label.pack(pady=(30, 10))
    
    # Add welcome text
    welcome = tk.Label(frame, text="Welcome", font=("Arial", 24, "bold"), fg="#0057b8", bg="white")
    welcome.pack()
    
    subtitle = tk.Label(frame, text="to Medical Care", font=("Arial", 18), fg="#29abe2", bg="white")
    subtitle.pack(pady=5)
    
    # Update the window to make sure everything is displayed
    root.update()
    
    # Wait for 3 seconds
    time.sleep(3)
    
    # Close the splash screen
    root.destroy()


# Add current directory to Python path
current_dir = os.path.abspath(os.path.dirname(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import modules
try:
    from theme_styles import COLORS, FONTS, setup_styles
except ImportError:
    # Default colors and fonts if theme_styles is not available
    COLORS = {
        "primary": "#0066ff",
        "background": "#00fffbc3",
        "text": "#333333",
        "text_secondary": "#666666"
    }
    FONTS = {
        "display": ("Segoe UI", 24, "bold"),
        "title": ("Segoe UI", 18, "bold"),
        "heading": ("Segoe UI", 14, "bold"),
        "body": ("Segoe UI", 10),
        "caption": ("Segoe UI", 9)
    }
    
    
    
    def setup_styles():
        style = ttk.Style()
        style.configure("Card.TFrame", relief="solid", borderwidth=1)
        return style

from db_manager import check_database, ensure_directories_exist
from user_auth import show_login_window

# Import tabs
try:
    # Import the enhanced medication manager
    from enhanced_medication_manager_ui import create_medication_manager_tab
except ImportError:
    print("Enhanced medication manager not found - will use fallback.")
    try:
        from medication_management_tab import create_medication_manager_tab
    except ImportError:
        print("Medication management tab not found - will use placeholder.")

# Import the AI assistant if available
try:
    from ai_assistant import create_ai_button, show_ai_assistant
    has_ai_assistant = True
except ImportError:
    print("AI assistant module not found - AI features will be disabled.")
    has_ai_assistant = False

def create_main_window(username):
    """Create the main application window after successful login"""
    root = tk.Tk()
    root.title("Medical Assistant")
    root.geometry("1000x700")
    
    # Setup styles
    setup_styles()
    
    # Create a header frame
    header_frame = ttk.Frame(root)
    header_frame.pack(fill="x", padx=0, pady=0)
    
    # App title with custom styling
    app_title = ttk.Label(
        header_frame, 
        text="Medical Assistant", 
        font=FONTS["title"],
        foreground=COLORS.get("primary", "#0066ff")
    )
    app_title.pack(side="left", padx=20, pady=10)
    
    # User info and logout frame
    user_frame = ttk.Frame(header_frame)
    user_frame.pack(side="right", padx=20, pady=10)
    
    # Username display
    user_label = ttk.Label(
        user_frame, 
        text=f"Welcome, {username}", 
        font=FONTS["body"]
    )
    user_label.pack(side="left", padx=(0, 10))
    
    # Settings button
    settings_button = tk.Button(
        user_frame,
        bg="#223edf",        # Blue background
        fg="#ffffff",
        text="Settings"
    )
    settings_button.pack(side="left", padx=5)
    
    # Try to create settings menu if available
    try:
        from settings_menu import create_settings_menu
        settings_menu = create_settings_menu(root, settings_button, username)
    except ImportError:
        # Fallback if settings_menu is not implemented
        settings_button.config(
            command=lambda: messagebox.showinfo("Settings", "Settings functionality will be implemented.")
        )
    
    # Logout Button
    logout_button = tk.Button(
        user_frame,
        bg="#223edf",        # Blue background
        fg="#ffffff", 
        text="Logout",
        command=lambda: logout(root)
    )
    logout_button.pack(side="left")
    
    def logout(root):
        root.destroy()
        show_login_window()
    
    # Main content area
    main_frame = ttk.Frame(root)
    main_frame.pack(fill="both", expand=True, padx=15, pady=15)
    
    # Create tabs
    tab_control = ttk.Notebook(main_frame)
    
    # Create dashboard tab
    dashboard_tab = ttk.Frame(tab_control)
    tab_control.add(dashboard_tab, text="Dashboard")
    try:
        from dashboard import create_dashboard_tab
        create_dashboard_tab(dashboard_tab, username)
    except ImportError:
        # Create simple dashboard if dashboard module is not available
        create_simple_dashboard(dashboard_tab, username)
    
    # Create medication management tab
    medication_tab = ttk.Frame(tab_control)
    tab_control.add(medication_tab, text="Medication Management")
    
    try:
        create_medication_manager_tab(medication_tab, username)
    except NameError:
        # If the function import failed earlier, use a placeholder
        create_placeholder_tab(medication_tab, "Medication Management")
    
    # Create doctor consultation tab
    consultation_tab = ttk.Frame(tab_control)
    tab_control.add(consultation_tab, text="Doctor Consultation")
    try:
        from doctor_consultation_tab import create_doctor_consultation_tab
        create_doctor_consultation_tab(consultation_tab, username)
    except ImportError:
        create_placeholder_tab(consultation_tab, "Doctor Consultation")
    
    # Create purchase medicine tab
    purchase_tab = ttk.Frame(tab_control)
    tab_control.add(purchase_tab, text="Purchase Medicine")
    try:
        from purchase_medicine_tab import create_purchase_medicine_tab
        create_purchase_medicine_tab(purchase_tab, username)
    except ImportError:
        create_placeholder_tab(purchase_tab, "Purchase Medicine")
    
    # Create health monitoring tab
    health_tab = ttk.Frame(tab_control)
    tab_control.add(health_tab, text="Health Monitoring")
    try:
        from health_monitoring_tab import create_health_monitoring_tab
        create_health_monitoring_tab(health_tab, username)
    except ImportError:
        create_placeholder_tab(health_tab, "Health Monitoring")
    
    # Create appointments tab
    appointment_tab = ttk.Frame(tab_control)
    tab_control.add(appointment_tab, text="Appointments")
    try:
        from appointment_tab import create_appointment_tab
        create_appointment_tab(appointment_tab, username)
    except ImportError:
        create_placeholder_tab(appointment_tab, "Appointments")
    
    # Create medical records tab
    records_tab = ttk.Frame(tab_control)
    tab_control.add(records_tab, text="Medical Records")
    try:
        from medical_records_tab import create_medical_records_tab
        create_medical_records_tab(records_tab, username)
    except ImportError:
        create_placeholder_tab(records_tab, "Medical Records")
    
    # Pack the tab control
    tab_control.pack(expand=1, fill="both")
    
    # Add AI button if available
    
    if has_ai_assistant:
        # Create a frame for the AI button with updated colors
        ai_frame = tk.Frame(
            root,
            bg="#000000",  # Light blue background
            bd=2,
            relief="raised",
            highlightbackground="#4a90e2",  # Blue border
            highlightthickness=2
        )

        # Create the AI button with updated styling
        ai_button = tk.Button(
            ai_frame,
            text="AI Assistant",
            font=("Segoe UI", 12, "bold"),
            bg="#483dbb",  # Brighter blue background
            fg="#ff0000",  # White text
            activebackground="#483dbb",  # Darker blue when clicked
            activeforeground="#ff0404",  # White text when clicked
            padx=15,
            pady=10,
            relief="raised",
            bd=2,
            cursor="hand2",
            command=lambda: show_ai_assistant(root, tab_control)
        )
        ai_button.pack(padx=2, pady=2)

        # Position the button in the bottom right corner
        def position_button():
            parent_width = root.winfo_width()
            parent_height = root.winfo_height()
            
            # Position at bottom right with padding
            x = parent_width - ai_frame.winfo_reqwidth() - 30  # 30px from right
            y = parent_height - ai_frame.winfo_reqheight() - 30  # 30px from bottom
            
            ai_frame.place(x=x, y=y)

        # Position initially and when the window is resized
        root.update_idletasks()
        position_button()
        root.bind("<Configure>", lambda e: position_button())

        # Ensure the button stays on top of other elements
        ai_frame.lift()

        # Make sure the button raises to the top after tab changes
        tab_control.bind("<<NotebookTabChanged>>", lambda e: ai_frame.lift())
    
    # Center window on screen
    center_window(root)
    
    # Start the main loop
    root.mainloop()

def create_simple_dashboard(parent, username):
    """Create a simple dashboard for when the dashboard module is not available"""
    frame = ttk.Frame(parent, padding=20)
    frame.pack(fill="both", expand=True)
    
    # Welcome header
    welcome_label = ttk.Label(
        frame,
        text=f"Welcome, {username}!",
        font=FONTS["display"]
    )
    welcome_label.pack(anchor="w", pady=(0, 20))
    
    # Current date
    from datetime import datetime
    date_label = ttk.Label(
        frame,
        text=datetime.now().strftime("%A, %d %B %Y"),
        font=FONTS["body"],
        foreground=COLORS.get("text_secondary", "#666666")
    )
    date_label.pack(anchor="w", pady=(0, 30))
    
    # Simple info cards in a grid
    cards_frame = ttk.Frame(frame)
    cards_frame.pack(fill="x", expand=True)
    
    # Create 2x2 grid of info cards
    info_cards = [
        {"title": "UPCOMING APPOINTMENTS", "value": "2", "desc": "Next: Tomorrow, 14:30"},
        {"title": "MEDICATION REMINDERS", "value": "3", "desc": "Next: Today, 20:00"},
        {"title": "HEALTH STATUS", "value": "Good", "desc": "Last check: Today"},
        {"title": "MEDICAL RECORDS", "value": "5", "desc": "Last update: 3 days ago"}
    ]
    
    for i, card_info in enumerate(info_cards):
        card = ttk.Frame(cards_frame, style="Card.TFrame", padding=15)
        card.grid(row=i//2, column=i%2, sticky="nsew", padx=5, pady=5)
        
        ttk.Label(card, text=card_info["title"], font=FONTS["caption"], 
                 foreground=COLORS.get("text_secondary", "#666666")).pack(anchor="w")
        
        ttk.Label(card, text=card_info["value"], 
                 font=FONTS["heading"]).pack(anchor="w", pady=(5, 0))
        
        ttk.Label(card, text=card_info["desc"], font=FONTS["caption"], 
                 foreground=COLORS.get("text_secondary", "#666666")).pack(anchor="w", pady=(5, 0))
    
    # Configure grid
    cards_frame.columnconfigure(0, weight=1)
    cards_frame.columnconfigure(1, weight=1)
    
    return frame

def create_placeholder_tab(parent, tab_name):
    """Create a placeholder tab for modules that aren't implemented yet"""
    frame = ttk.Frame(parent, padding=20)
    frame.pack(fill="both", expand=True)
    
    # Tab title
    title_label = ttk.Label(
        frame,
        text=f"{tab_name} Tab",
        font=FONTS["title"]
    )
    title_label.pack(pady=(0, 20))
    
    # Message
    message = ttk.Label(
        frame,
        text=(f"The {tab_name} functionality will be implemented soon.\n"),
        font=FONTS["body"],
        justify="center",
        wraplength=600
    )
    message.pack(pady=50)
    
    if has_ai_assistant:
        # Add AI assistant info with modified styling using a Button instead of Label
        ai_info_frame = ttk.Frame(frame)
        ai_info_frame.pack(pady=(0, 50))
        
        ai_info_text = ttk.Label(
            ai_info_frame,
            text=f"Need help with {tab_name.lower()}? ",
            font=FONTS["body"],
            justify="center"
        )
        ai_info_text.pack(side="left")
        
        # Create a clickable link-style button for AI assistance
        ai_link = tk.Button(
            ai_info_frame,
            text="Ask the AI Assistant",
            font=("Segoe UI", 10, "underline"),
            fg="#4a90e2",  # Blue text to match AI button
            activeforeground="#3a7bd5",  # Darker blue when clicked
            bd=0,  # No border
            relief="flat",
            highlightthickness=0,
            cursor="hand2",  # Hand cursor on hover
            bg=frame.cget("background"),  # Match parent background
            activebackground=frame.cget("background"),  # Match parent background when clicked
            command=lambda: show_ai_assistant(frame.winfo_toplevel(), None)
        )
        ai_link.pack(side="left")
    
    return frame

def center_window(window):
    """Center a window on the screen"""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def main():
    """Main application function"""
    # Initialize database and directories
    ensure_directories_exist()
    db_initialized = check_database()
    
    # Start the login process
    show_login_window()

if __name__ == "__main__":
    # First show splash screen
    show_splash_screen()
    
    # Then start your actual application
    print("Starting main application...")
    
    # Call the main function instead of creating another login window
    main()