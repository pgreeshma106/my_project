import customtkinter as ctk
from tkinter import messagebox
import random
import smtplib
from email.mime.text import MIMEText
import subprocess

def resetpassword():
    subprocess.Popen(["python", "confirmpassword.py"])
    
# Store the received OTP and email (will be set when run() is called)
received_otp = None
user_email = None
otp_window = None  # Define otp_window globally within this module
username = None

def run(email=None, otp=None, new_window=False):
    global received_otp, user_email, otp_window
    received_otp = otp
    user_email = email

    if new_window:
        otp_window = ctk.CTkToplevel()
        otp_window.title("OTP Verification")
    else:
        otp_window = ctk.CTk()
        otp_window.title("OTP Verification")

    otp_window.geometry("300x350")
    otp_window.configure(fg_color="#85C3E8")  # Background color

    # Instruction Label
    instruction = ctk.CTkLabel(
        otp_window,
        text=f"An Otp has been sent to you\n({user_email} address) to set\nyour password and it is valid for 10\nminutes.",
        font=ctk.CTkFont(size=16),
        text_color="black",
        justify="left"
    )
    instruction.pack(pady=20)

    # OTP Label
    otp_label = ctk.CTkLabel(otp_window, text="Please enter your otp here", font=ctk.CTkFont(size=16), text_color="black")
    otp_label.pack()

    # OTP Entry with rounded corners
    global otp_entry  # Make otp_entry accessible in other functions
    otp_entry = ctk.CTkEntry(otp_window, width=200, height=30, corner_radius=10, font=ctk.CTkFont(size=16))
    otp_entry.pack(pady=10)

    # Verify Button with rounded corners (renamed from "Next" and moved here)
    verify_button = ctk.CTkButton(otp_window, text="Verify OTP", command=verify_otp, width=200, height=35, corner_radius=10, font=ctk.CTkFont(size=16))
    verify_button.pack(pady=10)

    # Resend OTP Frame
    resend_frame = ctk.CTkFrame(otp_window, fg_color="#85C3E8", corner_radius=0)
    resend_frame.pack(pady=10)

    resend_label = ctk.CTkLabel(resend_frame, text="Didn't receive otp? ", font=ctk.CTkFont(size=16), text_color="black")
    resend_label.pack(side="left")

    # Resend link styled as label with clickable behavior
    resend_link = ctk.CTkLabel(resend_frame, text="click again", font=ctk.CTkFont(size=16, weight="bold"), text_color="black", cursor="hand2")
    resend_link.pack(side="left")
    resend_link.bind("<Button-1>", lambda e: resend_otp())

    if not new_window:
        otp_window.mainloop()

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(recipient_email, otp):
    sender_email = "support@cmich.edu"  
    sender_password = "1234567890"  
    smtp_server = "smtp.cmich.edu"  
    port = 587

    try:
        # Create message object
        msg = MIMEText(f"Your OTP is: {otp}")
        msg['Subject'] = "Your One-Time Password"
        msg['From'] = sender_email
        msg['To'] = recipient_email

        # Connect to the SMTP server
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())

        messagebox.showinfo("OTP", f"OTP sent to {recipient_email}")

    except Exception as e:
        messagebox.showerror("Error Sending OTP", f"Failed to send OTP. Error: {e}")

def verify_otp():
    global received_otp
    entered_otp = otp_entry.get()
    if entered_otp == str(received_otp):
        messagebox.showinfo("Success", "OTP verified successfully!")
        if otp_window:
            otp_window.destroy()
    else:
        messagebox.showerror("Error", "Invalid OTP. Please try again.")

def resend_otp():
    global user_email
    if user_email:
        new_otp = generate_otp()
        send_otp_email(user_email, new_otp)
        global received_otp  # Update the stored OTP
        received_otp = new_otp
        messagebox.showinfo("Resend OTP", f"A new OTP has been sent to {user_email}.")
    else:
        messagebox.showwarning("Error", "No email address available to resend OTP.")

if __name__ == "__main__":
    # This block is for testing otp.py independently (without the main script)
    # You can run this to see the OTP verification window
    run(email="test@example.com", otp="123456")