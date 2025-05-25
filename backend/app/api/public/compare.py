# backend/app/api/public/compare.py (新文件)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.core.database import get_db
from app.models.part import Part
from app.schemas.part import PartResponse
from app.auth.middleware import get_current_user_optional
from app.auth.models import User

router = APIRouter()

@router.post("/compare", response_model=Dict[str, Any])
async def compare_parts(
    part_ids: List[int],
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    对比多个零件的参数
    
    Args:
        part_ids: 要对比的零件ID列表
    
    Returns:
        对比结果，包含所有零件的所有参数
    """
    
    # 验证输入
    if not part_ids:
        raise HTTPException(status_code=400, detail="请至少选择一个零件进行对比")
    
    if len(part_ids) > 6:  # 限制对比数量，避免界面过于复杂
        raise HTTPException(status_code=400, detail="最多只能同时对比6个零件")
    
    # 查询零件信息
    parts = db.query(Part).filter(Part.id.in_(part_ids)).all()
    
    if len(parts) != len(part_ids):
        found_ids = [p.id for p in parts]
        missing_ids = [pid for pid in part_ids if pid not in found_ids]
        raise HTTPException(
            status_code=404, 
            detail=f"未找到零件: {missing_ids}"
        )
    
    # 按输入顺序排序零件
    parts_dict = {p.id: p for p in parts}
    ordered_parts = [parts_dict[pid] for pid in part_ids]
    
    # 构建对比数据
    comparison_result = build_comparison_data(ordered_parts)
    
    return comparison_result

def build_comparison_data(parts: List[Part]) -> Dict[str, Any]:
    """
    构建对比数据结构
    
    Args:
        parts: 要对比的零件列表
        
    Returns:
        格式化的对比数据
    """
    
    # 基本信息
    basic_info = {
        "零件ID": [str(p.id) for p in parts],
        "名称": [p.name for p in parts],
        "类别": [p.category or "—" for p in parts],
        "描述": [p.description or "—" for p in parts],
        "创建时间": [p.created_at.strftime("%Y-%m-%d") for p in parts]
    }
    
    # 收集所有属性键
    all_property_keys = set()
    for part in parts:
        if part.properties:
            all_property_keys.update(part.properties.keys())
    
    # 构建属性对比数据
    properties_comparison = {}
    for key in sorted(all_property_keys):  # 按字母顺序排序
        values = []
        for part in parts:
            if part.properties and key in part.properties:
                value = part.properties[key]
                # 确保值是字符串格式
                values.append(str(value) if value is not None else "—")
            else:
                values.append("—")
        properties_comparison[key] = values
    
    # 分析差异
    differences = analyze_differences(basic_info, properties_comparison)
    
    # 构建最终结果
    result = {
        "parts_info": [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "image_url": p.image_url
            } for p in parts
        ],
        "basic_comparison": basic_info,
        "properties_comparison": properties_comparison,
        "differences": differences,
        "comparison_count": len(parts),
        "total_attributes": len(all_property_keys) + len(basic_info) - 1,  # 不包括零件ID
        "generated_at": parts[0].created_at.isoformat() if parts else None
    }
    
    return result

def analyze_differences(basic_info: Dict[str, List], properties_comparison: Dict[str, List]) -> Dict[str, Any]:
    """
    分析对比中的差异
    
    Returns:
        差异分析结果
    """
    differences = {
        "identical_attributes": [],      # 所有零件都相同的属性
        "different_attributes": [],      # 存在差异的属性  
        "unique_attributes": [],         # 只有部分零件有的属性
        "missing_data_attributes": []    # 有零件缺少数据的属性
    }
    
    # 分析基本信息差异（跳过零件ID和名称，这些肯定不同）
    skip_keys = {"零件ID", "名称"}
    for key, values in basic_info.items():
        if key in skip_keys:
            continue
            
        unique_values = set(v for v in values if v != "—")
        has_missing = "—" in values
        
        if len(unique_values) == 0:
            differences["missing_data_attributes"].append(key)
        elif len(unique_values) == 1 and not has_missing:
            differences["identical_attributes"].append(key)
        else:
            differences["different_attributes"].append(key)
            if has_missing:
                differences["missing_data_attributes"].append(key)
    
    # 分析属性差异
    for key, values in properties_comparison.items():
        unique_values = set(v for v in values if v != "—")
        has_missing = "—" in values
        missing_count = values.count("—")
        
        if len(unique_values) == 0:
            differences["missing_data_attributes"].append(key)
        elif len(unique_values) == 1 and not has_missing:
            differences["identical_attributes"].append(key)
        elif missing_count == len(values) - 1:  # 只有一个零件有这个属性
            differences["unique_attributes"].append(key)
        else:
            differences["different_attributes"].append(key)
            if has_missing:
                differences["missing_data_attributes"].append(key)
    
    return differences

@router.get("/compare-suggestions/{part_id}", response_model=List[PartResponse])
async def get_comparison_suggestions(
    part_id: int,
    limit: int = Query(5, ge=1, le=10, description="建议数量"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    获取与指定零件相似的零件，用于对比建议
    
    Args:
        part_id: 基准零件ID
        limit: 返回建议数量
        
    Returns:
        建议对比的零件列表
    """
    
    # 获取基准零件
    base_part = db.query(Part).filter(Part.id == part_id).first()
    if not base_part:
        raise HTTPException(status_code=404, detail="零件未找到")
    
    # 查找相同类别的零件
    suggested_parts = []
    
    if base_part.category:
        # 优先推荐同类别零件
        same_category_parts = db.query(Part).filter(
            Part.category == base_part.category,
            Part.id != part_id
        ).limit(limit * 2).all()  # 多查一些用于筛选
        
        suggested_parts.extend(same_category_parts)
    
    # 如果同类别零件不够，添加相关零件
    if len(suggested_parts) < limit:
        # 基于名称相似性查找
        if base_part.name:
            name_keywords = base_part.name.split()[:2]  # 取前两个关键词
            for keyword in name_keywords:
                similar_parts = db.query(Part).filter(
                    Part.name.ilike(f"%{keyword}%"),
                    Part.id != part_id,
                    Part.id.notin_([p.id for p in suggested_parts])
                ).limit(3).all()
                suggested_parts.extend(similar_parts)
                
                if len(suggested_parts) >= limit:
                    break
    
    # 去重并限制数量
    seen_ids = set()
    final_suggestions = []
    for part in suggested_parts:
        if part.id not in seen_ids and len(final_suggestions) < limit:
            seen_ids.add(part.id)
            final_suggestions.append(part)
    
    return final_suggestions