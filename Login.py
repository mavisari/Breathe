# This code implements the Login Window GUI, which allows registered users to access the application by entering their credentials.
# It also provides a connection to the password retrieval page for users who have forgotten their password.
# The login window manages user authentication and directs users to their respective dashboards based on their roles.

import customtkinter as ctk
import sqlite3
import os
from datetime import datetime
from PIL import Image
from customtkinter import CTkImage

from Retrieve import RetrievePassword
from DashboardPatient import PatientDashboard
from DashboardSpecialist import SpecialistDashboard
from DashboardTechnician import TechnicianDashboard

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

class LoginWindow(ctk.CTkToplevel):
    def __init__(self, parent=None, dashboard_callback=None, return_to=None, return_window=None):
        super().__init__()
        # Initialize the login window with title, size, and styling
        self.title("Login")
        self.geometry("500x600")
        self.configure(fg_color="#E8F5E9")
        self.parent = parent
        self.state("zoomed")  # Maximize window
        self.dashboard_callback = dashboard_callback
        self.return_to = return_to
        self.return_window = return_window
        self.create_widgets()
        # Override window close event to handle going back properly
        self.protocol("WM_DELETE_WINDOW", self.go_back)

    def create_widgets(self):
        # Load and display logo and title
        BASE_DIR = os.path.dirname(__file__)
        LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 0))

        logo_image = Image.open(LOGO_PATH).resize((80, 80), Image.LANCZOS)
        logo = CTkImage(light_image=logo_image, size=(80, 80))
        logo_label = ctk.CTkLabel(header_frame, image=logo, text="")
        logo_label.pack(side="left")

        title_label = ctk.CTkLabel(
            header_frame,
            text="BREATHE",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#1B5E20"
        )
        title_label.pack(side="left", padx=(100, 0))

        # Label for Login section
        ctk.CTkLabel(self, text="Login", font=ctk.CTkFont(size=28, weight="bold"), text_color="#1B5E20").pack(pady=(40, 20))

        # Email input field
        self.email_entry = ctk.CTkEntry(self, placeholder_text="Email", width=300, height=45, font=ctk.CTkFont(size=14))
        self.email_entry.pack(pady=10)

        # Password input field (masked)
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=300, height=45, font=ctk.CTkFont(size=14))
        self.password_entry.pack(pady=10)

        # Label to show error or status messages
        self.message_label = ctk.CTkLabel(self, text="", text_color="red")
        self.message_label.pack(pady=(10, 5))

        # Login button triggers authentication
        self.login_button = ctk.CTkButton(self, text="Login →", command=self.login_user,
                                          width=240, height=50, font=ctk.CTkFont(size=16),
                                          fg_color="#388E3C", hover_color="#2E7D32")
        self.login_button.pack(pady=(10, 15))

        # Button to open password retrieval window
        self.retrieve_button = ctk.CTkButton(self, text="Retrieve Password", command=self.open_retrieve_password,
                                             width=240, height=45, font=ctk.CTkFont(size=14),
                                             fg_color="#A5D6A7", hover_color="#81C784", text_color="white")
        self.retrieve_button.pack(pady=(0, 15))

        # Button to go back to previous window
        self.go_back_button = ctk.CTkButton(self, text="← Go Back", command=self.go_back,
                                            width=180, height=40, font=ctk.CTkFont(size=14),
                                            fg_color="#A5D6A7", hover_color="#81C784", text_color="white")
        self.go_back_button.pack(pady=(10, 10))
    
        # Timestamp label at bottom-right corner, updated every second
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        # Update the timestamp label every second to show current time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 

    def login_user(self):
        # Authenticate user credentials and open the appropriate dashboard
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        self.message_label.configure(text="", text_color="red")

        # Check for missing inputs
        if not email or not password:
            self.message_label.configure(text="Missing information", text_color="red")
            return

        conn = sqlite3.connect("DBproject.db")
        cursor = conn.cursor()

        # Check if account is awaiting approval
        cursor.execute("SELECT 1 FROM WaitingConfirmation WHERE email=?", (email,))
        if cursor.fetchone():
            self.message_label.configure(text="Account awaiting approval", text_color="red")
            conn.close()
            return

        # Retrieve user info for authentication
        cursor.execute("SELECT ID_Person, password, role FROM Person WHERE email=?", (email,))
        result = cursor.fetchone()

        if result is None:
            self.message_label.configure(text="Account not registered", text_color="red")
            conn.close()
            return

        user_id, correct_password, role = result

        # Check password correctness
        if password != correct_password:
            self.message_label.configure(text="Wrong credentials", text_color="red")
            conn.close()
            return

        # Retrieve full name for dashboard display
        cursor.execute("SELECT name, surname FROM Person WHERE ID_Person=?", (user_id,))
        person_info = cursor.fetchone()
        conn.close()

        if person_info:
            name, surname = person_info
            full_name = f"{name} {surname}"

            # Close login window and open the respective dashboard
            self.destroy()
            if self.dashboard_callback:
                self.dashboard_callback(role, user_id, full_name)
            else:
                if role == "Technician":
                    dashboard = TechnicianDashboard(self.parent, user_id, role, full_name)
                elif role == "Patient":
                    dashboard = PatientDashboard(self.parent, user_id, role, full_name)
                elif role == "Specialist":
                    dashboard = SpecialistDashboard(self.parent, user_id, role, full_name)
                else:
                    self.message_label.configure(text=f"Unsupported role: {role}", text_color="red")
                    self.deiconify()
                    return

                # Set dashboard as modal window to block parent interaction
                dashboard.grab_set()
                dashboard.protocol("WM_DELETE_WINDOW", self.parent.deiconify)
        else:
            self.message_label.configure(text="Account not registered", text_color="red")

    def open_retrieve_password(self):
        # Open the password retrieval window modally, hiding login window
        self.withdraw()
        retrieve_window = RetrievePassword(self)
        retrieve_window.grab_set()
        retrieve_window.protocol("WM_DELETE_WINDOW", self.deiconify)

    def go_back(self):
        # Return to previous window or parent and close login window
        if self.return_to == "registration" and self.return_window:
            self.return_window.state("zoomed")
            self.return_window.deiconify()
            self.return_window.lift()
            self.return_window.focus_force()
        elif self.parent:
            self.parent.state("zoomed")
            self.parent.deiconify()
            self.parent.lift()
            self.parent.focus_force()
        self.after(10, self.destroy)