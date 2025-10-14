@echo off
echo ================================
echo Freedom AI - 启动脚本 (Windows)
echo ================================
echo.

REM 检查虚拟环境
if not exist "venv" (
    echo [1/4] 创建Python虚拟环境...
    python -m venv venv
) else (
    echo [1/4] 虚拟环境已存在
)

echo [2/4] 激活虚拟环境...
call venv\Scripts\activate.bat

echo [3/4] 安装依赖包...
pip install -r requirements.txt

echo [4/4] 启动服务...
echo.
echo 服务将在 http://localhost:8000 启动
echo API文档: http://localhost:8000/docs
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
