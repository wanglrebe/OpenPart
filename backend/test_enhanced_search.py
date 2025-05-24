# backend/app/models/part.py (更新版本 - 添加图片字段)
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class Part(Base):
    __tablename__ = "parts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), index=True)
    properties = Column(JSON)  # 存储所有自定义属性
    description = Column(Text)
    image_url = Column(String(500))  # 新增：图片URL字段
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# backend/app/schemas/part.py (更新版本 - 添加图片字段)
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class PartBase(BaseModel):
    name: str
    category: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    image_url: Optional[str] = None  # 新增：图片URL字段

class PartCreate(PartBase):
    pass

class PartUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class PartResponse(PartBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# backend/app/api/public/parts.py (增强版本 - 智能搜索)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
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
    增强搜索API - 支持智能参数搜索
    
    搜索逻辑：
    - 搜索词会在名称、描述、类别、属性中查找
    - 支持参数直接搜索（如搜索"5V"匹配properties中的"5V"）
    """
    query = db.query(Part)
    
    # 如果有搜索关键词
    if q:
        search_term = f"%{q}%"
        
        # 构建搜索条件
        search_conditions = [
            Part.name.ilike(search_term),           # 名称搜索
            Part.description.ilike(search_term),    # 描述搜索
            Part.category.ilike(search_term),       # 类别搜索
        ]
        
        # PostgreSQL JSON字段搜索 - 搜索所有properties值
        # 检查JSON中是否包含搜索词
        if db.bind.dialect.name == 'postgresql':
            # PostgreSQL特有的JSON搜索
            search_conditions.append(
                func.cast(Part.properties, db.Text).ilike(search_term)
            )
        else:
            # SQLite或其他数据库的JSON搜索
            search_conditions.append(
                func.json_extract(Part.properties, '$').like(search_term)
            )
        
        # 应用OR条件 - 任一字段匹配即可
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
    """
    获取搜索建议 - 返回相关的类别和参数
    """
    if not q:
        return []
    
    suggestions = set()
    search_term = f"%{q}%"
    
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

# backend/migrate_add_image.py (数据库迁移脚本)
"""
添加图片字段的数据库迁移脚本
"""
from sqlalchemy import text
from app.core.database import engine

def upgrade():
    """添加image_url字段"""
    with engine.connect() as conn:
        # 添加image_url字段
        conn.execute(text("""
            ALTER TABLE parts 
            ADD COLUMN image_url VARCHAR(500)
        """))
        conn.commit()
        print("✅ 成功添加 image_url 字段")

def downgrade():
    """移除image_url字段"""
    with engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE parts 
            DROP COLUMN image_url
        """))
        conn.commit()
        print("✅ 成功移除 image_url 字段")

if __name__ == "__main__":
    print("=== 数据库迁移：添加图片字段 ===")
    try:
        upgrade()
        print("迁移完成！")
    except Exception as e:
        print(f"迁移失败: {e}")

# backend/test_enhanced_search.py (修复版本)
import requests
import json

BASE_URL = "http://localhost:8000/api/public/parts"  # 修复：添加完整路径

def test_enhanced_search():
    """测试增强搜索功能"""
    print("=== 测试增强搜索功能 ===")
    
    # 测试参数搜索
    test_cases = [
        ("Arduino", "应该找到Arduino相关零件"),
        ("5V", "应该找到电压为5V的零件"),
        ("电阻", "应该找到所有电阻类零件"),
        ("32KB", "应该找到闪存为32KB的零件")
    ]
    
    for query, description in test_cases:
        print(f"\n🔍 搜索: '{query}' - {description}")
        
        response = requests.get(f"{BASE_URL}/search", params={"q": query})
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ 找到 {len(results)} 个结果")
            
            for part in results[:2]:  # 显示前2个结果
                print(f"  - {part['name']} ({part.get('category', '无分类')})")
                if part.get('properties'):
                    print(f"    属性: {part['properties']}")
        else:
            print(f"❌ 搜索失败: {response.status_code}")
            print(f"   错误信息: {response.text}")

def test_search_suggestions():
    """测试搜索建议"""
    print("\n=== 测试搜索建议 ===")
    
    test_queries = ["Ard", "电", "5"]
    
    for query in test_queries:
        print(f"\n💡 建议查询: '{query}'")
        
        response = requests.get(f"{BASE_URL}/suggestions", params={"q": query})
        
        if response.status_code == 200:
            suggestions = response.json()
            print(f"✅ 获得 {len(suggestions)} 个建议:")
            for suggestion in suggestions:
                print(f"  - {suggestion}")
        else:
            print(f"❌ 获取建议失败: {response.status_code}")
            print(f"   错误信息: {response.text}")

def test_categories():
    """测试分类获取"""
    print("\n=== 测试分类获取 ===")
    
    response = requests.get(f"{BASE_URL}/categories/")
    
    if response.status_code == 200:
        categories = response.json()
        print(f"✅ 获得 {len(categories)} 个分类:")
        for category in categories:
            print(f"  - {category}")
    else:
        print(f"❌ 获取分类失败: {response.status_code}")

if __name__ == "__main__":
    print("=== OpenPart 增强搜索测试 ===")
    print("后端API地址:", BASE_URL)
    input("按 Enter 键开始测试...")
    
    test_categories()
    test_enhanced_search()
    test_search_suggestions()
    
    print("\n=== 测试完成 ===")