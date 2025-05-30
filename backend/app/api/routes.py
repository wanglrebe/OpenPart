# backend/app/api/routes.py (修复版本 - 添加兼容性管理路由)
from fastapi import APIRouter
from app.auth.routes import router as auth_router
from app.api.admin.parts import router as admin_parts_router
from app.api.admin.upload import router as admin_upload_router
from app.api.admin.import_export import router as import_export_router
from app.api.admin.crawler_plugins import router as crawler_plugins_router
from app.api.admin.compatibility import router as admin_compatibility_router  # 新增兼容性管理
from app.api.public.parts import router as public_parts_router
from app.api.public.compare import router as compare_router
from app.api.public.compatibility import router as public_compatibility_router  # 新增公开兼容性API
from app.api.admin.image_download import router as image_download_router
from app.api.admin.file_upload import router as file_upload_router

api_router = APIRouter()

# ==================== 认证路由 ====================
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])

# ==================== 管理员API ====================
# 零件管理
api_router.include_router(admin_parts_router, prefix="/admin/parts", tags=["管理员-零件"])

# 文件和图片管理
api_router.include_router(admin_upload_router, prefix="/admin/upload", tags=["管理员-上传"])
api_router.include_router(image_download_router, prefix="/admin/images", tags=["管理员-图片下载"])
api_router.include_router(file_upload_router, prefix="/admin/files", tags=["管理员-文件上传"])

# 数据导入导出
api_router.include_router(import_export_router, prefix="/admin/import-export", tags=["管理员-导入导出"])

# 爬虫插件管理
api_router.include_router(crawler_plugins_router, prefix="/admin/crawler-plugins", tags=["管理员-插件管理"])

# 兼容性管理（新增）
api_router.include_router(admin_compatibility_router, prefix="/admin/compatibility", tags=["管理员-兼容性管理"])

# ==================== 公开API ====================
# 零件查询
api_router.include_router(public_parts_router, prefix="/public/parts", tags=["公开-零件"])

# 零件对比
api_router.include_router(compare_router, prefix="/public/compare", tags=["公开-对比"])

# 兼容性检查（新增）
api_router.include_router(public_compatibility_router, prefix="/public/compatibility", tags=["公开-兼容性检查"])

# ==================== API文档和元信息 ====================

@api_router.get("/", tags=["系统信息"])
async def root():
    """
    API根端点 - 返回系统信息
    """
    return {
        "name": "OpenPart API",
        "version": "1.0.0",
        "description": "开源零件仓库管理系统API",
        "features": {
            "user_management": "用户认证和权限管理",
            "parts_management": "零件CRUD和搜索",
            "import_export": "批量数据导入导出",
            "image_management": "图片上传和下载",
            "crawler_plugins": "爬虫插件管理",
            "compatibility_check": "智能兼容性检查",  # 新增
            "compatibility_search": "兼容性搜索和建议",  # 新增
            "rule_management": "兼容性规则管理",  # 新增
            "security_audit": "操作审计和安全监控"  # 新增
        },
        "endpoints": {
            "authentication": "/api/auth",
            "admin_apis": "/api/admin",
            "public_apis": "/api/public",
            "documentation": "/docs",
            "openapi_schema": "/openapi.json"
        },
        "compatibility_system": {
            "version": "1.0.0",
            "engine": "Rule-based compatibility evaluation",
            "security": "Multi-layer expression validation",
            "caching": "Intelligent result caching",
            "audit": "Complete operation logging"
        }
    }

@api_router.get("/health", tags=["系统信息"])
async def health_check():
    """
    健康检查端点
    """
    return {
        "status": "healthy",
        "timestamp": "2025-05-30T12:00:00Z",
        "services": {
            "database": "connected",
            "compatibility_engine": "ready",
            "expression_parser": "ready",
            "cache": "active"
        }
    }

@api_router.get("/version", tags=["系统信息"])
async def get_version():
    """
    获取系统版本信息
    """
    return {
        "api_version": "1.0.0",
        "system_version": "1.0.0",
        "build_date": "2025-05-30",
        "components": {
            "fastapi": "0.104.1",
            "sqlalchemy": "2.0.23",
            "compatibility_engine": "1.0.0",
            "expression_parser": "1.0.0",
            "security_validator": "1.0.0"
        },
        "features": {
            "compatibility_check": True,
            "compatibility_search": True,
            "rule_management": True,
            "security_audit": True,
            "expression_validation": True,
            "caching": True,
            "external_feedback": True,
            "user_contributions": False  # 未来功能
        }
    }