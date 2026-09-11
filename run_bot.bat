@echo off
chcp 65001 > nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
title Goldenbot - Sandekalabot Telegram Bot
color 0A
echo ====================================================
echo Starting Telegram Bot (Goldenbot @sandekalabot)...
echo ====================================================

:loop
"%~dp0.venv\Scripts\python.exe" main.py
echo.
echo [WARNING] Bot berhenti atau crash. Me-restart dalam 5 detik...
timeout /t 5
goto loop
