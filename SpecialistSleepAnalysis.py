# This module implements the SpecialistSleepAnalysisWindow and AnswersDetailWindow classes.
# The SpecialistSleepAnalysisWindow shows the specialist a simulated sleep analysis for the previous night,
# including various sleep metrics visualized in graphs.
# The sleep data is simulated and the specialist's access is limited to viewing only,
# with no real connection to external sleep monitoring devices or systems.
# The specialist can also access a questionnaire section to review patient responses.
# The AnswersDetailWindow displays detailed answers for a selected questionnaire.

import customtkinter as ctk
import sqlite3
import os
import random
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from PIL import Image
from customtkinter import CTkImage
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from PatientQuestionnaire import QUESTIONNAIRES  

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")

# Window showing the specialist a simulated sleep analysis of the previous night.
# Displays graphs for sleep cycles, sleep score, breath detection, and heart rate.
# Provides access to patient questionnaires.

class SpecialistSleepAnalysisWindow(ctk.CTkToplevel):
    def __init__(self, parent, specialist_id, patient_id, patient_name):
        super().__init__()
        self.title("Sleep Analysis - Specialist View")
        self.geometry("1000x700")
        self.configure(fg_color="#E8F5E9")

        self.parent = parent
        self.specialist_id = specialist_id
        self.patient_id = patient_id
        self.patient_name = patient_name

        self.state('zoomed')
        self.grab_set()  # Make this window modal to block interaction with parent

        self.fake_data = self.generate_fake_week_data()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", padx=20, pady=(10, 10), expand=True)

        # Header
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x")
        logo_image = Image.open(LOGO_PATH).resize((80, 80), Image.LANCZOS)
        logo = CTkImage(light_image=logo_image, size=(80, 80))
        logo_label = ctk.CTkLabel(header_frame, image=logo, text="")
        logo_label.pack(side="left")

        title_label = ctk.CTkLabel(header_frame, text="BREATHE", font=ctk.CTkFont(size=36, weight="bold"), text_color="#1B5E20")
        title_label.pack(side="left", padx=(100, 0))

        self.title_label = ctk.CTkLabel(container, text=f"Sleep Analysis: {self.patient_name}", 
                                        font=ctk.CTkFont(size=24, weight="bold"), text_color="#1B5E20")
        self.title_label.pack(pady=(5, 5), anchor="center")

        # Graphs container
        graph_grid_frame = ctk.CTkFrame(container, fg_color="white", corner_radius=12)
        graph_grid_frame.pack(fill="both", expand=True, padx=10, pady=10)

        for i in range(2):
            graph_grid_frame.rowconfigure(i, weight=1)
        for j in range(2):
            graph_grid_frame.columnconfigure(j, weight=1)

        dates = [d["date"].strftime("%d-%m") for d in self.fake_data]

        # Helper function to create canvas with toolbar
        def create_canvas_with_toolbar(fig, master):
            frame = ctk.CTkFrame(master, fg_color="white")
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            toolbar = NavigationToolbar2Tk(canvas, frame)
            toolbar.update()
            toolbar.pack(fill="x")
            return frame

        # Graph 1: Sleep Cycles
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
        frame1 = create_canvas_with_toolbar(fig1, graph_grid_frame)
        frame1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Graph 2: Sleep Score
        fig2 = plt.Figure(figsize=(5, 3), dpi=100)
        ax2 = fig2.add_subplot(111)
        scores = [d["sleep_score"] for d in self.fake_data]
        ax2.plot(dates, scores, marker='o', color='#388E3C')
        ax2.set_title("Sleep Score")
        ax2.set_ylim(0, 100)
        ax2.set_ylabel("Score")
        ax2.grid(True, alpha=0.3)
        frame2 = create_canvas_with_toolbar(fig2, graph_grid_frame)
        frame2.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Graph 3: Breath Detection
        fig3 = plt.Figure(figsize=(5, 3), dpi=100)
        ax3 = fig3.add_subplot(111)
        breaths = [d["breath_detection"] for d in self.fake_data]
        ax3.bar(dates, breaths, color='#388E3C')
        ax3.set_title("Breath Detection")
        ax3.set_ylabel("Events")
        ax3.grid(True, alpha=0.3)
        frame3 = create_canvas_with_toolbar(fig3, graph_grid_frame)
        frame3.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Graph 4: Heart Rate
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
        frame4 = create_canvas_with_toolbar(fig4, graph_grid_frame)
        frame4.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        # Buttons frame
        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.pack(pady=(10, 20))

        self.btn_questionnaires = ctk.CTkButton(button_frame, text="Questionnaires", width=180, height=40,
                                                corner_radius=15, fg_color="#388E3C", hover_color="#2E7D32",
                                                font=ctk.CTkFont(size=16), text_color="white",
                                                command=self.open_questionnaires)
        self.btn_questionnaires.pack(side="left", padx=20)

        self.btn_go_back = ctk.CTkButton(button_frame, text="← Exit", width=140, height=40,
                                         corner_radius=15, fg_color="#A5D6A7", hover_color="#81C784",
                                         font=ctk.CTkFont(size=14), text_color="white",
                                         command=self.exit_window)
        self.btn_go_back.pack(side="left", padx=20)

        # Timestamp label bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def generate_fake_sleep_cycles(self):
        """Generate fake sleep cycle data with random values for light, deep, REM, and awake minutes."""
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
        """Generate a fake sleep score between 50 and 95."""
        return random.randint(50, 95)

    def generate_fake_breath_detection(self):
        """Generate a fake number of breath detection events between 0 and 10."""
        return random.randint(0, 10)

    def generate_fake_heart_rate(self):
        """Generate fake heart rate data with average, minimum, and maximum BPM."""
        avg_hr = random.randint(50, 70)
        min_hr = avg_hr - random.randint(5, 10)
        max_hr = avg_hr + random.randint(5, 15)
        return {
            "avg_hr": avg_hr,
            "min_hr": min_hr,
            "max_hr": max_hr,
        }

    def generate_fake_night_data(self):
        """Generate fake data for a single night including date, sleep cycles, score, breath detection, and heart rate."""
        date = datetime.now().date()
        return {
            "date": date,
            "sleep_cycles": self.generate_fake_sleep_cycles(),
            "sleep_score": self.generate_fake_sleep_score(),
            "breath_detection": self.generate_fake_breath_detection(),
            "heart_rate": self.generate_fake_heart_rate(),
        }

    def generate_fake_week_data(self):
        """Generate fake sleep data for the past 7 days."""
        data = []
        for i in range(7):
            day_data = self.generate_fake_night_data()
            day_data["date"] = datetime.now().date() - timedelta(days=6 - i)
            data.append(day_data)
        return data

    def open_questionnaires(self):
        """Open the questionnaire history window modally, hiding this window."""
        self.withdraw()
        SpecialistQuestionnaireHistoryWindow(self, self.patient_id, self.patient_name)    

    def update_timestamp(self):
        """Update the timestamp label every second with current date and time."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp)
    
    def exit_window(self):
        """Close this window and restore the parent window."""
        self.grab_release()
        self.destroy()
        if self.parent:
            self.parent.deiconify()
            self.parent.state('zoomed')

# Window showing the history of questionnaires completed by a patient.
# Allows the specialist to view answers of each questionnaire.

class SpecialistQuestionnaireHistoryWindow(ctk.CTkToplevel):
    def __init__(self, parent, patient_id, patient_name):
        super().__init__()
        self.parent = parent
        self.patient_id = patient_id
        self.patient_name = patient_name

        # Window styling and header setup
        self.title("Patient Questionnaires")
        self.geometry("800x600")
        self.configure(fg_color="#E8F5E9")
        self.state("zoomed")
        self.focus_force()
        self.grab_set()  # Make this window modal to block interaction with parent
        self.protocol("WM_DELETE_WINDOW", self.go_back)

        # Main container frame
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", padx=20, pady=(10, 10), expand=True)

        # Header frame with logo and titles
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

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text=f"Questionnaires for: {patient_name}",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#1B5E20")
        subtitle_label.pack(side="left", padx=(60, 0))

        # Center frame containing scrollable list of questionnaires
        self.center_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.center_frame.pack(fill="both", expand=True, pady=(10, 10))

        self.scroll_frame = ctk.CTkScrollableFrame(self.center_frame, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Exit button at bottom
        self.exit_btn = ctk.CTkButton(
            container, text="← Go Back", command=self.go_back,
            fg_color="#A5D6A7", hover_color="#81C784", text_color="white", width=160, height=50,
            font=ctk.CTkFont(size=18)
        )
        self.exit_btn.pack(side="bottom", pady=20)

        # Timestamp label bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

        # Populate the questionnaire list from database
        self.populate_questionnaire_list()

    def update_timestamp(self):
        """Update the timestamp label every second with current date and time."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 

    def populate_questionnaire_list(self):
        """Load questionnaires completed by the patient from the database.
        Display each questionnaire with a 'View Answers' button."""
        conn = sqlite3.connect("DBproject.db")
        c = conn.cursor()
        c.execute("""
            SELECT ID_Filled, TemplateName, TemplateID, CompilationDate, Score
            FROM Questionnaire
            WHERE ID_Patient = ?
            ORDER BY CompilationDate DESC
        """, (self.patient_id,))
        rows = c.fetchall()
        conn.close()

        if not rows:
            empty_label = ctk.CTkLabel(self.scroll_frame, text="No questionnaires compiled.", font=ctk.CTkFont(size=16))
            empty_label.pack(pady=20)
            return

        for qid, name, template_id, date, score in rows:
            frame = ctk.CTkFrame(self.scroll_frame, fg_color="white", corner_radius=10)
            frame.pack(fill="x", padx=5, pady=5)

            info = f"{name} ({template_id})\nDate: {date} | Score: {score}"
            label = ctk.CTkLabel(frame, text=info, font=ctk.CTkFont(size=15), text_color="#2E7D32", justify="left")
            label.pack(side="left", padx=10, pady=10)

            btn = ctk.CTkButton(
                frame, text="View Answers", width=120,
                fg_color="#388E3C", hover_color="#2E7D32", text_color="white",
                command=lambda qid=qid, name=name, date=date: self.open_answers(qid, name, date)
            )
            btn.pack(side="right", padx=10, pady=10)

    def open_answers(self, id_filled, name, date):
        """Open the detailed answers window for the selected questionnaire."""       
        AnswersDetailWindow(self, id_filled, name, date)
    
    def go_back(self):
        """Close this window and restore the parent window."""
        self.grab_release()
        self.destroy()
        if self.parent:
            self.parent.deiconify()
            self.parent.focus_force()
            self.parent.state('zoomed')

