# AI Foundation Lab

A local, gamified AI-foundation learning app built around a developer-tool aesthetic.

## MVP included

- Dashboard with XP, streak, accuracy, progress, activity, achievements
- Parameter Mathematics + Parameter Battle
- Binary Teaching + Binary Decoder
- Text → Binary translator
- Binary → Text translator
- Dynamic question generation
- Progressive hints and post-answer explanations
- Adaptive difficulty hooks backed by recent results
- SQLite persistence
- Responsive GitHub/VS Code-inspired dark interface
- Optional light theme

The learning path is intentionally structured from fundamentals toward AI parameters and neural networks. fileciteturn0file0L1491-L1516

## Run locally

### 1. Create and activate a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Flask

```bash
pip install -r requirements.txt
```

### 3. Build TypeScript

```bash
tsc -p frontend/tsconfig.json
```

This writes the compiled client into `frontend/js/`.

### 4. Start Flask

```bash
python backend/app.py
```

Open http://127.0.0.1:5000

## Architecture

```text
ai-foundation-lab/
├── backend/
│   ├── app.py
│   ├── routes/
│   ├── services/
│   ├── models/
│   └── database/
├── frontend/
│   ├── index.html
│   ├── css/
│   └── ts/
├── data/
└── config/
```

The stack follows the requested Python/Flask + HTML/CSS/TypeScript + SQLite architecture. fileciteturn0file0L56-L83

## Windows shortcut

After Node.js is installed, double-click `start_windows.bat`. It creates the virtual environment, installs Flask, compiles TypeScript, and starts the local server.
