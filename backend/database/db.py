from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "learning.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                lesson TEXT NOT NULL,
                level TEXT NOT NULL,
                xp INTEGER NOT NULL DEFAULT 0,
                completed INTEGER NOT NULL DEFAULT 0,
                UNIQUE(user_id, lesson),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                lesson TEXT NOT NULL,
                question_type TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                correct INTEGER NOT NULL,
                time_taken REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                earned INTEGER NOT NULL DEFAULT 1,
                earned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, name),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """
        )
        row = conn.execute("SELECT id FROM users WHERE username = ?", ("Learner",)).fetchone()
        if row is None:
            user_id = conn.execute("INSERT INTO users(username) VALUES (?)", ("Learner",)).lastrowid
        else:
            user_id = row["id"]

        lessons = [
            ("numbers", "easy"),
            ("algebra", "easy"),
            ("functions", "easy"),
            ("parameters", "easy"),
            ("binary", "easy"),
            ("logic", "locked"),
            ("vectors", "locked"),
            ("matrices", "locked"),
            ("ai_parameters", "locked"),
            ("loss", "locked"),
            ("gradient_descent", "locked"),
            ("neural_networks", "locked"),
        ]
        for lesson, level in lessons:
            conn.execute(
                "INSERT OR IGNORE INTO progress(user_id, lesson, level) VALUES (?, ?, ?)",
                (user_id, lesson, level),
            )
