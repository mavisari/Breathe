# This module implements the notifications screen where the specialist receives their notifications.
# Notifications can be of three types:
# - Calendar: when the patient requests to reschedule or cancel an appointment.
# - Assistance: when a ticket is resolved by the technician.
# - Contact: when the specialist receives a message from a patient.
# Clicking on a notification redirects the specialist to the related page.

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
DB_PATH = os.path.join(BASE_DIR, "DBproject.db")

# Window to visualize specialist notifications.
# Displays system notifications and recent chat messages.
# Clicking a notification marks it as read and redirects to the related page.

class SpecialistNotifications(ctk.CTkToplevel):
    def __init__(self, parent=None, user_id=None):
        super().__init__(parent)
        self.state('zoomed')
        self.title("Visualize Notifications")
        self.geometry("600x500")
        self.configure(fg_color="#E8F5E9")
        self.user_id = user_id
        self.master = parent 

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
        
        # Section title
        ctk.CTkLabel(self, text="Notifications", font=ctk.CTkFont(size=32, weight="bold"), text_color="#1B5E20").pack(pady=30)

        # Scrollable frame for notifications list
        self.notifications_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.notifications_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Load notifications from the database and populate the UI
        self.notifications = self.load_notifications_from_db()
        self.populate_notifications()

        # Exit button to close the window
        exit_btn = ctk.CTkButton(
            self,
            text="← Exit",
            command=self.close,
            width=120,
            fg_color="#A5D6A7",
            hover_color="#81C784",
            text_color="white"
        )
        exit_btn.pack(pady=15)

        # Timestamp label at bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

        self.grab_set()  # Make this window modal to block interaction with parent

    def update_timestamp(self):
        """Update the timestamp label every second."""
        if not self.winfo_exists():
            return
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp)

    def load_notifications_from_db(self):
        """Load notifications and recent chat messages from the database for the current specialist.
        Returns a list of notification dictionaries sorted by date and time descending."""
        notifications = []
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            # Load system notifications for the specialist ordered by most recent
            c.execute("""
                SELECT Type, Title, Body, CompilationDate, CompilationTime, IsRead, ID_Visit
                FROM Notification 
                WHERE ID_Person = ?
                ORDER BY CompilationDate DESC, CompilationTime DESC
            """, (self.user_id,))
            rows = c.fetchall()
            for row in rows:
                notif_type, title, body, date, time, is_read, id_visit = row

                # Ignore any unhandled types (if any)
                if notif_type not in ("Calendar", "Contact", "Assistance"):
                    continue

                # Custom icons for types
                icon_map = {
                    "Calendar": "📅",
                    "Contact": "📞",
                    "Assistance": "🛠️"
                }
                icon = icon_map.get(notif_type, "")

                notifications.append({
                    "id": None,
                    "type": notif_type,
                    "title": title,
                    "body": body,
                    "text": f"{icon} {title}: {body}",
                    "is_read": bool(is_read),
                    "date": date,
                    "time": time,
                    "id_visit": id_visit
                })

            # Load last 20 chat messages received
            c.execute("""
                SELECT 
                    cm.ID_Message, 
                    cm.SenderID, 
                    p.Name, 
                    p.Surname,
                    cm.MessageBody, 
                    cm.CompilationDate, 
                    cm.CompilationTime,
                    cm.IsRead
                FROM ChatMessages cm
                LEFT JOIN Person p ON cm.SenderID = p.ID_Person
                WHERE cm.ReceiverID = ? AND cm.ID_Message LIKE "MP%"
                ORDER BY cm.CompilationDate DESC, cm.CompilationTime DESC
                LIMIT 20
            """, (self.user_id,))

            chat_rows = c.fetchall()
            for chat_row in chat_rows:
                msg_id, sender_id, name, surname, msg_body, date, time, is_read = chat_row
                sender_name = f"{name} {surname}" if name and surname else sender_id

                notifications.append({
                    "id": msg_id,
                    "type": "Contact",
                    "title": f"Message from {sender_name}",
                    "body": msg_body,
                    "text": f"💬 {sender_name}: {msg_body[:50]}{'...' if len(msg_body) > 50 else ''}",
                    "is_read": bool(is_read),
                    "date": date,
                    "time": time,
                })

            # Sort notifications by date and time descending (most recent first)
            notifications.sort(key=lambda x: (x["date"], x["time"]), reverse=True)
            conn.close()
        except Exception as e:
            print(f"Error loading notifications and messages: {e}")
            notifications = []
        return notifications

    def populate_notifications(self):
        """Populate the notifications frame with notification items.
        If no notifications exist, display a message indicating none are available."""
        if not self.notifications:
            ctk.CTkLabel(
                self.notifications_frame, 
                text="No notifications or messages available", 
                text_color="gray",
                font=ctk.CTkFont(size=16)
            ).pack(pady=20)
            return
            
        for notif in self.notifications:
            self.add_notification_item(notif)

        # Automatically scroll to the bottom of the notifications list
        self.after(100, lambda: self.notifications_frame._parent_canvas.yview_moveto(1))

    def add_notification_item(self, notif):
        """Add a single notification item to the notifications frame.
        Displays a colored circle indicating read/unread status and the notification text.
        Clicking the notification triggers the related action."""
        frame = ctk.CTkFrame(self.notifications_frame, fg_color="white", corner_radius=8)
        frame.pack(fill="x", pady=5, padx=5)

        # Red color for unread, green for read
        status_color = "#FF6B6B" if not notif["is_read"] else "#81C784"
        status_circle = ctk.CTkLabel(frame, width=20, height=20, corner_radius=10, fg_color=status_color, text="")
        status_circle.pack(side="left", padx=10, pady=10)

        label = ctk.CTkLabel(
            frame,
            text=notif["text"],
            font=ctk.CTkFont(size=14, weight="bold" if not notif["is_read"] else "normal"),
            text_color="#1B5E20",
            anchor="w"
        )
        label.pack(side="left", fill="x", expand=True, pady=10)

        # Bind click event on label to handle notification action
        label._label.bind("<Button-1>", lambda e, t=notif, s=status_circle: self.on_notification_click(t, s))

    def mark_notification_as_read(self, notification):
        """Mark the given notification as read in the database."""
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()

            if notification["type"] == "Contact":
                c.execute("""
                    UPDATE ChatMessages
                    SET IsRead = 1
                    WHERE ID_Message = ?
                """, (notification["id"],))
            else:
                c.execute("""
                    UPDATE Notification 
                    SET IsRead = 1 
                    WHERE ID_Person = ? AND CompilationDate = ? AND CompilationTime = ?
                """, (self.user_id, notification["date"], notification["time"]))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating notification status: {e}")

    def on_notification_click(self, notification, status_circle):
        """Handle click on a notification:
        - Mark it as read if unread.
        - Redirect to the related page if available.
        - Close this window shortly after."""
        if not notification["is_read"]:
            self.mark_notification_as_read(notification)
            status_circle.configure(fg_color="#81C784")
            notification["is_read"] = True

        if self.master:
            if notification["type"] == "Calendar" and hasattr(self.master, "open_specialist_calendar"):
                self.master.open_specialist_calendar()
            elif notification["type"] == "Contact" and hasattr(self.master, "open_contact_patient"):
                self.master.open_contact_patient()
            elif notification["type"] == "Assistance" and hasattr(self.master, "open_assistance"):
                self.master.open_assistance()
            else:
                print(f"No handler for notification type: {notification['type']} or method missing.")
        else:
            print("Master is None, cannot redirect.")

        # Close the window after 100ms to allow visual updates
        self.after(100, self.destroy)

    def close(self):
        """Close this window and restore the parent window."""
        self.grab_release()
        self.destroy()
        if self.master:
            self.master.deiconify()
            self.master.state('normal')
            width = self.master.winfo_screenwidth()
            height = self.master.winfo_screenheight()
            self.master.geometry(f"{width}x{height}+0+0")