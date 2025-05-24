# backend/app/api/routes.py (更新版本)
from fastapi import APIRouter
from app.auth.routes import router as auth_router
from app.api.admin.parts import router as admin_parts_router
from app.api.public.parts import router as public_parts_router

api_router = APIRouter()

# 认证路由
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])

# 管理员API
api_router.include_router(admin_parts_router, prefix="/admin/parts", tags=["管理员-零件"])

# 公开API - 注意这里的路由注册
api_router.include_router(public_parts_router, prefix="/public/parts", tags=["公开-零件"])