# backend/app/schemas/compatibility.py
"""
兼容性检查系统Pydantic Schema定义

定义API请求和响应的数据结构
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from enum import Enum

# ==================== 枚举定义 ====================

class CompatibilityStatus(str, Enum):
    """兼容性状态枚举"""
    COMPATIBLE = "compatible"
    INCOMPATIBLE = "incompatible"
    CONDITIONAL = "conditional"

class VerificationStatus(str, Enum):
    """验证状态枚举"""
    VERIFIED = "verified"
    PENDING = "pending"
    DISPUTED = "disputed"

class SourceType(str, Enum):
    """数据来源类型枚举"""
    ADMIN = "admin"
    OFFICIAL = "official"
    USER_CONTRIBUTION = "user_contribution"

class RiskLevel(str, Enum):
    """风险等级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class CompatibilityGrade(str, Enum):
    """兼容度等级"""
    OFFICIAL_SUPPORT = "official_support"      # 官方支持 (90-100分)
    UNOFFICIAL_SUPPORT = "unofficial_support"  # 非官方支持 (70-89分)
    THEORETICAL = "theoretical"                # 理论兼容 (50-69分)
    INCOMPATIBLE = "incompatible"             # 不兼容 (0-49分)

# ==================== 规则相关Schema ====================

class RuleBase(BaseModel):
    """规则基础Schema"""
    name: str = Field(..., min_length=1, max_length=200, description="规则名称")
    description: Optional[str] = Field(None, description="规则描述")
    rule_expression: str = Field(..., min_length=1, description="规则表达式")
    category_a: str = Field(..., min_length=1, max_length=100, description="零件类别A")
    category_b: str = Field(..., min_length=1, max_length=100, description="零件类别B")
    weight: int = Field(100, ge=0, le=1000, description="规则权重")
    is_blocking: bool = Field(False, description="是否为阻断性规则")

class RuleCreate(RuleBase):
    """创建规则Schema"""
    pass

