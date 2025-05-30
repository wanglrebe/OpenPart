#!/usr/bin/env python3
# backend/simple_api_test.py
"""
简化的API测试脚本

快速验证新创建的兼容性API是否能正常启动和响应
"""

import requests
import json
import sys
from datetime import datetime

# 测试配置
BASE_URL = "http://localhost:8000"
TIMEOUT = 10

def test_endpoint(name: str, method: str, url: str, data=None, auth_required=False, token=None):
    """测试单个端点"""
    try:
        print(f"🧪 测试: {name}")
        
        headers = {"Content-Type": "application/json"}
        if auth_required and token:
            headers["Authorization"] = f"Bearer {token}"
        
        if method.upper() == "GET":
            response = requests.get(f"{BASE_URL}{url}", headers=headers, timeout=TIMEOUT, params=data)
        elif method.upper() == "POST":
            response = requests.post(f"{BASE_URL}{url}", headers=headers, json=data, timeout=TIMEOUT)
        else:
            print(f"   ⚠️  不支持的方法: {method}")
            return False
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code < 400:
            print(f"   ✅ 成功")
            return True
        else:
            print(f"   ❌ 失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   错误信息: {error_data.get('detail', '未知错误')}")
            except:
                print(f"   响应内容: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ 连接失败: 无法连接到 {BASE_URL}")
        return False
    except requests.exceptions.Timeout:
        print(f"   ❌ 超时: 请求超过 {TIMEOUT} 秒")
        return False
    except Exception as e:
        print(f"   ❌ 异常: {str(e)}")
        return False

def get_auth_token(username: str, password: str):
    """获取认证token"""
    try:
        print("🔐 正在获取认证token...")
        
        data = {
            "username": username,
            "password": password,
            "grant_type": "password"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/token",
            data=data,  # 注意这里用data而不是json
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ 认证成功")
            return result["access_token"]
        else:
            print(f"   ❌ 认证失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ 认证异常: {str(e)}")
        return None

def main():
    """主测试函数"""
    print("🚀 兼容性API简化测试")
    print(f"目标服务器: {BASE_URL}")
    print("=" * 50)
    
    success_count = 0
    total_count = 0
    
    # 1. 测试基础端点（无需认证）
    print("\n📡 测试基础端点")
    print("-" * 30)
    
    tests = [
        ("API根端点", "GET", "/api/"),
        ("健康检查", "GET", "/api/health"), 
        ("版本信息", "GET", "/api/version"),
        ("兼容性系统状态", "GET", "/api/public/compatibility/system-status"),
        ("兼容性版本", "GET", "/api/public/compatibility/version"),
        ("外部反馈渠道", "GET", "/api/public/compatibility/feedback-channels"),
        ("兼容性知识库", "GET", "/api/public/compatibility/knowledge-base"),
        ("API使用示例", "GET", "/api/public/compatibility/examples"),
    ]
    
    for name, method, url in tests:
        total_count += 1
        if test_endpoint(name, method, url):
            success_count += 1
    
    # 2. 获取认证token
    print("\n🔐 获取认证token")
    print("-" * 30)
    
    token = get_auth_token("admin", "admin123")
    
    # 3. 测试需要认证的端点
    if token:
        print("\n🔧 测试管理员端点")
        print("-" * 30)
        
        admin_tests = [
            ("获取零件类别", "GET", "/api/admin/compatibility/categories"),
            ("获取安全函数", "GET", "/api/admin/compatibility/expression-functions"),
            ("获取规则列表", "GET", "/api/admin/compatibility/rules"),
            ("获取统计信息", "GET", "/api/admin/compatibility/stats"),
            ("获取审计日志", "GET", "/api/admin/compatibility/audit-log"),
            ("获取安全报告", "GET", "/api/admin/compatibility/security-report"),
        ]
        
        for name, method, url in admin_tests:
            total_count += 1
            if test_endpoint(name, method, url, auth_required=True, token=token):
                success_count += 1
        
        # 测试表达式验证
        print("\n🛡️ 测试安全验证")
        print("-" * 30)
        
        # 安全表达式
        total_count += 1
        if test_endpoint(
            "安全表达式验证", "POST", "/api/admin/compatibility/rules/validate",
            data={"expression": "part_a.voltage == part_b.voltage"},
            auth_required=True, token=token
        ):
            success_count += 1
        
        # 危险表达式
        total_count += 1
        if test_endpoint(
            "危险表达式验证", "POST", "/api/admin/compatibility/rules/validate", 
            data={"expression": "__import__('os').system('ls')"},
            auth_required=True, token=token
        ):
            success_count += 1
    else:
        print("⚠️  跳过需要认证的测试（认证失败）")
    
    # 4. 生成测试报告
    print("\n" + "=" * 50)
    print("📊 测试总结")
    print("=" * 50)
    
    print(f"总测试数: {total_count}")
    print(f"成功: {success_count} ✅")
    print(f"失败: {total_count - success_count} ❌")
    
    if total_count > 0:
        success_rate = (success_count / total_count) * 100
        print(f"成功率: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n🎉 测试结果良好！API基本功能正常")
            return True
        else:
            print("\n⚠️  部分测试失败，请检查服务器状态")
            return False
    else:
        print("\n❌ 没有执行任何测试")
        return False

if __name__ == "__main__":
    print(f"开始时间: {datetime.now()}")
    
    try:
        success = main()
        
        print(f"\n结束时间: {datetime.now()}")
        
        if success:
            print("\n✨ 所有核心功能测试通过！")
            sys.exit(0)
        else:
            print("\n💥 部分测试失败，请检查错误信息")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试异常: {str(e)}")
        sys.exit(1)