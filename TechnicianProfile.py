# This module implements the technician profile management section, where technicians can view and update their personal data entered during registration. 
# For example, if a technician needs to recover their password, they can use this section to set a new one after recovery.

import customtkinter as ctk
import sqlite3
import os
import re
from datetime import datetime
from PIL import Image
from customtkinter import CTkImage

DB_PATH = "DBproject.db"
BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")

# Window for viewing and editing the technician's personal profile information.
# Allows the technician to update fields such as password, address, and contact details.

class TechnicianProfileWindow(ctk.CTkToplevel):
    def __init__(self, parent, user_id, role, full_name, on_profile_update=None):
        super().__init__(parent)
        self.transient(parent)
        self.lift()
        self.focus_force()
        self.parent = parent
        self.user_id = user_id
        self.state('zoomed')
        self.title("Technician Profile")
        self.geometry("600x700")
        self.configure(fg_color="#E8F5E9")
        self.role = role
        self.full_name = full_name
        self.on_profile_update = on_profile_update
        self.data = {}
        self.entries = {}
        self.editing = False

        self.load_user_data()

        # Main container for the profile page
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20, pady=20)

        # Header with logo and title
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

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

        # Display role and full name
        role_label = ctk.CTkLabel(
            container,
            text=f"{self.role}: {self.full_name}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1B5E20"
        )
        role_label.pack(pady=(10, 20))

        # Form frame for all profile fields
        self.form_frame = ctk.CTkFrame(container, fg_color="white", corner_radius=10)
        self.form_frame.pack(pady=20, padx=60, fill="both", expand=False)

        fields_to_show = [
            "Name", "Surname", "Birthplace", "Birthdate", "Street", "City",
            "ZIP", "TaxCode", "Email", "Password", "Telephone"
        ]

        # Create entry widgets for each profile field
        for key in fields_to_show:
            value = self.data.get(key, "")
            row_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
            row_frame.pack(pady=5, padx=10, anchor="center")
            label = ctk.CTkLabel(row_frame, text=key + ":", width=150, anchor="w", justify="left")
            label.pack(side="left", padx=(0, 10))
            entry = ctk.CTkEntry(row_frame, width=300)
            entry.insert(0, str(value))
            entry.configure(state="disabled")
            entry.pack(side="left")
            self.entries[key] = entry

        # Bind input validation for certain fields
        self.entries["Birthdate"].bind("<KeyRelease>", self.format_birthdate_input)
        self.entries["ZIP"].bind("<KeyRelease>", lambda e: self.filter_digits(self.entries["ZIP"]))
        self.entries["Telephone"].bind("<KeyRelease>", lambda e: self.filter_digits(self.entries["Telephone"]))

        # Button styles for consistency
        button_style = {
            "fg_color": "#388E3C",
            "hover_color": "#2E7D32",
            "text_color": "white",
            "font": ctk.CTkFont(size=14)
        }
        self.goback_style = {
            "fg_color": "#A5D6A7",
            "hover_color": "#81C784",
            "text_color": "white",
            "font": ctk.CTkFont(size=14),
            "width": 140
        }

        # Action buttons for editing, saving, and exiting
        self.modify_btn = ctk.CTkButton(container, text="Modify Information", command=self.enable_editing, **button_style)
        self.modify_btn.pack(pady=10)

        self.exit_btn = ctk.CTkButton(container, text="← Exit", command=self.go_back, **self.goback_style)
        self.exit_btn.pack(pady=5)

        # Message label for feedback and errors
        self.message_label = ctk.CTkLabel(container, text="", text_color="#1B5E20", font=ctk.CTkFont(size=14))
        self.message_label.pack(pady=(5, 0))

        # Timestamp label at the bottom-right
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 

    def load_user_data(self):
        """Load the technician's data from the database and store it in self.data."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ID_Person, Name, Surname, Birthplace, Birthdate, Street, City, ZIP, TaxCode, Email, Password, Telephone
            FROM Person WHERE ID_Person = ? AND Role = 'Technician'
        """, (self.user_id,))
        row = cursor.fetchone()
        conn.close()
        fields = ["ID_Person", "Name", "Surname", "Birthplace", "Birthdate", "Street", "City", "ZIP", "TaxCode", "Email", "Password", "Telephone"]
        if row:
            self.data = dict(zip(fields, row))
        else:
            self.data = {field: "" for field in fields}

    def enable_editing(self):
        """Enable editing for all profile fields."""
        self.editing = True
        for entry in self.entries.values():
            entry.configure(state="normal")
        self.modify_btn.pack_forget()

        button_style = {
            "fg_color": "#388E3C",
            "hover_color": "#2E7D32",
            "text_color": "white",
            "font": ctk.CTkFont(size=14)
        }

        self.save_btn = ctk.CTkButton(self.exit_btn.master, text="Confirm Changes", command=self.save_data, **button_style)
        self.cancel_btn = ctk.CTkButton(self.exit_btn.master, text="Cancel Changes", command=self.cancel_editing, **button_style)
        self.save_btn.pack(pady=5, before=self.exit_btn)
        self.cancel_btn.pack(pady=5, before=self.exit_btn)
        self.state('zoomed')

    def cancel_editing(self):
        """Cancel editing and restore original data."""
        fields_to_show = [
            "Name", "Surname", "Birthplace", "Birthdate", "Street", "City",
            "ZIP", "TaxCode", "Email", "Password", "Telephone"
        ]
        for key in fields_to_show:
            entry = self.entries[key]
            entry.delete(0, "end")
            entry.insert(0, str(self.data.get(key, "")))
            entry.configure(state="disabled")
        self.save_btn.pack_forget()
        self.cancel_btn.pack_forget()
        self.modify_btn.pack(pady=10)
        self.message_label.configure(text="")
        self.state('zoomed')

    def save_data(self):
        """Validate and save the updated profile data to the database."""
        fields_to_show = [
            "Name", "Surname", "Birthplace", "Birthdate", "Street", "City",
            "ZIP", "TaxCode", "Email", "Password", "Telephone"
        ]
        new_data = {key: self.entries[key].get().strip() for key in fields_to_show}

        # Check for empty fields
        for field, value in new_data.items():
            if not value:
                self.message_label.configure(text=f"Field '{field}' cannot be empty.", text_color="red")
                return

        # Validate birthdate format
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", new_data["Birthdate"]):
            self.message_label.configure(text="Birthdate must be in YYYY-MM-DD format.", text_color="red")
            return

        # Email must contain '@'
        if "@" not in new_data["Email"]:
            self.message_label.configure(text="Invalid email format (missing '@').", text_color="red")
            return

        # Max length checks
        max_lengths = {
            "Name": 50,
            "Surname": 50,
            "Birthplace": 50,
            "Birthdate": 10,
            "Street": 100,
            "City": 50,
            "ZIP": 10,
            "TaxCode": 16,
            "Email": 100,
            "Password": 50,
            "Telephone": 15
        }
        for field, max_len in max_lengths.items():
            if len(new_data[field]) > max_len:
                self.message_label.configure(
                    text=f"Field '{field}' exceeds max length of {max_len} characters.",
                    text_color="red"
                )
                return

        changes = {k: v for k, v in new_data.items() if v != str(self.data.get(k, ""))}
        if not changes:
            self.message_label.configure(text="No modification made.", text_color="red")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            set_clause = ", ".join([f"{field} = ?" for field in changes])
            values = list(changes.values()) + [self.user_id]
            cursor.execute(f"UPDATE Person SET {set_clause} WHERE ID_Person = ?", values)
            conn.commit()
            conn.close()

            self.data.update(changes)
            for key, value in changes.items():
                self.entries[key].configure(state="normal")
                self.entries[key].delete(0, "end")
                self.entries[key].insert(0, str(value))
                self.entries[key].configure(state="disabled")

            self.save_btn.pack_forget()
            self.cancel_btn.pack_forget()
            self.modify_btn.pack(pady=10)
            self.message_label.configure(text="Changes saved successfully.", text_color="#1B5E20")
            self.editing = False

            if self.on_profile_update and callable(self.on_profile_update):
                full_name = f"{new_data.get('Name', '')} {new_data.get('Surname', '')}".strip()
                self.on_profile_update(new_full_name=full_name)

        except Exception as e:
            self.message_label.configure(text=f"Error while saving: {str(e)}", text_color="red")
            self.state('zoomed')

    def format_birthdate_input(self, event):
        """Format the birthdate input as YYYY-MM-DD while typing."""
        entry = self.entries["Birthdate"]
        text = entry.get()
        digits_only = ''.join(filter(str.isdigit, text))
        digits_only = digits_only[:8]
        if len(digits_only) >= 5:
            formatted = digits_only[:4] + '-' + digits_only[4:6] + '-' + digits_only[6:]
        elif len(digits_only) >= 3:
            formatted = digits_only[:4] + '-' + digits_only[4:]
        elif len(digits_only) > 0:
            formatted = digits_only
        else:
            formatted = ""
        entry.delete(0, 'end')
        entry.insert(0, formatted)

    def filter_digits(self, entry):
      """Allow only digits in the given entry field."""
      value = entry.get()
      filtered = ''.join(filter(str.isdigit, value))
      if value != filtered:
        entry.delete(0, 'end')
        entry.insert(0, filtered)

    def go_back(self):
        """Close this window and restore the parent window."""
        self.destroy()
        if self.parent:
            self.parent.deiconify()
            self.parent.after(0, lambda: self.parent.state('zoomed'))