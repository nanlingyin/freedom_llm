"""
Freedom AI - 智能对话助手系统
主程序入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import app_logger
from app.db.database import init_db
from app.api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    app_logger.info("=" * 50)
    app_logger.info("Freedom AI 启动中...")
    app_logger.info(f"LLM提供商: {settings.llm_provider}")
    app_logger.info(f"AI名称: {settings.ai_name}")
    app_logger.info(f"主动对话: {'启用' if settings.proactive_chat_enabled else '禁用'}")
    
    # 初始化数据库
    init_db()
    app_logger.info("数据库初始化完成")
    
    # 初始化向量数据库
    from app.memory.vector_store import get_vector_store
    get_vector_store()
    app_logger.info("向量数据库初始化完成")
    
    # 启动定时任务
    if settings.proactive_chat_enabled:
        from app.scheduler.proactive_chat import start_proactive_chat_scheduler
        start_proactive_chat_scheduler()
        app_logger.info("主动对话调度器已启动")
    
    from app.scheduler.schedule_reminder import start_schedule_reminder
    start_schedule_reminder()
    app_logger.info("日程提醒调度器已启动")
    
    app_logger.info("Freedom AI 启动完成!")
    app_logger.info("=" * 50)
    
    yield
    
    # 关闭时执行
    app_logger.info("Freedom AI 正在关闭...")


# 创建FastAPI应用
app = FastAPI(
    title="Freedom AI",
    description="智能对话助手系统 - 具有人格化、长期记忆、主动交互能力",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": f"欢迎使用 Freedom AI - {settings.ai_name}",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "ai_name": settings.ai_name,
        "llm_provider": settings.llm_provider
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
