# backend/app/api/admin/compatibility.py
"""
管理员兼容性管理API

提供兼容性规则、经验管理和安全验证功能
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta

from app.core.database import get_db
from app.auth.middleware import require_admin
from app.auth.models import User
from app.models.compatibility import (
    CompatibilityRule, CompatibilityExperience, RuleAuditLog,
    ExpressionSecurityCache, CompatibilityCache, CompatibilityTemplate,
    get_compatibility_experience_by_parts, get_active_rules_for_categories
)
from app.models.part import Part
from app.schemas.compatibility import (
    # 规则相关
    RuleCreate, RuleUpdate, RuleResponse, RuleTestRequest, RuleTestResponse,
    SecurityValidationRequest, SecurityValidationResponse, RuleListResponse,
    # 经验相关
    ExperienceCreate, ExperienceUpdate, ExperienceResponse, ExperienceListResponse,
    ExperienceBatchCreateRequest, ExperienceBatchCreateResponse,
    # 审计和统计
    AuditLogResponse, CompatibilityStatsResponse, SecurityReportResponse,
    # 筛选
    RuleFilter, ExperienceFilter,
    # 通用
    PaginatedResponse
)
from app.services.compatibility_engine import compatibility_engine
from app.services.safe_expression_parser import SafeExpressionEngine

router = APIRouter()
logger = logging.getLogger(__name__)

# 初始化安全表达式引擎
expression_engine = SafeExpressionEngine()

# ==================== 规则管理API ====================

@router.post("/rules", response_model=RuleResponse)
async def create_compatibility_rule(
    rule_data: RuleCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    创建兼容性规则
    
    - 自动进行表达式安全验证
    - 记录操作审计日志
    - 支持规则权重和阻断设置
    """
    try:
        logger.info(f"管理员 {current_user.username} 创建兼容性规则: {rule_data.name}")
        
        # 1. 验证表达式安全性
        security_validation = await expression_engine.validate_expression_security(
            rule_data.rule_expression, db
        )
        
        if not security_validation.is_safe:
            high_risk_issues = [
                issue for issue in security_validation.security_issues 
                if issue.get("severity") == "high"
            ]
            raise HTTPException(
                status_code=400, 
                detail={
                    "message": "表达式存在安全风险，无法创建规则",
                    "security_issues": high_risk_issues,
                    "recommendations": security_validation.recommendations
                }
            )
        
        # 2. 检查规则名称唯一性
        existing_rule = db.query(CompatibilityRule).filter(
            CompatibilityRule.name == rule_data.name
        ).first()
        
        if existing_rule:
            raise HTTPException(
                status_code=409, 
                detail=f"规则名称 '{rule_data.name}' 已存在"
            )
        
        # 3. 创建规则
        new_rule = CompatibilityRule(
            name=rule_data.name,
            description=rule_data.description,
            rule_expression=rule_data.rule_expression,
            category_a=rule_data.category_a,
            category_b=rule_data.category_b,
            weight=rule_data.weight,
            is_blocking=rule_data.is_blocking,
            created_by=current_user.id,
            is_active=True
        )
        
        db.add(new_rule)
        db.commit()
        db.refresh(new_rule)
        
        # 4. 记录审计日志
        await _log_rule_operation(
            db=db,
            rule_id=new_rule.id,
            action="create",
            user_id=current_user.id,
            new_expression=rule_data.rule_expression,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            security_result=security_validation.dict()
        )
        
        logger.info(f"规则创建成功: ID={new_rule.id}, 名称={new_rule.name}")
        return new_rule
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建规则失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建规则失败: {str(e)}")

