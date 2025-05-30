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

# ==================== 审计和统计相关Schema ====================

class AuditLogResponse(BaseModel):
    """审计日志响应Schema"""
    id: int
    rule_id: Optional[int]
    action: str
    old_expression: Optional[str]
    new_expression: Optional[str]
    changed_by: int
    changed_at: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    risk_level: RiskLevel
    
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