class RuleUpdate(BaseModel):
    """更新规则Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    rule_expression: Optional[str] = Field(None, min_length=1)
    category_a: Optional[str] = Field(None, min_length=1, max_length=100)
    category_b: Optional[str] = Field(None, min_length=1, max_length=100)
    weight: Optional[int] = Field(None, ge=0, le=1000)
    is_blocking: Optional[bool] = None
    is_active: Optional[bool] = None

class RuleResponse(RuleBase):
    """规则响应Schema"""
    id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    
    class Config:
        from_attributes = True

class RuleTestRequest(BaseModel):
    """规则测试请求Schema"""
    expression: str = Field(..., description="要测试的表达式")
    test_data: Dict[str, Any] = Field(..., description="测试数据")

class RuleTestResponse(BaseModel):
    """规则测试响应Schema"""
    success: bool
    result: Optional[bool] = None
    execution_time: float
    error_message: Optional[str] = None
    security_check: Dict[str, Any]

class SecurityValidationRequest(BaseModel):
    """安全验证请求Schema"""
    expression: str = Field(..., description="要验证的表达式")

class SecurityValidationResponse(BaseModel):
    """安全验证响应Schema"""
    is_safe: bool
    security_issues: List[Dict[str, Any]] = Field(default_factory=list)
    risk_level: RiskLevel
    recommendations: List[str] = Field(default_factory=list)

# ==================== 经验相关Schema ====================

class ExperienceBase(BaseModel):
    """经验基础Schema"""
    part_a_id: int = Field(..., gt=0, description="零件A的ID")
    part_b_id: int = Field(..., gt=0, description="零件B的ID")
    compatibility_status: CompatibilityStatus = Field(..., description="兼容性状态")
    compatibility_score: Optional[int] = Field(None, ge=0, le=100, description="兼容性评分")
    notes: Optional[str] = Field(None, description="备注说明")
    reference_url: Optional[str] = Field(None, description="外部反馈来源链接")
    
    @validator('part_a_id', 'part_b_id')
    def validate_different_parts(cls, v, values):
        if 'part_a_id' in values and v == values['part_a_id']:
            raise ValueError('零件A和零件B不能是同一个')
        return v

class ExperienceCreate(ExperienceBase):
    """创建经验Schema"""
    source: SourceType = Field(SourceType.ADMIN, description="数据来源")
    verification_status: VerificationStatus = Field(VerificationStatus.VERIFIED, description="验证状态")

class ExperienceUpdate(BaseModel):
    """更新经验Schema"""
    compatibility_status: Optional[CompatibilityStatus] = None
    compatibility_score: Optional[int] = Field(None, ge=0, le=100)
    notes: Optional[str] = None
    reference_url: Optional[str] = None
    verification_status: Optional[VerificationStatus] = None

class ExperienceResponse(ExperienceBase):
    """经验响应Schema"""
    id: int
    source: SourceType
    verification_status: VerificationStatus
    added_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # 关联数据
    part_a_name: Optional[str] = None
    part_b_name: Optional[str] = None
    added_by_username: Optional[str] = None
    
    class Config:
        from_attributes = True

class ExperienceBatchCreateRequest(BaseModel):
    """批量创建经验请求Schema"""
    experiences: List[ExperienceCreate] = Field(..., min_items=1, max_items=100)
    
class ExperienceBatchCreateResponse(BaseModel):
    """批量创建经验响应Schema"""
    success: bool
    total_processed: int
    successful_creates: int
    skipped_duplicates: int
    errors: List[Dict[str, Any]] = Field(default_factory=list)

# ==================== 兼容性检查相关Schema ====================

class CompatibilityCheckRequest(BaseModel):
    """兼容性检查请求Schema"""
    part_ids: List[int] = Field(..., min_items=2, max_items=10, description="要检查的零件ID列表")
    include_cache: bool = Field(True, description="是否使用缓存")
    detail_level: str = Field("standard", description="详细程度: basic/standard/detailed")

class RuleResult(BaseModel):
    """规则执行结果Schema"""
    rule_id: int
    rule_name: str
    passed: bool
    score: float
    weight: int
    is_blocking: bool
    error_message: Optional[str] = None
    execution_time: Optional[float] = None

class PartCompatibilityResult(BaseModel):
    """零件对兼容性结果Schema"""
    part_a_id: int
    part_b_id: int
    part_a_name: str
    part_b_name: str
    compatibility_grade: CompatibilityGrade
    compatibility_score: int
    is_compatible: bool
    rule_results: List[RuleResult] = Field(default_factory=list)
    experience_data: Optional[Dict[str, Any]] = None  # 改为字典类型，可选
    warnings: List[str] = Field(default_factory=list)

class CompatibilityCheckResponse(BaseModel):
    """兼容性检查响应Schema"""
    success: bool
    overall_compatibility_grade: CompatibilityGrade
    overall_score: int
    is_overall_compatible: bool
    part_combinations: List[PartCompatibilityResult]
    execution_time: float
    cached: bool
    warnings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

# ==================== 兼容性搜索相关Schema ====================

class CompatibilitySearchRequest(BaseModel):
    """兼容性搜索请求Schema"""
    selected_parts: List[int] = Field(..., min_items=1, description="已选择的零件ID列表")
    target_categories: Optional[List[str]] = Field(None, description="目标零件类别")
    min_compatibility_score: int = Field(50, ge=0, le=100, description="最低兼容性评分")
    limit: int = Field(20, ge=1, le=100, description="返回结果数量限制")
    include_theoretical: bool = Field(True, description="是否包含理论兼容的零件")

class CompatibilityMatch(BaseModel):
    """兼容性匹配结果Schema"""
    part_id: int
    part_name: str
    part_category: str
    compatibility_grade: CompatibilityGrade
    compatibility_score: int
    matching_rules_count: int
    experience_based: bool
    confidence_level: float
    reasons: List[str] = Field(default_factory=list)

class CompatibilitySearchResponse(BaseModel):
    """兼容性搜索响应Schema"""
    success: bool
    matches: List[CompatibilityMatch]
    total_found: int
    search_criteria: Dict[str, Any]
    execution_time: float
    recommendations: List[str] = Field(default_factory=list)

# ==================== 模板相关Schema ====================

class TemplateBase(BaseModel):
    """模板基础Schema"""
    name: str = Field(..., min_length=1, max_length=200, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    categories: List[str] = Field(..., min_items=2, description="零件类别列表")
    rules: Dict[str, Any] = Field(..., description="规则配置")
    is_public: bool = Field(False, description="是否公开")

class TemplateCreate(TemplateBase):
    """创建模板Schema"""
    pass

class TemplateUpdate(BaseModel):
    """更新模板Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    categories: Optional[List[str]] = Field(None, min_items=2)
    rules: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None