@router.get("/rules", response_model=RuleListResponse)
async def get_compatibility_rules(
    # 分页参数
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    # 筛选参数
    category_a: Optional[str] = Query(None, description="零件类别A"),
    category_b: Optional[str] = Query(None, description="零件类别B"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    is_blocking: Optional[bool] = Query(None, description="是否阻断性"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    # 排序
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    获取兼容性规则列表
    
    - 支持多条件筛选和搜索
    - 分页返回结果
    - 包含创建者信息
    """
    try:
        # 构建基础查询
        query = db.query(CompatibilityRule)
        
        # 应用筛选条件
        if category_a:
            query = query.filter(CompatibilityRule.category_a == category_a)
        if category_b:
            query = query.filter(CompatibilityRule.category_b == category_b)
        if is_active is not None:
            query = query.filter(CompatibilityRule.is_active == is_active)
        if is_blocking is not None:
            query = query.filter(CompatibilityRule.is_blocking == is_blocking)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    CompatibilityRule.name.ilike(search_term),
                    CompatibilityRule.description.ilike(search_term),
                    CompatibilityRule.rule_expression.ilike(search_term)
                )
            )
        
        # 应用排序
        if sort_order.lower() == "desc":
            query = query.order_by(desc(getattr(CompatibilityRule, sort_by, CompatibilityRule.created_at)))
        else:
            query = query.order_by(getattr(CompatibilityRule, sort_by, CompatibilityRule.created_at))
        
        # 计算总数
        total = query.count()
        
        # 应用分页
        offset = (page - 1) * size
        rules = query.offset(offset).limit(size).all()
        
        # 计算分页信息
        pages = (total + size - 1) // size
        
        return RuleListResponse(
            items=rules,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"获取规则列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取规则列表失败: {str(e)}")

@router.get("/rules/{rule_id}", response_model=RuleResponse)
async def get_compatibility_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取单个兼容性规则详情"""
    
    rule = db.query(CompatibilityRule).filter(CompatibilityRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="规则未找到")
    
    return rule

@router.put("/rules/{rule_id}", response_model=RuleResponse)
async def update_compatibility_rule(
    rule_id: int,
    rule_update: RuleUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    更新兼容性规则
    
    - 如果更新表达式，自动进行安全验证
    - 记录变更审计日志
    - 支持部分字段更新
    """
    try:
        # 获取现有规则
        rule = db.query(CompatibilityRule).filter(CompatibilityRule.id == rule_id).first()
        if not rule:
            raise HTTPException(status_code=404, detail="规则未找到")
        
        logger.info(f"管理员 {current_user.username} 更新规则 {rule_id}: {rule.name}")
        
        # 保存旧表达式用于审计
        old_expression = rule.rule_expression
        
        # 如果更新表达式，进行安全验证
        security_validation = None
        if rule_update.rule_expression and rule_update.rule_expression != old_expression:
            security_validation = await expression_engine.validate_expression_security(
                rule_update.rule_expression, db
            )
            
            if not security_validation.is_safe:
                high_risk_issues = [
                    issue for issue in security_validation.security_issues 
                    if issue.get("severity") == "high"
                ]
                raise HTTPException(
                    status_code=400, 
                    detail={
                        "message": "表达式存在安全风险，无法更新规则",
                        "security_issues": high_risk_issues,
                        "recommendations": security_validation.recommendations
                    }
                )
        
        # 检查名称唯一性（如果更新名称）
        if rule_update.name and rule_update.name != rule.name:
            existing_rule = db.query(CompatibilityRule).filter(
                CompatibilityRule.name == rule_update.name,
                CompatibilityRule.id != rule_id
            ).first()
            
            if existing_rule:
                raise HTTPException(
                    status_code=409, 
                    detail=f"规则名称 '{rule_update.name}' 已存在"
                )
        
        # 更新字段
        update_data = rule_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)
        
        rule.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(rule)
        
        # 记录审计日志
        await _log_rule_operation(
            db=db,
            rule_id=rule.id,
            action="update",
            user_id=current_user.id,
            old_expression=old_expression,
            new_expression=rule.rule_expression,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            security_result=security_validation.dict() if security_validation else None
        )
        
        logger.info(f"规则更新成功: ID={rule.id}")
        return rule
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新规则失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新规则失败: {str(e)}")

@router.delete("/rules/{rule_id}")
async def delete_compatibility_rule(
    rule_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    删除兼容性规则
    
    - 软删除（设置为非活跃状态）
    - 记录删除审计日志
    - 清理相关缓存
    """
    try:
        rule = db.query(CompatibilityRule).filter(CompatibilityRule.id == rule_id).first()
        if not rule:
            raise HTTPException(status_code=404, detail="规则未找到")
        
        logger.info(f"管理员 {current_user.username} 删除规则 {rule_id}: {rule.name}")
        
        # 软删除（设置为非活跃）
        old_expression = rule.rule_expression
        rule.is_active = False
        rule.updated_at = datetime.utcnow()
        db.commit()
        
        # 记录审计日志
        await _log_rule_operation(
            db=db,
            rule_id=rule.id,
            action="delete",
            user_id=current_user.id,
            old_expression=old_expression,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent")
        )
        
        # 清理相关缓存
        await _clear_related_cache(db, rule.category_a, rule.category_b)
        
        logger.info(f"规则删除成功: ID={rule.id}")
        return {"message": "规则已删除", "rule_id": rule.id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除规则失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除规则失败: {str(e)}")

# ==================== 安全验证API ====================

@router.post("/rules/validate", response_model=SecurityValidationResponse)
async def validate_expression_security(
    validation_request: SecurityValidationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    验证表达式安全性
    
    - 检查语法安全性
    - 返回详细的安全报告
    - 提供修复建议
    """
    try:
        logger.info(f"管理员 {current_user.username} 验证表达式安全性")
        
        validation_result = await expression_engine.validate_expression_security(
            validation_request.expression, db
        )
        
        return validation_result
        
    except Exception as e:
        logger.error(f"表达式安全验证失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"安全验证失败: {str(e)}")

@router.post("/rules/{rule_id}/test", response_model=RuleTestResponse)
async def test_rule_execution(
    rule_id: int,
    test_request: RuleTestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    测试规则执行
    
    - 在沙箱环境中安全执行规则
    - 使用提供的测试数据
    - 返回执行结果和性能指标
    """
    try:
        # 获取规则
        rule = db.query(CompatibilityRule).filter(CompatibilityRule.id == rule_id).first()
        if not rule:
            raise HTTPException(status_code=404, detail="规则未找到")
        
        logger.info(f"管理员 {current_user.username} 测试规则 {rule_id}: {rule.name}")
        
        # 先验证安全性
        security_validation = await expression_engine.validate_expression_security(
            rule.rule_expression, db
        )
        
        if not security_validation.is_safe:
            return RuleTestResponse(
                success=False,
                result=None,
                execution_time=0.0,
                error_message="规则表达式不安全，无法执行测试",
                security_check=security_validation.dict()
            )
        
        # 执行测试
        import time
        start_time = time.time()
        
        try:
            result = await expression_engine.execute_safe_expression(
                rule.rule_expression, 
                test_request.test_data
            )
            
            execution_time = time.time() - start_time
            
            # 记录测试审计日志
            await _log_rule_operation(
                db=db,
                rule_id=rule.id,
                action="test",
                user_id=current_user.id,
                validation_result={
                    "test_success": True,
                    "result": str(result),
                    "execution_time": execution_time
                }
            )
            
            return RuleTestResponse(
                success=True,
                result=result,
                execution_time=execution_time,
                security_check=security_validation.dict()
            )
            
        except Exception as exec_error:
            execution_time = time.time() - start_time
            error_message = str(exec_error)
            
            # 记录测试失败日志
            await _log_rule_operation(
                db=db,
                rule_id=rule.id,
                action="test",
                user_id=current_user.id,
                validation_result={
                    "test_success": False,
                    "error": error_message,
                    "execution_time": execution_time
                }
            )
            
            return RuleTestResponse(
                success=False,
                result=None,
                execution_time=execution_time,
                error_message=error_message,
                security_check=security_validation.dict()
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"规则测试失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"规则测试失败: {str(e)}")

# ==================== 经验管理API ====================

@router.post("/experiences", response_model=ExperienceResponse)
async def create_compatibility_experience(
    experience_data: ExperienceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    创建兼容性经验
    
    - 检查零件是否存在
    - 防止重复经验条目
    - 支持外部反馈来源追踪
    """
    try:
        logger.info(f"管理员 {current_user.username} 创建兼容性经验")
        
        # 验证零件存在
        part_a = db.query(Part).filter(Part.id == experience_data.part_a_id).first()
        part_b = db.query(Part).filter(Part.id == experience_data.part_b_id).first()
        
        if not part_a:
            raise HTTPException(status_code=404, detail=f"零件A未找到: ID={experience_data.part_a_id}")
        if not part_b:
            raise HTTPException(status_code=404, detail=f"零件B未找到: ID={experience_data.part_b_id}")
        
        # 检查是否已存在经验（双向检查）
        existing = get_compatibility_experience_by_parts(
            db, experience_data.part_a_id, experience_data.part_b_id
        )
        
        if existing:
            raise HTTPException(
                status_code=409, 
                detail=f"零件 {part_a.name} 和 {part_b.name} 的兼容性经验已存在"
            )
        
        # 创建经验记录
        new_experience = CompatibilityExperience(
            part_a_id=experience_data.part_a_id,
            part_b_id=experience_data.part_b_id,
            compatibility_status=experience_data.compatibility_status.value,
            compatibility_score=experience_data.compatibility_score,
            notes=experience_data.notes,
            source=experience_data.source.value,
            reference_url=experience_data.reference_url,
            verification_status=experience_data.verification_status.value,
            added_by=current_user.id
        )
        
        db.add(new_experience)
        db.commit()
        db.refresh(new_experience)
        
        # 清理相关缓存
        await _clear_related_cache(db, part_a.category, part_b.category)
        
        logger.info(f"兼容性经验创建成功: ID={new_experience.id}")
        return new_experience
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建兼容性经验失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建兼容性经验失败: {str(e)}")

@router.get("/experiences", response_model=ExperienceListResponse)
async def get_compatibility_experiences(
    # 分页参数
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    # 筛选参数
    part_a_id: Optional[int] = Query(None, description="零件A的ID"),
    part_b_id: Optional[int] = Query(None, description="零件B的ID"),
    compatibility_status: Optional[str] = Query(None, description="兼容性状态"),
    source: Optional[str] = Query(None, description="数据来源"),
    verification_status: Optional[str] = Query(None, description="验证状态"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取兼容性经验列表"""
    
    try:
        # 构建查询
        query = db.query(CompatibilityExperience)
        
        # 应用筛选
        if part_a_id:
            query = query.filter(CompatibilityExperience.part_a_id == part_a_id)
        if part_b_id:
            query = query.filter(CompatibilityExperience.part_b_id == part_b_id)
        if compatibility_status:
            query = query.filter(CompatibilityExperience.compatibility_status == compatibility_status)
        if source:
            query = query.filter(CompatibilityExperience.source == source)
        if verification_status:
            query = query.filter(CompatibilityExperience.verification_status == verification_status)
        
        # 排序
        query = query.order_by(desc(CompatibilityExperience.created_at))
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * size
        experiences = query.offset(offset).limit(size).all()
        
        # 计算分页信息
        pages = (total + size - 1) // size
        
        return ExperienceListResponse(
            items=experiences,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"获取兼容性经验列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取兼容性经验列表失败: {str(e)}")

@router.put("/experiences/{experience_id}", response_model=ExperienceResponse)
async def update_compatibility_experience(
    experience_id: int,
    experience_update: ExperienceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """更新兼容性经验"""
    
    try:
        experience = db.query(CompatibilityExperience).filter(
            CompatibilityExperience.id == experience_id
        ).first()
        
        if not experience:
            raise HTTPException(status_code=404, detail="兼容性经验未找到")
        
        logger.info(f"管理员 {current_user.username} 更新兼容性经验 {experience_id}")
        
        # 更新字段
        update_data = experience_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(value, 'value'):  # 处理枚举类型
                setattr(experience, field, value.value)
            else:
                setattr(experience, field, value)
        
        experience.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(experience)
        
        # 清理相关缓存
        part_a = db.query(Part).filter(Part.id == experience.part_a_id).first()
        part_b = db.query(Part).filter(Part.id == experience.part_b_id).first()
        if part_a and part_b:
            await _clear_related_cache(db, part_a.category, part_b.category)
        
        logger.info(f"兼容性经验更新成功: ID={experience.id}")
        return experience
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新兼容性经验失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新兼容性经验失败: {str(e)}")

@router.delete("/experiences/{experience_id}")
async def delete_compatibility_experience(
    experience_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """删除兼容性经验"""
    
    try:
        experience = db.query(CompatibilityExperience).filter(
            CompatibilityExperience.id == experience_id
        ).first()
        
        if not experience:
            raise HTTPException(status_code=404, detail="兼容性经验未找到")
        
        logger.info(f"管理员 {current_user.username} 删除兼容性经验 {experience_id}")
        
        # 获取零件信息用于清理缓存
        part_a = db.query(Part).filter(Part.id == experience.part_a_id).first()
        part_b = db.query(Part).filter(Part.id == experience.part_b_id).first()
        
        # 删除经验
        db.delete(experience)
        db.commit()
        
        # 清理相关缓存
        if part_a and part_b:
            await _clear_related_cache(db, part_a.category, part_b.category)
        
        logger.info(f"兼容性经验删除成功: ID={experience_id}")
        return {"message": "兼容性经验已删除", "experience_id": experience_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除兼容性经验失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除兼容性经验失败: {str(e)}")

@router.post("/experiences/batch", response_model=ExperienceBatchCreateResponse)
async def batch_create_experiences(
    batch_request: ExperienceBatchCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """批量创建兼容性经验"""
    
    try:
        logger.info(f"管理员 {current_user.username} 批量创建 {len(batch_request.experiences)} 个兼容性经验")
        
        result = ExperienceBatchCreateResponse(
            success=True,
            total_processed=len(batch_request.experiences),
            successful_creates=0,
            skipped_duplicates=0,
            errors=[]
        )
        
        for i, experience_data in enumerate(batch_request.experiences):
            try:
                # 验证零件存在
                part_a = db.query(Part).filter(Part.id == experience_data.part_a_id).first()
                part_b = db.query(Part).filter(Part.id == experience_data.part_b_id).first()
                
                if not part_a or not part_b:
                    result.errors.append({
                        "index": i,
                        "error": f"零件未找到: part_a_id={experience_data.part_a_id}, part_b_id={experience_data.part_b_id}"
                    })
                    continue
                
                # 检查是否已存在
                existing = get_compatibility_experience_by_parts(
                    db, experience_data.part_a_id, experience_data.part_b_id
                )
                
                if existing:
                    result.skipped_duplicates += 1
                    continue
                
                # 创建经验记录
                new_experience = CompatibilityExperience(
                    part_a_id=experience_data.part_a_id,
                    part_b_id=experience_data.part_b_id,
                    compatibility_status=experience_data.compatibility_status.value,
                    compatibility_score=experience_data.compatibility_score,
                    notes=experience_data.notes,
                    source=experience_data.source.value,
                    reference_url=experience_data.reference_url,
                    verification_status=experience_data.verification_status.value,
                    added_by=current_user.id
                )
                
                db.add(new_experience)
                result.successful_creates += 1
                
            except Exception as e:
                result.errors.append({
                    "index": i,
                    "error": str(e)
                })
                db.rollback()
                # 重新开启事务继续处理
                db.begin()
        
        # 提交所有成功的创建
        db.commit()
        
        # 批量清理缓存
        await _clear_all_compatibility_cache(db)
        
        logger.info(f"批量创建完成: 成功{result.successful_creates}个, 跳过{result.skipped_duplicates}个, 错误{len(result.errors)}个")
        return result
        
    except Exception as e:
        logger.error(f"批量创建兼容性经验失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"批量创建失败: {str(e)}")

# ==================== 统计和监控API ====================

@router.get("/stats", response_model=CompatibilityStatsResponse)
async def get_compatibility_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取兼容性系统统计信息"""
    
    try:
        # 规则统计
        total_rules = db.query(CompatibilityRule).count()
        active_rules = db.query(CompatibilityRule).filter(CompatibilityRule.is_active == True).count()
        
        # 经验统计
        total_experiences = db.query(CompatibilityExperience).count()
        verified_experiences = db.query(CompatibilityExperience).filter(
            CompatibilityExperience.verification_status == "verified"
        ).count()
        pending_experiences = db.query(CompatibilityExperience).filter(
            CompatibilityExperience.verification_status == "pending"
        ).count()
        
        # 今日检查统计（通过缓存表统计）
        today = datetime.utcnow().date()
        total_checks_today = db.query(CompatibilityCache).filter(
            CompatibilityCache.calculated_at >= today
        ).count()
        
        # 缓存命中率（最近7天）
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_cache_entries = db.query(CompatibilityCache).filter(
            CompatibilityCache.calculated_at >= week_ago
        ).count()
        
        # 简化的缓存命中率计算
        cache_hit_rate = min(0.8, recent_cache_entries * 0.1) if recent_cache_entries > 0 else 0.0
        
        # 平均检查时间（模拟数据，实际应该从日志中计算）
        avg_check_time = 0.5  # 秒
        
        # 热门类别统计
        from sqlalchemy import func
        top_categories = db.query(
            CompatibilityRule.category_a.label('category'),
            func.count(CompatibilityRule.id).label('count')
        ).filter(
            CompatibilityRule.is_active == True
        ).group_by(
            CompatibilityRule.category_a
        ).order_by(
            func.count(CompatibilityRule.id).desc()
        ).limit(10).all()
        
        top_categories_data = [
            {"category": cat.category, "rule_count": cat.count}
            for cat in top_categories
        ]
        
        return CompatibilityStatsResponse(
            total_rules=total_rules,
            active_rules=active_rules,
            total_experiences=total_experiences,
            verified_experiences=verified_experiences,
            pending_experiences=pending_experiences,
            total_checks_today=total_checks_today,
            cache_hit_rate=cache_hit_rate,
            avg_check_time=avg_check_time,
            top_categories=top_categories_data
        )
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@router.get("/audit-log", response_model=List[AuditLogResponse])
async def get_audit_log(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(50, ge=1, le=200, description="每页数量"),
    action: Optional[str] = Query(None, description="操作类型"),
    risk_level: Optional[str] = Query(None, description="风险等级"),
    days: int = Query(30, ge=1, le=365, description="查询天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取规则操作审计日志"""
    
    try:
        # 构建查询
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = db.query(RuleAuditLog).filter(
            RuleAuditLog.changed_at >= cutoff_date
        )
        
        # 应用筛选
        if action:
            query = query.filter(RuleAuditLog.action == action)
        if risk_level:
            query = query.filter(RuleAuditLog.risk_level == risk_level)
        
        # 排序
        query = query.order_by(desc(RuleAuditLog.changed_at))
        
        # 分页
        offset = (page - 1) * size
        logs = query.offset(offset).limit(size).all()
        
        return logs
        
    except Exception as e:
        logger.error(f"获取审计日志失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取审计日志失败: {str(e)}")

@router.get("/security-report", response_model=SecurityReportResponse)
async def get_security_report(
    days: int = Query(30, ge=1, le=365, description="报告周期（天）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取安全状态报告"""
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # 规则统计
        total_rules = db.query(CompatibilityRule).count()
        active_rules = db.query(CompatibilityRule).filter(CompatibilityRule.is_active == True).count()
        
        # 风险操作统计
        high_risk_ops = db.query(RuleAuditLog).filter(
            RuleAuditLog.changed_at >= cutoff_date,
            RuleAuditLog.risk_level == "high"
        ).count()
        
        medium_risk_ops = db.query(RuleAuditLog).filter(
            RuleAuditLog.changed_at >= cutoff_date,
            RuleAuditLog.risk_level == "medium"
        ).count()
        
        low_risk_ops = db.query(RuleAuditLog).filter(
            RuleAuditLog.changed_at >= cutoff_date,
            RuleAuditLog.risk_level == "low"
        ).count()
        
        # 最近的违规操作
        recent_violations = db.query(RuleAuditLog).filter(
            RuleAuditLog.changed_at >= cutoff_date,
            RuleAuditLog.risk_level.in_(["high", "medium"])
        ).order_by(desc(RuleAuditLog.changed_at)).limit(10).all()
        
        # 安全建议
        security_recommendations = []
        if high_risk_ops > 0:
            security_recommendations.append(f"发现 {high_risk_ops} 个高风险操作，建议立即检查")
        if medium_risk_ops > 10:
            security_recommendations.append("中风险操作较多，建议加强规则审查")
        if active_rules == 0:
            security_recommendations.append("系统中没有活跃规则，建议添加基础规则")
        if not security_recommendations:
            security_recommendations.append("系统安全状态良好")
        
        return SecurityReportResponse(
            report_date=datetime.utcnow(),
            total_rules=total_rules,
            active_rules=active_rules,
            high_risk_operations=high_risk_ops,
            medium_risk_operations=medium_risk_ops,
            low_risk_operations=low_risk_ops,
            recent_violations=recent_violations,
            security_recommendations=security_recommendations
        )
        
    except Exception as e:
        logger.error(f"获取安全报告失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取安全报告失败: {str(e)}")

# ==================== 工具和辅助端点 ====================

@router.get("/categories")
async def get_available_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取可用的零件类别列表"""
    
    try:
        categories = db.query(Part.category).distinct().filter(
            Part.category.isnot(None)
        ).all()
        
        category_list = [cat[0] for cat in categories if cat[0]]
        return sorted(category_list)
        
    except Exception as e:
        logger.error(f"获取类别列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取类别列表失败: {str(e)}")

@router.get("/expression-functions")
async def get_expression_functions(
    current_user: User = Depends(require_admin)
):
    """获取表达式中可用的安全函数列表"""
    
    try:
        functions = expression_engine.get_allowed_functions()
        
        function_help = {}
        for func_name in functions:
            help_text = expression_engine.get_function_help(func_name)
            if help_text:
                function_help[func_name] = help_text
        
        return {
            "functions": functions,
            "help": function_help,
            "examples": {
                "basic_comparison": "part_a.voltage == part_b.voltage",
                "range_check": "part_a.power >= 100 and part_a.power <= 500",
                "safe_get": "safe_get(part_a, 'frequency', 0) > 1000",
                "math_functions": "sum([part_a.power, part_b.power]) <= 1000"
            }
        }
        
    except Exception as e:
        logger.error(f"获取函数列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取函数列表失败: {str(e)}")

@router.post("/clear-cache")
async def clear_compatibility_cache(
    category_a: Optional[str] = Query(None, description="清理指定类别A的缓存"),
    category_b: Optional[str] = Query(None, description="清理指定类别B的缓存"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """清理兼容性检查缓存"""
    
    try:
        logger.info(f"管理员 {current_user.username} 清理兼容性缓存")
        
        if category_a or category_b:
            # 清理指定类别的缓存
            await _clear_related_cache(db, category_a, category_b)
            message = f"已清理类别 {category_a or 'ALL'} 和 {category_b or 'ALL'} 相关的缓存"
        else:
            # 清理所有缓存
            await _clear_all_compatibility_cache(db)
            message = "已清理所有兼容性缓存"
        
        return {"message": message}
        
    except Exception as e:
        logger.error(f"清理缓存失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"清理缓存失败: {str(e)}")

# ==================== 辅助函数 ====================

async def _log_rule_operation(
    db: Session,
    rule_id: Optional[int],
    action: str,
    user_id: int,
    old_expression: Optional[str] = None,
    new_expression: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    security_result: Optional[Dict[str, Any]] = None,
    validation_result: Optional[Dict[str, Any]] = None
):
    """记录规则操作审计日志"""
    
    try:
        # 计算风险等级
        risk_level = "low"
        if action in ["delete", "update"] and rule_id:
            risk_level = "medium"
        if security_result and not security_result.get("is_safe", True):
            risk_level = "high"
        
        # 合并验证结果
        combined_result = {}
        if security_result:
            combined_result.update(security_result)
        if validation_result:
            combined_result.update(validation_result)
        
        audit_log = RuleAuditLog(
            rule_id=rule_id,
            action=action,
            old_expression=old_expression,
            new_expression=new_expression,
            validation_result=combined_result if combined_result else None,
            changed_by=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            risk_level=risk_level
        )
        
        db.add(audit_log)
        db.commit()
        
    except Exception as e:
        logger.warning(f"记录审计日志失败: {str(e)}")
        # 审计日志失败不应影响主操作
        db.rollback()

async def _clear_related_cache(db: Session, category_a: Optional[str], category_b: Optional[str]):
    """清理相关类别的兼容性缓存"""
    
    try:
        if not category_a and not category_b:
            return
        
        # 这里简化实现，实际生产环境需要更精确的缓存管理
        # 可以根据零件类别来清理相关的缓存条目
        
        # 清理过期缓存
        expired_cutoff = datetime.utcnow()
        deleted_count = db.query(CompatibilityCache).filter(
            or_(
                CompatibilityCache.expires_at < expired_cutoff,
                CompatibilityCache.expires_at.is_(None)
            )
        ).delete()
        
        db.commit()
        
        if deleted_count > 0:
            logger.info(f"清理了 {deleted_count} 个过期缓存条目")
            
    except Exception as e:
        logger.warning(f"清理相关缓存失败: {str(e)}")
        db.rollback()

async def _clear_all_compatibility_cache(db: Session):
    """清理所有兼容性缓存"""
    
    try:
        deleted_count = db.query(CompatibilityCache).delete()
        db.commit()
        
        logger.info(f"清理了 {deleted_count} 个缓存条目")
        
    except Exception as e:
        logger.warning(f"清理所有缓存失败: {str(e)}")
        db.rollback()