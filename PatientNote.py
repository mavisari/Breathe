# This code implements the page connected to Medical Information for creating a new personal note.
# The created note will be saved in the database and shown in the updated list on the previous Medical Information page.

import customtkinter as ctk
import sqlite3
import os
from datetime import datetime
from PIL import Image
from customtkinter import CTkImage

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")

class UploadNotes(ctk.CTkToplevel):
    def __init__(self, parent, user_id):
        super().__init__()
        # Initialize the Upload Notes window
        self.parent = parent
        self.user_id = user_id
        self.title("Upload Notes")
        self.geometry("800x600")
        self.configure(fg_color="#E8F5E9")
        self.state('zoomed')
        self.attributes('-topmost', True)
        self.grab_set()  # Make this window modal to block interaction with parent

        # Main container frame
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", padx=20, pady=(10, 10))

        # Header frame with logo and title
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x")

        # Load and display logo image
        logo_image = Image.open(LOGO_PATH).resize((80, 80), Image.LANCZOS)
        logo = CTkImage(light_image=logo_image, size=(80, 80))
        logo_label = ctk.CTkLabel(header_frame, image=logo, text="")
        logo_label.pack(side="left")

        # Title label "BREATHE"
        title_label = ctk.CTkLabel(
            header_frame,
            text="BREATHE",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#1B5E20")
        title_label.pack(side="left", padx=(100, 0))

        # Create UI widgets for note input and buttons
        self.create_widgets()

        # Timestamp label at bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 

    def create_widgets(self):
        # Title label for new medical note
        title_label = ctk.CTkLabel(self, text="New Medical Note", font=ctk.CTkFont(size=32, weight="bold"), text_color="#1B5E20")
        title_label.pack(pady=30)

        # Textbox for note input
        self.text_box = ctk.CTkTextbox(self, width=700, height=300, corner_radius=10)
        self.text_box.pack(padx=30, pady=10)

        # Status message label to show errors or success
        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=14))
        self.status_label.pack(pady=10)

        # Frame for buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)

        # Confirm button to save note
        self.confirm_btn = ctk.CTkButton(button_frame, text="Confirm Notes", command=self.confirm_notes,
                                         fg_color="#388E3C", hover_color="#2E7D32", text_color="white",
                                         width=160, height=40, font=ctk.CTkFont(size=14))
        self.confirm_btn.pack(side="left", padx=10)

        # Cancel button to go back without saving
        self.cancel_btn = ctk.CTkButton(button_frame, text="← Go Back", command=self.cancel_notes,
                                        fg_color="#A5D6A7", hover_color="#81C784", text_color="white",
                                        width=160, height=40, font=ctk.CTkFont(size=14))
        self.cancel_btn.pack(side="left", padx=10)

    def confirm_notes(self):
        """Save the note text in the database and notify the user."""
        note_text = self.text_box.get("1.0", "end").strip()

        # Check if note text is empty
        if not note_text:
            self.status_label.configure(text="Please enter the note text before confirming.", text_color="red")
            return

        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")

        try:
            conn = sqlite3.connect("DBproject.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Note (ID_Person, Title, Body, CompilationDate, CompilationTime)
                VALUES (?, ?, ?, ?, ?)
            """, (self.user_id, "Patient note", note_text, date, time))
            conn.commit()
            conn.close()

            self.status_label.configure(text="Data successfully saved", text_color="green")
            # Close window after short delay to show success message
            self.after(1500, self.close_and_return)

        except Exception as e:
            self.status_label.configure(text="Error: note not saved. Retry", text_color="red")

    def cancel_notes(self):
        """Cancel note creation and return to previous window."""
        self.close_and_return()

    def close_and_return(self):
        """Close this window and restore the parent window, refreshing notes list."""
        self.grab_release()
        self.destroy()
        self.parent.after(0, lambda: self.parent.state('zoomed'))

        if self.parent:
            self.parent.deiconify()
            # Refresh notes list in parent window
            self.parent.load_notes()
            self.parent.after(0, lambda: self.parent.state('zoomed'))