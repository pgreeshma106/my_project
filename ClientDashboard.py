import os
import subprocess
import sys
import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog
import customtkinter as ctk
import matplotlib.pyplot as plt
import mysql.connector
import ttkbootstrap as ttkb
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ttkbootstrap.style import Colors
import SQLconnection

transparent_color = Colors.make_transparent(alpha=0.5, foreground='red', background='white')


logged_in_UserID= None
logged_in_Username= None
role= None

def set_user_info(userid, username, user_role):
    global logged_in_Username, role, logged_in_UserID
    logged_in_UserID = userid
    logged_in_Username = username
    role = user_role
    update_title()

def update_title():
    title = "Client Dashboard"
    if logged_in_Username:
        title += f" - User: {logged_in_Username}"
    if 'root' in globals(): # Check if root is defined
        root.title(title)

def support():
    subprocess.Popen(["python","helpandsupport.py"])

def logout():
    subprocess.Popen(["python", "login.py"])
    root.destroy()

def display_transaction_report():
    global logged_in_UserID, logged_in_Username # Make sure logged_in_UserID and logged_in_Username are accessible
    if not logged_in_UserID:
        messagebox.showerror("Authentication Required", "User ID not available. Please log in again.")
        return
    try:
        query = """
            SELECT
                DATE_FORMAT(t.transaction_date, '%Y-%m') AS month,
                SUM(CASE WHEN t.type = 'income' THEN t.transact ELSE 0 END) AS total_income,
                SUM(CASE WHEN t.type = 'expense' THEN ABS(t.transact) ELSE 0 END) AS total_expense
            FROM
                transactions AS t
            WHERE userid = %s
            GROUP BY month
            ORDER BY month;
        """
        print(f"Executing SQL Query: {query} with User ID: {logged_in_UserID}")
        SQLconnection.cursor.execute(query, (logged_in_UserID,))
        monthly_data = SQLconnection.cursor.fetchall()

        if not monthly_data:
            messagebox.showinfo("Report", "No transactions found for the current user.")
            return

        months = []
        income = []
        expense = []
        overall_total_income = 0
        overall_total_expense = 0

        for row in monthly_data:
            month, total_income, total_expense = row
            months.append(month)
            income.append(total_income)
            expense.append(total_expense)
            overall_total_income += total_income
            overall_total_expense += total_expense

        fig, ax = plt.subplots()

        bar_width = 0.35
        index = range(len(months))

        income_bars = ax.bar([i - bar_width/2 for i in index], income, bar_width, label='Income', color='green')
        expense_bars = ax.bar([i + bar_width/2 for i in index], expense, bar_width, label='Expense', color='red')

        ax.set_xlabel("Month")
        ax.set_ylabel("Amount")
        ax.set_title(f"Income vs Expense by Month for {logged_in_Username}\nTotal Income: ${overall_total_income:.2f}, Total Expenses: ${overall_total_expense:.2f}")
        ax.set_xticks(index)
        ax.set_xticklabels(months, rotation=45, ha="right")
        ax.legend()
        plt.tight_layout()

        # Create a new top-level window for the graph
        graph_window = tk.Toplevel(root)
        graph_window.title("Income vs Expense Report")

        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching data for report: {err}")
    except AttributeError as e:
        messagebox.showerror("Database Error", f"Database cursor error: {e}")
    except NameError:
        messagebox.showerror("Error", "Graph frame not initialized (graph_frame).")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

def link_to_eitracker():
    # Open entryfield.py and pass the logged_in_username as a command-line argument
    global logged_in_Username
    if logged_in_Username:
        try:
            filepath = os.path.join(os.getcwd(), "entryfield.py")
            subprocess.Popen(["python", filepath, logged_in_Username])
        except FileNotFoundError:
            messagebox.showerror("Error", "Expense and Income Tracker not found (entryfield.py).")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open Expense and Income Tracker: {e}")
    else:
        messagebox.showerror("Authentication Error", "No user logged in to pass to the tracker.")

