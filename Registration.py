# This module implements the registration screen for the application.
# Depending on the user's role (Patient, Specialist, Technician), different registration forms are presented with role-specific fields.
# After registration:
# - Patient and Specialist profiles are placed on standby awaiting technician approval.
# - Technician profiles are registered immediately and can log in directly (as system admins).

import customtkinter as ctk
import sqlite3
import os
import re
from datetime import datetime
from PIL import Image
from customtkinter import CTkImage

from Login import LoginWindow  

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")
DB_PATH = os.path.join(BASE_DIR, "DBproject.db")

# Window for selecting the user role before registration.
# Provides buttons for Patient, Specialist, and Technician roles.

class RoleSelection(ctk.CTkToplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title("Select Your Role")
        self.geometry("600x500")
        self.configure(fg_color="#E8F5E9")
        self.parent = parent
        self.state('zoomed')

        # Header frame with logo and title
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 0))

        logo_image = Image.open(LOGO_PATH).resize((80, 80), Image.LANCZOS)
        logo = CTkImage(light_image=logo_image, size=(80, 80))
        logo_label = ctk.CTkLabel(header_frame, image=logo, text="")
        logo_label.pack(side="left")

        title_label = ctk.CTkLabel(header_frame, text="BREATHE", font=ctk.CTkFont(size=36, weight="bold"), text_color="#1B5E20")
        title_label.pack(side="left", padx=(100, 0))

        # Container frame centered
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Prompt label
        ctk.CTkLabel(container, text="What is your role?", font=ctk.CTkFont(size=30, weight="bold"), text_color="#1B5E20").pack(pady=40)

        # Button style for role selection
        button_style = {
            "width": 250, "height": 60, "corner_radius": 10,
            "font": ctk.CTkFont(size=18), "fg_color": "#388E3C", "hover_color": "#2E7D32"
        }

        # Buttons for each role
        ctk.CTkButton(container, text="Patient", command=lambda: self.open_registration("Patient"), **button_style).pack(pady=(10, 5))
        ctk.CTkButton(container, text="Specialist", command=lambda: self.open_registration("Specialist"), **button_style).pack(pady=5)
        ctk.CTkButton(container, text="Technician", command=lambda: self.open_registration("Technician"), **button_style).pack(pady=5)

        # Go back button
        ctk.CTkButton(container, text="← Go Back", command=self.go_back, width=150, height=40, corner_radius=10,
                      font=ctk.CTkFont(size=14), fg_color="#A5D6A7", hover_color="#81C784").pack(pady=(5, 10))
        
        # Timestamp label bottom-right
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

        self.grab_set()  # Modal window

    def update_timestamp(self):
        """Update the timestamp label every second."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp)

    def open_registration(self, role):
        """Open the registration form for the selected role.
        The current window is hidden with a slight delay to avoid glitches."""
        form = RegistrationForm(role, self)
        self.after(10, self.withdraw)  # Hide this window after a short delay
        form.lift()  # Bring the new window to front
        form.focus_force()  # Force focus on new window
        form.protocol("WM_DELETE_WINDOW", lambda: (self.deiconify(), form.destroy()))

    def go_back(self):
        """Return to the parent window, restoring and focusing it.
        Then destroy this window with a slight delay."""
        if self.parent:
            self.parent.state("zoomed")      # Maximize parent window
            self.parent.deiconify()          # Show parent window
            self.parent.lift()               # Bring parent to front
            self.parent.focus_force()        # Focus parent window
        self.after(10, self.destroy)         # Destroy this window after delay

# Window for user registration. Fields vary depending on the selected role.
# Handles form validation, database insertion, and role-specific post-registration behavior.

class RegistrationForm(ctk.CTkToplevel):
    def __init__(self, role, parent):
        super().__init__()
        self.title(f"{role} Registration")
        self.geometry("1000x800")
        self.configure(fg_color="#E8F5E9")
        self.role = role
        self.parent = parent
        self.entries = {}

        # Header frame with logo and title
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(10, 10))

        logo_image = Image.open(LOGO_PATH).resize((80, 80), Image.LANCZOS)
        logo = CTkImage(light_image=logo_image, size=(80, 80))
        logo_label = ctk.CTkLabel(header_frame, image=logo, text="")
        logo_label.pack(side="left")

        title_label = ctk.CTkLabel(header_frame, text="BREATHE", font=ctk.CTkFont(size=36, weight="bold"), text_color="#1B5E20")
        title_label.pack(side="left", padx=(100, 0))

        # Form title label
        ctk.CTkLabel(self, text=f"{role} Registration Form", font=ctk.CTkFont(size=28, weight="bold"), text_color="#1B5E20").pack(pady=0)

        # Define fields depending on role
        fields = []
        if self.role == "Patient":
            fields = [
                "Name", "Surname", "Birthplace", "Birthdate (YYYY-MM-DD)", "Street", "City", "ZIP", "Tax Code",
                "Telephone", "Email", "Password", "Confirm Password", "Weight", "Height",
                "Emergency Contact", "Allergy", "Unique Code"
            ]
        elif self.role == "Specialist":
            fields = [
                "Name", "Surname", "Birthplace", "Birthdate (YYYY-MM-DD)", "Street", "City", "ZIP", "Tax Code",
                "Telephone", "Email", "Password", "Confirm Password", "Medical Registration Code"
            ]
        elif self.role == "Technician":
            fields = [
                "Name", "Surname", "Birthplace", "Birthdate (YYYY-MM-DD)", "Street", "City", "ZIP", "Tax Code",
                "Telephone", "Email", "Password", "Confirm Password", "Company Authentication Code"
            ]

        # Scrollable frame to hold input fields
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=700, height=450, fg_color="white", corner_radius=10)
        self.scrollable_frame.pack(padx=20, pady=(10, 5), anchor="center")

        # Create entries for each field, marking password and date fields accordingly
        for field in fields:
            is_password = "Password" in field
            is_date = "Birthdate" in field
            self.add_entry(field, is_password=is_password, is_date=is_date, parent=self.scrollable_frame)

        # Footer frame for notifications and consent
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.pack(pady=(5, 10), anchor="center")

        # Label for notifications and validation messages
        self.notification_label = ctk.CTkLabel(self.footer_frame, text="", text_color="red")
        self.notification_label.pack(pady=5)

        # Consent checkbox for data use agreement
        self.consent_var = ctk.BooleanVar()
        self.consent_check = ctk.CTkCheckBox(
            self.footer_frame,
            text="Agree to the conditions for consent to the use of data",
            variable=self.consent_var
        )
        self.consent_check.pack(pady=(5, 10))

        # Button frame for submit and go back buttons
        self.button_frame = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        self.button_frame.pack(pady=10)

        submit_button_style = {
            "width": 200, "height": 45, "corner_radius": 10,
            "font": ctk.CTkFont(size=16), "fg_color": "#388E3C", "hover_color": "#2E7D32"
        }

        goback_button_style = {
            "width": 200, "height": 45, "corner_radius": 10,
            "font": ctk.CTkFont(size=16), "fg_color": "#A5D6A7", "hover_color": "#81C784"
        }

        ctk.CTkButton(self.button_frame, text="← Go Back", command=self.go_back, **goback_button_style).pack(side="left", padx=40)
        self.submit_button = ctk.CTkButton(self.button_frame, text="Submit →", command=self.confirm, **submit_button_style)
        self.submit_button.pack(side="left", padx=40)

        self.state('zoomed')

        # Timestamp label bottom-right
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

        self.grab_set()  # Make this window modal

    def add_entry(self, label, is_password=False, is_date=False, parent=None):
     """Add a labeled entry widget to the specified parent frame.
     Password entries mask input; date entries have input formatting."""
     frame = ctk.CTkFrame(parent, fg_color="transparent")
     frame.pack(pady=8, anchor="center")

     ctk.CTkLabel(frame, text=label + ":", width=200, anchor="e").pack(side="left", padx=(0, 10))
     entry = ctk.CTkEntry(frame, width=350, show="*" if is_password else "")
     entry.pack(side="left")
     self.entries[label] = entry

     if is_date:
        entry.bind("<KeyRelease>", lambda e: self.format_date(entry))
     elif label in ["ZIP", "Unique Code", "Medical Registration Code", "Company Authentication Code"]:
        entry.bind("<KeyRelease>", lambda e: self.filter_digits(entry))
     elif label in ["Telephone", "Emergency Contact"]:
        entry.bind("<KeyRelease>", lambda e: self.filter_digits(entry))
     elif label in ["Weight", "Height"]:
        entry.bind("<KeyRelease>", lambda e: self.filter_float(entry))
        
    def format_date(self, entry):
        """Format the entry text as a date in YYYY-MM-DD format while typing.
        Non-digit characters are removed and dashes inserted appropriately."""
        value = re.sub(r"[^\d]", "", entry.get())  # Remove all non-digit characters
        formatted = ""
        if len(value) > 0:
            formatted += value[:4]  # Year
        if len(value) > 4:
            formatted += "-" + value[4:6]  # Month
        if len(value) > 6:
            formatted += "-" + value[6:8]  # Day
        entry.delete(0, "end")
        entry.insert(0, formatted)

    def filter_digits(self, entry):
     """Allow only digit characters in the entry."""
     value = re.sub(r"[^\d]", "", entry.get())
     entry.delete(0, "end")
     entry.insert(0, value)

    def filter_float(self, entry):
     """Allow only digits and a single dot for decimal numbers."""
     value = entry.get()
     filtered = re.sub(r"[^\d.]", "", value)
     parts = filtered.split(".")
     if len(parts) > 2:
        filtered = ".".join(parts[:2])  # only keep one dot
     entry.delete(0, "end")
     entry.insert(0, filtered)
     
    def update_timestamp(self):
        """Update the timestamp label every second."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp)

    def confirm(self):
        """Validate the registration form data before submission.
        Checks for missing fields, password match and length, consent,
        and validates formats for Tax Code, Telephone, Email, ZIP, and other fields.
        Inserts data into the database according to role-specific logic."""
        data = {}
        has_missing = False

        # Collect data from entries and check for missing values
        for label, entry in self.entries.items():
            value = entry.get().strip()
            if not value:
                has_missing = True
            data[label] = value

        if has_missing:
            self.notification_label.configure(text="Missing information", text_color="red")
            return

        # Password and confirmation must match
        if data.get("Password") != data.get("Confirm Password"):
            self.notification_label.configure(text="Passwords don't match", text_color="red")
            return

        # Password minimum length check
        if len(data.get("Password", "")) < 8:
            self.notification_label.configure(text="Password must be at least 8 characters", text_color="red")
            return

        # Consent must be given
        if not self.consent_var.get():
            self.notification_label.configure(text="You must accept the terms and conditions", text_color="red")
            return

        # Tax Code validation
        if not re.fullmatch(r"[A-Za-z0-9]{16}", data.get("Tax Code", "")):
            self.notification_label.configure(text="Tax Code must be 16 alphanumeric characters", text_color="red")
            return

        # Telephone validation
        if not re.fullmatch(r"\d{10,}", data.get("Telephone", "")):
            self.notification_label.configure(text="Invalid Telephone number (at least 10 digits)", text_color="red")
            return

        # Email format validation
        if not re.fullmatch(r"^[\w\.-]+@[\w\.-]+\.\w+$", data.get("Email", "")):
            self.notification_label.configure(text="Invalid Email format", text_color="red")
            return

        # Emergency Contact validation
        if "Emergency Contact" in data and data["Emergency Contact"] and not re.fullmatch(r"\d{10,}", data["Emergency Contact"]):
            self.notification_label.configure(text="Emergency Contact must be a valid phone number", text_color="red")
            return


        # Insert data into database with role-specific logic
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()

            # Check if email is already registered or awaiting confirmation
            c.execute("SELECT 1 FROM Person WHERE Email = ? UNION SELECT 1 FROM WaitingConfirmation WHERE Email = ?", (data["Email"], data["Email"]))
            if c.fetchone():
                self.notification_label.configure(text="Email already registered", text_color="red")
                conn.close()
                return

            if self.role in ["Patient", "Specialist"]:
                # Insert into WaitingConfirmation table for approval
                insert_query = """
                INSERT INTO WaitingConfirmation (
                    Email, Name, Surname, Birthplace, Birthdate, Street, City, ZIP, TaxCode,
                    Password, Telephone, Role, Weight, Height, EmergencyContactNumber, Allergy,
                    UniqueCode, MedicalRegistrationCode
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                values = [
                    data.get("Email"), data.get("Name"), data.get("Surname"), data.get("Birthplace"), data.get("Birthdate (YYYY-MM-DD)"),
                    data.get("Street"), data.get("City"), int(data["ZIP"]) if data.get("ZIP") else None, data.get("Tax Code"),
                    data.get("Password"), data.get("Telephone"), self.role,
                    float(data["Weight"]) if data.get("Weight") else None,
                    float(data["Height"]) if data.get("Height") else None,
                    data.get("Emergency Contact"),
                    data.get("Allergy"),
                    int(data["Unique Code"]) if data.get("Unique Code") else None,
                    data.get("Medical Registration Code")
                ]
                c.execute(insert_query, values)
                conn.commit()
                self.notification_label.configure(text="Account awaiting approval", text_color="green")

            elif self.role == "Technician":
                # Generate new Technician ID
                c.execute("SELECT ID_Person FROM Person WHERE Role = 'Technician' ORDER BY ID_Person DESC LIMIT 1")
                last_id = c.fetchone()
                new_number = int(last_id[0][1:]) + 1 if last_id else 1
                new_id = f"T{new_number:04d}"

                # Insert directly into Person table
                insert_query = """
                INSERT INTO Person (
                    ID_Person, Name, Surname, Birthplace, Birthdate, Street, City, ZIP, TaxCode,
                    Email, Password, Telephone, Role, CompanyAuthenticationCode
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                values = [
                    new_id, data.get("Name"), data.get("Surname"), data.get("Birthplace"), data.get("Birthdate (YYYY-MM-DD)"),
                    data.get("Street"), data.get("City"), int(data["ZIP"]) if data.get("ZIP") else None, data.get("Tax Code"),
                    data.get("Email"), data.get("Password"), data.get("Telephone"), "Technician",
                    data.get("Company Authentication Code")
                ]
                c.execute(insert_query, values)
                conn.commit()
                self.notification_label.configure(text="Registration successful!", text_color="green")
                self.submit_button.destroy()

                # Show login button after successful technician registration
                self.login_button = ctk.CTkButton(
                    self.button_frame, text="Login →", width=200, height=45, corner_radius=10,
                    font=ctk.CTkFont(size=16), fg_color="#388E3C", hover_color="#2E7D32", command=self.open_login)
                self.login_button.pack(side="left", padx=40)

            conn.close()

        except Exception as e:
            self.notification_label.configure(text=f"Error: {str(e)}", text_color="red")

    def open_login(self):
        """Open the login window and hide the registration form without destroying it."""
        self.withdraw()  # Hide registration window
        login_window = LoginWindow(parent=None, return_to="registration", return_window=self)
        login_window.mainloop()
        
    def go_back(self):
        """Return to the previous window (role selection).
        Restores and focuses the parent window before destroying the registration form."""
        if self.parent:
            self.parent.state('zoomed')           # Maximize parent window
            self.parent.deiconify()               # Show parent window
            self.parent.lift()                    # Bring parent to front
            self.parent.focus_force()             # Focus parent window
        self.after(10, self.destroy)              # Destroy this window after a short delay