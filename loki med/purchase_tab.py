"""
Medicine purchase tab UI
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import json
from datetime import datetime

# Import UI components
from widgets import create_custom_card, center_window

# Database path
DB_PATH = os.path.join("database", "medical_assistant.db")

def load_medicines():
    """Load medicines from the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, price, description, quantity FROM medications ORDER BY name")
    medicines = cursor.fetchall()
    
    conn.close()
    
    return medicines

def update_cart_display(cart_tree, total_label, username):
    """Update the cart display with items from the database"""
    # Clear existing items
    for item in cart_tree.get_children():
        cart_tree.delete(item)
    
    # Get cart items from database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get user ID
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return
    
    user_id = result[0]
    
    # Get cart items with medicine names
    cursor.execute("""
        SELECT c.id, m.name, c.quantity, m.price, (c.quantity * m.price) as subtotal
        FROM cart_items c
        JOIN medications m ON c.medicine_id = m.id
        WHERE c.user_id = ?
    """, (user_id,))
    
    cart_items = cursor.fetchall()
    conn.close()
    
    # Add items to treeview
    total_amount = 0
    for item in cart_items:
        cart_id, name, quantity, price, subtotal = item
        cart_tree.insert("", "end", iid=cart_id, values=(
            name,
            quantity,
            f"₹{price:.2f}",
            f"₹{subtotal:.2f}"
        ))
        total_amount += subtotal
    
    # Update total label
    total_label.config(text=f"Total: ₹{total_amount:.2f}")

def remove_from_cart(cart_tree, total_label, username):
    """Remove a selected item from the cart"""
    selected_item = cart_tree.selection()
    if not selected_item:
        messagebox.showinfo("Info", "Please select an item to remove")
        return
    
    # Get the cart item ID
    cart_item_id = selected_item[0]
    
    # Remove from database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM cart_items WHERE id = ?", (cart_item_id,))
    conn.commit()
    conn.close()
    
    # Update display
    update_cart_display(cart_tree, total_label, username)
    
    messagebox.showinfo("Success", "Item removed from cart")

def clear_cart(cart_tree, total_label, username):
    """Clear all items from the cart"""
    # Confirm with user
    if not messagebox.askyesno("Confirm", "Are you sure you want to clear your cart?"):
        return
    
    # Clear from database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get user ID
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return
    
    user_id = result[0]
    
    cursor.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    # Update display
    update_cart_display(cart_tree, total_label, username)
    
    messagebox.showinfo("Success", "Cart cleared")

def checkout(cart_tree, total_label, parent, username):
    """Process payment for items in cart"""
    # Check if cart is empty
    if not cart_tree.get_children():
        messagebox.showinfo("Info", "Your cart is empty")
        return
    
    # Get total amount
    total_text = total_label.cget("text")
    total_amount = float(total_text.replace("Total: ₹", ""))
    
    # Show payment screen
    show_payment_screen(total_amount, parent, cart_tree, total_label, username)

def show_payment_screen(amount, parent, cart_tree, total_label, username):
    """Show payment screen with QR code"""
    payment_window = ttk.Toplevel(parent)
    payment_window.title("Complete Payment")
    payment_window.geometry("400x450")
    
    # Create main frame
    main_frame = ttk.Frame(payment_window, padding=20)
    main_frame.pack(expand=True, fill="both", padx=20, pady=20)
    
    # Title
    title_label = ttk.Label(main_frame, text="Complete Your Payment", font=("Segoe UI", 16, "bold"))
    title_label.pack(pady=(0, 20))
    
    # Amount
    amount_label = ttk.Label(
        main_frame, 
        text=f"Amount to Pay: ₹{amount:.2f}",
        font=("Segoe UI", 14, "bold")
    )
    amount_label.pack(pady=(0, 20))
    
    # Payment method selection
    method_frame = ttk.Frame(main_frame)
    method_frame.pack(fill="x", pady=(0, 20))
    
    method_label = ttk.Label(method_frame, text="Select Payment Method:")
    method_label.pack(anchor="w", pady=(0, 5))
    
    method_var = tk.StringVar(value="UPI Payment")
    methods = ["UPI Payment", "Credit/Debit Card", "Net Banking", "Cash on Delivery"]
    method_combo = ttk.Combobox(method_frame, textvariable=method_var, values=methods, state="readonly")
    method_combo.pack(fill="x")
    
    # QR code frame
    qr_frame = ttk.Frame(main_frame)
    qr_frame.pack(fill="both", expand=True, pady=10)
    
    # QR code (simulated with text)
    qr_label = ttk.Label(
        qr_frame,
        text="[UPI QR Code]\nScan to Pay",
        font=("Segoe UI", 14),
        background="#ff0000",
        border=1,
        relief="solid",
        padding=40,
        justify="center"
    )
    qr_label.pack(fill="both", expand=True)
    
    # Function to handle payment completion
    def complete_payment():
        # Process the order
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if result:
            user_id = result[0]
            
            # Get ordered items to update inventory
            cursor.execute("""
                SELECT medicine_id, quantity
                FROM cart_items
                WHERE user_id = ?
            """, (user_id,))
            
            ordered_items = cursor.fetchall()
            
            # Update inventory quantities
            for medicine_id, quantity in ordered_items:
                cursor.execute(
                    "UPDATE medications SET quantity = quantity - ? WHERE id = ?",
                    (quantity, medicine_id)
                )
            
            # Clear cart
            cursor.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))
            
            conn.commit()
        
        conn.close()
        
        # Update the cart display
        update_cart_display(cart_tree, total_label, username)
        
        # Close payment window
        payment_window.destroy()
        
        # Show success message
        messagebox.showinfo(
            "Payment Successful", 
            "Your payment has been processed successfully!\nYour medicines will be delivered within 24-48 hours."
        )
    
    # Payment buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill="x", pady=(20, 0))
    
    pay_button = tk.Button(
        button_frame,
        bg="#31f627",
        fg="#000000",
        text="Complete Payment",
        command=complete_payment
    )
    pay_button.pack(fill="x", pady=(0, 10), ipady=5)
    
    cancel_button = tk.Button(
        button_frame,
        bg="#f53434",
        fg="#000000",
        text="Cancel",
        command=payment_window.destroy
    )
    cancel_button.pack(fill="x", ipady=5)
    
    # Center window on parent
    center_window(payment_window)

