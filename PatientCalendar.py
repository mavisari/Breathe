# This code implements the Patient Calendar page where the patient can view a calendar highlighting the current day and days with scheduled visits.
# Selecting a date with visits displays detailed information about those visits.
# The patient can request to reschedule or delete visits, with notifications sent to the associated specialist.
import customtkinter as ctk
import sqlite3
import os
from tkinter import messagebox
from datetime import datetime
from tkcalendar import Calendar
from tkinter import ttk
from PIL import Image
from customtkinter import CTkImage

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")
DB_PATH = "DBproject.db"

class PatientCalendar(ctk.CTkToplevel):
    def __init__(self, parent, user_id, role, full_name, id_visit=None):
        super().__init__()
        # Initialize window properties and store user info
        self.title("Visit Calendar")
        self.geometry("1000x650")
        self.configure(fg_color="#E8F5E9")
        self.parent = parent
        self.user_id = user_id
        self.role = role
        self.full_name = full_name
        self.id_visit = id_visit
        self.state('zoomed')

        # Make this window modal to block interaction with parent window
        self.grab_set()

        # Main container frame
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

        # Secondary container for role label and main content
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", padx=20, pady=(20, 20))

        # Display user role and full name
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

        # Content frame inside main frame for calendar and visit list
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Frame for calendar widget on left
        calendar_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        calendar_frame.pack(side="left", padx=(0, 20), fill="y")

        # Calendar widget with day selection and date pattern
        self.calendar = Calendar(calendar_frame, selectmode="day", date_pattern="yyyy-mm-dd", width=12, height=10)
        self.calendar.pack(pady=10)
        # Bind calendar selection event to update visit list
        self.calendar.bind("<<CalendarSelected>>", self.show_visits_for_date)

        # Frame for visit list table on right
        table_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        table_frame.pack(side="left", fill="both", expand=True)

        # Treeview widget to display visits with columns
        self.tree = ttk.Treeview(table_frame, columns=("Type", "Place", "Time", "Annotation"), show="headings", height=10)

        # Style configuration for treeview fonts
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 14))  # Row font
        style.configure("Treeview.Heading", font=("Arial", 16, "bold"))  # Header font

        # Setup treeview columns headers and alignment
        for col in ("Type", "Place", "Time", "Annotation"):
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=120, anchor="center", stretch=True)

        self.tree.pack(fill="both", expand=True)

        # Frame for action buttons (reschedule, delete)
        buttons_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        buttons_frame.pack(side="left", pady=20)

        # Reschedule visit button (initially hidden)
        self.reschedule_btn = ctk.CTkButton(buttons_frame, text="Reschedule visit", fg_color="#388E3C", hover_color="#2E7D32", text_color="white", 
                                            command=self.show_reschedule_message)
        # Delete visit button (initially hidden)
        self.delete_btn = ctk.CTkButton(buttons_frame, text="Delete visit", fg_color="#388E3C", hover_color="#2E7D32", text_color="white",
                                command=self.delete_visit)

        self.reschedule_btn.pack_forget()
        self.delete_btn.pack_forget()

        # Label for messages to user (status, errors)
        self.message_label = ctk.CTkLabel(container, text="", font=ctk.CTkFont(size=14), text_color="#1B5E20")
        self.message_label.pack(pady=5)

        # Exit button to close calendar and return
        self.exit_btn = ctk.CTkButton(container, text="← Exit", fg_color="#A5D6A7", hover_color="#81C784", text_color="white", command=self.go_back)
        self.exit_btn.pack(pady=10)

        # Load all visits from database and mark calendar
        self.load_all_visits()

        # Timestamp label at bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 

    def get_specialist_id_from_visit(self, date, time):
        """Retrieve the specialist ID associated with a specific visit."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ID_Specialist FROM Visit 
                WHERE ID_Patient = ? AND VisitDate = ? AND VisitTime = ?
            """, (self.user_id, date, time))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except Exception as e:
            print(f"Error retrieving specialist: {e}")
            return None

    def load_all_visits(self):
        """Load all visits for the patient and mark them on the calendar."""
        self.visits = {}
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Type, Place, VisitDate, VisitTime, Annotation
                FROM Visit WHERE ID_Patient = ?
            """, (self.user_id,))
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                type_, place, date, time_, annotation = row
                visit = (type_, place, time_, annotation)
                if date not in self.visits:
                    self.visits[date] = []
                self.visits[date].append(visit)

                try:
                    date_obj = datetime.strptime(date, "%Y-%m-%d").date()
                    self.calendar.calevent_create(date_obj, "Visit", tags="booked")
                except ValueError:
                    print(f"Invalid date format for: {date}")

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load visits: {str(e)}")

    def show_visits_for_date(self, event):
        """Display visits scheduled on the selected date in the treeview."""
        selected_date = self.calendar.get_date()
        self.tree.delete(*self.tree.get_children())

        visits = self.visits.get(selected_date, [])
        if not visits:
            self.tree.insert("", "end", values=("No visits", "", "", ""))
            self.reschedule_btn.pack_forget()
            self.delete_btn.pack_forget()
        else:
            for visit in visits:
                self.tree.insert("", "end", values=visit)
            self.reschedule_btn.pack(side="top", pady=5)
            self.delete_btn.pack(side="top", pady=5)

    def show_reschedule_message(self):
        """Send a reschedule request notification to the specialist."""
        selected_item = self.tree.selection()
        if selected_item:
            visit = self.tree.item(selected_item)["values"]
            visit_time = visit[2]
            visit_date = self.calendar.get_date()

            specialist_id = self.get_specialist_id_from_visit(visit_date, visit_time)
            if not specialist_id:
                self.message_label.configure(text="Unable to notify specialist.", text_color="red")
                return

            # Insert notification into the database
            ns_version = "v1.0"
            ns_type = "Usual"
            notif_title = "Patient Request: Reschedule Visit"
            notif_body = f"The patient {self.full_name} requests to reschedule the visit on {visit_date} at {visit_time}."
            compilation_date = datetime.now().strftime("%Y-%m-%d")
            compilation_time = datetime.now().strftime("%H:%M:%S")

            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Notification 
                    (ID_Person, NS_Version, NS_Type, Type, Title, Body, CompilationDate, CompilationTime, IsRead, ID_Visit)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, NULL)
                """, (specialist_id, ns_version, ns_type, "Calendar", notif_title, notif_body, compilation_date, compilation_time))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Error inserting reschedule notification: {e}")

            self.message_label.configure(text="Reschedule request sent to the specialist.", text_color="green")
        else:
            self.message_label.configure(text="Please select a visit to reschedule.", text_color="red")

    def delete_visit(self):
        """Delete the selected visit and notify the specialist."""
        selected_item = self.tree.selection()
        if selected_item:
            visit = self.tree.item(selected_item)["values"]
            visit_time = visit[2]
            visit_date = self.calendar.get_date()

            specialist_id = self.get_specialist_id_from_visit(visit_date, visit_time)

            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM Visit
                    WHERE ID_Patient = ? AND VisitDate = ? AND VisitTime = ?
                """, (self.user_id, visit_date, visit_time))
                conn.commit()
                conn.close()

                self.tree.delete(selected_item)
                self.message_label.configure(text="Visit deleted successfully.", text_color="green")

                # Send notification to specialist about cancellation
                if specialist_id:
                    ns_version = "v1.0"
                    ns_type = "Usual"
                    notif_title = "Visit Cancelled by Patient"
                    notif_body = f"The patient {self.full_name} cancelled the visit on {visit_date} at {visit_time}."
                    compilation_date = datetime.now().strftime("%Y-%m-%d")
                    compilation_time = datetime.now().strftime("%H:%M:%S")

                    try:
                        conn = sqlite3.connect(DB_PATH)
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO Notification 
                            (ID_Person, NS_Version, NS_Type, Type, Title, Body, CompilationDate, CompilationTime, IsRead, ID_Visit)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, NULL)
                        """, (specialist_id, ns_version, ns_type, "Calendar", notif_title, notif_body, compilation_date, compilation_time))
                        conn.commit()
                        conn.close()
                    except Exception as e:
                        print(f"Error inserting cancellation notification: {e}")

                # Update visits dictionary and calendar UI
                if visit_date in self.visits:
                    self.visits[visit_date] = [v for v in self.visits[visit_date] if v[2] != visit_time]
                    if not self.visits[visit_date]:
                        del self.visits[visit_date]
                        date_obj = datetime.strptime(visit_date, "%Y-%m-%d").date()
                        self.calendar.calevent_remove(date=date_obj, tag="booked")

                self.show_visits_for_date(None)

            except Exception as e:
                self.message_label.configure(text=f"Failed to delete visit: {str(e)}", text_color="red")
        else:
            self.message_label.configure(text="Please select a visit to delete.", text_color="red")

    def go_back(self):
        """Close this window and restore the parent window."""
        self.destroy()
        if self.parent:
            self.parent.deiconify()
            self.parent.after(0, lambda: self.parent.state('zoomed'))