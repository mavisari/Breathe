# This module implements the BackupMainWindow and BackupInterfaceWindow classes.
# It provides a modal interface for a technician to manage database backups.
# The technician can select existing storage or enter a new storage name for backup.
# The backup progress is simulated with a progress bar.
# Upon completion, backup records are saved and the storage list is updated.

import customtkinter as ctk
import sqlite3
import os
import random
from datetime import datetime
from PIL import Image
from customtkinter import CTkImage

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")

ip_dbms = "192168110"

# Window for technicians to manage database backups.
# Allows executing backup and opening detailed backup interface.

class BackupMainWindow(ctk.CTkToplevel):
    def __init__(self, parent, technician_id):
        super().__init__(parent)
        self.title("Database Management Interface")
        self.geometry("900x700")
        self.minsize(600, 400)
        self.configure(fg_color="#E8F5E9")
        self.parent = parent
        self.technician_id = technician_id
        self.state('zoomed')

        self.grab_set()  # Make this window modal

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=10, pady=10)

        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(side="top", fill="x")

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

        center_frame = ctk.CTkFrame(container, fg_color="transparent")
        center_frame.pack(expand=True, fill="both")

        center_frame.grid_rowconfigure(0, weight=1)  
        center_frame.grid_rowconfigure(4, weight=1)  
        center_frame.grid_columnconfigure(0, weight=1)

        label = ctk.CTkLabel(center_frame, text="Database Management Interface",
                             font=ctk.CTkFont(size=28, weight="bold"),
                             text_color="#1B5E20")
        label.grid(row=0, column=0, pady=(5, 10))

        exec_btn = ctk.CTkButton(center_frame, text="Execute Backup",
                                 fg_color="#388E3C", hover_color="#2E7D32",
                                 width=250, height=60, corner_radius=15,
                                 font=ctk.CTkFont(size=20),
                                 command=self.open_backup_interface)
        exec_btn.grid(row=2, column=0, pady=15)
        
        exit_btn = ctk.CTkButton(center_frame, text="← Exit",
                                 fg_color="#A5D6A7", hover_color="#81C784",
                                 width=250, height=60, corner_radius=15,
                                 font=ctk.CTkFont(size=20),
                                 command=self.exit_window)
        exit_btn.grid(row=3, column=0, pady=15)

        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second with current date and time."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 

    def open_backup_interface(self):
        """Open the detailed backup interface window modally."""
        self.withdraw()
        detail_window = BackupInterfaceWindow(self, technician_id=self.technician_id)
        detail_window.focus_force()

        def on_close():
            self.deiconify()
            self.lift()
        detail_window.protocol("WM_DELETE_WINDOW", lambda: (detail_window.destroy(), on_close()))

    def exit_window(self):
        """Close this window and restore the parent window."""
        self.grab_release()
        self.destroy()
        if self.parent and self.parent.winfo_exists():
            self.parent.deiconify()
            self.parent.lift()

# Window providing detailed backup options.
# Allows selecting existing storage or entering new storage name.
# Shows backup progress and updates backup records upon completion.

