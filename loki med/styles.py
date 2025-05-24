"""
UI styles and theme definitions for the Medical Assistant application.
"""

import tkinter as tk
from tkinter import ttk

# Color schemes
COLORS = {
    "primary": "#4a6fa5",
    "secondary": "#6c757d",
    "success": "#28a745",
    "danger": "#dc3545",
    "warning": "#ffc107",
    "info": "#17a2b8",
    "light": "#f8f9fa",
    "dark": "#343a40",
    "light_bg": "#f8f9fa",
    "dark_bg": "#212529",
    "card_bg": "#ffffff",
    "card_border": "#e6e6e6"
}

# Dark mode colors
DARK_COLORS = {
    "primary": "#5c88c5",
    "secondary": "#8c959d",
    "success": "#48c764",
    "danger": "#e05c70",
    "warning": "#ffce3a",
    "info": "#3fc8da",
    "light": "#f8f9fa",
    "dark": "#343a40",
    "light_bg": "#2e3338",
    "dark_bg": "#212529",
    "card_bg": "#343a40",
    "card_border": "#495057"
}

def setup_styles():
    """Set up ttk styles for the application"""
    # Create style object
    style = ttk.Style()
    
    # Configure the theme
    try:
        # Try to use a more modern theme if available
        style.theme_use("clam")  # Alternative: "vista" on Windows or "alt" on Linux
    except tk.TclError:
        # Fallback to default theme
        pass
    
    # Configure the basic styles
    style.configure("TFrame", background=COLORS["light_bg"])
    style.configure("TLabel", background=COLORS["light_bg"], foreground=COLORS["dark"])
    style.configure("TButton", background=COLORS["primary"], foreground=COLORS["light"])
    style.configure("TEntry", background=COLORS["light"], foreground=COLORS["dark"])
    
    # Card style
    style.configure("Card.TFrame", background=COLORS["card_bg"], relief="solid", borderwidth=1)
    
    # Text styles
    style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), background=COLORS["light_bg"], foreground=COLORS["primary"])
    style.configure("Subtitle.TLabel", font=("Segoe UI", 14, "bold"), background=COLORS["light_bg"], foreground=COLORS["secondary"])
    style.configure("Text.TLabel", font=("Segoe UI", 10), background=COLORS["light_bg"], foreground=COLORS["dark"])
    
    # Button styles
    style.configure("Primary.TButton", background=COLORS["primary"], foreground=COLORS["light"])
    style.configure("Success.TButton", background=COLORS["success"], foreground=COLORS["light"])
    style.configure("Danger.TButton", background=COLORS["danger"], foreground=COLORS["light"])
    style.configure("Warning.TButton", background=COLORS["warning"], foreground=COLORS["dark"])
    style.configure("Info.TButton", background=COLORS["info"], foreground=COLORS["light"])
    
    return style

def apply_theme(root, theme="light"):
    """Apply a theme to the application"""
    style = ttk.Style()
    
    # Configure colors based on theme
    if theme == "dark":
        colors = DARK_COLORS
        root.configure(bg=DARK_COLORS["dark_bg"])
    else:
        colors = COLORS
        root.configure(bg=COLORS["light_bg"])
    
    # Update styles with the theme colors
    style.configure("TFrame", background=colors["light_bg"])
    style.configure("TLabel", background=colors["light_bg"], foreground=colors["dark"])
    style.configure("TButton", background=colors["primary"], foreground=colors["light"])
    
    # Update card style
    style.configure("Card.TFrame", background=colors["card_bg"], relief="solid", borderwidth=1)
    
    # Update text styles
    style.configure("Title.TLabel", background=colors["light_bg"], foreground=colors["primary"])
    style.configure("Subtitle.TLabel", background=colors["light_bg"], foreground=colors["secondary"])
    style.configure("Text.TLabel", background=colors["light_bg"], foreground=colors["dark"])
    
    # Update button styles
    style.configure("Primary.TButton", background=colors["primary"], foreground=colors["light"])
    style.configure("Success.TButton", background=colors["success"], foreground=colors["light"])
    style.configure("Danger.TButton", background=colors["danger"], foreground=colors["light"])
    style.configure("Warning.TButton", background=colors["warning"], foreground=colors["dark"])
    style.configure("Info.TButton", background=colors["info"], foreground=colors["light"])
    
    # Update all children widgets to reflect the new theme
    update_widget_colors(root, colors)

def update_widget_colors(parent, colors):
    """Recursively update widget colors for theme change"""
    for widget in parent.winfo_children():
        try:
            # Update widget background if it has a background property
            if isinstance(widget, (ttk.Frame, ttk.Label, ttk.Button)):
                widget.configure(style=widget["style"])
            elif isinstance(widget, (tk.Frame, tk.Label, tk.Text, tk.Entry)):
                widget.configure(background=colors["light_bg"])
                if hasattr(widget, "foreground"):
                    widget.configure(foreground=colors["dark"])
        except (tk.TclError, TypeError, KeyError):
            # Ignore errors for widgets that don't have these properties
            pass
        
        # Recursively update children widgets
        if widget.winfo_children():
            update_widget_colors(widget, colors)