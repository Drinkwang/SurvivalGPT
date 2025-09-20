@echo off
chcp 65001 >nul
echo ========================================
echo    AI末日生存求生向导软件 - 安装程序
echo ========================================
echo.

echo [1/4] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到Python环境
    echo 请先安装Python 3.8或更高版本
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python环境检查通过
echo.

echo [2/4] 检查pip工具...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到pip工具
    echo 请确保pip已正确安装
    pause
    exit /b 1
)

echo ✅ pip工具检查通过
echo.

echo [3/4] 安装依赖包...
echo 正在安装必要的Python包，请稍候...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ 依赖包安装失败
    echo 请检查网络连接或手动安装依赖包
    pause
    exit /b 1
)

echo ✅ 依赖包安装完成
echo.

echo [4/4] 创建启动脚本...
echo @echo off > run.bat
echo chcp 65001 ^>nul >> run.bat
echo echo 启动AI末日生存求生向导软件... >> run.bat
echo python main.py >> run.bat
echo pause >> run.bat

echo ✅ 启动脚本创建完成
echo.

echo ========================================
echo           安装完成！
echo ========================================
echo.
echo 使用方法：
echo 1. 双击 run.bat 启动程序
echo 2. 或者在命令行中运行：python main.py
echo.
echo 如遇问题，请查看README.md文件
echo.
pause