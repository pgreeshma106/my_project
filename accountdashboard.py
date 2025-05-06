import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import SQLconnection
import mysql.connector # error handling
from PIL import Image, ImageTk
import subprocess
import customtkinter as ctk
import sys

Logged_in_UserID=None
logged_in_Username =None
role = None

# Initialize column_names with a default value
column_names = []


def get_all_users_info():
    """Fetches username, first name, and last name from the users table."""
    try:
        query = "SELECT username, firstname, lastname FROM users"
        SQLconnection.cursor.execute(query)
        users_info = []
        for row in SQLconnection.cursor.fetchall():
            username, firstname, lastname = row
            users_info.append(f"{username} ({firstname} {lastname})")
        return users_info
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching users: {err}")
        return []

def if_results():
    global graph_frame, column_names, results, edit_button, submit_update_button, transaction_tree, edit_entries

    if graph_frame is not None:
        graph_frame.destroy()

    graph_frame = ctk.CTkFrame(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT // 2)
    graph_frame.grid(row=1, column=0, columnspan=10, pady=(10, 0), sticky="nsew")
    graph_frame.grid_rowconfigure(0, weight=1)
    graph_frame.grid_columnconfigure(0, weight=1)

    # Create a Treeview widget to display transactions (still using ttk)
    transaction_tree = ttk.Treeview(graph_frame, columns=column_names, show="headings")

    # Define column headings
    for col in column_names:
        transaction_tree.heading(col, text=col, anchor="center")
        transaction_tree.column(col, width=150, anchor="center")  # Adjust width as needed

    # Insert transaction data with a unique identifier (e.g., index)
    for index, row in enumerate(support_results):
        transaction_tree.insert("", "end", values=row, iid=str(index)) # Use index as iid

    # Add scrollbars (still using ttk)
    vsb = ttk.Scrollbar(graph_frame, orient="vertical", command=transaction_tree.yview)
    hsb = ttk.Scrollbar(graph_frame, orient="horizontal", command=transaction_tree.xview)
    transaction_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    transaction_tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")

def open_edit_window():
    global transaction_tree, column_names, results, editing_transaction_id

    selected_item = transaction_tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a transaction to edit.")
        return

    editing_transaction_id = selected_item[0] # Store the transid
    selected_values = transaction_tree.item(editing_transaction_id, 'values')

    edit_window = ctk.CTkToplevel(root)
    edit_window.title("Edit Transaction")

    edit_entries_window = {}
    row_num = 0
    # Iterate through column_names, skipping the "ID" column
    for i, col in enumerate(column_names):
        if col == "ID":
            continue  # Skip the ID column

        # Adjust the index for selected_values to account for the skipped "ID"
        data_index = i if "ID" not in column_names else (i - 1 if i > 0 else i)
        if data_index < len(selected_values):
            label_text = f"Edit {col}:"
            label = ctk.CTkLabel(edit_window, text=label_text)
            label.grid(row=row_num, column=0, padx=10, pady=5, sticky="w")
            entry = ctk.CTkEntry(edit_window)
            entry.insert(0, selected_values[data_index])
            entry.grid(row=row_num, column=1, padx=10, pady=2, sticky="ew")
            edit_entries_window[col] = entry
            row_num += 1
        else:
            print(f"Warning: Index out of bounds for column: {col}") # Debugging



    # Configure column weights so the entry fields expand
    edit_window.grid_columnconfigure(1, weight=1)

    def submit_edit():
        global editing_transaction_id, column_names, results, transaction_tree

        if editing_transaction_id is None:
            messagebox.showerror("Error", "No transaction is being edited.")
            return

        updated_values = {}
        for col in column_names:
            if col == "ID":
                continue
            if col in edit_entries_window:
                updated_values[col] = edit_entries_window[col].get()
            else:
                original_index = column_names.index(col)
                original_values = transaction_tree.item(editing_transaction_id, 'values')
                updated_values[col] = original_values[original_index]

        date = updated_values.get("Date")
        t_name = updated_values.get("Name")
        amount = updated_values.get("Amount")
        category = updated_values.get("Category")
        transaction_type = updated_values.get("Type")
        data_to_update = (date, t_name, amount, category, transaction_type, editing_transaction_id)
        update_query = f"""
            UPDATE transactions
            SET transaction_date = %s,
                t_name = %s,
                transact = %s,
                catid = (SELECT catid FROM transaction_categories WHERE cat_name = %s),
                type = %s
            WHERE transid = %s;
        """

        mydb = SQLconnection.conn
        mycursor = mydb.cursor()
        try:
            mycursor.execute(update_query, data_to_update)
            mydb.commit()
            messagebox.showinfo("Success", "Transaction updated successfully!")
            edit_window.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error updating transaction: {err}")
        finally:
            mycursor.close()
            editing_transaction_id = None

    submit_button_window = ctk.CTkButton(edit_window, text="Submit", command=submit_edit, corner_radius=10)
    submit_button_window.grid(row=row_num, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
    row_num += 1

    cancel_button_window = ctk.CTkButton(edit_window, text="Cancel", command=edit_window.destroy, corner_radius=10)
    cancel_button_window.grid(row=row_num, column=0, columnspan=2, pady=5, padx=10, sticky="ew")

def transaction_mismatch():
    global column_names, results, logged_in_Username, graph_frame, transaction_tree

    # Clear the existing content of the graph_frame
    if graph_frame:
        for widget in graph_frame.winfo_children():
            widget.destroy()

    mydb = SQLconnection.conn
    mycursor = mydb.cursor()
    try:
        query = """
            SELECT
                t.transaction_date,
                t.t_name,
                t.transact,
                tc.cat_name,
                t.type
            FROM
                transactions t
            LEFT JOIN
                transaction_categories tc ON t.catid = tc.catid
            WHERE
                t.type = 'income'
                AND (tc.description NOT LIKE '%INCOME%' AND tc.description NOT LIKE '%PAYMENT%');
        """
        mycursor.execute(query)
        results = mycursor.fetchall()
        column_names = ["Date", "Name", "Amount", "Category", "Type"]

        # Recreate the Treeview widget
        global transaction_tree
        transaction_tree = ttk.Treeview(graph_frame, columns=column_names, show="headings")

        transaction_tree.configure(style="with_gridlines.Treeview")
        style = ttk.Style(root)
        style.layout("with_gridlines.Treeview",
                     [('Treeview.treearea', {'sticky': 'nswe'})])
        transaction_tree.grid(row=0, column=0, sticky="nsew")
        graph_frame.grid_rowconfigure(0, weight=1)
        graph_frame.grid_columnconfigure(0, weight=1)

        # Define column headings
        for col in column_names:
            transaction_tree.heading(col, text=col, anchor="center")
            transaction_tree.column(col, width=150, anchor="center")  # Adjust width as needed

        # Insert transaction data with a unique identifier (e.g., index)
        for index, row in enumerate(results):
            transaction_tree.insert("", "end", values=row, iid=str(index))

        treeview_stripes(transaction_tree)

        # Add scrollbars
        vsb = ttk.Scrollbar(graph_frame, orient="vertical", command=transaction_tree.yview)
        hsb = ttk.Scrollbar(graph_frame, orient="horizontal", command=transaction_tree.xview)
        transaction_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        transaction_tree.grid(row=0, column=0, sticky="nsew")

        if not results:
            no_mismatches_label = ctk.CTkLabel(graph_frame, text="No Mismatched Transactions Found")
            no_mismatches_label.grid(row=0, column=0, padx=10, pady=10) # Use grid here
            graph_frame.grid_columnconfigure(0, weight=1)


    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        mycursor.close()

def fetch_transactions(username):
    global column_names, results
    mydb = SQLconnection.conn
    mycursor = mydb.cursor()
    try:
        query = """
            SELECT
                transaction_date,
                t_name,
                transact,
                transaction_categories.cat_name,
                transactions.type
            FROM
                transactions
            LEFT JOIN
                transaction_categories on transactions.catid=transaction_categories.catid
            WHERE
                userid = (SELECT userid FROM users WHERE username = %s)
        """
        mycursor.execute(query, (username,))
        results = mycursor.fetchall()
        column_names = ["Date", "Name", "Amount", "Category", "Type"]
        return column_names, results
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching transactions: {err}")
        return [], []
    finally:
        mycursor.close()

def show_selected_user_transactions():
    global column_names, results, transaction_tree, graph_frame
    selected_user_info = client_dropdown.get()

    # Clear the existing content of the graph_frame
    if graph_frame:
        for widget in graph_frame.winfo_children():
            widget.destroy()

    if selected_user_info:
        username = selected_user_info.split(" ")[0]
        column_names, results = fetch_transactions(username)
        if results:
            # Recreate the Treeview widget
            transaction_tree = ttk.Treeview(graph_frame, columns=column_names, show="headings")
            for col in column_names:
                transaction_tree.heading(col, text=col, anchor="center")
                transaction_tree.column(col, width=150, anchor="center")
            style = ttk.Style(root)
            style.layout("with_gridlines.Treeview",
                         [('Treeview.treearea', {'sticky': 'nswe'})])
            style.configure("with_gridlines.Treeview", background="#85c3e8", foreground="black")
            style.configure("with_gridlines.Treeview.Heading", background="#85c3e8", foreground="black")
            transaction_tree.grid(row=0, column=0, sticky="nsew")

            for index, row in enumerate(results):
                transaction_tree.insert("", "end", values=row, iid=str(row[0]))
            vsb = ttk.Scrollbar(graph_frame, orient="vertical", command=transaction_tree.yview)
            hsb = ttk.Scrollbar(graph_frame, orient="horizontal", command=transaction_tree.xview)
            transaction_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

            vsb.grid(row=0, column=1, sticky="ns")
            hsb.grid(row=1, column=0, sticky="ew")
            transaction_tree.grid(row=0, column=0, sticky="nsew")

            graph_frame.grid_rowconfigure(0, weight=1)
            graph_frame.grid_columnconfigure(0, weight=1)
            # Removed: transaction_tree.pack(side="left", fill="both", expand=True)
        else:
            if graph_frame:
                no_transactions_label = ctk.CTkLabel(graph_frame, text=f"No transactions found for user '{username}'.")
                no_transactions_label.grid(row=0, column=0, padx=10, pady=10) # Use grid here
                graph_frame.grid_columnconfigure(0, weight=1)
    else:
        messagebox.showwarning("Warning", "Please select a user from the dropdown.")

def fetch_support_entries():
    global support_column_names, support_results
    mydb = SQLconnection.conn
    mycursor = mydb.cursor()
    try:
        query = """
            SELECT
                s.support_id,
                s.support_description,
                u.firstname,
                u.lastname
            FROM
                support s
            JOIN
                users u ON s.userid = u.userid
        """
        mycursor.execute(query)
        support_results = mycursor.fetchall()
        support_column_names = ["Support ID", "Description", "First Name", "Last Name"]
        support_tree = ttk.Treeview(graph_frame, columns=support_column_names, show="headings")
        for col in support_column_names:
            support_tree.heading(col, text=col)
            support_tree.column(col, width=150, anchor="center")

        return support_column_names, support_results
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching support entries: {err}")
        return [], []
    finally:
        mycursor.close()
def show_support_entries():
    global support_column_names, support_results, graph_frame, support_tree

    # Clear the existing content of the graph_frame
    if graph_frame:
        for widget in graph_frame.winfo_children():
            widget.destroy()

    support_column_names, support_results = fetch_support_entries()

    if support_results:
        # Recreate the Treeview widget for support entries
        support_tree = ttk.Treeview(graph_frame, columns=support_column_names, show="headings", style="with_gridlines.Treeview")
        for col in support_column_names:
                support_tree.heading(col, text=col, anchor="center")
                support_tree.column(col, width=150, anchor="center")
                style = ttk.Style(root)
                style.layout("with_gridlines.Treeview",
                                 [('Treeview.treearea', {'sticky': 'nswe'})])
                style.configure("with_gridlines.Treeview", background="#85c3e8", foreground="black")
                style.configure("with_gridlines.Treeview.Heading", background="#85c3e8", foreground="black")
                support_tree.grid(row=0, column=0, sticky="nsew")

        for index, row in enumerate(support_results):  # Use support_results here
            support_tree.insert("", "end", values=row, iid=str(index))

        treeview_stripes(support_tree)

        vsb = ttk.Scrollbar(graph_frame, orient="vertical", command=support_tree.yview)
        hsb = ttk.Scrollbar(graph_frame, orient="horizontal", command=support_tree.xview)
        support_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        support_tree.grid(row=0, column=0, sticky="nsew") # Use support_tree here

        graph_frame.grid_rowconfigure(0, weight=1)
        graph_frame.grid_columnconfigure(0, weight=1)
    else:
        if graph_frame:
            no_support_label = ctk.CTkLabel(graph_frame, text="No support entries found.")
            no_support_label.grid(row=0, column=0, padx=10, pady=10) # Use grid here
            graph_frame.grid_columnconfigure(0, weight=1)


def select_client():
    query = "SELECT username, role FROM users WHERE username = %s AND password = %s"
    pass

def set_user_info(username, user_role):
    global logged_in_Username, role
    logged_in_Username = username
    role = user_role
    update_title()

def update_title():
    title = "Accountant Dashboard"
    if logged_in_Username:
        title += f" - User: {logged_in_Username}"
    root.title(title)

def treeview_stripes(tree):
    children = tree.get_children()
    for index, item in enumerate(children):
        tree.item(item, tags=("evenrow" if index % 2 == 0 else "oddrow",))

    tree.tag_configure("evenrow", background="#f9f9f9")
    tree.tag_configure("oddrow", background="#ffffff")

WINDOW_WIDTH = 820
WINDOW_HEIGHT = 655

ctk.set_appearance_mode("Light")  # Or "Dark", "Light"
ctk.set_default_color_theme("blue")  # Use a built-in theme name

# Set the background color directly when creating the CTk window
root = ctk.CTk(fg_color="#85c3e8")  # Or any other color name or hex code you prefer
root.title("Accountant Dashboard")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)
 # Configure grid weights for root
root.grid_columnconfigure(0, weight=1)  # Controls frame (left)
root.grid_columnconfigure(1, weight=1)  # Background image and graph frame (right)
root.grid_rowconfigure(0, weight=1)    # Background image (top-right)
root.grid_rowconfigure(1, weight=1)
root.configure(fg_color="#85c3e8")    # Graph frame (bottom)

style = ttk.Style(root)
style.theme_use("default")

# Row and heading styles
style = ttk.Style(root)
style.theme_use("default")

# Treeview cells
style.configure("with_gridlines.Treeview",
                background="white",
                foreground="black",
                rowheight=25,
                fieldbackground="white",
                bordercolor="gray",
                borderwidth=1,
                relief="solid")

# Treeview headings
style.configure("with_gridlines.Treeview.Heading",
                background="#e1e1e1",
                foreground="black",
                bordercolor="gray",
                borderwidth=1,
                relief="ridge")

style.layout("with_gridlines.Treeview", [
    ('Treeview.field', {'sticky': 'nswe', 'border': 1}),
    ('Treeview.padding', {'sticky': 'nswe'}),
    ('Treeview.treearea', {'sticky': 'nswe'})
])

# Simulate gridlines by setting borders and alternating row colors
style.map("with_gridlines.Treeview", background=[('selected', '#cce5ff')])

# Optional: Alternate row colors for visual separation (zebra striping)
def treeview_stripes(tree):
    children = tree.get_children()
    for index, item in enumerate(children):
        tags = ("evenrow",) if index % 2 == 0 else ("oddrow",)
        tree.item(item, tags=tags)

    tree.tag_configure("evenrow", background="#f2f2f2")
    tree.tag_configure("oddrow", background="#ffffff")

# Create a ttk Style object
style = ttk.Style(root)
# Configure the background color of the Treeview
style.configure("Treeview", background="#85c3e8", foreground="black") # Set foreground to black for better visibility
style.configure("Treeview.Heading", background="#85c3e8", foreground="black") # Style the headings if needed

# Configure grid weights for root
root.grid_columnconfigure(0, weight=1)  # Controls frame (left)
root.grid_columnconfigure(1, weight=1)  # Background image and graph frame (right)
root.grid_rowconfigure(0, weight=1)    # Background image (top-right)
root.grid_rowconfigure(1, weight=1)    # Graph frame (bottom)

def logout():
    subprocess.Popen(["python", "login.py"])
    root.destroy()

# Frame for the controls (left side)
controls_frame = ctk.CTkFrame(root, fg_color="#85c3e8", bg_color="#85c3e8", border_width=0)
controls_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

# --- Dropdown List of Users ---
users_list = get_all_users_info()
client_label = ctk.CTkLabel(controls_frame, text="Select User:", fg_color="transparent", bg_color="#85c3e8")
client_label.pack(pady=(5, 0), padx=10, anchor="w")

client_dropdown = ctk.CTkComboBox(controls_frame, values=users_list, state="readonly")
client_dropdown.pack(pady=(0, 10), padx=10, fill="x")

# Button to retrieve transactions for the selected user
view_transactions_button = ctk.CTkButton(controls_frame, text="View Transactions", command=show_selected_user_transactions, corner_radius=10, bg_color="#85c3e8", border_width=0, border_color="#85c3e8")
view_transactions_button.pack(pady=(10, 10), padx=10, fill="x")

# Button to show mismatched categories and descriptions
view_mismatch_button = ctk.CTkButton(controls_frame, text="View Mismatched Transactions", command=transaction_mismatch, corner_radius=10, bg_color="#85c3e8", border_width=0, border_color="#85c3e8")
view_mismatch_button.pack(pady=(10, 10), padx=10, fill="x")

# Button to edit transactions
edit_button_control_frame = ctk.CTkButton(controls_frame, text="Edit Transaction", command=open_edit_window, corner_radius=10, bg_color="#85c3e8", border_width=0, border_color="#85c3e8")
edit_button_control_frame.pack(pady=(10, 10), padx=10, fill="x")

# Button to view support entries
support_button=ctk.CTkButton(controls_frame, text="View Support Entries", command=show_support_entries, corner_radius=10, bg_color="#85c3e8", border_width=0, border_color="#85c3e8")
support_button.pack(pady=(10, 10), padx=10, fill="x")

logout_button = ctk.CTkButton(controls_frame, text="Log Out", command=logout, bg_color="#85c3e8", border_width=0, corner_radius=10,border_color="#85c3e8")
logout_button.pack(pady=(10, 10), padx=10, fill="x")

    # Frame for the background image (right side)
bg_frame = ctk.CTkFrame(root)
bg_frame.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="nsew")

