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