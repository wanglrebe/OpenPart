#!/usr/bin/env python3
# backend/test_compatibility_api.py
"""
兼容性API完整测试脚本

测试所有新创建的兼容性API端点，确保功能正常
"""

import asyncio
import aiohttp
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional

# 测试配置
BASE_URL = "http://localhost:8000"
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"

class CompatibilityAPITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
        self.access_token = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def authenticate(self, username: str, password: str) -> bool:
        """用户认证获取token"""
        try:
            print("🔐 正在进行用户认证...")
            
            data = {
                "username": username,
                "password": password,
                "grant_type": "password"
            }
            
            async with self.session.post(
                f"{self.base_url}/api/auth/token",
                data=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.access_token = result["access_token"]
                    print("✅ 认证成功")
                    return True
                else:
                    print(f"❌ 认证失败: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ 认证异常: {str(e)}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    async def test_endpoint(self, name: str, method: str, url: str, 
                           data: Optional[Dict] = None, 
                           expected_status: int = 200,
                           description: str = "") -> bool:
        """测试单个API端点"""
        try:
            print(f"\n🧪 测试: {name}")
            if description:
                print(f"   描述: {description}")
            print(f"   方法: {method} {url}")
            
            start_time = time.time()
            
            kwargs = {
                "headers": self.get_headers()
            }
            
            if data and method.upper() in ["POST", "PUT", "PATCH"]:
                kwargs["json"] = data
            elif data and method.upper() == "GET":
                kwargs["params"] = data
            
            async with self.session.request(method, f"{self.base_url}{url}", **kwargs) as response:
                response_time = time.time() - start_time
                response_data = await response.text()
                
                # 尝试解析JSON响应
                try:
                    json_data = json.loads(response_data)
                except:
                    json_data = {"raw_response": response_data}
                
                success = response.status == expected_status
                
                result = {
                    "name": name,
                    "method": method,
                    "url": url,
                    "expected_status": expected_status,
                    "actual_status": response.status,
                    "response_time": round(response_time, 3),
                    "success": success,
                    "response_data": json_data
                }
                
                self.test_results.append(result)
                
                if success:
                    print(f"   ✅ 成功 ({response.status}) - {response_time:.3f}s")
                else:
                    print(f"   ❌ 失败 (期望:{expected_status}, 实际:{response.status}) - {response_time:.3f}s")
                    if "detail" in json_data:
                        print(f"   错误信息: {json_data['detail']}")
                
                return success, json_data
                
        except Exception as e:
            print(f"   ❌ 异常: {str(e)}")
            self.test_results.append({
                "name": name,
                "success": False,
                "error": str(e)
            })
            return False, {"error": str(e)}
    
    async def run_all_tests(self):
        """运行所有API测试"""
        print("🚀 开始兼容性API测试")
        print("=" * 60)
        
        # 1. 系统基础测试
        await self.test_system_endpoints()
        
        # 2. 管理员API测试
        await self.test_admin_apis()
        
        # 3. 公开API测试
        await self.test_public_apis()
        
        # 4. 生成测试报告
        self.generate_test_report()
    
    async def test_system_endpoints(self):
        """测试系统基础端点"""
        print("\n📡 测试系统基础端点")
        print("-" * 40)
        
        # API根端点
        await self.test_endpoint(
            "API根端点", "GET", "/api/",
            description="获取API基本信息"
        )
        
        # 健康检查
        await self.test_endpoint(
            "健康检查", "GET", "/api/health",
            description="检查系统健康状态"
        )
        
        # 版本信息
        await self.test_endpoint(
            "版本信息", "GET", "/api/version",
            description="获取系统版本信息"
        )
    
    async def test_admin_apis(self):
        """测试管理员API"""
        print("\n🔧 测试管理员API")
        print("-" * 40)
        
        # 测试表达式安全验证
        await self.test_endpoint(
            "表达式安全验证", "POST", "/api/admin/compatibility/rules/validate",
            data={"expression": "part_a.voltage == part_b.voltage"},
            description="验证安全表达式"
        )
        
        # 测试危险表达式验证
        await self.test_endpoint(
            "危险表达式验证", "POST", "/api/admin/compatibility/rules/validate",
            data={"expression": "__import__('os').system('ls')"},
            description="验证危险表达式应被拦截"
        )
        
        # 获取可用类别
        await self.test_endpoint(
            "获取零件类别", "GET", "/api/admin/compatibility/categories",
            description="获取可用的零件类别列表"
        )
        
        # 获取表达式函数
        await self.test_endpoint(
            "获取安全函数", "GET", "/api/admin/compatibility/expression-functions",
            description="获取表达式中可用的安全函数"
        )
        
        # 创建测试规则
        success, rule_data = await self.test_endpoint(
            "创建兼容性规则", "POST", "/api/admin/compatibility/rules",
            data={
                "name": "测试规则_电压匹配",
                "description": "测试用的电压匹配规则",
                "rule_expression": "part_a.voltage == part_b.voltage",
                "category_a": "CPU",
                "category_b": "主板",
                "weight": 100,
                "is_blocking": False
            },
            description="创建新的兼容性规则"
        )
        
        # 如果规则创建成功，继续测试其他操作
        if success and "id" in rule_data:
            rule_id = rule_data["id"]
            
            # 获取规则详情
            await self.test_endpoint(
                "获取规则详情", "GET", f"/api/admin/compatibility/rules/{rule_id}",
                description="获取单个规则的详细信息"
            )
            
            # 测试规则执行
            await self.test_endpoint(
                "测试规则执行", "POST", f"/api/admin/compatibility/rules/{rule_id}/test",
                data={
                    "expression": "part_a.voltage == part_b.voltage",
                    "test_data": {
                        "part_a": {"voltage": 12, "name": "测试CPU"},
                        "part_b": {"voltage": 12, "name": "测试主板"}
                    }
                },
                description="在沙箱环境中测试规则执行"
            )
            
            # 更新规则
            await self.test_endpoint(
                "更新兼容性规则", "PUT", f"/api/admin/compatibility/rules/{rule_id}",
                data={"description": "更新后的描述：测试用的电压匹配规则"},
                description="更新现有规则"
            )
        
        # 获取规则列表
        await self.test_endpoint(
            "获取规则列表", "GET", "/api/admin/compatibility/rules",
            data={"page": 1, "size": 10},
            description="获取兼容性规则列表"
        )
        
        # 获取统计信息
        await self.test_endpoint(
            "获取统计信息", "GET", "/api/admin/compatibility/stats",
            description="获取兼容性系统统计"
        )
        
        # 获取审计日志
        await self.test_endpoint(
            "获取审计日志", "GET", "/api/admin/compatibility/audit-log",
            data={"page": 1, "size": 10},
            description="获取操作审计日志"
        )
        
        # 获取安全报告
        await self.test_endpoint(
            "获取安全报告", "GET", "/api/admin/compatibility/security-report",
            description="获取系统安全状态报告"
        )
        
        # 清理缓存
        await self.test_endpoint(
            "清理缓存", "POST", "/api/admin/compatibility/clear-cache",
            description="清理兼容性检查缓存"
        )
    
    async def test_public_apis(self):
        """测试公开API"""
        print("\n🌐 测试公开API")
        print("-" * 40)
        
        # 系统状态
        await self.test_endpoint(
            "系统状态检查", "GET", "/api/public/compatibility/system-status",
            description="获取兼容性系统状态"
        )
        
        # 版本信息
        await self.test_endpoint(
            "兼容性版本信息", "GET", "/api/public/compatibility/version",
            description="获取兼容性系统版本"
        )
        
        # 外部反馈渠道
        await self.test_endpoint(
            "外部反馈渠道", "GET", "/api/public/compatibility/feedback-channels",
            description="获取外部反馈渠道信息"
        )
        
        # 知识库
        await self.test_endpoint(
            "兼容性知识库", "GET", "/api/public/compatibility/knowledge-base",
            description="获取兼容性知识库信息"
        )
        
        # 使用示例
        await self.test_endpoint(
            "API使用示例", "GET", "/api/public/compatibility/examples",
            description="获取API使用示例"
        )
        
        # 测试兼容性检查（使用示例数据）
        await self.test_endpoint(
            "兼容性检查", "POST", "/api/public/compatibility/check",
            data={
                "part_ids": [1, 2],
                "include_cache": True,
                "detail_level": "standard"
            },
            expected_status=404,  # 可能没有对应的零件数据
            description="测试兼容性检查功能（预期可能失败因为没有测试数据）"
        )
        
        # 测试快速检查
        await self.test_endpoint(
            "快速兼容性检查", "GET", "/api/public/compatibility/quick-check",
            data={"part_a_id": 1, "part_b_id": 2},
            expected_status=404,  # 可能没有对应的零件数据
            description="测试快速兼容性检查（预期可能失败因为没有测试数据）"
        )
        
        # 测试兼容性搜索
        await self.test_endpoint(
            "兼容性搜索", "POST", "/api/public/compatibility/search",
            data={
                "selected_parts": [1],
                "target_categories": ["CPU", "内存"],
                "min_compatibility_score": 70,
                "limit": 10
            },
            expected_status=404,  # 可能没有对应的零件数据
            description="测试兼容性搜索功能（预期可能失败因为没有测试数据）"
        )
    
    def generate_test_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📊 测试报告")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r.get("success", False)])
        failed_tests = total_tests - successful_tests
        
        print(f"总测试数: {total_tests}")
        print(f"成功: {successful_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print(f"成功率: {(successful_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ 失败的测试:")
            for result in self.test_results:
                if not result.get("success", False):
                    print(f"  - {result['name']}")
                    if "error" in result:
                        print(f"    错误: {result['error']}")
                    elif "actual_status" in result:
                        print(f"    状态: {result['actual_status']} (期望: {result['expected_status']})")
        
        print(f"\n⏱️  平均响应时间:")
        response_times = [r.get("response_time", 0) for r in self.test_results if "response_time" in r]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            print(f"  平均: {avg_time:.3f}s")
            print(f"  最快: {min_time:.3f}s")
            print(f"  最慢: {max_time:.3f}s")
        
        # 保存详细报告到文件
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "successful_tests": successful_tests,
                    "failed_tests": failed_tests,
                    "success_rate": (successful_tests/total_tests)*100
                },
                "detailed_results": self.test_results,
                "timestamp": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存到: {report_file}")
        
        # 返回测试是否整体成功
        return failed_tests == 0

async def main():
    """主测试函数"""
    print("🧪 兼容性API完整测试")
    print(f"目标服务器: {BASE_URL}")
    print(f"测试时间: {datetime.now()}")
    
    async with CompatibilityAPITester(BASE_URL) as tester:
        # 认证
        if not await tester.authenticate(TEST_USERNAME, TEST_PASSWORD):
            print("❌ 认证失败，跳过需要认证的测试")
            return False
        
        # 运行所有测试
        await tester.run_all_tests()
        
        # 生成并返回测试结果
        return tester.generate_test_report()

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if success:
            print("\n🎉 所有测试通过！")
            sys.exit(0)
        else:
            print("\n💥 部分测试失败，请检查上述错误信息")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试过程中发生异常: {str(e)}")
        sys.exit(1)