bg_photo = None  # Initialize first

def resize_image(event):
    global bg_photo
    try:
        bg_image = Image.open(r"images\Accountant_Dashboard.webp")  # Re-open the image
        new_width = event.width
        new_height = event.height
        bg_image = bg_image.resize((new_width, new_height), Image.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)
        canvas.create_image(0, 0, image=bg_photo, anchor="nw")
    except FileNotFoundError:
        print("Warning: Background image not found during resize.")
    except Exception as e:
        print(f"Error resizing background image: {e}")

# Create a canvas to hold the background
canvas = tk.Canvas(bg_frame, highlightthickness=0)  # Remove width and height
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_photo, anchor="nw")

bg_frame.bind("<Configure>", resize_image)
# Frame for the graph (right side, below the image) - Initialize it here
graph_frame = ctk.CTkFrame(root, fg_color="#85c3e8")
graph_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky="nsew")
graph_frame.grid_rowconfigure(0, weight=1)   # Allow content to expand vertically
graph_frame.grid_columnconfigure(0, weight=1)  # Allow content to expand horizontall


# Create the Treeview widget initially and assign it to the global variable
global transaction_tree
transaction_tree = ttk.Treeview(graph_frame, columns=column_names, show="headings", style="with_gridlines.Treeview")
transaction_tree.configure(style="with_gridlines.Treeview") # column_names will now be an empty list, which is acceptable initially
vsb = ttk.Scrollbar(graph_frame, orient="vertical", command=transaction_tree.yview)
hsb = ttk.Scrollbar(graph_frame, orient="horizontal", command=transaction_tree.xview)
transaction_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

vsb.grid(row=0, column=1, sticky="ns")
hsb.grid(row=1, column=0, sticky="ew")
transaction_tree.grid(row=0, column=0, sticky="nsew")
graph_frame.grid_rowconfigure(0, weight=1)
graph_frame.grid_columnconfigure(0, weight=1)


# --- Closing Connection ---
def on_closing():
    if hasattr(SQLconnection, 'conn') and SQLconnection.conn.is_connected():
        SQLconnection.conn.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

if __name__ == "__main__":
    if len(sys.argv) == 4:
        userid = sys.argv[1]
        logged_in_Username = sys.argv[2]
        role = sys.argv[3]
        try:
            logged_in_UserID = int(userid)
        except ValueError:
            messagebox.showerror("Error", "Invalid User ID format.")
            sys.exit()
        update_title() # Update the title with the username
    else:
        import tkinter.messagebox as mb # Re-import messagebox
        mb.showerror ("Error", "User ID, username, and role were not passed to the dashboard.")
    root.mainloop()