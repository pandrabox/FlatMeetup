@echo off
chcp 65001 > nul
cd /d "%~dp0"
python AddNewPoster.py "%~1"
pause
