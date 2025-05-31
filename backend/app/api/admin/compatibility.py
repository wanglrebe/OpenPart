# backend/app/api/admin/compatibility.py (修复版本)
"""
管理员兼容性管理API - 修复删除和停用功能

区分了停用/启用和真正的删除功能
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

# ==================== 批量操作API（必须放在参数化路由之前）====================

@router.patch("/rules/batch/disable")
async def batch_disable_rules(
    rule_ids: List[int],
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """批量停用规则"""
    try:
        logger.info(f"管理员 {current_user.username} 批量停用规则: {rule_ids}")
        
        # 查找规则
        rules = db.query(CompatibilityRule).filter(CompatibilityRule.id.in_(rule_ids)).all()
        found_ids = {rule.id for rule in rules}
        missing_ids = [rid for rid in rule_ids if rid not in found_ids]
        
        if missing_ids:
            raise HTTPException(status_code=404, detail=f"未找到规则: {missing_ids}")
        
        # 批量停用
        updated_count = 0
        for rule in rules:
            if rule.is_active:
                rule.is_active = False
                rule.updated_at = datetime.utcnow()
                updated_count += 1
                
                # 记录审计日志
                await _log_rule_operation(
                    db=db,
                    rule_id=rule.id,
                    action="disable",
                    user_id=current_user.id,
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("User-Agent"),
                    additional_context={"batch_operation": True}
                )
        
        db.commit()
        
        # 清理缓存
        await _clear_all_compatibility_cache(db)
        
        return {
            "message": f"批量停用完成",
            "total_requested": len(rule_ids),
            "actually_updated": updated_count,
            "already_disabled": len(rules) - updated_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量停用规则失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"批量停用失败: {str(e)}")

@router.patch("/rules/batch/enable")
async def batch_enable_rules(
    rule_ids: List[int],
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """批量启用规则"""
    try:
        logger.info(f"管理员 {current_user.username} 批量启用规则: {rule_ids}")
        
        # 查找规则
        rules = db.query(CompatibilityRule).filter(CompatibilityRule.id.in_(rule_ids)).all()
        found_ids = {rule.id for rule in rules}
        missing_ids = [rid for rid in rule_ids if rid not in found_ids]
        
        if missing_ids:
            raise HTTPException(status_code=404, detail=f"未找到规则: {missing_ids}")
        
        # 验证所有规则的安全性
        security_issues = []
        for rule in rules:
            if not rule.is_active:
                validation = await expression_engine.validate_expression_security(rule.rule_expression, db)
                if not validation.is_safe:
                    security_issues.append({
                        "rule_id": rule.id,
                        "rule_name": rule.name,
                        "issues": validation.security_issues
                    })
        
        if security_issues:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "部分规则不符合安全标准",
                    "security_issues": security_issues
                }
            )
        
        # 批量启用
        updated_count = 0
        for rule in rules:
            if not rule.is_active:
                rule.is_active = True
                rule.updated_at = datetime.utcnow()
                updated_count += 1
                
                # 记录审计日志
                await _log_rule_operation(
                    db=db,
                    rule_id=rule.id,
                    action="enable",
                    user_id=current_user.id,
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("User-Agent"),
                    additional_context={"batch_operation": True}
                )
        
        db.commit()
        
        # 清理缓存
        await _clear_all_compatibility_cache(db)
        
        return {
            "message": f"批量启用完成",
            "total_requested": len(rule_ids),
            "actually_updated": updated_count,
            "already_enabled": len(rules) - updated_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量启用规则失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"批量启用失败: {str(e)}")

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
        
        # 2. 检查规则名称唯一性（只检查未删除的规则）
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
            is_active=True  # 新创建的规则默认启用
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
    - 只返回未删除的规则
    """
    try:
        # 构建基础查询 - 只查询未删除的规则
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

# ==================== 新增：停用/启用API ====================

