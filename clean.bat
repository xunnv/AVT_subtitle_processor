@echo off
chcp 65001 >nul
title AVT Subtitle Processor - Clean

cd /d "%~dp0"

echo 清理构建临时文件...
echo.

if exist "build" (
    echo [删除] build 目录
    rmdir /s /q "build"
)

if exist "dist" (
    echo [删除] dist 目录
    rmdir /s /q "dist"
)

if exist "*.spec.bak" (
    echo [删除] *.spec.bak 文件
    del /q "*.spec.bak"
)

if exist "__pycache__" (
    echo [删除] __pycache__ 目录
    rmdir /s /q "__pycache__"
)

for /d /r . %%d in (__pycache__) do (
    if exist "%%d" (
        echo [删除] %%d
        rmdir /s /q "%%d"
    )
)

echo.
echo 清理完成！
pause
