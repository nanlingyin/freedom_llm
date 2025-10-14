# Freedom AI - 开发指南

## 开发环境准备

### 1. 系统要求

- **操作系统**: Windows / Linux / macOS
- **Python**: 3.9 或更高版本
- **内存**: 最低 2GB，推荐 4GB
- **硬盘**: 至少 2GB 可用空间

### 2. 安装依赖

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env`，然后编辑配置：

```bash
cp .env.example .env
```

**必须配置的项**:
```env
# LLM配置 (必填)
LLM_PROVIDER=openai
LLM_API_KEY=your-api-key-here
LLM_MODEL=gpt-3.5-turbo

# AI人格配置
AI_NAME=小艾
AI_PERSONALITY=你是一个友好、幽默、善解人意的AI助手...
```

---

## 项目结构详解

```
backend/
├── app/
│   ├── api/              # API路由层
│   │   └── v1/
│   │       ├── api.py           # 路由聚合
│   │       └── endpoints/       # 各个端点
│   │           ├── chat.py      # 聊天接口
│   │           ├── users.py     # 用户接口
│   │           └── websocket.py # WebSocket接口
│   ├── core/             # 核心配置
│   │   ├── config.py     # 配置管理
│   │   ├── logging.py    # 日志配置
│   │   └── prompts.py    # 提示词模板
│   ├── db/               # 数据库
│   │   ├── database.py   # 数据库配置
│   │   └── session.py    # 会话管理
│   ├── llm/              # LLM适配器
│   │   ├── adapters/     # 各厂商适配器
│   │   │   ├── base.py          # 基类
│   │   │   ├── openai_adapter.py
│   │   │   └── claude_adapter.py
│   │   └── factory.py    # 工厂类
│   ├── memory/           # 记忆系统
│   │   ├── vector_store.py      # 向量存储
│   │   └── memory_manager.py    # 记忆管理
│   ├── models/           # 数据模型
│   │   ├── user.py       # 用户模型
│   │   ├── message.py    # 消息模型
│   │   ├── memory.py     # 记忆模型
│   │   └── schedule.py   # 日程模型
│   ├── scheduler/        # 定时任务
│   │   ├── proactive_chat.py    # 主动对话
│   │   └── schedule_reminder.py # 日程提醒
│   ├── services/         # 业务服务
│   │   ├── chat_service.py      # 聊天服务
│   │   ├── user_service.py      # 用户服务
│   │   └── schedule_service.py  # 日程服务
│   └── main.py           # 应用入口
├── tests/                # 测试文件
├── requirements.txt      # Python依赖
├── .env                  # 环境变量
└── start.bat / start.sh  # 启动脚本
```

---

## 核心模块说明

### 1. LLM适配器层 (`app/llm/`)

**作用**: 统一不同LLM提供商的接口

**添加新的LLM适配器**:

```python
# app/llm/adapters/custom_adapter.py
from app.llm.adapters.base import BaseLLMAdapter

class CustomAdapter(BaseLLMAdapter):
    async def chat(self, messages, temperature, max_tokens):
        # 实现你的LLM调用逻辑
        pass
    
    async def chat_stream(self, messages, temperature, max_tokens):
        # 实现流式调用
        pass
    
    def count_tokens(self, text):
        # 实现token计数
        pass

# 在 factory.py 中注册
from app.llm.factory import LLMFactory
LLMFactory.register_adapter("custom", CustomAdapter)
```

### 2. 记忆系统 (`app/memory/`)

**组成**:
- **向量存储 (ChromaDB)**: 用于语义检索
- **关系数据库 (SQLite)**: 存储元数据
- **记忆管理器**: 协调两者工作

**工作流程**:
1. 用户消息 → 提取重要信息
2. 重要信息 → 向量化存储
3. 新消息来临 → 检索相关记忆
4. 相关记忆 → 加入对话上下文

### 3. 主动对话系统 (`app/scheduler/proactive_chat.py`)

**触发条件**:
- 用户在线
- 当前时间在活跃时段
- 距离上次主动消息超过最小间隔
- 随机概率触发（增加自然性）

**定制方法**:

修改 `app/core/prompts.py` 中的 `get_proactive_chat_prompt()`:

```python
@staticmethod
def get_proactive_chat_prompt(user_info, recent_topics):
    return f"""
    作为AI助手，根据以下信息生成主动问候：
    用户信息: {user_info}
    最近话题: {recent_topics}
    
    生成一条自然、友好的主动消息...
    """
