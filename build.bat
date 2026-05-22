@echo off
chcp 65001 >nul
title AVT Subtitle Processor - Build

cd /d "%~dp0"

echo ========================================
echo AVT Subtitle Processor 构建脚本
echo ========================================
echo.

REM 检查是否使用虚拟环境
if "%PADDLEOCR_VENV%"=="" (
    if exist "D:\Software\PaddleOCR_gpu\venv\Scripts\python.exe" (
        set PADDLEOCR_VENV=D:\Software\PaddleOCR_gpu\venv
        echo [INFO] 使用 PaddleOCR 虚拟环境: %PADDLEOCR_VENV%
    ) else (
        echo [ERROR] 未找到 PaddleOCR 虚拟环境
        echo 请设置 PADDLEOCR_VENV 环境变量
        pause
        exit /b 1
    )
) else (
    echo [INFO] 使用环境变量指定: %PADDLEOCR_VENV%
)

echo.
echo [1/5] 清理旧的构建文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"
echo [OK] 清理完成

echo.
echo [2/5] 运行 PyInstaller...
"%PADDLEOCR_VENV%\Scripts\python.exe" -m PyInstaller AVT_Subtitle_Processor.spec --clean

if errorlevel 1 (
    echo.
    echo [ERROR] PyInstaller 构建失败！
    pause
    exit /b 1
)

echo.
echo [3/5] 复制 FFmpeg 到打包目录...
if exist "bin\ffmpeg.exe" (
    if not exist "dist\AVT_Subtitle_Processor\_internal\bin" mkdir "dist\AVT_Subtitle_Processor\_internal\bin"
    copy /Y "bin\ffmpeg.exe" "dist\AVT_Subtitle_Processor\_internal\bin\" >nul
    copy /Y "bin\ffprobe.exe" "dist\AVT_Subtitle_Processor\_internal\bin\" >nul
    echo [OK] FFmpeg 已复制到 _internal\bin\
) else (
    echo [WARN] bin\ffmpeg.exe 未找到，请确保 bin 目录下有 FFmpeg
)

echo.
echo [4/5] 清理临时文件...
if exist "build" rmdir /s /q "build"

echo.
echo [5/5] 验证输出...
if exist "dist\AVT_Subtitle_Processor\AVT_Subtitle_Processor.exe" (
    echo [OK] 可执行文件已生成: dist\AVT_Subtitle_Processor\AVT_Subtitle_Processor.exe
) else (
    echo [ERROR] 未找到生成的可执行文件
    pause
    exit /b 1
)

echo.
echo ========================================
echo 构建成功！
echo ========================================
echo.
echo 输出目录: %~dp0dist\AVT_Subtitle_Processor
echo.
echo 下一步:
echo   1. 进入 dist 目录
echo   2. 测试运行 AVT_Subtitle_Processor.exe
echo   3. 如果正常，可以打包整个文件夹分发
echo.
echo 按任意键打开输出目录...
start explorer "dist"
pause
