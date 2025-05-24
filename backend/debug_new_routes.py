# backend/debug_new_routes.py (调试新路由)
"""调试新路由注册"""

def check_routes():
    """检查路由注册"""
    print("=== 检查新路由注册 ===")
    
    try:
        from app.main import app
        
        print("所有已注册的路由:")
        for route in app.routes:
            if hasattr(route, 'path'):
                methods = getattr(route, 'methods', [])
                print(f"  {methods} {route.path}")
            elif hasattr(route, 'routes'):  # 子路由
                print(f"  Router Group: {getattr(route, 'prefix', 'No prefix')}")
                for subroute in route.routes:
                    if hasattr(subroute, 'path'):
                        methods = getattr(subroute, 'methods', [])
                        full_path = getattr(route, 'prefix', '') + subroute.path
                        print(f"    {methods} {full_path}")
                        
    except Exception as e:
        print(f"❌ 检查路由失败: {e}")

def test_imports():
    """测试模块导入"""
    print("\n=== 测试新API导入 ===")
    
    try:
        from app.api.public.parts import search_parts_enhanced, get_search_suggestions
        print("✅ 新搜索函数导入成功")
    except Exception as e:
        print(f"❌ 新搜索函数导入失败: {e}")
    
    try:
        from app.api.public.parts import router
        print("✅ 公开API路由导入成功")
        print(f"路由中的端点数量: {len(router.routes)}")
        
        for route in router.routes:
            if hasattr(route, 'path'):
                print(f"  {route.methods} {route.path}")
    except Exception as e:
        print(f"❌ 公开API路由导入失败: {e}")

if __name__ == "__main__":
    test_imports()
    check_routes()