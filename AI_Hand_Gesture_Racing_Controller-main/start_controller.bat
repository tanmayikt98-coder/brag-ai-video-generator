@echo off
title AI Hand Gesture Racing Controller - Dry Run
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python run.py --dry-run --calibration data/calibration/default.yaml
pause
