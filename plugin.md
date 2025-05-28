# OpenPart 爬虫插件开发者指南

## 📖 目录

1. [概述](#概述)
2. [快速开始](#快速开始)
3. [插件架构和规范](#插件架构和规范)
4. [配置系统详解](#配置系统详解)
5. [安全约束和规范](#安全约束和规范)
6. [数据模型和类型](#数据模型和类型)
7. [API接口规范](#api接口规范)
8. [完整示例](#完整示例)
9. [最佳实践](#最佳实践)
10. [调试和测试](#调试和测试)
11. [常见问题](#常见问题)

---

## 概述

OpenPart 爬虫插件系统是一个安全、灵活、易扩展的数据采集框架，允许开发者创建自定义的零件数据爬虫插件。

### 🎯 主要特性

- **类型安全**：基于 Pydantic 的严格类型检查
- **安全沙箱**：AST 静态分析防止恶意代码执行
- **动态配置**：可视化的插件配置界面
- **任务调度**：支持手动、定时和间隔执行
- **实时监控**：完整的日志记录和状态跟踪
- **前端集成**：开箱即用的管理界面

### 🏗️ 系统架构

```
OpenPart 插件系统
├── 插件基类 (BaseCrawlerPlugin)
├── 插件管理器 (PluginManager)
├── 安全验证器 (SecurityValidator)
├── 任务调度器 (TaskScheduler)
├── API 接口层 (FastAPI)
└── 前端管理界面 (Vue 3)
```

---

## 快速开始

### 1. 环境准备

**必需依赖：**
```python
# 系统已内置，无需安装
from app.plugins.crawler_base import BaseCrawlerPlugin
from typing import Dict, Any, List
from pydantic import BaseModel
```

### 2. 创建基础插件

```python
# my_plugin.py
from app.plugins.crawler_base import (
    BaseCrawlerPlugin, PluginInfo, ConfigField,
    CrawlResult, TestResult, PartData, DataSourceType
)

class MyPlugin(BaseCrawlerPlugin):
    """我的第一个插件"""
    
    @property
    def plugin_info(self) -> PluginInfo:
        return PluginInfo(
            name="我的插件",
            version="1.0.0",
            description="插件描述",
            author="你的名字",
            data_source="数据源名称",
            data_source_type=DataSourceType.ECOMMERCE
        )
    
    @property
    def config_schema(self) -> List[ConfigField]:
        return [
            ConfigField(
                name="api_url",
                label="API地址",
                type="url",
                required=True,
                help_text="目标网站的API地址"
            )
        ]
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        if not config.get("api_url"):
            raise ValueError("API地址不能为空")
        return True
    
    def test_connection(self, config: Dict[str, Any]) -> TestResult:
        # 实现连接测试逻辑
        return TestResult(
            success=True,
            message="连接成功"
        )
    
    def crawl(self, config: Dict[str, Any], **kwargs) -> CrawlResult:
        # 实现数据爬取逻辑
        parts = []  # 爬取的零件数据
        
        return CrawlResult(
            success=True,
            data=parts,
            total_count=len(parts)
        )

# 必需：创建插件实例
plugin = MyPlugin()
```

### 3. 上传和测试

1. 将 `.py` 文件上传到管理后台
2. 在插件管理界面进行配置
3. 测试连接并执行爬取任务

---

## 插件架构和规范

### 核心接口

所有插件必须继承 `BaseCrawlerPlugin` 并实现以下抽象方法：

#### 1. plugin_info 属性

```python
@property
@abstractmethod
def plugin_info(self) -> PluginInfo:
    """返回插件基本信息"""
    pass
```

**PluginInfo 字段说明：**

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| name | str | ✅ | 插件名称（中文可读） |
| version | str | ✅ | 版本号（如：1.0.0） |
| description | str | ✅ | 插件功能描述 |
| author | str | ✅ | 开发者姓名或团队 |
| data_source | str | ✅ | 数据源名称 |
| data_source_type | DataSourceType | ✅ | 数据源类型枚举 |
| homepage | str | ❌ | 数据源官网 |
| terms_url | str | ❌ | 服务条款链接 |
| rate_limit | int | ❌ | 请求频率限制(秒) |
| batch_size | int | ❌ | 批次处理大小 |

**数据源类型枚举：**
```python
class DataSourceType(Enum):
    ECOMMERCE = "ecommerce"     # 电商平台
    SUPPLIER = "supplier"       # 供应商网站  
    DATABASE = "database"       # 数据库
    API = "api"                # API接口
    CATALOG = "catalog"        # 产品目录
    OTHER = "other"            # 其他
```

#### 2. config_schema 属性

```python
@property
@abstractmethod
def config_schema(self) -> List[ConfigField]:
    """返回插件配置表单定义"""
    pass
```

#### 3. 核心方法

```python
@abstractmethod
def validate_config(self, config: Dict[str, Any]) -> bool:
    """验证配置参数"""
    pass

@abstractmethod  
def test_connection(self, config: Dict[str, Any]) -> TestResult:
    """测试数据源连接"""
    pass

@abstractmethod
def crawl(self, config: Dict[str, Any], **kwargs) -> CrawlResult:
    """执行数据爬取"""
    pass
```

### 可选方法

```python
def get_allowed_domains(self) -> List[str]:
    """返回允许访问的域名列表"""
    return []

def get_required_permissions(self) -> List[str]:
    """返回需要的权限列表"""
    return ["network"]

def cleanup(self):
    """插件卸载时的清理工作"""
    pass
```

---

## 配置系统详解

### ConfigField 完整参考

```python
ConfigField(
    name="field_name",          # 字段名称（英文，代码中使用）
    label="显示名称",            # 界面显示标签
    type="field_type",          # 字段类型
    required=False,             # 是否必填
    default=None,               # 默认值
    placeholder="占位符",        # 输入提示
    options=[],                 # 选择项（select类型）
    help_text="帮助说明",        # 详细说明
    validation={}               # 验证规则
)
```

### 支持的字段类型

#### 1. 文本输入类型

```python
# 普通文本
ConfigField(
    name="username",
    label="用户名",
    type="text",
    required=True,
    placeholder="请输入用户名"
)

# 密码输入
ConfigField(
    name="password",
    label="密码",
    type="password",
    required=True,
    help_text="API访问密码"
)

# URL输入
ConfigField(
    name="api_url",
    label="API地址",
    type="url",
    required=True,
    validation={
        "pattern": r"^https?://.*",
        "message": "请输入有效的URL"
    }
)

# 多行文本
ConfigField(
    name="description",
    label="描述",
    type="textarea",
    placeholder="输入详细描述..."
)
```

#### 2. 数字输入类型

```python
ConfigField(
    name="timeout",
    label="超时时间(秒)",
    type="number",
    default=30,
    validation={
        "min": 1,
        "max": 300,
        "step": 1
    },
    help_text="请求超时时间，1-300秒"
)
```

#### 3. 选择类型

```python
# 下拉选择
ConfigField(
    name="region",
    label="地区",
    type="select",
    default="cn",
    options=[
        {"value": "cn", "label": "中国"},
        {"value": "us", "label": "美国"},
        {"value": "eu", "label": "欧洲"}
    ]
)

# 单选按钮
ConfigField(
    name="format",
    label="数据格式",
    type="radio",
    default="json",
    options=[
        {"value": "json", "label": "JSON"},
        {"value": "xml", "label": "XML"}
    ]
)

# 多选框
ConfigField(
    name="categories",
    label="类别",
    type="checkbox-group",
    default=[],
    options=[
        {"value": "resistor", "label": "电阻"},
        {"value": "capacitor", "label": "电容"}
    ]
)
```

#### 4. 布尔类型

```python
ConfigField(
    name="include_images",
    label="包含图片",
    type="checkbox",
    default=True,
    help_text="是否获取零件图片"
)
```

#### 5. JSON类型

```python
ConfigField(
    name="headers",
    label="HTTP请求头",
    type="json",
    default='{"User-Agent": "OpenPart-Crawler"}',
    help_text="自定义HTTP请求头，JSON格式"
)
```

### 验证规则

```python
validation = {
    # 字符串长度
    "min_length": 5,
    "max_length": 100,
    
    # 数字范围
    "min": 0,
    "max": 1000,
    "step": 0.1,
    
    # 正则表达式
    "pattern": r"^[a-zA-Z0-9]+$",
    "message": "只能包含字母和数字"
}
```

---

## 安全约束和规范

### 🚫 禁用功能

为了系统安全，插件代码中禁止使用以下功能：

#### 1. 禁用的导入模块

```python
# 禁止导入的模块
import os          # ❌ 系统操作
import sys         # ❌ 系统操作
import subprocess  # ❌ 进程执行
import socket      # ❌ 网络底层操作
import threading   # ❌ 多线程
import multiprocessing  # ❌ 多进程

# 允许的导入示例
import requests    # ✅ HTTP请求
import json        # ✅ JSON处理
import time        # ✅ 时间操作
import re          # ✅ 正则表达式
from urllib.parse import urljoin  # ✅ URL处理
```

#### 2. 禁用的函数调用

```python
# 禁止的函数
eval()         # ❌ 动态代码执行
exec()         # ❌ 动态代码执行
compile()      # ❌ 代码编译
__import__()   # ❌ 动态导入
open()         # ❌ 文件操作
```

#### 3. 禁用的属性访问

```python
# 禁止访问的属性
obj.__class__      # ❌ 类信息
obj.__globals__    # ❌ 全局变量
obj.__code__       # ❌ 代码对象
```

### ✅ 推荐的实现方式

```python
# 推荐的HTTP请求
import requests
response = requests.get(url, timeout=30)

# 推荐的数据解析
import json
data = json.loads(response.text)

# 推荐的URL处理
from urllib.parse import urljoin, urlparse
full_url = urljoin(base_url, relative_url)

# 推荐的错误处理
try:
    # 网络请求
    response = requests.get(url)
    response.raise_for_status()
except requests.RequestException as e:
    raise NetworkError(f"请求失败: {str(e)}")
```

---

## 数据模型和类型

### PartData - 零件数据模型

```python
class PartData(BaseModel):
    """零件数据标准格式"""
    
    # 必需字段
    name: str                           # 零件名称
    
    # 可选字段
    category: Optional[str] = None      # 零件类别
    description: Optional[str] = None   # 零件描述
    properties: Optional[Dict[str, Any]] = None  # 自定义属性
    image_url: Optional[str] = None     # 图片URL
    source_url: Optional[str] = None    # 原始数据URL
    external_id: Optional[str] = None   # 外部系统ID
    price: Optional[float] = None       # 价格信息
    availability: Optional[str] = None  # 库存状态
```

**示例：**

```python
part = PartData(
    name="1kΩ精密电阻",
    category="电阻器",
    description="1%精度金属膜电阻，功率0.25W",
    properties={
        "阻值": "1kΩ",
        "功率": "0.25W", 
        "精度": "±1%",
        "温度系数": "±100ppm/°C",
        "封装": "0805"
    },
    price=0.05,
    availability="现货",
    image_url="https://example.com/images/resistor_1k.jpg",
    source_url="https://example.com/products/res-1k-001"
)
```

### CrawlResult - 爬取结果模型

```python
class CrawlResult(BaseModel):
    """爬取结果"""
    success: bool                       # 是否成功
    data: List[PartData]                # 爬取的数据列表
    total_count: int                    # 总数据量
    error_message: Optional[str] = None # 错误信息
    warnings: List[str] = []            # 警告信息
    execution_time: Optional[float] = None  # 执行时间(秒)
    next_page_token: Optional[str] = None   # 下一页标识
```

### TestResult - 测试结果模型

```python
class TestResult(BaseModel):
    """测试结果"""
    success: bool                       # 测试是否成功
    message: str                        # 测试结果信息
    response_time: Optional[float] = None   # 响应时间(秒)
    sample_data: Optional[Dict[str, Any]] = None  # 示例数据
```

---

## API接口规范

### 插件管理接口

#### 1. 获取插件列表

```http
GET /api/admin/crawler-plugins/
Authorization: Bearer {token}
```

**响应：**
```json
[
  {
    "id": 1,
    "name": "test_electronics",
    "display_name": "测试电子元件爬虫",
    "version": "1.0.0",
    "description": "用于测试的电子元件数据爬虫",
    "author": "OpenPart Team",
    "data_source": "测试电子商城",
    "status": "active",
    "is_active": true,
    "config": {
      "api_base_url": "https://api.test-electronics.com",
      "category_filter": "all"
    },
    "config_schema": [...],
    "allowed_domains": ["test-electronics.com"],
    "required_permissions": ["network"],
    "run_count": 5,
    "success_count": 4,
    "error_count": 1,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### 2. 上传插件

```http
POST /api/admin/crawler-plugins/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

plugin_file: {file.py}
```

#### 3. 更新插件配置

```http
PUT /api/admin/crawler-plugins/{plugin_id}/config
Authorization: Bearer {token}
Content-Type: application/json

{
  "config": {
    "api_base_url": "https://api.example.com",
    "timeout": 30
  }
}
```

#### 4. 测试插件连接

```http
POST /api/admin/crawler-plugins/{plugin_id}/test
Authorization: Bearer {token}
Content-Type: application/json

{
  "config": {
    "api_base_url": "https://api.example.com"
  }
}
```

**响应：**
```json
{
  "success": true,
  "message": "连接测试成功",
  "response_time": 1.23,
  "sample_data": {
    "server": "api-server",
    "version": "v2.1"
  }
}
```

### 任务管理接口

#### 1. 创建任务

```http
POST /api/admin/crawler-plugins/{plugin_id}/tasks
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "每日爬取任务",
  "description": "每天定时爬取最新数据",
  "schedule_type": "cron",
  "schedule_config": {
    "cron_expression": "0 0 * * *"
  },
  "config": {
    "category_filter": "resistor"
  }
}
```

#### 2. 执行任务

```http
POST /api/admin/crawler-plugins/{plugin_id}/tasks/{task_id}/execute
Authorization: Bearer {token}
```

#### 3. 获取任务日志

```http
GET /api/admin/crawler-plugins/tasks/{task_id}/logs
Authorization: Bearer {token}
```

---

## 完整示例

### 高级电商插件示例

```python
# advanced_ecommerce_plugin.py
"""
高级电商爬虫插件示例

展示完整的插件开发最佳实践
"""

import time
import requests
import json
import re
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
from app.plugins.crawler_base import (
    BaseCrawlerPlugin, PluginInfo, ConfigField,
    CrawlResult, TestResult, PartData, DataSourceType,
    PluginUtils, NetworkError, DataError
)

class AdvancedEcommercePlugin(BaseCrawlerPlugin):
    """高级电商爬虫插件"""
    
    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OpenPart-Crawler/1.0'
        })
    
    @property
    def plugin_info(self) -> PluginInfo:
        return PluginInfo(
            name="高级电商爬虫",
            version="2.1.0",
            description="功能完整的电商网站零件数据爬虫，支持多种数据源和高级配置",
            author="Plugin Developer",
            data_source="Generic E-commerce",
            data_source_type=DataSourceType.ECOMMERCE,
            homepage="https://ecommerce-site.com",
            rate_limit=2,
            batch_size=50
        )
    
    @property
    def config_schema(self) -> List[ConfigField]:
        return [
            # 基础配置
            ConfigField(
                name="api_base_url",
                label="API基础地址",
                type="url",
                required=True,
                placeholder="https://api.example.com",
                help_text="电商网站的API基础地址",
                validation={"pattern": r"^https://.*"}
            ),
            
            ConfigField(
                name="api_key",
                label="API密钥",
                type="password",
                required=False,
                help_text="如果需要认证请填写API密钥"
            ),
            
            # 搜索配置
            ConfigField(
                name="search_categories",
                label="搜索类别",
                type="checkbox-group",
                default=["electronic"],
                options=[
                    {"value": "electronic", "label": "电子元件"},
                    {"value": "mechanical", "label": "机械零件"},
                    {"value": "sensor", "label": "传感器"},
                    {"value": "connector", "label": "连接器"}
                ],
                help_text="选择要爬取的零件类别"
            ),
            
            ConfigField(
                name="price_range",
                label="价格范围",
                type="select",
                default="all",
                options=[
                    {"value": "all", "label": "所有价格"},
                    {"value": "low", "label": "低价(≤10元)"},
                    {"value": "medium", "label": "中价(10-100元)"},
                    {"value": "high", "label": "高价(≥100元)"}
                ]
            ),
            
            # 高级配置
            ConfigField(
                name="request_settings",
                label="请求设置",
                type="json",
                default='{"timeout": 30, "retries": 3}',
                help_text="HTTP请求的高级设置，JSON格式"
            ),
            
            ConfigField(
                name="custom_headers",
                label="自定义请求头",
                type="textarea",
                placeholder="Referer: https://example.com\nX-Custom: value",
                help_text="每行一个请求头，格式：键: 值"
            ),
            
            # 数据处理配置
            ConfigField(
                name="data_filters",
                label="数据过滤器",
                type="json",
                default='{"min_stock": 1, "exclude_discontinued": true}',
                help_text="数据过滤规则，JSON格式"
            ),
            
            ConfigField(
                name="enable_image_download",
                label="下载产品图片",
                type="checkbox",
                default=False,
                help_text="启用后会下载并转换图片URL"
            ),
            
            # 性能配置
            ConfigField(
                name="concurrent_requests",
                label="并发请求数",
                type="number",
                default=3,
                validation={"min": 1, "max": 10},
                help_text="同时进行的HTTP请求数量"
            ),
            
            ConfigField(
                name="request_delay",
                label="请求延迟(秒)",
                type="number",
                default=1.0,
                validation={"min": 0.1, "max": 10.0, "step": 0.1},
                help_text="请求之间的延迟时间"
            )
        ]
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置参数"""
        
        # 验证必需字段
        if not config.get("api_base_url"):
            raise ValueError("API基础地址不能为空")
        
        # 验证URL格式
        if not PluginUtils.validate_url(config["api_base_url"]):
            raise ValueError("API基础地址格式不正确")
        
        # 验证JSON配置
        json_fields = ["request_settings", "data_filters"]
        for field in json_fields:
            if field in config and config[field]:
                try:
                    json.loads(config[field])
                except json.JSONDecodeError:
                    raise ValueError(f"{field} 必须是有效的JSON格式")
        
        # 验证数值范围
        if config.get("concurrent_requests", 0) > 10:
            raise ValueError("并发请求数不能超过10")
        
        return True
    
    def test_connection(self, config: Dict[str, Any]) -> TestResult:
        """测试数据源连接"""
        
        start_time = time.time()
        
        try:
            # 准备请求
            api_url = config["api_base_url"]
            headers = self._build_headers(config)
            
            # 测试基础连接
            test_endpoint = urljoin(api_url, "/health")
            response = self.session.get(
                test_endpoint,
                headers=headers,
                timeout=10
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    server_info = response.json()
                except:
                    server_info = {"status": "ok"}
                
                return TestResult(
                    success=True,
                    message=f"连接成功！服务器响应正常 (HTTP {response.status_code})",
                    response_time=round(response_time, 3),
                    sample_data=server_info
                )
            
            elif response.status_code == 404:
                # 健康检查端点不存在，尝试其他端点
                products_endpoint = urljoin(api_url, "/products")
                test_response = self.session.get(
                    products_endpoint,
                    headers=headers,
                    timeout=10,
                    params={"limit": 1}
                )
                
                if test_response.status_code in [200, 401, 403]:
                    return TestResult(
                        success=True,
                        message="连接成功！API端点可访问",
                        response_time=round(time.time() - start_time, 3),
                        sample_data={"endpoint": "products", "status": test_response.status_code}
                    )
            
            return TestResult(
                success=False,
                message=f"连接失败：HTTP {response.status_code}"
            )
            
        except requests.Timeout:
            return TestResult(
                success=False,
                message="连接超时，请检查网络或API地址"
            )
        except requests.ConnectionError:
            return TestResult(
                success=False,
                message="无法连接到服务器，请检查API地址"
            )
        except Exception as e:
            return TestResult(
                success=False,
                message=f"连接测试失败: {str(e)}"
            )
    
    def crawl(self, config: Dict[str, Any], **kwargs) -> CrawlResult:
        """执行数据爬取"""
        
        start_time = time.time()
        crawled_parts = []
        warnings = []
        
        try:
            # 解析配置
            api_url = config["api_base_url"]
            headers = self._build_headers(config)
            search_categories = config.get("search_categories", ["electronic"])
            price_range = config.get("price_range", "all")
            
            # 解析高级配置
            request_settings = self._parse_json_config(
                config.get("request_settings", "{}"),
                {"timeout": 30, "retries": 3}
            )
            
            data_filters = self._parse_json_config(
                config.get("data_filters", "{}"),
                {"min_stock": 1}
            )
            
            # 分页参数
            page_token = kwargs.get("page_token", "1")
            limit = kwargs.get("limit", config.get("batch_size", 50))
            
            # 爬取每个类别
            for category in search_categories:
                try:
                    category_parts = self._crawl_category(
                        api_url, headers, category, price_range,
                        request_settings, data_filters,
                        page_token, limit // len(search_categories)
                    )
                    crawled_parts.extend(category_parts)
                    
                    # 请求延迟
                    delay = config.get("request_delay", 1.0)
                    time.sleep(delay)
                    
                except Exception as e:
                    warnings.append(f"爬取类别 {category} 时出错: {str(e)}")
                    continue
            
            # 后处理
            if config.get("enable_image_download", False):
                crawled_parts = self._process_images(crawled_parts)
            
            execution_time = time.time() - start_time
            
            # 计算下一页标识
            next_page = None
            if len(crawled_parts) >= limit:
                current_page = int(page_token) if page_token.isdigit() else 1
                next_page = str(current_page + 1)
            
            return CrawlResult(
                success=True,
                data=crawled_parts,
                total_count=len(crawled_parts),
                execution_time=round(execution_time, 3),
                warnings=warnings,
                next_page_token=next_page
            )
            
        except Exception as e:
            return CrawlResult(
                success=False,
                data=crawled_parts,
                total_count=len(crawled_parts),
                error_message=f"爬取过程出错: {str(e)}",
                execution_time=time.time() - start_time,
                warnings=warnings
            )
    
    def _build_headers(self, config: Dict[str, Any]) -> Dict[str, str]:
        """构建HTTP请求头"""
        
        headers = {
            'User-Agent': 'OpenPart-Crawler/2.1',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # 添加API密钥
        if config.get("api_key"):
            headers['Authorization'] = f'Bearer {config["api_key"]}'
        
        # 添加自定义请求头
        custom_headers = config.get("custom_headers", "")
        if custom_headers:
            for line in custom_headers.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip()] = value.strip()
        
        return headers
    
    def _parse_json_config(self, json_str: str, default: Dict) -> Dict:
        """解析JSON配置"""
        try:
            if json_str:
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        return default
    
    def _crawl_category(self, api_url: str, headers: Dict, category: str,
                       price_range: str, request_settings: Dict,
                       data_filters: Dict, page_token: str, limit: int) -> List[PartData]:
        """爬取指定类别的零件"""
        
        parts = []
        
        # 构建搜索URL
        search_url = urljoin(api_url, "/products/search")
        params = {
            'category': category,
            'page': page_token,
            'limit': limit
        }
        
        # 添加价格过滤
        if price_range != "all":
            price_filters = {
                "low": {"max_price": 10},
                "medium": {"min_price": 10, "max_price": 100},
                "high": {"min_price": 100}
            }
            params.update(price_filters.get(price_range, {}))
        
        # 发送请求
        timeout = request_settings.get("timeout", 30)
        retries = request_settings.get("retries", 3)
        
        for attempt in range(retries):
            try:
                response = self.session.get(
                    search_url,
                    headers=headers,
                    params=params,
                    timeout=timeout
                )
                response.raise_for_status()
                break
            except requests.RequestException as e:
                if attempt == retries - 1:
                    raise NetworkError(f"请求失败: {str(e)}")
                time.sleep(1 * (attempt + 1))  # 递增延迟
        
        # 解析响应
        try:
            data = response.json()
            products = data.get('products', [])
        except json.JSONDecodeError:
            raise DataError("API返回的不是有效的JSON数据")
        
        # 处理每个产品
        for product in products:
            try:
                # 应用数据过滤器
                if not self._apply_filters(product, data_filters):
                    continue
                
                part = self._parse_product(product, category)
                if part:
                    parts.append(part)
                    
            except Exception as e:
                # 记录单个产品的错误，但继续处理其他产品
                continue
        
        return parts
    
    def _apply_filters(self, product: Dict, filters: Dict) -> bool:
        """应用数据过滤器"""
        
        # 最小库存过滤
        min_stock = filters.get("min_stock", 0)
        if product.get("stock", 0) < min_stock:
            return False
        
        # 排除停产产品
        if filters.get("exclude_discontinued", False):
            if product.get("status") == "discontinued":
                return False
        
        return True
    
    def _parse_product(self, product: Dict, category: str) -> Optional[PartData]:
        """解析产品数据为零件格式"""
        
        try:
            # 基础信息
            name = PluginUtils.clean_text(product.get("name", ""))
            if not name:
                return None
            
            description = PluginUtils.clean_text(product.get("description", ""))
            
            # 价格处理
            price = None
            price_str = product.get("price")
            if price_str:
                price = PluginUtils.extract_number(str(price_str))
            
            # 图片URL
            image_url = product.get("image_url")
            if image_url:
                image_url = PluginUtils.normalize_url(image_url, product.get("base_url"))
            
            # 自定义属性
            properties = {}
            specs = product.get("specifications", {})
            if isinstance(specs, dict):
                for key, value in specs.items():
                    if value:
                        properties[str(key)] = str(value)
            
            # 库存状态
            stock = product.get("stock", 0)
            availability = "现货" if stock > 0 else "缺货"
            
            return PartData(
                name=name,
                category=self._normalize_category(category),
                description=description,
                properties=properties if properties else None,
                price=price,
                availability=availability,
                image_url=image_url,
                source_url=product.get("url"),
                external_id=str(product.get("id", ""))
            )
            
        except Exception as e:
            return None
    
    def _normalize_category(self, category: str) -> str:
        """标准化类别名称"""
        category_map = {
            "electronic": "电子元件",
            "mechanical": "机械零件", 
            "sensor": "传感器",
            "connector": "连接器"
        }
        return category_map.get(category, category)
    
    def _process_images(self, parts: List[PartData]) -> List[PartData]:
        """处理图片URL"""
        # 这里可以实现图片下载和转换逻辑
        # 由于安全限制，实际实现会相对简单
        return parts
    
    def get_allowed_domains(self) -> List[str]:
        """返回允许访问的域名"""
        return [
            "api.ecommerce-site.com",
            "cdn.ecommerce-site.com",
            "img.ecommerce-site.com"
        ]
    
    def get_required_permissions(self) -> List[str]:
        """返回需要的权限"""
        return ["network"]
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'session'):
            self.session.close()

# 必需：创建插件实例
plugin = AdvancedEcommercePlugin()
```

---

## 最佳实践

### 1. 代码组织

```python
class MyPlugin(BaseCrawlerPlugin):
    """插件主类"""
    
    def __init__(self):
        super().__init__()
        # 初始化会话、缓存等资源
        self.session = requests.Session()
        self.cache = {}
    
    # 将复杂逻辑拆分为私有方法
    def _build_headers(self, config):
        """构建请求头"""
        pass
    
    def _parse_response(self, response):
        """解析响应数据"""
        pass
    
    def _validate_data(self, data):
        """验证数据完整性"""
        pass
```

### 2. 错误处理

```python
def test_connection(self, config: Dict[str, Any]) -> TestResult:
    try:
        # 核心逻辑
        response = requests.get(url, timeout=10)
        return TestResult(success=True, message="连接成功")
        
    except requests.Timeout:
        return TestResult(success=False, message="连接超时")
    except requests.ConnectionError:
        return TestResult(success=False, message="无法连接到服务器")
    except Exception as e:
        return TestResult(success=False, message=f"未知错误: {str(e)}")
```

### 3. 配置验证

```python
def validate_config(self, config: Dict[str, Any]) -> bool:
    # 检查必需字段
    required_fields = ["api_url", "timeout"]
    for field in required_fields:
        if not config.get(field):
            raise ValueError(f"{field} 不能为空")
    
    # 类型检查
    if not isinstance(config.get("timeout"), (int, float)):
        raise ValueError("timeout 必须是数字")
    
    # 范围检查
    if config["timeout"] < 1 or config["timeout"] > 300:
        raise ValueError("timeout 必须在 1-300 秒之间")
    
    return True
```

### 4. 数据处理

```python
def _clean_and_validate_data(self, raw_data: Dict) -> Optional[PartData]:
    """清理和验证数据"""
    
    # 清理文本
    name = PluginUtils.clean_text(raw_data.get("name", ""))
    if not name:
        return None
    
    # 提取数字
    price = PluginUtils.extract_number(raw_data.get("price", ""))
    
    # 标准化URL
    image_url = raw_data.get("image")
    if image_url:
        image_url = PluginUtils.normalize_url(image_url, base_url)
    
    return PartData(name=name, price=price, image_url=image_url)
```

### 5. 性能优化

```python
def crawl(self, config: Dict[str, Any], **kwargs) -> CrawlResult:
    # 使用会话复用连接
    session = requests.Session()
    
    # 批量处理
    batch_size = config.get("batch_size", 50)
    
    # 适当延迟避免被封
    delay = config.get("request_delay", 1.0)
    
    for batch in self._get_batches(data, batch_size):
        results = self._process_batch(batch, session)
        time.sleep(delay)
    
    session.close()
```

---

## 调试和测试

### 1. 本地测试

```python
# test_my_plugin.py
from my_plugin import plugin

# 测试配置验证
config = {
    "api_url": "https://api.example.com",
    "timeout": 30
}

try:
    plugin.validate_config(config)
    print("✅ 配置验证通过")
except ValueError as e:
    print(f"❌ 配置错误: {e}")

# 测试连接
result = plugin.test_connection(config)
print(f"连接测试: {'成功' if result.success else '失败'}")
print(f"消息: {result.message}")

# 测试爬取
crawl_result = plugin.crawl(config, limit=5)
print(f"爬取结果: {len(crawl_result.data)} 条数据")
```

### 2. 日志记录

```python
import logging

class MyPlugin(BaseCrawlerPlugin):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
    
    def crawl(self, config: Dict[str, Any], **kwargs) -> CrawlResult:
        self.logger.info("开始爬取数据")
        
        try:
            # 爬取逻辑
            self.logger.debug(f"处理URL: {url}")
            
        except Exception as e:
            self.logger.error(f"爬取失败: {e}")
            raise
```

### 3. 单元测试

```python
import unittest
from unittest.mock import patch, Mock

class TestMyPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = MyPlugin()
        self.config = {"api_url": "https://test.com"}
    
    def test_validate_config_success(self):
        """测试配置验证成功"""
        result = self.plugin.validate_config(self.config)
        self.assertTrue(result)
    
    def test_validate_config_missing_url(self):
        """测试缺少URL的配置验证"""
        with self.assertRaises(ValueError):
            self.plugin.validate_config({})
    
    @patch('requests.get')
    def test_connection_success(self, mock_get):
        """测试连接成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.plugin.test_connection(self.config)
        self.assertTrue(result.success)

if __name__ == '__main__':
    unittest.main()
```

---

## 常见问题

### Q: 如何处理分页数据？

**A:** 使用 `next_page_token` 机制：

```python
def crawl(self, config: Dict[str, Any], **kwargs) -> CrawlResult:
    page_token = kwargs.get("page_token", "1")
    current_page = int(page_token) if page_token.isdigit() else 1
    
    # 爬取当前页数据
    data = self._fetch_page(current_page)
    
    # 设置下一页标识
    next_page = None
    if len(data) >= batch_size:
        next_page = str(current_page + 1)
    
    return CrawlResult(
        success=True,
        data=data,
        next_page_token=next_page
    )
```

### Q: 如何处理网站反爬虫机制？

**A:** 使用以下策略：

```python
# 1. 设置合理的请求延迟
time.sleep(random.uniform(1, 3))

# 2. 使用真实的User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# 3. 会话保持
session = requests.Session()

# 4. 处理验证码和登录
def handle_captcha(self, response):
    # 检测并处理验证码
    pass
```

### Q: 如何处理大量数据？

**A:** 采用流式处理：

```python
def crawl(self, config: Dict[str, Any], **kwargs) -> CrawlResult:
    limit = kwargs.get("limit", 1000)
    batch_size = 100
    all_parts = []
    
    for offset in range(0, limit, batch_size):
        batch_parts = self._fetch_batch(offset, batch_size)
        all_parts.extend(batch_parts)
        
        # 内存控制
        if len(all_parts) >= limit:
            break
            
        time.sleep(1)  # 请求间隔
    
    return CrawlResult(success=True, data=all_parts[:limit])
```

### Q: 如何处理动态内容（JavaScript渲染）？

**A:** 当前系统不支持浏览器引擎，建议：

1. 寻找API接口而非网页抓取
2. 分析网络请求找到数据接口
3. 使用移动端API（通常更简单）

### Q: 插件上传后无法加载怎么办？

**A:** 检查以下问题：

1. **语法错误**：确保Python语法正确
2. **导入错误**：避免使用禁用的模块
3. **类名错误**：确保继承自`BaseCrawlerPlugin`
4. **实例变量**：确保文件末尾有`plugin = YourPlugin()`
5. **编码问题**：使用UTF-8编码保存文件

### Q: 如何测试插件的安全性？

**A:** 系统会自动进行AST安全扫描，但你也可以自查：

```python
# ❌ 避免这些危险操作
import os
eval("malicious_code")
__import__("sys")

# ✅ 使用安全的替代方案
import requests
import json
import re
```

---

## 总结

OpenPart 插件系统为开发者提供了一个功能强大而安全的数据采集平台。通过遵循本文档的规范和最佳实践，你可以：

- 🚀 快速开发高质量的爬虫插件
- 🛡️ 确保代码的安全性和稳定性
- 🎨 创建用户友好的配置界面
- 📊 实现可靠的数据采集和处理
- 🔧 便于维护和扩展

记住始终遵守目标网站的robots.txt和服务条款，合理控制请求频率，做一个负责任的爬虫开发者。

---

**开发愉快！** 🎉

*如有问题，请查看系统日志或联系技术支持。*