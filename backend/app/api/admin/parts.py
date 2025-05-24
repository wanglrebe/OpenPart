from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.part import Part
from app.schemas.part import PartCreate, PartUpdate, PartResponse
from app.auth.middleware import require_admin
from app.auth.models import User

router = APIRouter()

@router.get("/", response_model=List[PartResponse])
async def get_parts_admin(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取零件列表（管理员）"""
    query = db.query(Part)
    if category:
        query = query.filter(Part.category == category)
    parts = query.offset(skip).limit(limit).all()
    return parts

@router.get("/{part_id}", response_model=PartResponse)
async def get_part_admin(
    part_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取单个零件（管理员）"""
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="零件未找到")
    return part

@router.post("/", response_model=PartResponse)
async def create_part_admin(
    part: PartCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """创建新零件（管理员）"""
    db_part = Part(**part.dict())
    db.add(db_part)
    db.commit()
    db.refresh(db_part)
    return db_part

@router.put("/{part_id}", response_model=PartResponse)
async def update_part_admin(
    part_id: int,
    part_update: PartUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """更新零件（管理员）"""
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="零件未找到")
    
    update_data = part_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(part, field, value)
    
    db.commit()
    db.refresh(part)
    return part

@router.delete("/{part_id}")
async def delete_part_admin(
    part_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """删除零件（管理员）"""
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="零件未找到")
    
    db.delete(part)
    db.commit()
    return {"message": "零件已删除"}