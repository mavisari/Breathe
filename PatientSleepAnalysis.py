# This module implements the screen that displays the sleep data recorded by the device from the previous night.
# Since there is no real connection to a sensor, the data shown here is randomly generated to allow plotting of graphs.
# For the same reason, there is no historical recap of all previous nights—only the last week is simulated.

import customtkinter as ctk
import os
import random
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from customtkinter import CTkImage
from PIL import Image

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")

# Window that displays simulated sleep data from the previous night and the last week.
# Data is randomly generated to mimic real sensor output for demonstration purposes.
# Four plots are shown: Sleep Cycles, Sleep Score, Breath Detection, and Heart Rate.

class SleepAnalysisWindow(ctk.CTkToplevel):
    def __init__(self, parent, user_id):
        super().__init__()
        self.title("Sleep Analysis")
        self.geometry("420x480")
        self.configure(fg_color="#E8F5E9")
        self.parent = parent
        self.user_id = user_id
        self.state('zoomed')
        self.grab_set()  # Make this window modal to block interaction with parent

        # Main container frame
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", padx=20, pady=(10, 5))

        # Header frame with logo and title
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x")

        self.title_label = ctk.CTkLabel(
            container, text="Sleep Analysis",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#1B5E20"
        )
        self.title_label.pack(fill="x", pady=(0, 5), anchor="center")

        logo_image = Image.open(LOGO_PATH).resize((80, 80), Image.LANCZOS)
        logo = CTkImage(light_image=logo_image, size=(80, 80))
        logo_label = ctk.CTkLabel(header_frame, image=logo, text="")
        logo_label.pack(side="left")

        title_label = ctk.CTkLabel(
            header_frame,
            text="BREATHE",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#1B5E20"
        )
        title_label.pack(side="left", padx=(100, 0))
        
        # Generate random data for the past week
        self.fake_data = self.generate_fake_week_data()

        # Frame for graph grid
        graph_grid_frame = ctk.CTkFrame(container, fg_color="white", corner_radius=12)
        graph_grid_frame.pack(fill="both", expand=True, padx=10, pady=10)

        dates = [d["date"].strftime("%d-%m") for d in self.fake_data]

        def create_canvas_with_toolbar(parent, fig):
            """
            Create a frame containing a matplotlib canvas and toolbar.
            """
            frame = ctk.CTkFrame(parent, fg_color="white")
            frame.pack(side="top", fill="both", expand=True, padx=10, pady=5)

            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side="top", fill="both", expand=True, padx=5, pady=5)

            toolbar = NavigationToolbar2Tk(canvas, frame)
            toolbar.update()
            toolbar.pack(side="top", fill="x")
            return frame

        # Arrange plots in 2 rows with 2 plots per row
        row1_frame = ctk.CTkFrame(graph_grid_frame, fg_color="transparent")
        row1_frame.pack(side="top", fill="both", expand=True)

        row2_frame = ctk.CTkFrame(graph_grid_frame, fg_color="transparent")
        row2_frame.pack(side="top", fill="both", expand=True)

        # Plot 1: Sleep Cycles
        fig1 = plt.Figure(figsize=(5, 3), dpi=100)
        ax1 = fig1.add_subplot(111)
        light = [d["sleep_cycles"]["light_sleep_min"] for d in self.fake_data]
        deep = [d["sleep_cycles"]["deep_sleep_min"] for d in self.fake_data]
        rem = [d["sleep_cycles"]["rem_sleep_min"] for d in self.fake_data]
        awake = [d["sleep_cycles"]["awake_min"] for d in self.fake_data]
        ax1.bar(dates, light, label='Light', color='#90ee90')
        ax1.bar(dates, deep, bottom=light, label='Deep', color='#006400')
        bottom_rem = [light[i]+deep[i] for i in range(len(light))]
        ax1.bar(dates, rem, bottom=bottom_rem, label='REM', color='#32cd32')
        bottom_awake = [bottom_rem[i]+rem[i] for i in range(len(rem))]
        ax1.bar(dates, awake, bottom=bottom_awake, label='Awake', color='#ffa07a')
        ax1.set_title("Sleep Cycles (min)")
        ax1.tick_params(axis='x', rotation=30)
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)

        frame1 = create_canvas_with_toolbar(row1_frame, fig1)
        frame1.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Plot 2: Sleep Score
        fig2 = plt.Figure(figsize=(5, 3), dpi=100)
        ax2 = fig2.add_subplot(111)
        scores = [d["sleep_score"] for d in self.fake_data]
        ax2.plot(dates, scores, marker='o', color='#388E3C')
        ax2.set_title("Sleep Score")
        ax2.set_ylim(0, 100)
        ax2.set_ylabel("Score")
        ax2.grid(True, alpha=0.3)

        frame2 = create_canvas_with_toolbar(row1_frame, fig2)
        frame2.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Plot 3: Breath Detection
        fig3 = plt.Figure(figsize=(5, 3), dpi=100)
        ax3 = fig3.add_subplot(111)
        breaths = [d["breath_detection"] for d in self.fake_data]
        ax3.bar(dates, breaths, color='#388E3C')
        ax3.set_title("Breath Detection")
        ax3.set_ylabel("Events")
        ax3.grid(True, alpha=0.3)

        frame3 = create_canvas_with_toolbar(row2_frame, fig3)
        frame3.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Plot 4: Heart Rate
        fig4 = plt.Figure(figsize=(5, 3), dpi=100)
        ax4 = fig4.add_subplot(111)
        avg_hr = [d["heart_rate"]["avg_hr"] for d in self.fake_data]
        min_hr = [d["heart_rate"]["min_hr"] for d in self.fake_data]
        max_hr = [d["heart_rate"]["max_hr"] for d in self.fake_data]
        ax4.plot(dates, avg_hr, label="Avg HR", color='#1b5e20', marker='o')
        ax4.fill_between(dates, min_hr, max_hr, color='#a5d6a7', alpha=0.5, label="Min-Max HR")
        ax4.set_title("Heart Rate")
        ax4.set_ylabel("BPM")
        ax4.legend(fontsize=8)
        ax4.grid(True, alpha=0.3)

        frame4 = create_canvas_with_toolbar(row2_frame, fig4)
        frame4.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Button frame under the grid
        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.pack(side="top", pady=(10, 20))

        exit_style = {
            "width": 160,
            "height": 40,
            "corner_radius": 15,
            "fg_color": "#A5D6A7",
            "hover_color": "#81C784",
            "font": ctk.CTkFont(size=14),
            "text_color": "white",
        }
        self.btn_go_back = ctk.CTkButton(button_frame, text="← Exit", **exit_style, command=self.exit_window)
        self.btn_go_back.pack(side="left", padx=20)

        # Timestamp label at the bottom-right
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp)

    # --- Fake data generation methods ---

    def generate_fake_sleep_cycles(self):
        """Generate random sleep cycle data for one night."""
        light = random.randint(180, 240)
        deep = random.randint(60, 90)
        rem = random.randint(70, 100)
        awake = random.randint(20, 40)
        return {
            "light_sleep_min": light,
            "deep_sleep_min": deep,
            "rem_sleep_min": rem,
            "awake_min": awake,
            "total_sleep_min": light + deep + rem,
        }

    def generate_fake_sleep_score(self):
        """Generate a random sleep score."""
        return random.randint(50, 95)

    def generate_fake_breath_detection(self):
        """Generate a random number of breath detection events."""
        return random.randint(0, 10)

    def generate_fake_heart_rate(self):
        """Generate random heart rate data for one night."""
        avg_hr = random.randint(50, 70)
        min_hr = avg_hr - random.randint(5, 10)
        max_hr = avg_hr + random.randint(5, 15)
        return {
            "avg_hr": avg_hr,
            "min_hr": min_hr,
            "max_hr": max_hr,
        }

    def generate_fake_night_data(self):
        """Generate all fake data for a single night."""
        date = datetime.now().date()
        return {
            "date": date,
            "sleep_cycles": self.generate_fake_sleep_cycles(),
            "sleep_score": self.generate_fake_sleep_score(),
            "breath_detection": self.generate_fake_breath_detection(),
            "heart_rate": self.generate_fake_heart_rate(),
        }

    def generate_fake_week_data(self):
        """Generate fake data for the last 7 nights."""
        data = []
        for i in range(7):
            day_data = self.generate_fake_night_data()
            day_data["date"] = datetime.now().date() - timedelta(days=6 - i)
            data.append(day_data)
        return data

    def exit_window(self):
        """Close this window and restore the parent window."""
        self.grab_release()
        self.destroy()
        if self.parent:
            self.parent.deiconify()
            self.parent.after(0, lambda: self.parent.state('zoomed'))