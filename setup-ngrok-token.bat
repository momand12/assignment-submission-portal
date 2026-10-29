@echo off
title ngrok one-time setup
rem Use the ngrok 3.3.1 copy installed by winget. The newer copy is blocked by Windows Defender.
set NGROK=%LOCALAPPDATA%\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe
set CONFIG=%LOCALAPPDATA%\ngrok\ngrok.yml
echo ================================================================
echo  ngrok one-time setup
echo  1. In the ngrok dashboard, open "Your Authtoken" and click Copy.
echo  2. Click inside this window, press Ctrl+V to paste, then Enter.
echo ================================================================

:ask
echo.
set NGROK_TOKEN=
set /p NGROK_TOKEN=Paste your ngrok authtoken here: 
if "%NGROK_TOKEN%"=="" (
  echo Nothing was pasted. Copy the token again and press Ctrl+V.
  goto ask
)
"%NGROK%" config add-authtoken %NGROK_TOKEN% --config "%CONFIG%"
set NGROK_TOKEN=

echo.
if exist "%CONFIG%" (
  echo ****************************
  echo   SUCCESS - token is saved
  echo ****************************
) else (
  echo ****************************
  echo   FAILED - please try again
  echo ****************************
)
pause
