# backend/init_db.py
from app.core.database import engine, Base
from app.models.part import Part

# 创建所有表
Base.metadata.create_all(bind=engine)
print("数据库表创建完成！")