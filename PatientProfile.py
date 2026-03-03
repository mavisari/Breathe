# This module implements the user profile management section, where patients can view and update their personal data entered during registration. 
# For example, if a patient needs to recover their password, they can use this section to set a new one after recovery.

import customtkinter as ctk
import sqlite3
import os
import re
from datetime import datetime
from PIL import Image
from customtkinter import CTkImage

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")
DB_PATH = "DBproject.db"

# Window for viewing and editing the patient's personal profile information.
# Allows the patient to update fields such as password, address, and contact details.

class PatientProfile(ctk.CTkToplevel):
    def __init__(self, parent, user_id, role, full_name, on_profile_update=None):
        super().__init__(parent)
        self.parent = parent
        self.user_id = user_id
        self.title("User Profile")
        self.geometry("600x700")
        self.configure(fg_color="#E8F5E9")
        self.state('zoomed')
        self.grab_set()  # Make this window modal

        self.role = role
        self.full_name = full_name
        self.on_profile_update = on_profile_update
        self.data = {}
        self.entries = {}
        self.editing = False

        self.load_user_data()

        # Main container for the profile page
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", padx=20, pady=(10, 10))  

        # Header with logo and title
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x", anchor="w", pady=(0, 10))

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

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20, pady=20)

        # Display user role and full name
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

        # Create entry widgets for each profile field
        for key, value in self.data.items():
            row_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
            row_frame.pack(pady=5, padx=10, anchor="center")
            label = ctk.CTkLabel(row_frame, text=key + ":", width=150, anchor="w", justify="left", text_color="#1B5E20")
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

        # Button frame for actions
        self.button_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.button_frame.pack(pady=15)

        self.button_style = {
            "fg_color": "#388E3C",
            "hover_color": "#2E7D32",
            "text_color": "white",
            "font": ctk.CTkFont(size=14),
            "width": 140
        }
        self.goback_style = {
            "fg_color": "#A5D6A7",
            "hover_color": "#81C784",
            "text_color": "white",
            "font": ctk.CTkFont(size=14),
            "width": 140
        }

        # Action buttons for editing, saving, and exiting
        self.modify_btn = ctk.CTkButton(self.button_frame, text="Modify Information", command=self.enable_editing, **self.button_style)
        self.modify_btn.pack(side="left", padx=10)

        self.exit_btn = ctk.CTkButton(self.button_frame, text="← Exit", command=self.go_back, **self.goback_style)
        self.exit_btn.pack(side="left", padx=10)

        self.save_btn = ctk.CTkButton(self.button_frame, text="Save Changes", command=self.save_data, **self.button_style)
        self.cancel_btn = ctk.CTkButton(self.button_frame, text="Cancel Changes", command=self.cancel_editing, **self.button_style)

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
        """Load the user's data from the database and store it in self.data."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Name, Surname, Birthplace, Birthdate, Street, City, ZIP, TaxCode, Email, Password, Telephone
            FROM Person WHERE ID_Person = ? AND Role = 'Patient'
        """, (self.user_id,))
        row = cursor.fetchone()
        conn.close()
        fields = [
            "Name", "Surname", "Birthplace", "Birthdate", "Street", "City", "ZIP",
            "TaxCode", "Email", "Password", "Telephone"
        ]
        if row:
            self.data = dict(zip(fields, row))
        else:
            self.data = {field: "" for field in fields}

    def validate_data(self, new_data):
        """Validate the new data before saving. Returns (True, "") if valid, otherwise (False, error_message)."""
        required_fields = list(new_data.keys())
        for field in required_fields:
            if not new_data[field]:
                return False, f"{field} cannot be empty."

        if len(new_data["Name"]) > 20:
            return False, "Name must be at most 20 characters."
        if len(new_data["Surname"]) > 20:
            return False, "Surname must be at most 20 characters."
        if len(new_data["Birthplace"]) > 40:
            return False, "Birthplace must be at most 40 characters."
        if len(new_data["Street"]) > 50:
            return False, "Street must be at most 50 characters."
        if len(new_data["City"]) > 35:
            return False, "City must be at most 35 characters."
        if new_data["ZIP"] and (not new_data["ZIP"].isdigit() or len(new_data["ZIP"]) > 5):
            return False, "ZIP must be a number up to 5 digits."
        if len(new_data["TaxCode"]) != 16:
            return False, "Tax Code must be exactly 16 characters."
        if len(new_data["Email"]) > 40:
            return False, "Email must be at most 40 characters."
        if len(new_data["Password"]) < 8:
            return False, "Password must be at least 8 characters."
        if len(new_data["Password"]) > 30:
            return False, "Password must be at most 30 characters."
        if len(new_data["Telephone"]) > 20:
            return False, "Telephone must be at most 20 characters."
        return True, ""

    def enable_editing(self):
        """Enable editing for all profile fields."""
        self.editing = True
        for entry in self.entries.values():
            entry.configure(state="normal")
        self.modify_btn.pack_forget()
        self.save_btn.pack(side="left", padx=10)
        self.cancel_btn.pack(side="left", padx=10)

    def cancel_editing(self):
        """Cancel editing and restore original data."""
        for key, entry in self.entries.items():
            entry.delete(0, "end")
            entry.insert(0, str(self.data[key]))
            entry.configure(state="disabled")
        self.save_btn.pack_forget()
        self.cancel_btn.pack_forget()
        self.modify_btn.pack(side="left", padx=10)
        self.message_label.configure(text="")

    def save_data(self):
        """Validate and save the updated profile data to the database."""
        new_data = {key: entry.get().strip() for key, entry in self.entries.items()}
        changes = {k: v for k, v in new_data.items() if v != str(self.data[k])}

        if not changes:
            self.message_label.configure(text="No modification made.", text_color="gray")
            return

        is_valid, error_message = self.validate_data(new_data)
        if not is_valid:
            self.message_label.configure(text=error_message, text_color="red")
            return
        
        # Validate birthdate format
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", new_data["Birthdate"]):
            self.message_label.configure(text="Birthdate must be in YYYY-MM-DD format.", text_color="red")
            return

        # Email must contain '@'
        if "@" not in new_data["Email"]:
            self.message_label.configure(text="Invalid email format (missing '@').", text_color="red")
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
            self.modify_btn.pack(side="left", padx=10)
            self.message_label.configure(text="Changes saved successfully.", text_color="#1B5E20")

            if self.on_profile_update and callable(self.on_profile_update):
                full_name = f"{new_data.get('Name', '')} {new_data.get('Surname', '')}".strip()
                self.on_profile_update(new_full_name=full_name)

        except Exception as e:
            self.message_label.configure(text=f"Error while saving: {str(e)}", text_color="red")    

    def format_birthdate_input(self, event):
        """Format the birthdate input as YYYY-MM-DD while typing."""
        entry = self.entries["Birthdate"]
        text = entry.get()
        # Remove everything except digits
        digits_only = ''.join(filter(str.isdigit, text))

        # Limit to 8 digits (YYYYMMDD)
        digits_only = digits_only[:8]

        # Reconstruct with dashes after year and month
        if len(digits_only) >= 5:
            formatted = digits_only[:4] + '-' + digits_only[4:6] + '-' + digits_only[6:]
        elif len(digits_only) >= 3:
            formatted = digits_only[:4] + '-' + digits_only[4:]
        elif len(digits_only) > 0:
            formatted = digits_only
        else:
            formatted = ""

        # Prevent cursor from jumping by always moving it to the end
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
        self.grab_release()
        self.destroy()
        if self.parent:
            self.parent.deiconify()
            self.parent.after(0, lambda: self.parent.state('zoomed'))