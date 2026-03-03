# This module implements the second-level dashboard for the specialist.
# It displays a list of patients associated with the specialist.
# The specialist can select a patient to view detailed related information.

import customtkinter as ctk
import sqlite3
import os
from datetime import datetime
from PIL import Image
from customtkinter import CTkImage

from RelatedPatient import RelatedPatientDashboard

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")

# Window showing the list of patients associated with the specialist.
# Allows selection of a patient to open the related patient dashboard.

class SpecialistPatientList(ctk.CTkToplevel):
    def __init__(self, parent, specialist_id):
        super().__init__()
        self.title("Patient's List")
        self.geometry("600x500")
        self.state('zoomed')
        self.configure(fg_color="#E8F5E9")
        self.parent = parent
        self.specialist_id = specialist_id
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

        # Title label for patient list
        ctk.CTkLabel(self, text="Patients' List", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1B5E20").pack(pady=20)

        # Scrollable frame to contain patient buttons
        self.list_frame = ctk.CTkScrollableFrame(self, width=500, height=400)
        self.list_frame.pack(pady=10)

        # Exit button to close this window and return to parent
        self.exit_button = ctk.CTkButton(self, text="← Exit", command=self.exit_to_dashboard,
                                         width=100, height=40, fg_color="#A5D6A7",
                                         hover_color="#81C784", text_color="white")
        self.exit_button.pack(pady=20)

        # Load patients associated with the specialist
        self.load_patients()

        # Timestamp label bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second with current date and time."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 

    def load_patients(self):
        """Load the list of patients associated with the specialist from the database.
        Display each patient as a button in the scrollable frame."""
        conn = sqlite3.connect("DBproject.db")
        cursor = conn.cursor()

        query = """
            SELECT p.ID_Person, p.Name, p.Surname
            FROM Person p
            JOIN Patient pt ON p.ID_Person = pt.ID_Patient
            JOIN AssociationUniqueCode auc ON p.Email = auc.Email
            WHERE auc.ID_Specialist = ?
        """

        cursor.execute(query, (self.specialist_id,))
        patients = cursor.fetchall()
        conn.close()

        if not patients:
            ctk.CTkLabel(self.list_frame, text="No patients found.", text_color="red",
                         font=ctk.CTkFont(size=16)).pack(pady=10)
            return

        for pid, name, surname in patients:
            full_name = f"{name} {surname}"
            btn = ctk.CTkButton(self.list_frame, text=full_name,
                                command=lambda pid=pid, fn=full_name: self.open_patient_dashboard(pid, fn),
                                width=400, height=40, fg_color="#388E3C", hover_color="#2E7D32")
            btn.pack(pady=8)

    def open_patient_dashboard(self, patient_id, patient_name):
        """Open the RelatedPatientDashboard window for the selected patient.
        Hide this window while the patient dashboard is open.
        Restore this window when the patient dashboard is closed."""
        self.withdraw()
        self.related_window = RelatedPatientDashboard(self, self.specialist_id, patient_id, patient_name)
        self.related_window.protocol("WM_DELETE_WINDOW", self.deiconify)
        self.related_window.grab_set()  # Modal behavior

    def exit_to_dashboard(self):
        """Close this window and restore the parent specialist dashboard window."""
        self.grab_release()
        self.destroy()
        if self.parent:
            self.parent.deiconify()
            self.parent.after(0, lambda:self.parent.state('zoomed'))