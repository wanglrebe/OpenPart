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
    q: Optional[str] = Query(None, description="搜索关键词"),
    category: Optional[str] = Query(None, description="类别筛选"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    增强搜索API - 支持智能参数搜索（修复版本）
    """
    query = db.query(Part)
    
    # 如果有搜索关键词
    if q:
        search_term = f"%{q}%"
        
        # 构建基本搜索条件
        search_conditions = [
            Part.name.ilike(search_term),           # 名称搜索
            Part.description.ilike(search_term),    # 描述搜索
            Part.category.ilike(search_term),       # 类别搜索
        ]
        
        # 简化的JSON搜索 - 使用更兼容的方法
        try:
            # 尝试PostgreSQL的JSON操作符
            search_conditions.append(
                text("properties::text ILIKE :search_term").bindparam(search_term=search_term)
            )
        except:
            # 如果上面失败，使用更简单的方法
            pass
        
        # 应用OR条件
        query = query.filter(or_(*search_conditions))
    
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
    """获取搜索建议"""
    if not q:
        return []
    
    suggestions = set()
    search_term = f"%{q}%"
    
    try:
        # 获取匹配的类别
        categories = db.query(Part.category).filter(
            Part.category.ilike(search_term)
        ).distinct().limit(5).all()
        
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
                
    except Exception as e:
        print(f"获取搜索建议时出错: {e}")
        # 返回空列表而不是抛出异常
        return []
    
    # 限制返回数量
    return list(suggestions)[:limit]

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