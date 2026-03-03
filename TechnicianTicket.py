# This module implements the TicketsWindow class.
# It provides a modal window for technicians to view and manage pending tickets.
# The window displays a scrollable list of tickets that have not yet been replied to.
# Clicking on a ticket opens a detailed view of that ticket.

import customtkinter as ctk
import sqlite3
import os
from datetime import datetime
from tkinter import messagebox
from PIL import Image
from customtkinter import CTkImage

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")

# Window listing all pending tickets for technician review.
# Allows opening detailed views of individual tickets.

class TicketsWindow(ctk.CTkToplevel):
    def __init__(self, parent, technician_id):
        super().__init__(parent)
        self.title("Pending Tickets")
        self.geometry("600x450")
        self.configure(fg_color="#E8F5E9")
        self.parent = parent
        self.technician_id = technician_id
        self.state('zoomed')
        self.attributes('-topmost', True)  # Keep window on top

        # Main container frame with padding
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20, pady=20)

        # Header frame for logo and app title
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x")

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

        # Title label for the tickets section
        ctk.CTkLabel(container, text="Pending Tickets",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color="#1B5E20").pack(pady=10)

        # Scrollable frame to hold the list of tickets
        self.scroll_frame = ctk.CTkScrollableFrame(container, width=560, height=320)
        self.scroll_frame.pack(fill="both", expand=True)

        # Frame for exit button
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(pady=10)

        # Exit button to close this window and return to parent
        exit_btn = ctk.CTkButton(btn_frame, text="← Exit",
                                 fg_color="#A5D6A7", hover_color="#81C784",
                                 width=120, command=self.exit_window)
        exit_btn.pack()

        # Load tickets from database and display
        self.load_tickets()

        # Timestamp label bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second with current date and time."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp)

    def load_tickets(self):
        """Load all pending tickets (not replied) from the database and display them as clickable frames."""
        # Clear existing ticket widgets
        for w in self.scroll_frame.winfo_children():
            w.destroy()

        try:
            with sqlite3.connect('DBproject.db') as conn:
                c = conn.cursor()
                c.execute("""
                    SELECT Code, Title, Body, CompilationDate, CompilationTime, Type, ID_Person, IsReplied, Reply, ReplyDate, ReplyTime
                    FROM Ticket
                    WHERE IsReplied = 0
                    ORDER BY CompilationDate, CompilationTime
                """)
                self.tickets = c.fetchall()
        except Exception as e:
            # On error, clear tickets list and optionally log or show error
            self.tickets = []

        if not self.tickets:
            # Show message if no pending tickets found
            ctk.CTkLabel(self.scroll_frame, text="No pending tickets.",
                         font=ctk.CTkFont(size=14), text_color="#1B5E20").pack(pady=20)
            return

        # For each ticket, create a frame with details and bind click event
        for ticket in self.tickets:
            (code, title, body, date, time, ticket_type, sender_id,
             is_replied, reply, reply_date, reply_time) = ticket

            # Light green background color for unreplied tickets
            ticket_color = "#A5D6A7"

            ticket_box = ctk.CTkFrame(self.scroll_frame, fg_color=ticket_color, corner_radius=12,
                                      border_width=1, border_color="#C8E6C9")
            ticket_box.pack(fill="x", padx=10, pady=5)

            # Ticket title label
            ctk.CTkLabel(ticket_box, text=title,
                         font=ctk.CTkFont(size=16, weight="bold"),
                         text_color="#1B5E20").pack(anchor="w", padx=10, pady=(5, 0))

            # Ticket body label with wrapping
            ctk.CTkLabel(ticket_box, text=body,
                         wraplength=600, justify="left").pack(anchor="w", padx=10, pady=(0, 5))

            # Ticket date, time and type info label
            ctk.CTkLabel(ticket_box, text=f"Sent on {date} at {time} | Type: {ticket_type}",
                         font=ctk.CTkFont(size=12),
                         text_color="#1B5E20").pack(anchor="w", padx=10)

            # Bind click events on the frame and its children to open detailed ticket view
            ticket_box.bind("<Button-1>", lambda e, c=code: self.open_ticket_detail(c))
            for child in ticket_box.winfo_children():
                child.bind("<Button-1>", lambda e, c=code: self.open_ticket_detail(c))

    def open_ticket_detail(self, ticket_code):
        """Open a modal detailed view window for the selected ticket.
        Disables interaction with this window until detail window is closed."""
        detail_window = TicketDetailWindow(self, ticket_code)
        detail_window.grab_set()  # Make detail window modal

        def on_close():
            detail_window.destroy()
            self.load_tickets()  # Refresh list after detail window closes
            self.lift()

        detail_window.protocol("WM_DELETE_WINDOW", on_close)

    def exit_window(self):
        """Close this window and restore the parent window."""
        self.destroy()
        if self.parent and self.parent.winfo_exists():
            self.parent.deiconify()
            self.parent.lift()

