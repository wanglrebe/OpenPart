# backend/fix_db_columns.py
"""
修复数据库字段 - 添加缺失的列
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from app.core.config import settings

def fix_database_columns():
    """修复数据库字段"""
    print("🔧 修复数据库字段...")
    
    try:
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            print("✅ 数据库连接成功")
            
            # 为 crawler_plugins 表添加缺失字段
            try:
                conn.execute(text("""
                    ALTER TABLE crawler_plugins 
                    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP,
                    ADD COLUMN IF NOT EXISTS data_source_type VARCHAR(50),
                    ADD COLUMN IF NOT EXISTS homepage VARCHAR(500),
                    ADD COLUMN IF NOT EXISTS terms_url VARCHAR(500),
                    ADD COLUMN IF NOT EXISTS file_hash VARCHAR(64),
                    ADD COLUMN IF NOT EXISTS config_schema JSON,
                    ADD COLUMN IF NOT EXISTS allowed_domains JSON,
                    ADD COLUMN IF NOT EXISTS required_permissions JSON,
                    ADD COLUMN IF NOT EXISTS rate_limit INTEGER DEFAULT 2,
                    ADD COLUMN IF NOT EXISTS batch_size INTEGER DEFAULT 50
                """))
                print("✅ crawler_plugins 表字段添加完成")
            except Exception as e:
                print(f"⚠️ crawler_plugins 字段添加警告: {e}")
            
            # 为 crawler_tasks 表添加缺失字段
            try:
                conn.execute(text("""
                    ALTER TABLE crawler_tasks 
                    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP,
                    ADD COLUMN IF NOT EXISTS schedule_type VARCHAR(20) DEFAULT 'manual',
                    ADD COLUMN IF NOT EXISTS schedule_config JSON,
                    ADD COLUMN IF NOT EXISTS success_count INTEGER DEFAULT 0,
                    ADD COLUMN IF NOT EXISTS error_count INTEGER DEFAULT 0,
                    ADD COLUMN IF NOT EXISTS last_page_token VARCHAR(200),
                    ADD COLUMN IF NOT EXISTS created_by INTEGER
                """))
                print("✅ crawler_tasks 表字段添加完成")
            except Exception as e:
                print(f"⚠️ crawler_tasks 字段添加警告: {e}")
            
            # 检查表结构
            print("\n📋 检查表结构:")
            
            # 检查 crawler_plugins 表
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'crawler_plugins' 
                ORDER BY ordinal_position
            """))
            
            print("crawler_plugins 表字段:")
            for row in result:
                print(f"  - {row[0]} ({row[1]})")
            
            # 检查 crawler_tasks 表
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'crawler_tasks' 
                ORDER BY ordinal_position
            """))
            
            print("\ncrawler_tasks 表字段:")
            for row in result:
                print(f"  - {row[0]} ({row[1]})")
            
            conn.commit()
            print("\n🎉 数据库字段修复完成！")
            
            return True
            
    except Exception as e:
        print(f"❌ 数据库字段修复失败: {e}")
        return False

if __name__ == "__main__":
    if fix_database_columns():
        print("\n✅ 请重启后端服务器")
        print("重启命令:")
        print("  pkill -f 'uvicorn.*app.main:app'")
        print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("\n❌ 请检查数据库连接和权限")
        sys.exit(1)