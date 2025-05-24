"""
Theme and styles configuration for the Medical Assistant application.
This module centralizes styling to ensure a consistent look across the application.
"""

import tkinter as tk
from tkinter import ttk, font

# Color palette
COLORS = {
    # Primary colors
    "primary": "#3f51b5",  # Indigo
    "primary_light": "#757de8",
    "primary_dark": "#002984",
    
    # Secondary colors
    "secondary": "#00bcd4",  # Cyan
    "secondary_light": "#62efff",
    "secondary_dark": "#008ba3",
    
    # Accent colors
    "accent": "#ff4081",  # Pink
    "accent_light": "#ff79b0",
    "accent_dark": "#c60055",
    
    # Status colors
    "success": "#4caf50",  # Green
    "warning": "#ff9800",  # Orange
    "error": "#f44336",    # Red
    "info": "#2196f3",     # Blue
    
    # Neutral colors
    "text": "#212121",     # Very dark gray
    "text_secondary": "#757575",  # Medium gray
    "text_disabled": "#9e9e9e",   # Light gray
    "divider": "#e0e0e0",  # Very light gray
    
    # Background colors
    "background": "#ffffff",  # White
    "background_light": "#f5f5f5",  # Off-white
    "background_dark": "#e0e0e0",   # Light gray
    
    # Card colors
    "card": "#ffffff",  # White
    "card_hover": "#f9f9f9",  # Slightly off-white
    "card_border": "#e0e0e0",  # Light gray
}

# Font configurations
FONTS = {
    "display_large": ("Segoe UI", 32, "bold"),
    "display": ("Segoe UI", 24, "bold"),
    "title": ("Segoe UI", 18, "bold"),
    "subtitle": ("Segoe UI", 16, "bold"),
    "heading": ("Segoe UI", 14, "bold"),
    "subheading": ("Segoe UI", 12, "bold"),
    "body": ("Segoe UI", 10),
    "body_bold": ("Segoe UI", 10, "bold"),
    "caption": ("Segoe UI", 9),
    "small": ("Segoe UI", 8),
}

# Spacing values (in pixels)
SPACING = {
    "xs": 2,
    "s": 5,
    "m": 10,
    "l": 15,
    "xl": 20,
    "xxl": 30,
}

# Border radius values (in pixels)
BORDER_RADIUS = {
    "small": 2,
    "medium": 4,
    "large": 8,
    "circle": 50,  # Large enough to make a square into a circle
}

# Shadow configurations
SHADOWS = {
    "none": "none",
    "small": "0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)",
    "medium": "0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23)",
    "large": "0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23)",
    "extra": "0 14px 28px rgba(0,0,0,0.25), 0 10px 10px rgba(0,0,0,0.22)",
}

