@echo off
title Save Gmail app password as a GitHub secret
echo ================================================================
echo  Saves your Gmail APP PASSWORD as the GitHub secret SMTP_PASSWORD
echo  1. Copy the 16-letter app password from Google.
echo  2. Click inside this window, press Ctrl+V, then Enter.
echo     (Nothing shows while you paste - that is normal.)
echo ================================================================
echo.
gh secret set SMTP_PASSWORD --repo momand12/assignment-submission-portal
echo.
gh secret list --repo momand12/assignment-submission-portal | findstr SMTP_PASSWORD >nul && (
  echo ****************************************
  echo   SUCCESS - SMTP_PASSWORD is saved
  echo ****************************************
) || (
  echo ****************************************
  echo   FAILED - please try again
  echo ****************************************
)
pause
