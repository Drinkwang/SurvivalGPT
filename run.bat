@echo off
chcp 65001 >nul
echo ========================================
echo    🔥 SurvivalGPT - AI末日生存专家 🔥
echo ========================================
echo.
echo 正在启动程序，请稍候...
echo.

:: 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到Python环境
    echo 请先运行 install.bat 进行安装
    pause
    exit /b 1
)

:: 启动程序
echo 🚀 启动SurvivalGPT...
python main.py

:: 程序结束后暂停
echo.
echo 程序已退出
pause