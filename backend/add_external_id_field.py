# add_external_id_field.py
"""
数据库迁移脚本 - 添加 external_id 字段到 parts 表

使用方法:
python add_external_id_field.py

这个脚本会：
1. 检查 parts 表是否已有 external_id 字段
2. 如果没有，则添加该字段
3. 创建索引以提高查询性能
4. 验证迁移结果
"""

import os
import sys
import traceback
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, inspect
from sqlalchemy.exc import SQLAlchemyError

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入配置
try:
    from app.core.config import settings
    print("✓ 成功导入配置")
except ImportError as e:
    print(f"✗ 导入配置失败: {e}")
    print("请确保在项目根目录下运行此脚本")
    sys.exit(1)

def check_column_exists(engine, table_name, column_name):
    """检查表中是否存在指定列"""
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        column_names = [col['name'] for col in columns]
        return column_name in column_names
    except Exception as e:
        print(f"检查列是否存在时出错: {e}")
        return False

def add_external_id_field():
    """添加 external_id 字段到 parts 表"""
    
    print("=" * 60)
    print("开始数据库迁移：添加 external_id 字段")
    print("=" * 60)
    
    try:
        # 创建数据库连接
        print(f"连接数据库: {settings.database_url}")
        engine = create_engine(settings.database_url)
        
        # 测试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ 数据库连接成功")
        
        # 检查 parts 表是否存在
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'parts' not in tables:
            print("✗ parts 表不存在，请先创建基础表结构")
            return False
        
        print("✓ parts 表存在")
        
        # 检查 external_id 字段是否已存在
        if check_column_exists(engine, 'parts', 'external_id'):
            print("✓ external_id 字段已存在，无需迁移")
            return True
        
        print("→ external_id 字段不存在，开始添加...")
        
        # 执行迁移
        with engine.connect() as conn:
            # 开始事务
            trans = conn.begin()
            
            try:
                # 1. 添加 external_id 字段
                print("1. 添加 external_id 字段...")
                add_column_sql = """
                ALTER TABLE parts 
                ADD COLUMN external_id VARCHAR(255)
                """
                conn.execute(text(add_column_sql))
                print("   ✓ external_id 字段添加成功")
                
                # 2. 创建索引
                print("2. 创建索引...")
                create_index_sql = """
                CREATE INDEX ix_parts_external_id 
                ON parts (external_id)
                """
                conn.execute(text(create_index_sql))
                print("   ✓ external_id 索引创建成功")
                
                # 3. 验证字段是否添加成功
                print("3. 验证迁移结果...")
                verify_sql = """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'parts' 
                AND column_name = 'external_id'
                """
                result = conn.execute(text(verify_sql)).fetchone()
                
                if result:
                    print(f"   ✓ external_id 字段验证成功:")
                    print(f"     - 字段名: {result[0]}")
                    print(f"     - 数据类型: {result[1]}")
                    print(f"     - 可为空: {result[2]}")
                else:
                    raise Exception("验证失败：未找到 external_id 字段")
                
                # 4. 验证索引是否创建成功
                print("4. 验证索引...")
                index_sql = """
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename = 'parts' 
                AND indexname = 'ix_parts_external_id'
                """
                index_result = conn.execute(text(index_sql)).fetchone()
                
                if index_result:
                    print(f"   ✓ 索引验证成功: {index_result[0]}")
                else:
                    print("   ⚠ 索引可能未创建成功，但字段添加正常")
                
                # 5. 查看当前表结构
                print("5. 查看更新后的表结构...")
                columns_sql = """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'parts'
                ORDER BY ordinal_position
                """
                columns = conn.execute(text(columns_sql)).fetchall()
                
                print("   当前 parts 表字段:")
                for col in columns:
                    nullable = "YES" if col[2] == "YES" else "NO"
                    print(f"     - {col[0]}: {col[1]} (nullable: {nullable})")
                
                # 提交事务
                trans.commit()
                print("\n✓ 迁移完成！事务已提交")
                
                return True
                
            except Exception as e:
                # 回滚事务
                trans.rollback()
                print(f"\n✗ 迁移失败，事务已回滚: {e}")
                traceback.print_exc()
                return False
    
    except SQLAlchemyError as e:
        print(f"✗ 数据库错误: {e}")
        return False
    except Exception as e:
        print(f"✗ 未预期错误: {e}")
        traceback.print_exc()
        return False

def verify_migration():
    """验证迁移是否成功"""
    print("\n" + "=" * 60)
    print("验证迁移结果")
    print("=" * 60)
    
    try:
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            # 检查字段和索引
            check_sql = """
            SELECT 
                c.column_name,
                c.data_type,
                c.is_nullable,
                CASE 
                    WHEN i.indexname IS NOT NULL THEN 'YES'
                    ELSE 'NO'
                END as has_index
            FROM information_schema.columns c
            LEFT JOIN pg_indexes i ON i.tablename = 'parts' 
                AND i.indexname LIKE '%external_id%'
            WHERE c.table_name = 'parts' 
                AND c.column_name = 'external_id'
            """
            
            result = conn.execute(text(check_sql)).fetchone()
            
            if result:
                print("✓ 迁移验证成功:")
                print(f"  - 字段名: {result[0]}")
                print(f"  - 数据类型: {result[1]}")
                print(f"  - 可为空: {result[2]}")
                print(f"  - 有索引: {result[3]}")
                
                # 测试插入和查询
                print("\n测试字段功能...")
                
                # 检查是否有测试数据
                count_sql = "SELECT COUNT(*) FROM parts"
                count = conn.execute(text(count_sql)).scalar()
                print(f"当前 parts 表记录数: {count}")
                
                return True
            else:
                print("✗ 验证失败：external_id 字段不存在")
                return False
                
    except Exception as e:
        print(f"✗ 验证过程出错: {e}")
        return False

def main():
    """主函数"""
    print("OpenPart 数据库迁移工具")
    print("任务：添加 external_id 字段到 parts 表")
    
    # 执行迁移
    success = add_external_id_field()
    
    if success:
        # 验证迁移
        verify_success = verify_migration()
        
        if verify_success:
            print("\n" + "=" * 60)
            print("✅ 迁移完成并验证成功！")
            print("✅ 现在可以重启应用并测试插件功能")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("⚠️  迁移可能完成但验证失败")
            print("⚠️  建议手动检查数据库表结构")
            print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ 迁移失败")
        print("❌ 请检查错误信息并修复问题后重试")
        print("=" * 60)

if __name__ == "__main__":
    main()