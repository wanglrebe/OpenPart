# backend/simple_test.py
"""
简化版兼容性系统测试

先测试基本功能，确保系统可以正常启动
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试基本导入"""
    print("🔍 测试基本导入...")
    
    try:
        from app.core.database import SessionLocal, engine
        print("✅ 数据库连接模块导入成功")
        
        from app.models.compatibility import CompatibilityRule
        print("✅ 兼容性模型导入成功")
        
        from app.schemas.compatibility import CompatibilityCheckRequest
        print("✅ 兼容性Schema导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {str(e)}")
        return False

def test_database_connection():
    """测试数据库连接"""
    print("\n💾 测试数据库连接...")
    
    try:
        from app.core.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        # 尝试执行简单查询
        result = db.execute(text("SELECT 1")).fetchone()
        
        if result and result[0] == 1:
            print("✅ 数据库连接成功")
            db.close()
            return True
        else:
            print("❌ 数据库查询失败")
            db.close()
            return False
            
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False

def test_models():
    """测试数据模型"""
    print("\n📊 测试数据模型...")
    
    try:
        from app.models.compatibility import (
            CompatibilityRule, CompatibilityExperience, 
            CompatibilityCache, CompatibilityTemplate
        )
        
        print("✅ 兼容性模型加载成功")
        
        # 测试模型属性
        rule_attrs = ['id', 'name', 'rule_expression', 'category_a', 'category_b']
        for attr in rule_attrs:
            if hasattr(CompatibilityRule, attr):
                print(f"✅ CompatibilityRule.{attr} 存在")
            else:
                print(f"❌ CompatibilityRule.{attr} 不存在")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 模型测试失败: {str(e)}")
        return False

async def test_expression_engine():
    """测试表达式引擎"""
    print("\n⚡ 测试表达式引擎...")
    
    try:
        from app.services.safe_expression_parser import SafeExpressionEngine
        
        engine = SafeExpressionEngine()
        print("✅ 表达式引擎创建成功")
        
        # 测试简单表达式验证
        result = await engine.validate_expression_security("1 + 1")
        print(f"✅ 表达式验证成功: {result.is_safe}")
        
        # 测试表达式执行
        exec_result = await engine.execute_safe_expression("1 + 1", {})
        if exec_result == 2:
            print("✅ 表达式执行成功")
            return True
        else:
            print(f"❌ 表达式执行结果错误: {exec_result}")
            return False
            
    except Exception as e:
        print(f"❌ 表达式引擎测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_table_creation():
    """测试表是否正确创建"""
    print("\n🏗️ 测试数据表...")
    
    try:
        from app.core.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        # 检查兼容性相关表是否存在
        tables_to_check = [
            'compatibility_rules',
            'compatibility_experiences', 
            'compatibility_cache',
            'compatibility_templates',
            'rule_audit_log',
            'expression_security_cache'
        ]
        
        for table_name in tables_to_check:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}")).fetchone()
                print(f"✅ 表 {table_name} 存在，记录数: {result[0]}")
            except Exception as e:
                print(f"❌ 表 {table_name} 不存在或查询失败: {str(e)}")
                db.close()
                return False
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ 表检查失败: {str(e)}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始简化版兼容性系统测试...")
    print("="*50)
    
    tests = [
        ("基本导入", test_imports),
        ("数据库连接", test_database_connection),
        ("数据表检查", test_table_creation),
        ("数据模型", test_models),
        ("表达式引擎", test_expression_engine)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {str(e)}")
    
    print("\n" + "="*50)
    print(f"🎯 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有基础测试通过！系统基础架构正常。")
        print("\n下一步可以:")
        print("1. 运行完整测试 (python test_compatibility_system.py)")
        print("2. 开始实施API层")
        print("3. 创建管理界面")
    else:
        print(f"⚠️ 有 {total - passed} 个测试失败，请先解决这些问题。")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)