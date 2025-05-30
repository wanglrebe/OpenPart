# backend/app/api/public/compatibility.py
"""
公开兼容性检查API

为前端用户提供兼容性检查、搜索和建议功能
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from app.core.database import get_db
from app.auth.middleware import get_current_user_optional
from app.auth.models import User
from app.models.part import Part
from app.schemas.compatibility import (
    CompatibilityCheckRequest, CompatibilityCheckResponse,
    CompatibilitySearchRequest, CompatibilitySearchResponse,
    CompatibilityMatch
)
from app.schemas.part import PartResponse
from app.services.compatibility_engine import compatibility_engine

router = APIRouter()
logger = logging.getLogger(__name__)

# ==================== 兼容性检查API ====================

@router.post("/check", response_model=CompatibilityCheckResponse)
async def check_compatibility(
    request: CompatibilityCheckRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    检查多个零件的兼容性
    
    - 支持2-10个零件的组合检查
    - 返回详细的兼容性分析结果
    - 包含规则执行结果和经验数据
    - 提供优化建议和警告信息
    """
    try:
        logger.info(f"兼容性检查请求: 零件数量={len(request.part_ids)}, 用户={current_user.username if current_user else 'anonymous'}")
        
        # 验证输入
        if len(request.part_ids) < 2:
            raise HTTPException(
                status_code=400, 
                detail="至少需要2个零件进行兼容性检查"
            )
        
        if len(request.part_ids) > 10:
            raise HTTPException(
                status_code=400, 
                detail="最多支持10个零件的兼容性检查"
            )
        
        # 检查零件是否存在
        parts = db.query(Part).filter(Part.id.in_(request.part_ids)).all()
        if len(parts) != len(request.part_ids):
            found_ids = {p.id for p in parts}
            missing_ids = [pid for pid in request.part_ids if pid not in found_ids]
            raise HTTPException(
                status_code=404, 
                detail=f"未找到零件: {missing_ids}"
            )
        
        # 执行兼容性检查
        result = await compatibility_engine.check_compatibility(request, db)
        
        logger.info(f"兼容性检查完成: 整体评分={result.overall_score}, 兼容={result.is_overall_compatible}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"兼容性检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"兼容性检查失败: {str(e)}")

