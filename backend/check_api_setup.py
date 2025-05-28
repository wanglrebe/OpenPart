# backend/check_api_setup.py
"""
API设置检查器 - 用于调试和验证API配置
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_imports():
    """检查所有必要的导入"""
    print("🔍 检查API导入...")
    
    try:
        # 检查基础模块
        from app.core.database import get_db
        from app.auth.middleware import require_admin
        from app.auth.models import User
        print("✅ 基础模块导入成功")
        
        # 检查插件相关模块
        from app.models.crawler_plugin import CrawlerPlugin, CrawlerTask, PluginStatus, TaskStatus
        print("✅ 插件模型导入成功")
        
        # 检查schemas
        from app.schemas.crawler_plugin import (
            PluginResponse, PluginConfigRequest, PluginTestRequest,
            TaskResponse, TaskCreateRequest, TaskExecuteRequest
        )
        print("✅ Schema导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def check_database_tables():
    """检查数据库表是否存在"""
    print("🗄️ 检查数据库表...")
    
    try:
        from sqlalchemy import create_engine, inspect
        from app.core.config import settings
        
        engine = create_engine(settings.database_url)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        required_tables = ['crawler_plugins', 'crawler_tasks', 'schema_migrations']
        missing_tables = []
        
        for table in required_tables:
            if table in tables:
                print(f"✅ 表 {table} 存在")
            else:
                print(f"❌ 表 {table} 不存在")
                missing_tables.append(table)
        
        if missing_tables:
            print(f"\n⚠️ 缺少数据库表: {missing_tables}")
            print("请运行: ./migrate.sh migrate")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        return False

def check_api_routes():
    """检查API路由配置"""
    print("🛣️ 检查API路由...")
    
    try:
        from app.api.routes import api_router
        
        # 获取所有路由
        routes = []
        for route in api_router.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        required_routes = [
            '/admin/crawler-plugins',
            '/admin/crawler-plugins/stats'
        ]
        
        for route_pattern in required_routes:
            found = any(route_pattern in route for route in routes)
            if found:
                print(f"✅ 路由 {route_pattern} 已配置")
            else:
                print(f"❌ 路由 {route_pattern} 未找到")
        
        return True
        
    except Exception as e:
        print(f"❌ 路由检查失败: {e}")
        return False

def test_api_endpoints():
    """测试API端点"""
    print("🧪 测试API端点...")
    
    try:
        import requests
        import time
        
        # 等待服务器启动
        base_url = "http://localhost:8000"
        
        # 测试健康检查
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ 服务器运行正常")
            else:
                print(f"⚠️ 服务器响应异常: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ 无法连接到服务器，请确保服务器已启动")
            return False
        
        # 测试API文档
        try:
            response = requests.get(f"{base_url}/docs", timeout=5)
            if response.status_code == 200:
                print("✅ API文档可访问")
            else:
                print(f"⚠️ API文档访问异常: {response.status_code}")
        except:
            print("❌ API文档不可访问")
        
        return True
        
    except ImportError:
        print("⚠️ requests模块未安装，跳过端点测试")
        return True
    except Exception as e:
        print(f"❌ 端点测试失败: {e}")
        return False

def create_missing_files():
    """创建缺失的文件"""
    print("📝 检查必要文件...")
    
    # 检查__init__.py文件
    init_files = [
        "app/__init__.py",
        "app/api/__init__.py", 
        "app/api/admin/__init__.py",
        "app/models/__init__.py",
        "app/schemas/__init__.py",
        "app/plugins/__init__.py"
    ]
    
    for init_file in init_files:
        file_path = Path(init_file)
        if not file_path.exists():
            print(f"📄 创建 {init_file}")
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("# Auto-generated __init__.py\n")
        else:
            print(f"✅ {init_file} 存在")

def main():
    """主检查流程"""
    print("🔧 OpenPart API 设置检查器")
    print("=" * 50)
    
    all_checks_passed = True
    
    # 1. 创建必要文件
    create_missing_files()
    print()
    
    # 2. 检查导入
    if not check_imports():
        all_checks_passed = False
    print()
    
    # 3. 检查数据库
    if not check_database_tables():
        all_checks_passed = False
    print()
    
    # 4. 检查路由
    if not check_api_routes():
        all_checks_passed = False
    print()
    
    # 5. 测试端点
    if not test_api_endpoints():
        all_checks_passed = False
    print()
    
    # 总结
    print("=" * 50)
    if all_checks_passed:
        print("🎉 所有检查通过！API配置正确")
        print("\n建议:")
        print("1. 重启后端服务器")
        print("2. 刷新前端页面")
        print("3. 检查浏览器控制台是否还有错误")
    else:
        print("❌ 发现问题，请按照上述提示修复")
        print("\n常见解决方案:")
        print("1. 运行数据库迁移: ./migrate.sh migrate")
        print("2. 检查所有必要文件是否存在")
        print("3. 重启后端服务器")
    
    print("=" * 50)

if __name__ == "__main__":
    main()