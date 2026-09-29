@echo off
REM DataSense AI - Quick Start Script
REM This script helps set up and run the DataSense AI application

echo ========================================
echo DataSense AI - Setup & Launch
echo ========================================
echo.

REM Check for Python
echo Checking for Python...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python not found. Please install Python 3.8 or higher.
    echo Download from: https://www.python.org/downloads/
    echo.
    echo After installing, run this script again.
    pause
    exit /b 1
)

echo Python found!
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Warning: Some dependencies may have failed to install.
    echo Trying to continue anyway...
)

REM Run the application
echo.
echo ========================================
echo Starting DataSense AI...
echo ========================================
python run.py

REM Deactivate virtual environment
deactivate 2>nul

pause