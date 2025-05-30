# backend/app/services/compatibility_engine.py
"""
兼容性检查引擎核心服务

负责执行兼容性规则检查、计算兼容性评分、缓存管理等核心功能
"""

import time
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.compatibility import (
    CompatibilityRule, CompatibilityExperience, CompatibilityCache,
    get_compatibility_experience_by_parts, get_active_rules_for_categories,
    create_part_ids_hash
)
from app.models.part import Part
from app.schemas.compatibility import (
    CompatibilityCheckRequest, CompatibilityCheckResponse,
    CompatibilitySearchRequest, CompatibilitySearchResponse,
    PartCompatibilityResult, CompatibilityMatch, RuleResult,
    CompatibilityGrade, CompatibilityStatus
)
from app.services.safe_expression_parser import SafeExpressionEngine
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class CompatibilityEngine:
    """兼容性检查引擎"""
    
    def __init__(self):
        self.expression_engine = SafeExpressionEngine()
        self.cache_ttl_hours = 24  # 缓存24小时
        
    async def check_compatibility(
        self, 
        request: CompatibilityCheckRequest, 
        db: Session
    ) -> CompatibilityCheckResponse:
        """
        检查多个零件的兼容性
        
        Args:
            request: 兼容性检查请求
            db: 数据库会话
            
        Returns:
            CompatibilityCheckResponse: 兼容性检查结果
        """
        start_time = time.time()
        
        try:
            # 检查缓存
            cached_result = None
            if request.include_cache:
                cached_result = await self._get_cached_result(request.part_ids, db)
                if cached_result:
                    logger.info(f"返回缓存的兼容性检查结果，零件: {request.part_ids}")
                    return cached_result
            
            # 获取零件信息
            parts = await self._get_parts_info(request.part_ids, db)
            if len(parts) != len(request.part_ids):
                missing_ids = set(request.part_ids) - {p.id for p in parts}
                raise ValueError(f"未找到零件: {list(missing_ids)}")
            
            # 执行兼容性检查
            part_combinations = []
            warnings = []
            recommendations = []
            
            # 检查每对零件的兼容性
            for i, part_a in enumerate(parts):
                for j, part_b in enumerate(parts[i+1:], i+1):
                    combination_result = await self._check_part_pair_compatibility(
                        part_a, part_b, db, request.detail_level
                    )
                    part_combinations.append(combination_result)
                    
                    # 收集警告和建议
                    warnings.extend(combination_result.warnings)
            
            # 计算整体兼容性
            overall_score, overall_grade, overall_compatible = self._calculate_overall_compatibility(
                part_combinations
            )
            
            # 生成建议
            recommendations = self._generate_recommendations(part_combinations, parts)
            
            # 构建响应
            response = CompatibilityCheckResponse(
                success=True,
                overall_compatibility_grade=overall_grade,
                overall_score=overall_score,
                is_overall_compatible=overall_compatible,
                part_combinations=part_combinations,
                execution_time=time.time() - start_time,
                cached=False,
                warnings=list(set(warnings)),  # 去重
                recommendations=recommendations
            )
            
            # 缓存结果
            if request.include_cache:
                await self._cache_result(request.part_ids, response, db)
            
            logger.info(f"兼容性检查完成，零件: {request.part_ids}, 整体评分: {overall_score}")
            return response
            
        except Exception as e:
            logger.error(f"兼容性检查失败: {str(e)}")
            raise

    async def search_compatible_parts(
        self, 
        request: CompatibilitySearchRequest, 
        db: Session
    ) -> CompatibilitySearchResponse:
        """
        搜索与指定零件兼容的其他零件
        
        Args:
            request: 兼容性搜索请求
            db: 数据库会话
            
        Returns:
            CompatibilitySearchResponse: 搜索结果
        """
        start_time = time.time()
        
        try:
            # 获取已选择的零件信息
            selected_parts = await self._get_parts_info(request.selected_parts, db)
            if len(selected_parts) != len(request.selected_parts):
                missing_ids = set(request.selected_parts) - {p.id for p in selected_parts}
                raise ValueError(f"未找到零件: {list(missing_ids)}")
            
            # 构建候选零件查询
            candidates_query = db.query(Part).filter(
                ~Part.id.in_(request.selected_parts)  # 排除已选择的零件
            )
            
            # 按目标类别筛选
            if request.target_categories:
                candidates_query = candidates_query.filter(
                    Part.category.in_(request.target_categories)
                )
            
            candidate_parts = candidates_query.limit(1000).all()  # 限制候选数量避免性能问题
            
            # 检查每个候选零件与已选零件的兼容性
            matches = []
            for candidate in candidate_parts:
                match_result = await self._evaluate_candidate_compatibility(
                    candidate, selected_parts, request, db
                )
                
                if match_result and match_result.compatibility_score >= request.min_compatibility_score:
                    matches.append(match_result)
            
            # 按兼容性评分排序
            matches.sort(key=lambda x: (x.compatibility_score, x.confidence_level), reverse=True)
            
            # 限制返回结果数量
            matches = matches[:request.limit]
            
            response = CompatibilitySearchResponse(
                success=True,
                matches=matches,
                total_found=len(matches),
                search_criteria={
                    "selected_parts": request.selected_parts,
                    "target_categories": request.target_categories,
                    "min_score": request.min_compatibility_score
                },
                execution_time=time.time() - start_time,
                recommendations=self._generate_search_recommendations(matches, selected_parts)
            )
            
            logger.info(f"兼容性搜索完成，找到 {len(matches)} 个匹配零件")
            return response
            
        except Exception as e:
            logger.error(f"兼容性搜索失败: {str(e)}")
            raise

    async def _check_part_pair_compatibility(
        self, 
        part_a: Part, 
        part_b: Part, 
        db: Session,
        detail_level: str = "standard"
    ) -> PartCompatibilityResult:
        """检查两个零件之间的兼容性"""
        
        # 检查是否有经验数据
        experience = get_compatibility_experience_by_parts(db, part_a.id, part_b.id)
        
        # 获取适用的规则
        rules = get_active_rules_for_categories(db, part_a.category or "", part_b.category or "")
        
        # 执行规则检查
        rule_results = []
        for rule in rules:
            rule_result = await self._execute_rule(rule, part_a, part_b)
            rule_results.append(rule_result)
        
        # 计算兼容性评分
        score, grade, is_compatible = self._calculate_pair_compatibility_score(
            rule_results, experience
        )
        
        # 生成警告
        warnings = self._generate_pair_warnings(rule_results, experience)
        
        return PartCompatibilityResult(
            part_a_id=part_a.id,
            part_b_id=part_b.id,
            part_a_name=part_a.name,
            part_b_name=part_b.name,
            compatibility_grade=grade,
            compatibility_score=score,
            is_compatible=is_compatible,
            rule_results=rule_results if detail_level in ["standard", "detailed"] else [],
            experience_data=self._convert_experience_to_response(experience) if experience else None,
            warnings=warnings
        )

    async def _execute_rule(
        self, 
        rule: CompatibilityRule, 
        part_a: Part, 
        part_b: Part
    ) -> RuleResult:
        """执行单个兼容性规则"""
        
        start_time = time.time()
        
        try:
            # 准备执行上下文
            context = {
                'part_a': self._part_to_context(part_a),
                'part_b': self._part_to_context(part_b)
            }
            
            # 执行表达式
            result = await self.expression_engine.execute_safe_expression(
                rule.rule_expression, context
            )
            
            execution_time = time.time() - start_time
            
            return RuleResult(
                rule_id=rule.id,
                rule_name=rule.name,
                passed=bool(result),
                score=float(rule.weight if result else 0),
                weight=rule.weight,
                is_blocking=rule.is_blocking,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"规则执行失败 [规则ID: {rule.id}]: {str(e)}")
            return RuleResult(
                rule_id=rule.id,
                rule_name=rule.name,
                passed=False,
                score=0.0,
                weight=rule.weight,
                is_blocking=rule.is_blocking,
                error_message=str(e),
                execution_time=time.time() - start_time
            )

    def _part_to_context(self, part: Part) -> Dict[str, Any]:
        """将零件对象转换为规则执行上下文"""
        
        context = {
            'id': part.id,
            'name': part.name,
            'category': part.category or "",
            'description': part.description or ""
        }
        
        # 添加属性字段
        if part.properties:
            for key, value in part.properties.items():
                # 清理属性名，确保可以作为变量名使用
                clean_key = self._clean_property_name(key)
                context[clean_key] = value
                
                # 同时保留原始键名，支持中文属性名
                context[key] = value
        
        return context

    def _clean_property_name(self, name: str) -> str:
        """清理属性名，使其可以作为变量名使用"""
        import re
        
        # 移除特殊字符，只保留字母、数字和下划线
        clean_name = re.sub(r'[^a-zA-Z0-9_\u4e00-\u9fff]', '_', name)
        
        # 确保以字母或下划线开头
        if clean_name and clean_name[0].isdigit():
            clean_name = f"prop_{clean_name}"
        
        return clean_name or "unknown_prop"

    def _calculate_pair_compatibility_score(
        self, 
        rule_results: List[RuleResult], 
        experience: Optional[CompatibilityExperience]
    ) -> Tuple[int, CompatibilityGrade, bool]:
        """计算零件对的兼容性评分"""
        
        # 如果有经验数据，优先使用
        if experience:
            score = experience.compatibility_score or 0
            
            if experience.compatibility_status == CompatibilityStatus.COMPATIBLE:
                if experience.source == "official":
                    grade = CompatibilityGrade.OFFICIAL_SUPPORT
                else:
                    grade = CompatibilityGrade.UNOFFICIAL_SUPPORT
            elif experience.compatibility_status == CompatibilityStatus.CONDITIONAL:
                grade = CompatibilityGrade.UNOFFICIAL_SUPPORT
            else:
                grade = CompatibilityGrade.INCOMPATIBLE
                score = min(score, 30)  # 不兼容最高30分
            
            is_compatible = experience.compatibility_status != CompatibilityStatus.INCOMPATIBLE
            return score, grade, is_compatible
        
        # 基于规则计算评分
        if not rule_results:
            # 没有规则，默认理论兼容
            return 60, CompatibilityGrade.THEORETICAL, True
        
        # 检查阻断性规则
        blocking_failed = any(r.is_blocking and not r.passed for r in rule_results)
        if blocking_failed:
            return 0, CompatibilityGrade.INCOMPATIBLE, False
        
        # 计算加权平均分
        total_weight = sum(r.weight for r in rule_results)
        if total_weight == 0:
            return 60, CompatibilityGrade.THEORETICAL, True
        
        weighted_score = sum(r.score for r in rule_results) / total_weight * 100
        score = max(0, min(100, int(weighted_score)))
        
        # 确定等级
        if score >= 90:
            grade = CompatibilityGrade.OFFICIAL_SUPPORT
        elif score >= 70:
            grade = CompatibilityGrade.UNOFFICIAL_SUPPORT
        elif score >= 50:
            grade = CompatibilityGrade.THEORETICAL
        else:
            grade = CompatibilityGrade.INCOMPATIBLE
        
        is_compatible = score >= 50
        
        return score, grade, is_compatible

    def _calculate_overall_compatibility(
        self, 
        part_combinations: List[PartCompatibilityResult]
    ) -> Tuple[int, CompatibilityGrade, bool]:
        """计算整体兼容性"""
        
        if not part_combinations:
            return 100, CompatibilityGrade.OFFICIAL_SUPPORT, True
        
        # 如果有任何不兼容的组合，整体就不兼容
        incompatible_combinations = [c for c in part_combinations if not c.is_compatible]
        if incompatible_combinations:
            min_score = min(c.compatibility_score for c in incompatible_combinations)
            return min_score, CompatibilityGrade.INCOMPATIBLE, False
        
        # 计算平均分
        avg_score = sum(c.compatibility_score for c in part_combinations) / len(part_combinations)
        score = int(avg_score)
        
        # 取最低等级作为整体等级
        grade_scores = {
            CompatibilityGrade.OFFICIAL_SUPPORT: 95,
            CompatibilityGrade.UNOFFICIAL_SUPPORT: 80,
            CompatibilityGrade.THEORETICAL: 60,
            CompatibilityGrade.INCOMPATIBLE: 0
        }
        
        min_grade = min(c.compatibility_grade for c in part_combinations)
        overall_score = min(score, grade_scores[min_grade])
        
        return overall_score, min_grade, True

    def _generate_pair_warnings(
        self, 
        rule_results: List[RuleResult], 
        experience: Optional[CompatibilityExperience]
    ) -> List[str]:
        """生成零件对的警告信息"""
        
        warnings = []
        
        # 规则相关警告
        failed_rules = [r for r in rule_results if not r.passed]
        for rule in failed_rules:
            if rule.is_blocking:
                warnings.append(f"阻断性规则失败: {rule.rule_name}")
            else:
                warnings.append(f"建议性规则失败: {rule.rule_name}")
        
        # 经验相关警告
        if experience and experience.verification_status == "disputed":
            warnings.append("该兼容性存在争议，建议谨慎使用")
        
        return warnings

    def _generate_recommendations(
        self, 
        part_combinations: List[PartCompatibilityResult], 
        parts: List[Part]
    ) -> List[str]:
        """生成整体建议"""
        
        recommendations = []
        
        # 检查不兼容的组合
        incompatible = [c for c in part_combinations if not c.is_compatible]
        if incompatible:
            recommendations.append(f"发现 {len(incompatible)} 个不兼容组合，建议更换相关零件")
        
        # 检查低分组合
        low_score = [c for c in part_combinations if c.compatibility_score < 70 and c.is_compatible]
        if low_score:
            recommendations.append("部分组合兼容性较低，建议优化配置以获得更好性能")
        
        # 检查缺失属性
        parts_missing_props = [p for p in parts if not p.properties]
        if parts_missing_props:
            recommendations.append("部分零件缺少详细属性信息，可能影响兼容性检查准确性")
        
        return recommendations

    async def _evaluate_candidate_compatibility(
        self, 
        candidate: Part, 
        selected_parts: List[Part], 
        request: CompatibilitySearchRequest,
        db: Session
    ) -> Optional[CompatibilityMatch]:
        """评估候选零件与已选零件的兼容性"""
        
        compatibility_scores = []
        matching_rules_count = 0
        experience_based = False
        reasons = []
        
        # 与每个已选零件检查兼容性
        for selected_part in selected_parts:
            pair_result = await self._check_part_pair_compatibility(
                candidate, selected_part, db, "basic"
            )
            
            compatibility_scores.append(pair_result.compatibility_score)
            matching_rules_count += len([r for r in pair_result.rule_results if r.passed])
            
            if pair_result.experience_data:
                experience_based = True
            
            # 记录不兼容原因
            if not pair_result.is_compatible:
                reasons.append(f"与{selected_part.name}不兼容")
        
        # 如果与任何零件不兼容，则排除
        if any(score < 50 for score in compatibility_scores):
            return None
        
        # 计算综合评分
        avg_score = sum(compatibility_scores) / len(compatibility_scores)
        
        # 确定等级
        if avg_score >= 90:
            grade = CompatibilityGrade.OFFICIAL_SUPPORT
        elif avg_score >= 70:
            grade = CompatibilityGrade.UNOFFICIAL_SUPPORT
        elif avg_score >= 50:
            grade = CompatibilityGrade.THEORETICAL
        else:
            grade = CompatibilityGrade.INCOMPATIBLE
        
        # 计算置信度
        confidence = self._calculate_confidence(
            matching_rules_count, experience_based, len(selected_parts)
        )
        
        # 生成兼容原因
        if not reasons:
            if experience_based:
                reasons.append("基于用户经验验证")
            if matching_rules_count > 0:
                reasons.append(f"通过{matching_rules_count}个兼容性规则")
            if not reasons:
                reasons.append("理论兼容，建议验证")
        
        return CompatibilityMatch(
            part_id=candidate.id,
            part_name=candidate.name,
            part_category=candidate.category or "未分类",
            compatibility_grade=grade,
            compatibility_score=int(avg_score),
            matching_rules_count=matching_rules_count,
            experience_based=experience_based,
            confidence_level=confidence,
            reasons=reasons
        )

    def _calculate_confidence(
        self, 
        matching_rules: int, 
        has_experience: bool, 
        selected_count: int
    ) -> float:
        """计算兼容性置信度"""
        
        base_confidence = 0.5
        
        # 经验数据加分
        if has_experience:
            base_confidence += 0.3
        
        # 规则匹配加分
        rule_bonus = min(0.3, matching_rules * 0.05)
        base_confidence += rule_bonus
        
        # 多零件检查加分
        multi_part_bonus = min(0.2, (selected_count - 1) * 0.05)
        base_confidence += multi_part_bonus
        
        return min(1.0, base_confidence)

    def _generate_search_recommendations(
        self, 
        matches: List[CompatibilityMatch], 
        selected_parts: List[Part]
    ) -> List[str]:
        """生成搜索建议"""
        
        recommendations = []
        
        if not matches:
            recommendations.append("未找到兼容零件，建议：")
            recommendations.append("1. 降低兼容性评分要求")
            recommendations.append("2. 检查已选零件的属性信息是否完整")
            recommendations.append("3. 考虑更换部分已选零件")
        
        elif len(matches) < 5:
            recommendations.append("兼容零件较少，建议扩大搜索范围或优化筛选条件")
        
        # 分析匹配结果质量
        high_quality = [m for m in matches if m.compatibility_score >= 90]
        if high_quality:
            recommendations.append(f"推荐选择前{len(high_quality)}个高兼容性零件")
        
        return recommendations

    async def _get_parts_info(self, part_ids: List[int], db: Session) -> List[Part]:
        """获取零件信息"""
        return db.query(Part).filter(Part.id.in_(part_ids)).all()

    async def _get_cached_result(
        self, 
        part_ids: List[int], 
        db: Session
    ) -> Optional[CompatibilityCheckResponse]:
        """获取缓存的检查结果"""
        
        try:
            part_ids_hash = create_part_ids_hash(part_ids)
            
            cached = db.query(CompatibilityCache).filter(
                CompatibilityCache.part_ids_hash == part_ids_hash,
                CompatibilityCache.expires_at > datetime.utcnow()
            ).first()
            
            if cached:
                # 转换缓存数据为响应对象
                result_data = cached.compatibility_result
                result_data['cached'] = True
                return CompatibilityCheckResponse(**result_data)
            
            return None
            
        except Exception as e:
            logger.warning(f"获取缓存失败: {str(e)}")
            return None

    async def _cache_result(
        self, 
        part_ids: List[int], 
        response: CompatibilityCheckResponse, 
        db: Session
    ):
        """缓存检查结果"""
        
        try:
            part_ids_hash = create_part_ids_hash(part_ids)
            expires_at = datetime.utcnow() + timedelta(hours=self.cache_ttl_hours)
            
            # 删除旧缓存
            db.query(CompatibilityCache).filter(
                CompatibilityCache.part_ids_hash == part_ids_hash
            ).delete()
            
            # 创建新缓存
            cache_entry = CompatibilityCache(
                part_ids_hash=part_ids_hash,
                part_ids=part_ids,
                compatibility_result=response.dict(exclude={'cached'}),
                expires_at=expires_at
            )
            
            db.add(cache_entry)
            db.commit()
            
        except Exception as e:
            logger.warning(f"缓存结果失败: {str(e)}")
            db.rollback()

    def _convert_experience_to_response(
        self, 
        experience: CompatibilityExperience
    ) -> Dict[str, Any]:
        """将经验对象转换为响应格式"""
        
        return {
            "id": experience.id,
            "part_a_id": experience.part_a_id,
            "part_b_id": experience.part_b_id,
            "compatibility_status": experience.compatibility_status,
            "compatibility_score": experience.compatibility_score,
            "notes": experience.notes,
            "source": experience.source,
            "verification_status": experience.verification_status,
            "reference_url": experience.reference_url,
            "added_by": experience.added_by,
            "created_at": experience.created_at,
            "updated_at": experience.updated_at
        }

    async def cleanup_expired_cache(self, db: Session):
        """清理过期缓存"""
        
        try:
            deleted_count = db.query(CompatibilityCache).filter(
                CompatibilityCache.expires_at < datetime.utcnow()
            ).delete()
            
            db.commit()
            
            if deleted_count > 0:
                logger.info(f"清理了 {deleted_count} 个过期缓存条目")
            
        except Exception as e:
            logger.error(f"清理缓存失败: {str(e)}")
            db.rollback()

    async def get_compatibility_stats(self, db: Session) -> Dict[str, Any]:
        """获取兼容性系统统计信息"""
        
        try:
            # 规则统计
            total_rules = db.query(CompatibilityRule).count()
            active_rules = db.query(CompatibilityRule).filter(
                CompatibilityRule.is_active == True
            ).count()
            
            # 经验统计
            total_experiences = db.query(CompatibilityExperience).count()
            verified_experiences = db.query(CompatibilityExperience).filter(
                CompatibilityExperience.verification_status == "verified"
            ).count()
            
            # 缓存统计
            cache_entries = db.query(CompatibilityCache).filter(
                CompatibilityCache.expires_at > datetime.utcnow()
            ).count()
            
            return {
                "total_rules": total_rules,
                "active_rules": active_rules,
                "total_experiences": total_experiences,
                "verified_experiences": verified_experiences,
                "active_cache_entries": cache_entries,
                "cache_ttl_hours": self.cache_ttl_hours
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            return {}


# 全局实例
compatibility_engine = CompatibilityEngine()