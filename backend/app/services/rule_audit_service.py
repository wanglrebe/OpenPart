# backend/app/services/rule_audit_service.py
"""
规则审计服务

提供兼容性规则的操作审计、安全监控和风险评估功能
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.models.compatibility import RuleAuditLog, CompatibilityRule, ExpressionSecurityCache
from app.models.part import Part
from app.schemas.compatibility import (
    AuditLogResponse, SecurityReportResponse, RiskLevel
)

logger = logging.getLogger(__name__)

class RuleAuditService:
    """规则审计服务类"""
    
    def __init__(self):
        self.high_risk_actions = {"delete", "update"}
        self.security_scan_interval_hours = 24
        
    async def log_rule_operation(
        self,
        db: Session,
        rule_id: Optional[int],
        action: str,
        user_id: int,
        old_expression: Optional[str] = None,
        new_expression: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        validation_result: Optional[Dict[str, Any]] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> RuleAuditLog:
        """
        记录规则操作审计日志
        
        Args:
            db: 数据库会话
            rule_id: 规则ID
            action: 操作类型 (create/update/delete/test/validate)
            user_id: 操作用户ID
            old_expression: 旧表达式
            new_expression: 新表达式
            ip_address: 用户IP地址
            user_agent: 用户代理
            validation_result: 验证结果
            additional_context: 额外上下文信息
            
        Returns:
            RuleAuditLog: 创建的审计日志记录
        """
        try:
            # 计算风险等级
            risk_level = self._calculate_operation_risk_level(
                action, old_expression, new_expression, validation_result
            )
            
            # 合并验证结果和额外上下文
            combined_result = {}
            if validation_result:
                combined_result.update(validation_result)
            if additional_context:
                combined_result["additional_context"] = additional_context
            
            # 创建审计日志记录
            audit_log = RuleAuditLog(
                rule_id=rule_id,
                action=action,
                old_expression=old_expression,
                new_expression=new_expression,
                validation_result=combined_result if combined_result else None,
                changed_by=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                risk_level=risk_level.value
            )
            
            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)
            
            # 记录日志
            logger.info(f"审计日志记录成功: 操作={action}, 用户={user_id}, 风险={risk_level.value}")
            
            # 如果是高风险操作，触发额外处理
            if risk_level == RiskLevel.HIGH:
                await self._handle_high_risk_operation(db, audit_log)
            
            return audit_log
            
        except Exception as e:
            logger.error(f"记录审计日志失败: {str(e)}")
            db.rollback()
            raise

    async def get_audit_logs(
        self,
        db: Session,
        days: int = 30,
        action: Optional[str] = None,
        risk_level: Optional[str] = None,
        user_id: Optional[int] = None,
        rule_id: Optional[int] = None,
        page: int = 1,
        size: int = 50
    ) -> Tuple[List[RuleAuditLog], int]:
        """
        获取审计日志列表
        
        Args:
            db: 数据库会话
            days: 查询天数
            action: 操作类型筛选
            risk_level: 风险等级筛选
            user_id: 用户ID筛选
            rule_id: 规则ID筛选
            page: 页码
            size: 每页数量
            
        Returns:
            Tuple[List[RuleAuditLog], int]: (审计日志列表, 总数)
        """
        try:
            # 构建基础查询
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = db.query(RuleAuditLog).filter(
                RuleAuditLog.changed_at >= cutoff_date
            )
            
            # 应用筛选条件
            if action:
                query = query.filter(RuleAuditLog.action == action)
            if risk_level:
                query = query.filter(RuleAuditLog.risk_level == risk_level)
            if user_id:
                query = query.filter(RuleAuditLog.changed_by == user_id)
            if rule_id:
                query = query.filter(RuleAuditLog.rule_id == rule_id)
            
            # 计算总数
            total = query.count()
            
            # 应用排序和分页
            logs = query.order_by(desc(RuleAuditLog.changed_at))\
                      .offset((page - 1) * size)\
                      .limit(size)\
                      .all()
            
            return logs, total
            
        except Exception as e:
            logger.error(f"获取审计日志失败: {str(e)}")
            raise

    async def get_security_violations(
        self,
        db: Session,
        days: int = 30,
        min_risk_level: RiskLevel = RiskLevel.MEDIUM
    ) -> List[RuleAuditLog]:
        """
        获取安全违规操作记录
        
        Args:
            db: 数据库会话
            days: 查询天数
            min_risk_level: 最低风险等级
            
        Returns:
            List[RuleAuditLog]: 违规操作列表
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # 定义风险等级筛选条件
            risk_levels = []
            if min_risk_level == RiskLevel.LOW:
                risk_levels = ["low", "medium", "high"]
            elif min_risk_level == RiskLevel.MEDIUM:
                risk_levels = ["medium", "high"]
            else:
                risk_levels = ["high"]
            
            violations = db.query(RuleAuditLog).filter(
                RuleAuditLog.changed_at >= cutoff_date,
                RuleAuditLog.risk_level.in_(risk_levels)
            ).order_by(desc(RuleAuditLog.changed_at)).limit(100).all()
            
            return violations
            
        except Exception as e:
            logger.error(f"获取安全违规记录失败: {str(e)}")
            raise

    async def generate_security_report(
        self,
        db: Session,
        days: int = 30
    ) -> SecurityReportResponse:
        """
        生成安全状态报告
        
        Args:
            db: 数据库会话
            days: 报告周期（天）
            
        Returns:
            SecurityReportResponse: 安全报告
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # 基础统计
            total_rules = db.query(CompatibilityRule).count()
            active_rules = db.query(CompatibilityRule).filter(
                CompatibilityRule.is_active == True
            ).count()
            
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
            
            # 获取最近的违规操作
            recent_violations = await self.get_security_violations(
                db, days=7, min_risk_level=RiskLevel.MEDIUM
            )
            
            # 生成安全建议
            recommendations = await self._generate_security_recommendations(
                db, high_risk_ops, medium_risk_ops, active_rules, total_rules
            )
            
            # 构建报告
            report = SecurityReportResponse(
                report_date=datetime.utcnow(),
                total_rules=total_rules,
                active_rules=active_rules,
                high_risk_operations=high_risk_ops,
                medium_risk_operations=medium_risk_ops,
                low_risk_operations=low_risk_ops,
                recent_violations=recent_violations[:10],  # 最多返回10个
                security_recommendations=recommendations
            )
            
            logger.info(f"安全报告生成完成: 高风险操作={high_risk_ops}, 中风险操作={medium_risk_ops}")
            return report
            
        except Exception as e:
            logger.error(f"生成安全报告失败: {str(e)}")
            raise

    async def get_operation_statistics(
        self,
        db: Session,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        获取操作统计信息
        
        Args:
            db: 数据库会话
            days: 统计周期（天）
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # 按操作类型统计
            action_stats = db.query(
                RuleAuditLog.action,
                func.count(RuleAuditLog.id).label('count')
            ).filter(
                RuleAuditLog.changed_at >= cutoff_date
            ).group_by(RuleAuditLog.action).all()
            
            # 按风险等级统计
            risk_stats = db.query(
                RuleAuditLog.risk_level,
                func.count(RuleAuditLog.id).label('count')
            ).filter(
                RuleAuditLog.changed_at >= cutoff_date
            ).group_by(RuleAuditLog.risk_level).all()
            
            # 按用户统计（Top 10）
            user_stats = db.query(
                RuleAuditLog.changed_by,
                func.count(RuleAuditLog.id).label('count')
            ).filter(
                RuleAuditLog.changed_at >= cutoff_date
            ).group_by(RuleAuditLog.changed_by)\
             .order_by(desc(func.count(RuleAuditLog.id)))\
             .limit(10).all()
            
            # 按时间统计（每日操作数）
            daily_stats = db.query(
                func.date(RuleAuditLog.changed_at).label('date'),
                func.count(RuleAuditLog.id).label('count')
            ).filter(
                RuleAuditLog.changed_at >= cutoff_date
            ).group_by(func.date(RuleAuditLog.changed_at))\
             .order_by(func.date(RuleAuditLog.changed_at)).all()
            
            return {
                "period_days": days,
                "action_statistics": [
                    {"action": stat.action, "count": stat.count}
                    for stat in action_stats
                ],
                "risk_statistics": [
                    {"risk_level": stat.risk_level, "count": stat.count}
                    for stat in risk_stats
                ],
                "user_statistics": [
                    {"user_id": stat.changed_by, "operation_count": stat.count}
                    for stat in user_stats
                ],
                "daily_statistics": [
                    {"date": stat.date.isoformat(), "count": stat.count}
                    for stat in daily_stats
                ],
                "summary": {
                    "total_operations": sum(stat.count for stat in action_stats),
                    "unique_users": len(user_stats),
                    "active_days": len(daily_stats),
                    "avg_operations_per_day": sum(stat.count for stat in daily_stats) / max(len(daily_stats), 1)
                }
            }
            
        except Exception as e:
            logger.error(f"获取操作统计失败: {str(e)}")
            raise

    async def detect_suspicious_activity(
        self,
        db: Session,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        检测可疑活动
        
        Args:
            db: 数据库会话
            hours: 检测时间范围（小时）
            
        Returns:
            List[Dict[str, Any]]: 可疑活动列表
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            suspicious_activities = []
            
            # 1. 检测频繁的高风险操作
            high_risk_users = db.query(
                RuleAuditLog.changed_by,
                func.count(RuleAuditLog.id).label('count')
            ).filter(
                RuleAuditLog.changed_at >= cutoff_time,
                RuleAuditLog.risk_level == "high"
            ).group_by(RuleAuditLog.changed_by)\
             .having(func.count(RuleAuditLog.id) >= 5)\
             .all()
            
            for user_stat in high_risk_users:
                suspicious_activities.append({
                    "type": "frequent_high_risk_operations",
                    "user_id": user_stat.changed_by,
                    "count": user_stat.count,
                    "severity": "high",
                    "description": f"用户在{hours}小时内执行了{user_stat.count}次高风险操作"
                })
            
            # 2. 检测异常的删除操作
            delete_operations = db.query(RuleAuditLog).filter(
                RuleAuditLog.changed_at >= cutoff_time,
                RuleAuditLog.action == "delete"
            ).count()
            
            if delete_operations >= 3:
                suspicious_activities.append({
                    "type": "excessive_deletions",
                    "count": delete_operations,
                    "severity": "medium",
                    "description": f"在{hours}小时内发生了{delete_operations}次删除操作"
                })
            
            # 3. 检测来自同一IP的大量操作
            ip_operations = db.query(
                RuleAuditLog.ip_address,
                func.count(RuleAuditLog.id).label('count')
            ).filter(
                RuleAuditLog.changed_at >= cutoff_time,
                RuleAuditLog.ip_address.isnot(None)
            ).group_by(RuleAuditLog.ip_address)\
             .having(func.count(RuleAuditLog.id) >= 20)\
             .all()
            
            for ip_stat in ip_operations:
                suspicious_activities.append({
                    "type": "high_volume_from_ip",
                    "ip_address": ip_stat.ip_address,
                    "count": ip_stat.count,
                    "severity": "medium",
                    "description": f"IP {ip_stat.ip_address} 在{hours}小时内执行了{ip_stat.count}次操作"
                })
            
            # 4. 检测安全验证失败的操作
            security_failures = db.query(RuleAuditLog).filter(
                RuleAuditLog.changed_at >= cutoff_time,
                RuleAuditLog.validation_result.op('->>')('is_safe') == 'false'
            ).count()
            
            if security_failures >= 3:
                suspicious_activities.append({
                    "type": "security_validation_failures",
                    "count": security_failures,
                    "severity": "high",
                    "description": f"在{hours}小时内发生了{security_failures}次安全验证失败"
                })
            
            return suspicious_activities
            
        except Exception as e:
            logger.error(f"检测可疑活动失败: {str(e)}")
            return []

    async def cleanup_old_audit_logs(
        self,
        db: Session,
        retention_days: int = 365
    ) -> int:
        """
        清理旧的审计日志
        
        Args:
            db: 数据库会话
            retention_days: 保留天数
            
        Returns:
            int: 删除的记录数
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            deleted_count = db.query(RuleAuditLog).filter(
                RuleAuditLog.changed_at < cutoff_date
            ).delete()
            
            db.commit()
            
            logger.info(f"清理了 {deleted_count} 条超过 {retention_days} 天的审计日志")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理审计日志失败: {str(e)}")
            db.rollback()
            raise

    async def export_audit_logs(
        self,
        db: Session,
        start_date: datetime,
        end_date: datetime,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        导出审计日志
        
        Args:
            db: 数据库会话
            start_date: 开始日期
            end_date: 结束日期
            format: 导出格式 (json/csv)
            
        Returns:
            Dict[str, Any]: 导出数据
        """
        try:
            logs = db.query(RuleAuditLog).filter(
                and_(
                    RuleAuditLog.changed_at >= start_date,
                    RuleAuditLog.changed_at <= end_date
                )
            ).order_by(RuleAuditLog.changed_at).all()
            
            if format.lower() == "csv":
                # CSV格式导出
                export_data = {
                    "format": "csv",
                    "headers": [
                        "id", "rule_id", "action", "old_expression", "new_expression",
                        "changed_by", "changed_at", "ip_address", "risk_level"
                    ],
                    "data": [
                        [
                            log.id, log.rule_id, log.action, log.old_expression,
                            log.new_expression, log.changed_by, log.changed_at.isoformat(),
                            log.ip_address, log.risk_level
                        ]
                        for log in logs
                    ]
                }
            else:
                # JSON格式导出
                export_data = {
                    "format": "json",
                    "metadata": {
                        "export_date": datetime.utcnow().isoformat(),
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "total_records": len(logs)
                    },
                    "data": [
                        {
                            "id": log.id,
                            "rule_id": log.rule_id,
                            "action": log.action,
                            "old_expression": log.old_expression,
                            "new_expression": log.new_expression,
                            "validation_result": log.validation_result,
                            "changed_by": log.changed_by,
                            "changed_at": log.changed_at.isoformat(),
                            "ip_address": log.ip_address,
                            "user_agent": log.user_agent,
                            "risk_level": log.risk_level
                        }
                        for log in logs
                    ]
                }
            
            logger.info(f"导出了 {len(logs)} 条审计日志 (格式: {format})")
            return export_data
            
        except Exception as e:
            logger.error(f"导出审计日志失败: {str(e)}")
            raise

    # ==================== 私有方法 ====================

    def _calculate_operation_risk_level(
        self,
        action: str,
        old_expression: Optional[str],
        new_expression: Optional[str],
        validation_result: Optional[Dict[str, Any]]
    ) -> RiskLevel:
        """计算操作风险等级"""
        
        # 高风险操作
        if action in ["delete"]:
            return RiskLevel.HIGH
        
        # 安全验证失败
        if validation_result and not validation_result.get("is_safe", True):
            return RiskLevel.HIGH
        
        # 表达式更新操作
        if action == "update" and old_expression != new_expression:
            return RiskLevel.MEDIUM
        
        # 创建新规则
        if action == "create":
            return RiskLevel.MEDIUM
        
        # 测试和验证操作
        if action in ["test", "validate"]:
            return RiskLevel.LOW
        
        return RiskLevel.LOW

    async def _handle_high_risk_operation(
        self,
        db: Session,
        audit_log: RuleAuditLog
    ):
        """处理高风险操作"""
        
        try:
            # 记录警告日志
            logger.warning(
                f"高风险操作检测: 用户={audit_log.changed_by}, "
                f"操作={audit_log.action}, 规则={audit_log.rule_id}"
            )
            
            # 这里可以添加更多高风险操作的处理逻辑：
            # 1. 发送通知给管理员
            # 2. 临时锁定用户账户
            # 3. 触发额外的安全检查
            # 4. 记录到安全事件日志
            
            # 示例：检查是否需要额外审查
            recent_high_risk = db.query(RuleAuditLog).filter(
                RuleAuditLog.changed_by == audit_log.changed_by,
                RuleAuditLog.risk_level == "high",
                RuleAuditLog.changed_at >= datetime.utcnow() - timedelta(hours=1)
            ).count()
            
            if recent_high_risk >= 3:
                logger.critical(
                    f"用户 {audit_log.changed_by} 在1小时内执行了 {recent_high_risk} 次高风险操作，"
                    "建议立即检查！"
                )
            
        except Exception as e:
            logger.error(f"处理高风险操作失败: {str(e)}")

    async def _generate_security_recommendations(
        self,
        db: Session,
        high_risk_ops: int,
        medium_risk_ops: int,
        active_rules: int,
        total_rules: int
    ) -> List[str]:
        """生成安全建议"""
        
        recommendations = []
        
        # 基于高风险操作的建议
        if high_risk_ops > 0:
            recommendations.append(f"发现 {high_risk_ops} 个高风险操作，建议立即审查相关操作日志")
        
        if high_risk_ops >= 5:
            recommendations.append("高风险操作频繁，建议加强权限管理和操作审批流程")
        
        # 基于中风险操作的建议
        if medium_risk_ops > 20:
            recommendations.append("中风险操作较多，建议定期审查规则变更和创建操作")
        
        # 基于规则状态的建议
        if active_rules == 0:
            recommendations.append("系统中没有活跃规则，建议配置基础兼容性规则")
        elif active_rules < 5:
            recommendations.append("活跃规则较少，建议增加更多兼容性规则以提高系统覆盖率")
        
        inactive_rules = total_rules - active_rules
        if inactive_rules > active_rules:
            recommendations.append("非活跃规则数量较多，建议清理不必要的规则")
        
        # 安全最佳实践建议
        if not recommendations:
            recommendations.extend([
                "系统安全状态良好，建议继续保持当前的安全实践",
                "定期审查审计日志，监控异常操作模式",
                "确保所有管理员账户使用强密码和双因素认证",
                "定期备份兼容性规则和配置数据"
            ])
        else:
            recommendations.extend([
                "建议设置自动化监控告警，及时发现异常操作",
                "考虑实施操作审批流程，特别是对高风险操作",
                "定期进行安全培训，提高管理员的安全意识"
            ])
        
        return recommendations

    async def get_rule_change_history(
        self,
        db: Session,
        rule_id: int,
        limit: int = 50
    ) -> List[RuleAuditLog]:
        """
        获取特定规则的变更历史
        
        Args:
            db: 数据库会话
            rule_id: 规则ID
            limit: 返回记录数限制
            
        Returns:
            List[RuleAuditLog]: 变更历史列表
        """
        try:
            history = db.query(RuleAuditLog).filter(
                RuleAuditLog.rule_id == rule_id
            ).order_by(desc(RuleAuditLog.changed_at))\
             .limit(limit).all()
            
            return history
            
        except Exception as e:
            logger.error(f"获取规则变更历史失败: {str(e)}")
            raise

    async def validate_operation_permission(
        self,
        db: Session,
        user_id: int,
        action: str,
        rule_id: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        验证操作权限
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            action: 操作类型
            rule_id: 规则ID（可选）
            
        Returns:
            Tuple[bool, Optional[str]]: (是否允许, 拒绝原因)
        """
        try:
            # 检查用户近期的操作频率
            recent_time = datetime.utcnow() - timedelta(minutes=10)
            recent_operations = db.query(RuleAuditLog).filter(
                RuleAuditLog.changed_by == user_id,
                RuleAuditLog.changed_at >= recent_time
            ).count()
            
            # 操作频率限制
            if action in ["delete"] and recent_operations >= 5:
                return False, "操作过于频繁，请稍后再试"
            
            if recent_operations >= 20:
                return False, "操作次数超过限制，请稍后再试"
            
            # 检查是否有正在进行的高风险操作
            recent_high_risk = db.query(RuleAuditLog).filter(
                RuleAuditLog.changed_by == user_id,
                RuleAuditLog.risk_level == "high",
                RuleAuditLog.changed_at >= datetime.utcnow() - timedelta(hours=1)
            ).count()
            
            if action == "delete" and recent_high_risk >= 3:
                return False, "近期高风险操作过多，暂时限制删除操作"
            
            return True, None
            
        except Exception as e:
            logger.error(f"验证操作权限失败: {str(e)}")
            return False, "权限验证失败"


# 全局审计服务实例
rule_audit_service = RuleAuditService()