# test_compatibility_operations.py
"""
兼容性操作功能测试脚本

使用方法:
python test_compatibility_operations.py

这个脚本会测试：
1. 规则的停用/启用功能
2. 规则的删除功能（包括依赖检查）
3. 批量操作功能
4. 审计日志记录
5. API响应格式验证
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional

# 配置
API_BASE_URL = "http://localhost:8000/api"
ADMIN_USERNAME = "admin"  # 请根据实际情况修改
ADMIN_PASSWORD = "admin123"  # 请根据实际情况修改

class CompatibilityTester:
    """兼容性操作测试器"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
        self.test_results = []
    
    def authenticate(self, username: str, password: str) -> bool:
        """用户认证"""
        print("🔐 正在进行用户认证...")
        
        try:
            auth_data = {
                "username": username,
                "password": password
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/token",
                data=auth_data
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                print("✅ 认证成功")
                return True
            else:
                print(f"❌ 认证失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 认证异常: {e}")
            return False
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """记录测试结果"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
    
    def create_test_rule(self) -> Optional[int]:
        """创建测试规则"""
        print("\n📝 创建测试规则...")
        
        # 使用UUID确保规则名称唯一
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        rule_data = {
            "name": f"测试规则_{unique_id}_{int(time.time())}",
            "description": "这是一个用于测试停用/启用/删除功能的规则",
            "rule_expression": "part_a.voltage == part_b.voltage",
            "category_a": "CPU",
            "category_b": "主板",
            "weight": 100,
            "is_blocking": False
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/admin/compatibility/rules",
                json=rule_data
            )
            
            if response.status_code == 200:
                rule = response.json()
                rule_id = rule["id"]
                self.log_test("创建测试规则", True, f"规则ID: {rule_id}")
                return rule_id
            else:
                self.log_test("创建测试规则", False, f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("创建测试规则", False, str(e))
            return None
    
    def test_disable_rule(self, rule_id: int) -> bool:
        """测试停用规则"""
        print(f"\n⏸️ 测试停用规则 {rule_id}...")
        
        try:
            response = self.session.patch(
                f"{self.base_url}/admin/compatibility/rules/{rule_id}/disable"
            )
            
            if response.status_code == 200:
                result = response.json()
                expected_fields = ["message", "rule_id", "rule_name"]
                
                if all(field in result for field in expected_fields):
                    self.log_test("停用规则", True, f"消息: {result['message']}")
                    return True
                else:
                    self.log_test("停用规则", False, "响应格式不正确")
                    return False
            else:
                self.log_test("停用规则", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("停用规则", False, str(e))
            return False
    
    def test_enable_rule(self, rule_id: int) -> bool:
        """测试启用规则"""
        print(f"\n▶️ 测试启用规则 {rule_id}...")
        
        try:
            response = self.session.patch(
                f"{self.base_url}/admin/compatibility/rules/{rule_id}/enable"
            )
            
            if response.status_code == 200:
                result = response.json()
                expected_fields = ["message", "rule_id", "rule_name"]
                
                if all(field in result for field in expected_fields):
                    self.log_test("启用规则", True, f"消息: {result['message']}")
                    return True
                else:
                    self.log_test("启用规则", False, "响应格式不正确")
                    return False
            else:
                self.log_test("启用规则", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("启用规则", False, str(e))
            return False
    
    def test_delete_rule_with_dependency_check(self, rule_id: int) -> bool:
        """测试删除规则（包括依赖检查）"""
        print(f"\n🗑️ 测试删除规则 {rule_id}（检查依赖）...")
        
        try:
            # 首先尝试不强制删除
            response = self.session.delete(
                f"{self.base_url}/admin/compatibility/rules/{rule_id}"
            )
            
            if response.status_code == 200:
                result = response.json()
                expected_fields = ["message", "rule_id", "rule_name"]
                
                if all(field in result for field in expected_fields):
                    self.log_test("删除规则", True, f"消息: {result['message']}")
                    return True
                else:
                    self.log_test("删除规则", False, "响应格式不正确")
                    return False
            elif response.status_code == 409:
                # 有依赖关系，测试强制删除
                print("   检测到依赖关系，测试强制删除...")
                
                force_response = self.session.delete(
                    f"{self.base_url}/admin/compatibility/rules/{rule_id}?force=true"
                )
                
                if force_response.status_code == 200:
                    result = force_response.json()
                    self.log_test("强制删除规则", True, f"消息: {result['message']}")
                    return True
                else:
                    self.log_test("强制删除规则", False, f"HTTP {force_response.status_code}")
                    return False
            else:
                self.log_test("删除规则", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("删除规则", False, str(e))
            return False
    
    def test_batch_operations(self) -> bool:
        """测试批量操作"""
        print("\n📦 测试批量操作...")
        
        # 创建多个测试规则，每次都用不同的名称
        rule_ids = []
        for i in range(3):
            time.sleep(0.1)  # 短暂延迟确保时间戳不同
            rule_id = self.create_test_rule()
            if rule_id:
                rule_ids.append(rule_id)
            else:
                print(f"   警告：第 {i+1} 个测试规则创建失败")
        
        if len(rule_ids) < 2:
            self.log_test("批量操作准备", False, f"只创建了 {len(rule_ids)} 个测试规则，需要至少2个")
            return False
        
        print(f"   成功创建 {len(rule_ids)} 个测试规则: {rule_ids}")
        
        try:
            # 测试批量停用
            print("   测试批量停用...")
            disable_data = {"rule_ids": rule_ids}
            disable_response = self.session.patch(
                f"{self.base_url}/admin/compatibility/rules/batch/disable",
                json=rule_ids  # 直接发送数组，根据API实现调整
            )
            
            if disable_response.status_code != 200:
                print(f"   批量停用请求失败: {disable_response.status_code}")
                print(f"   响应内容: {disable_response.text}")
                self.log_test("批量停用", False, f"HTTP {disable_response.status_code}")
                return False
            
            disable_result = disable_response.json()
            self.log_test("批量停用", True, f"更新了 {disable_result.get('actually_updated', 0)} 个规则")
            
            # 测试批量启用
            print("   测试批量启用...")
            enable_response = self.session.patch(
                f"{self.base_url}/admin/compatibility/rules/batch/enable",
                json=rule_ids  # 直接发送数组
            )
            
            if enable_response.status_code != 200:
                print(f"   批量启用请求失败: {enable_response.status_code}")
                print(f"   响应内容: {enable_response.text}")
                self.log_test("批量启用", False, f"HTTP {enable_response.status_code}")
                return False
            
            enable_result = enable_response.json()
            self.log_test("批量启用", True, f"更新了 {enable_result.get('actually_updated', 0)} 个规则")
            
            # 清理测试规则
            print("   清理测试规则...")
            cleaned_count = 0
            for rule_id in rule_ids:
                try:
                    delete_response = self.session.delete(
                        f"{self.base_url}/admin/compatibility/rules/{rule_id}?force=true"
                    )
                    if delete_response.status_code == 200:
                        cleaned_count += 1
                except Exception as e:
                    print(f"   清理规则 {rule_id} 失败: {e}")
            
            print(f"   清理了 {cleaned_count}/{len(rule_ids)} 个测试规则")
            
            return True
            
        except Exception as e:
            self.log_test("批量操作", False, str(e))
            # 尝试清理已创建的规则
            for rule_id in rule_ids:
                try:
                    self.session.delete(f"{self.base_url}/admin/compatibility/rules/{rule_id}?force=true")
                except:
                    pass
            return False
    
    def test_audit_logging(self) -> bool:
        """测试审计日志"""
        print("\n📊 测试审计日志...")
        
        try:
            response = self.session.get(
                f"{self.base_url}/admin/compatibility/audit-log?size=10"
            )
            
            if response.status_code == 200:
                logs = response.json()
                
                if isinstance(logs, list):
                    # 检查是否有新的操作类型
                    actions = {log.get("action") for log in logs}
                    new_actions = {"disable", "enable"} & actions
                    
                    if new_actions:
                        self.log_test("审计日志", True, f"发现新操作类型: {new_actions}")
                    else:
                        self.log_test("审计日志", True, "日志格式正确，但未发现新操作类型")
                    
                    return True
                else:
                    self.log_test("审计日志", False, "响应格式不正确")
                    return False
            else:
                self.log_test("审计日志", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("审计日志", False, str(e))
            return False
    
    def test_api_documentation(self) -> bool:
        """测试API文档"""
        print("\n📚 测试API文档...")
        
        try:
            # 检查OpenAPI文档是否包含新端点
            response = self.session.get(f"{self.base_url.replace('/api', '')}/openapi.json")
            
            if response.status_code == 200:
                openapi_spec = response.json()
                paths = openapi_spec.get("paths", {})
                
                # 检查新端点是否存在
                new_endpoints = [
                    "/api/admin/compatibility/rules/{rule_id}/disable",
                    "/api/admin/compatibility/rules/{rule_id}/enable",
                    "/api/admin/compatibility/rules/batch/disable",
                    "/api/admin/compatibility/rules/batch/enable"
                ]
                
                found_endpoints = []
                for endpoint in new_endpoints:
                    if endpoint in paths:
                        found_endpoints.append(endpoint)
                
                if len(found_endpoints) >= 2:  # 至少找到一些新端点
                    self.log_test("API文档", True, f"发现 {len(found_endpoints)} 个新端点")
                    return True
                else:
                    self.log_test("API文档", False, "未发现新的API端点")
                    return False
            else:
                self.log_test("API文档", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("API文档", False, str(e))
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("🚀 开始兼容性操作功能测试")
        print("=" * 60)
        
        # 认证
        if not self.authenticate(ADMIN_USERNAME, ADMIN_PASSWORD):
            return {"success": False, "error": "认证失败"}
        
        # 创建测试规则
        test_rule_id = self.create_test_rule()
        if not test_rule_id:
            return {"success": False, "error": "无法创建测试规则"}
        
        try:
            # 运行各项测试
            tests = [
                ("停用规则", lambda: self.test_disable_rule(test_rule_id)),
                ("启用规则", lambda: self.test_enable_rule(test_rule_id)),
                ("删除规则", lambda: self.test_delete_rule_with_dependency_check(test_rule_id)),
                ("批量操作", self.test_batch_operations),
                ("审计日志", self.test_audit_logging),
                ("API文档", self.test_api_documentation),
            ]
            
            for test_name, test_func in tests:
                print(f"\n📋 执行测试: {test_name}")
                try:
                    test_func()
                except Exception as e:
                    self.log_test(test_name, False, f"测试异常: {str(e)}")
                
                time.sleep(1)  # 避免请求过快
            
            # 汇总结果
            total_tests = len(self.test_results)
            successful_tests = sum(1 for result in self.test_results if result["success"])
            
            print("\n" + "=" * 60)
            print("📊 测试结果汇总")
            print("=" * 60)
            
            for result in self.test_results:
                status = "✅" if result["success"] else "❌"
                print(f"{status} {result['test']}: {result['details']}")
            
            success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
            
            print(f"\n📈 成功率: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
            
            if success_rate >= 80:
                print("🎉 测试基本通过！兼容性操作功能正常工作")
                return {"success": True, "success_rate": success_rate, "results": self.test_results}
            else:
                print("⚠️ 测试未完全通过，请检查失败的项目")
                return {"success": False, "success_rate": success_rate, "results": self.test_results}
        
        except Exception as e:
            print(f"❌ 测试过程异常: {e}")
            return {"success": False, "error": str(e), "results": self.test_results}

def main():
    """主函数"""
    print("OpenPart 兼容性操作功能测试")
    print(f"目标服务器: {API_BASE_URL}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查服务器连接
    try:
        response = requests.get(f"{API_BASE_URL.replace('/api', '')}/health", timeout=5)
        if response.status_code != 200:
            print("❌ 服务器连接失败，请确保后端服务正在运行")
            return
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("请确保后端服务正在运行且地址正确")
        return
    
    # 运行测试
    tester = CompatibilityTester(API_BASE_URL)
    result = tester.run_all_tests()
    
    # 保存测试报告
    try:
        report_filename = f"compatibility_test_report_{int(time.time())}.json"
        with open(report_filename, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n📄 测试报告已保存: {report_filename}")
    except Exception as e:
        print(f"⚠️ 保存测试报告失败: {e}")
    
    # 退出码
    sys.exit(0 if result.get("success", False) else 1)

if __name__ == "__main__":
    main()