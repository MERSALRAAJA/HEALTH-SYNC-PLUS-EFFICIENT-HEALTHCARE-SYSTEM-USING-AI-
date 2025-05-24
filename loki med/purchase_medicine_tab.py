"""
Purchase medicine tab UI implementation with improved quantity field visibility and add button
"""

import tkinter as tk
from tkinter import ttk, messagebox, font, Canvas, Frame
import sqlite3
import os
import json
from datetime import datetime
from PIL import Image, ImageTk

# Database path
DB_PATH = os.path.join("database", "medical_assistant.db")

def create_custom_card(parent, title=None, padding=10):
    """Create a custom card widget with a title"""
    # Main card frame with visual styling
    card = ttk.Frame(parent, padding=padding)
    card.pack(fill="both", expand=True, pady=10)
    
    # Add a border effect
    inner_frame = ttk.Frame(card, relief="solid", borderwidth=1)
    inner_frame.pack(fill="both", expand=True, padx=1, pady=1)
    
    # Add title if provided
    if title:
        title_frame = ttk.Frame(inner_frame, padding=(5, 5, 5, 0))
        title_frame.pack(fill="x")
        
        title_label = ttk.Label(
            title_frame, 
            text=title, 
            font=("Segoe UI", 12, "bold"),
            foreground="#000000"
        )
        title_label.pack(anchor="w")
        
        # Add separator with custom color
        separator = ttk.Separator(inner_frame, orient="horizontal")
        separator.pack(fill="x", padx=5, pady=(5, 10))
    
    # Create a content frame
    content_frame = ttk.Frame(inner_frame, padding=(10, 5, 10, 10))
    content_frame.pack(fill="both", expand=True)
    
    return content_frame

