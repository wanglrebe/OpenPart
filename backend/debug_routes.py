# backend/debug_routes.py
"""调试路由注册问题"""

def check_files():
    """检查必需的文件是否存在"""
    import os
    
    required_files = [
        "app/auth/__init__.py",
        "app/auth/models.py", 
        "app/auth/routes.py",
        "app/auth/schemas.py",
        "app/auth/security.py",
        "app/auth/middleware.py",
        "app/api/admin/__init__.py",
        "app/api/admin/parts.py",
        "app/api/public/__init__.py", 
        "app/api/public/parts.py",
        "app/api/routes.py"
    ]
    
    print("=== 检查文件是否存在 ===")
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - 缺失")
            missing_files.append(file_path)
    
    return missing_files

def test_imports():
    """测试模块导入"""
    print("\n=== 测试模块导入 ===")
    
    try:
        from app.auth.models import User, UserRole
        print("✅ app.auth.models - 导入成功")
    except Exception as e:
        print(f"❌ app.auth.models - 导入失败: {e}")
    
    try:
        from app.auth.routes import router
        print("✅ app.auth.routes - 导入成功")
    except Exception as e:
        print(f"❌ app.auth.routes - 导入失败: {e}")
    
    try:
        from app.api.admin.parts import router
        print("✅ app.api.admin.parts - 导入成功")
    except Exception as e:
        print(f"❌ app.api.admin.parts - 导入失败: {e}")
    
    try:
        from app.api.public.parts import router
        print("✅ app.api.public.parts - 导入成功")
    except Exception as e:
        print(f"❌ app.api.public.parts - 导入失败: {e}")
    
    try:
        from app.api.routes import api_router
        print("✅ app.api.routes - 导入成功")
    except Exception as e:
        print(f"❌ app.api.routes - 导入失败: {e}")

def check_routes():
    """检查路由注册"""
    print("\n=== 检查路由注册 ===")
    
    try:
        from app.main import app
        
        print("已注册的路由:")
        for route in app.routes:
            if hasattr(route, 'path'):
                print(f"  {route.methods} {route.path}")
            elif hasattr(route, 'prefix'):
                print(f"  Router: {route.prefix}")
                
    except Exception as e:
        print(f"❌ 检查路由失败: {e}")

if __name__ == "__main__":
    missing_files = check_files()
    
    if missing_files:
        print(f"\n⚠️  发现 {len(missing_files)} 个缺失文件，请先创建这些文件")
        for file in missing_files:
            print(f"   {file}")
    else:
        print("\n✅ 所有必需文件都存在")
        test_imports()
        check_routes()