# This module implements the main application window, which is the first access page when the app is opened,
# either downloaded on a phone or accessed via internet link.
# If the user is already registered, they can proceed directly to login.
# Otherwise, they can start the registration process by selecting their role.

import customtkinter as ctk
import os
from datetime import datetime
from PIL import Image
from customtkinter import CTkImage

from Registration import RoleSelection
from Login import LoginWindow

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# Main application window shown on app launch.
# Provides buttons for registration and login.

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BREATHE")
        self.geometry("600x500")  
        self.configure(fg_color="#E8F5E9")
        self.after(0, self.state, "zoomed")  # Maximize window on start
        
        # Container frame centered in window
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Load and display logo image
        pil_img = Image.open(LOGO_PATH).resize((100, 100), Image.LANCZOS)
        ctki = CTkImage(light_image=pil_img, size=(100, 100))

        logo_label = ctk.CTkLabel(container, image=ctki, text="")
        logo_label.pack(pady=(0, 10))

        # App title label
        title_label = ctk.CTkLabel(
            container,
            text="BREATHE",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#1B5E20"
        )
        title_label.pack(pady=(0, 30))

        # Frame for buttons
        buttons_frame = ctk.CTkFrame(container, fg_color="transparent")
        buttons_frame.pack(pady=10)

        # Common button style
        button_style = {
            "width": 250, "height": 60,
            "corner_radius": 10,
            "font": ctk.CTkFont(size=18),
            "fg_color": "#388E3C", "hover_color": "#2E7D32"
        }

        # Register button opens role selection window modally
        register_btn = ctk.CTkButton(
            buttons_frame,
            text="Register",
            command=self.open_role_selection,
            **button_style
        )
        register_btn.pack(pady=10)

        # Login button opens login window modally
        login_btn = ctk.CTkButton(
            buttons_frame,
            text="Login",
            command=self.open_login_window,
            **button_style
        )
        login_btn.pack(pady=10)

        # Timestamp label bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second with current date and time."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 

    def open_role_selection(self):
        """Open the RoleSelection window modally and hide this main window.
        When the RoleSelection window is closed, restore this window."""
        self.withdraw()
        self.role_window = RoleSelection(self)
        self.role_window.protocol("WM_DELETE_WINDOW", self.deiconify)
        self.role_window.grab_set()  # Modal behavior

    def open_login_window(self):
        """Open the LoginWindow modally and hide this main window.
        When the LoginWindow is closed, restore this window."""
        self.withdraw()
        login_window = LoginWindow(self)
        login_window.protocol("WM_DELETE_WINDOW", self.deiconify)
        login_window.grab_set()  # Modal behavior
    
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()