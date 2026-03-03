# This module implements the PendingRequestsCTK class.
# It provides a modal window for technicians to view and manage pending registration requests.
# The window displays a scrollable list of pending users with their details.
# Technicians can click on any user entry to open a detailed view.

import customtkinter as ctk
import sqlite3
import os
from datetime import datetime
from tkinter import messagebox
from PIL import Image
from customtkinter import CTkImage

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")

def generate_custom_id(prefix, number):
    """Generate a custom ID string by combining a prefix with a zero-padded number."""
    return f"{prefix}{str(number).zfill(4)}"

def get_next_global_number(conn):
    """Retrieve the next available global number for ID_Person from the database."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT MAX(CAST(SUBSTR(ID_Person, 2) AS INTEGER)) FROM Person
        WHERE ID_Person GLOB '[PST]*'
    """)
    max_num = cursor.fetchone()[0]
    return 1 if max_num is None else max_num + 1

# Window listing pending registration requests for patients and specialists.
# Displays user details and allows opening a detailed view of each request.

class PendingRequestsCTK(ctk.CTkToplevel):
    def __init__(self, parent, technician_id):
        super().__init__(parent)
        self.title("Pending Registration Requests")
        self.geometry("600x430")
        self.configure(fg_color="#E8F5E9")
        self.parent = parent
        self.technician_id = technician_id
        self.state('zoomed')
        self.attributes('-topmost', True)  # Keep window on top

        # Main container frame with padding
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", padx=20, pady=(10, 10))  

        # Header frame for logo and app title
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x", anchor="w", pady=(0, 10))  

        # Load and display the application logo on the top-left of the header
        logo_image = Image.open(LOGO_PATH).resize((80, 80), Image.LANCZOS)
        logo = CTkImage(light_image=logo_image, size=(80, 80))
        logo_label = ctk.CTkLabel(header_frame, image=logo, text="")
        logo_label.pack(side="left")

        # Display the application name "BREATHE" prominently next to the logo
        title_label = ctk.CTkLabel(
            header_frame,
            text="BREATHE",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#1B5E20")
        title_label.pack(side="left", padx=(100, 0))

        # Secondary container for content below header
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20, pady=20)

        # Title label for the pending requests section
        ctk.CTkLabel(container, text="Pending Registration Requests",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color="#1B5E20").pack(pady=10)

        # Scrollable frame to hold the list of pending requests
        self.scroll_frame = ctk.CTkScrollableFrame(container, width=560, height=300)
        self.scroll_frame.pack(fill="both", expand=True)

        # Frame for the exit button
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(pady=10)

        # Exit button to close this window and return to parent
        self.back_btn = ctk.CTkButton(btn_frame, text="← Exit",
                                      fg_color="#A5D6A7", hover_color="#81C784",
                                      width=180, command=self.go_back)
        self.back_btn.pack()

        # Load pending requests from database and display
        self.load_requests()

        # Timestamp label at bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second with current date and time."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 

    def load_requests(self):
        """Load pending registration requests from the database and display them in the scrollable frame.
        Each request is shown with name, email, role, and optional medical and unique codes.
        Clicking on a request opens a detailed view."""
        # Clear existing widgets in the scroll frame
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        try:
            with sqlite3.connect('DBproject.db') as conn:
                c = conn.cursor()
                c.execute("""
                    SELECT Email, Name, Surname, MedicalRegistrationCode, UniqueCode, Role
                    FROM WaitingConfirmation
                    WHERE Role IN ('Patient', 'Specialist')
                """)
                self.pending_users = c.fetchall()
        except Exception as e:
            messagebox.showerror("DB Error", f"Error loading requests: {e}", parent=self)
            self.pending_users = []

        if not self.pending_users:
            # Show message if no pending requests found
            ctk.CTkLabel(self.scroll_frame, text="No pending requests.",
                         font=ctk.CTkFont(size=14), text_color="#1B5E20").pack(pady=20)
            return

        # Create a frame for each pending user with their details
        for user in self.pending_users:
            email, name, surname, med_code, unique_code, role = user

            user_box = ctk.CTkFrame(self.scroll_frame, fg_color="#A5D6A7", corner_radius=12,
                                    border_width=1, border_color="#C8E6C9")
            user_box.pack(fill="x", padx=10, pady=5)

            # Display user's full name prominently
            ctk.CTkLabel(user_box, text=f"{name} {surname}",
                         font=ctk.CTkFont(size=16, weight="bold"),
                         text_color="#1B5E20").pack(anchor="w", padx=10, pady=(5, 0))

            # Display user's email, role, and optional codes
            details = f"Email: {email}\nRole: {role}"
            if med_code:
                details += f"\nMedical Registration Code: {med_code}"
            if unique_code:
                details += f"\nUnique Code: {unique_code}"

            ctk.CTkLabel(user_box, text=details, wraplength=600, justify="left",
                         text_color="#1B5E20").pack(anchor="w", padx=10, pady=(0, 5))

            # Bind click events on the frame and its children to open detailed user view
            user_box.bind("<Button-1>", lambda e, u=user: self.open_user_detail(u))
            for child in user_box.winfo_children():
                child.bind("<Button-1>", lambda e, u=user: self.open_user_detail(u))

    def open_user_detail(self, user_data):
        """Open a modal detailed view window for the selected pending user.
        Disables interaction with this window until detail window is closed."""
        self.attributes('-disabled', True)
        detail = UserDetailCTK(self, user_data, technician_dashboard=self)
        detail.wait_window()  # Wait until detail window is closed
        self.attributes('-disabled', False)
        self.load_requests()  # Refresh the list after detail window closes

    def go_back(self):
        """Close this window and restore the parent window."""
        self.destroy()
        if self.parent and self.parent.winfo_exists():
            self.parent.deiconify()
            self.parent.after(0, lambda: self.parent.state('zoomed'))
            self.parent.lift()

