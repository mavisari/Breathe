# This module implements the second-level dashboard for the specialist related to the selected patient.
# It provides buttons to access various patient-related functionalities such as manual data entry, prescriptions,
# sleep analysis, contact, visits and EHR.

import customtkinter as ctk
import os
from datetime import datetime
from PIL import Image
from customtkinter import CTkImage

from SpecialistManualData import SpecialistManualData
from SpecialistPrescription import PrescriptionList 
from SpecialistSleepAnalysis import SpecialistSleepAnalysisWindow
from ContactPatient import ContactPatient
from SpecialistVisitWindow import PatientVisitsWindow  
from SpecialistEHR import EHRWindow

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")

# Window representing the patient dashboard for the specialist.
# Displays patient-specific options and allows navigation to related windows.

class RelatedPatientDashboard(ctk.CTkToplevel):
    def __init__(self, parent, specialist_id, patient_id, patient_name):
        super().__init__()
        self.title(f"Patient: {patient_name}")
        self.geometry("600x600")
        self.state('zoomed')
        self.configure(fg_color="#E8F5E9")

        self.parent = parent
        self.specialist_id = specialist_id
        self.patient_id = patient_id
        self.patient_name = patient_name

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

        # Dashboard title label
        ctk.CTkLabel(self, text=f"Patient Dashboard: {patient_name}",
                     font=ctk.CTkFont(size=24, weight="bold"), text_color="#1B5E20").pack(pady=20)

        # Frame for buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(expand=True)

        # Common button style
        button_style = {
            "width": 200,
            "height": 100,
            "corner_radius": 15,
            "font": ctk.CTkFont(size=16),
            "fg_color": "#388E3C",
            "hover_color": "#2E7D32"
        }

        # Buttons and their corresponding commands
        buttons = [
            ("Manual Data", self.open_manualdata),
            ("Prescription", self.open_prescriptions),
            ("Sleep Analysis", self.open_sleep_analysis),
            ("Contact Patient", self.open_contact_patient),
            ("Visit", self.open_visits),
            ("EHR", self.open_ehr),
        ]

        # Arrange buttons in grid: 2 columns
        for i, (text, cmd) in enumerate(buttons):
            row = i // 2
            col = i % 2
            btn = ctk.CTkButton(button_frame, text=text, command=cmd, **button_style)
            btn.grid(row=row, column=col, padx=20, pady=15)

        # Go back button at bottom
        back_button = ctk.CTkButton(self, text="← Go Back", command=self.go_back,
                                    width=100, height=40, fg_color="#A5D6A7",
                                    hover_color="#81C784", text_color="white")
        back_button.pack(pady=20)

        # Timestamp label bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

        self.grab_set()  # Make this window modal to block interaction with parent

    def update_timestamp(self):
        """Update the timestamp label every second with current date and time."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 

    # The following methods open respective windows and hide this dashboard.
    # On closing the child window, this dashboard is restored.

    def open_manualdata(self):
        self.withdraw()
        manualdata = SpecialistManualData(self, self.specialist_id, self.patient_id)
        manualdata.protocol("WM_DELETE_WINDOW", self.deiconify)
    
    def open_prescriptions(self):
        self.withdraw()
        presc_win = PrescriptionList(self, self.specialist_id, self.patient_id)
        presc_win.protocol("WM_DELETE_WINDOW", self.deiconify)
    
    def open_sleep_analysis(self):
        self.withdraw()
        sleep_analysis_window = SpecialistSleepAnalysisWindow(self, self.specialist_id, self.patient_id, self.patient_name)
        sleep_analysis_window.protocol("WM_DELETE_WINDOW", self.deiconify)

    def open_contact_patient(self):
        self.withdraw()
        contact_window = ContactPatient(self, self.specialist_id, self.patient_id, self.patient_name)
        contact_window.protocol("WM_DELETE_WINDOW", self.deiconify)

    def open_contact_patient_with_id(self, patient_id, specialist_id):
        ContactPatient(self, specialist_id, patient_id)
        
    def open_visits(self):
        self.withdraw()
        visits_window = PatientVisitsWindow(self, self.specialist_id, self.patient_id)
        visits_window.protocol("WM_DELETE_WINDOW", self.deiconify)

    def open_ehr(self):
        self.withdraw()
        presc_win = EHRWindow(self)
        presc_win.protocol("WM_DELETE_WINDOW", self.deiconify)
    
    def go_back(self):
        """Close this dashboard window and restore the parent window."""
        self.grab_release()
        self.destroy()
        if self.parent:
            self.parent.deiconify()
            self.parent.after(0, lambda: self.parent.state('zoomed'))