# Window showing detailed information of a ticket and allowing response.

class TicketDetailWindow(ctk.CTkToplevel):
    def __init__(self, parent, ticket_code):
        super().__init__(parent)
        self.title("Ticket Detail")
        self.geometry("600x500")
        self.configure(fg_color="#E8F5E9")
        self.parent = parent
        self.ticket_code = ticket_code
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

        # Content container frame
        content_container = ctk.CTkFrame(self, fg_color="transparent")
        content_container.pack(expand=True, fill="both", padx=20, pady=20)

        # Section title
        ctk.CTkLabel(content_container, text="Ticket Detail",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="#1B5E20").pack(pady=(0,10))

        # Label showing sender info and ticket type
        self.user_info_label = ctk.CTkLabel(content_container, text="", font=ctk.CTkFont(size=14, weight="bold"),
                                            text_color="#1B5E20", justify="left")
        self.user_info_label.pack(anchor="w", pady=(0,5))

        # Label showing ticket title
        self.title_label = ctk.CTkLabel(content_container, text="", font=ctk.CTkFont(size=17, weight="bold"),
                                        text_color="#1B5E20", wraplength=560, justify="left")
        self.title_label.pack(anchor="w", pady=(0,10))

        # Frame for ticket content text box
        content_frame = ctk.CTkFrame(content_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=False, pady=5)

        ctk.CTkLabel(content_frame, text="Content:", font=ctk.CTkFont(size=14, weight="bold"), text_color="#1B5E20").pack(anchor="w")
        self.content_text = ctk.CTkTextbox(content_frame, height=70, width=550)
        self.content_text.pack(fill="x")
        self.content_text.configure(state="disabled")  # Read-only

        # Label and textbox for technician's response
        ctk.CTkLabel(content_container, text="Your Response:", font=ctk.CTkFont(size=14, weight="bold"), text_color="#1B5E20").pack(anchor="w", pady=(10,0))
        self.answer_text = ctk.CTkTextbox(content_container, height=70, width=550)
        self.answer_text.pack(fill="both", expand=True)

        # Frame for buttons
        self.btn_frame = ctk.CTkFrame(content_container, fg_color="transparent")
        self.btn_frame.pack(pady=5)

        # Confirm button to submit response
        self.confirm_btn = ctk.CTkButton(self.btn_frame, text="Confirm",
                                         fg_color="#388E3C", hover_color="#2E7D32",
                                         width=120, command=self.confirm_response)
        self.confirm_btn.pack(side="left", padx=10)

        # Back button to close window
        self.back_btn = ctk.CTkButton(self.btn_frame, text="← Go Back",
                                      fg_color="#A5D6A7", hover_color="#81C784",
                                      width=120, command=self.close_window)
        self.back_btn.pack(side="left", padx=10)

        self.status_label = None

        # Timestamp label bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

        # Load ticket data from database
        self.load_ticket_data()

    def update_timestamp(self):
        """Update the timestamp label every second with current date and time."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp)

    def load_ticket_data(self):
        """Load ticket details from the database and populate the UI fields."""
        try:
            with sqlite3.connect('DBproject.db') as conn:
                c = conn.cursor()
                c.execute("""
                    SELECT t.ID_Person, p.Name, p.Surname, t.Title, t.Body, t.Type
                    FROM Ticket t
                    LEFT JOIN Person p ON t.ID_Person = p.ID_Person
                    WHERE t.Code = ?
                """, (self.ticket_code,))
                row = c.fetchone()
                if row:
                    user_id, user_name, user_surname, title, body, ticket_type = row
                    self.user_info_label.configure(text=f"From: {user_name} {user_surname} - Type: {ticket_type}")
                    self.title_label.configure(text=f"Title: {title}")
                    self.content_text.configure(state="normal")
                    self.content_text.delete("0.0", "end")
                    self.content_text.insert("0.0", body)
                    self.content_text.configure(state="disabled")
                else:
                    messagebox.showerror("Error", "Ticket not found.", parent=self)
                    self.close_window()
        except Exception as e:
            messagebox.showerror("DB Error", f"Error loading ticket data: {e}", parent=self)
            self.close_window()

    def confirm_response(self):
        """Save the technician's response to the ticket and send notification."""
        response = self.answer_text.get("0.0", "end").strip()
        if not response:
            self.show_status_message("Please enter a response before confirming.", success=False)
            return

        try:
            with sqlite3.connect('DBproject.db') as conn:
                c = conn.cursor()
                c.execute("SELECT ID_Person FROM Ticket WHERE Code = ?", (self.ticket_code,))
                row = c.fetchone()
                if not row:
                    self.show_status_message("Error: Ticket not found.", success=False)
                    return
                sender_id = row[0]

                now_date = datetime.now().strftime("%Y-%m-%d")
                now_time = datetime.now().strftime("%H:%M:%S")

                # Update ticket with response and mark as replied
                c.execute("""
                        UPDATE Ticket
                        SET IsReplied = 1,
                            Reply = ?,
                            ReplyDate = ?,
                            ReplyTime = ?
                        WHERE Code = ?
                """, (response, now_date, now_time, self.ticket_code))

                # Retrieve notification system version and type
                c.execute("SELECT Version, Type FROM NotificationSystem LIMIT 1")
                ns_row = c.fetchone()
                ns_version, ns_type = ns_row if ns_row else (None, None)

                # Insert notification for the ticket sender
                c.execute("""
                    INSERT INTO Notification (ID_Person, NS_Version, NS_Type, Type, Title, Body, CompilationDate, CompilationTime)
                    VALUES (?, ?, ?, ?, ?, ?, DATE('now'), TIME('now'))
                """, (sender_id, ns_version, ns_type, "Assistance", "Ticket Response", response))

                conn.commit()

            self.confirm_btn.configure(state="disabled")
            self.show_status_message("Ticket resolved and notification sent.", success=True)
        except Exception as e:
            self.show_status_message(f"Error: {e}", success=False)

    def show_status_message(self, message, success=True):
        """Display a status message below the response textbox.
        Green for success, red for error."""
        if self.status_label:
            self.status_label.destroy()

        color = "#4CAF50" if success else "#F44336"
        self.status_label = ctk.CTkLabel(self.answer_text.master, text=message, text_color=color,
                                         font=ctk.CTkFont(size=14, weight="bold"), justify="center")
        self.status_label.pack(pady=(10, 5))

    def go_back(self):
        """Close this window and return to the parent window."""
        self.close_window()

    def close_window(self):
        """Destroy this window and refresh the parent window's tickets list."""
        self.destroy()
        if self.parent and self.parent.winfo_exists():
            self.parent.state('zoomed')  # Ensure parent window is maximized
            self.parent.load_tickets()   # Refresh tickets list
            self.parent.lift()            # Bring parent window to front