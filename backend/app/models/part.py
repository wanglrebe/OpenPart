# backend/app/models/part.py - 添加数据源字段
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Float
from sqlalchemy.sql import func
from app.core.database import Base

class Part(Base):
    """零件模型 - 添加爬虫数据源字段"""
    __tablename__ = "parts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    category = Column(String(100), index=True)
    description = Column(Text)
    properties = Column(JSON)
    image_url = Column(String(500))
    
    # 爬虫数据源相关字段
    external_id = Column(String(255), index=True)  # 外部系统ID
    data_source = Column(String(200))              # 数据来源
    source_url = Column(String(500))               # 原始URL
    crawl_time = Column(DateTime(timezone=True))   # 爬取时间
    crawler_version = Column(String(50))           # 爬虫版本
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())