# This code implements a GUI window that allows specialists to input and book a new visit by entering date, time, location, and visit type.
# It validates the inputs, saves the visit information in a database, and creates a notification for the patient.

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

def generate_custom_id(prefix, number):
    """Generate a custom ID with a prefix and zero-padded number."""
    return f"{prefix}{str(number).zfill(4)}"

def get_next_ticket_number(conn):
    """Get the next sequential visit number from the database."""
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(CAST(SUBSTR(ID_Visit, 3) AS INTEGER)) FROM Visit WHERE ID_Visit LIKE 'V%'")
    max_num = cursor.fetchone()[0]
    return 1 if max_num is None else max_num + 1

class CalendarWindow(ctk.CTkToplevel):
    def __init__(self, parent_visit_window, specialist_id, patient_id):
        super().__init__(parent_visit_window)
        self.visit_window = parent_visit_window
        self.specialist_id = specialist_id
        self.patient_id = patient_id

        # Configure window appearance and layout
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", padx=20, pady=(10, 10))

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

        self.title("Book a New Visit")
        self.configure(fg_color="#E8F5E9")
        self.state('zoomed')

        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.pack(expand=True)

        # Entry fields with placeholders for date, time, location, and visit type
        self.date_entry = ctk.CTkEntry(self.center_frame, placeholder_text="Enter date (YYYY-MM-DD)", width=300)
        self.date_entry.pack(pady=10)
        self.date_entry.bind("<KeyRelease>", self.date_input_mask)

        self.time_entry = ctk.CTkEntry(self.center_frame, placeholder_text="Enter time (HH:MM)", width=300)
        self.time_entry.pack(pady=10)
        self.time_entry.bind("<KeyRelease>", self.time_input_mask)

        self.place_entry = ctk.CTkEntry(self.center_frame, placeholder_text="Enter location", width=300)
        self.place_entry.pack(pady=10)

        self.type_entry = ctk.CTkEntry(self.center_frame, placeholder_text="Enter visit type", width=300)
        self.type_entry.pack(pady=10)

        # Label to show feedback messages (errors or success)
        self.feedback_label = ctk.CTkLabel(self.center_frame, text="", text_color="green")
        self.feedback_label.pack(pady=(5, 5))

        # Confirm button to save visit
        self.confirm_button = ctk.CTkButton(
            self.center_frame, text="Confirm Visit", command=self.confirm_visit,
            fg_color="#388E3C", hover_color="#2E7D32"
        )
        self.confirm_button.pack(pady=10)

        # Go back button to close this window and return to the previous one
        self.go_back_button = ctk.CTkButton(
            self.center_frame, text="← Go Back", command=self.go_back,
            fg_color="#A5D6A7", hover_color="#81C784", text_color="white"
        )
        self.go_back_button.pack(pady=5)

        # Timestamp label at bottom-right corner, updated every second
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

        self.attributes('-topmost', True)
        self.grab_set()  # Make this window modal (block interaction with parent)

    def update_timestamp(self):
        """Update the timestamp label every second."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp)

    def date_input_mask(self, event):
        """Automatically format date input as YYYY-MM-DD while typing."""
        raw = ''.join(filter(str.isdigit, self.date_entry.get()))
        new_text = ""
        for i, char in enumerate(raw):
            if i == 4 or i == 6:
                new_text += "-"
            new_text += char
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, new_text[:10])

    def time_input_mask(self, event):
        """Automatically format time input as HH:MM while typing."""
        raw = ''.join(filter(str.isdigit, self.time_entry.get()))
        new_text = ""
        for i, char in enumerate(raw):
            if i == 2:
                new_text += ":"
            new_text += char
        self.time_entry.delete(0, "end")
        self.time_entry.insert(0, new_text[:5])

    def confirm_visit(self):
        """Validate inputs and save the new visit and notification to the database."""
        raw_date = self.date_entry.get().strip()
        raw_time = self.time_entry.get().strip()
        place = self.place_entry.get().strip()
        vtype = self.type_entry.get().strip()

        # Check for empty fields
        if not raw_date or not raw_time or not place or not vtype:
            self.feedback_label.configure(text="Please enter date, time, location and type.", text_color="red")
            return

        # Validate date format
        try:
            date = datetime.strptime(raw_date, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            self.feedback_label.configure(text="Invalid date format. Use YYYY-MM-DD.", text_color="red")
            return

        # Validate datetime and ensure visit is not in the past
        try:
            visit_datetime = datetime.strptime(f"{raw_date} {raw_time}", "%Y-%m-%d %H:%M")
            now = datetime.now()
            if visit_datetime < now:
                self.feedback_label.configure(text="You cannot book a visit in the past.", text_color="red")
                return
        except ValueError:
            self.feedback_label.configure(text="Invalid date or time format. Use YYYY-MM-DD and HH:MM.", text_color="red")
            return

        # Insert visit and notification into the database
        try:
            conn = sqlite3.connect("DBproject.db")
            cursor = conn.cursor()

            next_number = get_next_ticket_number(conn)
            code = generate_custom_id("V", next_number)

            cursor.execute(
                "INSERT INTO Visit (ID_Visit, ID_Patient, ID_Specialist, VisitDate, VisitTime, Place, Type) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (code, self.patient_id, self.specialist_id, date, raw_time, place, vtype)
            )

            # Insert notification for the patient about the new visit
            ns_version = "v1.0"
            ns_type = "Usual"
            notif_title = "New Visit Scheduled"
            notif_body = f"A new visit has been scheduled for {date} at {raw_time} in {place}."
            compilation_date = datetime.now().strftime("%Y-%m-%d")
            compilation_time = datetime.now().strftime("%H:%M:%S")

            cursor.execute("""
                INSERT INTO Notification 
                (ID_Person, NS_Version, NS_Type, Type, Title, Body, CompilationDate, CompilationTime, IsRead, ID_Visit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
            """, (
                self.patient_id,
                ns_version,
                ns_type,
                "Calendar",  # Recognized as calendar notification in PatientNotifications
                notif_title,
                notif_body,
                compilation_date,
                compilation_time,
                code  # ID_Visit
            ))

            conn.commit()
            conn.close()

            self.feedback_label.configure(text="Visit saved correctly.", text_color="green")

            # Reload visits in parent window if method exists
            if hasattr(self.visit_window, "load_visits") and callable(self.visit_window.load_visits):
                self.visit_window.load_visits()

            # Automatically go back after 2 seconds
            self.after(2000, self.go_back)

        except Exception as e:
            self.feedback_label.configure(text=f"Error: Visit not saved.\n{str(e)}", text_color="red")

    def go_back(self):
        """Close this window and restore the parent visit window."""
        self.destroy()
        if self.visit_window:
            self.visit_window.deiconify()
            self.visit_window.state('zoomed')