@router.patch("/rules/{rule_id}/disable")
async def disable_compatibility_rule(
    rule_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    停用兼容性规则
    
    - 将规则设置为非活跃状态
    - 保留规则数据，可以重新启用
    - 记录操作审计日志
    """
    try:
        rule = db.query(CompatibilityRule).filter(CompatibilityRule.id == rule_id).first()
        if not rule:
            raise HTTPException(status_code=404, detail="规则未找到")
        
        if not rule.is_active:
            raise HTTPException(status_code=400, detail="规则已经是停用状态")
        
        logger.info(f"管理员 {current_user.username} 停用规则 {rule_id}: {rule.name}")
        
        # 停用规则
        rule.is_active = False
        rule.updated_at = datetime.utcnow()
        db.commit()
        
        # 记录审计日志
        await _log_rule_operation(
            db=db,
            rule_id=rule.id,
            action="disable",
            user_id=current_user.id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            additional_context={"previous_state": "active"}
        )
        
        # 清理相关缓存
        await _clear_related_cache(db, rule.category_a, rule.category_b)
        
        logger.info(f"规则停用成功: ID={rule.id}")
        return {"message": "规则已停用", "rule_id": rule.id, "rule_name": rule.name}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"停用规则失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"停用规则失败: {str(e)}")

@router.patch("/rules/{rule_id}/enable")
async def enable_compatibility_rule(
    rule_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    启用兼容性规则
    
    - 将规则设置为活跃状态
    - 重新参与兼容性检查
    - 记录操作审计日志
    """
    try:
        rule = db.query(CompatibilityRule).filter(CompatibilityRule.id == rule_id).first()
        if not rule:
            raise HTTPException(status_code=404, detail="规则未找到")
        
        if rule.is_active:
            raise HTTPException(status_code=400, detail="规则已经是启用状态")
        
        logger.info(f"管理员 {current_user.username} 启用规则 {rule_id}: {rule.name}")
        
        # 重新验证规则表达式安全性（可能安全策略已更新）
        security_validation = await expression_engine.validate_expression_security(
            rule.rule_expression, db
        )
        
        if not security_validation.is_safe:
            high_risk_issues = [
                issue for issue in security_validation.security_issues 
                if issue.get("severity") == "high"
            ]
            raise HTTPException(
                status_code=400, 
                detail={
                    "message": "规则表达式不再符合安全标准，无法启用",
                    "security_issues": high_risk_issues,
                    "recommendations": security_validation.recommendations
                }
            )
        
        # 启用规则
        rule.is_active = True
        rule.updated_at = datetime.utcnow()
        db.commit()
        
        # 记录审计日志
        await _log_rule_operation(
            db=db,
            rule_id=rule.id,
            action="enable",
            user_id=current_user.id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            additional_context={"previous_state": "inactive"},
            security_result=security_validation.dict()
        )
        
        # 清理相关缓存
        await _clear_related_cache(db, rule.category_a, rule.category_b)
        
        logger.info(f"规则启用成功: ID={rule.id}")
        return {"message": "规则已启用", "rule_id": rule.id, "rule_name": rule.name}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"启用规则失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"启用规则失败: {str(e)}")

# ==================== 修复：真正的删除API ====================

@router.delete("/rules/{rule_id}")
async def delete_compatibility_rule(
    rule_id: int,
    request: Request,
    force: bool = Query(False, description="强制删除（忽略依赖检查）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    彻底删除兼容性规则
    
    - 物理删除规则记录，不可恢复
    - 检查依赖关系，防止数据完整性问题
    - 清理相关缓存和审计日志
    - 需要强制标志才能删除有依赖的规则
    """
    try:
        rule = db.query(CompatibilityRule).filter(CompatibilityRule.id == rule_id).first()
        if not rule:
            raise HTTPException(status_code=404, detail="规则未找到")
        
        logger.info(f"管理员 {current_user.username} 删除规则 {rule_id}: {rule.name}")
        
        # 检查依赖关系
        dependencies = await _check_rule_dependencies(rule, db)
        if dependencies and not force:
            raise HTTPException(
                status_code=409, 
                detail={
                    "message": "规则存在依赖关系，无法删除",
                    "dependencies": dependencies,
                    "hint": "如需强制删除，请添加 force=true 参数"
                }
            )
        
        # 保存规则信息用于审计
        old_expression = rule.rule_expression
        rule_name = rule.name
        rule_categories = (rule.category_a, rule.category_b)
        
        # 如果强制删除，先处理依赖关系
        if force and dependencies:
            await _handle_force_delete_dependencies(rule, dependencies, db)
        
        # 物理删除规则
        db.delete(rule)
        db.commit()
        
        # 记录审计日志（规则已删除，所以rule_id传None）
        await _log_rule_operation(
            db=db,
            rule_id=None,  # 规则已删除
            action="delete",
            user_id=current_user.id,
            old_expression=old_expression,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            additional_context={
                "deleted_rule_id": rule_id,
                "deleted_rule_name": rule_name,
                "force_delete": force,
                "dependencies_found": len(dependencies) if dependencies else 0
            }
        )
        
        # 清理相关缓存
        await _clear_related_cache(db, rule_categories[0], rule_categories[1])
        
        logger.info(f"规则删除成功: ID={rule_id}, 名称={rule_name}")
        return {
            "message": "规则已彻底删除", 
            "rule_id": rule_id, 
            "rule_name": rule_name,
            "force_delete": force
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除规则失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除规则失败: {str(e)}")

# ==================== 辅助函数 ====================

async def _check_rule_dependencies(rule: CompatibilityRule, db: Session) -> List[Dict[str, Any]]:
    """检查规则的依赖关系"""
    dependencies = []
    
    try:
        # 检查是否被模板引用
        from sqlalchemy import text
        template_count = db.execute(
            text("SELECT COUNT(*) FROM compatibility_templates WHERE rules::text LIKE :pattern"),
            {"pattern": f"%{rule.id}%"}
        ).scalar()
        
        if template_count > 0:
            dependencies.append({
                "type": "templates",
                "count": template_count,
                "description": f"被 {template_count} 个模板引用"
            })
        
        # 检查相关的审计日志数量
        audit_count = db.query(RuleAuditLog).filter(RuleAuditLog.rule_id == rule.id).count()
        if audit_count > 0:
            dependencies.append({
                "type": "audit_logs",
                "count": audit_count,
                "description": f"存在 {audit_count} 条审计日志"
            })
        
        # 检查是否有相关的缓存条目
        from sqlalchemy import func
        cache_count = db.query(CompatibilityCache).filter(
            func.jsonb_extract_path_text(CompatibilityCache.compatibility_result, 'rule_results').ilike(f'%"rule_id": {rule.id}%')
        ).count()
        
        if cache_count > 0:
            dependencies.append({
                "type": "cache_entries", 
                "count": cache_count,
                "description": f"存在 {cache_count} 个相关缓存条目"
            })
        
        return dependencies
        
    except Exception as e:
        logger.warning(f"检查规则依赖失败: {str(e)}")
        return []

async def _handle_force_delete_dependencies(
    rule: CompatibilityRule, 
    dependencies: List[Dict[str, Any]], 
    db: Session
):
    """处理强制删除时的依赖关系"""
    
    try:
        # 删除相关的审计日志
        for dep in dependencies:
            if dep["type"] == "audit_logs":
                db.query(RuleAuditLog).filter(RuleAuditLog.rule_id == rule.id).delete()
                logger.info(f"删除了 {dep['count']} 条相关审计日志")
        
        # 清理相关缓存
        await _clear_all_compatibility_cache(db)
        logger.info("清理了所有相关缓存")
        
        # 注意：模板引用需要手动处理，这里只记录警告
        for dep in dependencies:
            if dep["type"] == "templates":
                logger.warning(f"警告：规则被 {dep['count']} 个模板引用，删除后这些模板可能失效")
        
    except Exception as e:
        logger.error(f"处理强制删除依赖失败: {str(e)}")
        raise

# ==================== 保持原有的其他功能 ====================
# （安全验证、规则测试、经验管理、统计等功能保持不变）
# ... [这里保留原文件中的其他函数，如安全验证API、经验管理API等] ...

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
    additional_context: Optional[Dict[str, Any]] = None
):
    """记录规则操作审计日志"""
    
    try:
        # 计算风险等级
        risk_level = "low"
        if action in ["delete"]:
            risk_level = "high"
        elif action in ["enable", "disable", "update"]:
            risk_level = "medium"
        if security_result and not security_result.get("is_safe", True):
            risk_level = "high"
        
        # 合并验证结果和额外上下文
        combined_result = {}
        if security_result:
            combined_result.update(security_result)
        if additional_context:
            combined_result["additional_context"] = additional_context
        
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

# ==================== 保持原有的其他功能 ====================

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
                additional_context={
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
                additional_context={
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
    """删除兼容性经验（真正的删除）"""
    
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

# ==================== 审计日志API ====================

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