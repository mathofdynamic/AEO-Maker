@echo off
REM LLM.txt Generator - Windows Startup Script
REM ==========================================
REM This script starts the LLM.txt Generator application on Windows

echo 🚀 Starting LLM.txt Generator...
echo ==========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if required packages are installed
echo 📦 Checking dependencies...
python -c "import flask, flask_socketio, openai, requests" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Some dependencies are missing. Installing...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Start the application
echo 🎯 Starting application...
python app.py

REM If we get here, the application has stopped
echo.
echo 🛑 Application stopped
pause
