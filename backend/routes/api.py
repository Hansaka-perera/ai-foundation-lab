from __future__ import annotations

import json
import random
import time
from pathlib import Path

from flask import Blueprint, jsonify, request

from backend.database.db import get_connection
from backend.services.achievements import evaluate
from backend.services.question_generator import parameter_question, binary_question, compare_number, normalize_fraction

api = Blueprint("api", __name__, url_prefix="/api")
ROOT = Path(__file__).resolve().parents[2]
CONFIG = json.loads((ROOT / "config" / "config.json").read_text(encoding="utf-8"))
DEFAULT_USER = "Learner"

DIFFICULTY_XP = {"easy": 10, "medium": 20, "hard": 40, "ai": 100}


def current_user_id() -> int:
    with get_connection() as conn:
        row = conn.execute("SELECT id FROM users WHERE username=?", (DEFAULT_USER,)).fetchone()
        return row["id"]


def adaptive_difficulty(lesson: str) -> str:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT difficulty, correct FROM results WHERE user_id=? AND lesson=? ORDER BY id DESC LIMIT 10",
            (current_user_id(), lesson),
        ).fetchall()
    if len(rows) < 5:
        return "easy"
    accuracy = sum(r["correct"] for r in rows) / len(rows)
    levels = ["easy", "medium", "hard", "ai"]
    current = rows[0]["difficulty"] if rows[0]["difficulty"] in levels else "easy"
    idx = levels.index(current)
    if accuracy >= 0.8:
        return levels[min(idx + 1, len(levels)-1)]
    if accuracy < 0.5:
        return levels[max(idx - 1, 0)]
    return current


