# backend/simple_migrate.py
"""
简化版数据库迁移工具

功能:
- 迁移到最新版本
- 回滚到上一个版本
- 查看当前版本

用法:
python simple_migrate.py migrate    # 迁移
python simple_migrate.py rollback   # 回滚
python simple_migrate.py status     # 查看状态
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from app.core.config import settings

class SimpleMigration:
    def __init__(self):
        self.engine = create_engine(settings.database_url)
        self.migration_table = "simple_migrations"
        self._init_migration_table()
    
    def _init_migration_table(self):
        """初始化迁移表"""
        with self.engine.connect() as conn:
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {self.migration_table} (
                    version VARCHAR(50) PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    rollback_sql TEXT
                )
            """))
            conn.commit()
    
    def get_current_version(self):
        """获取当前版本"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"""
                    SELECT version FROM {self.migration_table} 
                    ORDER BY applied_at DESC LIMIT 1
                """))
                row = result.fetchone()
                return row[0] if row else None
        except:
            return None
    
    def migrate(self):
        """执行迁移"""
        current = self.get_current_version()
        
        # 定义迁移步骤
        migrations = [
            {
                "version": "001_initial",
                "sql": """
                    -- 基础表已存在，跳过
                """,
                "rollback": "-- 初始版本，无需回滚"
            },
            {
                "version": "002_plugin_tables", 
                "sql": """
                    -- 创建插件表
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
                    );

                    -- 创建任务表
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
                    );

                    -- 为零件表添加数据源字段
                    ALTER TABLE parts 
                    ADD COLUMN IF NOT EXISTS data_source VARCHAR(200),
                    ADD COLUMN IF NOT EXISTS source_url VARCHAR(500),
                    ADD COLUMN IF NOT EXISTS crawl_time TIMESTAMP;
                """,
                "rollback": """
                    ALTER TABLE parts 
                    DROP COLUMN IF EXISTS data_source,
                    DROP COLUMN IF EXISTS source_url,
                    DROP COLUMN IF EXISTS crawl_time;
                    
                    DROP TABLE IF EXISTS crawler_tasks CASCADE;
                    DROP TABLE IF EXISTS crawler_plugins CASCADE;
                """
            }
        ]
        
        # 执行未应用的迁移
        for migration in migrations:
            if not current or migration["version"] > current:
                print(f"🚀 应用迁移: {migration['version']}")
                
                try:
                    with self.engine.connect() as conn:
                        # 执行迁移SQL
                        for statement in migration["sql"].split(';'):
                            statement = statement.strip()
                            if statement and not statement.startswith('--'):
                                conn.execute(text(statement))
                        
                        # 记录迁移
                        conn.execute(text(f"""
                            INSERT INTO {self.migration_table} (version, rollback_sql)
                            VALUES ('{migration["version"]}', :rollback_sql)
                            ON CONFLICT (version) DO NOTHING
                        """), {"rollback_sql": migration["rollback"]})
                        
                        conn.commit()
                        print(f"✅ 迁移 {migration['version']} 完成")
                        
                except Exception as e:
                    print(f"❌ 迁移失败: {e}")
                    return False
        
        print("🎉 所有迁移完成！")
        return True
    
    def rollback(self):
        """回滚到上一个版本"""
        with self.engine.connect() as conn:
            # 获取最新的迁移记录
            result = conn.execute(text(f"""
                SELECT version, rollback_sql FROM {self.migration_table} 
                ORDER BY applied_at DESC LIMIT 1
            """))
            row = result.fetchone()
            
            if not row:
                print("⚠️ 没有可回滚的迁移")
                return False
            
            version, rollback_sql = row
            print(f"🔄 回滚版本: {version}")
            
            try:
                # 执行回滚SQL
                for statement in rollback_sql.split(';'):
                    statement = statement.strip()
                    if statement and not statement.startswith('--'):
                        conn.execute(text(statement))
                
                # 删除迁移记录
                conn.execute(text(f"""
                    DELETE FROM {self.migration_table} 
                    WHERE version = '{version}'
                """))
                
                conn.commit()
                print(f"✅ 已回滚版本: {version}")
                return True
                
            except Exception as e:
                print(f"❌ 回滚失败: {e}")
                return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python simple_migrate.py [migrate|rollback|status]")
        return
    
    command = sys.argv[1]
    migration = SimpleMigration()
    
    try:
        if command == "status":
            current = migration.get_current_version()
            print(f"当前版本: {current or '未设置'}")
            
        elif command == "migrate":
            print("📦 开始数据库迁移...")
            if migration.migrate():
                print("✅ 迁移成功")
            else:
                print("❌ 迁移失败")
                sys.exit(1)
                
        elif command == "rollback":
            print("🔄 开始回滚...")
            if migration.rollback():
                print("✅ 回滚成功")
            else:
                print("❌ 回滚失败")
                sys.exit(1)
        else:
            print("❌ 未知命令，使用: migrate, rollback, 或 status")
            
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()