# Freedom AI - 部署指南

## 部署方式

本项目支持多种部署方式，适合不同的使用场景。

---

## 方式一: 本地直接运行（推荐用于开发测试）

### Windows

```bash
# 1. 进入项目目录
cd freedom_ai\backend

# 2. 运行启动脚本
start.bat
```

### Linux/Mac

```bash
# 1. 进入项目目录
cd freedom_ai/backend

# 2. 添加执行权限
chmod +x start.sh

# 3. 运行启动脚本
./start.sh
```

---

## 方式二: 使用 Systemd 服务（Linux生产环境）

### 1. 创建服务文件

```bash
sudo nano /etc/systemd/system/freedom-ai.service
```

内容:
```ini
[Unit]
Description=Freedom AI Service
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/freedom_ai/backend
Environment="PATH=/path/to/freedom_ai/backend/venv/bin"
ExecStart=/path/to/freedom_ai/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. 启动服务

```bash
# 重新加载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start freedom-ai

# 设置开机自启
sudo systemctl enable freedom-ai

# 查看状态
sudo systemctl status freedom-ai

# 查看日志
sudo journalctl -u freedom-ai -f
```

---

## 方式三: 使用 Docker 部署

### 1. 创建 Dockerfile

在 `backend/` 目录创建 `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p logs chroma_db

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. 创建 docker-compose.yml

在项目根目录创建:

```yaml
version: '3.8'

services:
  freedom-ai:
    build: ./backend
    container_name: freedom-ai
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    volumes:
      - ./backend/freedom_ai.db:/app/freedom_ai.db
      - ./backend/chroma_db:/app/chroma_db
      - ./backend/logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 3. 部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 方式四: 使用 Nginx 反向代理

### 1. 安装 Nginx

```bash
# Ubuntu/Debian
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

### 2. 配置 Nginx

创建配置文件 `/etc/nginx/sites-available/freedom-ai`:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名

    # HTTP 请求
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket 连接
    location /api/v1/ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 静态文件（如果有前端）
    location / {
        root /var/www/freedom-ai;
        try_files $uri $uri/ /index.html;
    }
}
```

### 3. 启用配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/freedom-ai /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

### 4. 配置 HTTPS (可选但推荐)

使用 Let's Encrypt:

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

---

## 性能优化配置

### 1. 使用 Gunicorn + Uvicorn Workers

安装:
```bash
pip install gunicorn
```

启动命令:
```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --keep-alive 5
```

### 2. 配置进程管理器

使用 Supervisor (推荐):

```ini
[program:freedom-ai]
command=/path/to/venv/bin/gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
directory=/path/to/freedom_ai/backend
user=your-username
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/path/to/logs/freedom-ai.log
```

---

## 2C4G 服务器部署建议

### 系统要求

- **CPU**: 2核心
- **内存**: 4GB RAM
- **硬盘**: 至少 20GB
- **操作系统**: Ubuntu 20.04+ / CentOS 7+

### 优化配置

#### 1. 限制并发数

在 `.env` 中:
```env
# 减少记忆检索数量
LONG_TERM_MEMORY_RETRIEVE_SIZE=3
SHORT_TERM_MEMORY_SIZE=10

# 减少token使用
LLM_MAX_TOKENS=1500
```

#### 2. 使用轻量级模型

```env
LLM_MODEL=gpt-3.5-turbo  # 或其他轻量级模型
```

#### 3. Worker配置

```bash
# 2核心服务器建议使用2-3个workers
gunicorn app.main:app \
  --workers 2 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

#### 4. 数据库优化

定期清理:
```sql
-- 删除30天前的消息
DELETE FROM messages WHERE created_at < datetime('now', '-30 days');

-- 删除低重要性的记忆
DELETE FROM memories WHERE importance < 0.3 AND created_at < datetime('now', '-7 days');
```

---

## 监控和日志

### 1. 日志轮转

安装 logrotate:

```bash
sudo nano /etc/logrotate.d/freedom-ai
```

内容:
```
/path/to/freedom_ai/backend/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### 2. 性能监控

使用 htop 监控资源:
```bash
sudo apt install htop
htop
```

### 3. 应用监控

查看API响应时间:
```bash
# 查看日志中的慢请求
grep "took" logs/app.log | grep -v "took [0-9]\+ms"
```

---

## 备份策略

### 1. 数据库备份

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 备份SQLite数据库
cp freedom_ai.db "$BACKUP_DIR/freedom_ai_$DATE.db"

# 备份向量数据库
tar -czf "$BACKUP_DIR/chroma_db_$DATE.tar.gz" chroma_db/

# 删除7天前的备份
find "$BACKUP_DIR" -name "*.db" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete
```

### 2. 设置定时备份

```bash
# 添加到crontab
crontab -e

# 每天凌晨2点备份
0 2 * * * /path/to/backup.sh
```

---

## 安全建议

### 1. 防火墙配置

```bash
# 只开放必要端口
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 2. API密钥保护

- 不要将 `.env` 文件提交到Git
- 使用环境变量或密钥管理服务
- 定期轮换API密钥

### 3. 限流配置

使用 Nginx 限流:

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /api {
    limit_req zone=api_limit burst=20 nodelay;
    proxy_pass http://localhost:8000;
}
```

---

## 故障排查

### 常见问题

#### 1. 服务无法启动

```bash
# 检查端口占用
sudo lsof -i :8000

# 查看错误日志
tail -f logs/app.log
```

#### 2. 内存不足

```bash
# 查看内存使用
free -h

# 减少worker数量或重启服务
```

#### 3. 数据库锁定

```bash
# SQLite数据库锁定时重启服务
sudo systemctl restart freedom-ai
```

---

## 升级指南

### 1. 备份数据

```bash
cp freedom_ai.db freedom_ai.db.backup
cp -r chroma_db chroma_db.backup
```

### 2. 拉取新代码

```bash
git pull origin main
```

### 3. 更新依赖

```bash
pip install -r requirements.txt --upgrade
```

### 4. 重启服务

```bash
sudo systemctl restart freedom-ai
```

---

## 联系支持

如有问题，请查看:
- 项目文档: `/docs`
- Issue追踪: GitHub Issues
- 日志文件: `logs/app.log`

---

部署成功! 🎉
