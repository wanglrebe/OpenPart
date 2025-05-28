# backend/app/plugins/crawler_base.py
"""
OpenPart 爬虫插件基础规范

这个文件定义了所有爬虫插件必须遵循的接口标准
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class PluginStatus(Enum):
    """插件状态枚举"""
    ACTIVE = "active"           # 活跃
    INACTIVE = "inactive"       # 未激活
    ERROR = "error"            # 错误状态
    DISABLED = "disabled"       # 已禁用

class DataSourceType(Enum):
    """数据源类型枚举"""
    ECOMMERCE = "ecommerce"     # 电商平台
    SUPPLIER = "supplier"       # 供应商网站
    DATABASE = "database"       # 数据库
    API = "api"                # API接口
    CATALOG = "catalog"        # 产品目录
    OTHER = "other"            # 其他

class PartData(BaseModel):
    """爬取的零件数据标准格式"""
    name: str = Field(..., description="零件名称，必填")
    category: Optional[str] = Field(None, description="零件类别")
    description: Optional[str] = Field(None, description="零件描述")
    properties: Optional[Dict[str, Any]] = Field(None, description="自定义属性")
    image_url: Optional[str] = Field(None, description="图片URL")
    source_url: Optional[str] = Field(None, description="原始数据URL")
    external_id: Optional[str] = Field(None, description="外部系统ID")
    price: Optional[float] = Field(None, description="价格信息")
    availability: Optional[str] = Field(None, description="库存状态")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ConfigField(BaseModel):
    """配置字段定义"""
    name: str = Field(..., description="字段名称")
    label: str = Field(..., description="显示标签")
    type: str = Field(..., description="字段类型: text|password|number|select|checkbox|textarea")
    required: bool = Field(False, description="是否必填")
    default: Any = Field(None, description="默认值")
    placeholder: Optional[str] = Field(None, description="占位符文本")
    options: Optional[List[Dict[str, str]]] = Field(None, description="选择项(select类型使用)")
    help_text: Optional[str] = Field(None, description="帮助说明")
    validation: Optional[Dict[str, Any]] = Field(None, description="验证规则")

class PluginInfo(BaseModel):
    """插件信息"""
    name: str = Field(..., description="插件名称")
    version: str = Field(..., description="版本号")
    description: str = Field(..., description="插件描述")
    author: str = Field(..., description="作者")
    data_source: str = Field(..., description="数据源名称")
    data_source_type: DataSourceType = Field(..., description="数据源类型")
    homepage: Optional[str] = Field(None, description="数据源主页")
    terms_url: Optional[str] = Field(None, description="服务条款URL")
    rate_limit: Optional[int] = Field(None, description="请求频率限制(秒)")
    batch_size: Optional[int] = Field(50, description="批次处理大小")

class CrawlResult(BaseModel):
    """爬取结果"""
    success: bool = Field(..., description="是否成功")
    data: List[PartData] = Field(default_factory=list, description="爬取的数据")
    total_count: int = Field(0, description="总数据量")
    error_message: Optional[str] = Field(None, description="错误信息")
    warnings: List[str] = Field(default_factory=list, description="警告信息")
    execution_time: Optional[float] = Field(None, description="执行时间(秒)")
    next_page_token: Optional[str] = Field(None, description="下一页标识")

class TestResult(BaseModel):
    """测试结果"""
    success: bool = Field(..., description="测试是否成功")
    message: str = Field(..., description="测试结果信息")
    response_time: Optional[float] = Field(None, description="响应时间(秒)")
    sample_data: Optional[Dict[str, Any]] = Field(None, description="示例数据")

class BaseCrawlerPlugin(ABC):
    """
    爬虫插件基类
    
    所有爬虫插件都必须继承此类并实现所有抽象方法
    """
    
    def __init__(self):
        """初始化插件"""
        self._validate_plugin_info()
    
    @property
    @abstractmethod
    def plugin_info(self) -> PluginInfo:
        """
        返回插件基本信息
        
        Returns:
            PluginInfo: 插件信息对象
        """
        pass
    
    @property
    @abstractmethod
    def config_schema(self) -> List[ConfigField]:
        """
        返回插件配置表单定义
        
        Returns:
            List[ConfigField]: 配置字段列表
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证配置参数是否有效
        
        Args:
            config: 配置参数字典
            
        Returns:
            bool: 配置是否有效
            
        Raises:
            ValueError: 配置无效时抛出异常，异常信息会显示给用户
        """
        pass
    
    @abstractmethod
    def test_connection(self, config: Dict[str, Any]) -> TestResult:
        """
        测试与数据源的连接
        
        Args:
            config: 配置参数字典
            
        Returns:
            TestResult: 测试结果
        """
        pass
    
    @abstractmethod
    def crawl(self, config: Dict[str, Any], **kwargs) -> CrawlResult:
        """
        执行数据爬取
        
        Args:
            config: 配置参数字典
            **kwargs: 额外参数，可能包含:
                - page_token: 分页标识
                - limit: 数据限制数量
                - filters: 过滤条件
                
        Returns:
            CrawlResult: 爬取结果
        """
        pass
    
    def get_allowed_domains(self) -> List[str]:
        """
        返回插件允许访问的域名列表
        
        Returns:
            List[str]: 允许访问的域名列表
        """
        return []
    
    def get_required_permissions(self) -> List[str]:
        """
        返回插件需要的权限列表
        
        Returns:
            List[str]: 权限列表，可选值:
                - network: 网络访问
                - file_read: 文件读取
                - file_write: 文件写入
        """
        return ["network"]
    
    def cleanup(self):
        """
        插件卸载时的清理工作
        
        在插件被卸载或禁用时调用，用于释放资源
        """
        pass
    
    def _validate_plugin_info(self):
        """验证插件信息"""
        try:
            info = self.plugin_info
            if not info.name or not info.version:
                raise ValueError("插件名称和版本不能为空")
        except Exception as e:
            raise ValueError(f"插件信息验证失败: {e}")

# 安全装饰器
def safe_network_call(allowed_domains: List[str] = None):
    """
    网络调用安全装饰器
    
    Args:
        allowed_domains: 允许访问的域名列表
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 这里会在实际执行时添加网络访问检查
            return func(*args, **kwargs)
        return wrapper
    return decorator

# 工具类
class PluginUtils:
    """插件开发工具类"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """清理文本内容"""
        if not text:
            return ""
        return text.strip().replace('\n', ' ').replace('\r', '')
    
    @staticmethod
    def extract_number(text: str) -> Optional[float]:
        """从文本中提取数字"""
        import re
        if not text:
            return None
        
        # 提取数字
        numbers = re.findall(r'\d+\.?\d*', str(text))
        if numbers:
            try:
                return float(numbers[0])
            except ValueError:
                return None
        return None
    
    @staticmethod
    def normalize_url(url: str, base_url: str = None) -> str:
        """标准化URL"""
        from urllib.parse import urljoin, urlparse
        
        if not url:
            return ""
        
        # 如果是相对URL，转换为绝对URL
        if base_url and not urlparse(url).netloc:
            return urljoin(base_url, url)
        
        return url
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """验证URL格式"""
        from urllib.parse import urlparse
        
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

# 异常类定义
class PluginError(Exception):
    """插件基础异常"""
    pass

class ConfigError(PluginError):
    """配置错误"""
    pass

class NetworkError(PluginError):
    """网络错误"""
    pass

class DataError(PluginError):
    """数据错误"""
    pass

class SecurityError(PluginError):
    """安全错误"""
    pass