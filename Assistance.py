# This code implements a ticket assistance system GUI where the user can view the status of their open tickets,
# including any replies from technicians. The user can also create new assistance tickets by writing specific messages.
# These functionalities are implemented in two main windows: AssistanceWindow, which displays the list of tickets and their details,
# and NewTicketWindow, which provides a form for creating and submitting new tickets.

import customtkinter as ctk
import sqlite3
import os
from datetime import datetime
from PIL import Image
from customtkinter import CTkImage


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")

def generate_custom_id(prefix, number):
    """Generate a custom ticket code with a prefix and zero-padded number."""
    return f"{prefix}{str(number).zfill(4)}"

def get_next_ticket_number(conn):
    """Retrieve the next ticket number by finding the max existing ticket code."""
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(CAST(SUBSTR(Code, 3) AS INTEGER)) FROM Ticket WHERE Code LIKE 'TK%'")
    max_num = cursor.fetchone()[0]
    return 1 if max_num is None else max_num + 1

class AssistanceWindow(ctk.CTkToplevel):
    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.title("Assistance")
        self.geometry("600x500")
        self.configure(fg_color="#E8F5E9")
        self.user_id = user_id
        self.parent = parent
        self.attributes('-topmost', True)
        self.grab_set()  # Make this window modal (block interaction with parent)
        self.state('zoomed')

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", padx=20, pady=(10, 10))
        
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x")

        # Load and display logo image
        logo_image = Image.open(LOGO_PATH).resize((80, 80), Image.LANCZOS)
        logo = CTkImage(light_image=logo_image, size=(80, 80))
        logo_label = ctk.CTkLabel(header_frame, image=logo, text="")
        logo_label.pack(side="left")

        # Title label "BREATHE"
        title_label = ctk.CTkLabel(
            header_frame,
            text="BREATHE",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#1B5E20")
        title_label.pack(side="left", padx=(100, 0))

        # Main window title
        ctk.CTkLabel(self, text="Assistance", font=ctk.CTkFont(size=28, weight="bold"), text_color="#1B5E20").pack(pady=20)

        # Scrollable frame to list tickets
        self.ticket_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.ticket_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Button frame with New Ticket and Exit buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=15, anchor="center")

        ctk.CTkButton(button_frame, text="New Ticket", command=self.open_new_ticket,
                      fg_color="#388E3C", hover_color="#2E7D32", width=150).pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="← Exit", command=self.go_back,
                      fg_color="#A5D6A7", hover_color="#81C784", width=150).pack(side="left", padx=10)

        # Timestamp label at bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()
        
        self.load_tickets()

    def update_timestamp(self):
        """Update the timestamp label every second."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 

    def load_tickets(self):
        """Load tickets from the database and display them in the scrollable frame."""
        # Clear previous ticket widgets
        for widget in self.ticket_frame.winfo_children():
            widget.destroy()

        conn = sqlite3.connect("DBproject.db")
        c = conn.cursor()
        
        # Select tickets for the current user ordered by date descending
        c.execute("""SELECT Code, Title, Body, CompilationDate, CompilationTime, Type, IsReplied, Reply, ReplyDate, ReplyTime 
                    FROM Ticket WHERE ID_Person = ?
                    ORDER BY CompilationDate DESC""", (self.user_id,))
        tickets = c.fetchall()

        for ticket in tickets:
            code, title, body, date, time, type_, is_replied, reply, reply_date, reply_time = ticket

            # Light green if not replied, light gray if replied
            ticket_color = "#A5D6A7" if is_replied == 0 else "#E0E0E0"

            ticket_box = ctk.CTkFrame(self.ticket_frame, fg_color=ticket_color, corner_radius=12, border_width=1, border_color="#C8E6C9")
            ticket_box.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(ticket_box, text=f"{title}", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=10, pady=(5, 0))
            ctk.CTkLabel(ticket_box, text=f"{body}", wraplength=600, justify="left").pack(anchor="w", padx=10, pady=(0, 5))
            ctk.CTkLabel(ticket_box, text=f"Sent on {date} at {time} | Type: {type_}", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10)

            # Show technician's reply if present
            if is_replied == 1 and reply:
                response_frame = ctk.CTkFrame(ticket_box, fg_color="#F5F5F5", corner_radius=8)
                response_frame.pack(fill="x", padx=10, pady=10, ipadx=5, ipady=5)

                ctk.CTkLabel(response_frame,
                             text="Technician's Answer:",
                             font=ctk.CTkFont(size=12, weight="bold"),
                             text_color="#757575").pack(anchor="w", padx=10, pady=(5, 0))

                ctk.CTkLabel(response_frame,
                             text=reply,
                             wraplength=580,
                             justify="left").pack(anchor="w", padx=10, pady=(0, 5))

                if reply_date and reply_time:
                    ctk.CTkLabel(response_frame,
                                 text=f"Answer on {reply_date} at {reply_time}",
                                 font=ctk.CTkFont(size=12),
                                 text_color="#9E9E9E").pack(anchor="w", padx=10)

        conn.close()

    def open_new_ticket(self):
        """Open the NewTicketWindow as a modal dialog."""
        NewTicketWindow(self, user_id=self.user_id)

    def go_back(self):
        """Close this window and restore the parent window."""
        self.destroy()
        if self.parent:
            self.parent.deiconify()
            self.parent.state('normal')
            self.parent.geometry(f"{self.parent.winfo_screenwidth()}x{self.parent.winfo_screenheight()}+0+0")
            self.parent.after(0, lambda: self.parent.state('zoomed'))

class NewTicketWindow(ctk.CTkToplevel):
    def __init__(self, parent=None, user_id=None):
        super().__init__(parent)
        self.title("New Ticket")
        self.geometry("500x500")
        self.configure(fg_color="#E8F5E9")
        self.user_id = user_id
        self.parent = parent    
        self.attributes('-topmost', True)
        self.grab_set()  # Make this window modal (block interaction with parent)
        self.state('zoomed')

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", padx=20, pady=(10, 10))

        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x")

        # Load and display logo image
        logo_image = Image.open(LOGO_PATH).resize((80, 80), Image.LANCZOS)
        logo = CTkImage(light_image=logo_image, size=(80, 80))
        logo_label = ctk.CTkLabel(header_frame, image=logo, text="")
        logo_label.pack(side="left")

        # Title label "BREATHE"
        title_label = ctk.CTkLabel(
            header_frame,
            text="BREATHE",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#1B5E20")
        title_label.pack(side="left", padx=(100, 0))

        # Window title
        ctk.CTkLabel(self, text="Create New Ticket", font=ctk.CTkFont(size=22, weight="bold"), text_color="#1B5E20").pack(pady=(20, 10))

        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.pack(expand=True)

        # Entry for ticket title
        self.title_entry = ctk.CTkEntry(center_frame, placeholder_text="Ticket Title", width=400)
        self.title_entry.pack(pady=10)

        # Textbox for ticket body with placeholder text
        self.placeholder_text = "Describe your issue here..."
        self.body_entry = ctk.CTkTextbox(center_frame, width=400, height=100)
        self.body_entry.insert("1.0", self.placeholder_text)
        self.body_entry.configure(text_color="gray")
        self.body_entry.pack(pady=10)

        # Bind focus events to handle placeholder text
        self.body_entry.bind("<FocusIn>", self.clear_placeholder)
        self.body_entry.bind("<FocusOut>", self.restore_placeholder)

        # Dropdown menu for ticket type
        ctk.CTkLabel(center_frame, text="Type", text_color="#1B5E20", font=ctk.CTkFont(size=14)).pack(pady=(10, 5))
        self.type_menu = ctk.CTkOptionMenu(center_frame, values=["Assistance", "App", "Device"],
                                           fg_color="#388E3C", button_color="#388E3C", button_hover_color="#2E7D32")
        self.type_menu.set("Assistance")
        self.type_menu.pack(pady=5)

        # Frame for buttons
        self.button_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        self.button_frame.pack(pady=20)

        # Send and Cancel buttons
        self.send_button = ctk.CTkButton(self.button_frame, text="Send Ticket", command=self.submit_ticket,
                                         fg_color="#388E3C", hover_color="#2E7D32", width=150)
        self.send_button.pack(side="left", padx=10)

        self.cancel_button = ctk.CTkButton(self.button_frame, text="Cancel Ticket", command=self.cancel_ticket,
                                           fg_color="#A5D6A7", hover_color="#81C784", width=150)
        self.cancel_button.pack(side="left", padx=10)
       
        self.go_back_button = None  # Initially hidden

        # Timestamp label at bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

        # Warning label for error messages, initially hidden
        self.warning_label = ctk.CTkLabel(
            self, 
            text="", 
            text_color="red", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.warning_label.pack(pady=10)
        self.warning_label.pack_forget()

        # Success label for confirmation messages, initially hidden
        self.success_label = ctk.CTkLabel(
            self,
            text="",
            text_color="green",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.success_label.pack(pady=10)
        self.success_label.pack_forget()

    def update_timestamp(self):
        """Update the timestamp label every second."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp)

    def submit_ticket(self):
        """Validate input and submit the new ticket to the database."""
        title = self.title_entry.get().strip()
        body = self.body_entry.get("1.0", "end").strip()
        type_ = self.type_menu.get()

        # Check if title or body is empty or if body is placeholder text
        if not title or not body or body == self.placeholder_text:
            self.show_warning("Please fill in all fields.")
            self.hide_success()
            return
        else:
            self.hide_warning()

        # Insert new ticket into the database
        conn = sqlite3.connect("DBproject.db")
        c = conn.cursor()

        now = datetime.now()
        date = now.date().isoformat()
        time = now.time().strftime("%H:%M:%S")

        next_number = get_next_ticket_number(conn)
        code = generate_custom_id("TK", next_number)

        c.execute("""INSERT INTO Ticket (Code, ID_Person, Title, Body, CompilationDate, CompilationTime, Type)
                     VALUES (?, ?, ?, ?, ?, ?, ?)""", (code, self.user_id, title, body, date, time, type_))
        conn.commit()
        conn.close()

        self.show_success("Ticket sent correctly")

        # Disable send and cancel buttons after submission
        self.send_button.configure(state="disabled")
        self.cancel_button.configure(state="disabled")

        # Show the "Go Back" button to return to assistance window
        if not self.go_back_button:
            self.go_back_button = ctk.CTkButton(self, text="← Go Back", fg_color="#A5D6A7", hover_color="#81C784",
                                                command=self.go_back_to_assistance, width=200)
            self.go_back_button.pack(pady=5)

    def clear_placeholder(self, event):
        """Clear placeholder text when textbox gains focus."""
        current_text = self.body_entry.get("1.0", "end").strip()
        if current_text == self.placeholder_text:
            self.body_entry.delete("1.0", "end")
            self.body_entry.configure(text_color="black")

    def restore_placeholder(self, event):
        """Restore placeholder text if textbox is empty on losing focus."""
        current_text = self.body_entry.get("1.0", "end").strip()
        if not current_text:
            self.body_entry.insert("1.0", self.placeholder_text)
            self.body_entry.configure(text_color="gray")
        elif current_text == self.placeholder_text:
            self.body_entry.configure(text_color="gray")

    def cancel_ticket(self):
        """Cancel ticket creation and close this window."""
        self.destroy()
        if self.parent:
            self.parent.after(0, lambda: self.parent.state('zoomed'))

    def go_back_to_assistance(self):
        """Reload tickets in parent window and close this window."""
        if self.parent:
            self.parent.load_tickets()
        self.destroy()

    def show_warning(self, text):
        """Display a warning message."""
        self.warning_label.configure(text=text)
        self.warning_label.pack(pady=10)

    def hide_warning(self):
        """Hide the warning message."""
        self.warning_label.pack_forget()

    def show_success(self, text):
        """Display a success message."""
        self.success_label.configure(text=text)
        self.success_label.pack(pady=10)

    def hide_success(self):
        """Hide the success message."""
        self.success_label.pack_forget()