# backend/app/api/public/parts.py (修复版本)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, text
from typing import List, Optional
from app.core.database import get_db
from app.models.part import Part
from app.schemas.part import PartResponse
from app.auth.middleware import get_current_user_optional
from app.auth.models import User

router = APIRouter()

@router.get("/search", response_model=List[PartResponse])
async def search_parts_enhanced(
    q: Optional[str] = Query(None, description="搜索关键词，支持多词搜索"),
    category: Optional[str] = Query(None, description="类别筛选"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    增强搜索API - 支持多关键词和属性搜索
    
    搜索逻辑：
    - 支持空格分隔的多关键词搜索
    - 搜索范围：名称、描述、类别、所有自定义属性
    - 多词搜索：所有词都必须匹配（AND逻辑）
    - 示例：搜索"电阻 5V"会找到名称包含"电阻"且属性包含"5V"的零件
    """
    query = db.query(Part)
    
    # 如果有搜索关键词
    if q and q.strip():
        # 分割搜索词（按空格）
        search_terms = [term.strip() for term in q.split() if term.strip()]
        
        if search_terms:
            # 对每个搜索词，构建OR条件（在各字段中搜索）
            for term in search_terms:
                search_term = f"%{term}%"
                
                # 构建单个词的搜索条件
                term_conditions = [
                    Part.name.ilike(search_term),           # 名称搜索
                    Part.description.ilike(search_term),    # 描述搜索
                    Part.category.ilike(search_term),       # 类别搜索
                ]
                
                # PostgreSQL JSON字段搜索 - 搜索所有properties的键和值
                try:
                    # 搜索JSON中的所有键和值
                    term_conditions.append(
                        text("properties::text ILIKE :search_term").bindparam(search_term=search_term)
                    )
                except Exception as e:
                    print(f"JSON搜索出错: {e}")
                    # 降级处理：尝试转换为字符串搜索
                    pass
                
                # 应用OR条件（任一字段匹配该词即可）
                query = query.filter(or_(*term_conditions))
    
    # 类别筛选
    if category:
        query = query.filter(Part.category == category)
    
    # 分页
    parts = query.offset(skip).limit(limit).all()
    
    return parts

@router.get("/", response_model=List[PartResponse])
async def get_parts_public(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取零件列表（兼容性保持）"""
    query = db.query(Part)
    
    if category:
        query = query.filter(Part.category == category)
    
    parts = query.offset(skip).limit(limit).all()
    return parts

@router.get("/suggestions", response_model=List[str])
async def get_search_suggestions(
    q: Optional[str] = Query(None, min_length=1, description="搜索关键词"),
    limit: int = Query(10, ge=1, le=20, description="建议数量"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    获取搜索建议 - 支持属性值建议
    """
    if not q:
        return []
    
    suggestions = set()
    search_term = f"%{q}%"
    
    try:
        # 获取匹配的类别
        categories = db.query(Part.category).filter(
            Part.category.ilike(search_term)
        ).distinct().limit(3).all()
        
        for cat in categories:
            if cat[0]:
                suggestions.add(cat[0])
        
        # 获取匹配的零件名称
        names = db.query(Part.name).filter(
            Part.name.ilike(search_term)
        ).limit(5).all()
        
        for name in names:
            if name[0]:
                suggestions.add(name[0])
        
        # 获取匹配的属性值（从JSON中提取）
        # 这里简化处理，实际生产环境可能需要更复杂的JSON查询
        parts_with_properties = db.query(Part.properties).filter(
            Part.properties.isnot(None)
        ).limit(50).all()
        
        for part_props in parts_with_properties:
            if part_props[0]:  # properties不为空
                try:
                    properties = part_props[0]
                    if isinstance(properties, dict):
                        # 搜索属性键
                        for key in properties.keys():
                            if q.lower() in key.lower():
                                suggestions.add(key)
                        
                        # 搜索属性值
                        for value in properties.values():
                            if isinstance(value, str) and q.lower() in value.lower():
                                suggestions.add(value)
                except Exception as e:
                    continue
                    
    except Exception as e:
        print(f"获取搜索建议时出错: {e}")
        return []
    
    # 限制返回数量并排序
    result = sorted(list(suggestions))[:limit]
    return result

# 添加高级搜索端点
@router.get("/advanced-search", response_model=List[PartResponse])
async def advanced_search(
    name: Optional[str] = Query(None, description="名称搜索"),
    category: Optional[str] = Query(None, description="类别搜索"),
    description: Optional[str] = Query(None, description="描述搜索"),
    properties: Optional[str] = Query(None, description="属性搜索，格式: key:value,key2:value2"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    高级搜索API - 支持精确字段搜索
    """
    query = db.query(Part)
    
    # 名称搜索
    if name:
        query = query.filter(Part.name.ilike(f"%{name}%"))
    
    # 类别搜索
    if category:
        query = query.filter(Part.category == category)
    
    # 描述搜索
    if description:
        query = query.filter(Part.description.ilike(f"%{description}%"))
    
    # 属性搜索
    if properties:
        try:
            # 解析属性搜索：key:value,key2:value2
            prop_conditions = []
            for prop_pair in properties.split(','):
                if ':' in prop_pair:
                    key, value = prop_pair.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # JSON属性搜索
                    prop_conditions.append(
                        text("properties ->> :key ILIKE :value").bindparam(
                            key=key, value=f"%{value}%"
                        )
                    )
            
            if prop_conditions:
                query = query.filter(and_(*prop_conditions))
                
        except Exception as e:
            print(f"属性搜索出错: {e}")
    
    parts = query.offset(skip).limit(limit).all()
    return parts

@router.get("/{part_id}", response_model=PartResponse)
async def get_part_public(
    part_id: int, 
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取零件详情（公开API）"""
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="零件未找到")
    return part

@router.get("/categories/", response_model=List[str])
async def get_categories_public(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取所有类别（公开API）"""
    categories = db.query(Part.category).distinct().filter(Part.category.isnot(None)).all()
    return [cat[0] for cat in categories if cat[0]]