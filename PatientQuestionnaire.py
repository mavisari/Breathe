# This module implements the sleep disorder questionnaires section of the application.
# It includes definitions of various sleep-related questionnaires specific to apnea,
# their metadata such as frequency and questions, and scoring functions to evaluate patient responses.
# The module also provides GUI windows for listing available questionnaires and for patients (and caregivers) to complete them.

import customtkinter as ctk
import sqlite3
import os
import datetime
from customtkinter import CTkImage
from PIL import Image

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "Logo", "Logo.png")

# Dictionary defining all questionnaire templates, their associated metadata, and scoring criteria.

QUESTIONNAIRES = {
    "PSQI": {
        "name": "Pittsburgh Sleep Quality Index",
        "frequency": "Monthly",
        "interval_days": 28,
        "questions": [
            {
                "text": "During the past month, when have you usually gone to bed at night?",
                "options": ["Before 9 PM", "9-11 PM", "After 11 PM"]
            },
            {
                "text": "How often have you taken medicine to help you sleep?",
                "options": ["Not during the past month", "Less than once a week", "Once or twice a week", "Three or more times a week"]
            },
            {
                "text": "How often have you had trouble staying awake while driving, eating meals, or engaging in social activity?",
                "options": ["Not during the past month", "Less than once a week", "Once or twice a week", "Three or more times a week"]
            },
            {
                "text": "During the past month, how often have you had trouble sleeping because you wake up in the middle of the night or early morning?",
                "options": ["Not during the past month", "Less than once a week", "Once or twice a week", "Three or more times a week"]
            },
            {
                "text": "During the past month, how often have you had pain that interfered with your sleep?",
                "options": ["Not during the past month", "Less than once a week", "Once or twice a week", "Three or more times a week"]
            }
        ]
    },
    "PROMIS": {
        "name": "PROMIS Sleep Disturbance",
        "frequency": "Weekly",
        "interval_days": 7,
        "questions": [
            {
                "text": "In the past 7 days, how often did you have trouble falling asleep?",
                "options": ["Never", "Rarely", "Sometimes", "Often", "Always"]
            },
            {
                "text": "In the past 7 days, how often did you have trouble staying asleep?",
                "options": ["Never", "Rarely", "Sometimes", "Often", "Always"]
            },
            {
                "text": "In the past 7 days, how often did you feel tired during the day?",
                "options": ["Never", "Rarely", "Sometimes", "Often", "Always"]
            },
            {
                "text": "In the past 7 days, how often did you feel sleepy during the day?",
                "options": ["Never", "Rarely", "Sometimes", "Often", "Always"]
            },
            {
                "text": "In the past 7 days, how would you rate your overall sleep quality?",
                "options": ["Very good", "Good", "Fair", "Poor", "Very poor"]
            },
            {
                "text": "In the past 7 days, how often did your sleep problems interfere with your daily activities?",
                "options": ["Never", "Rarely", "Sometimes", "Often", "Always"]
            }
        ]
    },
    "CSD": {
        "name": "Consensus Sleep Diary",
        "frequency": "Daily",
        "interval_days": 1,
        "questions": [
            {
                "text": "What time did you get into bed last night?",
                "options": ["Before 10 PM", "10-11 PM", "After 11 PM"]
            },
            {
                "text": "How many times did you wake up during the night?",
                "options": ["None", "1", "2", "3 or more"]
            },
            {
                "text": "What time did you finally get out of bed this morning?",
                "options": ["Before 6 AM", "6-7 AM", "After 7 AM"]
            },
            {
                "text": "How would you rate your sleep quality last night?",
                "options": ["Very good", "Good", "Fair", "Poor", "Very poor"]
            },
            {
                "text": "Did you take any naps during the day?",
                "options": ["No", "Yes, less than 30 minutes", "Yes, 30-60 minutes", "Yes, more than 60 minutes"]
            },
            {
                "text": "How refreshed did you feel upon waking up?",
                "options": ["Very refreshed", "Somewhat refreshed", "Neither refreshed nor tired", "Somewhat tired", "Very tired"]
            }
        ]
    },
    "OSA50": {
        "name": "OSA50 Questionnaire",
        "frequency": "Once",
        "interval_days": 28,
        "questions": [
            {
                "text": "Do you often snore loudly (louder than talking or loud enough to be heard through closed doors)?",
                "options": ["Yes", "No"]
            },
            {
                "text": "Do you often feel tired, fatigued, or sleepy during daytime?",
                "options": ["Yes", "No"]
            },
            {
                "text": "Are you aged 50 years or over?",
                "options": ["Yes", "No"]
            },
            {
                "text": "Is your waist circumference greater than 102 cm (40 inches) for men or 88 cm (35 inches) for women?",
                "options": ["Yes", "No"]
            },
            {
                "text": "Do you experience morning headaches?",
                "options": ["Yes", "No"]
            }
        ]
    },
    "Berlin": {
        "name": "Berlin Questionnaire",
        "frequency": "Once",
        "interval_days": 28,
        "questions": [
            {
                "text": "Ask the caregiver: How often did you hear the patient snore loudly in the past month?",
                "options": ["Never", "Rarely", "Sometimes", "Often", "Always"]
            },
            {
                "text": "Ask the caregiver: How often did you observe the patient stop breathing during sleep in the past month?",
                "options": ["Never", "Rarely", "Sometimes", "Often", "Always"]
            },
            {
                "text": "Do you have high blood pressure?",
                "options": ["Yes", "No"]
            },
            {
                "text": "Do you feel tired or fatigued after sleep?",
                "options": ["Yes", "No"]
            },
            {
                "text": "Ask the caregiver: How often did the patient experience gasping or choking during sleep?",
                "options": ["Never", "Rarely", "Sometimes", "Often", "Always"]
            },
            {
                "text": "Do you fall asleep while driving or during other activities?",
                "options": ["Never", "Rarely", "Sometimes", "Often", "Always"]
            }
        ]
    }
}

