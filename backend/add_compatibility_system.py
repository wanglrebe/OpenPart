# add_compatibility_system.py
"""
数据库迁移脚本 - 添加兼容性检查系统相关表

使用方法:
python add_compatibility_system.py

这个脚本会：
1. 检查并创建兼容性系统相关的所有数据表
2. 创建必要的索引以提高查询性能
3. 验证迁移结果
4. 可选择插入示例数据
"""

import os
import sys
import traceback
from sqlalchemy import (
    create_engine, text, MetaData, Table, Column, String, Integer, 
    Boolean, DateTime, Text, inspect, ForeignKey, CheckConstraint, Index
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import JSONB, INET

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

def check_table_exists(engine, table_name):
    """检查表是否存在"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return table_name in tables
    except Exception as e:
        print(f"检查表是否存在时出错: {e}")
        return False

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

def create_compatibility_tables():
    """创建兼容性系统相关表"""
    
    print("=" * 60)
    print("开始数据库迁移：创建兼容性检查系统表")
    print("=" * 60)
    
    try:
        # 创建数据库连接
        print(f"连接数据库: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'localhost'}")
        engine = create_engine(settings.database_url)
        
        # 测试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ 数据库连接成功")
        
        # 检查依赖表是否存在
        required_tables = ['users', 'parts']
        for table in required_tables:
            if not check_table_exists(engine, table):
                print(f"✗ 依赖表 {table} 不存在，请先创建基础表结构")
                return False
        print("✓ 依赖表检查通过")
        
        # 定义要创建的表
        tables_to_create = [
            'compatibility_rules',
            'compatibility_experiences', 
            'compatibility_cache',
            'compatibility_templates',
            'rule_audit_log',
            'expression_security_cache'
        ]
        
        # 检查哪些表已存在
        existing_tables = []
        missing_tables = []
        
        for table in tables_to_create:
            if check_table_exists(engine, table):
                existing_tables.append(table)
            else:
                missing_tables.append(table)
        
        if existing_tables:
            print(f"⚠️  以下表已存在: {', '.join(existing_tables)}")
            response = input("是否继续创建剩余的表？(y/N): ")
            if response.lower() != 'y':
                print("迁移已取消")
                return False
        
        if not missing_tables:
            print("✓ 所有兼容性系统表都已存在")
            return True
        
        print(f"→ 需要创建的表: {', '.join(missing_tables)}")
        
        # 执行迁移
        with engine.connect() as conn:
            # 开始事务
            trans = conn.begin()
            
            try:
                # 1. 创建兼容性规则表
                if 'compatibility_rules' in missing_tables:
                    print("1. 创建 compatibility_rules 表...")
                    create_rules_table_sql = """
                    CREATE TABLE compatibility_rules (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(200) NOT NULL,
                        description TEXT,
                        rule_expression TEXT NOT NULL,
                        category_a VARCHAR(100) NOT NULL,
                        category_b VARCHAR(100) NOT NULL,
                        weight INTEGER NOT NULL DEFAULT 100,
                        is_blocking BOOLEAN NOT NULL DEFAULT FALSE,
                        created_by INTEGER NOT NULL REFERENCES users(id),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE,
                        is_active BOOLEAN NOT NULL DEFAULT TRUE,
                        CONSTRAINT check_rule_weight_range CHECK (weight >= 0 AND weight <= 1000)
                    )
                    """
                    conn.execute(text(create_rules_table_sql))
                    
                    # 创建索引
                    indices_sql = [
                        "CREATE INDEX ix_compatibility_rules_id ON compatibility_rules (id)",
                        "CREATE INDEX ix_compatibility_rules_category_a ON compatibility_rules (category_a)",
                        "CREATE INDEX ix_compatibility_rules_category_b ON compatibility_rules (category_b)",
                        "CREATE INDEX ix_compatibility_rules_is_active ON compatibility_rules (is_active)",
                        "CREATE INDEX ix_compatibility_rules_categories ON compatibility_rules (category_a, category_b)",
                        "CREATE INDEX ix_compatibility_rules_active_weight ON compatibility_rules (is_active, weight)"
                    ]
                    
                    for index_sql in indices_sql:
                        conn.execute(text(index_sql))
                    
                    print("   ✓ compatibility_rules 表创建成功")
                
                # 2. 创建兼容性经验表
                if 'compatibility_experiences' in missing_tables:
                    print("2. 创建 compatibility_experiences 表...")
                    create_experiences_table_sql = """
                    CREATE TABLE compatibility_experiences (
                        id SERIAL PRIMARY KEY,
                        part_a_id INTEGER NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
                        part_b_id INTEGER NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
                        compatibility_status VARCHAR(20) NOT NULL,
                        compatibility_score INTEGER,
                        notes TEXT,
                        source VARCHAR(50) NOT NULL DEFAULT 'admin',
                        reference_url VARCHAR(500),
                        verification_status VARCHAR(20) NOT NULL DEFAULT 'verified',
                        added_by INTEGER NOT NULL REFERENCES users(id),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE,
                        CONSTRAINT check_compatibility_score_range CHECK (compatibility_score >= 0 AND compatibility_score <= 100),
                        CONSTRAINT check_compatibility_status CHECK (compatibility_status IN ('compatible', 'incompatible', 'conditional')),
                        CONSTRAINT check_source_values CHECK (source IN ('admin', 'official', 'user_contribution')),
                        CONSTRAINT check_verification_status CHECK (verification_status IN ('verified', 'pending', 'disputed')),
                        CONSTRAINT check_different_parts CHECK (part_a_id != part_b_id),
                        CONSTRAINT unique_part_combination UNIQUE (part_a_id, part_b_id)
                    )
                    """
                    conn.execute(text(create_experiences_table_sql))
                    
                    # 创建索引
                    exp_indices_sql = [
                        "CREATE INDEX ix_compatibility_experiences_id ON compatibility_experiences (id)",
                        "CREATE INDEX ix_compatibility_experiences_part_a_id ON compatibility_experiences (part_a_id)",
                        "CREATE INDEX ix_compatibility_experiences_part_b_id ON compatibility_experiences (part_b_id)",
                        "CREATE INDEX ix_compatibility_experiences_source ON compatibility_experiences (source)",
                        "CREATE INDEX ix_compatibility_experiences_status ON compatibility_experiences (compatibility_status)",
                        "CREATE INDEX ix_compatibility_experiences_source_status ON compatibility_experiences (source, verification_status)"
                    ]
                    
                    for index_sql in exp_indices_sql:
                        conn.execute(text(index_sql))
                    
                    print("   ✓ compatibility_experiences 表创建成功")
                
                # 3. 创建兼容性缓存表
                if 'compatibility_cache' in missing_tables:
                    print("3. 创建 compatibility_cache 表...")
                    create_cache_table_sql = """
                    CREATE TABLE compatibility_cache (
                        id SERIAL PRIMARY KEY,
                        part_ids_hash VARCHAR(64) NOT NULL UNIQUE,
                        part_ids JSONB NOT NULL,
                        compatibility_result JSONB NOT NULL,
                        calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        expires_at TIMESTAMP WITH TIME ZONE
                    )
                    """
                    conn.execute(text(create_cache_table_sql))
                    
                    # 创建索引
                    cache_indices_sql = [
                        "CREATE INDEX ix_compatibility_cache_hash ON compatibility_cache (part_ids_hash)",
                        "CREATE INDEX ix_compatibility_cache_expires ON compatibility_cache (expires_at)",
                        "CREATE INDEX ix_compatibility_cache_expires_calc ON compatibility_cache (expires_at, calculated_at)"
                    ]
                    
                    for index_sql in cache_indices_sql:
                        conn.execute(text(index_sql))
                    
                    print("   ✓ compatibility_cache 表创建成功")
                
                # 4. 创建兼容性模板表
                if 'compatibility_templates' in missing_tables:
                    print("4. 创建 compatibility_templates 表...")
                    create_templates_table_sql = """
                    CREATE TABLE compatibility_templates (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(200) NOT NULL,
                        description TEXT,
                        categories JSONB NOT NULL,
                        rules JSONB NOT NULL,
                        created_by INTEGER NOT NULL REFERENCES users(id),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE,
                        is_public BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                    conn.execute(text(create_templates_table_sql))
                    
                    # 创建索引
                    template_indices_sql = [
                        "CREATE INDEX ix_compatibility_templates_id ON compatibility_templates (id)",
                        "CREATE INDEX ix_compatibility_templates_name ON compatibility_templates (name)",
                        "CREATE INDEX ix_compatibility_templates_public ON compatibility_templates (is_public)",
                        "CREATE INDEX ix_compatibility_templates_public_created ON compatibility_templates (is_public, created_at)"
                    ]
                    
                    for index_sql in template_indices_sql:
                        conn.execute(text(index_sql))
                    
                    print("   ✓ compatibility_templates 表创建成功")
                
                # 5. 创建规则审计日志表
                if 'rule_audit_log' in missing_tables:
                    print("5. 创建 rule_audit_log 表...")
                    create_audit_table_sql = """
                    CREATE TABLE rule_audit_log (
                        id SERIAL PRIMARY KEY,
                        rule_id INTEGER REFERENCES compatibility_rules(id) ON DELETE SET NULL,
                        action VARCHAR(20) NOT NULL,
                        old_expression TEXT,
                        new_expression TEXT,
                        validation_result JSONB,
                        changed_by INTEGER NOT NULL REFERENCES users(id),
                        changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        ip_address INET,
                        user_agent TEXT,
                        risk_level VARCHAR(20) NOT NULL DEFAULT 'low',
                        CONSTRAINT check_audit_action CHECK (action IN ('create', 'update', 'delete', 'test', 'validate')),
                        CONSTRAINT check_risk_level CHECK (risk_level IN ('low', 'medium', 'high'))
                    )
                    """
                    conn.execute(text(create_audit_table_sql))
                    
                    # 创建索引
                    audit_indices_sql = [
                        "CREATE INDEX ix_rule_audit_log_id ON rule_audit_log (id)",
                        "CREATE INDEX ix_rule_audit_log_rule_id ON rule_audit_log (rule_id)",
                        "CREATE INDEX ix_rule_audit_log_changed_at ON rule_audit_log (changed_at)",
                        "CREATE INDEX ix_rule_audit_log_action ON rule_audit_log (action)",
                        "CREATE INDEX ix_rule_audit_log_risk_level ON rule_audit_log (risk_level)",
                        "CREATE INDEX ix_rule_audit_log_time_risk ON rule_audit_log (changed_at, risk_level)",
                        "CREATE INDEX ix_rule_audit_log_user_action ON rule_audit_log (changed_by, action)"
                    ]
                    
                    for index_sql in audit_indices_sql:
                        conn.execute(text(index_sql))
                    
                    print("   ✓ rule_audit_log 表创建成功")
                
                # 6. 创建表达式安全缓存表
                if 'expression_security_cache' in missing_tables:
                    print("6. 创建 expression_security_cache 表...")
                    create_security_cache_sql = """
                    CREATE TABLE expression_security_cache (
                        id SERIAL PRIMARY KEY,
                        expression_hash VARCHAR(64) NOT NULL UNIQUE,
                        expression_text TEXT NOT NULL,
                        is_safe BOOLEAN NOT NULL,
                        security_issues JSONB,
                        scanned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                    """
                    conn.execute(text(create_security_cache_sql))
                    
                    # 创建索引
                    security_indices_sql = [
                        "CREATE INDEX ix_expression_security_cache_hash ON expression_security_cache (expression_hash)",
                        "CREATE INDEX ix_expression_security_cache_safe ON expression_security_cache (is_safe)",
                        "CREATE INDEX ix_expression_security_safe_scanned ON expression_security_cache (is_safe, scanned_at)"
                    ]
                    
                    for index_sql in security_indices_sql:
                        conn.execute(text(index_sql))
                    
                    print("   ✓ expression_security_cache 表创建成功")
                
                # 提交事务
                trans.commit()
                print("\n✓ 所有表创建完成！事务已提交")
                
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
            # 检查所有表是否创建成功
            expected_tables = [
                'compatibility_rules',
                'compatibility_experiences', 
                'compatibility_cache',
                'compatibility_templates',
                'rule_audit_log',
                'expression_security_cache'
            ]
            
            table_check_sql = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = ANY(%(table_names)s)
            """
            
            result = conn.execute(text(table_check_sql), {"table_names": expected_tables})
            existing_tables = [row[0] for row in result.fetchall()]
            
            print("表创建验证:")
            for table in expected_tables:
                if table in existing_tables:
                    print(f"  ✓ {table}")
                else:
                    print(f"  ✗ {table} (缺失)")
            
            if len(existing_tables) == len(expected_tables):
                print(f"\n✓ 所有 {len(expected_tables)} 个表创建成功")
                
                # 检查约束和索引
                print("\n检查约束和索引...")
                
                # 检查主要约束
                constraint_check_sql = """
                SELECT tc.table_name, tc.constraint_name, tc.constraint_type
                FROM information_schema.table_constraints tc
                WHERE tc.table_name = ANY(%(table_names)s)
                AND tc.constraint_type IN ('PRIMARY KEY', 'FOREIGN KEY', 'CHECK', 'UNIQUE')
                ORDER BY tc.table_name, tc.constraint_type
                """
                
                constraints = conn.execute(text(constraint_check_sql), {"table_names": expected_tables}).fetchall()
                
                constraint_count = len(constraints)
                print(f"  ✓ 发现 {constraint_count} 个约束")
                
                # 检查主要索引
                index_check_sql = """
                SELECT schemaname, tablename, indexname
                FROM pg_indexes
                WHERE tablename = ANY(%(table_names)s)
                AND schemaname = 'public'
                ORDER BY tablename, indexname
                """
                
                indices = conn.execute(text(index_check_sql), {"table_names": expected_tables}).fetchall()
                
                index_count = len(indices)
                print(f"  ✓ 发现 {index_count} 个索引")
                
                return True
            else:
                missing = set(expected_tables) - set(existing_tables)
                print(f"\n✗ 缺失表: {', '.join(missing)}")
                return False
                
    except Exception as e:
        print(f"✗ 验证过程出错: {e}")
        traceback.print_exc()
        return False

def insert_sample_data():
    """插入示例数据"""
    print("\n" + "=" * 60)
    print("插入示例数据")
    print("=" * 60)
    
    try:
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            trans = conn.begin()
            
            try:
                # 检查是否有管理员用户
                admin_check_sql = "SELECT id FROM users WHERE role = 'admin' LIMIT 1"
                admin_result = conn.execute(text(admin_check_sql)).fetchone()
                
                if not admin_result:
                    print("✗ 未找到管理员用户，无法插入示例数据")
                    return False
                
                admin_id = admin_result[0]
                print(f"✓ 使用管理员用户 ID: {admin_id}")
                
                # 插入示例规则
                print("插入示例兼容性规则...")
                
                sample_rules = [
                    {
                        'name': '基础电压匹配检查',
                        'description': '检查两个零件的工作电压是否兼容',
                        'rule_expression': 'part_a.voltage == part_b.voltage',
                        'category_a': '电源',
                        'category_b': '负载设备',
                        'weight': 100,
                        'is_blocking': True
                    },
                    {
                        'name': '尺寸适配检查',
                        'description': '检查零件A是否能物理安装到零件B',
                        'rule_expression': 'part_a.length <= part_b.max_length and part_a.width <= part_b.max_width',
                        'category_a': '插件',
                        'category_b': '插槽',
                        'weight': 90,
                        'is_blocking': True
                    },
                    {
                        'name': '功率余量检查',
                        'description': '确保电源功率有20%以上的余量',
                        'rule_expression': 'part_a.power_rating >= part_b.power_consumption * 1.2',
                        'category_a': '电源',
                        'category_b': '负载设备',
                        'weight': 80,
                        'is_blocking': False
                    }
                ]
                
                for rule in sample_rules:
                    insert_rule_sql = """
                    INSERT INTO compatibility_rules 
                    (name, description, rule_expression, category_a, category_b, weight, is_blocking, created_by)
                    VALUES (%(name)s, %(description)s, %(rule_expression)s, %(category_a)s, %(category_b)s, %(weight)s, %(is_blocking)s, %(created_by)s)
                    """
                    
                    rule['created_by'] = admin_id
                    conn.execute(text(insert_rule_sql), rule)
                    print(f"  ✓ {rule['name']}")
                
                # 插入示例模板
                print("插入示例兼容性模板...")
                
                template_data = {
                    'name': '基础电子设备组合',
                    'description': '常见的电子设备兼容性检查模板',
                    'categories': ['电源', 'CPU', '主板', '内存'],
                    'rules': [
                        {'rule_name': '电压匹配', 'weight': 100},
                        {'rule_name': '接口兼容', 'weight': 100},
                        {'rule_name': '功率检查', 'weight': 80}
                    ],
                    'is_public': True,
                    'created_by': admin_id
                }
                
                insert_template_sql = """
                INSERT INTO compatibility_templates 
                (name, description, categories, rules, is_public, created_by)
                VALUES (%(name)s, %(description)s, %(categories)s, %(rules)s, %(is_public)s, %(created_by)s)
                """
                
                # 将Python对象转换为JSON字符串
                import json
                template_data['categories'] = json.dumps(template_data['categories'])
                template_data['rules'] = json.dumps(template_data['rules'])
                
                conn.execute(text(insert_template_sql), template_data)
                print(f"  ✓ {template_data['name']}")
                
                trans.commit()
                print("✓ 示例数据插入成功")
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"✗ 示例数据插入失败: {e}")
                traceback.print_exc()
                return False
                
    except Exception as e:
        print(f"✗ 插入示例数据时出错: {e}")
        return False

def main():
    """主函数"""
    print("OpenPart 兼容性系统数据库迁移工具")
    print("任务：创建兼容性检查系统相关表")
    
    # 执行迁移
    success = create_compatibility_tables()
    
    if success:
        # 验证迁移
        verify_success = verify_migration()
        
        if verify_success:
            print("\n" + "=" * 60)
            print("✅ 迁移完成并验证成功！")
            
            # 询问是否插入示例数据
            response = input("是否插入示例数据？(y/N): ")
            if response.lower() == 'y':
                sample_success = insert_sample_data()
                if sample_success:
                    print("✅ 示例数据插入成功")
                else:
                    print("⚠️  示例数据插入失败，但迁移成功")
            
            print("✅ 现在可以重启应用并测试兼容性检查功能")
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