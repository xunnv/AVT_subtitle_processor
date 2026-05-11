@echo off
chcp 65001 >nul
title AVT Subtitle Processor

cd /d "%~dp0"

if "%PADDLEOCR_VENV%"=="" (
    if exist "D:\Software\PaddleOCR_gpu\venv\Scripts\python.exe" (
        set PADDLEOCR_VENV=D:\Software\PaddleOCR_gpu\venv
    ) else (
        echo Error: PaddleOCR environment not found.
        echo Please set PADDLEOCR_VENV environment variable or install PaddleOCR GPU environment.
        pause
        exit /b 1
    )
)

echo Starting application...
"%PADDLEOCR_VENV%\Scripts\python.exe" main.py

if errorlevel 1 (
    echo.
    echo Error occurred!
    pause
)
