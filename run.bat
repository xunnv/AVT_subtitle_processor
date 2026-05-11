@echo off
chcp 65001 >nul
title AVT Subtitle Processor

cd /d "%~dp0"

REM 设置 PaddleOCR 环境路径
REM 请根据实际情况修改此路径
if "%PADDLEOCR_VENV%"=="" (
    set PADDLEOCR_VENV=D:\Software\PaddleOCR_gpu\venv
)

echo Starting application...
"%PADDLEOCR_VENV%\Scripts\python.exe" main.py

if errorlevel 1 (
    echo.
    echo Error occurred!
    pause
)
