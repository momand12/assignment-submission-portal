@echo off
title ngrok tunnel - port 5050
cd /d "%~dp0"
echo Starting the ngrok tunnel to http://localhost:5050. Keep this window open.
".venv\Scripts\python.exe" receiver\tunnel.py
pause