#Scoring functions
def score_psqi(answers: dict) -> int:
    """Compute the PSQI score based on the user's answers."""
    mapping = {
        0: {"Before 9 PM": 0, "9-11 PM": 1, "After 11 PM": 2},
        1: {"Not during the past month": 0, "Less than once a week": 1, "Once or twice a week": 2, "Three or more times a week": 3},
        2: {"Not during the past month": 0, "Less than once a week": 1, "Once or twice a week": 2, "Three or more times a week": 3},
        3: {"Not during the past month": 0, "Less than once a week": 1, "Once or twice a week": 2, "Three or more times a week": 3},
        4: {"Not during the past month": 0, "Less than once a week": 1, "Once or twice a week": 2, "Three or more times a week": 3},
    }
    return sum(mapping.get(idx, {}).get(answers.get(idx, ""), 0) for idx in range(5))

def score_promis(answers: dict) -> int:
    """Compute the PROMIS Sleep Disturbance score based on the user's answers."""
    freq_opts = ["Never", "Rarely", "Sometimes", "Often", "Always"]
    qual_opts = ["Very good", "Good", "Fair", "Poor", "Very poor"]
    score = 0
    for idx, resp in answers.items():
        if idx == 4:  # question about sleep quality
            score += qual_opts.index(resp) + 1
        else:
            score += freq_opts.index(resp) + 1
    return score

def score_csd(answers: dict) -> int:
    """Compute the Consensus Sleep Diary score based on the user's answers."""
    mapping = {
        0: {"Before 10 PM": 0, "10-11 PM": 1, "After 11 PM": 2},
        1: {"None": 0, "1": 1, "2": 2, "3 or more": 3},
        2: {"Before 6 AM": 0, "6-7 AM": 1, "After 7 AM": 2},
        3: {"Very good": 0, "Good": 1, "Fair": 2, "Poor": 3, "Very poor": 4},
        4: {"No": 0, "Yes, less than 30 minutes": 1, "Yes, 30-60 minutes": 2, "Yes, more than 60 minutes": 3},
        5: {"Very refreshed": 0, "Somewhat refreshed": 1, "Neither refreshed nor tired": 2, "Somewhat tired": 3, "Very tired": 4},
    }
    return sum(mapping.get(idx, {}).get(answers.get(idx, ""), 0) for idx in range(6))

