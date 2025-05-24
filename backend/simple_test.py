# backend/simple_test.py
import requests

BASE_URL = "http://localhost:8000/api/public/parts"

def test_api():
    print("=== 简单API测试 ===")
    
    # 测试基本搜索
    print("\n🔍 测试基本搜索:")
    response = requests.get(f"{BASE_URL}/search?q=Arduino")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        results = response.json()
        print(f"找到 {len(results)} 个结果")
        for part in results:
            print(f"  - {part['name']}")
    
    # 测试分类
    print("\n📂 测试分类:")
    response = requests.get(f"{BASE_URL}/categories/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        categories = response.json()
        print(f"分类: {categories}")
    
    # 测试建议
    print("\n💡 测试建议:")
    response = requests.get(f"{BASE_URL}/suggestions?q=A")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        suggestions = response.json()
        print(f"建议: {suggestions}")

if __name__ == "__main__":
    test_api()