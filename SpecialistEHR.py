# This module implements the Electronic Health Record (EHR) window for a patient.
# It simulates loading EHR data with a progress bar, then displays a main menu with options.
# The actual connection to the Italian healthcare system via SS-Middleware is not implemented here.

import customtkinter as ctk
import os
from datetime import datetime
from PIL import Image
from customtkinter import CTkImage

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# Window displaying the Electronic Health Record interface.
# Shows a loading screen initially, then a main menu with options.

class EHRWindow(ctk.CTkToplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.title("Electronic Health Record")
        self.geometry("1000x700")
        self.configure(fg_color="#E8F5E9")
        self.state('zoomed')
        self.grab_set()  # Make this window modal to block interaction with parent

        # Build fixed header with logo and title
        self.build_header()

        # Container for main content area
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(fill="both", expand=True, padx=20, pady=20)

        # Show loading screen initially
        self.show_loading_screen()

        # Timestamp label bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second with current date and time."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 

    def build_header(self):
        """Build the fixed header with logo and application title."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(10, 0))

        logo_image = Image.open(LOGO_PATH).resize((80, 80), Image.LANCZOS)
        logo = CTkImage(light_image=logo_image, size=(80, 80))
        logo_label = ctk.CTkLabel(header, image=logo, text="")
        logo_label.pack(side="left")

        title_label = ctk.CTkLabel(
            header,
            text="BREATHE",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#1B5E20"
        )
        title_label.pack(side="left", padx=(100, 0))

    def show_loading_screen(self):
        """Show a loading message and animated progress bar before displaying main menu."""
        self.clear_main_content()

        label = ctk.CTkLabel(
            self.main_content,
            text="Loading EHR data, please wait...",
            font=ctk.CTkFont(size=20),
            text_color="#1B5E20"
        )
        label.pack(pady=40)

        self.progress = ctk.CTkProgressBar(self.main_content, width=500)
        self.progress.pack(pady=20)
        self.progress.set(0)
        self.progress_value = 0
        self.animate_progress()

        # After 2 seconds, show the main menu
        self.after(2000, self.show_main_menu)

    def animate_progress(self):
        """Animate the progress bar continuously until main menu is shown."""
        if not self.progress.winfo_exists():
            return
        self.progress_value += 0.01
        if self.progress_value > 1:
            self.progress_value = 0
        self.progress.set(self.progress_value)
        self.after(50, self.animate_progress)

    def show_main_menu(self):
        """Display the main menu with hypothetical buttons and Exit."""
        self.clear_main_content()

        title = ctk.CTkLabel(
            self.main_content,
            text="Electronic Health Record",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#1B5E20"
        )
        title.pack(pady=20)

        button_style = {
            "width": 240,
            "height": 60,
            "corner_radius": 15,
            "font": ctk.CTkFont(size=16),
            "fg_color": "#388E3C",
            "hover_color": "#2E7D32"
        }

        referti_btn = ctk.CTkButton(self.main_content, text="Reports", **button_style)
        referti_btn.pack(pady=18)

        summary_btn = ctk.CTkButton(self.main_content, text="Patient Summary", **button_style)
        summary_btn.pack(pady=18)

        exit_btn = ctk.CTkButton(
            self.main_content,
            text="← Exit",
            command=self.exit,
            width=120,
            height=38,
            fg_color="#A5D6A7",
            hover_color="#81C784",
            text_color="white",
            font=ctk.CTkFont(size=15)
        )
        exit_btn.pack(pady=18)

    def clear_main_content(self):
        """Remove all widgets from the main content frame."""
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def exit(self):
        """Close this window and restore the parent window."""
        self.grab_release()
        self.destroy()
        if self.parent:
            self.parent.deiconify()
            self.parent.after(0, lambda: self.parent.state('zoomed'))