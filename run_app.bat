@echo off
title Tender Procurement System - Runner
echo ========================================
echo   Tender Procurement System Launcher
echo ========================================

:: Check for python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python and add it to your PATH.
    pause
    exit /b
)

echo [1/3] Checking dependencies...
pip install fastapi uvicorn sqlalchemy pyside6 requests >nul 2>&1

echo [2/3] Starting Backend Server in a NEW window...
echo       (Keep the backend window open while using the app)
start "Tender Backend API" cmd /c "python -m backend.main"

echo [3/3] Waiting for backend to initialize (5s)...
timeout /t 5 /nobreak > nul

echo [SUCCESS] Launching Frontend Application...
python -m frontend.main

echo ========================================
echo   Application Closed.
echo ========================================
pause
