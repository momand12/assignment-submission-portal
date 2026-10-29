@echo off
title Assignment Submission Portal - port 5000
cd /d "%~dp0"
echo Starting the portal. Open http://localhost:5000 in your browser. Keep this window open.
".venv\Scripts\python.exe" app.py
pause
