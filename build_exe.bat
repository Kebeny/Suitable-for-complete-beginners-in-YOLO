@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ==========================================
echo   YOLO 训练引导工具 - 打包 exe
echo ==========================================

python -m PyInstaller --clean --noconfirm "YOLO训练引导工具.spec"

if %errorlevel% neq 0 (
    echo.
    echo [失败] 打包失败，请检查上方错误信息。
    pause
    exit /b 1
)

echo.
echo [成功] 输出目录: dist\YOLO训练引导工具
pause
