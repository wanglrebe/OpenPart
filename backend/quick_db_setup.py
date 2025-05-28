# backend/quick_db_setup.py
"""
快速数据库设置脚本 - 创建插件管理必需的表
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from app.core.config import settings

def create_plugin_tables():
    """创建插件相关表"""
    print("🚀 创建插件管理数据库表...")
    
    try:
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            # 测试连接
            conn.execute(text("SELECT 1"))
            print("✅ 数据库连接成功")
            
            # 创建插件表
            plugin_table_sql = """
                CREATE TABLE IF NOT EXISTS crawler_plugins (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    display_name VARCHAR(200) NOT NULL,
                    version VARCHAR(50) NOT NULL,
                    description TEXT,
                    author VARCHAR(100),
                    data_source VARCHAR(200),
                    file_path VARCHAR(500) NOT NULL,
                    status VARCHAR(20) DEFAULT 'inactive',
                    is_active BOOLEAN DEFAULT FALSE,
                    config JSON,
                    run_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    error_count INTEGER DEFAULT 0,
                    last_run_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            conn.execute(text(plugin_table_sql))
            print("✅ 插件表创建成功")
            
            # 创建任务表
            task_table_sql = """
                CREATE TABLE IF NOT EXISTS crawler_tasks (
                    id SERIAL PRIMARY KEY,
                    plugin_id INTEGER REFERENCES crawler_plugins(id) ON DELETE CASCADE,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    config JSON,
                    status VARCHAR(20) DEFAULT 'pending',
                    run_count INTEGER DEFAULT 0,
                    started_at TIMESTAMP,
                    finished_at TIMESTAMP,
                    execution_time FLOAT,
                    data_count INTEGER DEFAULT 0,
                    logs JSON,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            conn.execute(text(task_table_sql))
            print("✅ 任务表创建成功")
            
            # 创建迁移记录表
            migration_table_sql = """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version VARCHAR(50) PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            conn.execute(text(migration_table_sql))
            print("✅ 迁移记录表创建成功")
            
            # 记录迁移版本
            conn.execute(text("""
                INSERT INTO schema_migrations (version) 
                VALUES ('002_plugin_tables') 
                ON CONFLICT (version) DO NOTHING
            """))
            
            # 为零件表添加数据源字段（如果不存在）
            try:
                # 检查字段是否存在
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'parts' AND column_name = 'data_source'
                """))
                
                if not result.fetchone():
                    conn.execute(text("""
                        ALTER TABLE parts 
                        ADD COLUMN data_source VARCHAR(200),
                        ADD COLUMN source_url VARCHAR(500),
                        ADD COLUMN crawl_time TIMESTAMP
                    """))
                    print("✅ 零件表字段添加成功")
                else:
                    print("✅ 零件表字段已存在")
                    
            except Exception as e:
                print(f"⚠️ 零件表字段更新: {e}")
            
            # 创建索引
            try:
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_crawler_plugins_name ON crawler_plugins(name)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_crawler_tasks_plugin_id ON crawler_tasks(plugin_id)"))
                print("✅ 索引创建成功")
            except Exception as e:
                print(f"⚠️ 索引创建: {e}")
            
            # 提交所有更改
            conn.commit()
            
            # 验证表是否创建成功
            result = conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('crawler_plugins', 'crawler_tasks', 'schema_migrations')
                ORDER BY table_name
            """))
            
            created_tables = [row[0] for row in result.fetchall()]
            print(f"📋 已创建的表: {created_tables}")
            
            if len(created_tables) == 3:
                print("🎉 所有表创建完成！")
                return True
            else:
                print(f"⚠️ 期望3个表，实际创建了{len(created_tables)}个")
                return False
            
    except Exception as e:
        print(f"❌ 数据库设置失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_tables():
    """检查表是否存在"""
    print("🔍 检查数据库表...")
    
    try:
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            all_tables = [row[0] for row in result.fetchall()]
            print(f"📋 数据库中的所有表: {all_tables}")
            
            required_tables = ['crawler_plugins', 'crawler_tasks', 'schema_migrations']
            missing_tables = [t for t in required_tables if t not in all_tables]
            
            if missing_tables:
                print(f"❌ 缺少表: {missing_tables}")
                return False
            else:
                print("✅ 所有必需表都存在")
                return True
                
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    
    # 先检查现状
    if check_tables():
        print("✅ 数据库表已存在，无需创建")
    else:
        print("🔄 开始创建数据库表...")
        if create_plugin_tables():
            print("\n🎉 数据库设置完成！")
            print("✅ 可以启动服务器了！")
            print("启动命令: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        else:
            print("\n❌ 数据库设置失败，请检查:")
            print("1. 数据库连接配置")
            print("2. 数据库用户权限")
            print("3. PostgreSQL服务是否运行")
            sys.exit(1)
    
    print("=" * 50)