def add_to_cart(medicine_var, quantity_var, cart_tree, total_label, username):
    """Add a medicine to the shopping cart"""
    # Get selected medicine
    medicine_name = medicine_var.get()
    if not medicine_name:
        messagebox.showerror("Error", "Please select a medicine")
        return
    
    # Get quantity
    try:
        quantity = int(quantity_var.get())
        if quantity <= 0:
            messagebox.showerror("Error", "Please enter a valid quantity")
            return
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid quantity")
        return
    
    # Get medicine details from database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, price, quantity FROM medications WHERE name = ?", (medicine_name,))
    result = cursor.fetchone()
    
    if not result:
        messagebox.showerror("Error", "Medicine not found")
        conn.close()
        return
    
    medicine_id, price, available_quantity = result
    
    # Check if enough quantity is available
    if quantity > available_quantity:
        messagebox.showerror("Error", f"Only {available_quantity} units available")
        conn.close()
        return
    
    # Calculate subtotal
    subtotal = price * quantity
    
    # Add to cart_items table
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    
    if not result:
        messagebox.showerror("Error", "User not found")
        conn.close()
        return
    
    user_id = result[0]
    
    # Check if item already exists in cart
    cursor.execute(
        "SELECT id, quantity FROM cart_items WHERE user_id = ? AND medicine_id = ?",
        (user_id, medicine_id)
    )
    existing_item = cursor.fetchone()
    
    if existing_item:
        # Update existing item
        cart_item_id, current_quantity = existing_item
        
        new_quantity = current_quantity + quantity
        
        # Check if new quantity exceeds available stock
        if new_quantity > available_quantity:
            messagebox.showerror("Error", f"Cannot add {quantity} more units. Only {available_quantity - current_quantity} additional units available.")
            conn.close()
            return
        
        cursor.execute(
            "UPDATE cart_items SET quantity = ?, price = ? WHERE id = ?",
            (new_quantity, price, cart_item_id)
        )
    else:
        # Insert new item
        cursor.execute(
            "INSERT INTO cart_items (user_id, medicine_id, quantity, price) VALUES (?, ?, ?, ?)",
            (user_id, medicine_id, quantity, price)
        )
    
    conn.commit()
    conn.close()
    
    # Update the cart display
    update_cart_display(cart_tree, total_label, username)
    
    # Reset quantity
    quantity_var.set("1")
    
    messagebox.showinfo("Success", f"{quantity} units of {medicine_name} added to cart")

