import customtkinter as ctk
from tkinter import messagebox
import SQLconnection  # Assuming this module handles database connections
import hashlib
import mysql.connector
import sys  # Import the sys module to access command-line arguments


username = None
role = None

def hash_password(password):
    """Hashes the password using SHA256."""
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password


current_username = username
current_role = role

# Set appearance mode and theme
ctk.set_appearance_mode("light")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

# Function to validate and reset password
def reset_password():
    global current_username, current_role  # Ensure we are using the updated global variables
    new_pass = new_password.get()
    confirm_pass = confirm_password.get()

    if not new_pass or not confirm_pass:
        messagebox.showwarning("Warning", "Please fill in both fields.")
    elif new_pass != confirm_pass:
        messagebox.showerror("Error", "Passwords do not match.")
    elif not current_username or not current_role:
        messagebox.showerror("Error", "Username or role not set. Cannot reset password.")
    else:
        hashed_new_password = hash_password(new_pass)

        try:
            conn = SQLconnection.conn()
            cursor = SQLconnection.cursor()

            if current_role == "user":
                query = "UPDATE users SET password = %s WHERE username = %s"
                cursor.execute(query, (hashed_new_password, current_username))
                conn.commit()
                messagebox.showinfo("Success", "User password has been reset successfully!")
            elif current_role == "accountant":
                query = "UPDATE accountant SET password = %s WHERE username = %s"
                cursor.execute(query, (hashed_new_password, current_username))
                conn.commit()
                messagebox.showinfo("Success", "Accountant password has been reset successfully!")
            else:
                messagebox.showerror("Error", "Invalid user role.")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error updating password: {err}")
        finally:
            if SQLconnection.conn and SQLconnection.conn.is_connected():
                SQLconnection.cursor.close()
                SQLconnection.conn.close()

# Create main window
root = ctk.CTk()
root.title("Confirm Password")
root.geometry("300x300")
# noinspection SpellCheckingInspection
root.configure(fg_color="#87CEEB")  # Light sky blue background

# Heading
label_title = ctk.CTkLabel(root, text="You can make your own\npassword here!",
                            text_color="black", font=("Times new roman", 16), pady=10)
label_title.pack()

# New password label and entry
new_label = ctk.CTkLabel(root, text="Enter new password", text_color="black", font=("Times new roman", 16))
new_label.pack(pady=(10, 0))

new_password = ctk.CTkEntry(root, show="*", width=200, corner_radius=10)
new_password.pack()

# Confirm password label and entry
confirm_label = ctk.CTkLabel(root, text="Confirm new password", text_color="black", font=("Times new roman", 16))
confirm_label.pack(pady=(10, 0))

confirm_password = ctk.CTkEntry(root, show="*", width=200, corner_radius=10)
confirm_password.pack()

# Reset button
reset_btn = ctk.CTkButton(root, text="Reset", width=150, corner_radius=20, command=reset_password)
reset_btn.pack(pady=20)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        current_username = sys.argv[1]
        current_role = sys.argv[2]
    else:
        messagebox.showerror("Error", "Username and role must be provided as command-line arguments.")
        sys.exit()

    # Run the app
    root.mainloop()