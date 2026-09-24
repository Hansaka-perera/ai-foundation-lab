from __future__ import annotations

from backend.database.db import get_connection


def unlock(user_id: int, name: str, description: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO achievements(user_id, name, description) VALUES (?, ?, ?)",
            (user_id, name, description),
        )


def evaluate(user_id: int) -> None:
    with get_connection() as conn:
        solved = conn.execute("SELECT COUNT(*) c FROM results WHERE user_id=? AND correct=1", (user_id,)).fetchone()["c"]
        parameter = conn.execute("SELECT COUNT(*) c FROM results WHERE user_id=? AND lesson='parameters' AND correct=1", (user_id,)).fetchone()["c"]
        binary = conn.execute("SELECT COUNT(*) c FROM results WHERE user_id=? AND lesson='binary' AND correct=1", (user_id,)).fetchone()["c"]
        perfect_round = conn.execute("SELECT COUNT(*) c FROM results WHERE user_id=? AND correct=0", (user_id,)).fetchone()["c"] == 0 and solved >= 5

        grants = []
        if parameter >= 1:
            grants.append(("First Parameter", "Solve your first parameter challenge."))
        if binary >= 1:
            grants.append(("Binary Beginner", "Decode or convert your first binary challenge."))
        if solved >= 10:
            grants.append(("10 Problems Solved", "Solve 10 problems correctly."))
        if perfect_round:
            grants.append(("Perfect Round", "Build a clean run of correct answers."))
        if parameter >= 10:
            grants.append(("Parameter Master", "Solve 10 parameter problems correctly."))
        if binary >= 10:
            grants.append(("Binary Decoder", "Solve 10 binary problems correctly."))
        for name, description in grants:
            conn.execute("INSERT OR IGNORE INTO achievements(user_id,name,description) VALUES(?,?,?)", (user_id, name, description))