@api.get("/dashboard")
def dashboard():
    user_id = current_user_id()
    with get_connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        progress = conn.execute("SELECT lesson, level, xp, completed FROM progress WHERE user_id=?", (user_id,)).fetchall()
        stats = conn.execute(
            """SELECT
                COALESCE(SUM(correct),0) correct,
                COUNT(*) total,
                COALESCE(SUM(CASE WHEN correct=0 THEN 1 ELSE 0 END),0) wrong,
                COALESCE(SUM(time_taken),0) total_time
               FROM results WHERE user_id=?""", (user_id,)
        ).fetchone()
        streak = 0
        best_streak = 0
        current = 0
        result_rows = conn.execute("SELECT correct FROM results WHERE user_id=? ORDER BY id ASC", (user_id,)).fetchall()
        for row in result_rows:
            if row["correct"]:
                current += 1
                best_streak = max(best_streak, current)
            else:
                current = 0
        streak = current
        achievements = conn.execute("SELECT name, description FROM achievements WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()

    total_xp = sum(row["xp"] for row in progress)
    average = (stats["total_time"] / stats["total"]) if stats["total"] else 0
    accuracy = (stats["correct"] / stats["total"] * 100) if stats["total"] else 0
    return jsonify({
        "app_name": CONFIG["app_name"],
        "user": dict(user),
        "progress": [dict(p) for p in progress],
        "stats": {
            "total_xp": total_xp,
            "problems_solved": stats["total"],
            "correct_answers": stats["correct"],
            "wrong_answers": stats["wrong"],
            "current_streak": streak,
            "best_streak": best_streak,
            "average_solving_time": round(average, 1),
            "accuracy": round(accuracy, 1),
        },
        "achievements": [dict(a) for a in achievements],
    })


@api.get("/question/<lesson>/<difficulty>")
def question(lesson: str, difficulty: str):
    if difficulty == "auto":
        difficulty = adaptive_difficulty(lesson)
    if difficulty not in {"easy", "medium", "hard", "ai"}:
        return jsonify({"error": "Invalid difficulty"}), 400
    if lesson == "parameters":
        q = parameter_question(difficulty)
    elif lesson == "binary":
        q = binary_question(difficulty)
    else:
        return jsonify({"error": "MVP lesson not implemented"}), 404
    q["id"] = f"{lesson}-{int(time.time()*1000)}-{random.randint(1000,9999)}"
    return jsonify(q)


@api.get("/lesson/<lesson>")
def lesson(lesson: str):
    lessons = {
        "parameters": {
            "title": "Parameter Mathematics",
            "tagline": "Turn unknowns into something you can reason about.",
            "learn": [
                {"title": "Level 1 · Easy", "body": "Start with y = ax. If x and y are known, isolate a."},
                {"title": "Level 2 · Medium", "body": "Add a bias: y = ax + b. Move b, then divide by x."},
                {"title": "Level 3 · Hard", "body": "Solve two equations to recover two unknown parameters."},
                {"title": "Level 4 · AI Foundation", "body": "Use multiple inputs: y = w₁x₁ + w₂x₂ + b."},
                {"title": "Level 5 · AI Parameters", "body": "Weights and bias shape the output of a simple model."},
            ],
        },
        "binary": {
            "title": "Binary Teaching",
            "tagline": "Understand how computers represent information with 0s and 1s.",
            "learn": [
                {"title": "Bits", "body": "A bit stores one binary value: 0 or 1."},
                {"title": "Bytes", "body": "8 bits form one byte, enough for 256 possible values."},
                {"title": "Decimal", "body": "Binary digits represent powers of two: 1, 2, 4, 8, 16..."},
                {"title": "ASCII", "body": "ASCII maps common characters to numeric codes, which can be written as binary."},
            ],
        },
        "translator": {
            "title": "Binary Code Translator",
            "tagline": "Translate text ↔ binary and inspect the ASCII value.",
            "learn": [],
        },
    }
    if lesson not in lessons:
        return jsonify({"error": "Lesson not found"}), 404
    return jsonify(lessons[lesson])


def _parse_answer_map(payload: dict) -> dict[str, str]:
    values = payload.get("answers", {})
    if not isinstance(values, dict):
        return {}
    clean = {}
    for key, value in values.items():
        if not isinstance(key, str):
            continue
        if isinstance(value, (int, float)):
            clean[key] = str(value)
        elif isinstance(value, str) and len(value) <= 64:
            clean[key] = value.strip()
    return clean


@api.post("/answer")
def answer():
    payload = request.get_json(silent=True) or {}
    lesson = payload.get("lesson")
    difficulty = payload.get("difficulty")
    question_type = payload.get("question_type")
    expected = payload.get("expected") or {}
    answers = _parse_answer_map(payload)
    time_taken = max(0.0, min(float(payload.get("time_taken", 0)), 86400.0))

    if difficulty not in DIFFICULTY_XP or lesson not in {"parameters", "binary"}:
        return jsonify({"error": "Invalid submission"}), 400

    correct = False
    if lesson == "parameters":
        correct = all(k in answers and compare_number(answers[k], v) for k, v in expected.items())
    else:
        actual = answers.get("answer", "").strip()
        target = str(expected.get("answer_text", "")).strip()
        correct = actual.lower() == target.lower()

    xp = DIFFICULTY_XP[difficulty] if correct else 0
    hints_used = int(payload.get("hints_used", 0) or 0)
    no_hint_bonus = 25 if correct and hints_used == 0 else 0
    fast_bonus = 20 if correct and time_taken > 0 and time_taken <= 15 else 0
    gained = xp + no_hint_bonus + fast_bonus

    user_id = current_user_id()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO results(user_id,lesson,question_type,difficulty,correct,time_taken) VALUES(?,?,?,?,?,?)",
            (user_id, lesson, question_type or "unknown", difficulty, int(correct), time_taken),
        )
        row = conn.execute("SELECT xp, completed FROM progress WHERE user_id=? AND lesson=?", (user_id, lesson)).fetchone()
        if row:
            new_xp = row["xp"] + gained
            completed = 1 if new_xp >= 250 else row["completed"]
            conn.execute("UPDATE progress SET xp=?, completed=?, level=? WHERE user_id=? AND lesson=?", (new_xp, completed, difficulty, user_id, lesson))
        else:
            conn.execute("INSERT INTO progress(user_id,lesson,level,xp,completed) VALUES(?,?,?,?,?)", (user_id,lesson,difficulty,gained,0))
    evaluate(user_id)

    return jsonify({
        "correct": correct,
        "xp_gained": gained,
        "base_xp": xp,
        "no_hint_bonus": no_hint_bonus,
        "fast_bonus": fast_bonus,
        "explanation": expected.get("explanation", ""),
    })


@api.post("/progress")
def save_progress():
    payload = request.get_json(silent=True) or {}
    lesson = payload.get("lesson")
    level = payload.get("level", "easy")
    completed = int(bool(payload.get("completed", False)))
    if lesson not in {"parameters", "binary"}:
        return jsonify({"error": "Invalid lesson"}), 400
    with get_connection() as conn:
        conn.execute("UPDATE progress SET level=?, completed=? WHERE user_id=? AND lesson=?", (level, completed, current_user_id(), lesson))
    return jsonify({"ok": True})
