@echo off
REM Quick Start Script for AI Trading Lab PRO+ v4.0.0
REM Windows Batch File

echo ============================================================
echo   AI Trading Lab PRO+ v4.0.0
echo   Modern AI-Powered Trading Platform
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo Checking dependencies...
python start.py

pause

