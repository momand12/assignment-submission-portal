@echo off
title Report Receiver - port 5050
cd /d "%~dp0"
echo Starting the report receiver on port 5050. Keep this window open.
".venv\Scripts\python.exe" receiver\receiver.py
pause
