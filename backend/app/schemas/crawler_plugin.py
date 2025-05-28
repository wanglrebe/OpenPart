# backend/app/schemas/crawler_plugin.py
"""
爬虫插件相关的Pydantic Schema
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class PluginStatus(str, Enum):
    """插件状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    DISABLED = "disabled"

class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"

class ScheduleType(str, Enum):
    """调度类型枚举"""
    MANUAL = "manual"
    CRON = "cron"
    INTERVAL = "interval"

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