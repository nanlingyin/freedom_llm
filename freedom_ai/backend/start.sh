#!/bin/bash

echo "================================"
echo "Freedom AI - 启动脚本 (Linux/Mac)"
echo "================================"
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "[1/4] 创建Python虚拟环境..."
    python3 -m venv venv
else
    echo "[1/4] 虚拟环境已存在"
fi

echo "[2/4] 激活虚拟环境..."
source venv/bin/activate

echo "[3/4] 安装依赖包..."
pip install -r requirements.txt

echo "[4/4] 启动服务..."
echo ""
echo "服务将在 http://localhost:8000 启动"
echo "API文档: http://localhost:8000/docs"
echo ""
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
