# backend/app/models/compatibility.py
"""
兼容性检查系统数据模型

包含所有兼容性相关的SQLAlchemy模型定义
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB, INET
from app.core.database import Base
from typing import Optional, Dict, Any, List
import enum

class CompatibilityStatus(enum.Enum):
    """兼容性状态枚举"""
    COMPATIBLE = "compatible"           # 兼容
    INCOMPATIBLE = "incompatible"       # 不兼容
    CONDITIONAL = "conditional"         # 有条件兼容

class VerificationStatus(enum.Enum):
    """验证状态枚举"""
    VERIFIED = "verified"               # 已验证
    PENDING = "pending"                 # 待验证
    DISPUTED = "disputed"               # 有争议

class SourceType(enum.Enum):
    """数据来源类型枚举"""
    ADMIN = "admin"                     # 管理员添加
    OFFICIAL = "official"               # 官方数据
    USER_CONTRIBUTION = "user_contribution"  # 用户贡献（未来扩展）

class AuditAction(enum.Enum):
    """审计动作枚举"""
    CREATE = "create"                   # 创建
    UPDATE = "update"                   # 更新
    DELETE = "delete"                   # 删除
    TEST = "test"                       # 测试
    VALIDATE = "validate"               # 验证

class RiskLevel(enum.Enum):
    """风险等级枚举"""
    LOW = "low"                         # 低风险
    MEDIUM = "medium"                   # 中风险
    HIGH = "high"                       # 高风险

class CompatibilityRule(Base):
    """兼容性规则模型"""
    __tablename__ = "compatibility_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="规则名称")
    description = Column(Text, comment="规则描述")
    rule_expression = Column(Text, nullable=False, comment="规则表达式")
    category_a = Column(String(100), nullable=False, index=True, comment="零件类别A")
    category_b = Column(String(100), nullable=False, index=True, comment="零件类别B")
    weight = Column(Integer, nullable=False, default=100, comment="规则权重")
    is_blocking = Column(Boolean, nullable=False, default=False, comment="是否为阻断性规则")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, comment="创建者ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, nullable=False, default=True, index=True, comment="是否启用")
    
    # 关系
    creator = relationship("User", foreign_keys=[created_by])
    audit_logs = relationship("RuleAuditLog", back_populates="rule", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('ix_compatibility_rules_categories', 'category_a', 'category_b'),
        Index('ix_compatibility_rules_active_weight', 'is_active', 'weight'),
        CheckConstraint('weight >= 0 AND weight <= 1000', name='check_rule_weight_range'),
    )
    
    def __repr__(self):
        return f"<CompatibilityRule(id={self.id}, name='{self.name}', categories='{self.category_a}+{self.category_b}')>"

class CompatibilityExperience(Base):
    """兼容性经验模型（支持未来扩展的设计）"""
    __tablename__ = "compatibility_experiences"
    
    id = Column(Integer, primary_key=True, index=True)
    part_a_id = Column(Integer, ForeignKey("parts.id", ondelete="CASCADE"), nullable=False, index=True)
    part_b_id = Column(Integer, ForeignKey("parts.id", ondelete="CASCADE"), nullable=False, index=True)
    compatibility_status = Column(String(20), nullable=False, index=True, comment="兼容性状态")
    compatibility_score = Column(Integer, comment="兼容性评分(0-100)")
    notes = Column(Text, comment="备注说明")
    source = Column(String(50), nullable=False, default="admin", index=True, comment="数据来源")
    reference_url = Column(String(500), comment="外部反馈来源链接")
    verification_status = Column(String(20), nullable=False, default="verified", comment="验证状态")
    added_by = Column(Integer, ForeignKey("users.id"), nullable=False, comment="添加者ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    part_a = relationship("Part", foreign_keys=[part_a_id])
    part_b = relationship("Part", foreign_keys=[part_b_id])
    added_by_user = relationship("User", foreign_keys=[added_by])
    
    # 约束和索引
    __table_args__ = (
        CheckConstraint('compatibility_score >= 0 AND compatibility_score <= 100', 
                       name='check_compatibility_score_range'),
        CheckConstraint("compatibility_status IN ('compatible', 'incompatible', 'conditional')", 
                       name='check_compatibility_status'),
        CheckConstraint("source IN ('admin', 'official', 'user_contribution')", 
                       name='check_source_values'),
        CheckConstraint("verification_status IN ('verified', 'pending', 'disputed')", 
                       name='check_verification_status'),
        CheckConstraint('part_a_id != part_b_id', name='check_different_parts'),
        Index('ix_compatibility_experiences_parts', 'part_a_id', 'part_b_id', unique=True),
        Index('ix_compatibility_experiences_source_status', 'source', 'verification_status'),
    )
    
    def __repr__(self):
        return f"<CompatibilityExperience(id={self.id}, parts={self.part_a_id}+{self.part_b_id}, status='{self.compatibility_status}')>"

class CompatibilityCache(Base):
    """兼容性检查缓存模型"""
    __tablename__ = "compatibility_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    part_ids_hash = Column(String(64), nullable=False, unique=True, index=True, comment="零件ID组合哈希")
    part_ids = Column(JSONB, nullable=False, comment="零件ID列表")
    compatibility_result = Column(JSONB, nullable=False, comment="兼容性检查结果")
    calculated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), index=True, comment="过期时间")
    
    __table_args__ = (
        Index('ix_compatibility_cache_expires_calc', 'expires_at', 'calculated_at'),
    )
    
    def __repr__(self):
        return f"<CompatibilityCache(id={self.id}, hash='{self.part_ids_hash[:8]}...', expires={self.expires_at})>"

class CompatibilityTemplate(Base):
    """零件组合模板模型"""
    __tablename__ = "compatibility_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True, comment="模板名称")
    description = Column(Text, comment="模板描述")
    categories = Column(JSONB, nullable=False, comment="零件类别列表")
    rules = Column(JSONB, nullable=False, comment="规则配置")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_public = Column(Boolean, nullable=False, default=False, index=True, comment="是否公开")
    
    # 关系
    creator = relationship("User", foreign_keys=[created_by])
    
    __table_args__ = (
        Index('ix_compatibility_templates_public_created', 'is_public', 'created_at'),
    )
    
    def __repr__(self):
        return f"<CompatibilityTemplate(id={self.id}, name='{self.name}', public={self.is_public})>"

class RuleAuditLog(Base):
    """规则审计日志模型"""
    __tablename__ = "rule_audit_log"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("compatibility_rules.id", ondelete="SET NULL"), index=True)
    action = Column(String(20), nullable=False, index=True, comment="操作类型")
    old_expression = Column(Text, comment="旧表达式")
    new_expression = Column(Text, comment="新表达式")
    validation_result = Column(JSONB, comment="验证结果")
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False, comment="操作者ID")
    changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    ip_address = Column(INET, comment="IP地址")
    user_agent = Column(Text, comment="用户代理")
    risk_level = Column(String(20), nullable=False, default="low", index=True, comment="风险等级")
    
    # 关系
    rule = relationship("CompatibilityRule", back_populates="audit_logs")
    operator = relationship("User", foreign_keys=[changed_by])
    
    __table_args__ = (
        CheckConstraint("action IN ('create', 'update', 'delete', 'test', 'validate')", 
                       name='check_audit_action'),
        CheckConstraint("risk_level IN ('low', 'medium', 'high')", 
                       name='check_risk_level'),
        Index('ix_rule_audit_log_time_risk', 'changed_at', 'risk_level'),
        Index('ix_rule_audit_log_user_action', 'changed_by', 'action'),
    )
    
    def __repr__(self):
        return f"<RuleAuditLog(id={self.id}, rule_id={self.rule_id}, action='{self.action}', risk='{self.risk_level}')>"

class ExpressionSecurityCache(Base):
    """表达式安全扫描缓存模型"""
    __tablename__ = "expression_security_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    expression_hash = Column(String(64), nullable=False, unique=True, index=True, comment="表达式哈希")
    expression_text = Column(Text, nullable=False, comment="表达式文本")
    is_safe = Column(Boolean, nullable=False, index=True, comment="是否安全")
    security_issues = Column(JSONB, comment="安全问题列表")
    scanned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index('ix_expression_security_safe_scanned', 'is_safe', 'scanned_at'),
    )
    
    def __repr__(self):
        return f"<ExpressionSecurityCache(id={self.id}, hash='{self.expression_hash[:8]}...', safe={self.is_safe})>"

# 工具函数
def get_compatibility_experience_by_parts(db, part_a_id: int, part_b_id: int) -> Optional[CompatibilityExperience]:
    """根据零件ID获取兼容性经验（支持双向查找）"""
    
    # 先尝试 A->B 的顺序
    experience = db.query(CompatibilityExperience).filter(
        CompatibilityExperience.part_a_id == part_a_id,
        CompatibilityExperience.part_b_id == part_b_id
    ).first()
    
    if experience:
        return experience
    
    # 再尝试 B->A 的顺序
    experience = db.query(CompatibilityExperience).filter(
        CompatibilityExperience.part_a_id == part_b_id,
        CompatibilityExperience.part_b_id == part_a_id
    ).first()
    
    return experience

def get_active_rules_for_categories(db, category_a: str, category_b: str) -> List[CompatibilityRule]:
    """获取指定类别组合的活跃规则"""
    
    return db.query(CompatibilityRule).filter(
        CompatibilityRule.is_active == True,
        (
            (CompatibilityRule.category_a == category_a and CompatibilityRule.category_b == category_b) |
            (CompatibilityRule.category_a == category_b and CompatibilityRule.category_b == category_a)
        )
    ).order_by(CompatibilityRule.weight.desc()).all()

def create_part_ids_hash(part_ids: List[int]) -> str:
    """创建零件ID列表的哈希值"""
    import hashlib
    
    # 排序以确保相同零件组合产生相同哈希
    sorted_ids = sorted(part_ids)
    id_string = ','.join(map(str, sorted_ids))
    return hashlib.sha256(id_string.encode()).hexdigest()

def create_expression_hash(expression: str) -> str:
    """创建表达式的哈希值"""
    import hashlib
    
    # 标准化表达式（去除空格、统一格式）
    normalized = expression.strip().replace(' ', '').lower()
    return hashlib.sha256(normalized.encode()).hexdigest()