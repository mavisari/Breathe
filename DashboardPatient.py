# This code implements the Patient Dashboard GUI, which serves as the main hub for patients to access various features of the application.
# Through the dashboard, patients can navigate to different functionalities such as device management, profile editing, calendar, assistance,
# notifications, and more. The dashboard also provides a logout button to exit the application securely.

import customtkinter as ctk
import os
from tkinter import messagebox
from datetime import datetime
from PIL import Image
from customtkinter import CTkImage

from PatientDevice import NewDevicePrompt
from PatientProfile import PatientProfile
from PatientCalendar import PatientCalendar
from Assistance import AssistanceWindow
from ContactSpecialist import ContactSpecialist
from PatientNotifications import PatientNotifications
from PatientMedInfo import PatientMedInfo
from PatientSleepAnalysis import SleepAnalysisWindow

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")

class PatientDashboard(ctk.CTkToplevel):
    def __init__(self, parent, user_id, role, full_name):
        super().__init__()
        self.title("Patient Dashboard")
        self.geometry("800x600")
        self.configure(fg_color="#E8F5E9")
        self.parent = parent
        self.user_id = user_id
        self.role = role
        self.full_name = full_name
        self.state('zoomed')

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

        # Logout button on the top right
        logout_btn = ctk.CTkButton(
            header_frame,
            text="Logout →",
            width=100,
            height=35,
            font=ctk.CTkFont(size=14),
            fg_color="#A5D6A7",
            hover_color="#81C784",
            text_color="black",
            command=self.logout)
        logout_btn.pack(side="right")

        # Display user's role and full name below header
        self.role_label = ctk.CTkLabel(
            self,
            text=f"{self.role}: {self.full_name}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1B5E20")
        self.role_label.pack(pady=(10, 20))

        # Frame for dashboard buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(expand=True)

        button_style = {
            "width": 160,
            "height": 100,
            "corner_radius": 15,
            "font": ctk.CTkFont(size=16),
            "fg_color": "#388E3C",
            "hover_color": "#2E7D32"}

        # List of buttons with their labels and commands
        buttons = [
            ("New Device", self.open_patient_device),
            ("Profile", self.open_patient_profile),
            ("Calendar", self.open_patient_calendar),
            ("Assistance", self.open_assistance),
            ("Contact Specialist", self.open_contact_specialist),
            ("Notifications", self.open_patient_notifications),
            ("Medical Information", self.open_patient_medinfo),
            ("Sleep Analysis", self.open_sleep_analysis)
        ]

        # Arrange buttons in a grid (2 columns)
        for i, (text, cmd) in enumerate(buttons):
            row = i // 2
            col = i % 2
            btn = ctk.CTkButton(button_frame, text=text, command=cmd, **button_style)
            btn.grid(row=row, column=col, padx=20, pady=15)

        # Timestamp label at bottom-right corner, updated every second
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 
    
    # The following methods open the respective windows as modal dialogs,
    # hiding the dashboard window and restoring it when the child window closes.

    def open_patient_device(self):
        self.withdraw()
        self.role_window = NewDevicePrompt(self, self.user_id)
        self.role_window.grab_set()
        self.role_window.protocol("WM_DELETE_WINDOW", self.on_child_close)

    def open_patient_profile(self):
        self.withdraw()
        self.role_window = PatientProfile(self, self.user_id, self.role, self.full_name, on_profile_update=self.update_profile_info)
        self.role_window.grab_set()
        self.role_window.protocol("WM_DELETE_WINDOW", self.on_child_close)

    def open_patient_calendar(self):
        self.withdraw()
        self.role_window = PatientCalendar(self, self.user_id, self.role, self.full_name)
        self.role_window.grab_set()
        self.role_window.protocol("WM_DELETE_WINDOW", self.on_child_close)
    
    def open_assistance(self):
        self.withdraw()
        self.role_window = AssistanceWindow(self, self.user_id)
        self.role_window.grab_set()
        self.role_window.protocol("WM_DELETE_WINDOW", self.on_child_close)

    def open_contact_specialist(self):
        self.withdraw()
        self.role_window = ContactSpecialist(self, self.user_id)
        self.role_window.grab_set()
        self.role_window.protocol("WM_DELETE_WINDOW", self.on_child_close)

    def open_patient_notifications(self):
        self.withdraw()
        self.role_window = PatientNotifications(self, self.user_id, self.role, self.full_name)
        self.role_window.grab_set()
        self.role_window.protocol("WM_DELETE_WINDOW", self.on_child_close)

    def open_patient_medinfo(self):
        self.withdraw()
        self.role_window = PatientMedInfo(self, self.user_id)
        self.role_window.grab_set()
        self.role_window.protocol("WM_DELETE_WINDOW", self.on_child_close)
    
    def open_sleep_analysis(self):
        self.withdraw()
        self.role_window = SleepAnalysisWindow(self, self.user_id)
        self.role_window.grab_set()
        self.role_window.protocol("WM_DELETE_WINDOW", self.on_child_close)

    def open_patient_contact(self):
        self.withdraw()
        self.contact_window = ContactSpecialist(self, self.user_id, self.role, self.full_name)
        self.contact_window.grab_set()
        self.contact_window.protocol("WM_DELETE_WINDOW", self.on_child_close)
    
    def logout(self):
        """Confirm logout and close dashboard, restoring parent window."""
        confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if confirm:
            self.destroy()

            def show_main_zoomed():
                 self.parent.deiconify()
                 self.parent.lift()
                 self.parent.focus_force()
                 self.parent.state('zoomed')

            self.parent.after(100, show_main_zoomed)

    def update_profile_info(self, new_full_name=None, new_role=None):
        """Update the displayed profile information on the dashboard."""
        if new_full_name:
            self.full_name = new_full_name
        if new_role:
            self.role = new_role
        self.role_label.configure(text=f"{self.role}: {self.full_name}")

    def on_child_close(self):
        """Restore the dashboard window when a child window is closed."""
        if hasattr(self, 'role_window') and self.role_window.winfo_exists():
            self.role_window.destroy()
        if hasattr(self, 'contact_window') and self.contact_window.winfo_exists():
            self.contact_window.destroy()
        self.deiconify()
        self.lift()