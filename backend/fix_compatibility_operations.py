# fix_compatibility_operations.py
"""
数据库迁移脚本 - 修复兼容性系统的删除和停用功能

使用方法:
python fix_compatibility_operations.py

这个脚本会：
1. 更新审计日志表约束，支持新的操作类型（disable/enable）
2. 为现有的停用/启用操作补充审计记录
3. 创建优化查询的索引
4. 验证迁移结果
5. 清理可能的脏数据
"""

import os
import sys
import traceback
from datetime import datetime
from sqlalchemy import create_engine, text, MetaData, inspect
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

def check_table_exists(engine, table_name):
    """检查表是否存在"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return table_name in tables
    except Exception as e:
        print(f"检查表是否存在时出错: {e}")
        return False

def check_constraint_exists(engine, table_name, constraint_name):
    """检查约束是否存在"""
    try:
        with engine.connect() as conn:
            check_sql = """
            SELECT constraint_name 
            FROM information_schema.check_constraints 
            WHERE constraint_name = :constraint_name
            """
            result = conn.execute(text(check_sql), {"constraint_name": constraint_name}).fetchone()
            return result is not None
    except Exception as e:
        print(f"检查约束时出错: {e}")
        return False

def check_index_exists(engine, index_name):
    """检查索引是否存在"""
    try:
        with engine.connect() as conn:
            check_sql = """
            SELECT indexname 
            FROM pg_indexes 
            WHERE indexname = :index_name
            """
            result = conn.execute(text(check_sql), {"index_name": index_name}).fetchone()
            return result is not None
    except Exception as e:
        print(f"检查索引时出错: {e}")
        return False

def get_current_constraint_definition(engine, table_name, constraint_name):
    """获取当前约束定义"""
    try:
        with engine.connect() as conn:
            check_sql = """
            SELECT check_clause 
            FROM information_schema.check_constraints 
            WHERE constraint_name = :constraint_name
            """
            result = conn.execute(text(check_sql), {"constraint_name": constraint_name}).fetchone()
            return result[0] if result else None
    except Exception as e:
        print(f"获取约束定义时出错: {e}")
        return None

def fix_compatibility_operations():
    """修复兼容性操作功能"""
    
    print("=" * 70)
    print("开始数据库迁移：修复兼容性系统删除和停用功能")
    print("=" * 70)
    
    try:
        # 创建数据库连接
        print(f"连接数据库: {settings.database_url}")
        engine = create_engine(settings.database_url)
        
        # 测试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ 数据库连接成功")
        
        # 检查必要的表是否存在
        required_tables = ['compatibility_rules', 'rule_audit_log', 'users']
        
        for table in required_tables:
            if not check_table_exists(engine, table):
                print(f"✗ 必需表 {table} 不存在，请先创建基础表结构")
                return False
            print(f"✓ 表 {table} 存在")
        
        # 执行迁移
        with engine.connect() as conn:
            # 开始事务
            trans = conn.begin()
            
            try:
                print("\n" + "=" * 50)
                print("开始执行迁移操作")
                print("=" * 50)
                
                # 1. 更新审计日志约束
                print("1. 更新审计日志表约束...")
                
                # 检查当前约束
                current_constraint = get_current_constraint_definition(engine, 'rule_audit_log', 'check_audit_action')
                print(f"   当前约束定义: {current_constraint}")
                
                # 删除旧约束
                if current_constraint:
                    drop_constraint_sql = """
                    ALTER TABLE rule_audit_log 
                    DROP CONSTRAINT IF EXISTS check_audit_action
                    """
                    conn.execute(text(drop_constraint_sql))
                    print("   ✓ 删除旧约束成功")
                
                # 添加新约束
                add_constraint_sql = """
                ALTER TABLE rule_audit_log 
                ADD CONSTRAINT check_audit_action 
                CHECK (action IN ('create', 'update', 'delete', 'disable', 'enable', 'test', 'validate'))
                """
                conn.execute(text(add_constraint_sql))
                print("   ✓ 添加新约束成功 (支持 disable/enable 操作)")
                
                # 2. 创建优化索引
                print("2. 创建优化索引...")
                
                index_name = "idx_audit_log_disable_enable"
                if not check_index_exists(engine, index_name):
                    create_index_sql = """
                    CREATE INDEX idx_audit_log_disable_enable 
                    ON rule_audit_log(action, changed_at) 
                    WHERE action IN ('disable', 'enable')
                    """
                    conn.execute(text(create_index_sql))
                    print(f"   ✓ 创建索引 {index_name} 成功")
                else:
                    print(f"   ✓ 索引 {index_name} 已存在")
                
                # 3. 补充历史审计记录
                print("3. 补充历史审计记录...")
                
                # 检查是否有规则但缺少审计记录
                check_missing_sql = """
                SELECT 
                    cr.id,
                    cr.name,
                    cr.is_active,
                    cr.created_by,
                    cr.updated_at,
                    cr.created_at
                FROM compatibility_rules cr
                LEFT JOIN rule_audit_log ral ON ral.rule_id = cr.id 
                    AND ral.action IN ('create', 'enable', 'disable')
                WHERE ral.id IS NULL
                ORDER BY cr.id
                """
                
                missing_records = conn.execute(text(check_missing_sql)).fetchall()
                print(f"   发现 {len(missing_records)} 个规则缺少审计记录")
                
                if missing_records:
                    # 为缺少审计记录的规则补充记录
                    insert_audit_sql = """
                    INSERT INTO rule_audit_log 
                    (rule_id, action, changed_by, changed_at, risk_level, validation_result)
                    VALUES (:rule_id, :action, :changed_by, :changed_at, :risk_level, :validation_result)
                    """
                    
                    for record in missing_records:
                        rule_id, name, is_active, created_by, updated_at, created_at = record
                        
                        # 添加创建记录
                        conn.execute(text(insert_audit_sql), {
                            "rule_id": rule_id,
                            "action": "create",
                            "changed_by": created_by,
                            "changed_at": created_at,
                            "risk_level": "medium",
                            "validation_result": '{"migration": true, "note": "Historical create operation reconstruction"}'
                        })
                        
                        # 如果有更新时间且与创建时间不同，添加状态记录
                        if updated_at and updated_at != created_at:
                            action = "enable" if is_active else "disable"
                            conn.execute(text(insert_audit_sql), {
                                "rule_id": rule_id,
                                "action": action,
                                "changed_by": created_by,
                                "changed_at": updated_at,
                                "risk_level": "medium",
                                "validation_result": f'{{"migration": true, "note": "Historical {action} operation reconstruction"}}'
                            })
                    
                    print(f"   ✓ 补充了 {len(missing_records)} 个规则的审计记录")
                
                # 4. 清理数据完整性
                print("4. 清理数据完整性...")
                
                # 确保所有规则都有 is_active 值
                fix_active_sql = """
                UPDATE compatibility_rules 
                SET is_active = COALESCE(is_active, true),
                    updated_at = COALESCE(updated_at, created_at)
                WHERE is_active IS NULL OR updated_at IS NULL
                """
                affected = conn.execute(text(fix_active_sql))
                print(f"   ✓ 修复了 {affected.rowcount} 个规则的数据完整性")
                
                # 5. 添加列注释
                print("5. 更新表注释...")
                
                comment_sql = """
                COMMENT ON COLUMN rule_audit_log.action IS 
                '操作类型: create(创建), update(更新), delete(物理删除), disable(停用), enable(启用), test(测试), validate(验证)'
                """
                conn.execute(text(comment_sql))
                print("   ✓ 更新列注释成功")
                
                # 6. 验证迁移结果
                print("6. 验证迁移结果...")
                
                # 验证约束
                new_constraint = get_current_constraint_definition(engine, 'rule_audit_log', 'check_audit_action')
                if 'disable' in new_constraint and 'enable' in new_constraint:
                    print("   ✓ 约束验证成功: 支持新的操作类型")
                else:
                    raise Exception("约束验证失败")
                
                # 验证索引
                if check_index_exists(engine, "idx_audit_log_disable_enable"):
                    print("   ✓ 索引验证成功")
                else:
                    print("   ⚠ 索引验证失败，但不影响核心功能")
                
                # 验证审计记录数量
                audit_count_sql = """
                SELECT 
                    action,
                    COUNT(*) as count
                FROM rule_audit_log 
                GROUP BY action
                ORDER BY action
                """
                audit_counts = conn.execute(text(audit_count_sql)).fetchall()
                print("   审计记录统计:")
                for action, count in audit_counts:
                    print(f"     - {action}: {count} 条")
                
                # 验证规则状态
                rule_status_sql = """
                SELECT 
                    is_active,
                    COUNT(*) as count
                FROM compatibility_rules 
                GROUP BY is_active
                """
                rule_status = conn.execute(text(rule_status_sql)).fetchall()
                print("   规则状态统计:")
                for status, count in rule_status:
                    status_text = "启用" if status else "停用"
                    print(f"     - {status_text}: {count} 个规则")
                
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
    print("\n" + "=" * 70)
    print("验证迁移结果")
    print("=" * 70)
    
    try:
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            # 1. 验证约束
            print("1. 验证审计日志约束...")
            constraint_sql = """
            SELECT check_clause 
            FROM information_schema.check_constraints 
            WHERE constraint_name = 'check_audit_action'
            """
            constraint = conn.execute(text(constraint_sql)).fetchone()
            
            if constraint and 'disable' in constraint[0] and 'enable' in constraint[0]:
                print("   ✓ 约束验证成功: 支持所有操作类型")
                print(f"   约束定义: {constraint[0]}")
            else:
                print("   ✗ 约束验证失败")
                return False
            
            # 2. 验证索引
            print("2. 验证索引...")
            index_sql = """
            SELECT indexname, indexdef
            FROM pg_indexes 
            WHERE indexname = 'idx_audit_log_disable_enable'
            """
            index = conn.execute(text(index_sql)).fetchone()
            
            if index:
                print(f"   ✓ 索引验证成功: {index[0]}")
            else:
                print("   ⚠ 索引可能不存在，但不影响核心功能")
            
            # 3. 验证数据完整性
            print("3. 验证数据完整性...")
            
            # 检查是否有空的 is_active 值
            null_active_sql = """
            SELECT COUNT(*) 
            FROM compatibility_rules 
            WHERE is_active IS NULL
            """
            null_count = conn.execute(text(null_active_sql)).scalar()
            
            if null_count == 0:
                print("   ✓ 所有规则都有有效的 is_active 值")
            else:
                print(f"   ⚠ 发现 {null_count} 个规则缺少 is_active 值")
            
            # 4. 测试新操作类型
            print("4. 测试新操作类型...")
            
            # 尝试插入测试记录（然后删除）
            test_sql = """
            INSERT INTO rule_audit_log 
            (rule_id, action, changed_by, changed_at, risk_level)
            VALUES (NULL, 'disable', 1, NOW(), 'medium')
            RETURNING id
            """
            
            try:
                result = conn.execute(text(test_sql))
                test_id = result.fetchone()[0]
                
                # 删除测试记录
                conn.execute(text("DELETE FROM rule_audit_log WHERE id = :id"), {"id": test_id})
                conn.commit()
                
                print("   ✓ 新操作类型测试成功")
            except Exception as e:
                print(f"   ✗ 新操作类型测试失败: {e}")
                return False
            
            # 5. 显示最终统计
            print("5. 最终统计...")
            
            stats_sql = """
            SELECT 
                (SELECT COUNT(*) FROM compatibility_rules) as total_rules,
                (SELECT COUNT(*) FROM compatibility_rules WHERE is_active = true) as active_rules,
                (SELECT COUNT(*) FROM compatibility_rules WHERE is_active = false) as inactive_rules,
                (SELECT COUNT(*) FROM rule_audit_log) as total_audit_logs,
                (SELECT COUNT(*) FROM rule_audit_log WHERE action IN ('disable', 'enable')) as status_change_logs
            """
            
            stats = conn.execute(text(stats_sql)).fetchone()
            
            print(f"   - 总规则数: {stats[0]}")
            print(f"   - 启用规则: {stats[1]}")
            print(f"   - 停用规则: {stats[2]}")
            print(f"   - 总审计记录: {stats[3]}")
            print(f"   - 状态变更记录: {stats[4]}")
            
            return True
                
    except Exception as e:
        print(f"✗ 验证过程出错: {e}")
        traceback.print_exc()
        return False

def show_api_changes():
    """显示API变更说明"""
    print("\n" + "=" * 70)
    print("🔧 API变更说明")
    print("=" * 70)
    
    changes = [
        "新增API端点:",
        "  PATCH /api/admin/compatibility/rules/{rule_id}/disable  - 停用规则",
        "  PATCH /api/admin/compatibility/rules/{rule_id}/enable   - 启用规则",
        "  PATCH /api/admin/compatibility/rules/batch/disable      - 批量停用",
        "  PATCH /api/admin/compatibility/rules/batch/enable       - 批量启用",
        "",
        "变更的API端点:",
        "  DELETE /api/admin/compatibility/rules/{rule_id}         - 现在是真正的删除",
        "    * 支持 ?force=true 参数强制删除有依赖的规则",
        "    * 会检查依赖关系，防止数据完整性问题",
        "",
        "新增审计操作类型:",
        "  - disable: 停用规则",
        "  - enable:  启用规则", 
        "  - delete:  物理删除规则（高风险操作）",
        "",
        "重要提醒:",
        "  ⚠️  DELETE 操作现在是不可逆的物理删除",
        "  ✅  使用 disable/enable 进行可逆的状态管理",
        "  📝  所有操作都会记录详细的审计日志"
    ]
    
    for change in changes:
        print(change)

def main():
    """主函数"""
    print("OpenPart 数据库迁移工具")
    print("任务：修复兼容性系统的删除和停用功能")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 确认操作
    print("\n⚠️  这个迁移会修改数据库结构和数据，请确保已备份数据库")
    response = input("是否继续执行迁移？(y/N): ")
    
    if response.lower() != 'y':
        print("迁移已取消")
        return
    
    # 执行迁移
    success = fix_compatibility_operations()
    
    if success:
        # 验证迁移
        verify_success = verify_migration()
        
        if verify_success:
            print("\n" + "=" * 70)
            print("✅ 迁移完成并验证成功！")
            print("✅ 兼容性系统的删除和停用功能已修复")
            
            # 显示API变更
            show_api_changes()
            
            print("\n✅ 现在可以重启应用并测试新的API功能")
            print("=" * 70)
        else:
            print("\n" + "=" * 70)
            print("⚠️  迁移可能完成但验证失败")
            print("⚠️  建议手动检查数据库和API功能")
            print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("❌ 迁移失败")
        print("❌ 请检查错误信息并修复问题后重试")
        print("❌ 如果数据库有问题，请从备份恢复")
        print("=" * 70)

if __name__ == "__main__":
    main()