def score_osa50(answers: dict) -> int:
    """Compute the OSA50 questionnaire score based on the user's answers."""
    pts = 0
    pts += 3 if answers.get(0) == "Yes" else 0
    pts += 3 if answers.get(3) == "Yes" else 0
    pts += 2 if answers.get(4) == "Yes" else 0
    pts += 2 if answers.get(2) == "Yes" else 0
    return pts

def score_berlin(answers: dict) -> int:
    """Compute the Berlin questionnaire score based on the user's answers."""
    sec1 = any(answers.get(i) in ["Often", "Always"] for i in (0, 1, 5))
    sec2 = (answers.get(3) == "Yes") or (answers.get(6) in ["Often", "Always"])
    return 1 if (sec1 + sec2) >= 2 else 0

# Window displaying the list of available questionnaires for the patient.
# Shows status of each questionnaire (last filled date, next available date) and enables opening questionnaires.

class QuestionnaireWindow(ctk.CTkToplevel):
    def __init__(self, parent, user_id):
        super().__init__()
        self.parent = parent
        self.user_id = user_id
        self.title("Available Questionnaires")
        self.geometry("800x600")
        self.configure(fg_color="#E8F5E9")
        self.state("zoomed")
        self.grab_set()  # Make this window modal to block interaction with parent

        # Main container frame
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=(10, 10))

        # Header frame with logo and titles
        self.header_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 10))

        logo_image = Image.open(LOGO_PATH).resize((80, 80), Image.LANCZOS)
        logo = CTkImage(light_image=logo_image, size=(80, 80))
        logo_label = ctk.CTkLabel(self.header_frame, image=logo, text="")
        logo_label.pack(side="left")

        title_label = ctk.CTkLabel(
            self.header_frame,
            text="BREATHE",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#1B5E20"
        )
        title_label.pack(side="left", padx=(100, 0))

        questionnaires_label = ctk.CTkLabel(
            self.header_frame,
            text="         Available Questionnaires",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color="#1B5E20"
        )
        questionnaires_label.pack(side="left", padx=(40, 0))

        # Frame to hold questionnaire list
        self.center_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.center_frame.pack(fill="both", expand=True)

        # Exit button to close this window and return to parent
        self.exit_btn = ctk.CTkButton(
            self.container, text="← Go Back", command=self.exit_back,
            fg_color="#A5D6A7", hover_color="#81C784", text_color="white", width=160, height=50,
            font=ctk.CTkFont(size=18)
        )
        self.exit_btn.pack(side="bottom", pady=20)

        self.q_frame = None
        self.create_widgets()

        # Timestamp label bottom-right corner
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second to show when the window was opened."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 

    def create_widgets(self):
        """Create or refresh the list of questionnaires.
        Each questionnaire shows its name, last filled date, next available date, and an 'Open' button.
        The button is disabled if the questionnaire is not yet available based on the interval."""
        if self.q_frame:
            for child in self.q_frame.winfo_children():
                child.destroy()
        else:
            self.q_frame = ctk.CTkScrollableFrame(self.center_frame, fg_color="transparent")
            self.q_frame.pack(fill="both", expand=True, padx=30, pady=10)

        conn = sqlite3.connect("DBproject.db")
        cursor = conn.cursor()
        today = datetime.date.today()

        for qid, qdata in QUESTIONNAIRES.items():
            frame = ctk.CTkFrame(self.q_frame, fg_color="white", corner_radius=10)
            frame.pack(fill="x", padx=5, pady=5)

            # Query last completion date for this questionnaire and patient
            cursor.execute("""
                SELECT MAX(CompilationDate) FROM Questionnaire
                WHERE ID_Patient = ? AND TemplateID = ?
            """, (self.user_id, qid))
            row = cursor.fetchone()
            last_date = row[0]

            interval_days = qdata.get("interval_days", 9999)

            if last_date:
                try:
                    last_date_dt = datetime.datetime.strptime(last_date, "%Y-%m-%d").date()
                    days_passed = (today - last_date_dt).days
                    days_remaining = max(0, interval_days - days_passed)
                    status_text = f"Last filled: {last_date} | Next in {days_remaining} day(s)"
                except Exception:
                    days_passed = None
                    days_remaining = 9999
                    status_text = "Date error"
            else:
                days_passed = None
                days_remaining = 0
                status_text = "Never filled"

            # Determine background and button colors based on questionnaire availability
            if last_date is None:
                bg_color = "#C8E6C9"  # green background indicating ready to fill
                btn_color = "#388E3C"
                can_compile = True
            elif days_passed < interval_days:
                bg_color = "#EEEEEE"  # greyed out background indicating not ready
                btn_color = "#BDBDBD"
                can_compile = False
            else:
                ratio = (days_passed - interval_days) / interval_days if interval_days > 0 else 1
                if ratio > 0.5:
                    bg_color = "#FFCDD2"  # red background indicating overdue
                    btn_color = "#D32F2F"
                elif ratio > 1/3:
                    bg_color = "#FFF9C4"  # yellow background indicating approaching overdue
                    btn_color = "#FBC02D"
                else:
                    bg_color = "#C8E6C9"  # green background indicating ready
                    btn_color = "#388E3C"
                can_compile = True

            frame.configure(fg_color=bg_color)
            label = ctk.CTkLabel(frame, text=f"{qdata['name']} ({qid})\n{status_text}", font=ctk.CTkFont(size=14), text_color="#2E7D32", justify="left")
            label.pack(side="left", padx=10, pady=10)

            btn_state = "normal" if can_compile else "disabled"
            button = ctk.CTkButton(frame, text="Open", width=100,
                                fg_color=btn_color,
                                hover_color=btn_color,
                                state=btn_state,
                                command=lambda qid=qid: self.open_questionnaire(qid))
            button.pack(side="right", padx=10)

            # Update scroll region for smooth scrolling
            self.q_frame.update_idletasks()
            if hasattr(self.q_frame, "_canvas"):
                self.q_frame._canvas.configure(scrollregion=self.q_frame._canvas.bbox("all"))

        conn.close()
    
    def refresh_list(self):
        """Refresh the questionnaire list by clearing and recreating widgets."""
        if self.q_frame:
            for child in self.q_frame.winfo_children():
                child.destroy()
        self.create_widgets()

    def open_questionnaire(self, template_id):
        """Open the questionnaire form window modally and hide this window."""
        self.withdraw()
        form = QuestionnaireForm(self, self.user_id, template_id)
        form.grab_set()
        form.protocol("WM_DELETE_WINDOW", lambda: self.restore_and_refresh())

    def restore_and_refresh(self):
        """Restore this window and refresh the questionnaire list after closing the form."""
        self.deiconify()
        self.refresh_list()
        self.state("zoomed")

    def exit_back(self):
        """Release modal grab, close this window, and restore the parent window."""
        self.grab_release()
        self.destroy()
        if self.parent:
            self.parent.deiconify()
            self.parent.state("zoomed")

