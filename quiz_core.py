import json
import os
import random

BASE_DIR = os.path.dirname(__file__)
INPUT_FILE = os.path.join(BASE_DIR, "index.json")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "questions_answers.json")
LEADERBOARD_FILE = os.path.join(BASE_DIR, "leaderboard.json")


def parse_questions_file(path=INPUT_FILE):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Source file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "questions" in data:
        data = data["questions"]

    if not isinstance(data, list):
        raise ValueError("JSON must be a list or {'questions': [...]}")

    questions = []

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

        questions.append({
            "question": question,
            "options": options,
            "answer": answer
        })

    return questions


def get_age_quiz(questions, age):
    if age <= 15:
        n = 10
    else:
        n = 20

    if len(questions) <= n:
        return questions.copy()

    easy = [
        q for q in questions
        if q.get("difficulty", "").lower() in ("easy", "medium")
    ]

    if age <= 15 and len(easy) >= n:
        return random.sample(easy, n)

    return random.sample(questions, n)


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
            cleaned.append({
                "name": str(item["name"])[:10],
                "score": int(item["score"])
            })

    return sorted(cleaned, key=lambda x: x["score"], reverse=True)[:10]


def save_leaderboard(entries, path=LEADERBOARD_FILE):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries[:10], f, indent=2)


def add_leaderboard_entry(name, score, path=LEADERBOARD_FILE):
    entries = load_leaderboard(path)
    name = (name or "").strip()[:10] or "Anonymous"

    entries.append({"name": name, "score": int(score)})
    entries = sorted(entries, key=lambda x: x["score"], reverse=True)[:10]

    save_leaderboard(entries, path)
    return entries