@echo off
title ngrok tunnel - port 5050
rem Your free static ngrok domain (from dashboard.ngrok.com -> Domains)
set NGROK_DOMAIN=PUT-YOUR-DOMAIN-HERE.ngrok-free.app
echo Opening tunnel https://%NGROK_DOMAIN% -^> http://localhost:5050
echo Keep this window open while you push and during the demo.
ngrok http 5050 --domain=%NGROK_DOMAIN%
pause