class TemplateResponse(TemplateBase):
    """模板响应Schema"""
    id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ==================== 更新：审计日志Schema ====================

class AuditAction(str, Enum):
    """审计动作枚举 - 更新版本"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"      # 真正的删除
    DISABLE = "disable"    # 停用
    ENABLE = "enable"      # 启用
    TEST = "test"
    VALIDATE = "validate"

class AuditLogResponse(BaseModel):
    """审计日志响应Schema - 更新版本"""
    id: int
    rule_id: Optional[int]  # 删除的规则此字段为None
    action: AuditAction
    old_expression: Optional[str]
    new_expression: Optional[str]
    changed_by: int
    changed_at: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    risk_level: str
    
    # 新增字段
    operation_context: Optional[Dict[str, Any]] = Field(None, description="操作上下文")
    batch_operation: bool = Field(False, description="是否为批量操作")
    
    # 关联数据
    rule_name: Optional[str] = None
    operator_username: Optional[str] = None
    
    class Config:
        from_attributes = True

class SecurityReportResponse(BaseModel):
    """安全报告响应Schema"""
    report_date: datetime
    total_rules: int
    active_rules: int
    high_risk_operations: int
    medium_risk_operations: int
    low_risk_operations: int
    recent_violations: List[AuditLogResponse]
    security_recommendations: List[str]

class CompatibilityStatsResponse(BaseModel):
    """兼容性统计响应Schema"""
    total_rules: int
    active_rules: int
    total_experiences: int
    verified_experiences: int
    pending_experiences: int
    total_checks_today: int
    cache_hit_rate: float
    avg_check_time: float
    top_categories: List[Dict[str, Any]]

# ==================== 外部反馈相关Schema ====================

class FeedbackChannelResponse(BaseModel):
    """外部反馈渠道响应Schema"""
    name: str
    type: str  # forum/email/github/discord
    url: str
    description: str
    guidelines: Optional[str] = None

class FeedbackChannelsResponse(BaseModel):
    """外部反馈渠道列表响应Schema"""
    channels: List[FeedbackChannelResponse]
    general_guidelines: str
    contact_info: Dict[str, str]

# ==================== 分页和筛选Schema ====================

class PaginatedResponse(BaseModel):
    """分页响应基类"""
    total: int
    page: int
    size: int
    pages: int

class RuleListResponse(PaginatedResponse):
    """规则列表响应Schema"""
    items: List[RuleResponse]

class ExperienceListResponse(PaginatedResponse):
    """经验列表响应Schema"""
    items: List[ExperienceResponse]

class RuleFilter(BaseModel):
    """规则筛选Schema"""
    category_a: Optional[str] = None
    category_b: Optional[str] = None
    is_active: Optional[bool] = None
    is_blocking: Optional[bool] = None
    created_by: Optional[int] = None
    search: Optional[str] = None

class ExperienceFilter(BaseModel):
    """经验筛选Schema"""
    part_a_id: Optional[int] = None
    part_b_id: Optional[int] = None
    compatibility_status: Optional[CompatibilityStatus] = None
    source: Optional[SourceType] = None
    verification_status: Optional[VerificationStatus] = None
    added_by: Optional[int] = None












# ==================== 新增：操作响应Schema ====================

class RuleOperationResponse(BaseModel):
    """规则操作响应Schema"""
    message: str = Field(..., description="操作结果消息")
    rule_id: int = Field(..., description="规则ID")
    rule_name: Optional[str] = Field(None, description="规则名称")
    operation: str = Field(..., description="执行的操作")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="操作时间")

class RuleDisableResponse(RuleOperationResponse):
    """规则停用响应Schema"""
    operation: str = Field("disable", description="操作类型")
    previous_state: str = Field("active", description="之前的状态")

class RuleEnableResponse(RuleOperationResponse):
    """规则启用响应Schema"""
    operation: str = Field("enable", description="操作类型")
    previous_state: str = Field("inactive", description="之前的状态")
    security_check_passed: bool = Field(True, description="安全检查是否通过")

class RuleDeleteResponse(BaseModel):
    """规则删除响应Schema"""
    message: str = Field(..., description="删除结果消息")
    rule_id: int = Field(..., description="被删除的规则ID")
    rule_name: str = Field(..., description="被删除的规则名称")
    force_delete: bool = Field(False, description="是否为强制删除")
    dependencies_found: int = Field(0, description="发现的依赖关系数量")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="删除时间")

class BatchOperationResponse(BaseModel):
    """批量操作响应Schema"""
    message: str = Field(..., description="操作结果消息")
    operation: str = Field(..., description="操作类型")
    total_requested: int = Field(..., description="请求处理的规则数量")
    actually_updated: int = Field(..., description="实际更新的规则数量")
    already_in_target_state: int = Field(0, description="已经是目标状态的规则数量")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="错误列表")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="操作时间")

class BatchDisableResponse(BatchOperationResponse):
    """批量停用响应Schema"""
    operation: str = Field("batch_disable", description="操作类型")
    already_disabled: int = Field(0, description="已经停用的规则数量")
    
    @property
    def already_in_target_state(self) -> int:
        return self.already_disabled

class BatchEnableResponse(BatchOperationResponse):
    """批量启用响应Schema"""
    operation: str = Field("batch_enable", description="操作类型")
    already_enabled: int = Field(0, description="已经启用的规则数量")
    security_failures: List[Dict[str, Any]] = Field(default_factory=list, description="安全检查失败的规则")
    
    @property
    def already_in_target_state(self) -> int:
        return self.already_enabled

# ==================== 更新：依赖关系Schema ====================

class RuleDependency(BaseModel):
    """规则依赖关系Schema"""
    type: str = Field(..., description="依赖类型")
    count: int = Field(..., description="依赖数量")
    description: str = Field(..., description="依赖描述")

class RuleDependencyCheck(BaseModel):
    """规则依赖检查响应Schema"""
    rule_id: int = Field(..., description="规则ID")
    rule_name: str = Field(..., description="规则名称")
    has_dependencies: bool = Field(..., description="是否有依赖关系")
    dependencies: List[RuleDependency] = Field(default_factory=list, description="依赖关系列表")
    can_delete_safely: bool = Field(..., description="是否可以安全删除")
    requires_force: bool = Field(..., description="是否需要强制删除")



# ==================== 操作权限Schema ====================

class OperationPermission(BaseModel):
    """操作权限Schema"""
    operation: str = Field(..., description="操作类型")
    allowed: bool = Field(..., description="是否允许")
    reason: Optional[str] = Field(None, description="拒绝原因")
    rate_limit_remaining: Optional[int] = Field(None, description="剩余操作次数")
    cooldown_seconds: Optional[int] = Field(None, description="冷却时间（秒）")

class BulkOperationRequest(BaseModel):
    """批量操作请求Schema"""
    rule_ids: List[int] = Field(..., min_items=1, max_items=100, description="规则ID列表")
    confirm_action: bool = Field(False, description="确认执行操作")
    reason: Optional[str] = Field(None, description="操作原因")

# ==================== 规则状态Schema ====================

class RuleStatus(str, Enum):
    """规则状态枚举"""
    ACTIVE = "active"       # 启用
    INACTIVE = "inactive"   # 停用

class RuleStatusSummary(BaseModel):
    """规则状态摘要Schema"""
    total_rules: int = Field(..., description="总规则数")
    active_rules: int = Field(..., description="启用规则数")
    inactive_rules: int = Field(..., description="停用规则数")
    recently_modified: int = Field(..., description="最近修改的规则数")
    
    @property
    def active_percentage(self) -> float:
        """启用规则百分比"""
        return (self.active_rules / self.total_rules * 100) if self.total_rules > 0 else 0

# ==================== 错误响应Schema ====================

class OperationError(BaseModel):
    """操作错误Schema"""
    error_code: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误消息")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")
    suggestions: List[str] = Field(default_factory=list, description="解决建议")

class DependencyError(OperationError):
    """依赖关系错误Schema"""
    error_code: str = Field("DEPENDENCY_EXISTS", description="错误代码")
    dependencies: List[RuleDependency] = Field(..., description="依赖关系")
    force_delete_option: bool = Field(True, description="是否支持强制删除")

class SecurityError(OperationError):
    """安全错误Schema"""
    error_code: str = Field("SECURITY_VALIDATION_FAILED", description="错误代码")
    security_issues: List[Dict[str, Any]] = Field(..., description="安全问题列表")
    risk_level: str = Field(..., description="风险等级")

# ==================== API文档增强Schema ====================

class APIOperationExample(BaseModel):
    """API操作示例Schema"""
    operation: str = Field(..., description="操作名称")
    method: str = Field(..., description="HTTP方法")
    endpoint: str = Field(..., description="API端点")
    description: str = Field(..., description="操作描述")
    request_example: Optional[Dict[str, Any]] = Field(None, description="请求示例")
    response_example: Optional[Dict[str, Any]] = Field(None, description="响应示例")
    notes: List[str] = Field(default_factory=list, description="注意事项")

# ==================== 系统监控Schema ====================

class SystemHealthCheck(BaseModel):
    """系统健康检查Schema"""
    compatibility_system: bool = Field(..., description="兼容性系统状态")
    rule_engine: bool = Field(..., description="规则引擎状态")
    database_connection: bool = Field(..., description="数据库连接状态")
    cache_system: bool = Field(..., description="缓存系统状态")
    audit_logging: bool = Field(..., description="审计日志状态")
    last_check: datetime = Field(..., description="最后检查时间")

class OperationMetrics(BaseModel):
    """操作指标Schema"""
    total_operations: int = Field(..., description="总操作数")
    successful_operations: int = Field(..., description="成功操作数")
    failed_operations: int = Field(..., description="失败操作数")
    average_response_time: float = Field(..., description="平均响应时间(秒)")
    operations_by_type: Dict[str, int] = Field(..., description="按类型分组的操作数")
    high_risk_operations: int = Field(..., description="高风险操作数")

# ==================== 完整的更新说明 ====================

class MigrationSummary(BaseModel):
    """迁移总结Schema"""
    migration_version: str = Field("1.0.0", description="迁移版本")
    migration_date: datetime = Field(default_factory=datetime.utcnow, description="迁移时间")
    changes_summary: Dict[str, Any] = Field(..., description="变更摘要")
    api_changes: List[str] = Field(..., description="API变更列表")
    breaking_changes: List[str] = Field(..., description="破坏性变更")
    migration_notes: List[str] = Field(..., description="迁移说明")

# ==================== 使用示例常量 ====================

# API操作示例数据
API_OPERATION_EXAMPLES = [
    {
        "operation": "停用规则",
        "method": "PATCH",
        "endpoint": "/api/admin/compatibility/rules/{rule_id}/disable",
        "description": "将指定规则设置为停用状态，规则数据保留但不参与兼容性检查",
        "request_example": None,
        "response_example": {
            "message": "规则已停用",
            "rule_id": 123,
            "rule_name": "CPU功率兼容性检查",
            "operation": "disable",
            "previous_state": "active",
            "timestamp": "2025-05-31T10:30:00Z"
        },
        "notes": [
            "停用后规则不会被删除，可以重新启用",
            "停用操作会被记录到审计日志",
            "相关缓存会被自动清理"
        ]
    },
    {
        "operation": "启用规则",
        "method": "PATCH", 
        "endpoint": "/api/admin/compatibility/rules/{rule_id}/enable",
        "description": "将指定规则设置为启用状态，重新参与兼容性检查",
        "request_example": None,
        "response_example": {
            "message": "规则已启用",
            "rule_id": 123,
            "rule_name": "CPU功率兼容性检查",
            "operation": "enable",
            "previous_state": "inactive",
            "security_check_passed": True,
            "timestamp": "2025-05-31T10:35:00Z"
        },
        "notes": [
            "启用前会重新验证规则表达式的安全性",
            "如果安全验证失败，启用操作会被拒绝",
            "启用操作会被记录到审计日志"
        ]
    },
    {
        "operation": "删除规则",
        "method": "DELETE",
        "endpoint": "/api/admin/compatibility/rules/{rule_id}?force=false",
        "description": "彻底删除规则，不可恢复。会检查依赖关系。",
        "request_example": None,
        "response_example": {
            "message": "规则已彻底删除",
            "rule_id": 123,
            "rule_name": "已删除的规则",
            "force_delete": False,
            "dependencies_found": 0,
            "timestamp": "2025-05-31T10:40:00Z"
        },
        "notes": [
            "⚠️ 这是不可逆的物理删除操作",
            "如果规则有依赖关系，需要使用 force=true 参数",
            "建议优先使用停用功能而不是删除",
            "删除操作为高风险操作，会被特别审计"
        ]
    },
    {
        "operation": "批量停用",
        "method": "PATCH",
        "endpoint": "/api/admin/compatibility/rules/batch/disable", 
        "description": "批量停用多个规则",
        "request_example": {
            "rule_ids": [101, 102, 103],
            "confirm_action": True,
            "reason": "临时维护"
        },
        "response_example": {
            "message": "批量停用完成",
            "operation": "batch_disable",
            "total_requested": 3,
            "actually_updated": 2,
            "already_disabled": 1,
            "errors": [],
            "timestamp": "2025-05-31T10:45:00Z"
        },
        "notes": [
            "支持同时操作多个规则",
            "会跳过已经停用的规则",
            "每个规则都会单独记录审计日志"
        ]
    }
]

# 迁移变更摘要
MIGRATION_CHANGES = {
    "database_changes": {
        "updated_constraints": ["rule_audit_log.check_audit_action"],
        "new_indexes": ["idx_audit_log_disable_enable"],
        "new_audit_actions": ["disable", "enable"],
        "data_cleanup": ["is_active field normalization", "historical audit records"]
    },
    "api_changes": {
        "new_endpoints": [
            "PATCH /rules/{id}/disable",
            "PATCH /rules/{id}/enable", 
            "PATCH /rules/batch/disable",
            "PATCH /rules/batch/enable"
        ],
        "modified_endpoints": [
            "DELETE /rules/{id} - now performs physical deletion"
        ],
        "new_parameters": [
            "force query parameter for DELETE operations"
        ]
    },
    "behavior_changes": {
        "delete_operation": "Changed from soft delete to hard delete",
        "disable_enable": "New dedicated endpoints for state management",
        "dependency_checking": "Added for delete operations",
        "audit_logging": "Enhanced with new operation types"
    }
}

# 破坏性变更说明
BREAKING_CHANGES = [
    "DELETE /api/admin/compatibility/rules/{rule_id} 现在执行物理删除而不是软删除",
    "之前依赖删除API进行停用的客户端需要改用新的 disable 端点",
    "审计日志中的操作类型增加了 'disable' 和 'enable'",
    "删除操作现在会检查依赖关系，可能需要 force=true 参数"
]

# 迁移说明
MIGRATION_NOTES = [
    "执行迁移前请备份数据库",
    "迁移会为历史规则补充审计记录",
    "现有的 is_active 字段行为不变，但语义更清晰",
    "建议更新前端客户端以使用新的停用/启用端点",
    "删除操作现在需要更高的权限和确认",
    "新增的审计日志可以提供更详细的操作历史"
]