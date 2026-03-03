# This code implements the section that allows a patient to connect a new device via Bluetooth.
# It includes two windows: NewDevicePrompt, which prompts the user to start connecting a new device,
# and DeviceListWindow, which simulates searching for available devices and displays them or a message if none are found.

import customtkinter as ctk
import os
from datetime import datetime
from PIL import Image
from customtkinter import CTkImage

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")

class NewDevicePrompt(ctk.CTkToplevel):
    def __init__(self, parent, user_id):
        super().__init__()
        # Initialize the new device prompt window
        self.title("New Device")
        self.geometry("400x250")
        self.configure(fg_color="#E8F5E9")
        self.parent = parent
        self.user_id = user_id
        self.state('zoomed')
        self.attributes('-topmost', True)
        self.grab_set()  # Make this window modal to block interaction with parent

        # Main container frame
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", padx=20, pady=(10, 10))  

        # Header frame with logo and title
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x", anchor="w", pady=(0, 10))

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

        # Center frame for main content
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.pack(expand=True)

        # Instruction label
        label = ctk.CTkLabel(
            center_frame,
            text="Connect a New Device",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color="#1B5E20",
            justify="center"
        )
        label.pack(pady=25)

        # Button to open the device list window
        connect_btn = ctk.CTkButton(
            center_frame,
            text="Connect New Device",
            width=200,
            height=40,
            command=self.open_device_list,
            fg_color="#388E3C",
            hover_color="#2E7D32"
        )
        connect_btn.pack(pady=10)

        # Exit button to close this window and return to parent
        exit_btn = ctk.CTkButton(
            center_frame,
            text="← Exit",
            width=200,
            height=40,
            command=self.exit_action,
            fg_color="#A5D6A7", hover_color="#81C784"
        )
        exit_btn.pack(pady=10)

        # Timestamp label at bottom-right corner, updated every second
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 

    def open_device_list(self):
        """Open the device list window modally and hide this window."""
        self.withdraw()
        self.device_window = DeviceListWindow(self, self.user_id)
        self.device_window.protocol("WM_DELETE_WINDOW", self.on_device_window_close)

    def on_device_window_close(self):
        """Handle closing of the device list window and restore this window."""
        self.device_window.destroy()
        self.deiconify()

    def exit_action(self):
        """Close this window and restore the parent window."""
        self.destroy()
        self.parent.after(0, lambda:self.parent.state('zoomed'))


class DeviceListWindow(ctk.CTkToplevel):
    def __init__(self, parent, user_id):
        super().__init__()
        # Initialize the device list window
        self.title("Available Devices")
        self.geometry("500x400")
        self.configure(fg_color="#E8F5E9")
        self.parent = parent
        self.user_id = user_id
        self.state('zoomed')
        self.attributes('-topmost', True)
        self.grab_set()  # Make this window modal to block interaction with parent

        # Main container frame
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", padx=20, pady=(10, 10))  

        # Header frame with logo and title
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x", anchor="w", pady=(0, 10))

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

        # Center frame for main content
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.pack(pady=20)

        # Title label for available devices
        title = ctk.CTkLabel(
            center_frame,
            text="Available Devices",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#1B5E20",
            justify="center"
        )
        title.pack(pady=10)

        # Frame to hold device list or progress bar
        self.device_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        self.device_frame.pack(pady=10)

        # Progress bar indicating searching for devices
        self.progress = ctk.CTkProgressBar(self.device_frame, mode="indeterminate", width=300)
        self.progress.pack(pady=30)
        self.progress.start()  

        # Label shown if no devices are found (initially hidden)
        self.no_device_label = ctk.CTkLabel(
            self.device_frame,
            text="No devices available",
            font=ctk.CTkFont(size=16),
            justify="center"
        )
        self.no_device_label.pack(pady=10)
        self.no_device_label.pack_forget()

        # After 5 seconds, show no devices message if none found
        self.after(5000, self.show_no_devices)

        # Go back button to close this window and return to previous
        go_back_btn = ctk.CTkButton(
            center_frame,
            text="← Go Back",
            width=180,
            height=35,
            command=self.go_back,
            fg_color="#A5D6A7", hover_color="#81C784"
        )
        go_back_btn.pack(pady=15)

        # Handle window close event
        self.protocol("WM_DELETE_WINDOW", self.go_back)

        # Timestamp label at bottom-right corner, updated every second
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp)     

    def show_no_devices(self):
        """Stop progress bar and show no devices label."""
        self.progress.stop()
        self.progress.pack_forget()
        self.no_device_label.pack()

    def go_back(self):
        """Close this window and restore the parent window."""
        self.destroy()
        self.parent.deiconify()
        self.parent.after(0, lambda:self.parent.state('zoomed'))