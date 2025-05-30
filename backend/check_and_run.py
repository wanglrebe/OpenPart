#!/usr/bin/env python3
# backend/check_and_run.py
"""
检查和运行脚本

1. 检查所有必要的文件是否存在
2. 验证导入是否正确
3. 运行基础测试
"""

import os
import sys
import importlib.util
from pathlib import Path

def check_file_exists(file_path: str, description: str) -> bool:
    """检查文件是否存在"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (文件不存在)")
        return False

def check_import(module_path: str, description: str) -> bool:
    """检查模块是否可以导入"""
    try:
        spec = importlib.util.spec_from_file_location("temp_module", module_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"✅ {description}: 导入成功")
            return True
    except Exception as e:
        print(f"❌ {description}: 导入失败 - {str(e)}")
        return False
    
    return False

def main():
    """主检查函数"""
    print("🔍 检查兼容性API文件和依赖")
    print("=" * 50)
    
    # 检查必要的文件
    files_to_check = [
        ("app/api/admin/compatibility.py", "管理员兼容性API"),
        ("app/api/public/compatibility.py", "公开兼容性API"), 
        ("app/services/rule_audit_service.py", "规则审计服务"),
        ("app/api/routes.py", "API路由配置"),
        ("app/models/compatibility.py", "兼容性数据模型"),
        ("app/schemas/compatibility.py", "兼容性Schema"),
        ("app/services/compatibility_engine.py", "兼容性引擎"),
        ("app/services/safe_expression_parser.py", "安全表达式解析器"),
    ]
    
    missing_files = []
    for file_path, description in files_to_check:
        if not check_file_exists(file_path, description):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ 发现 {len(missing_files)} 个缺失文件:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\n请确保所有必要文件都已创建")
        return False
    
    print(f"\n✅ 所有必要文件都存在!")
    
    # 检查关键模块的导入
    print("\n🔍 检查模块导入")
    print("-" * 30)
    
    import_checks = [
        ("app/services/compatibility_engine.py", "兼容性引擎"),
        ("app/services/safe_expression_parser.py", "安全表达式解析器"),
        ("app/services/rule_audit_service.py", "规则审计服务"),
    ]
    
    import_errors = []
    for file_path, description in import_checks:
        if not check_import(file_path, description):
            import_errors.append(file_path)
    
    if import_errors:
        print(f"\n❌ 发现 {len(import_errors)} 个导入错误:")
        for file_path in import_errors:
            print(f"   - {file_path}")
        print("\n请检查导入错误并修复")
        return False
    
    print(f"\n✅ 所有关键模块导入正常!")
    
    # 检查数据库模型
    print("\n🗄️ 检查数据库模型")
    print("-" * 30)
    
    try:
        sys.path.append(os.getcwd())
        from app.models.compatibility import (
            CompatibilityRule, CompatibilityExperience, RuleAuditLog,
            CompatibilityCache, CompatibilityTemplate, ExpressionSecurityCache
        )
        print("✅ 兼容性数据模型加载成功")
        
        from app.schemas.compatibility import (
            RuleCreate, RuleResponse, ExperienceCreate, ExperienceResponse,
            CompatibilityCheckRequest, CompatibilityCheckResponse
        )
        print("✅ 兼容性Schema加载成功")
        
    except Exception as e:
        print(f"❌ 数据库模型检查失败: {str(e)}")
        return False
    
    # 检查API路由
    print("\n🛣️ 检查API路由")
    print("-" * 30)
    
    try:
        from app.api.routes import api_router
        print("✅ API路由加载成功")
        
        # 检查路由数量
        route_count = len(api_router.routes)
        print(f"✅ 发现 {route_count} 个路由")
        
    except Exception as e:
        print(f"❌ API路由检查失败: {str(e)}")
        return False
    
    print("\n🎉 所有检查通过！系统准备就绪")
    return True

def run_basic_test():
    """运行基础测试"""
    print("\n🧪 运行基础功能测试")
    print("-" * 30)
    
    try:
        # 测试兼容性引擎初始化
        from app.services.compatibility_engine import compatibility_engine
        print("✅ 兼容性引擎初始化成功")
        
        # 测试安全表达式解析器
        from app.services.safe_expression_parser import SafeExpressionEngine
        engine = SafeExpressionEngine()
        print("✅ 安全表达式解析器初始化成功")
        
        # 测试函数列表获取
        functions = engine.get_allowed_functions()
        print(f"✅ 获取到 {len(functions)} 个安全函数")
        
        # 测试规则审计服务
        from app.services.rule_audit_service import rule_audit_service
        print("✅ 规则审计服务初始化成功")
        
        print("\n🎉 基础功能测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 基础功能测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def create_test_runner():
    """创建测试运行脚本"""
    test_script = '''#!/bin/bash
# run_tests.sh - 兼容性API测试运行脚本

echo "🚀 启动兼容性API测试"
echo "请确保后端服务器正在运行在 http://localhost:8000"
echo ""

# 检查Python环境
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python3 未安装或不在PATH中"
    exit 1
fi

# 检查必要的包
python3 -c "import requests, aiohttp" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 缺少必要的包，请安装: pip install requests aiohttp"
    exit 1
fi

echo "✅ Python环境检查通过"
echo ""

# 运行检查脚本
echo "🔍 运行系统检查..."
python3 check_and_run.py
if [ $? -ne 0 ]; then
    echo "❌ 系统检查失败"
    exit 1
fi

echo ""
echo "🧪 运行简化API测试..."
python3 simple_api_test.py

echo ""
echo "📝 如需运行完整测试，请执行:"
echo "python3 test_compatibility_api.py"
'''
    
    with open("run_tests.sh", "w") as f:
        f.write(test_script)
    
    # 设置执行权限
    os.chmod("run_tests.sh", 0o755)
    print("✅ 创建了测试运行脚本: run_tests.sh")

if __name__ == "__main__":
    print("🔍 兼容性API系统检查")
    print(f"当前目录: {os.getcwd()}")
    print("=" * 50)
    
    try:
        # 运行文件检查
        if not main():
            print("\n💥 系统检查失败")
            sys.exit(1)
        
        # 运行基础功能测试
        if not run_basic_test():
            print("\n💥 基础功能测试失败")
            sys.exit(1)
        
        # 创建测试运行脚本
        create_test_runner()
        
        print("\n" + "=" * 50)
        print("🎉 系统检查完成！")
        print("")
        print("📋 下一步操作:")
        print("1. 确保数据库服务正在运行")
        print("2. 启动后端服务器: uvicorn app.main:app --reload")
        print("3. 运行API测试: ./run_tests.sh 或 python3 simple_api_test.py")
        print("")
        print("📚 测试脚本说明:")
        print("- simple_api_test.py: 快速基础测试")
        print("- test_compatibility_api.py: 完整功能测试")
        print("- run_tests.sh: 一键测试脚本")
        
    except Exception as e:
        print(f"\n💥 系统检查异常: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)