class BackupInterfaceWindow(ctk.CTkToplevel):
    def __init__(self, parent, technician_id):
        super().__init__(parent)
        self.title("Backup Interface")
        self.geometry("520x520")
        self.configure(fg_color="#E8F5E9")
        self.parent = parent
        self.technician_id = technician_id
        self.state('zoomed')

        self.grab_set()  # Make this window modal

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=10, pady=10)

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

        center_frame = ctk.CTkFrame(container, fg_color="transparent")
        center_frame.pack(expand=True, fill="both")

        center_frame.grid_rowconfigure(0, weight=1)    
        center_frame.grid_rowconfigure(20, weight=1)   
        center_frame.grid_columnconfigure(0, weight=1)

        row_idx = 1

        ctk.CTkLabel(center_frame, text="Backup Interface",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color="#1B5E20").grid(row=row_idx, column=0, pady=(0, 20), sticky="n")
        row_idx += 1

        ctk.CTkLabel(center_frame, text="Select Existing Storage:",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#1B5E20").grid(row=row_idx, column=0, pady=(0, 10), sticky="")
        row_idx += 1

        self.storage_var = ctk.StringVar(value="")
        self.radio_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        self.radio_frame.grid(row=row_idx, column=0, pady=(0, 20), sticky="")
        self.radio_frame.grid_columnconfigure(0, weight=1)
        self.load_storages_with_last_backup()
        row_idx += 1

        ctk.CTkLabel(center_frame, text="Or enter new storage name:",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#1B5E20").grid(row=row_idx, column=0, pady=(0, 10), sticky="n")
        row_idx += 1

        self.new_storage_entry = ctk.CTkEntry(center_frame, placeholder_text="New storage name", width=400)
        self.new_storage_entry.grid(row=row_idx, column=0, pady=(0, 20), sticky="n")
        row_idx += 1

        self.status_label = ctk.CTkLabel(center_frame, text="", font=ctk.CTkFont(size=14, weight="bold"))
        self.status_label.grid(row=row_idx, column=0, pady=(0, 10), sticky="n")
        row_idx += 1

        self.progress_bar = ctk.CTkProgressBar(center_frame, width=460, height=25, mode="determinate")
        self.progress_bar.grid(row=row_idx, column=0, pady=(0, 10), sticky="n")
        self.progress_bar.set(0)
        self.progress_bar.grid_remove()
        row_idx += 1

        btn_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        btn_frame.grid(row=row_idx, column=0, pady=15)

        self.start_btn = ctk.CTkButton(btn_frame, text="Start Backup",
                                       fg_color="#388E3C", hover_color="#2E7D32",
                                       width=140, command=self.start_backup_with_progress)
        self.start_btn.pack(side="left", padx=10)

        back_btn = ctk.CTkButton(btn_frame, text="← Go Back",
                                 fg_color="#A5D6A7", hover_color="#81C784",
                                 width=140, command=self.go_back)
        back_btn.pack(side="left", padx=10)

        self.progress_value = 0
        self.max_progress = 100

        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second with current date and time."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp)

    def load_storages_with_last_backup(self):
        """Load existing storages from the database along with their last backup timestamp.
        Populate the radio buttons for selection."""
        for widget in self.radio_frame.winfo_children():
            widget.destroy()
        try:
            with sqlite3.connect('DBproject.db') as conn:
                c = conn.cursor()
                c.execute("""
                    SELECT MIN(StorageName) AS DisplayName,
                           MAX(BackupDate || ' ' || BackupTime) AS LastBackupTimestamp
                    FROM Backup
                    WHERE StorageName IS NOT NULL AND StorageName != ''
                    GROUP BY LOWER(REPLACE(StorageName, ' ', ''))
                    ORDER BY DisplayName
                """)
                rows = c.fetchall()
        except Exception as e:
            self.show_status(f"Error loading storages: {e}", success=False)
            rows = []

        if not rows:
            self.show_status("No storages found. Please enter a new storage name.", success=False)
            return

        for storage_name, last_backup in rows:
            last_backup_str = last_backup if last_backup else "Never"
            text = f"{storage_name} (Last backup: {last_backup_str})"
            ctk.CTkRadioButton(self.radio_frame, text=text, variable=self.storage_var, value=storage_name).pack(anchor="w", pady=3)

    def start_backup_with_progress(self):
        """Start the backup process, choosing either a new or existing storage.
        Show progress bar and disable start button during backup."""
        new_storage = self.new_storage_entry.get().strip()
        selected_storage = self.storage_var.get()

        if new_storage:
            storage_name = new_storage
        elif selected_storage:
            storage_name = selected_storage
        else:
            self.show_status("Error: please select or enter a storage name.", success=False)
            return

        self.progress_bar.grid()
        self.progress_bar.set(0)
        self.progress_value = 0
        self.show_status("Backup started...", success=True)
        self.start_btn.configure(state="disabled")

        self.simulate_backup_progress(ip_dbms, storage_name)

    def simulate_backup_progress(self, ip_dbms, storage_name):
        """Simulate backup progress by incrementing progress bar periodically.
        Upon completion, insert backup record and update UI."""
        if self.progress_value < self.max_progress:
            self.progress_value += 5
            self.progress_bar.set(self.progress_value / self.max_progress)
            self.after(100, lambda: self.simulate_backup_progress(ip_dbms, storage_name))
        else:
            success = True  # Simulated success

            if success:
                self.insert_backup_record(ip_dbms, storage_name)
                self.show_status(f"Backup completed successfully on '{storage_name}'", success=True)
                self.load_storages_with_last_backup()
                self.new_storage_entry.delete(0, 'end')
            else:
                self.show_status("Error: backup went wrong. Retry", success=False)

            self.start_btn.configure(state="normal")

    def insert_backup_record(self, ip_dbms, storage_name):
        """Insert a new backup record into the database with current date/time and random size.
        Normalize storage name to avoid duplicates."""
        normalized_storage = storage_name.strip().lower().replace(" ", "")
        try:
            with sqlite3.connect('DBproject.db') as conn:
                c = conn.cursor()
                c.execute("""
                    SELECT StorageName FROM Backup
                    WHERE LOWER(REPLACE(StorageName, ' ', '')) = ?
                    LIMIT 1
                """, (normalized_storage,))
                existing = c.fetchone()
                if existing:
                    storage_name_to_use = existing[0]
                else:
                    storage_name_to_use = storage_name.strip()

                size = random.randint(50_000_000, 500_000_000)
                now = datetime.now()
                backup_date = now.strftime("%Y-%m-%d")
                backup_time = now.strftime("%H:%M:%S")
                data_bak = None

                c.execute("""
                    INSERT INTO Backup (ID_Technician, IP_DBMS, Size, BackupDate, BackupTime, Data, StorageName)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (self.technician_id, ip_dbms, size, backup_date, backup_time, data_bak, storage_name_to_use))
                conn.commit()
        except Exception as e:
            self.show_status(f"Error saving backup record: {e}", success=False)

    def show_status(self, message, success=True):
        """Display a status message with color indicating success or failure."""
        color = "#4CAF50" if success else "#F44336"
        self.status_label.configure(text=message, text_color=color)

    def go_back(self):
        """Close this window and restore the parent window."""
        self.grab_release()
        self.destroy()
        if self.parent and self.parent.winfo_exists():
            self.parent.deiconify()
            self.parent.state('zoomed')
            self.parent.lift()