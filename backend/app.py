from __future__ import annotations

from pathlib import Path
from flask import Flask, send_from_directory

from backend.database.db import init_db
from backend.routes.api import api

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"


def create_app() -> Flask:
    app = Flask(__name__, static_folder=str(FRONTEND), static_url_path="")
    init_db()
    app.register_blueprint(api)

    @app.get("/")
    def index():
        return send_from_directory(FRONTEND, "index.html")

    @app.get("/js/<path:filename>")
    def js(filename: str):
        return send_from_directory(FRONTEND / "js", filename)

    @app.get("/css/<path:filename>")
    def css(filename: str):
        return send_from_directory(FRONTEND / "css", filename)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