```

### 4. 日程管理系统 (`app/services/schedule_service.py`)

**功能**:
- 自动从对话中提取日程信息
- 定时检查并发送提醒
- 支持优先级和重复规则

---

## 开发工作流

### 1. 启动开发服务器

```bash
# Windows
start.bat

# Linux/Mac
chmod +x start.sh
./start.sh

# 或直接运行
uvicorn app.main:app --reload
```

访问 http://localhost:8000/docs 查看API文档

### 2. 数据库管理

**查看数据库**:
```bash
sqlite3 freedom_ai.db
.tables
.schema users
SELECT * FROM users;
```

**重置数据库**:
删除 `freedom_ai.db` 和 `chroma_db/` 目录，重新启动服务

### 3. 日志查看

日志文件位置: `logs/app.log`

```bash
# 实时查看日志
tail -f logs/app.log
```

### 4. 测试

```bash
# 运行测试
pytest tests/

# 运行特定测试
pytest tests/test_chat.py -v
```

---

## 自定义开发

### 1. 修改AI人格

编辑 `.env` 文件:

```env
AI_NAME=你的AI名字
AI_PERSONALITY=你是一个...的AI助手
AI_GENDER=female
AI_AGE=25
```

或直接修改 `app/core/prompts.py` 中的系统提示词。

### 2. 添加新的API端点

```python
# app/api/v1/endpoints/custom.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/custom")
async def custom_endpoint():
    return {"message": "自定义端点"}

# 在 app/api/v1/api.py 中注册
from app.api.v1.endpoints import custom
api_router.include_router(custom.router, prefix="/custom", tags=["custom"])
```

### 3. 添加新的服务

```python
# app/services/custom_service.py
from sqlalchemy.orm import Session

class CustomService:
    def __init__(self, db: Session):
        self.db = db
    
    def custom_method(self):
        # 实现你的业务逻辑
        pass

def get_custom_service(db: Session) -> CustomService:
    return CustomService(db)
```

### 4. 自定义记忆分类

修改 `app/memory/memory_manager.py`:

```python
# 创建记忆时指定分类
await memory_manager.create_memory(
    user_id=user_id,
    content="用户喜欢吃披萨",
    category="food_preference",  # 自定义分类
    importance=0.8
)

# 检索特定分类的记忆
memories = await memory_manager.retrieve_relevant_memories(
    user_id=user_id,
    query="食物",
    category="food_preference"
)
```

---

## 性能优化建议

### 1. 数据库优化

- 定期清理旧消息和低重要性记忆
- 为常用查询字段添加索引
- 使用连接池管理数据库连接

### 2. LLM调用优化

- 缓存常见问题的回答
- 控制上下文长度，避免token浪费
- 使用流式响应提升用户体验

### 3. 内存管理

- 限制短期记忆数量 (`SHORT_TERM_MEMORY_SIZE`)
- 设置记忆重要性阈值
- 定期归档历史数据

---

## 常见问题

### 1. LLM API调用失败

**检查项**:
- API密钥是否正确
- 网络连接是否正常
- 是否使用了代理 (设置 `LLM_BASE_URL`)

### 2. 向量数据库初始化失败

**解决方法**:
```bash
# 清除旧数据
rm -rf chroma_db/
# 重新启动服务
```

### 3. WebSocket连接断开

**原因**:
- 网络不稳定
- 服务器重启
- 超时未活动

**解决**: 客户端实现自动重连机制

---

## 调试技巧

### 1. 启用详细日志

在 `.env` 中设置:
```env
LOG_LEVEL=DEBUG
```

### 2. 使用 Python 调试器

```python
import pdb; pdb.set_trace()  # 设置断点
```

### 3. 查看SQL语句

在 `app/db/database.py` 中设置:
```python
engine = create_engine(
    settings.database_url,
    echo=True  # 打印SQL语句
)
```

---

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 资源链接

- **FastAPI文档**: https://fastapi.tiangolo.com/
- **SQLAlchemy文档**: https://docs.sqlalchemy.org/
- **ChromaDB文档**: https://docs.trychroma.com/
- **OpenAI API文档**: https://platform.openai.com/docs

---

祝开发愉快! 🚀
