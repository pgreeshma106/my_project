import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import subprocess
from tkinter import messagebox
import mysql.connector
import SQLconnection
import hashlib

def openlogin(app):
    """Opens the login window and destroys the current window."""
    subprocess.Popen(["python", "login.py"])
    app.destroy()  # Destroy the signup window


# Function to show/hide password
def toggle_password_visibility():
    """Toggles the visibility of the password in the entry fields."""
    if show_password_var.get():
        password_entry.configure(show="")
        confirm_password_entry.configure(show="")
    else:
        password_entry.configure(show="*")
        confirm_password_entry.configure(show="*")

def hash_password(password):
    """Hashes the password using SHA256."""
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

def signup(root):
    """Handles the signup process."""
    firstname = firstname_entry.get()
    lastname = lastname_entry.get()
    username = username_entry.get()
    email = email_entry.get()
    password = password_entry.get()
    account_type = role_optionmenu.get()

    if not firstname or not lastname or not username or not email or not password or account_type == "Select":
        tk.messagebox.showerror("Error", "Please fill in all fields and select an account type.")
        return

    hashed_password = hash_password(password)

    if account_type == "Client":
        try:
            mydb = SQLconnection.conn  # Access the connection object
            mycursor = mydb.cursor()  # Get the cursor from the connection
            sql = "INSERT INTO users (firstname, lastname, username, email, password, role) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (firstname, lastname, username, email, hashed_password, "client")
            mycursor.execute(sql, val)
            mydb.commit()  # Use mydb (the connection object) to commit
            tk.messagebox.showinfo("Success", "Client account created successfully!")
            openlogin(root)  # Open login window and destroy signup window
        except mysql.connector.Error as err:
            tk.messagebox.showerror("Error", f"Database error: {err}")
            if hasattr(SQLconnection, 'conn'): # Check if connection exists before rolling back
                SQLconnection.conn.rollback()
        except AttributeError:
            tk.messagebox.showerror("Error", "Database connection not properly initialized")
    elif account_type == "Accountant":
        try:
            mydb = SQLconnection.conn  # Access the connection object
            mycursor = mydb.cursor()  # Get the cursor from the connection
            sql = "INSERT INTO accountant (firstname, lastname, username, email, password, role) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (firstname, lastname, username, email, hashed_password, "accountant")
            mycursor.execute(sql, val)
            mydb.commit()  # Use mydb (the connection object) to commit
            tk.messagebox.showinfo("Success", "Accountant account created successfully!")
            openlogin(root)  # Open login window and destroy signup window
        except mysql.connector.Error as err:
            tk.messagebox.showerror("Error", f"Database error: {err}")
            if hasattr(SQLconnection, 'conn'): # Check if connection exists before rolling back
                SQLconnection.conn.rollback()
        except AttributeError:
            tk.messagebox.showerror("Error", "Database connection not properly initialized")
    else:
        tk.messagebox.showerror("Error", "Please select an account type.")
        
# Initialize the app
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

WINDOW_WIDTH = 940
WINDOW_HEIGHT = 780  # Increased window height
app = ctk.CTk()
app.title("Sign Up")
app.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
app.resizable(False, False)  # Allow resizing

# Load and set background image using Canvas
try:
    bg_image_path = r"images/Final_Signup_image.jpg"
    original_bg_image = Image.open(bg_image_path)
    bg_photo_tk = ImageTk.PhotoImage(original_bg_image)  # Keep original for resizing

    background_canvas = ctk.CTkCanvas(app, highlightthickness=0)
    background_canvas.place(x=0, y=0, relwidth=1, relheight=1)
    bg_image_item = background_canvas.create_image(0, 0, image=bg_photo_tk, anchor="nw")

    def resize_background(event):
        new_width = event.width
        new_height = event.height
        resized_image = original_bg_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        global resized_bg_photo_tk  # Keep a reference to avoid garbage collection
        resized_bg_photo_tk = ImageTk.PhotoImage(resized_image)
        background_canvas.itemconfig(bg_image_item, image=resized_bg_photo_tk)
        background_canvas.config(width=new_width, height=new_height)

    app.bind("<Configure>", resize_background)

except FileNotFoundError:
    print(f"Error: Background image not found at {bg_image_path}")
    app.config(bg="#A6D0FF")  # Fallback background color

