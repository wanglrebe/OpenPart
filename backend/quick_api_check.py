#!/usr/bin/env python3
# backend/quick_api_check.py
"""
快速API状态检查

在运行完整测试之前，快速检查服务器是否正常运行
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"

def check_server_status():
    """检查服务器状态"""
    print("🔍 检查服务器状态...")
    
    try:
        # 检查基础连接
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ 服务器正在运行")
            data = response.json()
            print(f"   状态: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
        print(f"   请确保后端服务正在运行在: {BASE_URL}")
        print("   启动命令: uvicorn app.main:app --reload")
        return False
    except requests.exceptions.Timeout:
        print("❌ 服务器响应超时")
        return False
    except Exception as e:
        print(f"❌ 检查服务器时出错: {str(e)}")
        return False

def check_compatibility_endpoints():
    """检查兼容性端点是否存在"""
    print("\n🔍 检查兼容性API端点...")
    
    endpoints_to_check = [
        ("/api/public/compatibility/version", "兼容性版本信息"),
        ("/api/public/compatibility/system-status", "系统状态"),
        ("/api/public/compatibility/feedback-channels", "反馈渠道"),
    ]
    
    available_endpoints = []
    
    for endpoint, description in endpoints_to_check:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if response.status_code < 500:  # 不是服务器错误
                print(f"✅ {description}: {response.status_code}")
                available_endpoints.append(endpoint)
            else:
                print(f"❌ {description}: {response.status_code}")
        except Exception as e:
            print(f"❌ {description}: 请求失败 - {str(e)}")
    
    return len(available_endpoints) > 0

def check_auth_endpoint():
    """检查认证端点"""
    print("\n🔍 检查认证端点...")
    
    try:
        # 尝试访问需要认证的端点（应该返回401）
        response = requests.get(f"{BASE_URL}/api/admin/compatibility/stats", timeout=5)
        
        if response.status_code == 401:
            print("✅ 认证端点正常工作（正确返回401）")
            return True
        elif response.status_code == 404:
            print("❌ 管理员兼容性端点不存在（404）")
            return False
        else:
            print(f"⚠️  认证端点响应异常: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 检查认证端点时出错: {str(e)}")
        return False

def check_documentation():
    """检查API文档"""
    print("\n🔍 检查API文档...")
    
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API文档可用")
            print(f"   访问地址: {BASE_URL}/docs")
            return True
        else:
            print(f"❌ API文档不可用: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 检查API文档时出错: {str(e)}")
        return False

def show_api_info():
    """显示API信息"""
    print("\n📊 API信息概览")
    print("-" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/api/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"API名称: {data.get('name', 'Unknown')}")
            print(f"版本: {data.get('version', 'Unknown')}")
            print(f"描述: {data.get('description', 'Unknown')}")
            
            features = data.get('features', {})
            print("\n支持的功能:")
            for feature, desc in features.items():
                print(f"  - {feature}: {desc}")
                
            endpoints = data.get('endpoints', {})
            print("\n主要端点:")
            for endpoint, path in endpoints.items():
                print(f"  - {endpoint}: {path}")
        else:
            print("无法获取API信息")
    except Exception as e:
        print(f"获取API信息时出错: {str(e)}")

def main():
    """主检查函数"""
    print("⚡ 快速API状态检查")
    print(f"目标服务器: {BASE_URL}")
    print(f"检查时间: {datetime.now()}")
    print("=" * 50)
    
    checks_passed = 0
    total_checks = 4
    
    # 1. 检查服务器基础状态
    if check_server_status():
        checks_passed += 1
    
    # 2. 检查兼容性端点
    if check_compatibility_endpoints():
        checks_passed += 1
    
    # 3. 检查认证端点
    if check_auth_endpoint():
        checks_passed += 1
    
    # 4. 检查API文档
    if check_documentation():
        checks_passed += 1
    
    # 显示API信息
    show_api_info()
    
    # 生成检查结果
    print("\n" + "=" * 50)
    print("📊 检查结果")
    print("=" * 50)
    print(f"通过检查: {checks_passed}/{total_checks}")
    
    if checks_passed == total_checks:
        print("🎉 所有检查通过！服务器运行正常")
        print("\n📋 下一步操作:")
        print("1. 运行简化测试: python3 simple_api_test.py")
        print("2. 运行完整测试: python3 test_compatibility_api.py")
        print("3. 查看API文档: http://localhost:8000/docs")
        return True
    elif checks_passed >= 2:
        print("⚠️  基础功能可用，但存在一些问题")
        print("建议检查服务器日志和配置")
        return True
    else:
        print("❌ 多项检查失败，服务器可能未正确启动")
        print("\n🔧 故障排除:")
        print("1. 确保后端服务正在运行: uvicorn app.main:app --reload")
        print("2. 检查端口8000是否被占用")
        print("3. 检查数据库连接是否正常")
        print("4. 查看服务器启动日志")
        return False

if __name__ == "__main__":
    try:
        success = main()
        
        if success:
            print(f"\n✨ 快速检查完成！准备进行详细测试")
            sys.exit(0)
        else:
            print(f"\n💥 快速检查发现问题，请先解决后再进行测试")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  检查被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 检查过程中发生异常: {str(e)}")
        sys.exit(1)