# Window to display detailed answers of a selected questionnaire.
# Shows questions and corresponding answers in a scrollable frame.

class AnswersDetailWindow(ctk.CTkToplevel):
    def __init__(self, parent, id_filled, questionnaire_name, date):
        super().__init__()
        self.parent = parent
        self.id_filled = id_filled
        self.title(f"{questionnaire_name} - {date}")
        self.geometry("600x500")
        self.configure(fg_color="#E8F5E9")
        self.state("normal")
        self.focus_force()
        self.grab_set()  # Make this window modal to block interaction with parent
        self.protocol("WM_DELETE_WINDOW", self.go_back)

        # Header label with questionnaire name and date
        header = ctk.CTkLabel(self, text=f"{questionnaire_name} ({date})", font=ctk.CTkFont(size=22, weight="bold"), text_color="#1B5E20")
        header.pack(pady=(20, 10))

        # Scrollable frame to hold questions and answers
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # Retrieve questions and answers from database
        conn = sqlite3.connect("DBproject.db")
        c = conn.cursor()
        c.execute("""
            SELECT QuestionIndex, Answer
            FROM QuestionnaireAnswer
            WHERE ID_Filled = ?
            ORDER BY QuestionIndex
        """, (id_filled,))
        answers = c.fetchall()
        c.execute("SELECT TemplateID FROM Questionnaire WHERE ID_Filled = ?", (id_filled,))
        row = c.fetchone()
        template_id = row[0] if row else None
        conn.close()

        # Retrieve questions text from predefined QUESTIONNAIRES dictionary
        questions = []
        if template_id and template_id in QUESTIONNAIRES:
            questions = [q["text"] for q in QUESTIONNAIRES[template_id]["questions"]]

        # Display each question and corresponding answer
        for idx, answer in answers:
            q_text = questions[idx] if idx < len(questions) else f"Question {idx+1}"
            frame = ctk.CTkFrame(scroll, fg_color="white", corner_radius=8)
            frame.pack(fill="x", padx=5, pady=5)
            qlabel = ctk.CTkLabel(frame, text=q_text, font=ctk.CTkFont(size=14), text_color="#1B5E20", anchor="w", justify="left")
            qlabel.pack(anchor="w", padx=10, pady=(8, 2))
            alabel = ctk.CTkLabel(frame, text=f"Answer: {answer}", font=ctk.CTkFont(size=13), text_color="#388E3C", anchor="w")
            alabel.pack(anchor="w", padx=20, pady=(0, 8))

        # Button frame with go back button
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)

        self.btn_go_back = ctk.CTkButton(
            btn_frame, text="← Go Back", command=self.go_back,
            fg_color="#A5D6A7", hover_color="#81C784", text_color="white", width=160, height=50,
            font=ctk.CTkFont(size=18)
        )
        self.btn_go_back.pack(side="bottom", padx=40)

        # Timestamp label bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second with current date and time."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp)         

    def go_back(self):
        """Close this window and restore the parent window."""
        self.grab_release()
        self.destroy()
        if self.parent:
            self.parent.deiconify()
            self.parent.focus_force()
            self.parent.state('zoomed')