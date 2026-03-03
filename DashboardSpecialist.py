# This code implements the Specialist Dashboard GUI, which operates on two levels:
# The first level manages the personal information and profile of the specialist.
# The second level, accessible via the "Patients' List" button, allows the specialist to select and manage specific patients associated with them.
# The dashboard provides access to calendar, assistance, notifications, unique codes, and patient management features.
# It also includes a logout button for secure exit.

import customtkinter as ctk
import os
from tkinter import messagebox
from datetime import datetime
from PIL import Image
from customtkinter import CTkImage

from SpecialistCalendar import SpecialistCalendar
from SpecialistProfile import SpecialistProfile
from Assistance import AssistanceWindow
from SpecialistNotifications import SpecialistNotifications
from SpecialistUniqueCode import UniqueCodeWindow
from SpecialistPatientList import SpecialistPatientList
from ContactPatient import ContactPatient

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")

class SpecialistDashboard(ctk.CTkToplevel):
    def __init__(self, parent, user_id, role, full_name):
        super().__init__()
        self.title("Specialist Dashboard")
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
        header_frame.pack(fill="x", anchor="w", pady=(0, 10))

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

        # Logout button
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

        # Label showing specialist's role and full name
        self.role_label = ctk.CTkLabel(
            self,
            text=f"{self.role}: {self.full_name}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1B5E20")
        self.role_label.pack(pady=(10, 20))

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(expand=False, pady=(20, 40))
        
        button_style = {
            "width": 160,
            "height": 100,
            "corner_radius": 15,
            "font": ctk.CTkFont(size=16),
            "fg_color": "#388E3C",
            "hover_color": "#2E7D32"
        }

        # First, create the Patients' List button on its own row
        patient_list_btn = ctk.CTkButton(
            button_frame,
            text="Patients' List",
            command=self.open_patient_list,
            width= 160,
            height= 100,
            corner_radius= 15,
            font= ctk.CTkFont(size=16),
            fg_color= "#26A69A",
            hover_color= "#00897B"
        )
        patient_list_btn.grid(row=0, column=0, columnspan=2, padx=20, pady=15, sticky="ew")

        # Remaining buttons (except Patients' List)
        buttons = [
            ("Calendar", self.open_specialist_calendar),
            ("Profile", self.open_specialist_profile),
            ("Assistance", self.open_assistance),
            ("Notifications", self.open_specialist_notifications),
            ("Unique Code", self.open_specialist_uniquecode)
        ]

        for i, (text, cmd) in enumerate(buttons):
            row = (i // 2) + 1  # rows start at 1 because row 0 is taken by Patients' List
            col = i % 2

            # Last button (uneven number of buttons) centered across two columns
            if i == len(buttons) - 1 and len(buttons) % 2 != 0:
                btn = ctk.CTkButton(button_frame, text=text, command=cmd, **button_style)
                btn.grid(row=row, column=0, columnspan=2, padx=20, pady=15)
            else:
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
    # ensuring only one instance is open and managing focus properly.

    def open_patient_list(self):
        """Open the patients' list window as a modal dialog."""
        self.withdraw()
        self.patient_list_window = SpecialistPatientList(self, self.user_id)
        self.patient_list_window.protocol("WM_DELETE_WINDOW", self.deiconify)

    def open_specialist_calendar(self, id_visit=None):
        """Open the specialist calendar window as a modal dialog."""
        self.withdraw()
        self.patient_list_window = SpecialistCalendar(self, self.user_id, self.role, self.full_name, id_visit=id_visit)
        self.patient_list_window.protocol("WM_DELETE_WINDOW", self.deiconify)
   
    def open_specialist_profile(self):
        """Open the specialist profile window as a modal dialog."""
        self.withdraw()
        self.role_window = SpecialistProfile(self, self.user_id, self.role, self.full_name, on_profile_update=self.update_profile_info)
        self.role_window.protocol("WM_DELETE_WINDOW", self.deiconify)
        
    def update_profile_info(self, new_full_name=None, new_role=None):
        """Update the displayed profile information dynamically."""
        if new_full_name:
            self.full_name = new_full_name
        if new_role:
            self.role = new_role
        self.role_label.configure(text=f"{self.role}: {self.full_name}")

    def open_assistance(self):
        """Open the assistance window as a modal dialog."""
        self.withdraw()
        self.role_window = AssistanceWindow(self, self.user_id)
        self.role_window.protocol("WM_DELETE_WINDOW", self.deiconify)

    def open_specialist_notifications(self):
        """Open the notifications window as a modal dialog."""
        self.withdraw()
        self.notifications_window = SpecialistNotifications(self, self.user_id)
        self.notifications_window.protocol("WM_DELETE_WINDOW", self.deiconify)
    
    def open_specialist_uniquecode(self):
        """Open the unique code window as a modal dialog."""
        self.withdraw()
        self.patient_list_window = UniqueCodeWindow(self, self.user_id)
        self.patient_list_window.protocol("WM_DELETE_WINDOW", self.deiconify)

    def open_contact_patient(self):
        """Open the contact patient window as a modal dialog."""
        self.withdraw()
        self.contact_window = ContactPatient(self, self.user_id, self.role, self.full_name)
        self.contact_window.protocol("WM_DELETE_WINDOW", self.deiconify)

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