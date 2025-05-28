# backend/test_api.py
"""
测试插件管理API是否正常工作
"""

import requests
import json

def test_api_endpoints():
    """测试API端点"""
    base_url = "http://localhost:8000"
    
    print("🧪 测试插件管理API...")
    
    # 1. 测试健康检查
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器健康检查通过")
        else:
            print(f"❌ 服务器健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        return False
    
    # 2. 测试统计端点（无需认证的测试）
    try:
        response = requests.get(f"{base_url}/api/admin/crawler-plugins/stats", timeout=5)
        print(f"📊 统计端点响应: {response.status_code}")
        if response.status_code == 422:
            print("⚠️ 统计端点需要认证")
        elif response.status_code == 401:
            print("⚠️ 统计端点需要认证（401）")
        elif response.status_code == 200:
            print("✅ 统计端点响应正常")
            print(f"   响应内容: {response.json()}")
        else:
            print(f"❌ 统计端点异常: {response.text}")
    except Exception as e:
        print(f"❌ 统计端点测试失败: {e}")
    
    # 3. 测试插件列表端点
    try:
        response = requests.get(f"{base_url}/api/admin/crawler-plugins/", timeout=5)
        print(f"📋 插件列表端点响应: {response.status_code}")
        if response.status_code == 422:
            print("⚠️ 插件列表端点需要认证")
        elif response.status_code == 401:
            print("⚠️ 插件列表端点需要认证（401）")
        elif response.status_code == 200:
            print("✅ 插件列表端点响应正常")
            plugins = response.json()
            print(f"   插件数量: {len(plugins)}")
        else:
            print(f"❌ 插件列表端点异常: {response.text}")
    except Exception as e:
        print(f"❌ 插件列表端点测试失败: {e}")
    
    # 4. 检查API文档
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API文档可访问")
            print(f"   访问地址: {base_url}/docs")
        else:
            print(f"❌ API文档访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ API文档测试失败: {e}")
    
    print("\n💡 提示:")
    print("- 如果看到401/422错误，说明端点需要认证，这是正常的")
    print("- 可以访问 http://localhost:8000/docs 查看完整API文档")
    print("- 前端需要通过登录获取token才能访问管理API")
    
    return True

if __name__ == "__main__":
    test_api_endpoints()