def open_add_vendor_window():
    add_vendor_window = tk.Toplevel(root)
    add_vendor_window.title("Add New Vendor")

    # Labels and Entry fields for Vendor Information
    tk.Label(add_vendor_window, text="Vendor Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    vendor_name_entry = tk.Entry(add_vendor_window)
    vendor_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(add_vendor_window, text="First Name:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    vendor_first_name_entry = tk.Entry(add_vendor_window)
    vendor_first_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(add_vendor_window, text="Last Name:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    vendor_last_name_entry = tk.Entry(add_vendor_window)
    vendor_last_name_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    # Separator or Label for Address Information
    tk.Label(add_vendor_window, text="--- Vendor Address (Optional) ---").grid(row=3, column=0, columnspan=2, pady=10)

    # Labels and Entry fields for Address Information
    tk.Label(add_vendor_window, text="Street Number:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
    street_number_entry = tk.Entry(add_vendor_window)
    street_number_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(add_vendor_window, text="Street Name:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
    street_name_entry = tk.Entry(add_vendor_window)
    street_name_entry.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(add_vendor_window, text="City:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
    city_entry = tk.Entry(add_vendor_window)
    city_entry.grid(row=6, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(add_vendor_window, text="State:").grid(row=7, column=0, padx=5, pady=5, sticky="w")
    state_entry = tk.Entry(add_vendor_window)
    state_entry.grid(row=7, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(add_vendor_window, text="Country:").grid(row=8, column=0, padx=5, pady=5, sticky="w")
    country_entry = tk.Entry(add_vendor_window)
    country_entry.grid(row=8, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(add_vendor_window, text="Postal Code:").grid(row=9, column=0, padx=5, pady=5, sticky="w")
    postal_code_entry = tk.Entry(add_vendor_window)
    postal_code_entry.grid(row=9, column=1, padx=5, pady=5, sticky="ew")

    def add_vendor_to_db():
        vendor_name = vendor_name_entry.get()
        vendor_first_name = vendor_first_name_entry.get()
        vendor_last_name = vendor_last_name_entry.get()

        street_number = street_number_entry.get()
        street_name = street_name_entry.get()
        city = city_entry.get()
        state = state_entry.get()
        country = country_entry.get()
        postal_code = postal_code_entry.get()

        if not vendor_name:
            messagebox.showerror("Error", "Vendor Name is required.")
            return

        try:
            cursor = SQLconnection.cursor
            address_id = None
            if street_number or street_name or city or state or country or postal_code:
                add_query = "INSERT INTO address (street_number, street_name, city, state, country, postal_code) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(add_query, (street_number, street_name, city, state, country, postal_code))
                SQLconnection.conn.commit()
                address_id = cursor.lastrowid

            vendor_query = "INSERT INTO vendor (vendor_name, vendor_first_name, vendor_last_name, addid) VALUES (%s, %s, %s, %s)"
            cursor.execute(vendor_query, (vendor_name, vendor_first_name, vendor_last_name, address_id))
            SQLconnection.conn.commit()
            messagebox.showinfo("Success", f"Vendor '{vendor_name}' added successfully.")
            add_vendor_window.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error adding vendor: {err}")

    add_button = ctk.CTkButton(add_vendor_window, text="Add Vendor", command=add_vendor_to_db, corner_radius=10)
    add_button.grid(row=10, column=0, columnspan=2, pady=10, padx=5, sticky="ew")

# --- Tkinter Setup ---
root = None # Initialize root outside the if block
bg_frame = None
canvas = None
right_frame = None
controls_frame = None
report_button = None
eitracker_button = None
help_btn = None
graph_frame = None # No longer directly used for displaying the graph in the main window
bg_photo = None
add_vendor_button = None # New button for adding vendor

def initialize_ui():
    global root, bg_frame, canvas, right_frame, controls_frame, report_button, eitracker_button, help_btn,bg_photo, add_vendor_button
    root = ttkb.Window(title="Client Dashboard", themename="cerculean")
    root.geometry("1200x600") # Adjusted width to accommodate the graph

    # Frame for the background image (left side)
    bg_frame = ttkb.Frame(root)
    bg_frame.pack(side="left", fill="both", expand=True)

    try:
        bg_image = Image.open(r"images\client_Dashboard.webp")
        bg_image = bg_image.resize((800, 500), Image.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)
    except FileNotFoundError:
        messagebox.ERROR("Warning: Background image not found.")
    except Exception as e:
        messagebox.ERROR(f"Error loading background image: {e}")

     # Create a canvas to hold the background
    canvas = tk.Canvas(bg_frame, width=800, height=500)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    # Frame for the right side containing controls
    right_frame = ttkb.Frame(root)
    right_frame.pack(side="right", fill="y")

    # Frame for the input controls (top of the right side)
    controls_frame = ttkb.Frame(right_frame)
    controls_frame.pack(pady=(10, 10), padx=10, fill="x")

    # Report Button
    report_button = ctk.CTkButton(controls_frame, text="Customer Overview Report", command=display_transaction_report, corner_radius=10)
    report_button.pack(pady=(0, 5), fill="x")

    # Link to EITracker4 Button
    eitracker_button = ctk.CTkButton(controls_frame, text="Income and Expense Tracker", command=link_to_eitracker, corner_radius=10)
    eitracker_button.pack(pady=(5, 0), fill="x")

    # Add Vendor Button
    add_vendor_button = ctk.CTkButton(controls_frame, text="Add Vendor", command=open_add_vendor_window, corner_radius=10)
    add_vendor_button.pack(pady=(5, 0), fill="x")

    # Help and Support Button
    help_btn=ctk.CTkButton(controls_frame, text="Need help?", command=support, corner_radius=10)
    help_btn.pack(pady=(5, 0), fill="x")

    # Log Out
    logout_button = ctk.CTkButton(controls_frame, text="Log Out", command=logout, corner_radius=10)
    logout_button.pack(pady=(5, 0), fill="x")

        # --- Closing Connection ---
    def on_closing():
        if hasattr(SQLconnection, 'conn') and SQLconnection.conn.is_connected():
            SQLconnection.conn.close()
        if root:
            root.destroy()

    if root:
        root.protocol("WM_DELETE_WINDOW", on_closing)

if __name__ == "__main__":
    initialize_ui() # Initialize the UI

    if len(sys.argv) == 4:
        user_id = sys.argv[1]
        logged_in_Username = sys.argv[2]
        role = sys.argv[3]
        try:
            logged_in_UserID = int(user_id)
        except ValueError:
            messagebox.showerror("Error", "Invalid User ID format.")
            sys.exit()
        update_title() # Update the title with the username
    else:
        messagebox.showerror ("Error: User ID, username, and role were not passed to the dashboard.")
        # Handle the case where arguments are missing

    if root:
        root.mainloop()