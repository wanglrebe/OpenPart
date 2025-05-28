# backend/app/api/routes.py (修复版本 - 添加插件管理路由)
from fastapi import APIRouter
from app.auth.routes import router as auth_router
from app.api.admin.parts import router as admin_parts_router
from app.api.admin.upload import router as admin_upload_router
from app.api.admin.import_export import router as import_export_router
from app.api.admin.crawler_plugins import router as crawler_plugins_router  # 添加这行！
from app.api.public.parts import router as public_parts_router
from app.api.public.compare import router as compare_router

api_router = APIRouter()

# 认证路由
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])

# 管理员API
api_router.include_router(admin_parts_router, prefix="/admin/parts", tags=["管理员-零件"])
api_router.include_router(admin_upload_router, prefix="/admin/upload", tags=["管理员-上传"])
api_router.include_router(import_export_router, prefix="/admin/import-export", tags=["管理员-导入导出"])
api_router.include_router(crawler_plugins_router, prefix="/admin/crawler-plugins", tags=["管理员-插件管理"])  # 添加这行！

# 公开API
api_router.include_router(public_parts_router, prefix="/public/parts", tags=["公开-零件"])
api_router.include_router(compare_router, prefix="/public/compare", tags=["公开-对比"])