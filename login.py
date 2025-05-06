import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import CENTER, E
import mysql.connector as sql
import hashlib
from PIL import Image, ImageTk
import SQLconnection
from ttkbootstrap.style import Colors
import customtkinter as ctk
import subprocess

# Setting element transparency for main window
transparent_color = Colors.make_transparent(alpha=0.5, foreground='red', background='white')

# Global Variables
logged_in_Username = None # Variable to store logged-in UserName
role = None # Variable to store logged-in user's role
logged_in_UserID = None  # Variable to store the logged-in userID

# Hasing password function
def hash_password(password):
    """Hashes the password using SHA256."""
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

# Role Check Function
def role_check(username, hashed_password, selected_role):
    """Checks the user's role against the database."""
    try:
        if selected_role == "Client":
            query = "SELECT userid, username, role FROM users WHERE username = %s AND password = %s"
            SQLconnection.cursor.execute(query, (username, hashed_password))
            user = SQLconnection.cursor.fetchone()
            return user
        elif selected_role == "Accountant":
            query = "SELECT accid, username, role FROM accountant WHERE username = %s AND password_hashed = %s"
            SQLconnection.cursor.execute(query, (username, hashed_password))
            user = SQLconnection.cursor.fetchone()
            return user
        else:
            messagebox.showwarning("Input Error", "Please select a role.")
            return None
    except sql.Error as e:
        messagebox.showerror("Database Error", f"Error checking role: {e}")
        return None
    except AttributeError as e:
        messagebox.showerror("Database Error", f"Database cursor error: {e}")
        return None

# call forgot password
def forgotpassword(username):
    subprocess.Popen(["python", "passwordhelp.py"])

# call signup
def signup():
    subprocess.Popen(["python", "signup.py"])

# check login credentials against established user and accountant dbs depending on role selection
def login():
    global logged_in_Username, role, logged_in_UserID
    username = username_entry.get()
    password = password_entry.get()
    selected_role = role_var.get()  # Get the selected role
    selected_role_lower = selected_role.lower() # Convert to lowercase for comparison

    if not username or not password:
        messagebox.showwarning("Input Error", "Please enter both username and password.")
        return

    if not SQLconnection or not hasattr(SQLconnection, 'cursor') or SQLconnection.cursor is None:
        messagebox.showerror("Error", "Database connection/cursor not initialized.")
        return
    if hasattr(SQLconnection, 'is_connected') and not SQLconnection.is_connected():
        messagebox.showerror("Error", "Database is not connected.")
        return  # Or try to reconnect

    try:
        hashed_password = hash_password(password) # hashing password

        if selected_role_lower == "client":
            query = "SELECT userid, username, role FROM users WHERE username = %s AND password = %s"
            SQLconnection.cursor.execute(query, (username, hashed_password))
            user_data = SQLconnection.cursor.fetchone()
            if user_data:
                logged_in_UserID = user_data[0]
                logged_in_Username = user_data[1]
                role = user_data[2]
        elif selected_role_lower == "accountant":
            query = "SELECT accid, username, role FROM accountant WHERE username = %s AND password_hash = %s" # Assuming 'password_hash' is the correct column name
            SQLconnection.cursor.execute(query, (username, hashed_password))
            user_data = SQLconnection.cursor.fetchone()
            if user_data:
                logged_in_UserID = user_data[0]
                logged_in_Username = user_data[1]
                role = user_data[2]
        else:
            messagebox.showwarning("Input Error", "Please select a role.")
            return

        if logged_in_Username and role:
            messagebox.showinfo("Success", f"Login Successful as {logged_in_Username} ({role})!")

            if role.lower() == "accountant": # Use lowercase for comparison here too
                try:
                    import accountdashboard  # Import the dashboard script
                    # Call the create_dashboard function from the imported module
                    subprocess.Popen(
                        ["python", "accountdashboard.py", str(logged_in_UserID), logged_in_Username, role]) # passing authenticated user to next module
                    root.destroy()  # Close the login window
                except ImportError:
                    messagebox.showerror("Error", "Accountant Dashboard not found.")
                except AttributeError:
                    messagebox.showerror("Error",
                                         "Accountant Dashboard does not have a 'create_dashboard' function.")
                except TypeError as e:
                    messagebox.showerror("Error",
                                         f"Error calling Accountant Dashboard: {e}\nDid you update its definition to accept (userid, username, role)?")

            elif role.lower() == "client": # Use lowercase for comparison here too
                try:
                    import ClientDashboard
                    # *** PASS USER ID, USERNAME, AND ROLE ***
                    subprocess.Popen(
                        ["python", "ClientDashboard.py", str(logged_in_UserID), logged_in_Username, role]) # passing authenticated user to next module
                    root.destroy()  # Close the login window
                except ImportError:
                    messagebox.showerror("Error", "Client Dashboard not found.")
                except AttributeError:
                    messagebox.showerror("Error", "Client Dashboard does not have a 'run' function.")
                except TypeError as e:  # Catch error if run() doesn't accept three arguments
                    messagebox.showerror("Error",
                                         f"Error calling Client Dashboard: {e}\nDid you update its definition to accept (userid, username, role)?")
            else:
                messagebox.showerror("Error", f"Unknown user role: {role}")
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    except sql.Error as e:  # Catch database errors specifically
        messagebox.showerror("Error", f"Database Error: {e}")
        print(f"SQL Error: {e}") # Print the specific SQL error
    except AttributeError as e:  # Catch errors like cursor being None if connection dropped
        messagebox.showerror("Error", f"Database Access Error: {e}. Connection might be closed.")
    except Exception as e:  # Catch any other unexpected error
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