def setup_styles():
    """Set up and configure all styles for the application"""
    style = ttk.Style()
    
    # Try to use a more modern theme
    try:
        # Attempt to use the 'clam' theme which is the most customizable cross-platform
        style.theme_use("clam")
    except tk.TclError:
        # If 'clam' is not available, fall back to default
        pass
    
    # ===== FRAMES =====
    # Default frame
    style.configure("TFrame", background=COLORS["background"])
    
    # Card frame with borders
    style.configure("Card.TFrame", 
                   background=COLORS["card"],
                   relief="solid",
                   borderwidth=1,
                   bordercolor=COLORS["card_border"])
    
    # Elevated card with shadow effect (must be used with a canvas in actual code)
    style.configure("Elevated.TFrame",
                   background=COLORS["card"])
    
    # Primary color frame
    style.configure("Primary.TFrame",
                   background=COLORS["primary"])
    
    # Secondary frame
    style.configure("Secondary.TFrame",
                   background=COLORS["secondary"])
    
    # ===== LABELS =====
    # Default label
    style.configure("TLabel", 
                   background=COLORS["background"],
                   foreground=COLORS["text"],
                   font=FONTS["body"])
    
    # Title label
    style.configure("Title.TLabel",
                   background=COLORS["background"],
                   foreground=COLORS["primary"],
                   font=FONTS["title"])
    
    # Subtitle label
    style.configure("Subtitle.TLabel",
                   background=COLORS["background"],
                   foreground=COLORS["text"],
                   font=FONTS["subtitle"])
    
    # Heading label
    style.configure("Heading.TLabel",
                   background=COLORS["background"],
                   foreground=COLORS["text"],
                   font=FONTS["heading"])
    
    # Caption label (smaller text)
    style.configure("Caption.TLabel",
                   background=COLORS["background"],
                   foreground=COLORS["text_secondary"],
                   font=FONTS["caption"])
    
    # Error label
    style.configure("Error.TLabel",
                   background=COLORS["background"],
                   foreground=COLORS["error"],
                   font=FONTS["body"])
    
    # ===== BUTTONS =====
    # Default button
    style.configure("TButton", 
                   background=COLORS["background_dark"],
                   foreground=COLORS["text"],
                   borderwidth=1,
                   focusthickness=3,
                   focuscolor=COLORS["primary_light"],
                   font=FONTS["body_bold"])
    
    style.map("TButton",
             background=[("active", COLORS["background_dark"]), 
                         ("pressed", COLORS["background_dark"])],
             relief=[("pressed", "sunken")])
    
    # Primary button
    style.configure("Primary.TButton", 
                   background=COLORS["primary"],
                   foreground=COLORS["background"],
                   borderwidth=0,
                   font=FONTS["body_bold"])
    
    style.map("Primary.TButton",
             background=[("active", COLORS["primary_light"]), 
                         ("pressed", COLORS["primary_dark"])],
             foreground=[("pressed", COLORS["background"])])
    
    # Secondary button
    style.configure("Secondary.TButton", 
                   background=COLORS["secondary"],
                   foreground=COLORS["background"],
                   borderwidth=0,
                   font=FONTS["body_bold"])
    
    style.map("Secondary.TButton",
             background=[("active", COLORS["secondary_light"]), 
                         ("pressed", COLORS["secondary_dark"])],
             foreground=[("pressed", COLORS["background"])])
    
    # Outline button
    style.configure("Outline.TButton", 
                   background=COLORS["background"],
                   foreground=COLORS["primary"],
                   borderwidth=1,
                   bordercolor=COLORS["primary"],
                   font=FONTS["body_bold"])
    
    style.map("Outline.TButton",
             background=[("active", COLORS["primary_light"]), 
                         ("pressed", COLORS["primary"])],
             foreground=[("active", COLORS["background"]),
                         ("pressed", COLORS["background"])])
    
    # Text button (looks like a hyperlink)
    style.configure("Text.TButton", 
                   background=COLORS["background"],
                   foreground=COLORS["primary"],
                   borderwidth=0,
                   font=FONTS["body_bold"])
    
    style.map("Text.TButton",
             foreground=[("active", COLORS["primary_light"]), 
                        ("pressed", COLORS["primary_dark"])])
    
    # ===== ENTRIES =====
    # Default entry
    style.configure("TEntry", 
                   foreground=COLORS["text"],
                   fieldbackground=COLORS["background"],
                   bordercolor=COLORS["divider"],
                   lightcolor=COLORS["background"],
                   darkcolor=COLORS["background"],
                   borderwidth=1,
                   font=FONTS["body"])
    
    style.map("TEntry",
             fieldbackground=[("focus", COLORS["background"])],
             bordercolor=[("focus", COLORS["primary"])])
    
    # ===== COMBOBOX =====
    # Default combobox
    style.configure("TCombobox",
                   foreground=COLORS["text"],
                   fieldbackground=COLORS["background"],
                   background=COLORS["background"],
                   arrowcolor=COLORS["primary"],
                   bordercolor=COLORS["divider"],
                   lightcolor=COLORS["background"],
                   darkcolor=COLORS["background"],
                   borderwidth=1,
                   font=FONTS["body"])
    
    style.map("TCombobox",
             fieldbackground=[("focus", COLORS["background"])],
             bordercolor=[("focus", COLORS["primary"])])
    
    # ===== CHECKBUTTON =====
    # Default checkbutton
    style.configure("TCheckbutton", 
                   background=COLORS["background"],
                   foreground=COLORS["text"],
                   font=FONTS["body"])
    
    style.map("TCheckbutton",
             background=[("active", COLORS["background"])],
             foreground=[("disabled", COLORS["text_disabled"])])
    
    # ===== RADIOBUTTON =====
    # Default radiobutton
    style.configure("TRadiobutton", 
                   background=COLORS["background"],
                   foreground=COLORS["text"],
                   font=FONTS["body"])
    
    style.map("TRadiobutton",
             background=[("active", COLORS["background"])],
             foreground=[("disabled", COLORS["text_disabled"])])
    
    # ===== NOTEBOOK (TABS) =====
    # Default notebook
    style.configure("TNotebook", 
                   background=COLORS["background"],
                   borderwidth=0)
    
    style.configure("TNotebook.Tab", 
                   background=COLORS["background"],
                   foreground=COLORS["text_secondary"],
                   borderwidth=0,
                   font=FONTS["body_bold"],
                   padding=[10, 5])
    
    style.map("TNotebook.Tab",
             background=[("selected", COLORS["background"]), 
                         ("active", COLORS["background_light"])],
             foreground=[("selected", COLORS["primary"]), 
                         ("active", COLORS["primary_light"])],
             expand=[("selected", [0, 0, 0, 2])])
    
    # ===== TREEVIEW (TABLE/LIST) =====
    # Default treeview
    style.configure("Treeview", 
                   background=COLORS["background"],
                   foreground=COLORS["text"],
                   rowheight=25,
                   borderwidth=0,
                   font=FONTS["body"])
    
    # Treeview headings
    style.configure("Treeview.Heading", 
                   background=COLORS["background_light"],
                   foreground=COLORS["text"],
                   borderwidth=1,
                   font=FONTS["body_bold"],
                   relief="flat")
    
    style.map("Treeview.Heading",
             background=[("active", COLORS["background_dark"])])
    
    style.map("Treeview",
             background=[("selected", COLORS["primary_light"])],
             foreground=[("selected", COLORS["background"])])
    
    # ===== PROGRESSBAR =====
    # Default progressbar
    style.configure("TProgressbar", 
                   background=COLORS["primary"],
                   troughcolor=COLORS["background_light"],
                   borderwidth=0,
                   thickness=10)
    
    # ===== SCROLLBAR =====
    # Default scrollbar
    style.configure("TScrollbar", 
                   background=COLORS["background_light"],
                   troughcolor=COLORS["background"],
                   borderwidth=0,
                   arrowcolor=COLORS["text_secondary"])
    
    style.map("TScrollbar",
             background=[("active", COLORS["background_dark"]),
                         ("disabled", COLORS["background_light"])])
    
    # ===== SCALE (SLIDER) =====
    # Default scale
    style.configure("TScale", 
                   background=COLORS["background"],
                   troughcolor=COLORS["background_light"],
                   borderwidth=0)
    
    # ===== SEPARATOR =====
    # Default separator
    style.configure("TSeparator", 
                   background=COLORS["divider"])
    
    # ===== SIZEGRIP =====
    # Default sizegrip
    style.configure("TSizegrip", 
                   background=COLORS["background"])
    
    return style

