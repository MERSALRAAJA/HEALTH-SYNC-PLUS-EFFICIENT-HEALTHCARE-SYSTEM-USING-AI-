"""
Custom widgets and UI components for the Medical Assistant application.
"""

import tkinter as tk
from tkinter import ttk

def center_window(window):
    """Center a window on the screen"""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def create_custom_card(parent, title=None, padding=10):
    """Create a custom card widget with a title"""
    # Main card frame
    card = ttk.Frame(parent, style="Card.TFrame", padding=padding)
    card.pack(fill="both", expand=True, pady=10)
    
    # Add title if provided
    if title:
        title_frame = ttk.Frame(card, style="Card.TFrame")
        title_frame.pack(fill="x", pady=(0, 10))
        
        title_label = ttk.Label(
            title_frame, 
            text=title, 
            font=("Segoe UI", 12, "bold"),
            style="Subtitle.TLabel"
        )
        title_label.pack(anchor="w")
        
        # Add separator
        separator = ttk.Separator(card, orient="horizontal")
        separator.pack(fill="x", pady=(0, 10))
    
    return card

def create_scrollable_frame(parent):
    """Create a scrollable frame"""
    # Create a canvas with scrollbar
    canvas = tk.Canvas(parent)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    
    # Configure the canvas scrolling
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Place canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Create a frame inside the canvas
    frame = ttk.Frame(canvas)
    
    # Create window inside the canvas with the frame
    canvas_window = canvas.create_window((0, 0), window=frame, anchor="nw")
    
    # Function to handle canvas resize
    def configure_frame(event):
        # Update the width of the frame to fill the canvas
        canvas.itemconfig(canvas_window, width=event.width)
    
    # Function to handle frame resize
    def configure_canvas(event):
        # Update the scrollregion to include the entire frame
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    # Bind events
    canvas.bind("<Configure>", configure_frame)
    frame.bind("<Configure>", configure_canvas)
    
    # Enable mouse wheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    # Return the frame
    return frame, canvas

def create_tooltip(widget, text):
    """Create a tooltip for a widget"""
    
    def show_tooltip(event):
        # Get the widget position
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 25
        
        # Create a toplevel window
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{x}+{y}")
        
        # Create a label with the tooltip text
        label = ttk.Label(
            tooltip, 
            text=text, 
            justify="left",
            background="#ffffe0", 
            relief="solid", 
            borderwidth=1,
            padding=5
        )
        label.pack(ipadx=5, ipady=5)
        
        # Function to hide tooltip
        def hide_tooltip(event):
            tooltip.destroy()
        
        # Bind events
        label.bind("<Leave>", hide_tooltip)
        widget.bind("<Leave>", hide_tooltip)
        
        # Store reference to prevent garbage collection
        widget._tooltip = tooltip
    
    # Bind event to show tooltip
    widget.bind("<Enter>", show_tooltip)

def create_rounded_button(parent, text, command=None, **kwargs):
    """Create a button with rounded corners (simulation with regular ttk button)"""
    button_style = kwargs.pop("style", "TButton")
    
    button = ttk.Button(
        parent,
        text=text,
        command=command,
        style=button_style,
        **kwargs
    )
    
    return button

def create_notification_badge(parent, text="0", **kwargs):
    """Create a notification badge (small circle with a number)"""
    # Default settings
    background = kwargs.pop("background", "#ffffff")
    foreground = kwargs.pop("foreground", "#ffffff")
    font = kwargs.pop("font", ("Segoe UI", 8))
    
    # Create a label with circular appearance
    badge = tk.Label(
        parent,
        text=text,
        background=background,
        foreground=foreground,
        font=font,
        borderwidth=0,
        highlightthickness=0,
        padx=4,
        pady=0,
        **kwargs
    )
    
    # Make the badge circular by setting height and width
    badge.update_idletasks()
    width = badge.winfo_reqwidth()
    height = badge.winfo_reqheight()
    size = max(width, height)
    badge.configure(width=size // 10, height=size // 20)
    
    return badge

def create_status_indicator(parent, status="online", **kwargs):
    """Create a small colored circle indicating status"""
    # Status colors
    status_colors = {
        "online": "#28a745",  # Green
        "offline": "#dc3545",  # Red
        "away": "#ffc107",    # Yellow
        "busy": "#fd7e14"     # Orange
    }
    
    # Default size
    size = kwargs.pop("size", 10)
    
    # Get color based on status
    color = status_colors.get(status.lower(), "#6c757d")  # Default to gray
    
    # Create a canvas for drawing the circle
    canvas = tk.Canvas(
        parent,
        width=size,
        height=size,
        highlightthickness=0,
        **kwargs
    )
    
    # Draw the circle
    canvas.create_oval(0, 0, size, size, fill=color, outline="")
    
    return canvas

def create_search_entry(parent, placeholder="Search...", command=None, **kwargs):
    """Create a search entry with placeholder text"""
    frame = ttk.Frame(parent)
    
    # Create entry widget
    entry_var = tk.StringVar()
    entry = ttk.Entry(frame, textvariable=entry_var, **kwargs)
    entry.pack(side="left", fill="x", expand=True)
    
    # Set placeholder text
    if not entry_var.get():
        entry.insert(0, placeholder)
        entry.config(foreground="#6c757d")
    
    # Functions to handle placeholder behavior
    def on_focus_in(event):
        if entry_var.get() == placeholder:
            entry.delete(0, "end")
            entry.config(foreground="#000000")
    
    def on_focus_out(event):
        if not entry_var.get():
            entry.insert(0, placeholder)
            entry.config(foreground="#6c757d")
    
    # Bind events
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    
    # Add search button if command is provided
    if command:
        search_button = ttk.Button(
            frame,
            text="Search",
            command=lambda: command(entry_var.get())
        )
        search_button.pack(side="right", padx=(5, 0))
    
    return frame, entry_var