def load_medicines():
    """Load medicines from the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, price, description, quantity FROM medications ORDER BY name")
        medicines = cursor.fetchall()
        
        conn.close()
        
        if not medicines:
            # Return default medicines if none found
            return [
                (1, "Amoxicillin", 1079.73, "Antibiotic used to treat bacterial infections", 20),
                (2, "Ciprofloxacin", 1287.53, "Broad-spectrum antibiotic used for respiratory infections", 10),
                (3, "Metronidazole", 830.37, "Antibiotic effective against anaerobic bacteria", 15),
                (4, "Azithromycin", 1578.45, "Macrolide antibiotic used for respiratory infections", 12),
                (5, "Cephalexin", 1205.24, "First-generation cephalosporin antibiotic", 25),
                (6, "Amoxicillin + Clavulanate", 1910.93, "Combination antibiotic with beta-lactamase inhibitor", 18),
                (7, "Doxycycline", 996.61, "Tetracycline antibiotic effective against many bacteria", 30),
                (8, "Cloxacillin", 1142.90, "Penicillin antibiotic resistant to penicillinase", 20),
                (9, "Clarithromycin", 1661.57, "Macrolide antibiotic used for respiratory infections", 15),
                (10, "Paracetamol", 497.89, "Pain reliever and fever reducer", 50)
            ]
        
        return medicines
    except Exception as e:
        print(f"Error loading medicines: {e}")
        # Return default medicines if error occurs
        return [
            (1, "Amoxicillin", 1079.73, "Antibiotic used to treat bacterial infections", 20),
            (2, "Ciprofloxacin", 1287.53, "Broad-spectrum antibiotic used for respiratory infections", 10),
            (3, "Metronidazole", 830.37, "Antibiotic effective against anaerobic bacteria", 15),
            (4, "Azithromycin", 1578.45, "Macrolide antibiotic used for respiratory infections", 12),
            (5, "Cephalexin", 1205.24, "First-generation cephalosporin antibiotic", 25),
            (6, "Amoxicillin + Clavulanate", 1910.93, "Combination antibiotic with beta-lactamase inhibitor", 18),
            (7, "Doxycycline", 996.61, "Tetracycline antibiotic effective against many bacteria", 30),
            (8, "Cloxacillin", 1142.90, "Penicillin antibiotic resistant to penicillinase", 20),
            (9, "Clarithromycin", 1661.57, "Macrolide antibiotic used for respiratory infections", 15),
            (10, "Paracetamol", 497.89, "Pain reliever and fever reducer", 50)
        ]

def add_to_cart(catalog_tree, medicine_var, quantity_var, cart_tree, total_label, username):
    """Add a medicine to the shopping cart"""
    # Get selected medicine
    medicine_name = medicine_var.get()
    if not medicine_name:
        # If no medicine selected from dropdown, try to get from the selected tree item
        selected = catalog_tree.selection()
        if selected:
            medicine_name = catalog_tree.item(selected[0])["values"][0]
        
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

def update_cart_display(cart_tree, total_label, username):
    """Update the cart display with items from the database"""
    try:
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
            # If user not found in the database
            total_label.config(text="Total: ₹0.00")
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
        
    except Exception as e:
        print(f"Error updating cart: {e}")
        total_label.config(text="Total: ₹0.00")

def remove_from_cart(cart_tree, total_label, username):
    """Remove selected item from the cart"""
    selected = cart_tree.selection()
    if not selected:
        messagebox.showinfo("Info", "Please select an item to remove")
        return
    
    # Get the cart item ID
    cart_item_id = selected[0]
    
    # Get the name for confirmation message
    item_values = cart_tree.item(selected[0], "values")
    item_name = item_values[0]
    item_quantity = item_values[1]
    
    # Confirm removal
    confirm = messagebox.askyesno("Confirm Removal", f"Remove {item_quantity} {item_name} from your cart?")
    if not confirm:
        return
    
    try:
        # Remove from database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM cart_items WHERE id = ?", (cart_item_id,))
        conn.commit()
        conn.close()
        
        # Update display
        update_cart_display(cart_tree, total_label, username)
        
        messagebox.showinfo("Success", f"{item_name} removed from cart")
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to remove item: {str(e)}")

def clear_cart(cart_tree, total_label, username):
    """Clear all items from cart"""
    if not cart_tree.get_children():
        messagebox.showinfo("Info", "Cart is already empty")
        return
    
    # Confirm clear
    confirm = messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all items from your cart?")
    if not confirm:
        return
    
    try:
        # Clear from database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if result:
            user_id = result[0]
            cursor.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))
            conn.commit()
        
        conn.close()
        
        # Update display
        update_cart_display(cart_tree, total_label, username)
        
        messagebox.showinfo("Success", "Cart cleared successfully")
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to clear cart: {str(e)}")

def create_enhanced_payment_window(parent, cart_tree, total_label, username):
    """Create an enhanced payment window with all payment methods"""
    if not cart_tree.get_children():
        messagebox.showinfo("Info", "Your cart is empty")
        return
    
    # Get total amount
    total_text = total_label.cget("text")
    total_amount = float(total_text.replace("Total: ₹", ""))
    
    # Show payment window
    payment_window = tk.Toplevel(parent)
    payment_window.title("Complete Payment")
    payment_window.geometry("500x600")  # Increased height for more content
    payment_window.transient(parent)
    payment_window.grab_set()
    
    # Create a canvas with scrollbar for scrollable content
    main_canvas = Canvas(payment_window)
    scrollbar = ttk.Scrollbar(payment_window, orient="vertical", command=main_canvas.yview)
    
    # Configure the scrolling
    main_canvas.configure(yscrollcommand=scrollbar.set)
    main_canvas.bind('<Configure>', lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
    
    # Pack canvas and scrollbar
    main_canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Create a frame inside the canvas for the content
    main_frame = ttk.Frame(main_canvas)
    main_canvas.create_window((0, 0), window=main_frame, anchor="nw", width=480)  # Fixed width
    
    # Enable mousewheel scrolling
    def _on_mousewheel(event):
        main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    # Content frame with padding
    content_frame = ttk.Frame(main_frame, padding=20)
    content_frame.pack(fill="both", expand=True)
    
    # Title
    title_label = ttk.Label(content_frame, text="Complete Your Payment", font=("Segoe UI", 16, "bold"))
    title_label.pack(pady=(0, 20))
    
    # Order summary
    summary_frame = ttk.LabelFrame(content_frame, text="Order Summary")
    summary_frame.pack(fill="x", pady=(0, 20))
    
    # Create a small treeview to list items
    summary_tree = ttk.Treeview(summary_frame, columns=("Item", "Qty", "Price"), show="headings", height=5)
    summary_tree.heading("Item", text="Item")
    summary_tree.heading("Qty", text="Qty")
    summary_tree.heading("Price", text="Price")
    
    summary_tree.column("Item", width=200)
    summary_tree.column("Qty", width=50, anchor="center")
    summary_tree.column("Price", width=100, anchor="e")
    
    summary_tree.pack(fill="x", padx=10, pady=10)
    
    # Copy items from cart to summary
    for item_id in cart_tree.get_children():
        item_values = cart_tree.item(item_id, "values")
        name, quantity, price, subtotal = item_values
        summary_tree.insert("", "end", values=(name, quantity, subtotal))
    
    # Show total
    total_frame = ttk.Frame(summary_frame)
    total_frame.pack(fill="x", pady=10, padx=10)
    
    total_amount_label = ttk.Label(total_frame, text=f"Total Amount: ", font=("Segoe UI", 11, "bold"))
    total_amount_label.pack(side="left")
    
    total_value_label = ttk.Label(total_frame, text=f"₹{total_amount:.2f}", font=("Segoe UI", 11, "bold"))
    total_value_label.pack(side="right")
    
    # Payment method selection
    payment_frame = ttk.LabelFrame(content_frame, text="Payment Method")
    payment_frame.pack(fill="x", pady=(0, 20))
    
    payment_var = tk.StringVar(value="Credit/Debit Card")
    methods = ["Credit/Debit Card", "UPI", "Net Banking", "Cash on Delivery"]
    
    for method in methods:
        ttk.Radiobutton(payment_frame, text=method, variable=payment_var, value=method).pack(anchor="w", padx=20, pady=5)
    
    # Create all payment method frames
    # 1. Credit card info frame
    card_frame = ttk.Frame(content_frame)
    
    ttk.Label(card_frame, text="Card Number:").pack(anchor="w", pady=(0, 5))
    card_entry = ttk.Entry(card_frame)
    card_entry.pack(fill="x", pady=(0, 10))
    
    card_info_frame = ttk.Frame(card_frame)
    card_info_frame.pack(fill="x")
    
    # Name on card
    ttk.Label(card_frame, text="Name on Card:").pack(anchor="w", pady=(0, 5))
    name_entry = ttk.Entry(card_frame)
    name_entry.pack(fill="x", pady=(0, 10))
    
    exp_frame = ttk.Frame(card_frame)
    exp_frame.pack(fill="x", pady=(0, 10))
    
    ttk.Label(exp_frame, text="Expiry Date:").pack(side="left", padx=(0, 5))
    
    month_var = tk.StringVar(value="MM")
    month_combo = ttk.Combobox(exp_frame, textvariable=month_var, values=[f"{i:02d}" for i in range(1, 13)], width=5)
    month_combo.pack(side="left", padx=(0, 5))
    
    ttk.Label(exp_frame, text="/").pack(side="left", padx=(0, 5))
    
    year_var = tk.StringVar(value="YY")
    year_combo = ttk.Combobox(exp_frame, textvariable=year_var, 
                             values=[str(i)[-2:] for i in range(2025, 2035)], width=5)
    year_combo.pack(side="left")
    
    cvv_frame = ttk.Frame(card_frame)
    cvv_frame.pack(fill="x")
    
    ttk.Label(cvv_frame, text="CVV:").pack(side="left", padx=(0, 5))
    cvv_entry = ttk.Entry(cvv_frame, width=5, show="*")
    cvv_entry.pack(side="left")
    
    # 2. UPI frame
    upi_frame = ttk.Frame(content_frame)
    
    # UPI options frame
    upi_options_frame = ttk.Frame(upi_frame)
    upi_options_frame.pack(fill="x", pady=(0, 10))
    
    # QR Code section
    qr_label = ttk.Label(upi_frame, text="Scan QR Code to Pay:", font=("Segoe UI", 11))
    qr_label.pack(anchor="w", pady=(0, 10))
    
    # QR code image frame
    qr_image_frame = ttk.Frame(upi_frame)
    qr_image_frame.pack(pady=(0, 10))
    
    # Load QR code image
    qr_path = r"C:\Users\Logith\OneDrive\Desktop\loki med\gpay qr.jpg"
    
    # Function to load the QR code image
    def load_qr_image():
        try:
            # Check if file exists
            if os.path.exists(qr_path):
                # Open and resize image
                img = Image.open(qr_path)
                img = img.resize((200, 200), Image.LANCZOS)  # Resize to fit
                photo = ImageTk.PhotoImage(img)
                
                # Create label and display image
                qr_img_label = ttk.Label(qr_image_frame, image=photo)
                qr_img_label.image = photo  # Keep a reference
                qr_img_label.pack(pady=5)
                
                # UPI ID info
                upi_id_frame = ttk.Frame(upi_frame)
                upi_id_frame.pack(fill="x", pady=5)
                
                ttk.Label(upi_id_frame, text="UPI ID: dhanakesavan2004@okaxis", font=("Segoe UI", 10)).pack(anchor="center")
                ttk.Label(upi_id_frame, text="Bank: Canara Bank 8956", font=("Segoe UI", 10)).pack(anchor="center")
                
                # Or enter UPI ID manually
                manual_upi_frame = ttk.Frame(upi_frame)
                manual_upi_frame.pack(fill="x", pady=(10, 0))
                
                ttk.Label(manual_upi_frame, text="Or Enter Your UPI ID:").pack(anchor="w", pady=(0, 5))
                
                upi_entry_frame = ttk.Frame(manual_upi_frame)
                upi_entry_frame.pack(fill="x")
                
                upi_entry = ttk.Entry(upi_entry_frame)
                upi_entry.pack(side="left", fill="x", expand=True)
                
                verify_button = tk.Button(upi_entry_frame,bg="#3116f9",fg="#000000", text="Verify", width=10)
                verify_button.pack(side="right", padx=(5, 0))
            else:
                error_label = ttk.Label(qr_image_frame, text="QR image not found", foreground="red")
                error_label.pack(pady=5)
        except Exception as e:
            error_label = ttk.Label(qr_image_frame, text=f"Error loading QR image: {str(e)}", foreground="red")
            error_label.pack(pady=5)
    
    # Schedule image loading
    payment_window.after(100, load_qr_image)
    
    # 3. Net Banking frame
    netbanking_frame = ttk.Frame(content_frame)
    
    ttk.Label(netbanking_frame, text="Select Your Bank:").pack(anchor="w", pady=(0, 10))
    
    # Popular banks frame
    popular_banks_frame = ttk.LabelFrame(netbanking_frame, text="Popular Banks")
    popular_banks_frame.pack(fill="x", pady=(0, 10))
    
    bank_var = tk.StringVar()
    banks = ["SBI", "HDFC Bank", "ICICI Bank", "Axis Bank", "Canara Bank", "Bank of Baroda"]
    
    # Create a grid of radio buttons for banks
    for i, bank in enumerate(banks):
        row, col = divmod(i, 2)
        ttk.Radiobutton(popular_banks_frame, text=bank, variable=bank_var, value=bank).grid(
            row=row, column=col, sticky="w", padx=15, pady=5)
    
    # Other banks
    ttk.Label(netbanking_frame, text="Or Select Other Bank:").pack(anchor="w", pady=(10, 5))
    
    other_banks = ["Punjab National Bank", "Union Bank", "Indian Bank", "Kotak Mahindra Bank", 
                   "Yes Bank", "IndusInd Bank", "Federal Bank", "South Indian Bank"]
    
    bank_combo = ttk.Combobox(netbanking_frame, values=banks + other_banks, state="readonly")
    bank_combo.pack(fill="x")
    
    # 4. Cash on Delivery frame
    cod_frame = ttk.Frame(content_frame)
    
    cod_info = ttk.Label(
        cod_frame,
        text="Pay in cash at the time of delivery. Additional COD fee of ₹40 will be charged.",
        wraplength=400,
        justify="left"
    )
    cod_info.pack(anchor="w", pady=10)
    
    # Delivery address
    address_label = ttk.Label(cod_frame, text="Confirm Delivery Address:", font=("Segoe UI", 11))
    address_label.pack(anchor="w", pady=(10, 5))
    
    address_entry = tk.Text(cod_frame, height=4, width=40)
    address_entry.insert("1.0", "Enter your complete delivery address here...")
    address_entry.pack(fill="x", pady=(0, 10))
    
    # Function to update payment method fields visibility
    def update_payment_fields(*args):
        selected = payment_var.get()
        
        # Hide all frames first
        card_frame.pack_forget()
        upi_frame.pack_forget()
        netbanking_frame.pack_forget()
        cod_frame.pack_forget()
        
        # Show the selected frame
        if selected == "Credit/Debit Card":
            card_frame.pack(fill="x", pady=(0, 20))
        elif selected == "UPI":
            upi_frame.pack(fill="x", pady=(0, 20))
        elif selected == "Net Banking":
            netbanking_frame.pack(fill="x", pady=(0, 20))
        elif selected == "Cash on Delivery":
            cod_frame.pack(fill="x", pady=(0, 20))
        
        # Update scrollregion after changing content
        payment_window.update_idletasks()
        main_canvas.configure(scrollregion=main_canvas.bbox("all"))
    
    # Bind to payment method changes
    payment_var.trace("w", update_payment_fields)
    
    # Buttons
    button_frame = ttk.Frame(content_frame)
    button_frame.pack(fill="x", pady=(20, 10))
    
    # Function to process payment
    def process_payment():
        selected_method = payment_var.get()
        
        # Validate input based on payment method
        if selected_method == "Credit/Debit Card":
            card_num = card_entry.get().strip()
            name = name_entry.get().strip()
            cvv = cvv_entry.get().strip()
            month = month_var.get()
            year = year_var.get()
            
            if not card_num or len(card_num) < 13:
                messagebox.showerror("Error", "Please enter a valid card number")
                return
                
            if not name:
                messagebox.showerror("Error", "Please enter the name on card")
                return
                
            if not cvv or len(cvv) < 3:
                messagebox.showerror("Error", "Please enter a valid CVV")
                return
                
            if month == "MM" or year == "YY":
                messagebox.showerror("Error", "Please select expiry date")
                return
        
        elif selected_method == "Net Banking":
            if not bank_var.get() and not bank_combo.get():
                messagebox.showerror("Error", "Please select a bank")
                return
        
        elif selected_method == "Cash on Delivery":
            address = address_entry.get("1.0", "end-1c").strip()
            if not address or address == "Enter your complete delivery address here...":
                messagebox.showerror("Error", "Please enter your delivery address")
                return
        
        # Close payment window
        payment_window.destroy()
        
        # Show success message
        success_msg = f"Your order has been placed successfully!\n\n"
        success_msg += f"Payment method: {selected_method}\n"
        success_msg += f"Total amount: ₹{total_amount:.2f}\n\n"
        
        if selected_method == "Cash on Delivery":
            success_msg += f"Total payable at delivery: ₹{total_amount + 40:.2f} (includes ₹40 COD fee)\n\n"
        
        success_msg += "Your medicines will be delivered within 2-3 business days."
        
        messagebox.showinfo("Payment Successful", success_msg)
    
    # Payment button
    pay_button = tk.Button(
        button_frame,
        bg="#31f627",
        fg="#000000",
        text="Complete Payment",
        command=process_payment
    )
    pay_button.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=5)
    
    # Cancel button
    cancel_button = tk.Button(
        button_frame,
        bg="#f8271c",
        fg="#000000",
        text="Cancel",
        command=payment_window.destroy
    )
    cancel_button.pack(side="right", fill="x", expand=True, ipady=5)
    
    # Set initial payment method display
    update_payment_fields()
    
    # Center window
    payment_window.update_idletasks()
    width = payment_window.winfo_width()
    height = payment_window.winfo_height()
    x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
    y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)
    payment_window.geometry(f"{width}x{height}+{x}+{y}")
    
    # Make sure the scrollregion is updated after all widgets are in place
    payment_window.update_idletasks()
    main_canvas.configure(scrollregion=main_canvas.bbox("all"))


def checkout(cart_tree, total_label, parent, username):
    """Process checkout by opening the enhanced payment window"""
    create_enhanced_payment_window(parent, cart_tree, total_label, username)
    if not cart_tree.get_children():
        messagebox.showinfo("Info", "Your cart is empty")
        return
    
    # Get total amount
    total_text = total_label.cget("text")
    total_amount = float(total_text.replace("Total: ₹", ""))
    
    # Show payment window
    payment_window = tk.Toplevel(parent)
    payment_window.title("Complete Payment")
    payment_window.geometry("500x500")
    payment_window.transient(parent)
    payment_window.grab_set()
    
    # Main frame
    main_frame = ttk.Frame(payment_window, padding=20)
    main_frame.pack(fill="both", expand=True)
    
    # Title
    title_label = ttk.Label(main_frame, text="Complete Your Payment", font=("Segoe UI", 16, "bold"))
    title_label.pack(pady=(0, 20))
    
    # Order summary
    summary_frame = ttk.LabelFrame(main_frame, text="Order Summary")
    summary_frame.pack(fill="x", pady=(0, 20))
    
    # Create a small treeview to list items
    summary_tree = ttk.Treeview(summary_frame, columns=("Item", "Qty", "Price"), show="headings", height=5)
    summary_tree.heading("Item", text="Item")
    summary_tree.heading("Qty", text="Qty")
    summary_tree.heading("Price", text="Price")
    
    summary_tree.column("Item", width=200)
    summary_tree.column("Qty", width=50, anchor="center")
    summary_tree.column("Price", width=100, anchor="e")
    
    summary_tree.pack(fill="x", padx=10, pady=10)
    
    # Copy items from cart to summary
    for item_id in cart_tree.get_children():
        item_values = cart_tree.item(item_id, "values")
        name, quantity, price, subtotal = item_values
        summary_tree.insert("", "end", values=(name, quantity, subtotal))
    
    # Show total
    total_frame = ttk.Frame(summary_frame)
    total_frame.pack(fill="x", pady=10, padx=10)
    
    total_amount_label = ttk.Label(total_frame, text=f"Total Amount: ", font=("Segoe UI", 11, "bold"))
    total_amount_label.pack(side="left")
    
    total_value_label = ttk.Label(total_frame, text=f"₹{total_amount:.2f}", font=("Segoe UI", 11, "bold"))
    total_value_label.pack(side="right")
    
    # Payment method selection
    payment_frame = ttk.LabelFrame(main_frame, text="Payment Method")
    payment_frame.pack(fill="x", pady=(0, 20))
    
    payment_var = tk.StringVar(value="Credit/Debit Card")
    methods = ["Credit/Debit Card", "UPI", "Net Banking", "Cash on Delivery"]
    
    for method in methods:
        ttk.Radiobutton(payment_frame, text=method, variable=payment_var, value=method).pack(anchor="w", padx=20, pady=5)
    
    # Credit card info frame (visible only for card payment)
    card_frame = ttk.Frame(main_frame)
    card_frame.pack(fill="x", pady=(0, 20))
    
    ttk.Label(card_frame, text="Card Number:").pack(anchor="w", pady=(0, 5))
    card_entry = ttk.Entry(card_frame)
    card_entry.pack(fill="x", pady=(0, 10))
    
    exp_frame = ttk.Frame(card_frame)
    exp_frame.pack(fill="x", pady=(0, 10))
    
    ttk.Label(exp_frame, text="Expiry Date:").pack(side="left", padx=(0, 5))
    
    month_var = tk.StringVar(value="MM")
    month_combo = ttk.Combobox(exp_frame, textvariable=month_var, values=[f"{i:02d}" for i in range(1, 13)], width=5)
    month_combo.pack(side="left", padx=(0, 5))
    
    ttk.Label(exp_frame, text="/").pack(side="left", padx=(0, 5))
    
    year_var = tk.StringVar(value="YY")
    year_combo = ttk.Combobox(exp_frame, textvariable=year_var, 
                             values=[str(i)[-2:] for i in range(2025, 2035)], width=5)
    year_combo.pack(side="left")
    
    cvv_frame = ttk.Frame(card_frame)
    cvv_frame.pack(fill="x")
    
    ttk.Label(cvv_frame, text="CVV:").pack(side="left", padx=(0, 5))
    cvv_entry = ttk.Entry(cvv_frame, width=5, show="*")
    cvv_entry.pack(side="left")


def create_purchase_medicine_tab(parent, username):
    """Create the purchase medicines tab"""
    # Set up custom fonts
    custom_font = font.nametofont("TkDefaultFont").copy()
    custom_font.configure(size=10)
    
    header_font = font.Font(family="Segoe UI", size=12, weight="bold")
    title_font = font.Font(family="Segoe UI", size=11, weight="bold")
    
    # Main frame
    main_frame = ttk.Frame(parent, padding=15)
    main_frame.pack(fill="both", expand=True)
    
    # Create two columns with adjusted proportions - make right side wider
    left_frame = ttk.Frame(main_frame)
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=0)
    
    # Add scrolling capability to left frame
    left_canvas = tk.Canvas(left_frame, borderwidth=0, highlightthickness=0)
    left_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=left_canvas.yview)
    left_scrollable_frame = ttk.Frame(left_canvas)
    
    left_scrollable_frame.bind(
        "<Configure>",
        lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all"))
    )
    
    left_canvas.create_window((0, 0), window=left_scrollable_frame, anchor="nw")
    left_canvas.configure(yscrollcommand=left_scrollbar.set)
    
    left_canvas.pack(side="left", fill="both", expand=True)
    left_scrollbar.pack(side="right", fill="y")
    
    
    # Add mouse wheel scrolling
    def _on_mousewheel(event):
        left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    left_canvas.bind("<MouseWheel>", _on_mousewheel)
    
    # Right frame with increased width - set width proportion
    right_frame = ttk.Frame(main_frame, width=600)  # Set explicit width
    right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
    right_frame.pack_propagate(False)  # Prevent the frame from shrinking to fit its contents
    
    # Left frame - Medicine catalog with reduced spacing
    catalog_card = create_custom_card(left_scrollable_frame, "Medicines Catalog")
    
    # Create treeview for medicine catalog
    catalog_frame = ttk.Frame(catalog_card)
    catalog_frame.pack(fill="both", expand=True)
    
    columns = ("Medicine Name", "Price ($)", "Description", "In Stock")
    catalog_tree = ttk.Treeview(catalog_frame, columns=columns, show="headings", height=10)
    
    # Configure columns
    for col in columns:
        catalog_tree.heading(col, text=col)
    
    catalog_tree.column("Medicine Name", width=150)
    catalog_tree.column("Price ($)", width=80)
    catalog_tree.column("Description", width=250)
    catalog_tree.column("In Stock", width=80)
    
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
    
    # Add to cart section - REDUCED SPACING between catalog and add to cart
    add_card = create_custom_card(left_scrollable_frame, "Add to Cart")

    # Medicine selection
    medicine_label = ttk.Label(add_card, text="Select Medicine:", font=title_font)
    medicine_label.pack(anchor="w", pady=(0, 5))

    medicine_var = tk.StringVar()
    medicine_names = [medicine[1] for medicine in medicines]
    medicine_combo = ttk.Combobox(add_card, textvariable=medicine_var, values=medicine_names, state="readonly", font=custom_font)
    medicine_combo.pack(fill="x", pady=(0, 15))

    # Quantity with high visibility
    quantity_label = ttk.Label(add_card, text="Quantity:", font=title_font)
    quantity_label.pack(anchor="w", pady=(0, 5))

    # Quantity frame with controls
    quantity_frame = ttk.Frame(add_card)
    quantity_frame.pack(fill="x", pady=(0, 20))

    # Using a custom styled Entry with dark border and background color for better visibility
    quantity_var = tk.StringVar(value="1")

    # Create a custom frame for the quantity input for better visibility
    quantity_input_frame = ttk.Frame(quantity_frame, style="QuantityFrame.TFrame")
    quantity_input_frame.pack(side="left", padx=(0, 10))

    # Use a regular Entry instead of ttk.Entry for more styling options
    quantity_entry = tk.Entry(
        quantity_input_frame, 
        textvariable=quantity_var,
        font=("Segoe UI", 16, "bold"),  # Even larger, bold font
        width=5,                        # Compact width
        justify="center",               # Center text
        bg="#1ac54d",                   # White background
        fg="#000000",                   # Black text
        relief="sunken",                # Sunken relief for better visibility
        bd=2                            # Thicker border
    )
    quantity_entry.pack(pady=5, padx=10, ipady=5)  # Extra padding all around

    # Control buttons
    control_frame = ttk.Frame(quantity_frame)
    control_frame.pack(side="left")

    def increase_quantity():
        try:
            current = int(quantity_var.get())
            quantity_var.set(str(current + 1))
        except ValueError:
            quantity_var.set("1")

    def decrease_quantity():
        try:
            current = int(quantity_var.get())
            if current > 1:
                quantity_var.set(str(current - 1))
        except ValueError:
            quantity_var.set("1")

    # Larger control buttons
    minus_btn = ttk.Button(
        control_frame, 
        text="-", 
        width=3,
        command=decrease_quantity,
        style="Control.TButton"
    )
    minus_btn.pack(side="top", pady=(0, 5))
    
    plus_btn = ttk.Button(
        control_frame, 
        text="+", 
        width=3,
        command=increase_quantity,
        style="Control.TButton"
    )
    plus_btn.pack(side="bottom")

    # Large, visually distinct "Add to Cart" button with improved visibility
    add_button = tk.Button(
        add_card,
        text="Add to Cart",
        command=lambda: add_to_cart(catalog_tree, medicine_var, quantity_var, cart_tree, total_label, username),
        font=("Segoe UI", 14, "bold"),
        bg="#1ecd27",                 # Blue background
        fg="#000000",                 # White text
        activebackground="#1ecd27",   # Darker blue when clicked
        activeforeground="#000000",   # White text when clicked
        relief="raised",              # Raised appearance
        bd=2,                         # Thicker border
        padx=10,
        pady=10,
        cursor="hand2"                # Hand cursor on hover
    )
    add_button.pack(fill="x", pady=(10, 5))
    
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
    for col in cart_columns:
        cart_tree.heading(col, text=col)
    
    cart_tree.column("Item", width=150, stretch=tk.YES)
    cart_tree.column("Quantity", width=60, anchor="center", stretch=tk.NO)
    cart_tree.column("Price", width=80, anchor="e", stretch=tk.NO)
    cart_tree.column("Subtotal", width=80, anchor="e", stretch=tk.NO)
    
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
    
    # Remove item button
    remove_button = tk.Button(
        button_frame,
        bg="#ff2c2c",
        fg="#000000",
        text="Remove Item",
        command=lambda: remove_from_cart(cart_tree, total_label, username)
    )
    remove_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
    
    # Clear cart button
    clear_button = tk.Button(
        button_frame,
        bg="#ff2c2c",
        fg="#000000",
        text="Clear Cart",
        command=lambda: clear_cart(cart_tree, total_label, username)
    )
    clear_button.pack(side="right", fill="x", expand=True)
    
    # Checkout button
    checkout_button = tk.Button(
        cart_card,
        text="Checkout",
        command=lambda: checkout(cart_tree, total_label, parent, username),
        font=("Segoe UI", 14, "bold"),
        bg="#1ecd27",                 # Green background
        fg="#000000",                 # White text
        activebackground="#1ecd27",   # Darker green when clicked
        activeforeground="#000000",   # White text when clicked
        relief="raised",              # Raised appearance
        bd=2,                         # Thicker border
        padx=10,
        pady=10,
        cursor="hand2"                # Hand cursor on hover
    )
    checkout_button.pack(fill="x", pady=(5, 0))

    
    return main_frame