def create_shadow_frame(parent, **kwargs):
    """Create a frame with shadow effect using a canvas"""
    # Canvas for shadow effect
    canvas = tk.Canvas(parent, 
                      background=COLORS["background"],
                      highlightthickness=0,
                      **kwargs)
    canvas.pack(fill="both", expand=True)
    
    # Create the shadow rectangle
    shadow_color = "#dddddd"  # Light gray shadow
    canvas.create_rectangle(3, 3, kwargs.get("width", 200) - 3, kwargs.get("height", 200) - 3,
                           fill=shadow_color, outline="", tags="shadow")
    
    # Create the main frame on top
    frame = ttk.Frame(canvas, style="Elevated.TFrame")
    canvas.create_window(0, 0, anchor="nw", window=frame, tags="frame",
                        width=kwargs.get("width", 200) - 6, 
                        height=kwargs.get("height", 200) - 6)
    
    return frame

def apply_theme(window):
    """Apply the theme to a window and its children recursively"""
    # Setup styles if not already done
    setup_styles()
    
    # Configure the window background
    window.configure(background=COLORS["background"])
    
    # Apply styles to all children widgets
    for widget in window.winfo_children():
        # Configure based on widget type
        if isinstance(widget, ttk.Frame):
            # Skip frames with custom styles
            pass
        elif isinstance(widget, ttk.Label):
            # Skip labels with custom styles
            pass
        elif isinstance(widget, ttk.Button):
            # Skip buttons with custom styles
            pass
        elif isinstance(widget, ttk.Entry):
            # Apply the default style to all entries
            widget.configure(style="TEntry")
        elif isinstance(widget, ttk.Combobox):
            # Apply the default style to all comboboxes
            widget.configure(style="TCombobox")
        elif isinstance(widget, ttk.Checkbutton):
            # Apply the default style to all checkbuttons
            widget.configure(style="TCheckbutton")
        elif isinstance(widget, ttk.Radiobutton):
            # Apply the default style to all radiobuttons
            widget.configure(style="TRadiobutton")
        elif isinstance(widget, ttk.Notebook):
            # Apply the default style to all notebooks
            widget.configure(style="TNotebook")
        elif isinstance(widget, ttk.Treeview):
            # Apply the default style to all treeviews
            widget.configure(style="Treeview")
        elif isinstance(widget, ttk.Progressbar):
            # Apply the default style to all progressbars
            widget.configure(style="TProgressbar")
        elif isinstance(widget, ttk.Scrollbar):
            # Apply the default style to all scrollbars
            widget.configure(style="TScrollbar")
        elif isinstance(widget, ttk.Scale):
            # Apply the default style to all scales
            widget.configure(style="TScale")
        elif isinstance(widget, ttk.Separator):
            # Apply the default style to all separators
            widget.configure(style="TSeparator")
        elif isinstance(widget, ttk.Sizegrip):
            # Apply the default style to all sizegrips
            widget.configure(style="TSizegrip")
        
        # Recursively apply theme to children
        if widget.winfo_children():
            for child in widget.winfo_children():
                apply_theme(child)

