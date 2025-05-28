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
    """插件安全验证器"""
    
    # 禁用的导入模块
    FORBIDDEN_IMPORTS = {
        'os', 'sys', 'subprocess', 'socket', 'threading', 'multiprocessing',
        'eval', 'exec', 'compile', '__import__', 'open', 'file',
        'input', 'raw_input', 'reload', 'globals', 'locals', 'vars',
        'dir', 'getattr', 'setattr', 'delattr', 'hasattr'
    }
    
    # 禁用的函数调用
    FORBIDDEN_FUNCTIONS = {
        'eval', 'exec', 'compile', '__import__', 'open', 'file',
        'input', 'raw_input', 'reload'
    }
    
    # 危险的属性访问
    DANGEROUS_ATTRIBUTES = {
        '__class__', '__bases__', '__subclasses__', '__mro__',
        '__globals__', '__code__', '__func__', '__self__'
    }
    
    def validate_plugin_code(self, file_path: str) -> bool:
        """验证插件代码安全性"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # 解析AST
            tree = ast.parse(code)
            
            # 检查导入语句
            self._check_imports(tree)
            
            # 检查函数调用
            self._check_function_calls(tree)
            
            # 检查属性访问
            self._check_attribute_access(tree)
            
            # 检查字符串内容
            self._check_string_literals(tree)
            
            return True
            
        except Exception as e:
            logger.error(f"代码安全验证失败: {e}")
            raise SecurityError(f"插件代码存在安全风险: {e}")
    
    def _check_imports(self, tree: ast.AST):
        """检查导入语句"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in self.FORBIDDEN_IMPORTS:
                        raise SecurityError(f"禁止导入模块: {alias.name}")
            
            elif isinstance(node, ast.ImportFrom):
                if node.module in self.FORBIDDEN_IMPORTS:
                    raise SecurityError(f"禁止导入模块: {node.module}")
                
                # 检查from import语句
                for alias in node.names:
                    if alias.name in self.FORBIDDEN_IMPORTS:
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
    
    def _check_attribute_access(self, tree: ast.AST):
        """检查属性访问"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                if node.attr in self.DANGEROUS_ATTRIBUTES:
                    raise SecurityError(f"禁止访问危险属性: {node.attr}")
    
    def _check_string_literals(self, tree: ast.AST):
        """检查字符串字面量"""
        dangerous_patterns = [
            r'__.*__',  # 双下划线属性
            r'eval\s*\(',  # eval调用
            r'exec\s*\(',  # exec调用
            r'import\s+os',  # 动态导入os
            r'import\s+sys',  # 动态导入sys
        ]
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Str):
                content = node.s
                for pattern in dangerous_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        raise SecurityError(f"字符串包含危险内容: {pattern}")


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
        """验证插件文件并返回插件信息"""
        
        try:
            # 安全验证
            self.security_validator.validate_plugin_code(file_path)
            
            # 加载模块获取信息
            spec = importlib.util.spec_from_file_location("temp_plugin", file_path)
            if not spec or not spec.loader:
                raise ValueError("无法加载插件文件")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找插件类
            plugin_instance = None
            if hasattr(module, 'plugin'):
                plugin_instance = module.plugin
            else:
                # 查找继承自BaseCrawlerPlugin的类
                for item_name in dir(module):
                    item = getattr(module, item_name)
                    if (isinstance(item, type) and 
                        issubclass(item, BaseCrawlerPlugin) and 
                        item != BaseCrawlerPlugin):
                        plugin_instance = item()
                        break
            
            if not plugin_instance:
                raise ValueError("未找到有效的插件类")
            
            # 获取插件信息
            plugin_info = plugin_instance.plugin_info
            
            return {
                "name": plugin_info.name.replace(" ", "_").lower(),  # 标准化名称
                "display_name": plugin_info.name,
                "version": plugin_info.version,
                "description": plugin_info.description,
                "author": plugin_info.author,
                "data_source": plugin_info.data_source,
                "data_source_type": plugin_info.data_source_type.value,
                "homepage": plugin_info.homepage,
                "terms_url": plugin_info.terms_url,
                "rate_limit": plugin_info.rate_limit,
                "batch_size": plugin_info.batch_size,
                "config_schema": [field.dict() for field in plugin_instance.config_schema],
                "allowed_domains": plugin_instance.get_allowed_domains(),
                "required_permissions": plugin_instance.get_required_permissions()
            }
            
        except Exception as e:
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