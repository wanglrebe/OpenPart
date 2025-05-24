# backend/test_direct_api.py (直接测试API)
"""直接测试API端点"""
import requests

def test_direct_endpoints():
    """直接测试各个端点"""
    base_url = "http://localhost:8000"
    
    endpoints_to_test = [
        "/api/public/parts/",                    # 原有端点
        "/api/public/parts/search",             # 新搜索端点
        "/api/public/parts/suggestions",        # 建议端点
        "/api/public/parts/categories/",        # 分类端点
    ]
    
    print("=== 直接测试API端点 ===")
    
    for endpoint in endpoints_to_test:
        print(f"\n🔍 测试: {endpoint}")
        
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功 - 返回数据类型: {type(data)}")
                if isinstance(data, list):
                    print(f"   数据数量: {len(data)}")
            elif response.status_code == 404:
                print(f"❌ 404 - 端点不存在")
            else:
                print(f"⚠️  状态码: {response.status_code}")
                print(f"   响应: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败 - 请确保后端服务正在运行")
        except Exception as e:
            print(f"❌ 错误: {e}")

if __name__ == "__main__":
    test_direct_endpoints()