from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles  # 确保导入了这个
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import api_router
import os

app = FastAPI(
    title="OpenPart API",
    description="开源零件数据管理系统 - 安全版本",
    version="0.2.0"
)

# 创建静态文件目录（如果不存在）
os.makedirs("static/images/parts", exist_ok=True)

# 添加静态文件服务 - 这行很重要！
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "OpenPart API is running",
        "version": "0.2.0",
        "features": ["认证系统", "权限控制", "管理员API", "公开API", "图片上传"],
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.2.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)