@echo off
setlocal enabledelayedexpansion

:: --- SETTINGS ---
set "ROOM_ID=6a27ac89e858fd2002302b10"
set "TOKEN=04283e4c562763702122cebce3ccf27689e0d61cd2b44b2acd03d548c7b90cbb"
set "PROJECT_DIR=C:\Users\mdsai\Documents\hr bot"
set "VENV_PATH=%PROJECT_DIR%\.venv\Scripts\activate"

:: --- INITIALIZATION ---
cd /d "%PROJECT_DIR%"
title Highrise Bot Manager

echo [!] Launching Bot...
call "%VENV_PATH%"

:: --- START BOT ---
python -m highrise main:Bot %ROOM_ID% %TOKEN%

:: --- CRASH CATCHER ---
echo.
echo [!] The bot has stopped. If you see an error above, it is listed here.
pause