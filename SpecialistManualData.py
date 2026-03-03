# This module implements the manual data entry window for specialists to input patient vitals and notes.
# It includes a scrollable frame with input fields, a text box for visit notes, and a table displaying historical manual data.

import customtkinter as ctk
import sqlite3
import os
from datetime import datetime, date
from PIL import Image
from customtkinter import CTkImage

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")

# Window for specialists to manually enter patient data.
# Displays input fields for blood pressure, oxygen saturation, weight, and visit notes.
# Also shows a table of previous manual data entries.

class SpecialistManualData(ctk.CTkToplevel):
    def __init__(self, parent, specialist_id, patient_id):
        super().__init__()
        self.title("Manual Data Entry")
        self.geometry("700x600")
        self.configure(fg_color="#E8F5E9")
        self.state('zoomed')
        self.grab_set()  # Make this window modal to block interaction with parent

        self.parent = parent
        self.specialist_id = specialist_id
        self.patient_id = patient_id

        # Scrollable frame to hold all content
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="#E8F5E9")
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header frame with logo and title inside scrollable frame
        header_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 10))

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
        
        # Title label for manual data section
        ctk.CTkLabel(self.scrollable_frame, text="Manual Data", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1B5E20").pack(pady=20)

        # Frame for input form
        form_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        form_frame.pack(pady=10)

        # Labels for input fields
        labels = ["Blood Pressure (mmHg)", "Oxygen Saturation (%)", "Weight (kg)"]
        self.entries = {}

        input_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        input_frame.pack(pady=10)

        # Create label and entry for each input field
        for i, label_text in enumerate(labels):
            lbl = ctk.CTkLabel(input_frame, text=label_text, font=ctk.CTkFont(size=14))
            lbl.grid(row=0, column=i, padx=20, pady=5)
            entry = ctk.CTkEntry(input_frame, width=100, placeholder_text="Value")
            entry.grid(row=1, column=i, padx=20, pady=5)
            self.entries[label_text] = entry

        # Label and textbox for visit note
        ctk.CTkLabel(form_frame, text="Visit Note:", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 5))
        self.visit_note_textbox = ctk.CTkTextbox(form_frame, width=600, height=100)
        self.visit_note_textbox.pack(pady=(0, 15))

        # Feedback label for errors or info
        self.feedback_label = ctk.CTkLabel(self.scrollable_frame, text="", text_color="red")
        self.feedback_label.pack(pady=5)

        # Submit button for manual data
        submit_btn = ctk.CTkButton(form_frame, text="Submit", command=self.submit_manual_data,
                                   fg_color="#388E3C", hover_color="#2E7D32")
        submit_btn.pack(pady=15)

        # Outer frame for historical data table with green background
        table_outer_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="#C8E6C9")
        table_outer_frame.pack(pady=15, fill="x")
        table_outer_frame.configure(height=300)
        table_outer_frame.pack_propagate(False)

        # Inner frame for table with white background and rounded corners
        self.table_bg_frame = ctk.CTkFrame(table_outer_frame, fg_color="white", corner_radius=5)
        self.table_bg_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Table headers
        headers = ["Visit Date", "Blood Pressure (mmHg)", "Oxygen Saturation (%)", "Weight (kg)", "Visit Note"]
        for col, text in enumerate(headers):
            lbl = ctk.CTkLabel(self.table_bg_frame,
                               text=text,
                               font=ctk.CTkFont(size=14, weight="bold"),
                               fg_color="white",
                               anchor="center",
                               justify="center")
            lbl.grid(row=0, column=col, sticky="nsew", padx=5, pady=(8, 5))
            self.table_bg_frame.grid_columnconfigure(col, weight=1)

        # Load historical manual data into the table
        self.load_historical_data()

        # Exit button to close this window and return to parent
        back_btn = ctk.CTkButton(self.scrollable_frame, text="← Exit", command=self.go_back,
                                 width=120, height=35,
                                 fg_color="#A5D6A7", hover_color="#81C784",
                                 text_color="white", font=ctk.CTkFont(size=14))
        back_btn.pack(pady=15)

        # Timestamp label bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second with current date and time."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp)

    def submit_manual_data(self):
        """Collect manual data inputs, validate, and insert into the database.
        Updates the visit annotation with the visit note.
        Clears input fields and reloads historical data upon success."""
        pressure = self.entries["Blood Pressure (mmHg)"].get().strip()
        oxygen = self.entries["Oxygen Saturation (%)"].get().strip()
        weight = self.entries["Weight (kg)"].get().strip()
        visit_note = self.visit_note_textbox.get("1.0", "end").strip()

        # Validate required fields
        if not all([pressure, oxygen, weight]):
            self.feedback_label.configure(text="Please fill in all fields.", text_color="red")
            return

        try:
            conn = sqlite3.connect("DBproject.db")
            c = conn.cursor()

            visit_date_str = date.today().strftime("%Y-%m-%d")

            # Find the latest visit for this patient today
            c.execute("""
                SELECT ID_Visit FROM Visit 
                WHERE ID_Patient=? AND VisitDate=?
                ORDER BY VisitDate DESC LIMIT 1
            """, (self.patient_id, visit_date_str))
            visit_row = c.fetchone()

            if not visit_row:
                self.feedback_label.configure(text="No visit found for this patient today.", text_color="red")
                conn.close()
                return

            id_visit = visit_row[0]
            id_manual_data = f"MD_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            compilation_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Insert manual data record
            c.execute("""
                INSERT INTO ManualData (ID_ManualData, ID_Visit, CompilationDate, BloodPressure, OxygenSaturation, Weight, VisitNote)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id_manual_data, id_visit, compilation_datetime, pressure, oxygen, weight, visit_note))

            # Update visit annotation with visit note
            c.execute("""
                UPDATE Visit
                SET Annotation = ?
                WHERE ID_Visit = ?
            """, (visit_note, id_visit))

            conn.commit()
            conn.close()

            self.feedback_label.configure(text="Manual data submitted successfully.", text_color="green")

            # Clear inputs
            for entry in self.entries.values():
                entry.delete(0, "end")
            self.visit_note_textbox.delete("1.0", "end")

            # Reload historical data to reflect new entry
            self.load_historical_data()

        except sqlite3.Error as e:
            self.feedback_label.configure(text=f"Database error: {e}", text_color="red")

    def load_historical_data(self):
        """Load the last 20 manual data entries from the database and display them in the table.
        Truncates long visit notes for display."""
        # Clear existing table rows (except headers)
        for widget in self.table_bg_frame.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()

        try:
            conn = sqlite3.connect("DBproject.db")
            c = conn.cursor()

            c.execute("""
                SELECT V.VisitDate, M.BloodPressure, M.OxygenSaturation, M.Weight, M.VisitNote
                FROM ManualData M
                JOIN Visit V ON M.ID_Visit = V.ID_Visit
                WHERE V.ID_Patient=?
                ORDER BY V.VisitDate DESC
                LIMIT 20
            """, (self.patient_id,))

            rows = c.fetchall()
            conn.close()

            # Populate table rows
            for i, row in enumerate(rows, start=1):
                for col, val in enumerate(row):
                    # Truncate visit notes longer than 40 characters
                    display_text = val if col != 4 else (val[:40] + "..." if val and len(val) > 40 else val)
                    lbl = ctk.CTkLabel(self.table_bg_frame, text=str(display_text or ""),
                                       anchor="center", justify="center",
                                       font=ctk.CTkFont(size=12))
                    lbl.grid(row=i, column=col, sticky="nsew", padx=5, pady=(5, 2))

        except sqlite3.Error as e:
            self.feedback_label.configure(text=f"Error loading data: {e}", text_color="red")

    def go_back(self):
        """Close this window and restore the parent window."""
        self.grab_release()
        self.destroy()
        if self.parent:
            self.parent.deiconify()
            self.parent.after(0, lambda: self.parent.state('zoomed'))