# Window showing detailed information for a pending user registration.
# Allows technician to confirm or decline the registration after reviewing details.
class UserDetailCTK(ctk.CTkToplevel):
    def __init__(self, parent, user_data, technician_dashboard):
        super().__init__(parent)
        self.user_data = user_data
        self.technician_dashboard = technician_dashboard
        self.state('zoomed')        
        self.title("User Details Review")
        self.geometry("600x450")
        self.configure(fg_color="#E8F5E9")

        self.attributes('-topmost', True)  # Keep window on top
        self.grab_set()  # Make this window modal

        # Unpack user data tuple
        email, name, surname, medico_code, unique_code, role = user_data

        # Main container frame with padding
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", padx=20, pady=(10, 10))  

        # Header frame for logo and app title
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x", anchor="w", pady=(0, 10))

        # Load and display the application logo on the top-left of the header
        logo_image = Image.open(LOGO_PATH).resize((80, 80), Image.LANCZOS)
        logo = CTkImage(light_image=logo_image, size=(80, 80))
        logo_label = ctk.CTkLabel(header_frame, image=logo, text="")
        logo_label.pack(side="left")

        # Display the application name "BREATHE" prominently next to the logo
        title_label = ctk.CTkLabel(
            header_frame,
            text="BREATHE",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#1B5E20")
        title_label.pack(side="left", padx=(100, 0))

        # Secondary container for content below header
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20, pady=20)

        # Title label for user registration review section
        ctk.CTkLabel(container, text="Review User Registration",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="#1B5E20").pack(pady=(0, 10))

        # Frame for displaying user information fields
        info_frame = ctk.CTkFrame(container, fg_color="transparent")
        info_frame.pack(pady=10, fill="x")

        # Basic user information fields
        fields = [
            ("Email:", email),
            ("Name:", name),
            ("Surname:", surname),
        ]
        
        # Additional fields depending on role
        if role == "Patient":
            # Unique code entered by patient
            fields.append(("Unique Code entered by patient:", unique_code if unique_code else "N/A"))
            # Unique code generated by doctor fetched from DB
            medico_generated_code = self.get_medico_generated_code(email)
            fields.append(("Unique Code entered by doctor:", medico_generated_code if medico_generated_code else "N/A"))
        else:
            # For specialists, show medical registration code
            fields.append(("Medical Registration Code:", medico_code if medico_code else "N/A"))

        # If patient with unique code, get associated doctor's name and ID
        medico_nome = None
        medico_id = None
        if role == "Patient" and unique_code:
            medico_nome, medico_id = self.get_medico_nome_and_id(unique_code)

        # Display all fields in the info frame
        for label_text, value in fields:
            combined_text = f"{label_text} {value}"
            ctk.CTkLabel(info_frame, text=combined_text,
                         font=ctk.CTkFont(size=14),
                         text_color="#1B5E20",
                         anchor="center",
                         justify="center").pack(fill="x", pady=3)

        # Show associated medical doctor if patient
        if role == "Patient":
            medico_text = f"Associated Medical: {medico_nome if medico_nome else 'Not found'}"
            ctk.CTkLabel(info_frame, text=medico_text,
                         font=ctk.CTkFont(size=14),
                         text_color="#1B5E20",
                         anchor="center",
                         justify="center").pack(fill="x", pady=3)

        # Verify patient's unique code validity
        if role == "Patient":
            self.code_status = self.verify_patient_code(unique_code, medico_id)
            status_text = "✔️ Valid unique code" if self.code_status else "❌ Invalid unique code"
            status_color = "#4CAF50" if self.code_status else "#F44336"
            self.status_label = ctk.CTkLabel(container, text=status_text, text_color=status_color,
                                             font=ctk.CTkFont(size=16, weight="bold"))
            self.status_label.pack(pady=10)
        else:
            self.code_status = True
            self.status_label = None

        # Frame for action buttons
        self.btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.btn_frame.pack(pady=20)

        buttons_row = ctk.CTkFrame(self.btn_frame, fg_color="transparent")
        buttons_row.pack()

        # Confirm button to approve registration
        self.confirm_btn = ctk.CTkButton(buttons_row, text="Confirm",
                                         fg_color="#388E3C", hover_color="#2E7D32",
                                         width=120, command=self.confirm_user)
        self.confirm_btn.pack(side="left", padx=10)

        # Decline button to reject registration
        self.decline_btn = ctk.CTkButton(buttons_row, text="Decline",
                                         fg_color="#388E3C", hover_color="#2E7D32",
                                         width=120, command=self.decline_user)
        self.decline_btn.pack(side="left", padx=10)

        # Back button to close this window and return
        self.back_btn = ctk.CTkButton(self.btn_frame, text="← Go Back",
                                      fg_color="#A5D6A7", hover_color="#81C784",
                                      width=120, command=self.go_back)
        self.back_btn.pack(pady=10)

        # Timestamp label bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second with current date and time."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp)

    def get_medico_generated_code(self, email):
        """Retrieve the unique code generated by the doctor associated with the patient's email.
        Returns the unique code string or None if not found."""
        try:
            with sqlite3.connect('DBproject.db') as conn:
                c = conn.cursor()
                c.execute("""
                    SELECT UniqueCode FROM AssociationUniqueCode WHERE Email = ?
                """, (email,))
                result = c.fetchone()
                return result[0] if result else None
        except Exception as e:
            messagebox.showerror("DB Error", f"Error retrieving medical code: {e}", parent=self)
            return None

    def get_medico_nome_and_id(self, unique_code):
        """Retrieve the full name and ID of the specialist associated with the given unique code.
        Returns a tuple (full_name, specialist_id) or (None, None) if not found."""
        try:
            with sqlite3.connect('DBproject.db') as conn:
                c = conn.cursor()
                c.execute("""
                    SELECT P.Name, P.Surname, S.ID_Specialist
                    FROM AssociationUniqueCode A
                    JOIN Specialist S ON A.ID_Specialist = S.ID_Specialist
                    JOIN Person P ON S.ID_Specialist = P.ID_Person
                    WHERE A.UniqueCode = ?
                """, (unique_code,))
                result = c.fetchone()
                if result:
                    return f"{result[0]} {result[1]}", result[2]
                else:
                    return None, None
        except Exception as e:
            messagebox.showerror("DB Error", f"Error retrieving associated medical: {e}", parent=self)
            return None, None

    def verify_patient_code(self, unique_code, medico_id):
        """Verify if the patient's unique code matches the doctor's unique code in the database.
        Returns True if valid, False otherwise."""
        if not medico_id:
            return False
        try:
            with sqlite3.connect('DBproject.db') as conn:
                c = conn.cursor()
                c.execute("""
                    SELECT 1 FROM AssociationUniqueCode WHERE UniqueCode = ? AND ID_Specialist = ?
                """, (unique_code, medico_id))
                return c.fetchone() is not None
        except Exception as e:
            messagebox.showerror("DB Error", f"Error verifying unique code: {e}", parent=self)
            return False

    def confirm_user(self):
        """Confirm the user's registration after validation.
        Inserts the user into the Person table and related tables depending on role.
        Removes the user from WaitingConfirmation and sends a notification."""
        # Prevent confirmation if patient code is invalid
        if self.user_data[5] == "Patient" and not self.code_status:
            messagebox.showwarning("Invalid Code", "Cannot confirm profile with invalid unique code.", parent=self)
            return

        email, name, surname, medico_code, unique_code, role = self.user_data

        prefix_map = {'Patient': 'P', 'Specialist': 'S'}
        prefix = prefix_map.get(role)
        if not prefix:
            messagebox.showerror("Error", "Invalid role.", parent=self)
            return

        try:
            with sqlite3.connect('DBproject.db') as conn:
                c = conn.cursor()
                next_num = get_next_global_number(conn)
                user_id = generate_custom_id(prefix, next_num)

                # Retrieve full user data from waiting list
                c.execute("SELECT * FROM WaitingConfirmation WHERE Email=?", (email,))
                full_user_data = c.fetchone()
                if not full_user_data:
                    messagebox.showerror("Error", "User data not found.", parent=self)
                    self.destroy()
                    self.technician_dashboard.deiconify()
                    return

                # Prepare data tuple for Person insertion
                person_data = (
                    user_id,                   # ID_Person
                    full_user_data[1],         # Name
                    full_user_data[2],         # Surname
                    full_user_data[3],         # Birthplace
                    full_user_data[4],         # Birthdate
                    full_user_data[5],         # Street
                    full_user_data[6],         # City
                    full_user_data[7],         # ZIP 
                    full_user_data[8],         # TaxCode
                    full_user_data[0],         # Email
                    full_user_data[9],         # Password
                    full_user_data[10],        # Telephone
                    full_user_data[11],        # Role
                )

                # Insert into Person table
                c.execute('''INSERT INTO Person 
                    (ID_Person, Name, Surname, Birthplace, Birthdate, Street, City, ZIP, TaxCode, Email, Password, Telephone, Role) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', person_data)
                
                # Insert into Patient or Specialist table depending on role
                if role == "Patient":
                    c.execute("SELECT ID_Specialist FROM AssociationUniqueCode WHERE Email = ?", (email,))
                    specialist_row = c.fetchone()
                    id_specialist = specialist_row[0] if specialist_row else None

                    allergy = full_user_data[15] if full_user_data[15] else ""

                    c.execute('''INSERT INTO Patient (ID_Patient, ID_Specialist, Weight, Height, EmergencyContactNumber, Allergy) 
                                VALUES (?, ?, ?, ?, ?, ?)''',
                            (user_id, id_specialist, full_user_data[12], full_user_data[13], full_user_data[14], allergy))
                else:
                    c.execute('''INSERT INTO Specialist (ID_Specialist, MedicalRegistrationCode) 
                        VALUES (?, ?)''',
                        (user_id, full_user_data[17]))
                
                # Remove user from waiting list
                c.execute("DELETE FROM WaitingConfirmation WHERE Email=?", (email,))

                # Insert notification about successful registration
                c.execute('''INSERT INTO Notification (ID_Person, Title, Body, CompilationDate, CompilationTime)
                    VALUES (?, ?, ?, DATE('now'), TIME('now'))''',
                    (user_id, "Registration Confirmed", "Your account has been successfully activated!"))

                conn.commit()

                self.show_final_message(f"Profile for {name} has been successfully confirmed.\nA notification has been sent to the user.", success=True)

        except Exception as e:
            messagebox.showerror("DB Error", f"Error during confirmation: {e}", parent=self)

    def decline_user(self):
        """Decline the user's registration request.
        Removes the user from the waiting list and informs the technician."""
        email = self.user_data[0]
        try:
            with sqlite3.connect('DBproject.db') as conn:
                c = conn.cursor()
                c.execute("DELETE FROM WaitingConfirmation WHERE Email=?", (email,))
                conn.commit()

            self.show_final_message("Profile has been declined and removed from requests.\nAn email has been sent to the user.", success=False)

        except Exception as e:
            messagebox.showerror("DB Error", f"Error during decline: {e}", parent=self)

    def show_final_message(self, message, success=True):
        """Display a final status message after confirmation or decline.
        Hides confirm and decline buttons and shows the message in appropriate color."""
        self.confirm_btn.pack_forget()
        self.decline_btn.pack_forget()

        if self.status_label:
            self.status_label.destroy()

        color = "#4CAF50" if success else "#F44336"
        self.status_label = ctk.CTkLabel(self.btn_frame, text=message, text_color=color,
                                         font=ctk.CTkFont(size=16, weight="bold"), justify="center")
        self.status_label.pack(pady=10)

    def go_back(self):
        """Close this window and restore the technician dashboard window."""
        self.destroy()
        if self.technician_dashboard and self.technician_dashboard.winfo_exists():
            self.technician_dashboard.deiconify()
            self.technician_dashboard.after(0, lambda: self.technician_dashboard.state('zoomed'))
            self.technician_dashboard.lift()