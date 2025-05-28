# OpenPart 爬虫插件开发者指南

## 📖 目录

1. [概述](#概述)
2. [快速开始](#快速开始)
3. [插件架构和规范](#插件架构和规范)
4. [配置系统详解](#配置系统详解)
5. [安全约束和规范](#安全约束和规范)
6. [数据模型和类型](#数据模型和类型)
7. [API接口规范](#api接口规范)
8. [图片下载接口](#图片下载接口)
9. [文件上传和批量处理接口](#文件上传和批量处理接口)
10. [完整示例](#完整示例)
11. [最佳实践](#最佳实践)
12. [调试和测试](#调试和测试)
13. [常见问题](#常见问题)

---

## 概述

OpenPart 爬虫插件系统是一个安全、灵活、易扩展的数据采集框架，允许开发者创建自定义的零件数据爬虫插件。系统提供了完整的数据采集、处理和存储能力。

### 🎯 主要特性

- **类型安全**：基于 Pydantic 的严格类型检查
- **安全沙箱**：AST 静态分析防止恶意代码执行
- **动态配置**：可视化的插件配置界面
- **任务调度**：支持手动、定时和间隔执行
- **实时监控**：完整的日志记录和状态跟踪
- **图片下载**：安全的远程图片下载和本地存储
- **文件处理**：支持PDF、Excel等文档解析和批量数据导入
- **前端集成**：开箱即用的管理界面

### 🏗️ 系统架构

```
OpenPart 插件系统
├── 插件基类 (BaseCrawlerPlugin)
├── 插件管理器 (PluginManager)
├── 安全验证器 (SecurityValidator)
├── 任务调度器 (TaskScheduler)
├── 图片下载服务 (ImageDownloadAPI)
├── 文件处理服务 (FileUploadAPI)
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
import requests  # HTTP请求
import json      # JSON处理
import time      # 时间控制
```

### 2. 创建基础插件

```python
# my_plugin.py
from app.plugins.crawler_base import (
    BaseCrawlerPlugin, PluginInfo, ConfigField,
    CrawlResult, TestResult, PartData, DataSourceType
)
import requests
import json

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
        try:
            response = requests.get(config["api_url"], timeout=10)
            return TestResult(
                success=True,
                message="连接成功",
                response_time=1.0
            )
        except Exception as e:
            return TestResult(
                success=False,
                message=f"连接失败: {str(e)}"
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
    DOCUMENT = "document"      # 文档处理
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

## 图片下载接口

OpenPart 提供了安全的图片下载API，插件可以调用此接口将远程图片下载到本地服务器。

### 图片下载API

#### 接口说明

```http
POST /api/admin/images/download
Authorization: Bearer {admin_token}
Content-Type: application/json

{
    "part_id": 123,
    "image_url": "https://example.com/image.jpg",
    "replace_existing": true
}
```

**请求参数：**

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| part_id | int | ✅ | 零件ID |
| image_url | string | ✅ | 图片URL地址 |
| replace_existing | boolean | ❌ | 是否替换已有图片（默认true） |

**响应格式：**
```json
{
    "success": true,
    "message": "图片下载成功",
    "image_url": "/static/images/parts/part_123_abc123.jpg",
    "file_size": 245760,
    "content_type": "image/jpeg",
    "replaced_existing": false,
    "old_image_url": null
}
```

### 安全限制

- **URL安全检查**：阻止访问内网地址、localhost
- **文件大小限制**：最大5MB
- **文件类型验证**：仅支持JPG、PNG、GIF、WebP格式
- **图片格式验证**：检查文件头部确保为真实图片
- **自动优化**：下载的图片会自动调整大小并转换为JPEG格式

### 插件中的使用示例

```python
import requests

class MyPlugin(BaseCrawlerPlugin):
    def __init__(self):
        super().__init__()
        self.api_base = "http://localhost:8000/api"
        self.admin_token = None  # 在实际使用中会被系统注入
    
    def download_part_image(self, part_id: int, image_url: str) -> Optional[str]:
        """为零件下载图片"""
        try:
            response = requests.post(
                f"{self.api_base}/admin/images/download",
                headers={"Authorization": f"Bearer {self.admin_token}"},
                json={
                    "part_id": part_id,
                    "image_url": image_url,
                    "replace_existing": True
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("image_url")
            else:
                print(f"图片下载失败: {response.text}")
                return None
                
        except Exception as e:
            print(f"图片下载异常: {str(e)}")
            return None
    
    def crawl(self, config: Dict[str, Any], **kwargs) -> CrawlResult:
        parts = []
        
        # 爬取数据...
        for raw_data in self.fetch_raw_data(config):
            part = self.parse_part_data(raw_data)
            
            # 如果有图片URL，下载到本地
            if part.image_url and config.get("download_images", False):
                # 创建零件记录以获取ID
                part_id = self.create_part_record(part)
                
                # 下载图片
                local_image_url = self.download_part_image(part_id, part.image_url)
                if local_image_url:
                    part.image_url = local_image_url
            
            parts.append(part)
        
        return CrawlResult(success=True, data=parts, total_count=len(parts))
```

### URL安全测试接口

```http
GET /api/admin/images/download/test?url=https://example.com/image.jpg
Authorization: Bearer {admin_token}
```

用于测试URL是否符合安全要求。

---

## 文件上传和批量处理接口

对于处理PDF产品目录、Excel价格表等文档数据，OpenPart提供了安全的文件上传和批量数据处理接口。

### 工作流程

```
插件上传文档 → 服务器安全存储 → 插件下载解析 → 提交结构化数据 → 批量入库
```

### 1. 文件上传接口

#### 上传文件

```http
POST /api/admin/files/upload
Authorization: Bearer {admin_token}
Content-Type: multipart/form-data

file: {document_file}
```

**支持的文件格式：**
- 文档：PDF, DOC, DOCX
- 表格：XLS, XLSX, CSV
- 压缩包：ZIP, RAR, 7Z
- 文本：TXT, JSON, XML

**响应格式：**
```json
{
    "success": true,
    "message": "文件上传成功",
    "file_id": "abc123def456",
    "filename": "parts_catalog.pdf",
    "file_size": 2048576,
    "content_type": "application/pdf",
    "download_url": "/api/admin/files/abc123def456/download",
    "expires_at": "2024-01-02T00:00:00Z"
}
```

#### 下载文件

```http
GET /api/admin/files/{file_id}/download
Authorization: Bearer {admin_token}
```

插件使用此接口下载文件进行解析。

#### 删除文件

```http
DELETE /api/admin/files/{file_id}
Authorization: Bearer {admin_token}
```

插件处理完成后调用此接口清理临时文件。

### 2. 批量数据创建接口

#### 批量创建零件

```http
POST /api/admin/files/parts/batch-create
Authorization: Bearer {admin_token}
Content-Type: application/json

{
    "parts": [
        {
            "name": "零件名称1",
            "category": "电阻",
            "description": "零件描述",
            "properties": {"阻值": "1kΩ", "功率": "0.25W"},
            "price": 0.05,
            "image_url": null
        },
        {
            "name": "零件名称2",
            "category": "电容",
            "description": "另一个零件",
            "properties": {"容量": "100μF", "电压": "16V"}
        }
    ]
}
```

**响应格式：**
```json
{
    "success": true,
    "message": "批量处理完成",
    "total_processed": 2,
    "successful_creates": 2,
    "skipped_duplicates": 0,
    "errors": []
}
```

### 3. 安全限制

- **文件大小限制**：单文件最大50MB
- **批量数据限制**：单次最多创建1000个零件
- **文件类型验证**：检查MIME类型和文件头部
- **临时存储**：文件24小时后自动清理
- **恶意文件检测**：防止路径遍历和文件炸弹攻击

### 4. 插件使用示例

```python
import requests
import io
import csv
import json

class DocumentProcessorPlugin(BaseCrawlerPlugin):
    """文档处理插件示例"""
    
    def __init__(self):
        super().__init__()
        self.api_base = "http://localhost:8000/api"
        self.admin_token = None
    
    @property
    def plugin_info(self) -> PluginInfo:
        return PluginInfo(
            name="文档处理插件",
            version="1.0.0",
            description="处理PDF产品目录和Excel价格表",
            author="Plugin Developer",
            data_source="Document Files",
            data_source_type=DataSourceType.DOCUMENT
        )
    
    @property
    def config_schema(self) -> List[ConfigField]:
        return [
            ConfigField(
                name="file_type",
                label="文件类型",
                type="select",
                default="pdf",
                options=[
                    {"value": "pdf", "label": "PDF文档"},
                    {"value": "excel", "label": "Excel表格"},
                    {"value": "csv", "label": "CSV文件"}
                ]
            ),
            ConfigField(
                name="auto_categorize",
                label="自动分类",
                type="checkbox",
                default=True,
                help_text="根据产品名称自动分配类别"
            )
        ]
    
    def process_uploaded_file(self, file_path: str, config: Dict[str, Any]) -> List[PartData]:
        """处理上传的文件"""
        
        # 1. 上传文件
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{self.api_base}/admin/files/upload",
                headers={"Authorization": f"Bearer {self.admin_token}"},
                files=files
            )
        
        if response.status_code != 200:
            raise Exception(f"文件上传失败: {response.text}")
        
        upload_result = response.json()
        file_id = upload_result['file_id']
        
        try:
            # 2. 下载并解析文件
            download_response = requests.get(
                f"{self.api_base}/admin/files/{file_id}/download",
                headers={"Authorization": f"Bearer {self.admin_token}"}
            )
            
            if download_response.status_code != 200:
                raise Exception(f"文件下载失败: {download_response.text}")
            
            # 3. 根据文件类型解析内容
            file_type = config.get("file_type", "pdf")
            if file_type == "csv":
                parts_data = self.parse_csv(download_response.content)
            elif file_type == "excel":
                parts_data = self.parse_excel(download_response.content)
            elif file_type == "pdf":
                parts_data = self.parse_pdf(download_response.content)
            else:
                raise Exception(f"不支持的文件类型: {file_type}")
            
            # 4. 批量创建零件
            if parts_data:
                create_response = requests.post(
                    f"{self.api_base}/admin/files/parts/batch-create",
                    headers={
                        "Authorization": f"Bearer {self.admin_token}",
                        "Content-Type": "application/json"
                    },
                    json={"parts": [part.dict() for part in parts_data]}
                )
                
                if create_response.status_code == 200:
                    result = create_response.json()
                    print(f"批量创建完成: 成功{result['successful_creates']}个")
                    return parts_data
                else:
                    raise Exception(f"批量创建失败: {create_response.text}")
            
        finally:
            # 5. 清理临时文件
            requests.delete(
                f"{self.api_base}/admin/files/{file_id}",
                headers={"Authorization": f"Bearer {self.admin_token}"}
            )
        
        return []
    
    def parse_csv(self, content: bytes) -> List[PartData]:
        """解析CSV文件"""
        parts = []
        csv_text = content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(csv_text))
        
        for row in reader:
            if row.get('name'):  # 确保有名称
                properties = {}
                # 提取除基础字段外的所有字段作为属性
                for key, value in row.items():
                    if key not in ['name', 'category', 'description', 'price'] and value:
                        properties[key] = value
                
                part = PartData(
                    name=row['name'],
                    category=row.get('category'),
                    description=row.get('description'),
                    properties=properties if properties else None,
                    price=float(row['price']) if row.get('price') else None
                )
                parts.append(part)
        
        return parts
    
    def parse_excel(self, content: bytes) -> List[PartData]:
        """解析Excel文件 - 需要pandas或openpyxl库"""
        # 注意：由于安全限制，实际插件中需要使用允许的库
        # 这里提供伪代码示例
        parts = []
        
        # 伪代码 - 实际实现需要根据可用库调整
        # workbook = load_excel(content)
        # for row in workbook.active.iter_rows(values_only=True):
        #     if row[0]:  # 有名称
        #         parts.append(PartData(name=str(row[0]), ...))
        
        return parts
    
    def parse_pdf(self, content: bytes) -> List[PartData]:
        """解析PDF文件 - 需要PDF处理库"""
        parts = []
        
        # 伪代码 - PDF解析通常比较复杂
        # 可能需要使用OCR技术或特定的PDF解析库
        # text = extract_text_from_pdf(content)
        # parts = extract_parts_from_text(text)
        
        return parts
    
    def crawl(self, config: Dict[str, Any], **kwargs) -> CrawlResult:
        """此插件通过文件处理而不是网络爬取获取数据"""
        # 文档处理插件通常通过上传文件接口工作
        # 而不是传统的网络爬取
        return CrawlResult(
            success=True,
            data=[],
            total_count=0,
            warnings=["此插件需要通过文件上传接口使用"]
        )

# 必需：创建插件实例
plugin = DocumentProcessorPlugin()
```

### 5. 使用场景示例

#### 场景1：处理供应商价格表
```python
# 供应商每月发送Excel价格表
def process_supplier_pricelist(self, excel_file_path: str):
    parts = self.process_uploaded_file(excel_file_path, {
        "file_type": "excel",
        "auto_categorize": True
    })
    return parts
```

#### 场景2：解析PDF产品目录
```python
# 处理PDF格式的产品目录
def process_product_catalog(self, pdf_file_path: str):
    parts = self.process_uploaded_file(pdf_file_path, {
        "file_type": "pdf",
        "auto_categorize": False
    })
    return parts
```

#### 场景3：批量导入CSV数据
```python
# 处理标准化的CSV数据
def import_csv_data(self, csv_file_path: str):
    parts = self.process_uploaded_file(csv_file_path, {
        "file_type": "csv"
    })
    return parts
```

### 6. 获取文件统计接口

```http
GET /api/admin/files/stats
Authorization: Bearer {admin_token}
```

**响应格式：**
```json
{
    "total_files": 3,
    "total_size": 15728640,
    "total_size_mb": 15.0,
    "files": [
        {
            "filename": "abc123_1640995200.pdf",
            "size": 2048576,
            "created_at": "2024-01-01T12:00:00",
            "modified_at": "2024-01-01T12:00:00"
        }
    ]
}
```

---

## 完整示例

### 高级电商插件示例（包含图片下载）

```python
# advanced_ecommerce_plugin.py
"""
高级电商爬虫插件示例

展示完整的插件开发最佳实践，包含图片下载功能
"""

import time
import requests
import json
import re
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
from app.plugins.crawler_base import (
    BaseCrawlerPlugin, PluginInfo, ConfigField,
    CrawlResult, TestResult, PartData, DataSourceType
)

class AdvancedEcommercePlugin(BaseCrawlerPlugin):
    """高级电商爬虫插件"""
    
    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OpenPart-Crawler/1.0'
        })
        self.api_base = "http://localhost:8000/api"
        self.admin_token = None  # 由系统注入
    
    @property
    def plugin_info(self) -> PluginInfo:
        return PluginInfo(
            name="高级电商爬虫",
            version="2.1.0",
            description="功能完整的电商网站零件数据爬虫，支持图片下载和高级配置",
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
            
            # 图片下载配置
            ConfigField(
                name="download_images",
                label="下载产品图片",
                type="checkbox",
                default=True,
                help_text="启用后会自动下载产品图片到本地服务器"
            ),
            
            ConfigField(
                name="image_quality",
                label="图片质量",
                type="select",
                default="medium",
                options=[
                    {"value": "high", "label": "高质量（原始尺寸）"},
                    {"value": "medium", "label": "中等质量（800x600）"},
                    {"value": "low", "label": "低质量（400x300）"}
                ],
                help_text="选择下载图片的质量等级"
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
            
            # 性能配置
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
        if not config.get("api_base_url"):
            raise ValueError("API基础地址不能为空")
        
        # 验证URL格式
        try:
            result = urlparse(config["api_base_url"])
            if not all([result.scheme, result.netloc]):
                raise ValueError("API基础地址格式不正确")
        except Exception:
            raise ValueError("API基础地址格式不正确")
        
        return True
    
    def test_connection(self, config: Dict[str, Any]) -> TestResult:
        """测试数据源连接"""
        start_time = time.time()
        
        try:
            api_url = config["api_base_url"]
            headers = self._build_headers(config)
            
            # 尝试连接健康检查端点
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
            else:
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
            api_url = config["api_base_url"]
            headers = self._build_headers(config)
            search_categories = config.get("search_categories", ["electronic"])
            download_images = config.get("download_images", False)
            
            # 分页参数
            page_token = kwargs.get("page_token", "1")
            limit = kwargs.get("limit", config.get("batch_size", 50))
            
            # 爬取每个类别
            for category in search_categories:
                try:
                    category_parts = self._crawl_category(
                        api_url, headers, category, page_token, 
                        limit // len(search_categories)
                    )
                    
                    # 处理图片下载
                    if download_images:
                        category_parts = self._process_images(category_parts, warnings)
                    
                    crawled_parts.extend(category_parts)
                    
                    # 请求延迟
                    delay = config.get("request_delay", 1.0)
                    time.sleep(delay)
                    
                except Exception as e:
                    warnings.append(f"爬取类别 {category} 时出错: {str(e)}")
                    continue
            
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
        
        if config.get("api_key"):
            headers['Authorization'] = f'Bearer {config["api_key"]}'
        
        return headers
    
    def _crawl_category(self, api_url: str, headers: Dict, category: str,
                       page_token: str, limit: int) -> List[PartData]:
        """爬取指定类别的零件"""
        parts = []
        
        # 构建搜索URL
        search_url = urljoin(api_url, "/products/search")
        params = {
            'category': category,
            'page': page_token,
            'limit': limit
        }
        
        # 发送请求
        response = self.session.get(
            search_url,
            headers=headers,
            params=params,
            timeout=30
        )
        response.raise_for_status()
        
        # 解析响应
        data = response.json()
        products = data.get('products', [])
        
        # 处理每个产品
        for product in products:
            try:
                part = self._parse_product(product, category)
                if part:
                    parts.append(part)
            except Exception as e:
                continue
        
        return parts
    
    def _parse_product(self, product: Dict, category: str) -> Optional[PartData]:
        """解析产品数据为零件格式"""  
        try:
            name = product.get("name", "").strip()
            if not name:
                return None
            
            description = product.get("description", "").strip()
            
            # 价格处理
            price = None
            price_str = product.get("price")
            if price_str:
                try:
                    price = float(re.sub(r'[^\d.]', '', str(price_str)))
                except ValueError:
                    pass
            
            # 图片URL
            image_url = product.get("image_url")
            if image_url and not image_url.startswith('http'):
                image_url = urljoin(product.get("base_url", ""), image_url)
            
            # 自定义属性
            properties = {}
            specs = product.get("specifications", {})
            if isinstance(specs, dict):
                for key, value in specs.items():
                    if value:
                        properties[str(key)] = str(value)
            
            return PartData(
                name=name,
                category=self._normalize_category(category),
                description=description,
                properties=properties if properties else None,
                price=price,
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
    
    def _process_images(self, parts: List[PartData], warnings: List[str]) -> List[PartData]:
        """处理图片下载"""
        processed_parts = []
        
        for part in parts:
            if part.image_url:
                try:
                    # 首先需要创建零件记录以获取part_id
                    # 这里假设有一个临时创建方法
                    part_id = self._create_temp_part_record(part)
                    
                    # 调用图片下载API
                    local_image_url = self._download_part_image(part_id, part.image_url)
                    if local_image_url:
                        part.image_url = local_image_url
                    else:
                        warnings.append(f"图片下载失败: {part.name}")
                        
                except Exception as e:
                    warnings.append(f"处理图片时出错 {part.name}: {str(e)}")
            
            processed_parts.append(part)
        
        return processed_parts
    
    def _download_part_image(self, part_id: int, image_url: str) -> Optional[str]:
        """调用图片下载API"""
        try:
            response = requests.post(
                f"{self.api_base}/admin/images/download",
                headers={"Authorization": f"Bearer {self.admin_token}"},
                json={
                    "part_id": part_id,
                    "image_url": image_url,
                    "replace_existing": True
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("image_url")
            else:
                return None
                
        except Exception as e:
            return None
    
    def _create_temp_part_record(self, part: PartData) -> int:
        """创建临时零件记录（示例方法）"""
        # 这里需要根据实际API实现
        # 返回创建的零件ID
        return 1  # 示例返回
    
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
        self.api_base = "http://localhost:8000/api"
        self.admin_token = None
    
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

### 3. 图片处理最佳实践

```python
def _safe_download_image(self, part_id: int, image_url: str) -> Optional[str]:
    """安全的图片下载"""
    try:
        # 验证URL格式
        if not image_url or not image_url.startswith(('http://', 'https://')):
            return None
        
        # 调用系统图片下载API
        response = requests.post(
            f"{self.api_base}/admin/images/download",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json={
                "part_id": part_id,
                "image_url": image_url,
                "replace_existing": True
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return result.get("image_url")
        
        return None
        
    except Exception as e:
        # 记录错误但不中断主流程
        print(f"图片下载失败: {str(e)}")
        return None
```

### 4. 文件处理最佳实践

```python
def _safe_process_file(self, file_path: str, file_type: str) -> List[PartData]:
    """安全的文件处理"""
    file_id = None
    try:
        # 1. 上传文件
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{self.api_base}/admin/files/upload",
                headers={"Authorization": f"Bearer {self.admin_token}"},
                files=files
            )
        
        if response.status_code != 200:
            raise Exception(f"文件上传失败: {response.text}")
        
        upload_result = response.json()
        file_id = upload_result['file_id']
        
        # 2. 下载并解析
        download_response = requests.get(
            f"{self.api_base}/admin/files/{file_id}/download",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        if download_response.status_code == 200:
            return self._parse_file_content(download_response.content, file_type)
        else:
            raise Exception("文件下载失败")
            
    except Exception as e:
        print(f"文件处理失败: {str(e)}")
        return []
        
    finally:
        # 3. 清理临时文件
        if file_id:
            try:
                requests.delete(
                    f"{self.api_base}/admin/files/{file_id}",
                    headers={"Authorization": f"Bearer {self.admin_token}"}
                )
            except:
                pass  # 清理失败不影响主流程
```

### 5. 批量数据处理

```python
def _batch_create_parts(self, parts: List[PartData]) -> Dict[str, Any]:
    """批量创建零件"""
    try:
        # 转换为字典格式
        parts_data = []
        for part in parts[:1000]:  # 限制数量
            part_dict = {
                "name": part.name,
                "category": part.category,
                "description": part.description,
                "properties": part.properties,
                "image_url": part.image_url,
                "price": part.price
            }
            # 过滤None值
            part_dict = {k: v for k, v in part_dict.items() if v is not None}
            parts_data.append(part_dict)
        
        # 发送批量创建请求
        response = requests.post(
            f"{self.api_base}/admin/files/parts/batch-create",
            headers={
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            },
            json={"parts": parts_data}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"批量创建失败: {response.text}")
            
    except Exception as e:
        return {
            "success": False,
            "error_message": str(e),
            "total_processed": 0,
            "successful_creates": 0
        }
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
    "timeout": 30,
    "download_images": True
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

### 2. 图片下载测试

```python
def test_image_download():
    """测试图片下载功能"""
    test_urls = [
        "https://example.com/image1.jpg",
        "https://example.com/image2.png",
        "invalid-url",  # 测试错误处理
    ]
    
    for i, url in enumerate(test_urls):
        result = plugin._safe_download_image(part_id=i+1, image_url=url)
        print(f"图片 {i+1}: {'成功' if result else '失败'} - {url}")
```

### 3. 文件处理测试

```python
def test_file_processing():
    """测试文件处理功能"""
    test_files = [
        ("test_data.csv", "csv"),
        ("product_catalog.pdf", "pdf"),
        ("price_list.xlsx", "excel")
    ]
    
    for file_path, file_type in test_files:
        if os.path.exists(file_path):
            parts = plugin._safe_process_file(file_path, file_type)
            print(f"文件 {file_path}: 解析出 {len(parts)} 个零件")
```

---

## 常见问题

### Q: 如何在插件中使用图片下载功能？

**A:** 使用系统提供的图片下载API：

```python
def download_product_image(self, part_id: int, image_url: str) -> Optional[str]:
    """下载产品图片到本地"""
    try:
        response = requests.post(
            f"{self.api_base}/admin/images/download",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json={
                "part_id": part_id,
                "image_url": image_url,
                "replace_existing": True
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("image_url")  # 返回本地图片URL
        else:
            return None
    except Exception:
        return None
```

### Q: 如何处理PDF或Excel文件？

**A:** 使用文件上传和批量处理API：

```python
def process_document(self, file_path: str) -> List[PartData]:
    """处理文档文件"""
    # 1. 上传文件
    with open(file_path, 'rb') as f:
        upload_response = requests.post(
            f"{self.api_base}/admin/files/upload",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            files={'file': f}
        )
    
    if upload_response.status_code != 200:
        return []
    
    file_id = upload_response.json()['file_id']
    
    try:
        # 2. 下载并解析
        download_response = requests.get(
            f"{self.api_base}/admin/files/{file_id}/download",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        # 3. 解析内容（根据文件类型）
        parts_data = self.parse_file_content(download_response.content)
        
        # 4. 批量创建零件
        if parts_data:
            batch_response = requests.post(
                f"{self.api_base}/admin/files/parts/batch-create",
                headers={
                    "Authorization": f"Bearer {self.admin_token}",
                    "Content-Type": "application/json"
                },
                json={"parts": [part.dict() for part in parts_data]}
            )
            
            if batch_response.status_code == 200:
                result = batch_response.json()
                print(f"成功创建 {result['successful_creates']} 个零件")
        
        return parts_data
        
    finally:
        # 5. 清理临时文件
        requests.delete(
            f"{self.api_base}/admin/files/{file_id}",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
```

### Q: 如何处理大量数据而不超出内存限制？

**A:** 采用分批处理策略：

```python
def crawl_large_dataset(self, config: Dict[str, Any]) -> CrawlResult:
    """处理大量数据"""
    all_parts = []
    batch_size = 100
    page = 1
    
    while True:
        # 分页获取数据
        batch_parts = self.fetch_page_data(config, page, batch_size)
        
        if not batch_parts:
            break
            
        # 立即处理图片下载
        if config.get("download_images"):
            batch_parts = self.process_batch_images(batch_parts)
        
        # 立即批量创建零件
        self.batch_create_parts(batch_parts)
        
        all_parts.extend(batch_parts)
        page += 1
        
        # 内存控制：限制总数量
        if len(all_parts) >= 1000:
            break
        
        time.sleep(1)  # 避免过快请求
    
    return CrawlResult(success=True, data=all_parts, total_count=len(all_parts))
```

### Q: 如何处理网站反爬虫机制？

**A:** 使用以下策略：

```python
class AntiCrawlerPlugin(BaseCrawlerPlugin):
    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        # 设置真实浏览器User-Agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def crawl_with_protection(self, config: Dict[str, Any]) -> CrawlResult:
        """带反爬保护的爬取"""
        parts = []
        
        for url in self.get_target_urls(config):
            try:
                # 随机延迟
                delay = random.uniform(1, 3)
                time.sleep(delay)
                
                # 使用会话保持Cookie
                response = self.session.get(url, timeout=30)
                
                # 检测反爬虫响应
                if self.is_blocked_response(response):
                    # 等待更长时间后重试
                    time.sleep(10)
                    response = self.session.get(url, timeout=30)
                
                # 解析数据
                page_parts = self.parse_page(response)
                parts.extend(page_parts)
                
            except Exception as e:
                continue
        
        return CrawlResult(success=True, data=parts, total_count=len(parts))
    
    def is_blocked_response(self, response) -> bool:
        """检测是否被反爬虫拦截"""
        # 检查状态码
        if response.status_code in [403, 429, 503]:
            return True
        
        # 检查页面内容
        content = response.text.lower()
        block_indicators = ['captcha', 'blocked', 'forbidden', '验证码']
        return any(indicator in content for indicator in block_indicators)
```

### Q: 如何优化插件性能？

**A:** 以下是性能优化建议：

```python
class OptimizedPlugin(BaseCrawlerPlugin):
    def __init__(self):
        super().__init__()
        # 使用连接池
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=3
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # 缓存机制
        self.cache = {}
    
    def crawl_optimized(self, config: Dict[str, Any]) -> CrawlResult:
        """优化的爬取方法"""
        parts = []
        
        # 1. 批量获取URL列表
        urls = self.get_all_urls(config)
        
        # 2. 分批处理
        batch_size = 20
        for i in range(0, len(urls), batch_size):
            batch_urls = urls[i:i + batch_size]
            batch_parts = self.process_url_batch(batch_urls)
            parts.extend(batch_parts)
            
            # 批量处理图片
            if config.get("download_images"):
                self.batch_process_images(batch_parts)
            
            # 进度报告
            progress = (i + batch_size) / len(urls) * 100
            print(f"进度: {progress:.1f}%")
        
        return CrawlResult(success=True, data=parts, total_count=len(parts))
    
    def process_url_batch(self, urls: List[str]) -> List[PartData]:
        """批量处理URL"""
        parts = []
        
        for url in urls:
            # 检查缓存
            if url in self.cache:
                parts.append(self.cache[url])
                continue
            
            try:
                response = self.session.get(url, timeout=10)
                part = self.parse_product_page(response)
                if part:
                    self.cache[url] = part  # 缓存结果
                    parts.append(part)
            except Exception:
                continue
        
        return parts
```

### Q: 如何处理插件配置验证？

**A:** 实现全面的配置验证：

```python
def validate_config(self, config: Dict[str, Any]) -> bool:
    """全面的配置验证"""
    
    # 1. 必需字段检查
    required_fields = ["api_url", "timeout"]
    for field in required_fields:
        if not config.get(field):
            raise ValueError(f"{field} 不能为空")
    
    # 2. 类型检查
    if not isinstance(config.get("timeout"), (int, float)):
        raise ValueError("timeout 必须是数字")
    
    # 3. 范围检查
    timeout = config["timeout"]
    if timeout < 1 or timeout > 300:
        raise ValueError("timeout 必须在 1-300 秒之间")
    
    # 4. URL格式验证
    api_url = config["api_url"]
    try:
        result = urlparse(api_url)
        if not all([result.scheme, result.netloc]):
            raise ValueError("API地址格式不正确")
    except Exception:
        raise ValueError("API地址格式不正确")
    
    # 5. JSON配置验证
    json_fields = ["custom_headers", "advanced_settings"]
    for field in json_fields:
        if field in config and config[field]:
            try:
                json.loads(config[field])
            except json.JSONDecodeError:
                raise ValueError(f"{field} 必须是有效的JSON格式")
    
    # 6. 枚举值验证
    if "image_quality" in config:
        valid_qualities = ["low", "medium", "high"]
        if config["image_quality"] not in valid_qualities:
            raise ValueError(f"image_quality 必须是: {', '.join(valid_qualities)}")
    
    return True
```

### Q: 如何处理插件的错误和异常？

**A:** 建立完善的错误处理机制：

```python
class RobustPlugin(BaseCrawlerPlugin):
    def __init__(self):
        super().__init__()
        self.error_count = 0
        self.max_errors = 10
    
    def crawl(self, config: Dict[str, Any], **kwargs) -> CrawlResult:
        """健壮的爬取方法"""
        parts = []
        warnings = []
        
        try:
            urls = self.get_target_urls(config)
            
            for i, url in enumerate(urls):
                try:
                    part = self.crawl_single_url(url, config)
                    if part:
                        parts.append(part)
                    
                    # 重置错误计数
                    self.error_count = 0
                    
                except requests.RequestException as e:
                    # 网络错误
                    self.error_count += 1
                    warning = f"网络错误 {url}: {str(e)}"
                    warnings.append(warning)
                    
                    if self.error_count >= self.max_errors:
                        return CrawlResult(
                            success=False,
                            data=parts,
                            total_count=len(parts),
                            error_message=f"连续网络错误过多，已停止爬取",
                            warnings=warnings
                        )
                    
                    # 网络错误时等待更长时间
                    time.sleep(5)
                    
                except json.JSONDecodeError as e:
                    # 数据解析错误
                    warnings.append(f"数据解析错误 {url}: {str(e)}")
                    continue
                    
                except Exception as e:
                    # 其他未预期错误
                    warnings.append(f"未知错误 {url}: {str(e)}")
                    continue
            
            return CrawlResult(
                success=True,
                data=parts,
                total_count=len(parts),
                warnings=warnings
            )
            
        except Exception as e:
            # 全局错误
            return CrawlResult(
                success=False,
                data=parts,
                total_count=len(parts),
                error_message=f"爬取过程发生严重错误: {str(e)}",
                warnings=warnings
            )
    
    def crawl_single_url(self, url: str, config: Dict[str, Any]) -> Optional[PartData]:
        """爬取单个URL的数据"""
        response = requests.get(url, timeout=config.get("timeout", 30))
        response.raise_for_status()  # 抛出HTTP错误
        
        data = response.json()  # 可能抛出JSON解析错误
        
        return self.parse_product_data(data)  # 可能抛出数据处理错误
```

### Q: 插件如何处理认证和会话管理？

**A:** 实现安全的认证机制：

```python
class AuthenticatedPlugin(BaseCrawlerPlugin):
    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.access_token = None
        self.token_expires_at = None
    
    def authenticate(self, config: Dict[str, Any]) -> bool:
        """处理认证"""
        try:
            auth_url = urljoin(config["api_base_url"], "/auth/login")
            
            auth_data = {
                "username": config.get("username"),
                "password": config.get("password"),
                "api_key": config.get("api_key")
            }
            
            response = self.session.post(auth_url, json=auth_data)
            response.raise_for_status()
            
            auth_result = response.json()
            self.access_token = auth_result.get("access_token")
            
            # 计算token过期时间
            expires_in = auth_result.get("expires_in", 3600)
            self.token_expires_at = time.time() + expires_in
            
            # 设置认证头
            self.session.headers["Authorization"] = f"Bearer {self.access_token}"
            
            return True
            
        except Exception as e:
            print(f"认证失败: {str(e)}")
            return False
    
    def is_token_valid(self) -> bool:
        """检查token是否有效"""
        if not self.access_token or not self.token_expires_at:
            return False
        
        # 提前5分钟刷新token
        return time.time() < (self.token_expires_at - 300)
    
    def ensure_authenticated(self, config: Dict[str, Any]) -> bool:
        """确保已认证"""
        if not self.is_token_valid():
            return self.authenticate(config)
        return True
    
    def crawl(self, config: Dict[str, Any], **kwargs) -> CrawlResult:
        """带认证的爬取"""
        # 确保已认证
        if not self.ensure_authenticated(config):
            return CrawlResult(
                success=False,
                data=[],
                total_count=0,
                error_message="认证失败，无法继续爬取"
            )
        
        # 进行正常爬取
        return super().crawl(config, **kwargs)
```

---

## 总结

OpenPart 插件系统为开发者提供了一个功能强大、安全可靠的数据采集平台。通过本指南，你现在可以：

### 🚀 核心能力
- **快速开发**：使用标准化的插件框架
- **安全运行**：在沙箱环境中安全执行
- **灵活配置**：通过可视化界面进行配置
- **实时监控**：完整的任务执行和日志系统

### 🎯 新增特性
- **图片下载**：安全地将远程图片下载到本地服务器
- **文件处理**：支持PDF、Excel等文档的解析和批量数据导入
- **批量操作**：高效的批量数据创建和管理

### 🛡️ 安全保障
- **代码审查**：AST静态分析防止恶意代码
- **网络安全**：URL白名单和安全检查
- **文件安全**：严格的文件类型和大小限制
- **权限控制**：基于角色的访问控制

### 📈 最佳实践建议
1. **遵循规范**：严格按照插件接口规范开发
2. **错误处理**：实现完善的异常处理机制
3. **性能优化**：合理使用缓存和批量处理
4. **资源管理**：及时清理临时文件和网络连接
5. **安全编码**：避免使用禁用的模块和函数

### 🔧 开发工具
- **配置系统**：支持多种字段类型的动态配置
- **测试接口**：内置的连接测试和调试功能
- **API集成**：完整的RESTful API支持
- **前端界面**：开箱即用的管理界面

记住始终遵守目标网站的robots.txt和服务条款，合理控制请求频率，尊重数据源的使用限制，做一个负责任的数据采集开发者。

---

**开发愉快！** 🎉

*如有问题，请查看系统日志、使用调试接口，或联系技术支持团队。*

### 📚 相关资源

- **API文档**：`/docs` - 完整的API接口文档
- **示例代码**：参考本文档中的完整示例
- **错误排查**：查看插件管理界面的详细错误信息
- **性能监控**：使用任务管理界面跟踪执行状态

### 🆕 版本更新

- **v2.1.0**：新增图片下载和文件处理功能
- **v2.0.0**：插件系统重构，增强安全性
- **v1.x**：基础爬虫插件系统