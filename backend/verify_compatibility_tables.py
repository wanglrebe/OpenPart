# verify_compatibility_tables.py
"""
验证兼容性系统表是否正确创建

使用方法:
python verify_compatibility_tables.py
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.core.config import settings
    print("✓ 成功导入配置")
except ImportError as e:
    print(f"✗ 导入配置失败: {e}")
    sys.exit(1)

def verify_compatibility_system():
    """验证兼容性系统表"""
    
    print("=" * 60)
    print("验证兼容性系统数据库表")
    print("=" * 60)
    
    try:
        # 连接数据库
        engine = create_engine(settings.database_url)
        print(f"连接数据库: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'localhost'}")
        
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✓ 数据库连接成功")
            
            # 1. 检查表是否存在
            print("\n1. 检查表结构...")
            inspector = inspect(engine)
            all_tables = inspector.get_table_names()
            
            expected_tables = [
                'compatibility_rules',
                'compatibility_experiences', 
                'compatibility_cache',
                'compatibility_templates',
                'rule_audit_log',
                'expression_security_cache'
            ]
            
            print("表存在性检查:")
            missing_tables = []
            for table in expected_tables:
                if table in all_tables:
                    print(f"  ✓ {table}")
                else:
                    print(f"  ✗ {table} (缺失)")
                    missing_tables.append(table)
            
            if missing_tables:
                print(f"\n❌ 缺失表: {', '.join(missing_tables)}")
                return False
            
            # 2. 检查表结构
            print("\n2. 检查表结构详情...")
            
            for table_name in expected_tables:
                print(f"\n表: {table_name}")
                columns = inspector.get_columns(table_name)
                print(f"  字段数: {len(columns)}")
                
                # 显示关键字段
                key_columns = []
                for col in columns:
                    if col['name'] in ['id', 'name', 'rule_expression', 'part_a_id', 'part_b_id']:
                        key_columns.append(f"{col['name']}({col['type']})")
                
                if key_columns:
                    print(f"  关键字段: {', '.join(key_columns)}")
            
            # 3. 检查外键约束
            print("\n3. 检查外键约束...")
            
            fk_tables = ['compatibility_rules', 'compatibility_experiences', 'compatibility_templates', 'rule_audit_log']
            total_fks = 0
            
            for table_name in fk_tables:
                fks = inspector.get_foreign_keys(table_name)
                print(f"  {table_name}: {len(fks)} 个外键")
                total_fks += len(fks)
            
            print(f"总外键数: {total_fks}")
            
            # 4. 检查索引
            print("\n4. 检查索引...")
            
            total_indexes = 0
            for table_name in expected_tables:
                indexes = inspector.get_indexes(table_name)
                unique_indexes = len([idx for idx in indexes if idx['unique']])
                regular_indexes = len(indexes) - unique_indexes
                print(f"  {table_name}: {regular_indexes} 个普通索引, {unique_indexes} 个唯一索引")
                total_indexes += len(indexes)
            
            print(f"总索引数: {total_indexes}")
            
            # 5. 测试基本操作
            print("\n5. 测试基本数据库操作...")
            
            try:
                # 测试插入（如果有管理员用户）
                admin_check = conn.execute(text("SELECT id FROM users WHERE role = 'admin' LIMIT 1")).fetchone()
                
                if admin_check:
                    admin_id = admin_check[0]
                    print(f"  ✓ 找到管理员用户 ID: {admin_id}")
                    
                    # 测试规则表插入
                    test_rule_sql = """
                    INSERT INTO compatibility_rules 
                    (name, rule_expression, category_a, category_b, created_by)
                    VALUES ('测试规则', 'part_a.test == part_b.test', '测试类别A', '测试类别B', :admin_id)
                    RETURNING id
                    """
                    
                    result = conn.execute(text(test_rule_sql), {"admin_id": admin_id})
                    test_rule_id = result.fetchone()[0]
                    print(f"  ✓ 测试规则插入成功 ID: {test_rule_id}")
                    
                    # 立即删除测试数据
                    conn.execute(text("DELETE FROM compatibility_rules WHERE id = :rule_id"), {"rule_id": test_rule_id})
                    print("  ✓ 测试数据清理完成")
                    
                    # 提交测试事务
                    conn.commit()
                    
                else:
                    print("  ⚠️  未找到管理员用户，跳过插入测试")
                
            except Exception as e:
                print(f"  ⚠️  基本操作测试失败: {str(e)}")
                conn.rollback()
            
            # 6. 统计当前数据
            print("\n6. 当前数据统计...")
            
            data_tables = ['compatibility_rules', 'compatibility_experiences', 'compatibility_templates']
            
            for table_name in data_tables:
                try:
                    count_sql = f"SELECT COUNT(*) FROM {table_name}"
                    count = conn.execute(text(count_sql)).scalar()
                    print(f"  {table_name}: {count} 条记录")
                except Exception as e:
                    print(f"  {table_name}: 查询失败 - {str(e)}")
            
            print("\n" + "=" * 60)
            print("✅ 兼容性系统验证完成！")
            print("✅ 所有表结构正确，可以开始使用兼容性功能")
            print("=" * 60)
            
            return True
            
    except Exception as e:
        print(f"\n❌ 验证过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_sample_data():
    """检查是否有示例数据，如果没有则询问是否添加"""
    
    try:
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            # 检查规则数量
            rule_count = conn.execute(text("SELECT COUNT(*) FROM compatibility_rules")).scalar()
            template_count = conn.execute(text("SELECT COUNT(*) FROM compatibility_templates")).scalar()
            
            if rule_count == 0 and template_count == 0:
                print("\n📝 当前没有示例数据")
                response = input("是否添加示例规则和模板？(y/N): ")
                
                if response.lower() == 'y':
                    return add_sample_data()
            else:
                print(f"\n📊 当前有 {rule_count} 个规则和 {template_count} 个模板")
            
            return True
            
    except Exception as e:
        print(f"检查示例数据时出错: {str(e)}")
        return False

def add_sample_data():
    """添加示例数据"""
    
    try:
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            trans = conn.begin()
            
            try:
                # 获取管理员ID
                admin_result = conn.execute(text("SELECT id FROM users WHERE role = 'admin' LIMIT 1")).fetchone()
                
                if not admin_result:
                    print("❌ 未找到管理员用户，无法添加示例数据")
                    return False
                
                admin_id = admin_result[0]
                
                # 添加示例规则
                sample_rules = [
                    ("电压匹配检查", "检查两个零件的工作电压是否兼容", "part_a.voltage == part_b.voltage", "电源", "负载设备", 100, True),
                    ("尺寸适配检查", "检查零件A是否能物理安装到零件B", "part_a.length <= part_b.max_length and part_a.width <= part_b.max_width", "插件", "插槽", 90, True),
                    ("功率余量检查", "确保电源功率有20%以上的余量", "part_a.power_rating >= part_b.power_consumption * 1.2", "电源", "负载设备", 80, False)
                ]
                
                print("添加示例规则...")
                for name, desc, expr, cat_a, cat_b, weight, blocking in sample_rules:
                    insert_sql = """
                    INSERT INTO compatibility_rules 
                    (name, description, rule_expression, category_a, category_b, weight, is_blocking, created_by)
                    VALUES (:name, :desc, :expr, :cat_a, :cat_b, :weight, :blocking, :admin_id)
                    """
                    
                    conn.execute(text(insert_sql), {
                        "name": name, "desc": desc, "expr": expr,
                        "cat_a": cat_a, "cat_b": cat_b, "weight": weight,
                        "blocking": blocking, "admin_id": admin_id
                    })
                    print(f"  ✓ {name}")
                
                # 添加示例模板
                import json
                template_data = {
                    "name": "基础电子设备组合",
                    "description": "常见的电子设备兼容性检查模板",
                    "categories": json.dumps(["电源", "CPU", "主板", "内存"]),
                    "rules": json.dumps([
                        {"rule_name": "电压匹配", "weight": 100},
                        {"rule_name": "接口兼容", "weight": 100},
                        {"rule_name": "功率检查", "weight": 80}
                    ]),
                    "is_public": True,
                    "created_by": admin_id
                }
                
                print("添加示例模板...")
                template_sql = """
                INSERT INTO compatibility_templates 
                (name, description, categories, rules, is_public, created_by)
                VALUES (:name, :description, :categories, :rules, :is_public, :created_by)
                """
                
                conn.execute(text(template_sql), template_data)
                print(f"  ✓ {template_data['name']}")
                
                trans.commit()
                print("✅ 示例数据添加成功")
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ 添加示例数据失败: {str(e)}")
                return False
                
    except Exception as e:
        print(f"❌ 添加示例数据时出错: {str(e)}")
        return False

def main():
    """主函数"""
    print("OpenPart 兼容性系统验证工具")
    
    # 验证表结构
    if verify_compatibility_system():
        # 检查示例数据
        check_sample_data()
        
        print("\n🎉 验证完成！你现在可以：")
        print("1. 重启后端服务器")
        print("2. 在管理后台添加兼容性规则")
        print("3. 在用户界面测试兼容性检查功能")
    else:
        print("\n❌ 验证失败，请检查数据库迁移")

if __name__ == "__main__":
    main()