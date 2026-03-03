# This module implements the prescription management windows for specialists.
# It includes two windows:
# 1. PrescriptionList: shows a list of prescriptions for a specific patient or all prescriptions by the specialist.
# 2. NewPrescriptionForm: allows the specialist to create a new prescription for the patient.

import customtkinter as ctk
import sqlite3
import os
from datetime import datetime
from PIL import Image
from customtkinter import CTkImage

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")
DB_PATH = os.path.join(BASE_DIR, "DBproject.db")

def generate_custom_id(prefix, number):
    """Generate a custom ID string with a prefix and zero-padded number."""
    return f"{prefix}{str(number).zfill(4)}"

def get_next_ticket_number(conn):
    """Get the next sequential visit number from the database."""
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(CAST(SUBSTR(ID_Prescription, 3) AS INTEGER)) FROM Prescription WHERE ID_Prescription LIKE 'PR%'")
    max_num = cursor.fetchone()[0]
    return 1 if max_num is None else max_num + 1

# Window displaying a list of prescriptions.
# Shows prescriptions for a specific patient or all prescriptions by the specialist.
# Allows creating new prescriptions and exiting to the specialist dashboard.

class PrescriptionList(ctk.CTkToplevel):
    def __init__(self, parent, specialist_id, patient_id, role=None, full_name=None, patient_name=None):
        super().__init__()
        self.title("Prescriptions")
        self.geometry("700x500")
        self.state("zoomed")
        self.configure(fg_color="#E8F5E9")
        self.grab_set()  # Make this window modal to block interaction with parent

        self.parent = parent
        self.specialist_id = specialist_id
        self.role = role
        self.full_name = full_name
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

        # Patient info label if patient name is provided
        patient_info = f" for {self.patient_name}" if self.patient_name else ""
        ctk.CTkLabel(self, text=f"Prescriptions{patient_info}", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1B5E20").pack(pady=20)

        # Scrollable frame for prescriptions list
        self.list_frame = ctk.CTkScrollableFrame(self, width=600, height=350)
        self.list_frame.pack(pady=10, fill="both", expand=True)

        # Button frame for new prescription and exit buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=10)

        self.new_prescription_button = ctk.CTkButton(
            button_frame,
            text="New Prescription",
            command=self.open_new_prescription,
            fg_color="#388E3C",
            hover_color="#2E7D32"
        )
        self.new_prescription_button.grid(row=0, column=0, padx=10)

        self.exit_button = ctk.CTkButton(
            button_frame,
            text="← Exit",
            command=self.exit_to_specialist_dashboard,
            fg_color="#A5D6A7",
            hover_color="#81C784"
        )
        self.exit_button.grid(row=0, column=1, padx=10)

        # Load prescriptions from the database
        self.load_prescriptions()

        # Timestamp label bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second with current date and time."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 

    def load_prescriptions(self):
        """Load prescriptions from the database.
        If patient_id is specified, load only that patient's prescriptions.
        Otherwise, load all prescriptions by the specialist.
        Display them in the scrollable list frame with styled frames and status indicators."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        if self.patient_id:
            query = """
                SELECT ID_Prescription, Type, Title, Body, CompilationDate, CompilationTime
                FROM Prescription
                WHERE ID_Patient = ? AND ID_Specialist = ?
                ORDER BY CompilationDate DESC, CompilationTime DESC
            """
            cursor.execute(query, (self.patient_id, self.specialist_id))
        else:
            query = """
                SELECT ID_Prescription, Type, Title, Body, CompilationDate, CompilationTime, ID_Patient
                FROM Prescription
                WHERE ID_Specialist = ?
                ORDER BY CompilationDate DESC, CompilationTime DESC
            """
            cursor.execute(query, (self.specialist_id,))

        prescriptions = cursor.fetchall()
        conn.close()

        # Clear existing widgets in the list frame
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        if not prescriptions:
            ctk.CTkLabel(self.list_frame, text="No prescriptions found.", text_color="red", font=ctk.CTkFont(size=16)).pack(pady=10)
            return

        # Map prescription types to icons (example icons, adjust as needed)
        icon_map = {
            "Medication": "💊",
            "Therapy": "🩺",
            "Other": "📋"
        }

        for pres in prescriptions:
            if self.patient_id:
                p_id, p_type, title, body, cdate, ctime = pres
            else:
                p_id, p_type, title, body, cdate, ctime, p_patient_id = pres

            icon = icon_map.get(p_type, "📋")
            text = f"{icon} {cdate} {ctime} - [{p_type}] {title}: {body}"

            # Create a frame for each prescription to style it
            frame = ctk.CTkFrame(self.list_frame, fg_color="white", corner_radius=8)
            frame.pack(fill="x", pady=5, padx=5)

            # Status circle - you can customize color or logic if needed
            status_circle = ctk.CTkLabel(frame, width=20, height=20, corner_radius=10, fg_color="#81C784", text="")
            status_circle.pack(side="left", padx=10, pady=10)

            label = ctk.CTkLabel(
                frame,
                text=text,
                font=ctk.CTkFont(size=14),
                text_color="#1B5E20",
                anchor="w"
            )
            label.pack(side="left", fill="x", expand=True, pady=10)

    def open_new_prescription(self):
        """Open the new prescription form window modally.
        Hide this window while the new prescription form is open."""
        self.withdraw()
        new_presc_win = NewPrescriptionForm(self, self.specialist_id, self.patient_id, self.patient_name)
        new_presc_win.protocol("WM_DELETE_WINDOW", self.deiconify)
        new_presc_win.grab_set()  # Modal behavior

    def exit_to_specialist_dashboard(self):
        """Close this window and restore the specialist dashboard window."""
        self.grab_release()
        self.destroy()
        if self.parent:
            self.parent.deiconify()
            self.parent.after(0, lambda: self.parent.state('zoomed'))

# Window for creating a new prescription.
# Allows the specialist to enter type, title, and body of the prescription.

class NewPrescriptionForm(ctk.CTkToplevel):
    def __init__(self, parent, specialist_id, patient_id, patient_name):
        super().__init__()
        self.title("New Prescription")
        self.geometry("600x600")
        self.state("zoomed")
        self.configure(fg_color="#E8F5E9")
        self.grab_set()  # Make this window modal to block interaction with parent

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

        # Title label for new prescription
        ctk.CTkLabel(self, text="Create Prescription", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1B5E20").pack(pady=20)

        # Entry for prescription type
        self.type_entry = ctk.CTkEntry(self, placeholder_text="Type (e.g., Medication, Therapy)")
        self.type_entry.pack(pady=10, padx=20, fill="x")

        # Entry for prescription title
        self.title_entry = ctk.CTkEntry(self, placeholder_text="Title")
        self.title_entry.pack(pady=10, padx=20, fill="x")

        # Textbox for prescription body
        self.body_text = ctk.CTkTextbox(self, height=150)
        self.body_text.pack(pady=10, padx=20, fill="both")

        # Status label for feedback
        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=14))
        self.status_label.pack(pady=(5, 5))

        # Button frame for confirm and cancel
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)

        send_button = ctk.CTkButton(
            button_frame,
            text="Confirm Prescription",
            command=self.send_prescription,
            fg_color="#388E3C",
            hover_color="#2E7D32"
        )
        send_button.grid(row=0, column=0, padx=10)

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel Prescription",
            command=self.exit_form,
            fg_color="#A5D6A7",
            hover_color="#81C784"
        )
        cancel_button.grid(row=0, column=1, padx=10)

        # Timestamp label bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second with current date and time."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 

    def send_prescription(self):
        """Validate input fields and insert a new prescription record into the database.
        Provides feedback on success or error."""
        p_type = self.type_entry.get().strip()
        title = self.title_entry.get().strip()
        body = self.body_text.get("1.0", "end").strip()

        if not p_type or not title or not body:
            self.status_label.configure(text="Please fill in all fields.", text_color="red")
            return

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("SELECT IP_SS FROM SS_Middleware LIMIT 1")
            ip_ss_row = cursor.fetchone()
            ip_ss = ip_ss_row[0] if ip_ss_row else 1

            next_number = get_next_ticket_number(conn)
            code = generate_custom_id("PR", next_number)

            cursor.execute("""
                INSERT INTO Prescription (ID_Prescription, ID_Patient, ID_Specialist, IP_SS, Type, Title, Body, CompilationDate, CompilationTime)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (code, self.patient_id, self.specialist_id, ip_ss, p_type, title, body, date_str, time_str))

            conn.commit()
            conn.close()

            self.status_label.configure(text="Prescription taken in charge!", text_color="green")
            self.clear_form()
            self.after(1500, self.close_and_refresh)

        except Exception as e:
            self.status_label.configure(text="Error. Retry.", text_color="red")
            print("Error inserting prescription:", e)

    def clear_form(self):
        """Clear all input fields in the form."""
        self.type_entry.delete(0, "end")
        self.title_entry.delete(0, "end")
        self.body_text.delete("1.0", "end")

    def close_and_refresh(self):
        """Close this window, restore the parent, and refresh the prescription list."""
        self.destroy()
        self.parent.deiconify()
        self.parent.load_prescriptions()
        self.parent.state('zoomed')

    def exit_form(self):
        """Cancel the form and return to the parent window."""
        self.destroy()
        self.parent.deiconify()
        self.parent.state('zoomed')