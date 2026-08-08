@echo off
REM Engineering AI Agent Frontend 快速启动脚本（Windows）

echo.
echo 🚀 Engineering AI Agent Frontend 启动中...
echo.

REM 检查Node.js是否安装
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js未安装，请先安装Node.js
    pause
    exit /b 1
)

REM 检查npm是否安装
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ npm未安装，请先安装npm
    pause
    exit /b 1
)

echo ✅ 环境检查通过
echo.

REM 检查node_modules是否存在
if not exist "node_modules" (
    echo 📦 首次运行，正在安装依赖...
    call npm install
    if %errorlevel% neq 0 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
    echo ✅ 依赖安装完成
    echo.
)

echo 🌐 启动前端开发服务器...
echo.
echo 📝 访问地址: http://localhost:5173
echo.
echo 🛑 停止服务: 按 Ctrl+C
echo.

REM 启动Vite开发服务器
call npm run dev

pause
