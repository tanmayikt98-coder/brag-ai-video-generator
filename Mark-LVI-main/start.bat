@echo off
cd /d "%~dp0"
py -3.13 -X utf8 main.py
if errorlevel 1 pause