def create_purchase_tab(parent, username):
    """Create the purchase medicines tab"""
    # Create main frame
    main_frame = ttk.Frame(parent)
    main_frame.pack(fill="both", expand=True)
    
    # Create two columns
    left_frame = ttk.Frame(main_frame)
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
    
    right_frame = ttk.Frame(main_frame)
    right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
    
    # Left frame - Medicine catalog
    catalog_card = create_custom_card(left_frame, "Medicine Catalog")
    
    # Create treeview for medicine catalog
    catalog_frame = ttk.Frame(catalog_card)
    catalog_frame.pack(fill="both", expand=True)
    
    columns = ("Medicine", "Price", "Description", "Available")
    catalog_tree = ttk.Treeview(catalog_frame, columns=columns, show="headings", height=10)
    
    # Configure columns
    catalog_tree.heading("Medicine", text="Medicine Name")
    catalog_tree.heading("Price", text="Price")
    catalog_tree.heading("Description", text="Description")
    catalog_tree.heading("Available", text="In Stock")
    
    catalog_tree.column("Medicine", width=150)
    catalog_tree.column("Price", width=80)
    catalog_tree.column("Description", width=250)
    catalog_tree.column("Available", width=80)
    
    catalog_tree.pack(side="left", fill="both", expand=True)
    
    # Add scrollbar
    catalog_scrollbar = ttk.Scrollbar(catalog_frame, orient="vertical", command=catalog_tree.yview)
    catalog_scrollbar.pack(side="right", fill="y")
    catalog_tree.configure(yscrollcommand=catalog_scrollbar.set)
    
    # Load medicines
    medicines = load_medicines()
    for medicine in medicines:
        medicine_id, name, price, description, quantity = medicine
        catalog_tree.insert("", "end", iid=medicine_id, values=(
            name,
            f"₹{price:.2f}",
            description,
            quantity
        ))
    
    # Add to cart section
    add_card = create_custom_card(left_frame, "Add to Cart")
    
    # Medicine selection
    medicine_label = ttk.Label(add_card, text="Select Medicine:")
    medicine_label.pack(anchor="w", pady=(0, 5))
    
    medicine_var = tk.StringVar()
    medicine_names = [medicine[1] for medicine in medicines]
    medicine_combo = ttk.Combobox(add_card, textvariable=medicine_var, values=medicine_names)
    medicine_combo.pack(fill="x", pady=(0, 15))
    
    # Quantity
    quantity_label = ttk.Label(add_card, text="Quantity:")
    quantity_label.pack(anchor="w", pady=(0, 5))
    
    quantity_var = tk.StringVar(value="1")
    quantity_entry = ttk.Entry(add_card, textvariable=quantity_var)
    quantity_entry.pack(fill="x", pady=(0, 15))
    
    # Add button
    add_button = ttk.Button(
        add_card,
        text="Add to Cart",
        command=lambda: add_to_cart(medicine_var, quantity_var, cart_tree, total_label, username)
    )
    add_button.pack(fill="x")
    
    # Update medicine selection when clicking on catalog
    def on_catalog_select(event):
        selected = catalog_tree.focus()
        if selected:
            medicine_name = catalog_tree.item(selected)["values"][0]
            medicine_var.set(medicine_name)
    
    catalog_tree.bind("<<TreeviewSelect>>", on_catalog_select)
    
    # Right frame - Shopping cart
    cart_card = create_custom_card(right_frame, "Shopping Cart")
    
    # Create treeview for cart
    cart_frame = ttk.Frame(cart_card)
    cart_frame.pack(fill="both", expand=True)
    
    cart_columns = ("Item", "Quantity", "Price", "Subtotal")
    cart_tree = ttk.Treeview(cart_frame, columns=cart_columns, show="headings", height=10)
    
    # Configure columns
    cart_tree.heading("Item", text="Item")
    cart_tree.heading("Quantity", text="Quantity")
    cart_tree.heading("Price", text="Price")
    cart_tree.heading("Subtotal", text="Subtotal")
    
    cart_tree.column("Item", width=150)
    cart_tree.column("Quantity", width=80)
    cart_tree.column("Price", width=80)
    cart_tree.column("Subtotal", width=100)
    
    cart_tree.pack(side="left", fill="both", expand=True)
    
    # Add scrollbar
    cart_scrollbar = ttk.Scrollbar(cart_frame, orient="vertical", command=cart_tree.yview)
    cart_scrollbar.pack(side="right", fill="y")
    cart_tree.configure(yscrollcommand=cart_scrollbar.set)
    
    # Cart total
    total_label = ttk.Label(cart_card, text="Total: ₹0.00", font=("Segoe UI", 12, "bold"))
    total_label.pack(anchor="e", pady=(10, 5))
    
    # Cart buttons
    button_frame = ttk.Frame(cart_card)
    button_frame.pack(fill="x", pady=(0, 5))
    
    remove_button = ttk.Button(
        button_frame,
        text="Remove Selected",
        command=lambda: remove_from_cart(cart_tree, total_label, username)
    )
    remove_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
    
    clear_button = ttk.Button(
        button_frame,
        text="Clear Cart",
        command=lambda: clear_cart(cart_tree, total_label, username)
    )
    clear_button.pack(side="right", fill="x", expand=True)
    
    # Checkout button
    checkout_button = ttk.Button(
        cart_card,
        text="Checkout",
        command=lambda: checkout(cart_tree, total_label, parent, username)
    )
    checkout_button.pack(fill="x", pady=(5, 0), ipady=5)
    
    # Payment info
    payment_card = create_custom_card(right_frame, "Payment Information")
    
    payment_info = ttk.Label(
        payment_card,
        text="We accept the following payment methods:\n"
            "• UPI Payment\n"
            "• Credit/Debit Card\n"
            "• Net Banking\n"
            "• Cash on Delivery\n\n"
            "Delivery is usually within 24-48 hours.",
        justify="left",
        wraplength=300
    )
    payment_info.pack(fill="both", expand=True)
    
    # Load cart items
    update_cart_display(cart_tree, total_label, username)
    
    return main_frame

# For testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Medicine Purchase Test")
    root.geometry("900x600")
    
    frame = create_purchase_tab(root, "test")
    
   