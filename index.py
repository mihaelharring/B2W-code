import json
import os
import random
import re
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog

INPUT_FILE = os.path.join(os.path.dirname(__file__), "index.json")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "questions_answers.json")
LEADERBOARD_FILE = os.path.join(os.path.dirname(__file__), "leaderboard.json")


def load_leaderboard(path=LEADERBOARD_FILE):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        return []
    cleaned = []
    for item in data:
        if isinstance(item, dict) and "name" in item and "score" in item:
            name = str(item.get("name", ""))[:10]
            try:
                score = int(item.get("score", 0))
            except (ValueError, TypeError):
                continue
            cleaned.append({"name": name, "score": score})
    return sorted(cleaned, key=lambda x: x["score"], reverse=True)[:10]


def save_leaderboard(entries, path=LEADERBOARD_FILE):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries[:10], f, ensure_ascii=False, indent=2)


def add_leaderboard_entry(name, score, path=LEADERBOARD_FILE):
    entries = load_leaderboard(path)
    name = (name or "").strip()[:10] or "Anonymous"
    try:
        score = int(score)
    except (TypeError, ValueError):
        score = 0
    entries.append({"name": name, "score": score})
    entries = sorted(entries, key=lambda x: x["score"], reverse=True)[:10]
    save_leaderboard(entries, path)
    return entries


def clean_down_options(opts):

    cleaned = {}
    for k, v in opts.items():
        v2 = v.strip()
        m = re.match(r"^[a-e][\)\.]\s*(.*)$", v2, re.IGNORECASE)
        if m:
            v2 = m.group(1).strip()
        cleaned[k] = v2
    return cleaned


def parse_questions_file(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Source file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

     
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = None

    questions = []

    if isinstance(data, dict):
        if "questions" in data and isinstance(data["questions"], list):
            data = data["questions"]
        else:
            raise ValueError("JSON must be either a list of question objects or {\"questions\": [...]}")

    if isinstance(data, list):
        for item in data:
            question = item.get("question", "").strip()
            answer = str(item.get("answer", "")).strip().lower()

            raw_choices = item.get("choices") or item.get("options") or []
            options = {}
            if isinstance(raw_choices, list):
                keys = ["a", "b", "c", "d", "e"]
                options = {k: v for k, v in zip(keys, raw_choices)}
            elif isinstance(raw_choices, dict):
                options = {k.lower(): v for k, v in raw_choices.items()}

            questions.append({"question": question, "options": options, "answer": answer})

        return questions

    
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]

    for blk in blocks:
        lines = [line.strip() for line in blk.splitlines() if line.strip()]
        if not lines:
            continue

        question = lines[0]
        options = {}
        for line in lines[1:]:
            stripped = line.lstrip('•').strip()
            m = re.match(r"^([abcde])\)\s*(.*)$", stripped, re.IGNORECASE)
            if m:
                key = m.group(1).lower()
                value = m.group(2).strip()
                options[key] = value
            else:
                m2 = re.match(r"^([abcde])\.\s*(.*)$", stripped, re.IGNORECASE)
                if m2:
                    key = m2.group(1).lower()
                    value = m2.group(2).strip()
                    options[key] = value

        answer = ""
        questions.append({"question": question, "options": options, "answer": answer})

    return questions


def save_questions_json(questions, path=OUTPUT_FILE):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"questions": questions}, f, ensure_ascii=False, indent=2)


def load_questions_json(path=OUTPUT_FILE):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("questions") or data


def get_random_question(questions):
    return random.choice(questions)


def get_age_quiz(questions, age):
    
    if age <= 15:
        n = 10
    else:
        n = 20

    if len(questions) <= n:
        return questions.copy()

    
    easy = [q for q in questions if q.get("difficulty", "").lower() in ("easy", "medium")]
    if age <= 15 and len(easy) >= n:
        return random.sample(easy, n)

    return random.sample(questions, n)


def print_question(q):
    print("\n----- RANDOM QUESTION -----")
    print(q.get("question", ""))
    for key in sorted(q.get("options", {}).keys()):
        text = q["options"][key]
        marker = " <- Correct" if key == q.get("answer") else ""
        print(f"{key}) {text}{marker}")
    print(f"Correct: {q.get('answer')}\n")


