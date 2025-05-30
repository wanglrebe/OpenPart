#!/bin/bash
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
