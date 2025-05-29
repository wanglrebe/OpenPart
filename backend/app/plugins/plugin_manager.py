# backend/app/plugins/plugin_manager.py
"""
插件管理器核心类

负责插件的加载、卸载、执行和安全管理
"""

import os
import sys
import importlib.util
import hashlib
import logging
from typing import Dict, Optional, List, Any
from pathlib import Path
import ast
import re
from app.plugins.crawler_base import BaseCrawlerPlugin, SecurityError
from app.models.crawler_plugin import PluginStatus

logger = logging.getLogger(__name__)

class PluginSecurityValidator:
    """插件安全验证器 - 渐进式安全策略"""
    
    # 完全禁用的核心危险模块
    FORBIDDEN_CORE_MODULES = {
        'subprocess', 'multiprocessing', 'threading',
        'socket', 'socketserver', 'ssl', 'ftplib', 'telnetlib',
        'eval', 'exec', 'compile', '__import__'
    }
    
    # 允许的数据处理库（白名单）
    ALLOWED_DATA_LIBRARIES = {
        # PDF处理
        'pdfplumber', 'PyPDF2', 'pdfminer', 'pymupdf', 'fitz',
        # Excel/CSV处理
        'pandas', 'openpyxl', 'xlrd', 'xlwt', 'csv',
        # Word文档处理
        'python-docx', 'docx', 'mammoth',
        # 文本处理
        'markdown', 'beautifulsoup4', 'bs4', 'lxml',
        # 图像处理
        'pillow', 'PIL', 'opencv-python', 'cv2',
        # 数据格式
        'json', 'yaml', 'pyyaml', 'xml', 'jsonschema',
        # 科学计算
        'numpy', 'scipy',
        # 时间和正则
        'datetime', 're', 'time', 'calendar',
        # 数学和统计
        'math', 'statistics', 'random',
        # 网络请求（已有控制）
        'requests', 'urllib', 'http',
        # 其他工具
        'uuid', 'hashlib', 'base64', 'collections',
        'itertools', 'functools', 'operator'
    }
    
    # 受限但允许的系统模块（需要检查具体用法）
    RESTRICTED_SYSTEM_MODULES = {
        'os': ['path'],  # 只允许 os.path
        'sys': ['version', 'platform'],  # 只允许读取系统信息
        'tempfile': ['NamedTemporaryFile', 'mktemp', 'gettempdir'],  # 临时文件操作
        'shutil': ['copy', 'move'],  # 有限的文件操作
    }
    
    # 禁用的函数调用
    FORBIDDEN_FUNCTIONS = {
        'eval', 'exec', 'compile', '__import__', 'reload',
        'input', 'raw_input', 'open'  # 直接文件操作被禁止，使用安全包装器
    }
    
    # 危险的属性访问
    DANGEROUS_ATTRIBUTES = {
        '__class__', '__bases__', '__subclasses__', '__mro__',
        '__globals__', '__code__', '__func__', '__self__',
        '__builtins__', '__import__'
    }
    
    def validate_plugin_code(self, file_path: str) -> bool:
        """验证插件代码安全性 - 更新版本"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # 解析AST
            tree = ast.parse(code)
            
            # 检查导入语句 - 使用新的策略
            self._check_imports_with_whitelist(tree)
            
            # 检查函数调用
            self._check_function_calls(tree)
            
            # 检查属性访问
            self._check_attribute_access(tree)
            
            # 检查字符串内容中的危险模式
            self._check_string_literals(tree)
            
            print(f"✓ 插件安全验证通过: {file_path}")
            return True
            
        except Exception as e:
            print(f"✗ 插件安全验证失败: {e}")
            raise SecurityError(f"插件代码存在安全风险: {e}")
    
    def _check_imports_with_whitelist(self, tree: ast.AST):
        """检查导入语句 - 白名单策略"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]  # 获取顶级模块名
                    
                    # 检查是否为核心禁用模块
                    if module_name in self.FORBIDDEN_CORE_MODULES:
                        raise SecurityError(f"禁止导入核心危险模块: {module_name}")
                    
                    # 检查是否在白名单中
                    if module_name not in self.ALLOWED_DATA_LIBRARIES and module_name not in self.RESTRICTED_SYSTEM_MODULES:
                        # 给出警告但不阻止（可以根据需要调整）
                        print(f"⚠️ 警告：使用了未在白名单中的模块: {module_name}")
                        # 暂时允许，但记录
                        pass
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module.split('.')[0]
                    
                    # 检查核心禁用模块
                    if module_name in self.FORBIDDEN_CORE_MODULES:
                        raise SecurityError(f"禁止从危险模块导入: {module_name}")
                    
                    # 检查受限模块的特定导入
                    if module_name in self.RESTRICTED_SYSTEM_MODULES:
                        allowed_items = self.RESTRICTED_SYSTEM_MODULES[module_name]
                        for alias in node.names:
                            if alias.name not in allowed_items and alias.name != '*':
                                raise SecurityError(f"禁止从 {module_name} 导入: {alias.name}")
                    
                    # 检查是否导入禁用函数
                    for alias in node.names:
                        if alias.name in self.FORBIDDEN_FUNCTIONS:
                            raise SecurityError(f"禁止导入函数: {alias.name}")
    
    def _check_function_calls(self, tree: ast.AST):
        """检查函数调用"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # 检查直接函数调用
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.FORBIDDEN_FUNCTIONS:
                        raise SecurityError(f"禁止调用函数: {node.func.id}")
                
                # 检查属性方法调用
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in self.FORBIDDEN_FUNCTIONS:
                        raise SecurityError(f"禁止调用方法: {node.func.attr}")
                    
                    # 检查特定的危险调用模式
                    if isinstance(node.func.value, ast.Name):
                        if (node.func.value.id == 'os' and 
                            node.func.attr not in ['path']):
                            raise SecurityError(f"禁止调用 os.{node.func.attr}")
    
    def _check_attribute_access(self, tree: ast.AST):
        """检查属性访问"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                if node.attr in self.DANGEROUS_ATTRIBUTES:
                    raise SecurityError(f"禁止访问危险属性: {node.attr}")
    
    def _check_string_literals(self, tree: ast.AST):
        """检查字符串字面量中的危险模式"""
        dangerous_patterns = [
            r'__.*__',  # 双下划线属性
            r'eval\s*\(',  # eval调用
            r'exec\s*\(',  # exec调用
            r'subprocess\.',  # subprocess模块
            r'os\.system',  # os.system调用
        ]
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Str, ast.Constant)) and isinstance(getattr(node, 's', getattr(node, 'value', None)), str):
                content = getattr(node, 's', getattr(node, 'value', ''))
                for pattern in dangerous_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        raise SecurityError(f"字符串包含潜在危险内容: {pattern}")


