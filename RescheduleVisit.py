# This module implements the reschedule visit.It allows the specialist, after selecting a specific visit of a patient,
# to modify the visit date and time to reschedule it.

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

# Window for rescheduling a patient visit.
# Allows input of new date and time with validation and updates the database.
# Sends a notification to the patient about the rescheduled visit.

class RescheduleVisitWindow(ctk.CTkToplevel):
    def __init__(self, parent, visit_id, current_date, current_time, on_reschedule_callback, visits_window):
        super().__init__(parent)
        self.parent = parent
        self.visit_id = visit_id
        self.on_reschedule_callback = on_reschedule_callback
        self.visits_window = visits_window

        self.title("Reschedule Visit")
        self.configure(fg_color="#E8F5E9")
        self.state('zoomed')
        self.grab_set()  # Make this window modal to block interaction with parent

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

        # Center frame for input fields and buttons
        self.center = ctk.CTkFrame(self, fg_color="transparent")
        self.center.pack(expand=True, pady=20)

        # Date entry with placeholder and initial value
        self.date_entry = ctk.CTkEntry(self.center, placeholder_text="New date (YYYY-MM-DD)", width=300)
        self.date_entry.insert(0, current_date)
        self.date_entry.pack(pady=5)
        self.date_entry.bind("<KeyRelease>", self.date_input_mask)

        # Time entry with placeholder and initial value
        self.time_entry = ctk.CTkEntry(self.center, placeholder_text="New time (HH:MM)", width=300)
        self.time_entry.insert(0, current_time)
        self.time_entry.pack(pady=5)
        self.time_entry.bind("<KeyRelease>", self.time_input_mask)

        # Feedback label for validation messages
        self.feedback_label = ctk.CTkLabel(self.center, text="")
        self.feedback_label.pack()

        # Confirm button to submit changes
        self.confirm_button = ctk.CTkButton(
            self.center, text="Confirm", command=self.confirm,
            fg_color="#388E3C", hover_color="#2E7D32"
        )
        self.confirm_button.pack(pady=10)

        # Cancel button to close window without changes
        self.cancel_button = ctk.CTkButton(
            self.center, text="Cancel", command=self.cancel,
            fg_color="#A5D6A7", hover_color="#81C784"
        )
        self.cancel_button.pack()

        # Timestamp label bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 

    def date_input_mask(self, event):
        """Format the date entry as YYYY-MM-DD while typing.
        Allows only digits and inserts dashes appropriately."""
        raw = ''.join(filter(str.isdigit, self.date_entry.get()))
        new_text = ""
        for i, char in enumerate(raw):
            if i == 4 or i == 6:
                new_text += "-"
            new_text += char
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, new_text[:10])

    def time_input_mask(self, event):
        """Format the time entry as HH:MM while typing.
        Allows only digits and inserts colon appropriately."""
        raw = ''.join(filter(str.isdigit, self.time_entry.get()))
        new_text = ""
        for i, char in enumerate(raw):
            if i == 2:
                new_text += ":"
            new_text += char
        self.time_entry.delete(0, "end")
        self.time_entry.insert(0, new_text[:5])

    def confirm(self):
        """Validate inputs and update the visit with new date and time.
        Sends notification to the patient about the rescheduling."""
        raw_date = self.date_entry.get().strip()
        raw_time = self.time_entry.get().strip()

        if not raw_date or not raw_time:
            self.feedback_label.configure(text="Please fill both fields", text_color="red")
            return

        # Validate date format YYYY-MM-DD
        try:
            datetime.strptime(raw_date, "%Y-%m-%d")
        except ValueError:
            self.feedback_label.configure(text="Invalid date format. Use YYYY-MM-DD", text_color="red")
            return

        # Validate time format HH:MM (24h)
        try:
            datetime.strptime(raw_time, "%H:%M")
        except ValueError:
            self.feedback_label.configure(text="Invalid time format. Use HH:MM (24h)", text_color="red")
            return

        success = self.update_visit(self.visit_id, raw_date, raw_time)
        if success:
            if self.on_reschedule_callback:
                self.on_reschedule_callback(self.visit_id, raw_date, raw_time)
            self.feedback_label.configure(text="Rescheduled successfully! Returning in 3 seconds...", text_color="green")
            self.after(3000, self.close_window)
        else:
            self.feedback_label.configure(text="Error rescheduling.", text_color="red")

    def update_visit(self, visit_id, new_date, new_time):
        """Update the visit date and time in the database.
        Also creates a notification for the patient about the rescheduling."""
        try:
            conn = sqlite3.connect("DBproject.db")
            cursor = conn.cursor()

            # Retrieve patient ID and visit place for notification
            cursor.execute("SELECT ID_Patient, Place FROM Visit WHERE ID_Visit = ?", (visit_id,))
            result = cursor.fetchone()
            if not result:
                conn.close()
                return False
            patient_id, place = result

            # Update visit date and time
            cursor.execute(
                "UPDATE Visit SET VisitDate = ?, VisitTime = ? WHERE ID_Visit = ?",
                (new_date, new_time, visit_id)
            )

            # Create notification for patient
            ns_version = "v1.0"
            ns_type = "Usual"
            notif_title = "Visit Rescheduled"
            notif_body = f"Your visit has been rescheduled to {new_date} at {new_time} in {place}."
            compilation_date = datetime.now().strftime("%Y-%m-%d")
            compilation_time = datetime.now().strftime("%H:%M:%S")

            cursor.execute("""
                INSERT INTO Notification 
                (ID_Person, NS_Version, NS_Type, Type, Title, Body, CompilationDate, CompilationTime, IsRead, ID_Visit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
            """, (
                patient_id,
                ns_version,
                ns_type,
                "Calendar",
                notif_title,
                notif_body,
                compilation_date,
                compilation_time,
                visit_id
            ))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error updating visit: {e}")
            return False

    def cancel(self):
        """Cancel the rescheduling and close the window."""
        self.close_window()

    def close_window(self):
        """Close this window and restore the visits window."""
        self.grab_release()
        self.destroy()
        if self.visits_window:
            self.visits_window.deiconify()
            self.visits_window.state('zoomed')