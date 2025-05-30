# backend/test_compatibility_system.py
"""
兼容性系统集成测试脚本

测试数据库模型、安全表达式引擎、兼容性检查引擎的基本功能
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.compatibility import (
    CompatibilityRule, CompatibilityExperience, CompatibilityCache,
    get_compatibility_experience_by_parts, get_active_rules_for_categories
)
from app.models.part import Part
from app.auth.models import User, UserRole
from app.services.safe_expression_parser import SafeExpressionEngine
from app.services.compatibility_engine import compatibility_engine
from app.schemas.compatibility import (
    CompatibilityCheckRequest, CompatibilitySearchRequest,
    RuleCreate, ExperienceCreate, CompatibilityStatus
)

class CompatibilitySystemTester:
    def __init__(self):
        self.db = SessionLocal()
        self.expression_engine = SafeExpressionEngine()
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "name": test_name,
            "success": success,
            "message": message
        })
        print(f"{status} {test_name}" + (f" - {message}" if message else ""))
    
    def setup_test_data(self):
        """设置测试数据"""
        print("\n🔧 设置测试数据...")
        
        try:
            # 创建测试用户（如果不存在）
            test_admin = self.db.query(User).filter(User.username == "test_admin").first()
            if not test_admin:
                from app.auth.security import get_password_hash
                test_admin = User(
                    username="test_admin",
                    email="test@example.com",
                    hashed_password=get_password_hash("test123"),
                    role=UserRole.ADMIN
                )
                self.db.add(test_admin)
                self.db.commit()
                self.db.refresh(test_admin)
            
            # 创建测试零件
            test_parts = [
                Part(
                    name="测试CPU",
                    category="CPU",
                    description="测试用CPU",
                    properties={
                        "voltage": 12,
                        "power_consumption": 65,
                        "socket": "LGA1700",
                        "frequency": 3500,
                        "cores": 8
                    }
                ),
                Part(
                    name="测试主板",
                    category="主板",
                    description="测试用主板",
                    properties={
                        "voltage": 12,
                        "max_power": 200,
                        "socket": "LGA1700",
                        "min_freq": 2000,
                        "max_freq": 5000,
                        "form_factor": "ATX"
                    }
                ),
                Part(
                    name="测试电源",
                    category="电源",
                    description="测试用电源",
                    properties={
                        "voltage": 12,
                        "wattage": 650,
                        "efficiency": 80,
                        "form_factor": "ATX"
                    }
                ),
                Part(
                    name="不兼容CPU",
                    category="CPU", 
                    description="不兼容的CPU",
                    properties={
                        "voltage": 5,  # 不同电压
                        "power_consumption": 300,  # 功耗过高
                        "socket": "AM4",  # 不同接口
                        "frequency": 2000
                    }
                )
            ]
            
            # 检查是否已存在，避免重复创建
            for part in test_parts:
                existing = self.db.query(Part).filter(Part.name == part.name).first()
                if not existing:
                    self.db.add(part)
            
            self.db.commit()
            
            # 获取创建的零件
            self.test_cpu = self.db.query(Part).filter(Part.name == "测试CPU").first()
            self.test_motherboard = self.db.query(Part).filter(Part.name == "测试主板").first()
            self.test_power = self.db.query(Part).filter(Part.name == "测试电源").first()
            self.incompatible_cpu = self.db.query(Part).filter(Part.name == "不兼容CPU").first()
            self.test_admin = test_admin
            
            self.log_test("设置测试数据", True, "创建了测试零件和用户")
            
        except Exception as e:
            self.log_test("设置测试数据", False, str(e))
            raise
    
    async def test_expression_engine_security(self):
        """测试表达式引擎安全性"""
        print("\n🔒 测试表达式引擎安全性...")
        
        # 安全表达式测试
        safe_expressions = [
            "part_a.voltage == part_b.voltage",
            "part_a.power_consumption <= part_b.max_power", 
            "len(part_a.name) > 0",
            "part_a.socket == part_b.socket",
            "sum([part_a.power_consumption, 100]) <= part_b.wattage"
        ]
        
        # 危险表达式测试
        dangerous_expressions = [
            "__import__('os').system('ls')",
            "eval('print(\"hacked\")')",
            "open('/etc/passwd').read()",
            "part_a.__class__.__bases__",
            "exec('import subprocess')"
        ]
        
        try:
            # 测试安全表达式
            for expr in safe_expressions:
                validation = await self.expression_engine.validate_expression_security(expr)
                if validation.is_safe:
                    self.log_test(f"安全表达式验证: {expr[:30]}...", True)
                else:
                    self.log_test(f"安全表达式验证: {expr[:30]}...", False, "应该被识别为安全")
            
            # 测试危险表达式
            for expr in dangerous_expressions:
                validation = await self.expression_engine.validate_expression_security(expr)
                if not validation.is_safe:
                    self.log_test(f"危险表达式拦截: {expr[:30]}...", True)
                else:
                    self.log_test(f"危险表达式拦截: {expr[:30]}...", False, "应该被识别为危险")
            
        except Exception as e:
            self.log_test("表达式引擎安全测试", False, str(e))
    
    async def test_expression_execution(self):
        """测试表达式执行"""
        print("\n⚡ 测试表达式执行...")
        
        context = {
            'part_a': {
                'voltage': 12,
                'power_consumption': 65,
                'socket': 'LGA1700',
                'name': 'Test CPU'
            },
            'part_b': {
                'voltage': 12,
                'max_power': 200,
                'socket': 'LGA1700',
                'wattage': 650
            }
        }
        
        test_cases = [
            ("part_a.voltage == part_b.voltage", True),
            ("part_a.power_consumption <= part_b.max_power", True),
            ("part_a.socket == part_b.socket", True),
            ("part_a.voltage == 5", False),
            ("len(part_a.name) > 0", True),
            ("part_a.power_consumption + 100 <= part_b.wattage", True)
        ]
        
        try:
            for expr, expected in test_cases:
                result = await self.expression_engine.execute_safe_expression(expr, context)
                if result == expected:
                    self.log_test(f"表达式执行: {expr}", True, f"结果: {result}")
                else:
                    self.log_test(f"表达式执行: {expr}", False, f"期望: {expected}, 实际: {result}")
        
        except Exception as e:
            self.log_test("表达式执行测试", False, str(e))
    
    def test_database_models(self):
        """测试数据库模型"""
        print("\n💾 测试数据库模型...")
        
        try:
            # 测试创建兼容性规则
            test_rule = CompatibilityRule(
                name="电压匹配测试",
                description="测试CPU和主板电压匹配",
                rule_expression="part_a.voltage == part_b.voltage",
                category_a="CPU",
                category_b="主板",
                weight=100,
                is_blocking=True,
                created_by=self.test_admin.id
            )
            self.db.add(test_rule)
            self.db.commit()
            self.db.refresh(test_rule)
            
            self.log_test("创建兼容性规则", True, f"规则ID: {test_rule.id}")
            
            # 测试创建兼容性经验
            test_experience = CompatibilityExperience(
                part_a_id=self.test_cpu.id,
                part_b_id=self.test_motherboard.id,
                compatibility_status=CompatibilityStatus.COMPATIBLE,
                compatibility_score=95,
                notes="经过实际测试，完全兼容",
                source="admin",
                added_by=self.test_admin.id
            )
            self.db.add(test_experience)
            self.db.commit()
            self.db.refresh(test_experience)
            
            self.log_test("创建兼容性经验", True, f"经验ID: {test_experience.id}")
            
            # 测试查询功能
            found_experience = get_compatibility_experience_by_parts(
                self.db, self.test_cpu.id, self.test_motherboard.id
            )
            if found_experience and found_experience.id == test_experience.id:
                self.log_test("查询兼容性经验", True)
            else:
                self.log_test("查询兼容性经验", False, "未找到或ID不匹配")
            
            # 测试规则查询
            rules = get_active_rules_for_categories(self.db, "CPU", "主板")
            if any(rule.id == test_rule.id for rule in rules):
                self.log_test("查询分类规则", True, f"找到 {len(rules)} 个规则")
            else:
                self.log_test("查询分类规则", False, "未找到创建的规则")
            
        except Exception as e:
            self.log_test("数据库模型测试", False, str(e))
    
    async def test_compatibility_engine(self):
        """测试兼容性检查引擎"""
        print("\n🔧 测试兼容性检查引擎...")
        
        try:
            # 先创建一些测试规则
            rules = [
                CompatibilityRule(
                    name="接口匹配",
                    description="CPU和主板接口必须匹配",
                    rule_expression="safe_get(part_a, 'socket', '') == safe_get(part_b, 'socket', '')",
                    category_a="CPU",
                    category_b="主板",
                    weight=100,
                    is_blocking=True,
                    created_by=self.test_admin.id
                ),
                CompatibilityRule(
                    name="功率检查",
                    description="CPU功耗不能超过主板最大功率",
                    rule_expression="safe_get(part_a, 'power_consumption', 0) <= safe_get(part_b, 'max_power', 1000)",
                    category_a="CPU",
                    category_b="主板",
                    weight=80,
                    is_blocking=False,
                    created_by=self.test_admin.id
                ),
                CompatibilityRule(
                    name="电源功率检查",
                    description="电源功率必须足够",
                    rule_expression="safe_get(part_a, 'power_consumption', 0) + safe_get(part_b, 'power_consumption', 0) <= safe_get(part_c, 'wattage', 500)",
                    category_a="CPU",
                    category_b="主板",
                    weight=90,
                    is_blocking=True,
                    created_by=self.test_admin.id
                )
            ]
            
            for rule in rules:
                existing = self.db.query(CompatibilityRule).filter(
                    CompatibilityRule.name == rule.name
                ).first()
                if not existing:
                    self.db.add(rule)
            
            self.db.commit()
            
            # 测试兼容性检查
            request = CompatibilityCheckRequest(
                part_ids=[self.test_cpu.id, self.test_motherboard.id],
                include_cache=False,
                detail_level="detailed"
            )
            
            result = await compatibility_engine.check_compatibility(request, self.db)
            
            if result.success:
                self.log_test("兼容性检查", True, f"整体评分: {result.overall_score}")
                
                # 检查结果详情
                if result.part_combinations:
                    combo = result.part_combinations[0]
                    self.log_test("零件组合分析", True, 
                                f"CPU+主板兼容性: {combo.compatibility_grade.value}")
                else:
                    self.log_test("零件组合分析", False, "没有返回组合结果")
            else:
                self.log_test("兼容性检查", False, "检查失败")
            
            # 测试不兼容情况
            incompatible_request = CompatibilityCheckRequest(
                part_ids=[self.incompatible_cpu.id, self.test_motherboard.id],
                include_cache=False
            )
            
            incompatible_result = await compatibility_engine.check_compatibility(
                incompatible_request, self.db
            )
            
            if incompatible_result.success and not incompatible_result.is_overall_compatible:
                self.log_test("不兼容检测", True, "正确识别不兼容组合")
            else:
                self.log_test("不兼容检测", False, "未能正确识别不兼容")
            
        except Exception as e:
            self.log_test("兼容性引擎测试", False, str(e))
    
    async def test_compatibility_search(self):
        """测试兼容性搜索"""
        print("\n🔍 测试兼容性搜索...")
        
        try:
            # 搜索与测试CPU兼容的零件
            search_request = CompatibilitySearchRequest(
                selected_parts=[self.test_cpu.id],
                target_categories=["主板", "电源"],
                min_compatibility_score=50,
                limit=10
            )
            
            search_result = await compatibility_engine.search_compatible_parts(
                search_request, self.db
            )
            
            if search_result.success:
                compatible_count = len(search_result.matches)
                self.log_test("兼容性搜索", True, f"找到 {compatible_count} 个兼容零件")
                
                # 检查是否包含我们的测试主板
                motherboard_found = any(
                    match.part_id == self.test_motherboard.id 
                    for match in search_result.matches
                )
                
                if motherboard_found:
                    self.log_test("搜索结果验证", True, "找到兼容的测试主板")
                else:
                    self.log_test("搜索结果验证", False, "未找到应该兼容的主板")
            else:
                self.log_test("兼容性搜索", False, "搜索失败")
        
        except Exception as e:
            self.log_test("兼容性搜索测试", False, str(e))
    
    def test_data_cleanup(self):
        """清理测试数据"""
        print("\n🧹 清理测试数据...")
        
        try:
            # 删除测试规则
            self.db.query(CompatibilityRule).filter(
                CompatibilityRule.created_by == self.test_admin.id
            ).delete()
            
            # 删除测试经验
            self.db.query(CompatibilityExperience).filter(
                CompatibilityExperience.added_by == self.test_admin.id
            ).delete()
            
            # 删除测试零件
            test_part_names = ["测试CPU", "测试主板", "测试电源", "不兼容CPU"]
            for name in test_part_names:
                self.db.query(Part).filter(Part.name == name).delete()
            
            # 删除测试用户
            self.db.query(User).filter(User.username == "test_admin").delete()
            
            self.db.commit()
            self.log_test("清理测试数据", True)
            
        except Exception as e:
            self.log_test("清理测试数据", False, str(e))
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "="*50)
        print("🎯 测试总结")
        print("="*50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['name']}: {result['message']}")
        
        print("\n" + "="*50)
        
        if failed_tests == 0:
            print("🎉 所有测试通过！兼容性系统基础架构运行正常。")
        else:
            print(f"⚠️  有 {failed_tests} 个测试失败，请检查相关功能。")
    
    def cleanup(self):
        """清理资源"""
        if self.db:
            self.db.close()

async def main():
    """主测试函数"""
    print("🚀 开始测试兼容性系统...")
    print("="*50)
    
    tester = CompatibilitySystemTester()
    
    try:
        # 设置测试数据
        tester.setup_test_data()
        
        # 执行各项测试
        await tester.test_expression_engine_security()
        await tester.test_expression_execution()
        tester.test_database_models()
        await tester.test_compatibility_engine()
        await tester.test_compatibility_search()
        
        # 打印测试总结
        tester.print_summary()
        
    except Exception as e:
        print(f"\n💥 测试过程中出现严重错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理测试数据和资源
        tester.test_data_cleanup()
        tester.cleanup()

if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())