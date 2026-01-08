@echo off
title Tender System - Database Seeder
echo ========================================
echo   Tender System Database Seeder
echo ========================================
echo This will create the initial demo users:
echo admin, sales, client, vendor, finance
echo.
echo Make sure the BACKEND is RUNNING before seeding.
echo.
set /p proceed="Continue? (Y/N): "
if /i "%proceed%" neq "Y" exit /b

python -m backend.seed

echo.
echo ========================================
echo   Seeding process finished.
echo ========================================
pause
