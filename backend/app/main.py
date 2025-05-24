from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import api_router

app = FastAPI(
    title="OpenPart API",
    description="开源零件数据管理系统",
    version="0.1.0"
)

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Vue开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "OpenPart API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)