class PluginManager:
    """插件管理器"""
    
    def __init__(self):
        self.plugins: Dict[str, BaseCrawlerPlugin] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
        self.security_validator = PluginSecurityValidator()
        self.plugin_directory = "app/plugins/crawlers"
        
        # 确保插件目录存在
        os.makedirs(self.plugin_directory, exist_ok=True)
    
    def validate_plugin_file(self, file_path: str) -> Dict[str, Any]:
        """验证插件文件并返回插件信息 - 调试版本"""
        
        try:
            print(f"开始验证插件文件: {file_path}")
            
            # 安全验证
            print("1. 执行安全验证...")
            self.security_validator.validate_plugin_code(file_path)
            print("   ✓ 安全验证通过")
            
            # 加载模块获取信息
            print("2. 加载插件模块...")
            spec = importlib.util.spec_from_file_location("temp_plugin", file_path)
            if not spec or not spec.loader:
                raise ValueError("无法加载插件文件")
            
            print("   ✓ 模块规范创建成功")
            
            module = importlib.util.module_from_spec(spec)
            print("   ✓ 模块对象创建成功")
            
            spec.loader.exec_module(module)
            print("   ✓ 模块执行成功")
            
            # 查找插件类
            print("3. 查找插件实例...")
            plugin_instance = None
            
            if hasattr(module, 'plugin'):
                print("   → 找到 'plugin' 属性")
                plugin_instance = module.plugin
                print(f"   → plugin 类型: {type(plugin_instance)}")
            else:
                print("   → 未找到 'plugin' 属性，搜索插件类...")
                # 查找继承自BaseCrawlerPlugin的类
                for item_name in dir(module):
                    item = getattr(module, item_name)
                    print(f"   → 检查项目: {item_name} = {type(item)}")
                    
                    if isinstance(item, type):
                        print(f"     → {item_name} 是类型")
                        try:
                            # 检查是否继承自BaseCrawlerPlugin
                            if hasattr(item, '__bases__'):
                                print(f"     → {item_name} 的基类: {item.__bases__}")
                                for base in item.__bases__:
                                    print(f"       → 基类名称: {base.__name__}")
                                    if base.__name__ == 'BaseCrawlerPlugin':
                                        print(f"     → ✓ 找到插件类: {item_name}")
                                        plugin_instance = item()
                                        break
                        except Exception as e:
                            print(f"     → 检查类 {item_name} 时出错: {e}")
                            continue
                    
                    if plugin_instance:
                        break
            
            if not plugin_instance:
                available_items = [name for name in dir(module) if not name.startswith('_')]
                raise ValueError(f"未找到有效的插件类。模块中可用的项目: {available_items}")
            
            print(f"   ✓ 插件实例创建成功: {type(plugin_instance)}")
            
            # 获取插件信息
            print("4. 获取插件信息...")
            try:
                plugin_info = plugin_instance.plugin_info
                print(f"   ✓ 插件信息获取成功: {type(plugin_info)}")
                print(f"   → 插件信息内容: {plugin_info}")
            except Exception as e:
                print(f"   ✗ 获取插件信息失败: {e}")
                import traceback
                traceback.print_exc()
                raise ValueError(f"获取插件信息失败: {str(e)}")
            
            # 获取配置schema
            print("5. 获取配置schema...")
            try:
                config_schema = plugin_instance.config_schema
                print(f"   ✓ 配置schema获取成功，字段数量: {len(config_schema)}")
            except Exception as e:
                print(f"   ✗ 获取配置schema失败: {e}")
                import traceback
                traceback.print_exc()
                raise ValueError(f"获取配置schema失败: {str(e)}")
            
            # 验证必要字段
            print("6. 验证插件信息字段...")
            required_fields = ['name', 'version', 'description', 'author', 'data_source']
            for field in required_fields:
                if not hasattr(plugin_info, field):
                    raise ValueError(f"插件信息缺少必要字段: {field}")
                value = getattr(plugin_info, field)
                print(f"   → {field}: {value}")
                if not value:
                    raise ValueError(f"插件信息字段 {field} 不能为空")
            
            # 构建返回结果
            print("7. 构建返回结果...")
            result = {
                "name": plugin_info.name.replace(" ", "_").lower(),  # 标准化名称
                "display_name": plugin_info.name,
                "version": plugin_info.version,
                "description": plugin_info.description,
                "author": plugin_info.author,
                "data_source": plugin_info.data_source,
                "data_source_type": plugin_info.data_source_type.value if hasattr(plugin_info, 'data_source_type') else "other",
                "homepage": getattr(plugin_info, 'homepage', None),
                "terms_url": getattr(plugin_info, 'terms_url', None),
                "rate_limit": getattr(plugin_info, 'rate_limit', None),
                "batch_size": getattr(plugin_info, 'batch_size', 50),
                "config_schema": [field.dict() for field in config_schema],
                "allowed_domains": plugin_instance.get_allowed_domains(),
                "required_permissions": plugin_instance.get_required_permissions()
            }
            
            print(f"   ✓ 验证完成，返回结果: {result}")
            return result
            
        except Exception as e:
            print(f"✗ 插件验证失败: {str(e)}")
            import traceback
            traceback.print_exc()
            logger.error(f"插件验证失败: {e}")
            raise ValueError(f"插件验证失败: {str(e)}")
    
    def load_plugin(self, plugin_name: str, file_path: str) -> BaseCrawlerPlugin:
        """加载插件"""
        
        try:
            # 先验证插件
            plugin_info = self.validate_plugin_file(file_path)
            
            # 计算文件哈希
            file_hash = self._calculate_file_hash(file_path)
            
            # 动态导入插件模块
            spec = importlib.util.spec_from_file_location(plugin_name, file_path)
            if not spec or not spec.loader:
                raise ValueError("无法创建模块规范")
            
            module = importlib.util.module_from_spec(spec)
            
            # 添加到sys.modules以便插件内部导入
            sys.modules[plugin_name] = module
            
            # 执行模块
            spec.loader.exec_module(module)
            
            # 获取插件实例
            plugin_instance = None
            if hasattr(module, 'plugin'):
                plugin_instance = module.plugin
            else:
                # 查找插件类并实例化
                for item_name in dir(module):
                    item = getattr(module, item_name)
                    if (isinstance(item, type) and 
                        issubclass(item, BaseCrawlerPlugin) and 
                        item != BaseCrawlerPlugin):
                        plugin_instance = item()
                        break
            
            if not plugin_instance:
                raise ValueError("未找到有效的插件实例")
            
            # 存储插件
            self.plugins[plugin_name] = plugin_instance
            
            logger.info(f"插件加载成功: {plugin_name}")
            return plugin_instance
            
        except Exception as e:
            logger.error(f"加载插件失败: {plugin_name}, 错误: {e}")
            # 清理可能的模块引用
            if plugin_name in sys.modules:
                del sys.modules[plugin_name]
            raise ValueError(f"加载插件失败: {str(e)}")
    
    def unload_plugin(self, plugin_name: str):
        """卸载插件"""
        
        try:
            if plugin_name in self.plugins:
                # 调用插件清理方法
                plugin = self.plugins[plugin_name]
                if hasattr(plugin, 'cleanup'):
                    plugin.cleanup()
                
                # 移除插件引用
                del self.plugins[plugin_name]
                
                # 清理配置
                if plugin_name in self.plugin_configs:
                    del self.plugin_configs[plugin_name]
                
                # 清理模块引用
                if plugin_name in sys.modules:
                    del sys.modules[plugin_name]
                
                logger.info(f"插件卸载成功: {plugin_name}")
            
        except Exception as e:
            logger.error(f"卸载插件失败: {plugin_name}, 错误: {e}")
            raise ValueError(f"卸载插件失败: {str(e)}")
    
    def get_plugin(self, plugin_name: str) -> Optional[BaseCrawlerPlugin]:
        """获取插件实例"""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[str]:
        """列出所有已加载的插件"""
        return list(self.plugins.keys())
    
    def reload_plugin(self, plugin_name: str, file_path: str) -> BaseCrawlerPlugin:
        """重新加载插件"""
        
        try:
            # 先卸载现有插件
            if plugin_name in self.plugins:
                self.unload_plugin(plugin_name)
            
            # 重新加载
            return self.load_plugin(plugin_name, file_path)
            
        except Exception as e:
            logger.error(f"重新加载插件失败: {plugin_name}, 错误: {e}")
            raise ValueError(f"重新加载插件失败: {str(e)}")
    
    def set_plugin_config(self, plugin_name: str, config: Dict[str, Any]):
        """设置插件配置"""
        
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            raise ValueError(f"插件未找到: {plugin_name}")
        
        # 验证配置
        try:
            plugin.validate_config(config)
            self.plugin_configs[plugin_name] = config
            logger.info(f"插件配置更新成功: {plugin_name}")
        except Exception as e:
            raise ValueError(f"配置验证失败: {str(e)}")
    
    def get_plugin_config(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """获取插件配置"""
        return self.plugin_configs.get(plugin_name)
    
    def test_plugin_connection(self, plugin_name: str, config: Optional[Dict[str, Any]] = None):
        """测试插件连接"""
        
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            raise ValueError(f"插件未找到: {plugin_name}")
        
        test_config = config or self.plugin_configs.get(plugin_name, {})
        if not test_config:
            raise ValueError("未提供测试配置")
        
        return plugin.test_connection(test_config)
    
    def execute_plugin(self, plugin_name: str, config: Optional[Dict[str, Any]] = None, **kwargs):
        """执行插件爬取"""
        
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            raise ValueError(f"插件未找到: {plugin_name}")
        
        exec_config = config or self.plugin_configs.get(plugin_name, {})
        if not exec_config:
            raise ValueError("未提供执行配置")
        
        return plugin.crawl(exec_config, **kwargs)
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件哈希值"""
        
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def scan_plugin_directory(self) -> List[str]:
        """扫描插件目录"""
        
        plugin_files = []
        plugin_dir = Path(self.plugin_directory)
        
        if plugin_dir.exists():
            for file_path in plugin_dir.glob("*.py"):
                if file_path.name != "__init__.py":
                    plugin_files.append(str(file_path))
        
        return plugin_files
    
    def auto_load_plugins(self):
        """自动加载插件目录中的所有插件"""
        
        plugin_files = self.scan_plugin_directory()
        loaded_count = 0
        failed_count = 0
        
        for file_path in plugin_files:
            try:
                plugin_info = self.validate_plugin_file(file_path)
                plugin_name = plugin_info["name"]
                
                if plugin_name not in self.plugins:
                    self.load_plugin(plugin_name, file_path)
                    loaded_count += 1
                    logger.info(f"自动加载插件: {plugin_name}")
                
            except Exception as e:
                failed_count += 1
                logger.error(f"自动加载插件失败: {file_path}, 错误: {e}")
        
        logger.info(f"自动加载完成，成功: {loaded_count}, 失败: {failed_count}")
        return {"loaded": loaded_count, "failed": failed_count}
    
    def get_plugin_status(self, plugin_name: str) -> Dict[str, Any]:
        """获取插件状态"""
        
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            return {"status": "not_loaded", "error": "插件未加载"}
        
        try:
            plugin_info = plugin.plugin_info
            return {
                "status": "loaded",
                "name": plugin_info.name,
                "version": plugin_info.version,
                "author": plugin_info.author,
                "data_source": plugin_info.data_source,
                "has_config": plugin_name in self.plugin_configs,
                "config_valid": self._validate_current_config(plugin_name),
                "allowed_domains": plugin.get_allowed_domains(),
                "required_permissions": plugin.get_required_permissions()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _validate_current_config(self, plugin_name: str) -> bool:
        """验证当前配置是否有效"""
        
        try:
            plugin = self.get_plugin(plugin_name)
            config = self.plugin_configs.get(plugin_name)
            
            if not plugin or not config:
                return False
            
            plugin.validate_config(config)
            return True
        except:
            return False
    
    def cleanup_all_plugins(self):
        """清理所有插件"""
        
        plugin_names = list(self.plugins.keys())
        for plugin_name in plugin_names:
            try:
                self.unload_plugin(plugin_name)
            except Exception as e:
                logger.error(f"清理插件失败: {plugin_name}, 错误: {e}")
        
        logger.info("所有插件已清理")


# 全局插件管理器实例
plugin_manager = PluginManager()