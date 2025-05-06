import customtkinter as ctk
from tkinter import messagebox
import random
import otp  # Import the otp.py script

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class HelpSupportForm(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Help & Support")
        self.geometry("450x550")  # Increased height to accommodate new widgets
        self.resizable(False, False)
        self.generated_otp = None
        self.user_email = None

        self.create_widgets()

    def generate_otp(self):
        """Generates a 6-digit random OTP."""
        return str(random.randint(100000, 999999))

    def initiate_otp_verification(self):
        self.user_email = self.email_entry.get().strip()
        if not self.user_email:
            messagebox.showwarning("Input Error", "Please enter your email address.")
            return

        self.generated_otp = self.generate_otp()
        otp.send_otp_email(self.user_email, self.generated_otp)
        otp.run(email=self.user_email, otp=self.generated_otp, new_window=True)

    def create_widgets(self):
        # Main Container
        container = ctk.CTkFrame(self, fg_color="#89CFF0", corner_radius=10)
        container.pack(expand=True, fill="both", padx=20, pady=20)

        # Header
        ctk.CTkLabel(container, text="Help & Support",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 5))

        ctk.CTkLabel(container,
                     text="If you are facing any issues. Please let us\n"
                          "know. We will try to solve them as soon as\n"
                          "possible.",
                     justify="center").pack(pady=(0, 15))

        # Email Label and Entry
        ctk.CTkLabel(container, text="Email", anchor="w").pack(padx=55, anchor="w")
        self.email_entry = ctk.CTkEntry(container, placeholder_text="Your email address", width=300)
        self.email_entry.pack(padx=20, pady=(5, 15))

        # Title Label and Entry
        ctk.CTkLabel(container, text="Title", anchor="w").pack(padx=55, anchor="w")
        self.title_entry = ctk.CTkEntry(container, placeholder_text="Your issue title here", width=300)
        self.title_entry.pack(padx=20, pady=(5, 15))

        # Description Label and Entry
        ctk.CTkLabel(container, text="Explain the issue", anchor="w").pack(padx=55, anchor="w")
        self.desc_box = ctk.CTkTextbox(container, height=100, width=300, corner_radius=10)
        self.desc_box.insert("0.0", "Type your query here")
        self.desc_box.pack(padx=20, pady=(5, 20))

        # Submit Button
        self.submit_btn = ctk.CTkButton(container, text="Submit", width=300, command=self.submit, corner_radius=10)
        self.submit_btn.pack(pady=(0, 10))

        # OTP Verification Button
        #self.otp_button = ctk.CTkButton(container, text="Verify Email via OTP", width=300, command=self.initiate_otp_verification, corner_radius=10)
        #self.otp_button.pack(pady=(5, 20))

        # Footer Contact Info
        ctk.CTkLabel(container,
                     text="You can contact us on this number: 1234567890 ",
                     font=ctk.CTkFont(size=12)).pack(pady=(5, 20))
        #ctk.CTkLabel(container,
                    # text="",
                     #font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(5, 20))

    def submit(self):
        title = self.title_entry.get().strip()
        desc = self.desc_box.get("1.0", "end").strip()

        if not title or not desc or desc == "Type your query here":
            messagebox.showwarning("Missing Info", "Please fill in both title and issue.")
        else:
            messagebox.showinfo("Submitted", "Thank you for your feedback!\nWe'll get back to you soon.")
            self.title_entry.delete(0, "end")
            self.desc_box.delete("1.0", "end")
            self.desc_box.insert("0.0", "Type your query here")


def run():
    app = HelpSupportForm()
    app.mainloop()

if __name__ == "__main__":
    run()