"""
Enhanced Payment Window with scrolling support
This module creates a payment window with scrollable content for the Medical Assistant application.
"""

import tkinter as tk
from tkinter import ttk, messagebox

def create_payment_window(parent, total_amount, cart_tree, username, on_complete_callback):
    """Create a payment window with scrollable content"""
    # Create the payment window
    payment_window = tk.Toplevel(parent)
    payment_window.title("Complete Payment")
    payment_window.geometry("500x600")
    payment_window.transient(parent)
    payment_window.grab_set()
    
    # Create a canvas with scrollbar for scrollable content
    canvas = tk.Canvas(payment_window)
    scrollbar = ttk.Scrollbar(payment_window, orient="vertical", command=canvas.yview)
    
    # Configure the canvas to use scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Layout scrollbar and canvas
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    
    # Create main frame inside canvas
    main_frame = ttk.Frame(canvas, padding=20)
    
    # Create a window in the canvas to hold the main frame
    canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")
    
    # Configure the canvas to resize with the window
    def configure_canvas(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        # Make sure main_frame width matches canvas width
        canvas.itemconfig(canvas_window, width=event.width)
    
    main_frame.bind("<Configure>", configure_canvas)
    
    # Configure the canvas to be resized with the window
    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)
    
    canvas.bind("<Configure>", on_canvas_configure)
    
    # Add mouse wheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
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
    
    # Function to update payment method fields visibility
    def update_payment_fields(*args):
        selected = payment_var.get()
        if selected == "Credit/Debit Card":
            card_frame.pack(fill="x", pady=(0, 20))
        else:
            card_frame.pack_forget()
    
    # Bind to payment method changes
    payment_var.trace("w", update_payment_fields)
    
    # Set initial state
    update_payment_fields()
    
    # Billing address
    address_frame = ttk.LabelFrame(main_frame, text="Billing Address")
    address_frame.pack(fill="x", pady=(0, 20))
    
    # Address Line 1
    ttk.Label(address_frame, text="Address Line 1:").pack(anchor="w", pady=(5, 0))
    address1_entry = ttk.Entry(address_frame)
    address1_entry.pack(fill="x", pady=(0, 10), padx=10)
    
    # Address Line 2
    ttk.Label(address_frame, text="Address Line 2 (Optional):").pack(anchor="w", pady=(0, 0))
    address2_entry = ttk.Entry(address_frame)
    address2_entry.pack(fill="x", pady=(0, 10), padx=10)
    
    # City, State, ZIP in one row
    address_row = ttk.Frame(address_frame)
    address_row.pack(fill="x", pady=(0, 10), padx=10)
    
    # City
    city_frame = ttk.Frame(address_row)
    city_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
    ttk.Label(city_frame, text="City:").pack(anchor="w")
    city_entry = ttk.Entry(city_frame)
    city_entry.pack(fill="x")
    
    # State
    state_frame = ttk.Frame(address_row)
    state_frame.pack(side="left", fill="x", expand=True, padx=5)
    ttk.Label(state_frame, text="State:").pack(anchor="w")
    state_entry = ttk.Entry(state_frame)
    state_entry.pack(fill="x")
    
    # ZIP
    zip_frame = ttk.Frame(address_row)
    zip_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))
    ttk.Label(zip_frame, text="ZIP:").pack(anchor="w")
    zip_entry = ttk.Entry(zip_frame)
    zip_entry.pack(fill="x")
    
    # Function to process payment
    def process_payment():
        selected_method = payment_var.get()
        
        # Validate card details if card payment
        if selected_method == "Credit/Debit Card":
            card_num = card_entry.get().strip()
            cvv = cvv_entry.get().strip()
            month = month_var.get()
            year = year_var.get()
            
            if not card_num or len(card_num) < 13:
                messagebox.showerror("Error", "Please enter a valid card number")
                return
                
            if not cvv or len(cvv) < 3:
                messagebox.showerror("Error", "Please enter a valid CVV")
                return
                
            if month == "MM" or year == "YY":
                messagebox.showerror("Error", "Please select expiry date")
                return
        
        # Validate address
        if not address1_entry.get().strip() or not city_entry.get().strip() or not state_entry.get().strip() or not zip_entry.get().strip():
            messagebox.showerror("Error", "Please enter your billing address details")
            return
        
        # Call the completion callback
        on_complete_callback(selected_method)
        
        # Close payment window
        payment_window.destroy()
        
        # Show success message
        messagebox.showinfo(
            "Payment Successful", 
            f"Your order has been placed successfully!\nPayment method: {selected_method}\nTotal amount: ₹{total_amount:.2f}\n\nYour medicines will be delivered within 2-3 business days."
        )
    
    # Buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill="x", pady=(20, 0))
    
    # Payment button
    pay_button = tk.Button(
        button_frame,
        bg="#32f502",
        fg="#000000",
        text="Complete Payment",
        command=process_payment
    )
    pay_button.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=5)
    
    # Cancel button
    cancel_button = tk.Button(
        button_frame,
        bg="#ff1717",
        fg="#000000",
        text="Cancel",
        command=payment_window.destroy
    )
    cancel_button.pack(side="right", fill="x", expand=True, ipady=5)
    
    # Center window
    payment_window.update_idletasks()
    width = payment_window.winfo_width()
    height = payment_window.winfo_height()
    x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
    y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)
    payment_window.geometry(f"{width}x{height}+{x}+{y}")
    
    return payment_window