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