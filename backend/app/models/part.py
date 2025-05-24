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