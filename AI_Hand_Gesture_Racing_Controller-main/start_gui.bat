@echo off
title AI Hand Gesture Racing Controller - Desktop Studio
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python gui.py
pause
