# This module implements the UniqueCodeWindow class.
# It allows a specialist to generate a unique code and assign it to a patient by entering their email.
# When the patient registers, the unique code they provide will be matched against this code to confirm the association.

import customtkinter as ctk
import sqlite3
import os
import random
from datetime import datetime
from PIL import Image
from customtkinter import CTkImage

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")

# Window for specialists to generate and assign a unique code to a patient.
# The specialist inputs the patient's email to associate with the generated code.

class UniqueCodeWindow(ctk.CTkToplevel):
    def __init__(self, parent, specialist_id):
        super().__init__()
        self.title("Create Unique Code")
        self.geometry("400x350")
        self.configure(fg_color="#E8F5E9")
        self.parent = parent
        self.specialist_id = specialist_id
        self.state('zoomed')
        self.attributes('-topmost', True)
        self.grab_set()  # Make this window modal to block interaction with parent

        # Generate a random 6-digit unique code
        self.code = random.randint(100000, 999999)

        # Main container frame
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", padx=20, pady=(10, 10))

        # Header frame with logo and title
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x")

        logo_image = Image.open(LOGO_PATH).resize((80, 80), Image.LANCZOS)
        logo = CTkImage(light_image=logo_image, size=(80, 80))
        logo_label = ctk.CTkLabel(header_frame, image=logo, text="")
        logo_label.pack(side="left")

        title_label = ctk.CTkLabel(
            header_frame,
            text="BREATHE",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#1B5E20")
        title_label.pack(side="left", padx=(100, 0))

        # Label showing the generated unique code
        code_title_label = ctk.CTkLabel(self, text="Generated Unique Code", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1B5E20")
        code_title_label.pack(pady=(30, 10))

        self.code_label = ctk.CTkLabel(self, text=str(self.code), font=ctk.CTkFont(size=32), text_color="#1B5E20")
        self.code_label.pack(pady=10)

        # Entry for patient email input
        self.email_entry = ctk.CTkEntry(self, placeholder_text="Patient Email", width=250)
        self.email_entry.pack(pady=10)

        # Label for confirmation or error messages
        self.confirmation_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=14))
        self.confirmation_label.pack(pady=(5, 10))

        # Button frame for Save and Exit buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)

        save_btn = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save_code,
            fg_color="#388E3C",
            hover_color="#2E7D32",
            width=120,
            height=40
        )
        save_btn.grid(row=0, column=0, padx=10)

        exit_btn = ctk.CTkButton(
            button_frame,
            text="← Exit",
            command=self.close_window,
            fg_color="#A5D6A7", hover_color="#81C784",
            width=120,
            height=40
        )
        exit_btn.grid(row=0, column=1, padx=10)

        # Ensure parent window is maximized and visible
        self.parent.after(0, lambda: self.parent.state('zoomed'))

        # Timestamp label bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second with current date and time."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 

    def save_code(self):
        """Save the generated unique code and associate it with the patient's email in the database.
        Validates email input and checks for existing codes before insertion."""
        email = self.email_entry.get().strip()

        if not email:
            self.confirmation_label.configure(text="Please enter patient email.", text_color="red")
            return

        try:
            conn = sqlite3.connect("DBproject.db")
            c = conn.cursor()

            # Check if the email already has an associated unique code
            c.execute("""
                SELECT UniqueCode FROM AssociationUniqueCode WHERE Email = ?
            """, (email,))
            existing = c.fetchone()

            if existing:
                self.confirmation_label.configure(
                    text="This email already has an associated code.",
                    text_color="red"
                )
                conn.close()
                return

            # Insert the unique code and email association
            c.execute("""
                INSERT INTO AssociationUniqueCode (UniqueCode, Email, ID_Specialist)
                VALUES (?, ?, ?)
            """, (self.code, email, self.specialist_id))

            # Attempt to update WaitingConfirmation table if email exists (non-blocking if not found)
            c.execute("""
                UPDATE WaitingConfirmation
                SET UniqueCode = ?
                WHERE Email = ?
            """, (self.code, email))

            conn.commit()
            conn.close()

            self.confirmation_label.configure(
                text=f"Code {self.code} saved for {email}.",
                text_color="green"
            )

        except sqlite3.IntegrityError:
            self.confirmation_label.configure(
                text="Code or email already exists or is not valid.",
                text_color="red"
            )
        except Exception as e:
            self.confirmation_label.configure(
                text=f"Code not saved. Please retry.\n{str(e)}",
                text_color="red"
            )

    def close_window(self):
        """Close this window and restore the parent window."""
        self.grab_release()
        self.destroy()
        if self.parent:
            self.parent.deiconify()
            self.parent.state('zoomed')