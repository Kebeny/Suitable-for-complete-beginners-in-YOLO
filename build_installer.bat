@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ==========================================
echo   YOLO 训练引导工具 - 生成安装包
echo ==========================================

where ISCC.exe >nul 2>nul
if %errorlevel%==0 (
    ISCC.exe "setup.iss"
) else (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "setup.iss"
)

if %errorlevel% neq 0 (
    echo.
    echo [失败] 安装包生成失败，请检查是否已安装 Inno Setup 6。
    pause
    exit /b 1
)

echo.
echo [成功] 安装包已生成：YOLO训练引导工具_Setup.exe
pause
