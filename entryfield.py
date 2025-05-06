import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import SQLconnection
import mysql.connector # error handling
import customtkinter as ctk
import sys

logged_in_username = None
role = None
userid = None  # Initialize userid as None

# Check for logged-in username from command-line arguments
if len(sys.argv) > 1:
    logged_in_username = sys.argv[1]
    # Now, fetch the userid from the database based on the username
    try:
        SQLconnection.cursor.execute("SELECT userid FROM users WHERE username = %s", (logged_in_username,))
        result = SQLconnection.cursor.fetchone()
        if result:
            userid = result[0]  # Assuming userid is the first column
        else:
            messagebox.showerror("Authentication Error", f"User '{logged_in_username}' not found.")
            sys.exit() # Exit if the user is not found
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching user ID: {err}")
        sys.exit()
else:
    messagebox.showerror("Error", "No username passed to the tracker.")
    sys.exit() # Exit if no username is provided

entries = []
category_name_to_id = {} # Dictionary to store category name to ID mapping
vendor_name_to_id = {} # Dictionary to store vendor name to ID mapping

def populate_categories():
    global category_name_to_id
    try:
        SQLconnection.cursor.execute("SELECT catid, cat_name FROM transaction_categories")  # Fetch both ID and name
        categories_data = SQLconnection.cursor.fetchall()
        categories = [row[1] for row in categories_data]
        category_name_to_id = {row[1]: row[0] for row in categories_data} # Populate the mapping

        category_var.set("Select Category")
        category_dropdown['values'] = categories

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        category_dropdown['values'] = ["Error fetching categories"]

def populate_vendors():
    global vendor_name_to_id
    try:
        SQLconnection.cursor.execute("SELECT vendid, vendor_name FROM vendor")
        vendors_data = SQLconnection.cursor.fetchall()
        vendors = [row[1] for row in vendors_data]
        vendor_name_to_id = {row[1]: row[0] for row in vendors_data}

        vendor_var.set("Optional Vendor")
        vendor_dropdown['values'] = ["Optional Vendor"] + vendors # Add "Optional Vendor" as the default

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        vendor_dropdown['values'] = ["Error fetching vendors"]

def add_entry():
    amount = amount_entry.get()
    description = description_entry.get()
    category_name = category_dropdown.get()
    entry_type = type_combobox.get()
    vendor_name = vendor_dropdown.get()

    if not amount or not description or category_name == "Select Category":
        messagebox.showerror("Input Error", "Please fill in all required fields (Amount, Description, Category).")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Input Error", "Amount must be a number.")
        return

    catid = category_name_to_id.get(category_name)
    if catid is None:
        messagebox.showerror("Database Error", f"Category '{category_name}' not found in database.")
        return

    vendid = None
    if vendor_name != "Optional Vendor":
        vendid = vendor_name_to_id.get(vendor_name)
        if vendid is None:
            messagebox.showerror("Database Error", f"Vendor '{vendor_name}' not found in database.")
            return

    entry_text = f"{entry_type} - {category_name} - {description} - ${amount:.2f}"
    if vendor_name != "Optional Vendor":
        entry_text += f" - Vendor: {vendor_name}"
    entries_listbox.insert(tk.END, entry_text)
    entries.append((entry_type, amount, description, catid, vendid)) # Store catid and vendid

    amount_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)
    category_dropdown.set("Select Category")
    type_combobox.set("Income")
    vendor_dropdown.set("Optional Vendor")

def calculate_total():
    income_total = sum(amount for etype, amount, _, _, _ in entries if etype == "Income")
    expense_total = sum(amount for etype, amount, _, _, _ in entries if etype == "Expense")
    net_total = income_total - expense_total
    messagebox.showinfo("Total", f"Income: ${income_total:.2f}\nExpenses: ${expense_total:.2f}\nNet: ${net_total:.2f}")

def clear_entries():
    entries.clear()
    entries_listbox.delete(0, tk.END)

