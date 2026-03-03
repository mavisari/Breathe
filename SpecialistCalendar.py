# This module implements the specialist's calendar window.
# It provides a read-only view of all scheduled visits with various patients.
# The specialist can see the dates with visits marked on the calendar and view visit details for the selected date.

import customtkinter as ctk
import sqlite3
import os
from datetime import datetime
from tkinter import messagebox
from tkcalendar import Calendar
from tkinter import ttk
from PIL import Image
from customtkinter import CTkImage

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")
DB_PATH = "DBproject.db"

# Window representing the specialist's visit calendar.
# Displays all visits scheduled with patients.
# Allows viewing visit details by selecting dates on the calendar.

class SpecialistCalendar(ctk.CTkToplevel):
    def __init__(self, parent, user_id, role, full_name, id_visit=None):
        super().__init__()
        self.title("Visit Calendar")
        self.geometry("1000x650")
        self.configure(fg_color="#E8F5E9")
        self.parent = parent
        self.user_id = user_id
        self.role = role
        self.full_name = full_name
        self.id_visit = id_visit
        self.state('zoomed')
        self.attributes('-topmost', True)
        self.grab_set()  # Make this window modal to block interaction with parent

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

        # Container for role and name label and main content
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20, pady=20)

        # Display role and full name of the specialist
        role_label = ctk.CTkLabel(
            container,
            text=f"{self.role}: {self.full_name}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1B5E20"
        )
        role_label.pack(pady=(10, 0), anchor="center")

        # Main frame with white background and rounded corners
        main_frame = ctk.CTkFrame(container, fg_color="white", corner_radius=10)
        main_frame.pack(padx=10, pady=20, fill="both", expand=True)

        # Content frame inside main frame
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Left frame for calendar widget
        calendar_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        calendar_frame.pack(side="left", padx=(0, 20), fill="y")

        # Calendar widget allowing day selection with date pattern YYYY-MM-DD
        self.calendar = Calendar(calendar_frame, selectmode="day", date_pattern="yyyy-mm-dd", width=12, height=10)
        self.calendar.pack(pady=10)
        self.calendar.bind("<<CalendarSelected>>", self.show_visits_for_date)

        # Right frame for visit details table
        table_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        table_frame.pack(side="left", fill="both", expand=True)

        # Treeview widget to display visit details with columns
        self.tree = ttk.Treeview(table_frame, columns=("Patient", "Type", "Place", "Time", "Annotation"), show="headings", height=10)

        # Style configuration for the treeview and headings
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 14)) 
        style.configure("Treeview.Heading", font=("Arial", 16, "bold"))  

        # Define columns with headings and widths
        for col in ("Patient", "Type", "Place", "Time", "Annotation"):
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=120, anchor="center", stretch=True)

        self.tree.pack(fill="both", expand=True)

        # Exit button to close calendar and return to parent
        self.exit_btn = ctk.CTkButton(container, text="← Exit", fg_color="#A5D6A7", hover_color="#81C784", text_color="white", command=self.go_back)
        self.exit_btn.pack(pady=10)

        # Load all visits from database and mark them on calendar
        self.load_all_visits()

        # Timestamp label bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second with current date and time."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 

    def load_all_visits(self):
        """Load all visits for the specialist from the database.
        Store visits in a dictionary keyed by date.
        Mark dates with visits on the calendar.
        If a visit ID is specified, select its date on the calendar."""
        self.visits = {}
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT V.ID_Visit, V.Type, V.Place, V.VisitDate, V.VisitTime, V.Annotation, P.Name, P.Surname
                FROM Visit V
                JOIN Person P ON V.ID_Patient = P.ID_Person
                WHERE V.ID_Specialist = ?
            """, (self.user_id,))
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                visit_id, type_, place, date, time_, annotation, patient_name, patient_surname = row
                visit = {
                    "id": visit_id,
                    "data": (f"{patient_name} {patient_surname}", type_, place, time_, annotation)
                }

                if date not in self.visits:
                    self.visits[date] = []
                self.visits[date].append(visit)

                # Mark the date on the calendar as booked
                try:
                    date_obj = datetime.strptime(date, "%Y-%m-%d").date()
                    self.calendar.calevent_create(date_obj, "Visit", tags="booked")
                except ValueError:
                    print(f"Invalid date format for: {date}")

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load visits: {str(e)}")
        
        # If a visit ID was passed, select the corresponding date on the calendar and show visits
        if self.id_visit:
            for date_str, visits in self.visits.items():
                for visit in visits:
                    if visit["id"] == self.id_visit:
                        try:
                            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                            self.calendar.selection_set(date_obj)
                            self.show_visits_for_date(None)
                            return
                        except Exception as e:
                            print(f"Error selecting visit: {e}")

    def show_visits_for_date(self, event):
        """Display all visits scheduled on the selected date in the treeview.
        If no visits exist, display a placeholder message."""
        selected_date = self.calendar.get_date()
        self.tree.delete(*self.tree.get_children())

        visits = self.visits.get(selected_date, [])
        if not visits:
            self.tree.insert("", "end", values=("No visits", "", "", "", ""))
        else:
            for visit in visits:
                self.tree.insert("", "end", values=visit["data"])

    def go_back(self):
        """Close this calendar window and restore the parent window."""
        self.grab_release()
        self.destroy()
        if self.parent:
            self.parent.deiconify()
            self.parent.after(0, lambda: self.parent.state('zoomed'))