@router.post("/search", response_model=CompatibilitySearchResponse)
async def search_compatible_parts(
    request: CompatibilitySearchRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    搜索与指定零件兼容的其他零件
    
    - 基于已选零件查找兼容的候选零件
    - 支持类别筛选和评分阈值设置
    - 返回排序后的兼容性匹配结果
    - 包含匹配原因和置信度评估
    """
    try:
        logger.info(f"兼容性搜索请求: 已选零件={len(request.selected_parts)}, 用户={current_user.username if current_user else 'anonymous'}")
        
        # 验证输入
        if len(request.selected_parts) == 0:
            raise HTTPException(
                status_code=400, 
                detail="请至少选择一个零件进行兼容性搜索"
            )
        
        if len(request.selected_parts) > 5:
            raise HTTPException(
                status_code=400, 
                detail="最多支持5个零件的兼容性搜索"
            )
        
        # 检查已选零件是否存在
        selected_parts = db.query(Part).filter(Part.id.in_(request.selected_parts)).all()
        if len(selected_parts) != len(request.selected_parts):
            found_ids = {p.id for p in selected_parts}
            missing_ids = [pid for pid in request.selected_parts if pid not in found_ids]
            raise HTTPException(
                status_code=404, 
                detail=f"未找到已选零件: {missing_ids}"
            )
        
        # 执行兼容性搜索
        result = await compatibility_engine.search_compatible_parts(request, db)
        
        logger.info(f"兼容性搜索完成: 找到{len(result.matches)}个匹配零件")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"兼容性搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"兼容性搜索失败: {str(e)}")

@router.get("/suggestions/{part_id}", response_model=List[PartResponse])
async def get_compatibility_suggestions(
    part_id: int,
    limit: int = Query(10, ge=1, le=50, description="建议数量"),
    min_score: int = Query(70, ge=0, le=100, description="最低兼容性评分"),
    categories: Optional[str] = Query(None, description="目标类别，逗号分隔"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    获取与指定零件兼容的建议零件
    
    - 基于单个零件推荐兼容的其他零件
    - 支持类别筛选和评分阈值
    - 快速返回高兼容性的推荐结果
    """
    try:
        logger.info(f"获取兼容性建议: 零件ID={part_id}, 用户={current_user.username if current_user else 'anonymous'}")
        
        # 检查零件是否存在
        base_part = db.query(Part).filter(Part.id == part_id).first()
        if not base_part:
            raise HTTPException(status_code=404, detail="零件未找到")
        
        # 解析目标类别
        target_categories = None
        if categories:
            target_categories = [cat.strip() for cat in categories.split(",") if cat.strip()]
        
        # 构建搜索请求
        search_request = CompatibilitySearchRequest(
            selected_parts=[part_id],
            target_categories=target_categories,
            min_compatibility_score=min_score,
            limit=limit,
            include_theoretical=True
        )
        
        # 执行搜索
        search_result = await compatibility_engine.search_compatible_parts(search_request, db)
        
        # 获取建议零件的详细信息
        suggested_part_ids = [match.part_id for match in search_result.matches]
        suggested_parts = db.query(Part).filter(Part.id.in_(suggested_part_ids)).all()
        
        # 按搜索结果的顺序排序
        parts_dict = {p.id: p for p in suggested_parts}
        ordered_parts = [parts_dict[match.part_id] for match in search_result.matches if match.part_id in parts_dict]
        
        logger.info(f"兼容性建议完成: 返回{len(ordered_parts)}个建议零件")
        return ordered_parts
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取兼容性建议失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取兼容性建议失败: {str(e)}")

# ==================== 快速兼容性检查API ====================

@router.get("/quick-check")
async def quick_compatibility_check(
    part_a_id: int = Query(..., description="零件A的ID"),
    part_b_id: int = Query(..., description="零件B的ID"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    快速两两兼容性检查
    
    - 专用于两个零件的快速兼容性检查
    - 返回简化的兼容性结果
    - 适用于实时兼容性提示
    """
    try:
        logger.info(f"快速兼容性检查: 零件A={part_a_id}, 零件B={part_b_id}")
        
        # 检查零件是否存在
        part_a = db.query(Part).filter(Part.id == part_a_id).first()
        part_b = db.query(Part).filter(Part.id == part_b_id).first()
        
        if not part_a:
            raise HTTPException(status_code=404, detail=f"零件A未找到: ID={part_a_id}")
        if not part_b:
            raise HTTPException(status_code=404, detail=f"零件B未找到: ID={part_b_id}")
        
        if part_a_id == part_b_id:
            raise HTTPException(status_code=400, detail="不能检查同一个零件的兼容性")
        
        # 构建检查请求
        check_request = CompatibilityCheckRequest(
            part_ids=[part_a_id, part_b_id],
            include_cache=True,
            detail_level="basic"
        )
        
        # 执行检查
        result = await compatibility_engine.check_compatibility(check_request, db)
        
        # 提取第一个（也是唯一的）零件对结果
        if result.part_combinations:
            pair_result = result.part_combinations[0]
            
            return {
                "compatible": pair_result.is_compatible,
                "score": pair_result.compatibility_score,
                "grade": pair_result.compatibility_grade,
                "part_a": {
                    "id": part_a.id,
                    "name": part_a.name,
                    "category": part_a.category
                },
                "part_b": {
                    "id": part_b.id,
                    "name": part_b.name,
                    "category": part_b.category
                },
                "warnings": pair_result.warnings,
                "cached": result.cached,
                "execution_time": result.execution_time
            }
        else:
            return {
                "compatible": False,
                "score": 0,
                "grade": "incompatible",
                "error": "检查失败"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"快速兼容性检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"快速兼容性检查失败: {str(e)}")

# ==================== 外部反馈渠道API ====================

@router.get("/feedback-channels")
async def get_feedback_channels(
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    获取外部反馈渠道信息
    
    - 为用户提供贡献兼容性经验的渠道
    - 包含各种反馈方式的链接和说明
    - 支持未来用户贡献系统的扩展
    """
    try:
        # 外部反馈渠道配置
        feedback_channels = [
            {
                "name": "GitHub Issues",
                "type": "github",
                "url": "https://github.com/your-org/openpart/issues",
                "description": "通过GitHub Issues报告兼容性问题或贡献经验",
                "guidelines": "请使用 'compatibility' 标签，并提供详细的零件信息和测试结果"
            },
            {
                "name": "社区论坛",
                "type": "forum",
                "url": "https://forum.openpart.org/compatibility",
                "description": "在社区论坛分享兼容性经验和讨论",
                "guidelines": "发帖时请包含零件型号、测试环境和结果描述"
            },
            {
                "name": "邮件反馈",
                "type": "email",
                "url": "mailto:compatibility@openpart.org",
                "description": "通过邮件发送兼容性报告",
                "guidelines": "邮件标题请以 [兼容性] 开头，并附上相关文档或图片"
            },
            {
                "name": "Discord社区",
                "type": "discord",
                "url": "https://discord.gg/openpart",
                "description": "在Discord的#compatibility频道实时讨论",
                "guidelines": "请在 #compatibility 频道分享您的发现和问题"
            }
        ]
        
        # 通用贡献指南
        general_guidelines = """
        ## 贡献兼容性经验指南

        ### 提交信息时请包含：
        1. **零件详情**：完整的零件型号、制造商、版本号
        2. **测试环境**：使用场景、配置环境、测试条件
        3. **兼容性结果**：
           - ✅ 完全兼容：正常工作，无任何问题
           - ⚠️ 有条件兼容：可以工作，但有限制或需要特殊配置
           - ❌ 不兼容：无法正常工作或存在冲突
        4. **详细描述**：具体的测试过程和发现的问题
        5. **支持文档**：相关图片、日志、规格书等

        ### 质量标准：
        - 提供准确、客观的测试结果
        - 包含足够的技术细节便于验证
        - 遵循社区行为准则
        - 避免商业推广内容

        您的贡献将帮助整个社区！管理员会审核并整合高质量的反馈到系统中。
        """
        
        # 联系信息
        contact_info = {
            "general_email": "contact@openpart.org",
            "compatibility_email": "compatibility@openpart.org",
            "technical_support": "support@openpart.org",
            "website": "https://openpart.org",
            "documentation": "https://docs.openpart.org/compatibility"
        }
        
        return {
            "channels": feedback_channels,
            "general_guidelines": general_guidelines,
            "contact_info": contact_info,
            "contribution_stats": {
                "total_contributors": 156,  # 示例数据
                "monthly_contributions": 23,
                "processed_this_month": 18
            },
            "future_features": {
                "user_contributions": {
                    "status": "planned",
                    "description": "未来版本将支持用户直接在平台内贡献兼容性经验",
                    "expected_release": "v2.0"
                },
                "contribution_rewards": {
                    "status": "planned", 
                    "description": "贡献者声誉系统和积分奖励",
                    "expected_release": "v2.1"
                }
            }
        }
        
    except Exception as e:
        logger.error(f"获取反馈渠道信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取反馈渠道信息失败: {str(e)}")

# ==================== 兼容性知识库API ====================

@router.get("/knowledge-base")
async def get_compatibility_knowledge_base(
    category: Optional[str] = Query(None, description="筛选特定类别"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    获取兼容性知识库信息
    
    - 提供常见兼容性规则的说明
    - 帮助用户理解兼容性检查逻辑
    - 支持按类别筛选相关知识
    """
    try:
        # 获取活跃规则的统计信息
        from sqlalchemy import func
        from app.models.compatibility import CompatibilityRule
        
        query = db.query(
            CompatibilityRule.category_a,
            CompatibilityRule.category_b,
            func.count(CompatibilityRule.id).label('rule_count'),
            func.avg(CompatibilityRule.weight).label('avg_weight')
        ).filter(
            CompatibilityRule.is_active == True
        ).group_by(
            CompatibilityRule.category_a,
            CompatibilityRule.category_b
        )
        
        if category:
            query = query.filter(
                (CompatibilityRule.category_a == category) |
                (CompatibilityRule.category_b == category)
            )
        
        category_rules = query.all()
        
        # 构建知识库内容
        knowledge_base = {
            "category_combinations": [],
            "common_rules": {
                "电源兼容性": {
                    "description": "检查电源功率是否满足所有组件需求",
                    "example": "power_supply.wattage >= sum([cpu.power, gpu.power, motherboard.power])",
                    "importance": "high"
                },
                "接口兼容性": {
                    "description": "验证连接器和接口类型匹配",
                    "example": "cpu.socket == motherboard.socket",
                    "importance": "high"
                },
                "尺寸兼容性": {
                    "description": "确保物理尺寸和空间要求匹配",
                    "example": "gpu.length <= case.max_gpu_length",
                    "importance": "medium"
                },
                "频率兼容性": {
                    "description": "检查工作频率和时序兼容性",
                    "example": "ram.frequency <= motherboard.max_memory_frequency",
                    "importance": "medium"
                }
            },
            "tips": [
                "兼容性评分90-100分表示官方确认兼容",
                "70-89分表示社区验证可用但可能有限制",
                "50-69分表示理论兼容但建议实际测试",
                "低于50分表示不兼容或存在已知问题",
                "优先查看经验清单中的实际使用反馈"
            ]
        }
        
        # 添加类别组合信息
        for rule_stat in category_rules:
            knowledge_base["category_combinations"].append({
                "category_a": rule_stat.category_a,
                "category_b": rule_stat.category_b,
                "rule_count": rule_stat.rule_count,
                "avg_weight": float(rule_stat.avg_weight) if rule_stat.avg_weight else 0.0,
                "coverage": "high" if rule_stat.rule_count >= 3 else "medium" if rule_stat.rule_count >= 1 else "low"
            })
        
        return knowledge_base
        
    except Exception as e:
        logger.error(f"获取兼容性知识库失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取兼容性知识库失败: {str(e)}")

# ==================== 系统状态API ====================

@router.get("/system-status")
async def get_compatibility_system_status(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    获取兼容性系统状态信息
    
    - 显示系统可用性和性能指标
    - 提供用户友好的状态概览
    - 不包含敏感的管理员信息
    """
    try:
        # 获取系统基础统计
        stats = await compatibility_engine.get_compatibility_stats(db)
        
        # 计算系统健康度
        health_score = 100
        status_messages = []
        
        # 检查规则覆盖率
        if stats.get("active_rules", 0) == 0:
            health_score -= 30
            status_messages.append("系统中没有活跃的兼容性规则")
        elif stats.get("active_rules", 0) < 5:
            health_score -= 10
            status_messages.append("兼容性规则较少，覆盖范围有限")
        
        # 检查经验数据
        if stats.get("verified_experiences", 0) == 0:
            health_score -= 20
            status_messages.append("暂无验证的兼容性经验数据")
        
        # 确定系统状态
        if health_score >= 90:
            system_status = "excellent"
            status_text = "系统运行良好"
        elif health_score >= 70:
            system_status = "good"
            status_text = "系统基本正常"
        elif health_score >= 50:
            system_status = "limited"
            status_text = "系统功能有限"
        else:
            system_status = "poor"
            status_text = "系统需要配置"
        
        if not status_messages:
            status_messages.append("所有功能运行正常")
        
        return {
            "system_status": system_status,
            "status_text": status_text,
            "health_score": health_score,
            "messages": status_messages,
            "capabilities": {
                "compatibility_check": stats.get("active_rules", 0) > 0,
                "experience_lookup": stats.get("verified_experiences", 0) > 0,
                "compatibility_search": True,
                "caching": True
            },
            "statistics": {
                "total_rules": stats.get("total_rules", 0),
                "active_rules": stats.get("active_rules", 0),
                "verified_experiences": stats.get("verified_experiences", 0),
                "cache_entries": stats.get("active_cache_entries", 0)
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取系统状态失败: {str(e)}")
        # 返回基础状态信息，避免完全失败
        return {
            "system_status": "unknown",
            "status_text": "无法获取系统状态",
            "health_score": 0,
            "messages": ["系统状态检查失败"],
            "capabilities": {
                "compatibility_check": False,
                "experience_lookup": False,
                "compatibility_search": False,
                "caching": False
            },
            "error": str(e)
        }

# ==================== 示例和文档API ====================

@router.get("/examples")
async def get_compatibility_examples(
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    获取兼容性检查示例
    
    - 提供常见场景的使用示例
    - 帮助用户理解API使用方法
    - 包含请求和响应示例
    """
    try:
        examples = {
            "basic_check": {
                "title": "基础兼容性检查",
                "description": "检查两个零件是否兼容",
                "request": {
                    "method": "POST",
                    "url": "/api/public/compatibility/check",
                    "body": {
                        "part_ids": [1, 2],
                        "include_cache": True,
                        "detail_level": "standard"
                    }
                },
                "response_example": {
                    "success": True,
                    "overall_compatibility_grade": "unofficial_support",
                    "overall_score": 85,
                    "is_overall_compatible": True,
                    "execution_time": 0.234
                }
            },
            "multi_part_check": {
                "title": "多零件兼容性检查",
                "description": "检查多个零件组合的兼容性",
                "request": {
                    "method": "POST",
                    "url": "/api/public/compatibility/check",
                    "body": {
                        "part_ids": [1, 2, 3, 4],
                        "include_cache": True,
                        "detail_level": "detailed"
                    }
                },
                "response_example": {
                    "success": True,
                    "overall_compatibility_grade": "theoretical",
                    "overall_score": 72,
                    "is_overall_compatible": True,
                    "part_combinations": "..."
                }
            },
            "compatibility_search": {
                "title": "兼容性搜索",
                "description": "搜索与已选零件兼容的其他零件",
                "request": {
                    "method": "POST", 
                    "url": "/api/public/compatibility/search",
                    "body": {
                        "selected_parts": [1, 2],
                        "target_categories": ["内存", "显卡"],
                        "min_compatibility_score": 70,
                        "limit": 10
                    }
                },
                "response_example": {
                    "success": True,
                    "matches": [
                        {
                            "part_id": 15,
                            "part_name": "DDR4-3200 16GB",
                            "compatibility_score": 92,
                            "compatibility_grade": "unofficial_support"
                        }
                    ]
                }
            },
            "quick_check": {
                "title": "快速兼容性检查",
                "description": "两个零件的快速兼容性检查",
                "request": {
                    "method": "GET",
                    "url": "/api/public/compatibility/quick-check?part_a_id=1&part_b_id=2"
                },
                "response_example": {
                    "compatible": True,
                    "score": 88,
                    "grade": "unofficial_support",
                    "cached": True
                }
            }
        }
        
        return {
            "examples": examples,
            "general_tips": [
                "使用缓存可以提高响应速度",
                "detail_level='basic'适用于快速检查",
                "detail_level='detailed'提供完整的规则执行信息",
                "兼容性搜索支持类别筛选以提高精度",
                "建议设置合理的评分阈值过滤结果"
            ],
            "error_handling": {
                "404": "零件未找到 - 检查零件ID是否正确",
                "400": "请求参数错误 - 检查参数格式和范围",
                "500": "服务器内部错误 - 请稍后重试"
            }
        }
        
    except Exception as e:
        logger.error(f"获取示例信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取示例信息失败: {str(e)}")

# ==================== 版本和功能信息API ====================

@router.get("/version")
async def get_compatibility_version():
    """
    获取兼容性系统版本信息
    
    - 显示当前系统版本
    - 列出支持的功能特性
    - 提供API版本信息
    """
    try:
        return {
            "api_version": "1.0.0",
            "system_version": "1.0.0",
            "compatibility_engine": "1.0.0", 
            "features": {
                "multi_part_check": True,
                "compatibility_search": True,
                "experience_lookup": True,
                "rule_based_evaluation": True,
                "caching": True,
                "security_validation": True,
                "external_feedback": True,
                "user_contributions": False,  # 未来功能
                "advanced_analytics": False  # 未来功能
            },
            "supported_detail_levels": ["basic", "standard", "detailed"],
            "max_parts_per_check": 10,
            "max_search_results": 100,
            "cache_ttl_hours": 24,
            "build_date": "2025-05-30",
            "documentation": "https://docs.openpart.org/api/compatibility"
        }
        
    except Exception as e:
        logger.error(f"获取版本信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取版本信息失败: {str(e)}")