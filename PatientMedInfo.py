# This code implements the Medical Notes section where patients can view a list of their personal notes.
# From this section, patients can also access a questionnaires area and create new notes.
# The notes are retrieved from a SQLite database, can be deleted, and the UI updates accordingly.

import customtkinter as ctk
import sqlite3
import os
from datetime import datetime
from PIL import Image
from customtkinter import CTkImage

from PatientQuestionnaire import QuestionnaireWindow
from PatientNote import UploadNotes

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")

class PatientMedInfo(ctk.CTkToplevel):
    def __init__(self, parent, user_id):
        super().__init__()
        # Initialize the Medical Information window
        self.parent = parent
        self.user_id = user_id
        self.title("Medical Information")
        self.geometry("800x600")
        self.configure(fg_color="#E8F5E9")
        self.state('zoomed')

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

        # Create UI widgets and load notes
        self.create_widgets()
        self.load_notes()

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
        # Title label for Medical Information section
        title_label = ctk.CTkLabel(self, text="Medical Information", font=ctk.CTkFont(size=32, weight="bold"), text_color="#1B5E20")
        title_label.pack(pady=30)

        # Scrollable frame to hold medical notes
        self.notes_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.notes_frame.pack(padx=30, pady=10, fill="both", expand=True)

        # Frame for buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)

        # Button style dictionary for consistency
        self.button_style = {
            "fg_color": "#388E3C",
            "hover_color": "#2E7D32",
            "text_color": "white",
            "font": ctk.CTkFont(size=14),
            "width": 160,
            "height": 40
        }

        # Buttons for questionnaires, new notes, and exit
        ctk.CTkButton(button_frame, text="Questionnaires", command=self.open_questionnaires, **self.button_style).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="New Notes", command=self.open_new_notes, **self.button_style).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="← Exit", command=self.exit_to_dashboard,
                      fg_color="#A5D6A7", hover_color="#81C784", text_color="white",
                      font=ctk.CTkFont(size=14), width=160, height=40).pack(side="left", padx=10)

    def load_notes(self):
        """Load medical notes from the database and display them."""
        conn = sqlite3.connect("DBproject.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT CompilationDate, CompilationTime, Title, Body 
            FROM Note 
            WHERE ID_Person = ? 
            ORDER BY CompilationDate DESC, CompilationTime DESC
        """, (self.user_id,))
        notes = cursor.fetchall()
        conn.close()

        # Clear existing displayed notes
        for widget in self.notes_frame.winfo_children():
            widget.destroy()

        # If no notes found, display a message
        if not notes:
            ctk.CTkLabel(self.notes_frame, text="No medical notes found.", font=ctk.CTkFont(size=16), text_color="gray").pack(pady=20)
        else:
            # Display each note in a card-like frame
            for note in notes:
                date, time, title, body = note

                card = ctk.CTkFrame(self.notes_frame, fg_color="white", corner_radius=10)
                card.pack(fill="x", padx=10, pady=8)

                header_frame = ctk.CTkFrame(card, fg_color="transparent")
                header_frame.pack(fill="x", padx=10, pady=5)

                # Date and time label
                date_label = ctk.CTkLabel(
                    header_frame,
                    text=f"{date} {time}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#388E3C",
                )
                date_label.grid(row=0, column=0, sticky="w")

                # Title label
                title_label = ctk.CTkLabel(
                    header_frame,
                    text=title,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="#1B5E20"
                )
                title_label.grid(row=0, column=1, sticky="w", padx=15)

                # Trash icon label for deleting note
                trash_label = ctk.CTkLabel(header_frame, text="🗑️", font=ctk.CTkFont(size=30))
                trash_label.grid(row=0, column=2, sticky="nse", padx=(10, 0), pady=5)
                trash_label.configure(cursor="hand2")
                # Bind left-click event to delete_note method with date and time parameters
                trash_label.bind("<Button-1>", lambda e, d=date, t=time: self.delete_note(d, t))

                header_frame.grid_columnconfigure(1, weight=1)

                # Body text label with wrapping
                ctk.CTkLabel(
                    card,
                    text=body,
                    font=ctk.CTkFont(size=13),
                    justify="left",
                    wraplength=700,
                    text_color="#2E7D32"
                ).pack(padx=10, pady=5, anchor="w")

    def delete_note(self, date, time):
        """Delete a medical note from the database."""
        try:
            conn = sqlite3.connect("DBproject.db")
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM Note 
                WHERE ID_Person = ? AND CompilationDate = ? AND CompilationTime = ?
            """, (self.user_id, date, time))
            conn.commit()

            # Check if any row was deleted
            if cursor.rowcount == 0:
                from tkinter import messagebox as mb
                mb.showwarning("Warning", "Note not found in database. Please check the date and time.")
            else:
                # Reload notes after deletion
                self.load_notes()

            conn.close()
        except Exception as e:
            from tkinter import messagebox as mb
            mb.showerror("Error", f"Error during deletion: {e}")

    def open_questionnaires(self):
        """Open the questionnaires window modally and hide this window."""
        self.withdraw()
        questionnaire_window = QuestionnaireWindow(self, self.user_id)
        questionnaire_window.grab_set()
        questionnaire_window.protocol("WM_DELETE_WINDOW", self.deiconify)

    def open_new_notes(self):
        """Open the new notes upload window modally and hide this window."""
        self.withdraw()
        notes_window = UploadNotes(self, self.user_id)
        notes_window.grab_set()
        notes_window.protocol("WM_DELETE_WINDOW", self.deiconify)

    def exit_to_dashboard(self):
        """Close this window and restore the parent dashboard."""
        self.destroy()
        if self.parent:
            self.parent.deiconify()
            self.parent.after(0, lambda: self.parent.state('zoomed'))