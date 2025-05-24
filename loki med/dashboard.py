"""
Dashboard module for the Medical Assistant application.
Provides a summary view of key information for the user.
"""

import tkinter as tk
from tkinter import ttk
import sqlite3
import os
from datetime import datetime, timedelta
import calendar

from theme_styles import COLORS, FONTS, create_card, create_dashboard_card

# Database path
DB_PATH = os.path.join("database", "medical_assistant.db")

def get_greeting():
    """Return a greeting based on the time of day"""
    current_hour = datetime.now().hour
    
    if current_hour < 12:
        return "Good morning"
    elif current_hour < 18:
        return "Good afternoon"
    else:
        return "Good evening"

def get_user_info(username):
    """Get user information from the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT full_name FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return result[0]
        return username
    except:
        return username

def get_dashboard_data(username):
    """Get data for dashboard widgets"""
    data = {
        "appointments": {
            "upcoming": 0,
            "next_date": "None scheduled",
            "next_doctor": ""
        },
        "medications": {
            "total": 0,
            "due_today": 0
        },
        "health": {
            "latest_pulse": "--",
            "pulse_date": "No data"
        },
        "records": {
            "total": 0,
            "latest": "No records"
        }
    }
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return data
        
        user_id = result[0]
        
        # Upcoming appointments
        today = datetime.now().strftime("%d-%m-%Y")
        cursor.execute("""
            SELECT COUNT(*), MIN(date), doctor
            FROM appointments 
            WHERE user_id = ? AND date >= ? AND status != 'Completed' AND status != 'Cancelled'
            GROUP BY user_id
        """, (user_id, today))
        
        result = cursor.fetchone()
        if result:
            data["appointments"]["upcoming"] = result[0]
            data["appointments"]["next_date"] = result[1]
            data["appointments"]["next_doctor"] = result[2]
        
        # Medications
        cursor.execute("""
            SELECT COUNT(*) FROM reminders WHERE user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        if result:
            data["medications"]["total"] = result[0]
        
        today = datetime.now().strftime("%d-%m-%Y")
        cursor.execute("""
            SELECT COUNT(*) FROM reminders WHERE user_id = ? AND date = ?
        """, (user_id, today))
        
        result = cursor.fetchone()
        if result:
            data["medications"]["due_today"] = result[0]
        
        # Health readings
        cursor.execute("""
            SELECT value, timestamp FROM health_readings 
            WHERE user_id = ? AND reading_type = 'pulse'
            ORDER BY timestamp DESC LIMIT 1
        """, (user_id,))
        
        result = cursor.fetchone()
        if result:
            data["health"]["latest_pulse"] = result[0]
            data["health"]["pulse_date"] = result[1]
        
        # Medical records
        cursor.execute("""
            SELECT COUNT(*), MAX(upload_date) FROM medical_records WHERE user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        if result and result[0]:
            data["records"]["total"] = result[0]
            data["records"]["latest"] = result[1]
        
        conn.close()
    except Exception as e:
        print(f"Error getting dashboard data: {e}")
    
    return data

def create_calendar_widget(parent, username):
    """Create calendar widget showing appointments"""
    # Get current date information
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    
    # Create a frame to hold calendar
    cal_frame = create_card(parent, "Calendar")
    
    # Month and year header
    header_frame = ttk.Frame(cal_frame)
    header_frame.pack(fill="x", pady=(0, 10))
    
    month_year = f"{calendar.month_name[current_month]} {current_year}"
    month_label = ttk.Label(header_frame, text=month_year, font=FONTS["subtitle"])
    month_label.pack(side="left")
    
    # Navigation buttons
    nav_frame = ttk.Frame(header_frame)
    nav_frame.pack(side="right")
    
    prev_button = ttk.Button(nav_frame, text="<", width=2, style="Text.TButton")
    prev_button.pack(side="left", padx=2)
    
    next_button = ttk.Button(nav_frame, text=">", width=2, style="Text.TButton")
    next_button.pack(side="left", padx=2)
    
    # Days of week header
    days_frame = ttk.Frame(cal_frame)
    days_frame.pack(fill="x")
    
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for day in days:
        day_label = ttk.Label(days_frame, text=day, font=FONTS["caption"], anchor="center", width=4)
        day_label.pack(side="left", expand=True, fill="x")
    
    # Calendar grid
    cal_grid_frame = ttk.Frame(cal_frame)
    cal_grid_frame.pack(fill="both", expand=True)
    
    # Get calendar for current month
    cal = calendar.monthcalendar(current_year, current_month)
    
    # Get appointment dates
    appointment_dates = []
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if result:
            user_id = result[0]
            
            cursor.execute("""
                SELECT date FROM appointments 
                WHERE user_id = ? AND status != 'Cancelled'
            """, (user_id,))
            
            for row in cursor.fetchall():
                try:
                    date_str = row[0]
                    date = datetime.strptime(date_str, "%d-%m-%Y")
                    if date.month == current_month and date.year == current_year:
                        appointment_dates.append(date.day)
                except:
                    continue
        
        conn.close()
    except Exception as e:
        print(f"Error getting appointment dates: {e}")
    
    # Today's date
    today = now.day if now.month == current_month and now.year == current_year else -1
    
    # Create calendar cells
    for week in cal:
        week_frame = ttk.Frame(cal_grid_frame)
        week_frame.pack(fill="x", expand=True)
        
        for day in week:
            # Create day frame
            day_frame = ttk.Frame(week_frame, width=30, height=30)
            day_frame.pack_propagate(False)
            day_frame.pack(side="left", expand=True, fill="both", padx=1, pady=1)
            
            if day == 0:
                # Empty cell for days not in this month
                continue
            
            # Determine style based on whether it's today or has appointments
            if day == today:
                # Today's date
                bg_color = COLORS["primary"]
                fg_color = COLORS["background"]
                font_config = FONTS["body_bold"]
            elif day in appointment_dates:
                # Day with appointments
                bg_color = COLORS["primary_light"]
                fg_color = COLORS["background"]
                font_config = FONTS["body"]
            else:
                # Regular day
                bg_color = COLORS["background"]
                fg_color = COLORS["text"]
                font_config = FONTS["body"]
            
            # Create custom label since ttk.Label doesn't support background easily
            day_label = tk.Label(
                day_frame, 
                text=str(day),
                bg=bg_color,
                fg=fg_color,
                font=font_config
            )
            day_label.pack(fill="both", expand=True)
    
    return cal_frame

def create_dashboard_tab(parent, username):
    """Create the dashboard tab"""
    # Main frame
    dash_frame = ttk.Frame(parent)
    dash_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Get user's full name
    user_fullname = get_user_info(username) or username
    
    # Get dashboard data
    data = get_dashboard_data(username)
    
    # Welcome header
    greeting = get_greeting()
    header_label = ttk.Label(
        dash_frame, 
        text=f"{greeting}, {user_fullname}",
        style="Title.TLabel"
    )
    header_label.pack(anchor="w", pady=(0, 20))
    
    date_label = ttk.Label(
        dash_frame,
        text=datetime.now().strftime("%A, %d %B %Y"),
        font=FONTS["body"],
        foreground=COLORS["text_secondary"]
    )
    date_label.pack(anchor="w", pady=(0, 30))
    
    # Dashboard content in 2 columns
    content_frame = ttk.Frame(dash_frame)
    content_frame.pack(fill="both", expand=True)
    
    # Left column - Stats cards
    left_frame = ttk.Frame(content_frame)
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=(0, 15))
    
    # Top row of cards
    top_row = ttk.Frame(left_frame)
    top_row.pack(fill="x", pady=(0, 20))
    
    # Appointments card
    appointments_card = create_dashboard_card(
        top_row,
        "UPCOMING APPOINTMENTS",
        str(data["appointments"]["upcoming"]),
        f"Next: {data['appointments']['next_date']}",
        "📅",
        COLORS["primary"]
    )
    appointments_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
    
    # Medications card
    medications_card = create_dashboard_card(
        top_row,
        "MEDICATION REMINDERS",
        str(data["medications"]["due_today"]),
        f"Due today out of {data['medications']['total']} total",
        "💊",
        COLORS["secondary"]
    )
    medications_card.pack(side="left", fill="both", expand=True)
    
    # Bottom row of cards
    bottom_row = ttk.Frame(left_frame)
    bottom_row.pack(fill="x")
    
    # Health card
    health_card = create_dashboard_card(
        bottom_row,
        "LATEST PULSE READING",
        f"{data['health']['latest_pulse']} BPM",
        f"Recorded: {data['health']['pulse_date']}",
        "❤️",
        COLORS["accent"]
    )
    health_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
    
    # Medical records card
    records_card = create_dashboard_card(
        bottom_row,
        "MEDICAL RECORDS",
        str(data["records"]["total"]),
        f"Latest update: {data['records']['latest']}",
        "📋",
        COLORS["info"]
    )
    records_card.pack(side="left", fill="both", expand=True)
    
    # Right column with calendar and recent activity
    right_frame = ttk.Frame(content_frame)
    right_frame.pack(side="right", fill="both", expand=True)
    
    # Calendar widget showing appointments
    calendar_widget = create_calendar_widget(right_frame, username)
    calendar_widget.pack(fill="both", expand=True, pady=(0, 15))
    
    # Recent activity card
    activity_card = create_card(right_frame, "Recent Activity")
    activity_card.pack(fill="both", expand=True)
    
    # Create a listbox for activity items
    activity_list = tk.Listbox(
        activity_card,
        height=8,
        background=COLORS["background"],
        foreground=COLORS["text"],
        font=FONTS["body"],
        borderwidth=0,
        highlightthickness=0
    )
    activity_list.pack(fill="both", expand=True)
    
    # Add some sample activity items
    activity_items = [
        "Appointment with Dr. Smith confirmed (10 minutes ago)",
        "New medical record uploaded (2 hours ago)",
        "Medication reminder: Paracetamol 500mg (3 hours ago)",
        "Your prescription has been renewed (Yesterday)",
        "Health reading recorded: Pulse rate 72 BPM (Yesterday)",
        "Payment processed for medicine purchase (2 days ago)"
    ]
    
    for item in activity_items:
        activity_list.insert(tk.END, item)
        
    # Add a "View All" link at the bottom
    view_all_frame = ttk.Frame(activity_card)
    view_all_frame.pack(fill="x", pady=(10, 0))
    
    view_all_button = ttk.Button(
        view_all_frame,
        text="View All Activity",
        style="Text.TButton"
    )
    view_all_button.pack(side="right")
    
    # Quick access section at the bottom
    quick_access_frame = ttk.Frame(dash_frame)
    quick_access_frame.pack(fill="x", pady=(20, 0))
    
    quick_access_label = ttk.Label(
        quick_access_frame,
        text="Quick Access",
        style="Heading.TLabel"
    )
    quick_access_label.pack(anchor="w", pady=(0, 10))
    
    # Quick access buttons
    buttons_frame = ttk.Frame(quick_access_frame)
    buttons_frame.pack(fill="x")
    
    # Create quick access buttons with icons
    quick_buttons = [
        {"text": "Add Appointment", "icon": "📅", "color": COLORS["primary"]},
        {"text": "New Medication", "icon": "💊", "color": COLORS["secondary"]},
        {"text": "Health Check", "icon": "❤️", "color": COLORS["accent"]},
        {"text": "Upload Record", "icon": "📋", "color": COLORS["info"]}
    ]
    
    for btn in quick_buttons:
        # Create frame for button to enable custom styling
        btn_frame = ttk.Frame(buttons_frame)
        btn_frame.pack(side="left", fill="x", expand=True, padx=5)
        
        # Create custom button with icon
        quick_btn = tk.Button(
            btn_frame,
            text=f"{btn['icon']} {btn['text']}",
            background=btn['color'],
            foreground=COLORS["background"],
            font=FONTS["body_bold"],
            borderwidth=0,
            padx=10,
            pady=10,
            cursor="hand2"
        )
        quick_btn.pack(fill="x")
    
    return dash_frame