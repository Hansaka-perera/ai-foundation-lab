from __future__ import annotations

import random
from fractions import Fraction

DIFFICULTIES = ("easy", "medium", "hard", "ai")


def _num(n: int) -> str:
    return str(n)


def parameter_question(difficulty: str) -> dict:
    difficulty = difficulty.lower()
    if difficulty == "easy":
        a = random.randint(2, 9)
        x = random.randint(2, 9)
        y = a * x
        return {
            "type": "parameter_single",
            "difficulty": "easy",
            "question": f"y = ax  |  x = {x}  |  y = {y}\nFind a.",
            "variables": ["a"],
            "answer": {"a": a},
            "hints": ["Start from y = ax.", "Divide both sides by x.", f"a = {y} / {x}"],
            "explanation": f"a = y / x = {y} / {x} = {a}.",
        }

    if difficulty == "medium":
        a = random.randint(2, 8)
        x = random.randint(2, 8)
        b = random.randint(-5, 6)
        y = a * x + b
        return {
            "type": "parameter_affine",
            "difficulty": "medium",
            "question": f"y = ax + b\n\nx = {x}\ny = {y}\nb = {b}\n\nFind a.",
            "variables": ["a"],
            "answer": {"a": a},
            "hints": ["Move b away from y.", f"{y} - ({b}) leaves the ax term.", f"Then divide by {x}."],
            "explanation": f"{y} = {x}a + {b}\n{y - b} = {x}a\na = {a}.",
        }

    if difficulty == "hard":
        a = random.randint(2, 7)
        b = random.randint(-2, 7)
        c1 = random.randint(2, 5)
        c2 = random.randint(c1 + 1, 7)
        r1 = c1 * a + b
        r2 = c2 * a + b
        return {
            "type": "parameter_system",
            "difficulty": "hard",
            "question": f"{c1}a + b = {r1}\n{c2}a + b = {r2}\n\nFind a and b.",
            "variables": ["a", "b"],
            "answer": {"a": a, "b": b},
            "hints": [
                "The b terms match.",
                "Subtract the first equation from the second.",
                f"({c2}a + b) - ({c1}a + b) = {r2} - {r1}",
            ],
            "explanation": f"Subtracting cancels b: {(c2-c1)}a = {r2-r1}, so a = {a}. Substitute into {c1}a + b = {r1}: b = {b}.",
        }

    x1, x2 = random.randint(1, 5), random.randint(1, 5)
    w1, w2 = random.randint(1, 6), random.randint(1, 6)
    b = random.randint(-3, 4)
    y = w1 * x1 + w2 * x2 + b
    return {
        "type": "ai_parameters",
        "difficulty": "ai",
        "question": f"y = w₁x₁ + w₂x₂ + b\n\nx₁ = {x1}   x₂ = {x2}\nw₁ = {w1}  w₂ = {w2}  b = {b}\n\nFind y.",
        "variables": [],
        "answer": {"y": y},
        "hints": ["Substitute every value into the formula.", "Multiply each weight by its input.", "Then add the bias."],
        "explanation": f"y = {w1}({x1}) + {w2}({x2}) + ({b}) = {y}.",
    }


def binary_question(difficulty: str) -> dict:
    if difficulty == "easy":
        value = random.randint(1, 15)
        width = 4
    elif difficulty == "medium":
        value = random.randint(8, 63)
        width = 6
    elif difficulty == "hard":
        value = random.randint(0, 255)
        width = 8
    else:
        ch = random.choice("ABCDEHILNORSTU")
        return {
            "type": "binary_character",
            "difficulty": "ai",
            "direction": "binary_to_text",
            "question": f"Decode this 8-bit value: {format(ord(ch), '08b')}",
            "answer_text": ch,
            "hints": ["8 bits make one byte.", f"Its decimal value is {ord(ch)}.", "Map the ASCII value to a character."],
            "explanation": f"{format(ord(ch), '08b')} = {ord(ch)} in decimal, which is ASCII '{ch}'.",
        }
    binary = format(value, f"0{width}b")
    return {
        "type": "binary_to_decimal",
        "difficulty": difficulty,
        "question": f"Convert binary {binary} to decimal.",
        "answer_text": str(value),
        "hints": ["Write the place values from right to left.", f"Use powers of 2 up to 2^{width-1}.", f"The total is {value}."],
        "explanation": f"{binary} = {value} in decimal.",
    }


def normalize_fraction(value: str) -> Fraction | None:
    try:
        text = value.strip()
        if not text:
            return None
        if "/" in text:
            left, right = text.split("/", 1)
            return Fraction(int(left.strip()), int(right.strip()))
        return Fraction(text)
    except (ValueError, ZeroDivisionError):
        return None


def compare_number(user_value: str, expected: int | float | Fraction) -> bool:
    parsed = normalize_fraction(user_value)
    if parsed is None:
        return False
    return parsed == Fraction(expected)
