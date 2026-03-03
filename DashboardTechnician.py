# This code implements the Technician Dashboard GUI, which serves as the main control panel for technicians to access various application features.
# Through this dashboard, technicians can manage their profile, confirm pending profiles, handle tickets, and manage backups.
# The dashboard also includes a logout button to securely exit the application.

import customtkinter as ctk
import os
from tkinter import messagebox
from datetime import datetime
from PIL import Image
from customtkinter import CTkImage

from TechnicianProfile import TechnicianProfileWindow
from TechnicianConfirm import PendingRequestsCTK
from TechnicianTicket import TicketsWindow
from TechnicianBackup import BackupMainWindow


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")

class TechnicianDashboard(ctk.CTkToplevel):
    def __init__(self, parent, user_id, role, full_name):
        super().__init__()
        self.title("Technician Dashboard")
        self.geometry("800x600")
        self.configure(fg_color="#E8F5E9")
        self.parent = parent
        self.user_id = user_id
        self.role = role
        self.full_name = full_name
        self.state('zoomed')

        # Main container centered
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20, pady=(10, 10))

        # Header section
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

        # Button frame centered
        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.pack(expand=True)

        # Technician role and full name label
        self.role_label = ctk.CTkLabel(
            button_frame,
            text=f"{self.role}: {self.full_name}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1B5E20")
        self.role_label.pack(pady=(0, 20))

        button_style = {
            "width": 250,
            "height": 60,
            "corner_radius": 10,
            "font": ctk.CTkFont(size=18),
            "fg_color": "#388E3C",
            "hover_color": "#2E7D32"
        }

        # Buttons for dashboard features
        buttons = [
            ("Profile", self.open_profile),
            ("Confirm Profiles", self.open_pending_requests),
            ("Tickets", self.open_tickets),
            ("Backup", self.open_backup_main)
        ]

        for text, cmd in buttons:
            btn = ctk.CTkButton(button_frame, text=text, command=cmd, **button_style)
            btn.pack(pady=15)

        # Timestamp label at bottom-right corner, updated every second
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

        # Initialize window references
        self.pending_window = None
        self.tickets_window = None
        self.profile_window = None
        self.backup_main_window = None

    def update_timestamp(self):
        """Update the timestamp label every second."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 

    # The following methods open the respective windows as modal dialogs,
    # ensuring only one instance is open and managing focus properly.
    
    def open_profile(self):
        "Pass a callback to update profile info on dashboard"
        if self.profile_window and self.profile_window.winfo_exists():
            self.profile_window.lift()
            return
        self.profile_window = TechnicianProfileWindow(self, self.user_id, self.role, self.full_name, on_profile_update=self.update_profile_info)
        self.profile_window.grab_set()
        self.profile_window.focus_force()

    def update_profile_info(self, new_full_name=None, new_role=None):
        """Update the displayed profile information on the dashboard."""
        if new_full_name:
            self.full_name = new_full_name
        if new_role:
            self.role = new_role
        self.role_label.configure(text=f"{self.role}: {self.full_name}")

    def open_pending_requests(self):
        if self.pending_window and self.pending_window.winfo_exists():
            self.pending_window.lift()
            return
        self.pending_window = PendingRequestsCTK(self, self.user_id)
        self.pending_window.grab_set()
        self.pending_window.focus_force()

    def open_tickets(self):
        if self.tickets_window and self.tickets_window.winfo_exists():
            self.tickets_window.lift()
            return
        self.tickets_window = TicketsWindow(self, self.user_id)
        self.tickets_window.grab_set()
        self.tickets_window.focus_force()

    def open_backup_main(self):
        if self.backup_main_window and self.backup_main_window.winfo_exists():
            self.backup_main_window.lift()
            return
        self.backup_main_window = BackupMainWindow(self, technician_id=self.user_id)
        self.backup_main_window.grab_set()
        self.backup_main_window.focus_force()

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