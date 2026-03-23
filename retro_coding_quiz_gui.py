import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

from quiz_core import (
    parse_questions_file,
    get_age_quiz,
    add_leaderboard_entry,
    load_leaderboard
)

# -----------------------------
# Retro Theme
# -----------------------------
BG = "#0a0a0a"
FG = "#00ff55"
BTN_BG = "#003300"
BTN_HOVER = "#005500"
FONT_MAIN = ("Consolas", 16)
FONT_TITLE = ("Consolas", 26, "bold")
CRT_IMAGE_PATH = "crt_background.png"  # Make sure this matches your filename

class RetroQuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Retro Quiz Game")
        self.root.geometry("900x600")
        self.root.resizable(False, False)

        # Load CRT background image
        self.bg_image = Image.open(CRT_IMAGE_PATH).resize((900, 600))
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.canvas = tk.Canvas(root, width=900, height=600, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas_bg = self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        self.time_elapsed = 0
        self.timer_running = False

        try:
            self.all_questions = parse_questions_file()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            root.quit()
            return

        self.show_age_screen()

    # -----------------------------
    # Utility
    # -----------------------------
    def add_hover(self, widget):
        widget.bind("<Enter>", lambda e: widget.config(bg=BTN_HOVER))
        widget.bind("<Leave>", lambda e: widget.config(bg=BTN_BG))

    def clear(self):
        for widget in self.canvas.winfo_children():
            widget.destroy()

    def add_watermark(self):
        label = tk.Label(
            self.canvas,
            text="This game is run on Tkinter",
            font=("Consolas", 10),
            fg="#888888",
            bg=BG
        )
        label.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")

    # -----------------------------
    # Age Screen
    # -----------------------------
    def show_age_screen(self):
        self.clear()

        tk.Label(self.canvas, text="RETRO QUIZ SYSTEM", font=FONT_TITLE, fg=FG, bg=BG).pack(pady=40)
        tk.Label(self.canvas, text="Enter your age:", font=FONT_MAIN, fg=FG, bg=BG).pack(pady=10)

        self.age_entry = tk.Entry(self.canvas, font=FONT_MAIN, fg=FG, bg="#111111", insertbackground=FG)
        self.age_entry.pack(pady=10)

        btn = tk.Button(self.canvas, text="CONTINUE", font=FONT_MAIN, fg=FG, bg=BTN_BG,
                        width=20, command=self.process_age)
        btn.pack(pady=20)
        self.add_hover(btn)

        self.add_watermark()

    def process_age(self):
        age_text = self.age_entry.get()
        if not age_text.isdigit():
            messagebox.showerror("Error", "Please enter a valid age.")
            return

        age = int(age_text)
        self.questions = get_age_quiz(self.all_questions, age)
        self.index = 0
        self.score = 0
        self.time_elapsed = 0
        self.timer_running = False

        self.show_start_menu()

    # -----------------------------
    # Start Menu
    # -----------------------------
    def show_start_menu(self):
        self.clear()

        tk.Label(self.canvas, text="RETRO QUIZ SYSTEM", font=FONT_TITLE, fg=FG, bg=BG).pack(pady=40)

        start_btn = tk.Button(self.canvas, text="START QUIZ", font=FONT_MAIN, fg=FG, bg=BTN_BG,
                              width=20, command=self.show_question)
        start_btn.pack(pady=20)
        self.add_hover(start_btn)

        lb_btn = tk.Button(self.canvas, text="LEADERBOARD", font=FONT_MAIN, fg=FG, bg=BTN_BG,
                           width=20, command=self.show_leaderboard)
        lb_btn.pack(pady=10)
        self.add_hover(lb_btn)

        quit_btn = tk.Button(self.canvas, text="QUIT", font=FONT_MAIN, fg=FG, bg=BTN_BG,
                             width=20, command=self.root.quit)
        quit_btn.pack(pady=10)
        self.add_hover(quit_btn)

        self.add_watermark()

    # -----------------------------
    # Timer
    # -----------------------------
    def start_timer(self):
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if self.timer_running:
            self.time_elapsed += 1
            self.root.after(1000, self.update_timer)

    # -----------------------------
    # Questions
    # -----------------------------
    def show_question(self):
        self.clear()

        if self.index == 0 and not self.timer_running:
            self.start_timer()

        q = self.questions[self.index]

        tk.Label(self.canvas, text=f"Q{self.index+1}: {q['question']}",
                 font=FONT_MAIN, fg=FG, bg=BG, wraplength=800, justify="left").pack(pady=40)

        for key, text in q["options"].items():
            btn = tk.Button(self.canvas, text=f"{key.upper()}) {text}", font=FONT_MAIN, fg=FG, bg=BTN_BG,
                            width=40, command=lambda k=key: self.check_answer(k))
            btn.pack(pady=10)
            self.add_hover(btn)

        self.add_watermark()

    def check_answer(self, selected_key):
        correct = self.questions[self.index]["answer"]
        if selected_key.lower() == correct:
            self.score += 1

        self.index += 1
        if self.index >= len(self.questions):
            self.show_name_screen()
        else:
            self.show_question()

    # -----------------------------
    # Name Screen
    # -----------------------------
    def show_name_screen(self):
        self.clear()
        self.timer_running = False


        bonus = max(5, 120 - self.time_elapsed)

        self.final_score = self.score + bonus

        tk.Label(self.canvas, text=(
            f"QUIZ COMPLETE\n"
            f"Correct Answers: {self.score}\n"
            f"Time: {self.time_elapsed} seconds\n"
            f"Bonus: +{bonus}\n"
            f"Final Score: {self.final_score}"
        ), font=FONT_TITLE, fg=FG, bg=BG).pack(pady=40)

        tk.Label(self.canvas, text="Enter your name:", font=FONT_MAIN, fg=FG, bg=BG).pack(pady=10)

        self.name_entry = tk.Entry(self.canvas, font=FONT_MAIN, fg=FG, bg="#111111", insertbackground=FG)
        self.name_entry.pack(pady=10)

        save_btn = tk.Button(self.canvas, text="SAVE SCORE", font=FONT_MAIN, fg=FG, bg=BTN_BG,
                             width=20, command=self.save_score)
        save_btn.pack(pady=20)
        self.add_hover(save_btn)

        self.add_watermark()

    def save_score(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a name.")
            return

        add_leaderboard_entry(name, self.final_score)
        self.show_leaderboard()

    # -----------------------------
    # Leaderboard
    # -----------------------------
    def show_leaderboard(self):
        self.clear()

        tk.Label(self.canvas, text="LEADERBOARD", font=FONT_TITLE, fg=FG, bg=BG).pack(pady=20)

        entries = load_leaderboard()
        if not entries:
            tk.Label(self.canvas, text="No leaderboard data yet.", font=FONT_MAIN, fg=FG, bg=BG).pack(pady=20)
        else:
            for i, entry in enumerate(entries, start=1):
                tk.Label(self.canvas, text=f"{i}. {entry['name']} - {entry['score']}",
                         font=FONT_MAIN, fg=FG, bg=BG).pack(pady=5)

        back_btn = tk.Button(self.canvas, text="BACK", font=FONT_MAIN, fg=FG, bg=BTN_BG,
                             width=20, command=self.show_start_menu)
        back_btn.pack(pady=30)
        self.add_hover(back_btn)

        self.add_watermark()


# -----------------------------
# Run App
# -----------------------------
root = tk.Tk()
app = RetroQuizApp(root)
root.mainloop()