def create_card(parent, title=None, padding=10):
    """Create a card widget with an optional title"""
    # Main card frame
    card = ttk.Frame(parent, style="Card.TFrame", padding=padding)
    
    # Add title if provided
    if title:
        # Title label
        title_label = ttk.Label(card, text=title, style="Subtitle.TLabel")
        title_label.pack(anchor="w", pady=(0, 10))
        
        # Separator
        separator = ttk.Separator(card, orient="horizontal")
        separator.pack(fill="x", pady=(0, 10))
    
    return card

def create_dashboard_card(parent, title, value, description=None, icon=None, color=None):
    """Create a dashboard info card with a title, value and optional description"""
    # Main card frame
    card = ttk.Frame(parent, style="Card.TFrame", padding=10)
    
    # Card header with title
    header_frame = ttk.Frame(card)
    header_frame.pack(fill="x", pady=(0, 5))
    
    # Icon (placeholder)
    if icon:
        icon_label = ttk.Label(header_frame, text=icon, foreground=color or COLORS["primary"])
        icon_label.pack(side="left", padx=(0, 5))
    
    # Title
    title_label = ttk.Label(header_frame, text=title, foreground=COLORS["text_secondary"], font=FONTS["caption"])
    title_label.pack(side="left")
    
    # Value
    value_label = ttk.Label(card, text=value, font=FONTS["heading"], foreground=color or COLORS["text"])
    value_label.pack(anchor="w", pady=(5, 0))
    
    # Description
    if description:
        desc_label = ttk.Label(card, text=description, foreground=COLORS["text_secondary"], font=FONTS["caption"])
        desc_label.pack(anchor="w", pady=(5, 0))
    
    return card