# Title - Sign Up
title_label = ctk.CTkLabel(app, text="Sign up", font=("Arial", 36, "bold"), text_color="#000000", bg_color='#a6d1fe')
title_label.place(x=390, y=50)  # Adjusted y

# Already have an account? Sign In (using CTkButton)
signin_button = ctk.CTkButton(app, text="Already have an Account? Sign In", font=("Arial", 14), text_color="#000000", fg_color='#a6d1fe', border_width=0, command=openlogin, cursor="hand2")
signin_button.place(x=350, y=100)  # Adjusted y

# Name
firstname_label = ctk.CTkLabel(app, text="First Name",font=("Arial", 16), text_color="#000000", bg_color='#a6d1fe')
firstname_label.place(x=310, y=140)  # Increased y
firstname_entry = ctk.CTkEntry(app, placeholder_text="First Name",  width=324, height=35, corner_radius=8,
                            fg_color="transparent", border_width=0)
firstname_entry.place(x=310, y=175)  # Slightly adjusted y

lastname_label = ctk.CTkLabel(app, text="Last Name", font=("Arial", 16), text_color="#000000", bg_color='#a6d1fe')
lastname_label.place(x=310, y=210)  # Increased y
lastname_entry=ctk.CTkEntry(app,placeholder_text="Last Name",  width=324, height=35, corner_radius=8,
                            fg_color="transparent", border_width=0)
lastname_entry.place(x=310, y=245)  # Slightly adjusted y

username_label = ctk.CTkLabel(app, text="Username", font=("Arial", 16), text_color="#000000", bg_color='#a6d1fe')
username_label.place(x=310, y=280)  # Increased y
username_entry = ctk.CTkEntry(app, placeholder_text="Username", width=324, height=35, corner_radius=8,
                            fg_color="transparent", border_width=0)
username_entry.place(x=310, y=315)  # Slightly adjusted y

# Email Label
email_label = ctk.CTkLabel(app, text="Email", font=("Arial", 16), text_color="#000000", bg_color='#a6d1fe')
email_label.place(x=310, y=350)  # Increased y

# Email Entry
email_entry = ctk.CTkEntry(app, placeholder_text="Email", width=324, height=35, corner_radius=8,
                            fg_color="transparent", border_width=0)
email_entry.place(x=310, y=385)  # Slightly adjusted y

# Password Label
password_label = ctk.CTkLabel(app, text="Password", font=("Arial", 16), text_color="#000000", bg_color='#a6d1fe')
password_label.place(x=310, y=420)  # Increased y

# Password Entry
password_entry = ctk.CTkEntry(app, placeholder_text="Password", show="*", width=324, height=35, corner_radius=8,
                            fg_color="transparent", border_width=0)
password_entry.place(x=310, y=455)  # Slightly adjusted y

# Confirm Password Label
confirm_password_label = ctk.CTkLabel(app, text="Confirm Password", font=("Arial", 16), text_color="#000000", bg_color='#a6d1fe')
confirm_password_label.place(x=310, y=490)  # Increased y

# Confirm Password Entry
confirm_password_entry = ctk.CTkEntry(app, placeholder_text="Confirm Password", show="*", width=324, height=35, corner_radius=8,
                                    fg_color="transparent", border_width=0)
confirm_password_entry.place(x=310, y=525)  # Slightly adjusted y

# Show Password Checkbox
show_password_var = ctk.BooleanVar()
show_password_checkbox = ctk.CTkCheckBox(app, text="Show Password", variable=show_password_var,
                                    command=toggle_password_visibility, bg_color='#a6d1fe')
show_password_checkbox.place(x=310, y=560)  # Adjusted y

# Role Dropdown (Client / Accountant)
role_label = ctk.CTkLabel(app, text="Select Role", font=("Arial", 16), text_color="#000000", bg_color='#a6d1fe')
role_label.place(x=310, y=590)  # Increased y

role_optionmenu = ctk.CTkOptionMenu(app, values=["Client", "Accountant"], text_color="#000000",
                                    width=324, height=35, fg_color="#FFFFFF",
                                    button_color="#A6D0FF")
role_optionmenu.place(x=310, y=625)  # Slightly adjusted y

# Sign Up Button
signup_button = ctk.CTkButton(app, text="Sign Up", width=324, height=40, corner_radius=8,
                            fg_color="#FFFFFF", hover_color="#A0CAFC", text_color="#000000", command=lambda: signup(app))
signup_button.place(x=310, y=680)  # Adjusted y
app.mainloop()