# create login screen
def run_login_screen():
    """Runs the login screen application."""
    global root, username_entry, password_entry, role_var, canvas

    WINDOW_WIDTH = 920
    WINDOW_HEIGHT = 655

    root = ttkb.Window(title="Accounting Login", themename="cerculean")
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    root.resizable(False, False)

    # Use grid layout for the root window
    root.grid_columnconfigure(0, weight=1)  # Left column for image
    root.grid_columnconfigure(1, weight=1)  # Right column for login, expand to fill
    root.grid_rowconfigure(0, weight=1)

    # Canvas for the background image on the left
    image_canvas = tk.Canvas(root, highlightthickness=0)
    image_canvas.configure(width=WINDOW_WIDTH // 2, height=WINDOW_HEIGHT)
    image_canvas.grid(row=0, column=0, sticky="nsew")

    # Load and display background image on the left canvas
    try:
        bg_image_path = r"images/signin_image_final.jpg "
        bg_image = Image.open(bg_image_path)
        bg_image = bg_image.resize((WINDOW_WIDTH // 2, WINDOW_HEIGHT), Image.Resampling.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)
        image_canvas.create_image(0, 0, image=bg_photo, anchor="nw")
    except FileNotFoundError:
        print(f"Warning: Background image not found at '{bg_image_path}'. Displaying without background.")
        image_canvas.config(bg=ttkb.Style().colors.get('bg'))
    except Exception as e:
        print(f"Error loading background image: {e}")
        image_canvas.config(bg=ttkb.Style().colors.get('bg'))

    # Frame to hold the login widgets on the right
    login_frame = ctk.CTkFrame(root, fg_color='#85c3e8')  # Let it expand
    login_frame.grid(row=0, column=1, sticky="nsew")  # Sticky "nsew" to fill

    # Configure grid for the login frame to make its contents expand
    login_frame.grid_columnconfigure(0, weight=1)
    login_frame.grid_columnconfigure(1, weight=1)
    login_frame.grid_rowconfigure(0, weight=0)  # Sign In label
    login_frame.grid_rowconfigure(1, weight=0)  # Username label/entry
    login_frame.grid_rowconfigure(2, weight=0)  # Forgot Password
    login_frame.grid_rowconfigure(3, weight=0)  # Password label/entry
    login_frame.grid_rowconfigure(4, weight=0)  # Show Password
    login_frame.grid_rowconfigure(5, weight=0)  # Account Label
    login_frame.grid_rowconfigure(6, weight=0)  # Role Combobox
    login_frame.grid_rowconfigure(7, weight=1)  # Spacer
    login_frame.grid_rowconfigure(8, weight=0)  # Sign In button
    login_frame.grid_rowconfigure(9, weight=0)  # Sign Up button
    login_frame.grid_rowconfigure(10, weight=1) # Spacer at the bottom

    # Style configuration
    style = ttkb.Style()
    style.configure('TLabel', foreground='#333', background='#85c3e8')
    style.configure('Custom.TLabel', font=('Helvetica', 12),foreground='#333', background='#85c3e8')  # Style for labels inside the frame
    style.configure('TEntry', font=('Helvetica', 12))
    style.configure('TCheckbutton', background='#85c3e8', foreground='#333') # Style for Checkbox
    style.configure('TCombobox', font=('Helvetica', 12)) # Style for Combobox
    style.configure('ForgotPassword.TButton', foreground='#333', background='#85c3e8', borderwidth=0, font=("Arial", 10), cursor="hand2")

    # Sign In Section with Labels and Entry fields
    sign_label = ttkb.Label(login_frame, text="Sign In", font=('Helvetica', 20, 'bold'), foreground='#333',
                                    background='#85c3e8')
    sign_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="ew", padx=5)

    username_label = ttkb.Label(login_frame, text="Username:", style='Custom.TLabel')
    username_label.grid(row=1, column=0, padx=5, pady=(0, 5),  sticky="e")

    username_entry = ctk.CTkEntry(login_frame, width=200, corner_radius=10,text_color='#000000', fg_color="white") # Increased width
    username_entry.grid(row=1, column=1, padx=5, pady=(0, 5),  sticky="ew")

    # Forgot Password Button (moved here)
    forgot_password = ttkb.Button(login_frame, text="Forgot Password", command=lambda: forgotpassword(username_entry), style='ForgotPassword.TButton')
    forgot_password.grid(row=2, column=0, columnspan=2, sticky="e", pady=(5, 10)) # Placed between username and password

    password_label = ttkb.Label(login_frame, text="Password:", style='Custom.TLabel')
    password_label.grid(row=3, column=0, padx=5, pady=(0, 5),  sticky="e")

    password_entry = ctk.CTkEntry(login_frame, show="*", width=200, corner_radius=10,text_color='#000000', fg_color="white") # Increased width
    password_entry.grid(row=3, column=1, padx=5, pady=(0, 5),  sticky="ew")
    # Bind Enter key to the login function
    root.bind('<Return>', lambda event: login())

    # Frame for Show Password
    show_password_frame = ctk.CTkFrame(login_frame, fg_color='#85c3e8')
    show_password_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=0, sticky="ew")
    show_password_frame.grid_columnconfigure(0, weight=1)

    # Show Password Function
    def show_password():
        if show_password_var.get():
            password_entry.configure(show="")
        else:
            password_entry.configure(show="*")

    show_password_var = tk.IntVar()
    show_password_check = ttkb.Checkbutton(show_password_frame, text="Show Password", variable=show_password_var, command=show_password, style='TCheckbutton')
    show_password_check.grid(row=0, column=0, sticky="w", pady=5)

    # Role Selection with default role defined
    role_label = ttkb.Label(login_frame, text="Account:", style='Custom.TLabel')
    role_label.grid(row=5, column=0, columnspan=2, padx=5, pady=(10, 2), sticky="ew")

    roles = ["Client", "Accountant"]
    role_var = tk.StringVar(value=roles[0])  # Default role
    role_combobox = ttkb.Combobox(login_frame, textvariable=role_var, values=roles, state="readonly")
    role_combobox.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(0, 10))

    # Signin Button
    login_button = ctk.CTkButton(login_frame, text="Sign In", command=login, corner_radius=10)
    login_button.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(5, 5))
    # Signup Button
    signup_button = ttkb.Button(login_frame, text="Don't have an account? Sign up", command=lambda: signup, style='ForgotPassword.TButton')
    signup_button.grid(row=9, column=0, columnspan=2, sticky="ew", pady=0) # Reduced pady

    root.mainloop()

    if SQLconnection and hasattr(SQLconnection, 'is_connected') and SQLconnection.is_connected():
        SQLconnection.close()

if __name__ == "__main__":
    # This block will only run when this script is executed directly
    run_login_screen()