def run_quiz_gui(questions):
    root = tk.Tk()
    root.title("Keyboard Quiz")

    idx = 0
    score = 0
    selected_answers = [None] * len(questions)
    selected_display = [""] * len(questions)
    current_option_map = {}

    question_var = tk.StringVar()
    options_var = tk.StringVar()
    status_var = tk.StringVar()
    dropdown_var = tk.StringVar()

    def show_question(i):
        q = questions[i]
        question_var.set(f"{i+1}. {q.get('question', '')}")

        choices = list(q.get('options', {}).items())[:4]
        random.shuffle(choices)

        option_lines = []
        current_option_map.clear()
        for index, (orig_key, text) in enumerate(choices):
            disp_key = "abcd"[index]
            option_lines.append(f"{disp_key}) {text}")
            current_option_map[disp_key] = orig_key

        options_var.set("\n".join(option_lines))

        saved_display = selected_display[i]
        dropdown_var.set(saved_display or "")
        status_var.set(f"Question {i+1}/{len(questions)}  Score: {score}")

    def go_to_question(i):
        nonlocal idx
        idx = i
        show_question(idx)

    def on_submit():
        nonlocal score
        sel = dropdown_var.get().strip().lower()
        if sel not in ["a", "b", "c", "d"] or sel not in current_option_map:
            status_var.set("Please select a valid option (a-d).")
            return

        selected_key = current_option_map[sel]
        selected_answers[idx] = selected_key
        selected_display[idx] = sel

        q = questions[idx]
        correct = str(q.get("answer", "")).strip().lower()

        if selected_key.lower() == correct:
            score += 1
            status_var.set(f"Correct! Score {score}/{len(questions)}")
        else:
            status_var.set(f"Wrong; correct is {correct}. Score {score}/{len(questions)}")

        
        next_idx = None
        for i, ans in enumerate(selected_answers):
            if ans is None:
                next_idx = i
                break

        if next_idx is None:
            messagebox.showinfo("Quiz Complete", f"Finished! Score {score}/{len(questions)}")
            root.quit()
            return

        go_to_question(next_idx)

    frame = tk.Frame(root, padx=10, pady=10)
    frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(frame, textvariable=question_var, font=("Segoe UI", 14), wraplength=700, justify="left").pack(anchor="w", pady=(0, 8))
    tk.Label(frame, textvariable=options_var, font=("Segoe UI", 12), justify="left", anchor="w", bg="#f0f0f0", bd=1, relief="solid", padx=6, pady=6).pack(fill=tk.BOTH, pady=(0, 12))

    controls = tk.Frame(frame)
    controls.pack(fill=tk.X, pady=(0, 12))

    tk.Label(controls, text="Pick answer letter:", font=("Segoe UI", 12)).pack(side=tk.LEFT)
    dropdown = tk.OptionMenu(controls, dropdown_var, "a", "b", "c", "d")
    dropdown.config(width=4)
    dropdown.pack(side=tk.LEFT, padx=(5, 20))

    tk.Button(controls, text="Submit", command=on_submit, width=10).pack(side=tk.LEFT, padx=4)
    tk.Button(controls, text="Quit", command=root.quit, width=10).pack(side=tk.LEFT, padx=4)

    tk.Label(frame, textvariable=status_var, font=("Segoe UI", 11), fg="green").pack(anchor="w")

    show_question(idx)
    root.mainloop()

if __name__ == "__main__":
    try:
        questions = parse_questions_file(INPUT_FILE)
        if not questions:
            raise ValueError("No questions parsed from input file")

        root = tk.Tk()
        root.withdraw()
        age = simpledialog.askinteger("Age Check", "Enter your age:", minvalue=1, maxvalue=120, parent=root)
        if age is None:
            messagebox.showinfo("Cancelled", "Age is required to start the quiz.")
            root.destroy()
            sys.exit(0)

        selected = get_age_quiz(questions, age)
        save_questions_json(selected)

        root.destroy()

        run_quiz_gui(selected)

    except ValueError as ve:
        messagebox.showerror("Input error", str(ve))
    except Exception as ex:
        messagebox.showerror("Error", str(ex))
while True:
    name = input("Enter your name: ")
    score = int(input("Enter your score: "))

