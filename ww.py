import tkinter as tk
from tkinter import messagebox, ttk
import requests
import random

class TriviaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🎉 Trivia Quiz Application 🎉")
        self.geometry("600x800")
        self.minsize(800, 650)  # Minimum size of the window
        self.maxsize(1200, 900)  # Maximum size of the window
        self.configure(bg="black")
        self.center_window()

        # Initialize variables
        self.score = 0
        self.current_question = None
        self.current_answers = []
        self.num_questions = 10  # Default number of questions
        self.questions_attempted = 0

        # Fonts and styles
        self.title_font = ("Helvetica", 24, "bold")
        self.subtitle_font = ("Helvetica", 18, "bold")
        self.text_font = ("Helvetica", 14)
        self.button_style = {"font": self.text_font, "bg": "white", "fg": "black", "width": 20, "height": 2, "relief": "raised"}
        self.label_style = {"font": self.text_font, "bg": "black", "fg": "white"}

        # Canvas for adding border
        self.canvas = tk.Canvas(self, bg="black", bd=0, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Container for frames inside canvas
        self.container = tk.Frame(self.canvas, bg="black")
        self.container.place(relwidth=1, relheight=1)

        self.frames = {}
        for F in (StartPage, QuizPage, SettingsPage, WinningScreen):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Draw corner borders
        self.draw_corner_borders()

        self.show_frame(StartPage)

    def center_window(self):
        """Center the window on the screen."""
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_cord = int((screen_width / 2) - (window_width / 2))
        y_cord = int((screen_height / 2) - (window_height / 2))
        self.geometry(f"{window_width}x{window_height}+{x_cord}+{y_cord}")

    def draw_corner_borders(self):
        """Draw white border lines in the corners of the window."""
        corner_length = 30  # Length of the corner lines
        # Top-left corner
        self.canvas.create_line(0, 0, corner_length, 0, fill="white", width=3)
        self.canvas.create_line(0, 0, 0, corner_length, fill="white", width=3)

        # Top-right corner
        self.canvas.create_line(self.winfo_width(), 0, self.winfo_width() - corner_length, 0, fill="white", width=3)
        self.canvas.create_line(self.winfo_width(), 0, self.winfo_width(), corner_length, fill="white", width=3)

        # Bottom-left corner
        self.canvas.create_line(0, self.winfo_height(), corner_length, self.winfo_height(), fill="white", width=3)
        self.canvas.create_line(0, self.winfo_height(), 0, self.winfo_height() - corner_length, fill="white", width=3)

        # Bottom-right corner
        self.canvas.create_line(self.winfo_width(), self.winfo_height(), self.winfo_width() - corner_length, self.winfo_height(), fill="white", width=3)
        self.canvas.create_line(self.winfo_width(), self.winfo_height(), self.winfo_width(), self.winfo_height() - corner_length, fill="white", width=3)

    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()
        if page == WinningScreen:
            frame.update_screen()

    def fetch_questions(self, category=None, difficulty=None):
        """Fetch questions from the Open Trivia Database API."""
        url = "https://opentdb.com/api.php"
        params = {
            "amount": self.num_questions,
            "type": "multiple",
        }
        if category:
            params["category"] = category
        if difficulty:
            params["difficulty"] = difficulty

        response = requests.get(url, params=params)
        data = response.json()

        if data["response_code"] == 0:
            return data["results"]
        else:
            messagebox.showerror("Error", "Failed to fetch questions.")
            return []


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="black")
        self.controller = controller

        # Title
        title_label = tk.Label(self, text="🎉 Welcome to Trivia Quiz! 🎉", font=controller.title_font, bg="black", fg="white")
        title_label.pack(pady=40)

        # Start Button
        start_button = tk.Button(self, text="Start Quiz", **controller.button_style, command=lambda: [controller.frames[QuizPage].start_quiz(), controller.show_frame(QuizPage)])
        start_button.pack(pady=10)

        # Settings Button
        settings_button = tk.Button(self, text="Settings ⚙️", **controller.button_style, command=lambda: controller.show_frame(SettingsPage))
        settings_button.pack(pady=10)

        # Exit Button
        exit_button = tk.Button(self, text="Exit ❌", **controller.button_style, command=self.quit)
        exit_button.pack(pady=10)


class QuizPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="black")
        self.controller = controller
        self.questions = []

        # Question Label (showing question number)
        self.question_label = tk.Label(self, text="", font=controller.subtitle_font, bg="black", fg="white", wraplength=700, justify="center")
        self.question_label.pack(pady=20)

        # Question number display
        self.question_num_label = tk.Label(self, text="Question 1", font=controller.label_style["font"], bg="black", fg="white")
        self.question_num_label.pack()

        # Answer Buttons
        self.answer_buttons = []
        for i in range(4):
            button = tk.Button(self, text="", **controller.button_style, command=lambda i=i: self.check_answer(i))
            button.pack(pady=10, fill="x", padx=40)
            self.answer_buttons.append(button)

        # Next Button
        self.next_button = tk.Button(self, text="➡️ Next Question", **controller.button_style, command=self.load_next_question)
        self.next_button.pack(pady=20)

    def start_quiz(self):
        """Start the quiz and fetch the questions."""
        self.controller.questions_attempted = 0
        self.controller.score = 0
        self.questions = self.controller.fetch_questions()
        if self.questions:
            self.load_next_question()

    def load_next_question(self):
        """Load the next trivia question."""
        if self.controller.questions_attempted < self.controller.num_questions:
            question = self.questions.pop(0)
            self.controller.current_question = question
            self.controller.current_answers = question["incorrect_answers"] + [question["correct_answer"]]
            random.shuffle(self.controller.current_answers)

            # Update the question number
            self.controller.questions_attempted += 1
            self.question_num_label.config(text=f"Question {self.controller.questions_attempted}/{self.controller.num_questions}")

            self.question_label.config(text=question["question"])
            for i, answer in enumerate(self.controller.current_answers):
                self.answer_buttons[i].config(text=answer, state="normal")
        else:
            # Show the winning screen when all questions are completed
            self.controller.show_frame(WinningScreen)

    def check_answer(self, index):
        """Check if the selected answer is correct."""
        correct_answer = self.controller.current_question["correct_answer"]
        selected_answer = self.controller.current_answers[index]

        if selected_answer == correct_answer:
            self.controller.score += 1
            messagebox.showinfo("✅ Correct!", "You answered correctly!")
        else:
            messagebox.showinfo("❌ Incorrect", f"The correct answer was: {correct_answer}")

        for button in self.answer_buttons:
            button.config(state="disabled")


class SettingsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="black")
        self.controller = controller

        # Title
        title_label = tk.Label(self, text="⚙️ Settings ⚙️", font=controller.title_font, bg="black", fg="white")
        title_label.pack(pady=40)

        # Category Dropdown
        category_label = tk.Label(self, text="Select Category:", font=controller.text_font, bg="black", fg="white")
        category_label.pack(pady=5)
        self.category_var = tk.StringVar()
        category_dropdown = ttk.Combobox(self, textvariable=self.category_var, state="readonly")
        category_dropdown['values'] = ["Any", "General Knowledge", "Science", "Math", "History"]
        category_dropdown.pack(pady=5)

        # Difficulty Dropdown
        difficulty_label = tk.Label(self, text="Select Difficulty:", font=controller.text_font, bg="black", fg="white")
        difficulty_label.pack(pady=5)
        self.difficulty_var = tk.StringVar()
        difficulty_dropdown = ttk.Combobox(self, textvariable=self.difficulty_var, state="readonly")
        difficulty_dropdown['values'] = ["Any", "Easy", "Medium", "Hard"]
        difficulty_dropdown.pack(pady=5)

        # Number of Questions Dropdown
        num_questions_label = tk.Label(self, text="Number of Questions:", font=controller.text_font, bg="black", fg="white")
        num_questions_label.pack(pady=5)
        self.num_questions_var = tk.IntVar(value=10)
        num_questions_dropdown = ttk.Combobox(self, textvariable=self.num_questions_var, state="readonly")
        num_questions_dropdown['values'] = [5, 10, 15, 20]
        num_questions_dropdown.pack(pady=5)

        # Save Button
        save_button = tk.Button(self, text="Save Settings", **controller.button_style, command=self.save_settings)
        save_button.pack(pady=20)

        # Back Button
        back_button = tk.Button(self, text="Back ⬅️", **controller.button_style, command=lambda: controller.show_frame(StartPage))
        back_button.pack(pady=10)

    def save_settings(self):
        """Save user settings.""" 
        category = self.category_var.get()
        difficulty = self.difficulty_var.get()
        num_questions = self.num_questions_var.get()

        # Logic to apply settings
        self.controller.category = category if category != "Any" else None
        self.controller.difficulty = difficulty if difficulty != "Any" else None
        self.controller.num_questions = num_questions

        messagebox.showinfo("Settings Saved", "Your preferences have been saved!")


class WinningScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="black")
        self.controller = controller

        # Winning Message
        self.message_label = tk.Label(self, text="", font=controller.title_font, bg="black", fg="white")
        self.message_label.pack(pady=40)

        # Quit Button
        quit_button = tk.Button(self, text="Quit ❌", **controller.button_style, command=controller.quit)
        quit_button.pack(pady=20)

    def update_screen(self):
        """Update the winning screen with the score."""
        score_message = f"🎉 Congratulations! 🎉\nYour Score: {self.controller.score}/{self.controller.num_questions}"
        self.message_label.config(text=score_message)


if __name__ == "__main__":
    app = TriviaApp()
    app.mainloop()
