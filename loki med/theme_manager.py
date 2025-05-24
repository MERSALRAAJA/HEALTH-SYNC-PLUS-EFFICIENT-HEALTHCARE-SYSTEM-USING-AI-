"""
Theme manager for the Medical Assistant application.
This module provides centralized theme and style application using the theme_styles.py configuration.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add parent directory to import path if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import theme styles
from theme_styles import COLORS, FONTS, SPACING, setup_styles, apply_theme, create_shadow_frame, create_card, create_dashboard_card

class ThemeManager:
    """Manages application-wide theme and styling"""
    
    def __init__(self, root):
        """Initialize theme manager with root window"""
        self.root = root
        self.current_theme = "light"  # Default theme
        
        # Initialize styles
        self.style = setup_styles()
    
    def apply_theme(self, theme="light"):
        """Apply theme to all widgets"""
        self.current_theme = theme
        apply_theme(self.root)
    
    def create_card(self, parent, title=None, padding=SPACING["m"]):
        """Create a styled card widget"""
        return create_card(parent, title, padding)
    
    def create_dashboard_card(self, parent, title, value, description=None, icon=None, color=None):
        """Create a dashboard info card"""
        return create_dashboard_card(parent, title, value, description, icon, color)
    
    def create_shadow_frame(self, parent, **kwargs):
        """Create a frame with shadow effect"""
        return create_shadow_frame(parent, **kwargs)
    
    def get_color(self, color_name):
        """Get a color by name from the color palette"""
        return COLORS.get(color_name, COLORS["text"])
    
    def get_font(self, font_name):
        """Get a font by name from the font definitions"""
        return FONTS.get(font_name, FONTS["body"])

def get_theme_manager(root):
    """Get or create a theme manager instance for the given root"""
    if not hasattr(root, "_theme_manager"):
        root._theme_manager = ThemeManager(root)
    return root._theme_manager