# This module implements the password retrieval page, which is accessed from the login screen when the user forgets their password.
# By entering their email, the software generates a new random password and simulates sending it externally via email.
# If the user does not receive the email, they can request to resend it.

import customtkinter as ctk
import sqlite3
import os
import random
import string
from datetime import datetime
from PIL import Image
from customtkinter import CTkImage

DB_PATH = "DBproject.db"

def generate_random_password(length=10):
    """Generate a random alphanumeric password of given length."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Window for password retrieval.
# Allows user to input their email to receive a new randomly generated password.
# Provides option to resend the password email.

class RetrievePassword(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__()
        self.title("Retrieve Password")
        self.geometry("500x400")
        self.configure(fg_color="#E8F5E9")
        self.state('zoomed')
        self.parent = parent
        self.generated_password = None
        self.email_entered = None

        BASE_DIR = os.path.dirname(__file__)
        LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")

        # Header frame with logo and title
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 0))

        logo_image = Image.open(LOGO_PATH).resize((80, 80), Image.LANCZOS)
        logo = CTkImage(light_image=logo_image, size=(80, 80))
        logo_label = ctk.CTkLabel(header_frame, image=logo, text="")
        logo_label.pack(side="left", padx=(0, 10))

        title_label = ctk.CTkLabel(
            header_frame,
            text="BREATHE",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#1B5E20"
        )
        title_label.pack(side="left", padx=(100, 0))
        
        # Container for main content
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(pady=(30, 10))

        # Instruction label
        ctk.CTkLabel(container,
                     text="Retrieve your password",
                     font=ctk.CTkFont(size=28, weight="bold"),
                     text_color="#1B5E20").pack(pady=(20, 10))

        # Email entry field
        self.email_entry = ctk.CTkEntry(container, width=300, height=45, placeholder_text="Enter your email", font=ctk.CTkFont(size=14))
        self.email_entry.pack(pady=10)

        # Notification label for feedback
        self.notification_label = ctk.CTkLabel(container, text="", text_color="red", font=ctk.CTkFont(size=14))
        self.notification_label.pack(pady=10)

        # Button style dictionary
        button_style = {
            "width": 240,
            "height": 45,
            "corner_radius": 12,
            "font": ctk.CTkFont(size=14),
            "fg_color": "#388E3C",
            "hover_color": "#2E7D32",
            "text_color": "white"
        }

        # Send new password button
        ctk.CTkButton(container, text="Send New Password", command=self.send_password, **button_style).pack(pady=10)

        # Resend password button, initially disabled
        self.resend_button = ctk.CTkButton(container, text="Send Again", command=self.resend_password, **button_style)
        self.resend_button.pack(pady=10)
        self.resend_button.configure(state="disabled")

        # Back to login button
        ctk.CTkButton(
            container,
            text="← Back to Login",
            command=self.go_back,
            width=160,
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(size=14, family="Segoe UI"),
            fg_color="#A5D6A7",
            hover_color="#81C784",
            text_color="white"
        ).pack(pady=20)
    
        # Timestamp label bottom-right
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

        self.grab_set()  # Make this window modal to block interaction with parent

    def update_timestamp(self):
        """Update the timestamp label every second with current date and time."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 

    def send_password(self):
        """Generate a new random password and update it in the database for the entered email.
        Simulate sending the new password via email.
        Enable the resend button upon success."""
        email = self.email_entry.get().strip()
        if not email:
            self.notification_label.configure(text="Please enter your email", text_color="red")
            return

        self.generated_password = generate_random_password()
        self.email_entered = email

        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()

            # Check if email exists in the system
            c.execute("SELECT 1 FROM Person WHERE Email = ?", (email,))
            if not c.fetchone():
                self.notification_label.configure(text="Email not found in the system", text_color="red")
                conn.close()
                return

            # Update password in database
            c.execute("UPDATE Person SET Password = ? WHERE Email = ?", (self.generated_password, email))
            conn.commit()
            conn.close()

            # Simulate sending email (print to console)
            print(f"[Email Simulation] New password sent to {email}: {self.generated_password}")
            self.notification_label.configure(text="New password sent via email", text_color="green")
            self.resend_button.configure(state="normal")

        except Exception as e:
            self.notification_label.configure(text=f"Database error: {str(e)}", text_color="red")

    def resend_password(self):
        """Resend the previously generated password to the email."""
        if self.email_entered and self.generated_password:
            print(f"[Email Simulation] Resent new password to {self.email_entered}: {self.generated_password}")
            self.notification_label.configure(text="New email sent", text_color="green")

    def go_back(self):
        """Close this window and restore the login window."""
        self.grab_release()
        self.destroy()
        if self.parent:
            self.parent.deiconify()
            self.parent.after(0, lambda: self.parent.state('zoomed'))