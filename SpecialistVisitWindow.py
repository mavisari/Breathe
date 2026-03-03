# This module implements the PatientVisitsWindow class.
# It provides a modal window listing all visits related to a specific patient.
# The specialist can book new visits, reschedule existing ones, or delete visits.
# When a visit is deleted, a notification is sent to the patient.
# The visit list updates automatically after any changes.

import customtkinter as ctk
import sqlite3
import os
from datetime import datetime
from tkinter import messagebox
from PIL import Image
from customtkinter import CTkImage

from BookVisit import CalendarWindow
from RescheduleVisit import RescheduleVisitWindow

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")

# Window for specialists to manage patient visits.
# Allows viewing scheduled visits, rescheduling, deleting, and booking new visits.

class PatientVisitsWindow(ctk.CTkToplevel):
    
    def __init__(self, master=None, specialist_id=None, patient_id=None):
        super().__init__(master)
        self.master = master
        self.specialist_id = specialist_id
        self.patient_id = patient_id
        self.title("Patient Visits")
        self.configure(fg_color="#E8F5E9")

        self.grab_set()  # Make this window modal to block interaction with parent
        self.fullscreen()

        self.selected_visit = None  # Store currently selected visit

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

        # Center frame containing visits list and controls
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.pack(expand=True, padx=40, pady=40)

        # Scrollable frame for visits list
        self.scroll_frame = ctk.CTkScrollableFrame(self.center_frame, width=800, height=400)
        self.scroll_frame.pack(pady=20)

        # Label to display error or success messages
        self.error_label = ctk.CTkLabel(self.center_frame, text="", text_color="red", font=("Arial", 14, "bold"))
        self.error_label.pack(pady=(0, 10))

        # Frame for action buttons arranged horizontally
        self.buttons_row_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.buttons_row_frame.pack(pady=10)

        self.reschedule_button = ctk.CTkButton(
            self.buttons_row_frame, text="Reschedule Visit", command=self.open_reschedule,
            fg_color="#388E3C", hover_color="#2E7D32", height=40, width=250, font=("Arial", 14)
        )
        self.reschedule_button.grid(row=0, column=0, padx=10)

        self.delete_button = ctk.CTkButton(
            self.buttons_row_frame, text="Delete Visit", command=self.open_delete_visit,
            fg_color="#388E3C", hover_color="#2E7D32", height=40, width=250, font=("Arial", 14)
        )
        self.delete_button.grid(row=0, column=1, padx=10)

        self.new_visit_button = ctk.CTkButton(
            self.buttons_row_frame, text="New Visit", command=self.open_calendar,
            fg_color="#388E3C", hover_color="#2E7D32", height=40, width=250, font=("Arial", 14)
        )
        self.new_visit_button.grid(row=0, column=2, padx=10)

        # Exit button centered below
        self.exit_button = ctk.CTkButton(
            self.center_frame, text="← Exit", command=self.close_window,
            fg_color="#A5D6A7", hover_color="#81C784", height=40, width=250, font=("Arial", 14)
        )
        self.exit_button.pack(pady=(20, 10))

        # Load visits from database and populate list
        self.load_visits()

        # Timestamp label bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second with current date and time."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 

    def fullscreen(self):
        """Set the window size to full screen based on the current screen resolution."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")

    def load_visits(self):
        """Load all visits of the patient from the database and display them as buttons in the scrollable frame.
        Clears previous widgets and highlights the selected visit."""
        # Clear existing visit buttons/widgets
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.scroll_frame.configure(fg_color="white")

        # Connect to database and fetch visits for the patient
        conn = sqlite3.connect("DBproject.db")
        cursor = conn.cursor()

        cursor.execute("""SELECT ID_Visit, VisitDate, VisitTime, Place, Type 
                       FROM Visit 
                       WHERE ID_Patient = ?
                       ORDER BY VisitDate ASC, VisitTime ASC""", (self.patient_id,))
        visits = cursor.fetchall()
        conn.close()

        self.visits_data = visits
        self.visit_buttons = []

        if not visits:
            # Show message if no visits found
            label = ctk.CTkLabel(self.scroll_frame, text="No previous visits found.", font=("Arial", 16), text_color="black")
            label.pack(pady=10)
        else:
            # Create a button for each visit
            for idx, visit in enumerate(visits):
                visit_id, date, time, place, vtype = visit
                text = f"{date} at {time} — {place} — {vtype}"

                is_past = self.is_past_visit(date)

                if is_past:
                    fg_color = "#D3D3D3"       # gray for past visits
                    hover_color = "#A9A9A9"
                    text_color = "black"
                else:
                    fg_color = "#A5D6A7"       # green for upcoming visits
                    hover_color = "#81C784"
                    text_color = "black"

                button = ctk.CTkButton(
                    self.scroll_frame,
                    text=text,
                    font=("Arial", 16),
                    width=750,
                    fg_color=fg_color,
                    hover_color=hover_color,
                    text_color=text_color,
                    anchor="w",
                    command=lambda v=visit, b_idx=idx: self.select_visit(v, b_idx)
                )
                button.pack(pady=5)
                self.visit_buttons.append(button)

    def select_visit(self, visit, index):
        """Handle selection of a visit.
        Highlights the selected visit button and clears any error messages."""
        self.selected_visit = visit
        self.error_label.configure(text="")

        # Reset all buttons to default color
        for btn in self.visit_buttons:
            btn.configure(fg_color="#A5D6A7", hover_color="#81C784")

        # Highlight the selected button
        self.visit_buttons[index].configure(fg_color="#388E3C", hover_color="#2E7D32")

    def open_reschedule(self):
        """Open the reschedule visit window for the selected visit.
        Validates that a visit is selected and that it is not in the past."""
        if self.selected_visit is None:
            self.error_label.configure(text="No visit has been selected", text_color="red")
            return

        visit_id, visit_date, visit_time, _, _ = self.selected_visit

        if self.is_past_visit(visit_date):
            self.error_label.configure(text="Cannot reschedule a past visit.", text_color="red")
            return

        self.withdraw()
        RescheduleVisitWindow(self, visit_id, visit_date, visit_time, self.reschedule_callback, self)

    def reschedule_callback(self, visit_id, new_date, new_time):
        """Callback function to update the visit date and time in the database after rescheduling.
        Reloads the visit list and shows success or error messages."""
        try:
            conn = sqlite3.connect("DBproject.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE Visit SET VisitDate=?, VisitTime=? WHERE ID_Visit=?", (new_date, new_time, visit_id))
            conn.commit()
            conn.close()

            self.load_visits()
            self.deiconify()
            self.fullscreen()
            self.error_label.configure(text="Rescheduled successfully", text_color="green")
            return True
        except Exception as e:
            print("Error:", e)
            self.error_label.configure(text=f"Error rescheduling visit: {e}", text_color="red")
            return False

    def open_delete_visit(self):
        """Delete the selected visit after confirmation.
        Validates selection and that the visit is not in the past.
        Sends a notification to the patient upon successful deletion."""
        if self.selected_visit is None:
            self.error_label.configure(text="No visit has been selected", text_color="red")
            return

        visit_id, visit_date, _, _, _ = self.selected_visit

        if self.is_past_visit(visit_date):
            self.error_label.configure(text="Cannot delete a past visit.", text_color="red")
            return

        answer = messagebox.askyesno("Delete Visit", "Are you sure you want to delete the selected visit?")
        if answer:
            try:
                conn = sqlite3.connect("DBproject.db")
                cursor = conn.cursor()

                # Retrieve visit info for notification message
                cursor.execute("SELECT VisitDate, VisitTime, Place FROM Visit WHERE ID_Visit = ?", (visit_id,))
                visit_data = cursor.fetchone()
                if not visit_data:
                    conn.close()
                    self.error_label.configure(text="Visit not found in database.", text_color="red")
                    return

                visit_date, visit_time, place = visit_data

                # Delete the visit
                cursor.execute("DELETE FROM Visit WHERE ID_Visit = ?", (visit_id,))

                # Insert cancellation notification for patient
                ns_version = "v1.0"
                ns_type = "Usual"
                notif_title = "Visit Cancelled"
                notif_body = f"Your visit on {visit_date} at {visit_time} in {place} has been cancelled."
                compilation_date = datetime.now().strftime("%Y-%m-%d")
                compilation_time = datetime.now().strftime("%H:%M:%S")

                cursor.execute("""
                    INSERT INTO Notification 
                    (ID_Person, NS_Version, NS_Type, Type, Title, Body, CompilationDate, CompilationTime, IsRead, ID_Visit)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
                """, (
                    self.patient_id,
                    ns_version,
                    ns_type,
                    "Calendar",  # notification type
                    notif_title,
                    notif_body,
                    compilation_date,
                    compilation_time,
                    visit_id
                ))

                conn.commit()
                conn.close()

                self.error_label.configure(text="Visit deleted successfully.", text_color="green")
                self.selected_visit = None
                self.load_visits()
            except Exception as e:
                self.error_label.configure(text=f"Error deleting visit: {e}", text_color="red")

    def is_past_visit(self, visit_date_str):
        """Check if the given visit date string (YYYY-MM-DD) is in the past compared to today."""
        try:
            visit_date = datetime.strptime(visit_date_str, "%Y-%m-%d").date()
            today = datetime.today().date()
            return visit_date < today
        except Exception as e:
            print(f"Error parsing date: {e}")
            return False

    def open_calendar(self):
        """Open the calendar window to book a new visit modally."""
        self.withdraw()
        CalendarWindow(self, self.specialist_id, self.patient_id)

    def close_window(self):
        """Close this window and restore the parent window."""
        self.grab_release()
        self.destroy()
        if self.master:
            self.master.deiconify()
            if hasattr(self.master, "fullscreen") and callable(self.master.fullscreen):
                self.master.fullscreen()
            else:
                try:
                    self.master.state("zoomed")
                except Exception:
                    pass