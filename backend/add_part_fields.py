# add_part_fields.py - 为零件表添加数据源字段
"""
为parts表添加爬虫相关字段
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent / "backend"
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from app.core.config import settings

def add_part_source_fields():
    """为零件表添加数据源字段"""
    
    print("🔧 为零件表添加数据源字段...")
    
    try:
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            # 要添加的字段
            new_fields = [
                ("data_source", "VARCHAR(200)"),
                ("source_url", "VARCHAR(500)"),
                ("crawl_time", "TIMESTAMP WITH TIME ZONE"),
                ("crawler_version", "VARCHAR(50)")
            ]
            
            for field_name, field_type in new_fields:
                try:
                    # 检查字段是否已存在
                    result = conn.execute(text(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'parts' AND column_name = '{field_name}'
                    """))
                    
                    if not result.fetchone():
                        print(f"  添加字段: {field_name}")
                        conn.execute(text(f"""
                            ALTER TABLE parts 
                            ADD COLUMN {field_name} {field_type}
                        """))
                        conn.commit()
                    else:
                        print(f"  字段 {field_name} 已存在")
                        
                except Exception as e:
                    print(f"  添加字段 {field_name} 失败: {e}")
            
            print("✅ 零件表字段添加完成")
            return True
            
    except Exception as e:
        print(f"❌ 添加字段失败: {e}")
        return False

def main():
    """主函数"""
    
    print("=" * 50)
    print("🔧 添加零件表数据源字段")
    print("=" * 50)
    
    if add_part_source_fields():
        print("\n🎉 字段添加完成！")
        print("\n请重启后端服务：")
        print("  cd backend")
        print("  source venv/bin/activate") 
        print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("\n❌ 添加失败")

if __name__ == "__main__":
    main()