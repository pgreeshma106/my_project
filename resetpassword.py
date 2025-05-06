import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import sys

# Global variables to store email and OTP
generated_otp = None
user_email = None
username= None

def generate_otp():
    """Generates a 6-digit random OTP."""
    return str(random.randint(100000, 999999))

def get_otp():
    global generated_otp, user_email
    user_email = email_entry.get()
    if user_email and user_email != "Enter Email":
        generated_otp = generate_otp()
        messagebox.showinfo("OTP", f"OTP sent to {user_email}. OTP is: {generated_otp}") # In a real application, you would send this via email
        open_otp()
    else:
        messagebox.showwarning("Input Error", "Please enter your email.")

def open_otp():
    import otp
    otp.run(email=user_email, otp=generated_otp, new_window=True)


# Set appearance
ctk.set_appearance_mode("light")  # can be "dark" or "light"
ctk.set_default_color_theme("blue")  # themes: blue, green, dark-blue

# Create main window
root = ctk.CTk()
root.title("Reset Password")
root.geometry("500,600")
root.configure(fg_color="#add8e6")  # Light blue background

# Instruction label
instruction = ctk.CTkLabel(root, text="Reset your password here by confirming email", text_color="black", font=("Times new roman", 18))
instruction.pack(pady=10)

# Load and display image
try:
    bg_image_path = r"images\reset_password_image.jpg"
    bg_image = Image.open(bg_image_path)
    resized_image = bg_image.resize((455, 290), Image.Resampling.LANCZOS)

    # Convert PIL Image to CTkImage
    photo = ctk.CTkImage(light_image=resized_image, dark_image=resized_image, size=(455, 290))

    image_label = ctk.CTkLabel(root, image=photo, text="")
    image_label.pack(pady=10)
except FileNotFoundError:
    print("Error: reset_password_image.jpg not found in the specified path.")

# Email label
email_label = ctk.CTkLabel(root, text="Email", text_color="black",justify="left", font=("Times new roman", 18))
email_label.pack(pady=10)

# Email entry with rounded corners
email_entry = ctk.CTkEntry(root, width=300, height=35, corner_radius=10, placeholder_text="Enter Email")
email_entry.pack(pady=10)

# Get OTP button with rounded corners
otp_button = ctk.CTkButton(root, text="Get Otp", command=get_otp, width=200, height=40, corner_radius=10, fg_color="#87CEFA", text_color="black", hover_color="#00BFFF")
otp_button.pack(pady=20)

root.mainloop()