@echo off
title Apna Desi Kirana Store Server
echo ===================================================
echo     APNA DESI KIRANA STORE (Full-Stack Web App)
echo ===================================================
echo Starting Flask Backend and Web Application...
echo.
echo Website URL: http://127.0.0.1:5000
echo.
cd /d "%~dp0backend"
python app.py
pause
