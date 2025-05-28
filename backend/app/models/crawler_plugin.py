# backend/app/models/crawler_plugin.py - 修复版本
"""
爬虫插件相关的数据模型
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class PluginStatus(enum.Enum):
    """插件状态枚举"""
    ACTIVE = "active"           # 活跃
    INACTIVE = "inactive"       # 未激活
    ERROR = "error"            # 错误状态
    DISABLED = "disabled"       # 已禁用

class TaskStatus(enum.Enum):
    """任务状态枚举"""
    PENDING = "pending"         # 等待执行
    RUNNING = "running"         # 执行中
    COMPLETED = "completed"     # 已完成
    FAILED = "failed"          # 失败
    STOPPED = "stopped"        # 已停止

class ScheduleType(enum.Enum):
    """调度类型枚举"""
    MANUAL = "manual"          # 手动执行
    CRON = "cron"             # 定时执行
    INTERVAL = "interval"      # 间隔执行

class CrawlerPlugin(Base):
    """爬虫插件模型"""
    __tablename__ = "crawler_plugins"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)  # 插件标识名
    display_name = Column(String(200), nullable=False)  # 显示名称
    version = Column(String(50), nullable=False)  # 版本号
    description = Column(Text)  # 描述信息
    author = Column(String(100))  # 开发者
    data_source = Column(String(200))  # 数据源名称
    
    # 文件信息
    file_path = Column(String(500), nullable=False)  # 插件文件路径
    
    # 状态信息
    status = Column(String(20), default='inactive')  # 状态：active, inactive, error
    is_active = Column(Boolean, default=False)  # 是否启用
    
    # 配置信息
    config = Column(JSON)  # 插件配置
    
    # 统计信息
    run_count = Column(Integer, default=0)  # 运行次数
    success_count = Column(Integer, default=0)  # 成功次数
    error_count = Column(Integer, default=0)  # 错误次数
    last_run_at = Column(DateTime(timezone=True))  # 最后运行时间
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    tasks = relationship("CrawlerTask", back_populates="plugin", cascade="all, delete-orphan")

class CrawlerTask(Base):
    """爬虫任务模型 - 修复版本"""
    __tablename__ = "crawler_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    plugin_id = Column(Integer, ForeignKey("crawler_plugins.id"), nullable=False)
    
    # 任务信息
    name = Column(String(200), nullable=False)  # 任务名称
    description = Column(Text)  # 任务描述
    
    # 配置信息
    config = Column(JSON)  # 任务配置
    schedule_type = Column(String(20), default='manual')  # 修复：添加调度类型字段
    schedule_config = Column(JSON)  # 修复：添加调度配置字段
    
    # 状态信息
    status = Column(String(20), default='pending')  # pending, running, completed, failed, stopped
    
    # 执行信息
    run_count = Column(Integer, default=0)  # 执行次数
    started_at = Column(DateTime(timezone=True))  # 开始时间
    finished_at = Column(DateTime(timezone=True))  # 结束时间
    execution_time = Column(Float)  # 执行时间(秒)
    
    # 结果统计
    data_count = Column(Integer, default=0)  # 总数据数量
    success_count = Column(Integer, default=0)  # 成功处理数量
    error_count = Column(Integer, default=0)  # 错误数量
    
    # 日志信息
    logs = Column(JSON)  # 执行日志
    error_message = Column(Text)  # 错误信息
    
    # 创建信息 - 修复：添加缺失字段
    created_by = Column(Integer, ForeignKey("users.id"))  # 创建者ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    plugin = relationship("CrawlerPlugin", back_populates="tasks")

# ==================== Schema定义 ====================

# backend/app/schemas/crawler_plugin.py
"""
爬虫插件相关的Pydantic Schema
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.crawler_plugin import PluginStatus, TaskStatus, ScheduleType

class PluginBase(BaseModel):
    """插件基础Schema"""
    name: str
    display_name: str
    version: str
    description: Optional[str] = None
    author: Optional[str] = None
    data_source: Optional[str] = None

class PluginCreate(PluginBase):
    """创建插件Schema"""
    file_path: str
    config: Optional[Dict[str, Any]] = None

class PluginUpdate(BaseModel):
    """更新插件Schema"""
    display_name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class PluginConfigRequest(BaseModel):
    """插件配置请求Schema"""
    config: Dict[str, Any]

class PluginTestRequest(BaseModel):
    """插件测试请求Schema"""
    config: Optional[Dict[str, Any]] = None

class ConfigFieldSchema(BaseModel):
    """配置字段Schema"""
    name: str
    label: str
    type: str
    required: bool = False
    default: Any = None
    placeholder: Optional[str] = None
    options: Optional[List[Dict[str, str]]] = None
    help_text: Optional[str] = None
    validation: Optional[Dict[str, Any]] = None

class PluginResponse(PluginBase):
    """插件响应Schema"""
    id: int
    status: PluginStatus
    is_active: bool
    config: Optional[Dict[str, Any]] = None
    config_schema: Optional[List[ConfigFieldSchema]] = None
    allowed_domains: Optional[List[str]] = None
    required_permissions: Optional[List[str]] = None
    run_count: int = 0
    success_count: int = 0
    error_count: int = 0
    last_run_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    """任务基础Schema"""
    name: str
    description: Optional[str] = None
    schedule_type: ScheduleType = ScheduleType.MANUAL
    schedule_config: Optional[Dict[str, Any]] = None

class TaskCreate(TaskBase):
    """创建任务Schema"""
    plugin_id: int
    config: Optional[Dict[str, Any]] = None

class TaskCreateRequest(TaskBase):
    """任务创建请求Schema"""
    config: Optional[Dict[str, Any]] = None

class TaskUpdate(BaseModel):
    """更新任务Schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    schedule_config: Optional[Dict[str, Any]] = None

class TaskExecuteRequest(BaseModel):
    """任务执行请求Schema"""
    config: Optional[Dict[str, Any]] = None

class TaskResponse(TaskBase):
    """任务响应Schema"""
    id: int
    plugin_id: int
    status: TaskStatus
    run_count: int = 0
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    execution_time: Optional[float] = None
    data_count: int = 0
    success_count: int = 0
    error_count: int = 0
    logs: Optional[List[str]] = None
    error_message: Optional[str] = None
    last_page_token: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TaskStatsResponse(BaseModel):
    """任务统计响应Schema"""
    total_tasks: int
    pending_tasks: int
    running_tasks: int
    completed_tasks: int
    failed_tasks: int

class PluginStatsResponse(BaseModel):
    """插件统计响应Schema"""
    total_plugins: int
    active_plugins: int
    inactive_plugins: int
    error_plugins: int

class CrawlResultResponse(BaseModel):
    """爬取结果响应Schema"""
    success: bool
    data_count: int
    execution_time: float
    error_message: Optional[str] = None
    warnings: Optional[List[str]] = None

class TestResultResponse(BaseModel):
    """测试结果响应Schema"""
    success: bool
    message: str
    response_time: Optional[float] = None
    sample_data: Optional[Dict[str, Any]] = None