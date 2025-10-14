# Freedom AI - 智能对话助手系统

## 🌟 项目简介

Freedom AI 是一个具有人格化、长期记忆、主动交互能力的智能对话系统。它不仅能够响应你的消息，还能主动发起对话，记住你的偏好，管理日程，真正像朋友一样与你交流。

## ✨ 核心特性

- 🤖 **人格化对话** - AI可以主动发起聊天，拥有独特的交流风格
- 🧠 **长期记忆系统** - 记住用户的偏好、历史对话和重要信息
- 📅 **智能日程管理** - AI主动提醒和管理任务
- 🔌 **多LLM支持** - 支持OpenAI、Claude、Gemini、国产大模型等
- 💬 **桌面客户端** - 类似QQ的聊天界面，体验流畅
- ⚡ **轻量化设计** - 可运行在2C4G服务器上
- 🎨 **高度可定制** - 自定义AI人格、对话风格、功能模块

## 🏗️ 技术架构

### 后端技术栈
- **Web框架**: FastAPI (高性能异步框架)
- **数据库**: SQLite (轻量级关系数据库)
- **向量数据库**: ChromaDB (本地向量存储，用于记忆检索)
- **缓存**: Redis (可选，用于会话管理)
- **任务调度**: APScheduler (AI主动对话调度)
- **WebSocket**: 实时双向通信

### 前端技术栈
- **框架**: Electron + Vue3
- **UI组件**: Element Plus
- **状态管理**: Pinia
- **通信**: WebSocket + HTTP

### 系统架构图

```
┌─────────────────┐         ┌──────────────────────┐
│  Electron 客户端 │◄───────►│   FastAPI 后端服务    │
│   (Vue3 + UI)   │         │  ┌─────────────────┐ │
└─────────────────┘         │  │  LLM 适配器层   │ │
                            │  └─────────────────┘ │
      WebSocket             │  ┌─────────────────┐ │
       实时通信              │  │   记忆系统      │ │
                            │  │ (向量数据库)    │ │
                            │  └─────────────────┘ │
                            │  ┌─────────────────┐ │
                            │  │  主动对话引擎   │ │
                            │  └─────────────────┘ │
                            │  ┌─────────────────┐ │
                            │  │  日程管理系统   │ │
                            │  └─────────────────┘ │
                            └──────────────────────┘
```

## 📁 项目结构

```
freedom_ai/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── db/             # 数据库相关
│   │   ├── llm/            # LLM适配器
│   │   ├── memory/         # 记忆系统
│   │   ├── models/         # 数据模型
│   │   ├── scheduler/      # 任务调度
│   │   ├── services/       # 业务服务
│   │   └── main.py         # 应用入口
│   ├── tests/              # 测试文件
│   ├── requirements.txt    # Python依赖
│   └── .env.example        # 环境变量示例
├── frontend/               # 前端客户端
│   ├── src/
│   │   ├── components/     # Vue组件
│   │   ├── views/          # 页面视图
│   │   ├── store/          # 状态管理
│   │   └── main.js         # 应用入口
│   └── package.json        # Node依赖
└── docs/                   # 项目文档
    ├── API.md              # API文档
    ├── DEPLOYMENT.md       # 部署指南
    └── DEVELOPMENT.md      # 开发指南
```

## 🚀 快速开始

### 1. 后端服务启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env
# 编辑.env文件，填入你的LLM API密钥

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 前端客户端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 开发模式启动
npm run dev

# 构建桌面应用
npm run build
```

## ⚙️ 配置说明

### 环境变量配置 (.env)

```env
# LLM配置
LLM_PROVIDER=openai          # 可选: openai, claude, gemini, qwen等
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo

# 数据库配置
DATABASE_URL=sqlite:///./freedom_ai.db

# 服务器配置
HOST=0.0.0.0
PORT=8000

# AI人格配置
AI_NAME=小助手
AI_PERSONALITY=友好、幽默、善解人意

# 主动对话配置
PROACTIVE_CHAT_ENABLED=true
PROACTIVE_CHAT_INTERVAL=3600  # 秒
```

## 📚 核心功能说明

### 1. 人格化对话系统
AI会根据配置的人格特征进行对话，可以识别情感、调整语气、使用表情符号等，让交流更自然。

### 2. 长期记忆系统
- **短期记忆**: 保存最近的对话上下文
- **长期记忆**: 使用向量数据库存储重要信息
- **记忆检索**: 自动检索相关历史记忆增强对话质量

### 3. 主动对话引擎
- 根据用户活跃时间智能选择对话时机
- 基于用户兴趣和历史对话生成话题
- 日程提醒、节日问候、关心慰问等

### 4. 智能日程管理
- 自然语言创建任务和提醒
- AI主动提醒重要事项
- 日程冲突检测和建议

### 5. 多LLM适配
支持切换不同的LLM服务商，统一的接口设计让扩展变得简单。

## 🔧 开发指南

### 添加新的LLM适配器

```python
# 在 app/llm/adapters/ 下创建新的适配器
class YourLLMAdapter(BaseLLMAdapter):
    async def chat(self, messages: List[Dict]) -> str:
        # 实现你的LLM调用逻辑
        pass
```

### 自定义AI人格

编辑 `app/core/prompts.py` 中的系统提示词，或在配置中设置人格特征。

### 添加新功能模块

1. 在 `app/services/` 创建服务类
2. 在 `app/api/` 创建API路由
3. 在前端创建对应的UI组件

## 📊 性能优化

- **内存优化**: 使用流式响应，避免大量数据加载
- **数据库优化**: 合理使用索引，定期清理过期数据
- **缓存策略**: 缓存常用的LLM响应和记忆检索结果
- **异步处理**: 使用异步IO提高并发性能

## 🔒 安全性

- API密钥加密存储
- 用户数据本地化，不上传第三方
- WebSocket连接认证
- 敏感信息过滤

## 📝 开发计划

- [x] 阶段1: 项目架构搭建
- [ ] 阶段2: 后端核心功能实现
- [ ] 阶段3: 智能功能开发
- [ ] 阶段4: 前端客户端开发
- [ ] 阶段5: 集成测试与优化

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

## 📄 许可证

MIT License

## 💬 联系方式

如有问题，欢迎提Issue或Pull Request。

---

**享受与AI的智能对话吧！** 🎉
