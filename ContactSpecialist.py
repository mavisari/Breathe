# This module implements the ContactSpecialist class.
# It provides a modal window for a patient to contact their assigned specialist via chat.
# The window displays the specialist's name and options to start chat or exit.
# The chat history is fetched from the database and displayed in a styled UI.

import customtkinter as ctk
import sqlite3
import os
from datetime import datetime
from tkinter import messagebox
from PIL import Image
from customtkinter import CTkImage

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")

def generate_custom_id(prefix, number):
    """Generate a custom ID string by combining a prefix with a zero-padded number."""
    return f"{prefix}{str(number).zfill(4)}"

def get_next_message_number(cursor):
    """Retrieve the next available message number for chat messages.
    It finds the maximum numeric suffix of IDs starting with 'MP' and increments it."""
    cursor.execute("SELECT MAX(CAST(SUBSTR(ID_Message, 3) AS INTEGER)) FROM ChatMessages WHERE ID_Message LIKE 'MP%'")
    max_num = cursor.fetchone()[0]
    return 0 if max_num is None else max_num + 1

# Window for patient to contact their specialist.
# Shows specialist's name and options to start chat or exit.

class ContactSpecialist(ctk.CTkToplevel):
    def __init__(self, parent, patient_id):
        super().__init__(parent)
        self.title("Contact Specialist")
        self.geometry("1000x700")
        self.configure(fg_color="#E8F5E9")
        self.parent = parent
        self.patient_id = patient_id

        # Main container frame with padding
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", padx=20, pady=(10, 10))

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

        # Establish database connection and cursor
        self.conn = sqlite3.connect('DBproject.db')
        self.cursor = self.conn.cursor()

        # Retrieve the specialist ID assigned to this patient
        self.cursor.execute("SELECT ID_Specialist FROM Patient WHERE ID_Patient = ?", (self.patient_id,))
        result = self.cursor.fetchone()
        if not result:
            messagebox.showerror("Error", "Specialist not found for this patient.")
            self.destroy()
            return

        self.specialist_id = result[0]

        # Retrieve specialist's full name
        self.cursor.execute("SELECT Name, Surname FROM Person WHERE ID_Person = ?", (self.specialist_id,))
        spec_info = self.cursor.fetchone()
        self.specialist_name = f"{spec_info[0]} {spec_info[1]}" if spec_info else "Specialist"

        self.state('zoomed')
        self.attributes('-topmost', True)  # Keep window on top
        self.grab_set()  # Make this window modal

        # Main frame for content below header
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)

        self.status_label = None  # Placeholder for status messages

        # Create main UI options (chat button and exit)
        self.create_main_options()

        # Timestamp label bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second with current date and time."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 

    def clear_frame(self):
        """Remove all widgets from the main frame."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def create_main_options(self):
        """Create main UI options: a button to contact via chat and an exit button."""
        self.clear_frame()

        center_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        center_frame.pack(expand=True)

        # Title label showing specialist name
        title_label = ctk.CTkLabel(center_frame,
                                   text=f"Contact {self.specialist_name}",
                                   font=ctk.CTkFont(size=24, weight="bold"),
                                   text_color="#1B5E20")
        title_label.pack(pady=(20, 20))

        # Style dictionaries for buttons
        button_style_green = {
            "width": 160, "height": 50,
            "corner_radius": 15,
            "font": ctk.CTkFont(size=16),
            "fg_color": "#388E3C", "hover_color": "#2E7D32"
        }

        button_style_back = {
            "width": 160, "height": 50,
            "corner_radius": 15,
            "font": ctk.CTkFont(size=16),
            "fg_color": "#A5D6A7", "hover_color": "#81C784"
        }

        # Button to open chat UI
        chat_button = ctk.CTkButton(center_frame, text="Contact via Chat",
                                    command=self.show_chat_ui, **button_style_green)
        chat_button.pack(pady=15)

        # Exit button to close window
        exit_button = ctk.CTkButton(center_frame, text="← Exit",
                                    command=self.exit, **button_style_back)
        exit_button.pack(pady=15)

    def get_previous_messages(self):
        """Retrieve all previous chat messages exchanged between the patient and specialist,
        ordered chronologically by date and time. Returns a list of tuples: (SenderID, CompilationDate, CompilationTime, MessageBody)."""
        try:
            self.cursor.execute("""
                SELECT SenderID, CompilationDate, CompilationTime, MessageBody
                FROM ChatMessages
                WHERE (SenderID = ? AND ReceiverID = ?) OR (SenderID = ? AND ReceiverID = ?)
                ORDER BY CompilationDate ASC, CompilationTime ASC
            """, (self.patient_id, self.specialist_id, self.specialist_id, self.patient_id))
            return self.cursor.fetchall()
        except Exception as e:
            print("Error retrieving messages:", e)
            return []
        
    def show_chat_ui(self):
        """Display the chat interface with previous messages and input controls.
        Messages are styled differently depending on sender (patient vs specialist)."""
        self.clear_frame()

        # Frame to hold chat content
        chat_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        chat_frame.pack(fill="both", expand=True)

        # Title label with specialist name
        title_label = ctk.CTkLabel(chat_frame,
                                   text=f"Chat with {self.specialist_name}",
                                   font=ctk.CTkFont(size=24, weight="bold"),
                                   text_color="#1B5E20")
        title_label.pack(pady=(20, 10))

        # Scrollable frame for messages
        messages_frame = ctk.CTkScrollableFrame(chat_frame, height=400, fg_color="white")
        messages_frame.pack(fill="x", expand=False, padx=20, pady=(0, 10))

        # Fetch previous messages from database
        previous_messages = self.get_previous_messages()
        if previous_messages:
            for sender_id, date, time, body in previous_messages:
                is_patient = sender_id == self.patient_id
                sender_name = "Me" if is_patient else self.specialist_name
                align = "e" if is_patient else "w"  # Right align patient messages
                anchor = "e" if is_patient else "w"
                text_color = "#1B5E20" if is_patient else "#424242"
                bg_color = "#C8E6C9" if is_patient else "#F0F0F0"
                info = f"{sender_name}, {date} {time}"

                # Container frame for each message bubble
                container = ctk.CTkFrame(messages_frame, fg_color=bg_color)
                container.pack(anchor=anchor, fill="none", padx=10, pady=5)

                # Message text label
                msg_label = ctk.CTkLabel(container, text=body, wraplength=500, justify="left",
                                         font=ctk.CTkFont(size=14), text_color=text_color)
                msg_label.pack(anchor=align, padx=10, pady=2)

                # Info label with sender and timestamp
                info_label = ctk.CTkLabel(container, text=info, font=ctk.CTkFont(size=10), text_color="gray")
                info_label.pack(anchor=align, padx=10, pady=(0, 5))
        else:
            # Show message if no previous messages exist
            empty_label = ctk.CTkLabel(messages_frame, text="No previous messages.", text_color="gray")
            empty_label.pack(pady=10)

        # Entry box for typing new message
        self.message_entry = ctk.CTkEntry(chat_frame, height=40, font=ctk.CTkFont(size=16))
        self.message_entry.pack(fill="x", padx=20, pady=10)

        # Status label for feedback messages
        self.status_label = ctk.CTkLabel(chat_frame, text="", font=ctk.CTkFont(size=14), text_color="red")
        self.status_label.pack(pady=(0, 5))

        # Container for send and cancel buttons
        button_container = ctk.CTkFrame(chat_frame, fg_color="transparent")
        button_container.pack(pady=10)

        # Button styles
        button_style_green = {
            "width": 160, "height": 50,
            "corner_radius": 15,
            "font": ctk.CTkFont(size=16),
            "fg_color": "#388E3C", "hover_color": "#2E7D32"
        }

        button_style_back = {
            "width": 160, "height": 50,
            "corner_radius": 15,
            "font": ctk.CTkFont(size=16),
            "fg_color": "#A5D6A7", "hover_color": "#81C784"
        }

        # Send message button
        send_button = ctk.CTkButton(button_container, text="Send Message",
                                    command=self.send_message, **button_style_green)
        send_button.grid(row=0, column=0, padx=10)

        # Cancel message button to return to main options
        cancel_button = ctk.CTkButton(button_container, text="Cancel Message",
                                      command=self.create_main_options, **button_style_back)
        cancel_button.grid(row=0, column=1, padx=10)

    def send_message(self):
        """Send the message typed by the patient to the specialist.
        Saves the message in the database and refreshes the chat UI."""
        message = self.message_entry.get().strip()
        if not message:
            self.status_label.configure(text="Please write a message before sending.", text_color="red")
            return

        try:
            self.notify_specialist(message)
            self.status_label.configure(text="Message sent successfully!", text_color="green")
            self.message_entry.delete(0, "end")
            # Refresh chat UI after a short delay to show the new message
            self.after(1500, self.show_chat_ui)
        except Exception:
            self.status_label.configure(text="Error: message not sent. Retry", text_color="red")

    def notify_specialist(self, message):
        """Insert the new chat message into the database.
        Generates a unique message ID and stores sender, receiver, message, date, and time."""
        conn = sqlite3.connect('DBproject.db')
        c = conn.cursor()

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        next_number = get_next_message_number(c)
        message_id = generate_custom_id("MP", next_number)

        try:
            c.execute("""
                INSERT INTO ChatMessages (ID_Message, SenderID, ReceiverID, MessageBody, CompilationDate, CompilationTime)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (message_id, self.patient_id, self.specialist_id, message, date_str, time_str))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def exit(self):
        """Close this chat window, close DB connection, and restore the parent window."""
        self.conn.close()
        self.destroy()
        self.parent.deiconify()
        self.parent.after(0, lambda: self.parent.state('zoomed'))