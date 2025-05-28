# fix_database_tables.py - 修复数据库表结构
"""
修复爬虫插件数据库表结构
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent / "backend"
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from app.core.config import settings

def fix_crawler_tasks_table():
    """修复 crawler_tasks 表结构"""
    
    print("🔧 修复 crawler_tasks 表结构...")
    
    try:
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            # 检查表是否存在
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'crawler_tasks'
                );
            """))
            
            table_exists = result.fetchone()[0]
            
            if table_exists:
                print("✅ crawler_tasks 表已存在，检查字段...")
                
                # 检查并添加缺失的字段
                missing_fields = [
                    ("schedule_type", "VARCHAR(20) DEFAULT 'manual'"),
                    ("schedule_config", "JSON"),
                    ("created_by", "INTEGER REFERENCES users(id)")
                ]
                
                for field_name, field_definition in missing_fields:
                    # 检查字段是否存在
                    result = conn.execute(text(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'crawler_tasks' AND column_name = '{field_name}'
                    """))
                    
                    if not result.fetchone():
                        print(f"  添加字段: {field_name}")
                        conn.execute(text(f"""
                            ALTER TABLE crawler_tasks 
                            ADD COLUMN {field_name} {field_definition}
                        """))
                        conn.commit()
                    else:
                        print(f"  字段 {field_name} 已存在")
                
                print("✅ crawler_tasks 表结构修复完成")
            else:
                print("❌ crawler_tasks 表不存在，需要重新创建")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 修复 crawler_tasks 表失败: {e}")
        return False

def main():
    """主函数"""
    
    print("=" * 60)
    print("🔧 OpenPart 数据库表结构修复")
    print("=" * 60)
    
    # 修复任务表
    if fix_crawler_tasks_table():
        print("\n🎉 数据库表结构修复完成！")
        print("\n请重启后端服务：")
        print("  cd backend")
        print("  source venv/bin/activate")
        print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("\n❌ 修复失败，请检查数据库连接")

if __name__ == "__main__":
    main()