# Window for compiling a specific questionnaire.
# Handles navigation, answer collection, summary, and saving to database.

class QuestionnaireForm(ctk.CTkToplevel):
    def __init__(self, parent, user_id, template_id):
        super().__init__()
        self.parent = parent  
        self.user_id = user_id
        self.template_id = template_id
        self.data = QUESTIONNAIRES[template_id]

        self.title(self.data["name"])
        self.geometry("800x600")
        self.configure(fg_color="#E8F5E9")
        self.state("zoomed")
        self.grab_set()  # Make this window modal

        # Main container frame
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", padx=20, pady=(10, 10))

        # Header with logo and title
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x")

        logo_image = Image.open(LOGO_PATH).resize((80, 80), Image.LANCZOS)
        logo = ctk.CTkImage(light_image=logo_image, size=(80, 80))
        logo_label = ctk.CTkLabel(header_frame, image=logo, text="")
        logo_label.pack(side="left")

        title_label = ctk.CTkLabel(
            header_frame,
            text="BREATHE",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#1B5E20")
        title_label.pack(side="left", padx=(100, 0))

        # Scrollable frame for questions
        self.question_frame = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=10)
        self.question_frame.pack(fill="both", expand=True, padx=50, pady=20)

        # Questionnaire state variables
        self.questions = self.data["questions"]
        self.current_index = -1
        self.answers = {}
        self.answer_var = None
        self.message_label = None
        self.caregiver_confirmed = ctk.BooleanVar(value=False)
        self.confirmed = False

        self.create_widgets()
        self.show_intro_modal()

        # Timestamp label at bottom-right
        self.timestamp_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.timestamp_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.update_timestamp()

    def update_timestamp(self):
        """Update the timestamp label every second."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.configure(text=f"Opened: {timestamp}")
        self.after(1000, self.update_timestamp) 

    def show_intro_modal(self):
        """Show an introduction modal before starting the questionnaire."""
        self.intro_win = ctk.CTkToplevel(self)
        self.intro_win.title("Questionnaire Introduction")
        self.intro_win.geometry("800x600")
        self.intro_win.state('zoomed')
        self.intro_win.configure(fg_color="#E8F5E9")
        self.intro_win.grab_set()  # Make the intro modal block interaction
        total_questions = len(self.questions)
        label = ctk.CTkLabel(
            self.intro_win,
            text=f"This questionnaire consists of {total_questions} questions.\nAre you ready to start?",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#1B5E20",
            justify="center"
        )
        label.pack(expand=True, pady=100)

        btn_frame = ctk.CTkFrame(self.intro_win, fg_color="transparent")
        btn_frame.pack(pady=30)

        ctk.CTkButton(
            btn_frame, text="← Go Back", width=140, height=50,
            font=ctk.CTkFont(size=18),
            fg_color= "#A5D6A7", 
            hover_color= "#81C784",
            command=self.exit_intro_modal
        ).pack(side="left", padx=30)

        ctk.CTkButton(
            btn_frame, text="Start →", width=140, height=50,
            font=ctk.CTkFont(size=18),
            fg_color= "#388E3C", 
            hover_color= "#2E7D32",
            command=self.start_from_intro_modal
        ).pack(side="left", padx=30)

    def exit_intro_modal(self):
        """Close the intro modal and exit the questionnaire form."""
        self.intro_win.grab_release()
        self.intro_win.destroy()
        self.exit_back()

    def start_from_intro_modal(self):
        """Close the intro modal and show the first question."""
        self.intro_win.grab_release()
        self.intro_win.destroy()
        self.current_index = 0
        self.show_question()

    def create_widgets(self):
        """Create or clear all widgets in the question frame."""
        for widget in self.question_frame.winfo_children():
            widget.destroy()
        self.title_label = ctk.CTkLabel(self.question_frame, text=self.data["name"], font=ctk.CTkFont(size=26, weight="bold"), text_color="#1B5E20")
        self.title_label.pack(pady=30)
        self.message_label = ctk.CTkLabel(self.question_frame, text="", font=ctk.CTkFont(size=20), text_color="#D32F2F")
        self.message_label.pack(pady=10)

    def show_question(self):
        """Display the current question and navigation controls."""
        for widget in self.question_frame.winfo_children():
            widget.destroy()
        self.message_label = ctk.CTkLabel(self.question_frame, text="", font=ctk.CTkFont(size=20), text_color="#D32F2F")
        self.message_label.pack(pady=10)
        self.title_label = ctk.CTkLabel(self.question_frame, text=self.data["name"], font=ctk.CTkFont(size=26, weight="bold"), text_color="#1B5E20")
        self.title_label.pack(pady=10)

        if self.current_index < len(self.data["questions"]):
            q = self.questions[self.current_index]
            question_label = ctk.CTkLabel(self.question_frame, text=q["text"], font=ctk.CTkFont(size=22, weight="bold"), wraplength=700, justify="center")
            question_label.pack(pady=10)
            self.answer_var = ctk.StringVar()
            self.answer_var.set(self.answers.get(self.current_index, ""))

            for opt in q["options"]:
                rb = ctk.CTkRadioButton(self.question_frame, text=opt, variable=self.answer_var, value=opt, font=ctk.CTkFont(size=18))
                rb.pack(anchor="w", padx=80, pady=8)

            # Caregiver confirmation logic for certain questions
            if self.current_index == 0 and q.get("caregiver", False) and not self.caregiver_confirmed.get():
                label = ctk.CTkLabel(self.question_frame, text="Please call your caregiver to complete the following questions.", font=ctk.CTkFont(size=18), text_color="#D84315", wraplength=600, justify="center")
                label.pack(pady=20)
                confirm_check = ctk.CTkCheckBox(self.question_frame, text="Caregiver is present", variable=self.caregiver_confirmed, command=self.show_question)
                confirm_check.pack(pady=10)
                nav_frame = ctk.CTkFrame(self.question_frame, fg_color="transparent")
                nav_frame.pack(pady=20)
                back_btn = ctk.CTkButton(nav_frame, text="← Go Back", command=self.prev_question, width=200, height=55, font=ctk.CTkFont(size=20), fg_color= "#A5D6A7", hover_color= "#81C784", state="disabled")
                back_btn.pack(side="left", padx=15)
                continue_btn = ctk.CTkButton(nav_frame, text="Continue →", command=self.next_question, width=200, height=55, font=ctk.CTkFont(size=20), fg_color= "#388E3C", hover_color= "#2E7D32", state="disabled")
                continue_btn.pack(side="left", padx=15)
                return

            nav_frame = ctk.CTkFrame(self.question_frame, fg_color="transparent")
            nav_frame.pack(pady=20)
            back_btn = ctk.CTkButton(nav_frame, text="← Go Back", command=self.prev_question, width=140, height=40, font=ctk.CTkFont(size=16), fg_color= "#A5D6A7", hover_color= "#81C784",
                                     state="normal" if self.current_index > 0 else "disabled")
            back_btn.pack(side="left", padx=15)
            continue_btn = ctk.CTkButton(nav_frame, text="Continue →", command=self.next_question, width=140, height=40, font=ctk.CTkFont(size=16), fg_color= "#388E3C", hover_color= "#2E7D32", state="normal")
            continue_btn.pack(side="left", padx=15)
        else:
            self.show_summary()

    def next_question(self):
        """Go to the next question, saving the answer if provided."""
        selected = self.answer_var.get() if self.answer_var else ""
        if not selected:
            self.message_label.configure(text="Missing Information: please select an answer.",
                                         font=ctk.CTkFont(size=20, weight="bold"),
                                         text_color="#D32F2F"
            )
            return
        self.message_label.configure(text="")
        self.answers[self.current_index] = selected
        self.current_index += 1
        self.show_question()

    def prev_question(self):
        """Go back to the previous question."""
        if self.current_index > 0:
            self.current_index -= 1
            self.show_question()

    def show_summary(self):
        """Show a summary of all answers before saving."""
        for widget in self.question_frame.winfo_children():
            widget.destroy()
        self.message_label = ctk.CTkLabel(self.question_frame, text="", font=ctk.CTkFont(size=20), text_color="#D32F2F")
        self.message_label.pack(pady=10)
        ctk.CTkLabel(self.question_frame, text="Review your answers", font=ctk.CTkFont(size=22, weight="bold"), text_color="#1B5E20").pack(pady=20)
        for idx, ans in self.answers.items():
            q_text = self.data["questions"][idx]["text"]
            summary = f"{q_text}\n→ {ans}"
            ctk.CTkLabel(self.question_frame, text=summary, font=ctk.CTkFont(size=14), wraplength=700, justify="left", text_color="#2E7D32").pack(pady=5, anchor="w", padx=20)
        btn_frame = ctk.CTkFrame(self.question_frame, fg_color="transparent")
        btn_frame.pack(pady=30)
        confirm_btn = ctk.CTkButton(btn_frame, text="Confirm Questionnaire", fg_color= "#388E3C", hover_color= "#2E7D32", command=self.save_questionnaire)
        confirm_btn.pack(side="left", padx=20)
        change_btn = ctk.CTkButton(btn_frame, text="Change Answers", fg_color= "#A5D6A7", hover_color= "#81C784", command=self.change_answers)
        change_btn.pack(side="left", padx=10)

    def change_answers(self):
        """Return to the first question to allow changing answers."""
        self.current_index = 0
        self.show_question()

    def save_questionnaire(self):
        """Save the questionnaire and answers to the database, with scoring."""
        try:
            # Check if all answers are provided
            missing = [i for i in range(len(self.questions)) if i not in self.answers or not self.answers[i]]
            if missing:
                self.message_label.configure(text=f"Missing answers for questions: {', '.join(str(i+1) for i in missing)}", text_color="red")
                return

            conn = sqlite3.connect("DBproject.db")
            cursor = conn.cursor()
            date_today = datetime.date.today().isoformat()
            time_now = datetime.datetime.now().strftime("%H:%M:%S")
            filled_id = f"{self.template_id}_{self.user_id}_{date_today}_{time_now.replace(':','')}"

            # Compute the score for the questionnaire
            if self.template_id == "PSQI":
                score = score_psqi(self.answers)
            elif self.template_id == "PROMIS":
                score = score_promis(self.answers)
            elif self.template_id == "CSD":
                score = score_csd(self.answers)
            elif self.template_id == "OSA50":
                score = score_osa50(self.answers)
            elif self.template_id == "Berlin":
                score = score_berlin(self.answers)
            else:
                score = 0

            cursor.execute("""
                INSERT INTO Questionnaire (ID_Filled, ID_Patient, TemplateID, TemplateName, Frequency, Score, CompilationDate, CompilationTime)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                filled_id,
                self.user_id,
                self.template_id,
                self.data["name"],
                self.data["frequency"],
                score,
                date_today,
                time_now
            ))

            for idx, ans in self.answers.items():
                cursor.execute("""
                    INSERT INTO QuestionnaireAnswer (ID_Filled, QuestionIndex, Answer)
                    VALUES (?, ?, ?)
                """, (filled_id, idx, ans))

            conn.commit()
            conn.close()
            self.confirmed = True

            # Show confirmation message
            for widget in self.question_frame.winfo_children():
                widget.destroy()
            ctk.CTkLabel(self.question_frame, text="Questionnaire successfully submitted!", font=ctk.CTkFont(size=20), text_color="#1B5E20").pack(pady=30)
            exit_btn = ctk.CTkButton(self.question_frame, text="← Exit", fg_color="#A5D6A7", hover_color="#81C784", command=self.exit_back, width=200, height=55, font=ctk.CTkFont(size=20))
            exit_btn.pack(pady=20)

        except Exception as e:
            if self.message_label:
                self.message_label.configure(text=f"Error saving questionnaire: {e}", text_color="red")

        if hasattr(self.parent, "refresh_list"):
            self.parent.refresh_list()

    def exit_back(self):
        """Release modal grab, close this window, and restore parent."""
        self.grab_release()
        self.destroy()
        if self.parent:
            self.parent.refresh_list()
            self.parent.deiconify()
            self.parent.state("zoomed")
            if hasattr(self.parent, "create_widgets"):
                self.parent.create_widgets()