def update_entries_to_database():
    global logged_in_username, userid
    if not logged_in_username or userid is None:
        messagebox.showerror("Authentication Error", "User not logged in or user ID not found.")
        return

    try:
        for entry_type, amount, description, catid, vendid in entries: # catid and vendid are now stored
            query = """
                INSERT INTO transactions(userid, transaction_date, transact, t_name, catid, type, vendid)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
            now = datetime.datetime.now()
            SQLconnection.cursor.execute(query, (userid, now, amount, description, catid, entry_type, vendid))
        SQLconnection.conn.commit()
        messagebox.showinfo("Success", "Entries updated in the database.")
        clear_entries() # Optionally clear the local entries after saving
    except mysql.connector.Error as err:
        SQLconnection.conn.rollback()
        messagebox.showerror("Database Error", f"Error updating database: {err}")

root = tk.Tk()
root.title("Income/Expense Tracker")
root.geometry("410x550") # Increased height to accommodate the vendor dropdown
root.configure(bg="#e6f2ff")
button_color = "#66b3ff" # Define the desired button color

# Display logged-in username
if logged_in_username:
    username_label = tk.Label(root, text=f"Logged in as: {logged_in_username}", bg="#e6f2ff", font=('Arial', 10))
    username_label.pack(pady=(5, 0))

# Entry Frame
entry_frame = tk.LabelFrame(root, text="Entry Details:", bg="#99ccf2", font=('Arial', 12, 'bold'))
entry_frame.pack(fill="x", padx=10, pady=10)

tk.Label(entry_frame, text="Amount:", bg="#99ccf2").grid(row=0, column=0, padx=5, pady=5, sticky="e")
amount_entry = tk.Entry(entry_frame)
amount_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(entry_frame, text="Description:", bg="#99ccf2").grid(row=1, column=0, padx=5, pady=5, sticky="e")
description_entry = tk.Entry(entry_frame)
description_entry.grid(row=1, column=1, padx=5, pady=5)

category_var = tk.StringVar()
category_label_widget = ttk.Label(entry_frame, text="Category:")
category_label_widget.grid(row=2, column=0, padx=5, pady=5)
category_dropdown = ttk.Combobox(entry_frame, textvariable=category_var, values=[], state="readonly")  # Initialize as empty
category_dropdown.grid(row=2, column=1, padx=5, pady=5)
populate_categories()  # Call after setting up the dropdown

tk.Label(entry_frame, text="Type:", bg="#99ccf2").grid(row=3, column=0, padx=5, pady=5, sticky="e")
type_combobox = ttk.Combobox(entry_frame, values=["Income", "Expense"])
type_combobox.set("Income")
type_combobox.grid(row=3, column=1, padx=5, pady=5)

vendor_var = tk.StringVar()
vendor_label_widget = tk.Label(entry_frame, text="Vendor (Optional):", bg="#99ccf2")
vendor_label_widget.grid(row=4, column=0, padx=5, pady=5)
vendor_dropdown = ttk.Combobox(entry_frame, textvariable=vendor_var, values=[], state="readonly")
vendor_dropdown.grid(row=4, column=1, padx=5, pady=5)
populate_vendors() # Call to populate the vendor dropdown

add_button = ctk.CTkButton(entry_frame, text="Add Entry", command=add_entry, fg_color=button_color, width=20, corner_radius=10)
add_button.grid(row=5, column=0, columnspan=2, pady=10)

# Entries Display
entries_frame = tk.LabelFrame(root, text="Entries:", bg="#99ccf2", font=('Arial', 12, 'bold'))
entries_frame.pack(fill="both", expand=True, padx=10, pady=5)

entries_listbox = tk.Listbox(entries_frame, height=8)
entries_listbox.pack(fill="both", expand=True, padx=5, pady=5)

# Buttons
button_frame = tk.Frame(root, bg="#e6f2ff")
button_frame.pack(pady=10)

calc_button = ctk.CTkButton(button_frame, text="Calculate Total", fg_color=button_color, width=20, command=calculate_total, corner_radius=10)
calc_button.grid(row=0, column=0, padx=10)

clear_button = ctk.CTkButton(button_frame, text="Clear All Entries", fg_color=button_color, width=20, command=clear_entries, corner_radius=10)
clear_button.grid(row=0, column=1, padx=10)

update_db_button = ctk.CTkButton(button_frame, text="Save Entries", fg_color=button_color, width=20, command=update_entries_to_database, corner_radius=10)
update_db_button.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

root.mainloop()