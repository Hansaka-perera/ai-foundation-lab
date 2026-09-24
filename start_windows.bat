@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  py -m venv .venv
)
call ".venv\Scripts\activate.bat"
python -m pip install -r requirements.txt
where tsc >nul 2>nul
if errorlevel 1 (
  echo TypeScript compiler not found. Install Node.js, then run: npm install -g typescript
  exit /b 1
)
tsc -p frontend\tsconfig.json
python backend\app.py
