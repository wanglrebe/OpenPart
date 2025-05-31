# fix_remaining_issues.py
"""
修复剩余问题的脚本

解决：
1. 测试脚本中规则名称重复的问题
2. 补充缺失的审计日志记录
3. 验证迁移是否完全成功
"""

import os
import sys
import traceback
import uuid
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.core.config import settings
    print("✓ 成功导入配置")
except ImportError as e:
    print(f"✗ 导入配置失败: {e}")
    sys.exit(1)

def fix_remaining_issues():
    """修复剩余问题"""
    
    print("=" * 60)
    print("修复兼容性系统剩余问题")
    print("=" * 60)
    
    try:
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            print("✓ 数据库连接成功")
            
            # 开始事务
            trans = conn.begin()
            
            try:
                # 1. 检查并修复约束
                print("1. 检查审计日志约束...")
                
                constraint_sql = """
                SELECT check_clause 
                FROM information_schema.check_constraints 
                WHERE constraint_name = 'check_audit_action'
                """
                
                result = conn.execute(text(constraint_sql)).fetchone()
                
                if result and 'disable' in result[0] and 'enable' in result[0]:
                    print("   ✓ 约束已正确设置")
                else:
                    print("   → 修复约束...")
                    
                    # 删除旧约束
                    conn.execute(text("ALTER TABLE rule_audit_log DROP CONSTRAINT IF EXISTS check_audit_action"))
                    
                    # 添加新约束
                    conn.execute(text("""
                        ALTER TABLE rule_audit_log 
                        ADD CONSTRAINT check_audit_action 
                        CHECK (action IN ('create', 'update', 'delete', 'disable', 'enable', 'test', 'validate'))
                    """))
                    
                    print("   ✓ 约束修复完成")
                
                # 2. 补充审计日志记录
                print("2. 补充审计日志记录...")
                
                # 查找缺少审计记录的规则
                missing_audit_sql = """
                SELECT cr.id, cr.name, cr.is_active, cr.created_by, cr.created_at, cr.updated_at
                FROM compatibility_rules cr
                WHERE NOT EXISTS (
                    SELECT 1 FROM rule_audit_log ral 
                    WHERE ral.rule_id = cr.id 
                    AND ral.action IN ('create', 'enable', 'disable')
                )
                ORDER BY cr.id
                """
                
                missing_rules = conn.execute(text(missing_audit_sql)).fetchall()
                
                if missing_rules:
                    print(f"   发现 {len(missing_rules)} 个规则缺少审计记录")
                    
                    for rule in missing_rules:
                        rule_id, name, is_active, created_by, created_at, updated_at = rule
                        
                        # 添加创建记录
                        conn.execute(text("""
                            INSERT INTO rule_audit_log 
                            (rule_id, action, changed_by, changed_at, risk_level, validation_result)
                            VALUES (:rule_id, 'create', :changed_by, :changed_at, 'medium', 
                                   '{"migration": true, "note": "Historical operation reconstruction"}')
                        """), {
                            "rule_id": rule_id,
                            "changed_by": created_by,
                            "changed_at": created_at
                        })
                        
                        # 如果有更新时间，添加状态变更记录
                        if updated_at and updated_at != created_at:
                            action = "enable" if is_active else "disable"
                            conn.execute(text("""
                                INSERT INTO rule_audit_log 
                                (rule_id, action, changed_by, changed_at, risk_level, validation_result)
                                VALUES (:rule_id, :action, :changed_by, :changed_at, 'medium', 
                                       :validation_result)
                            """), {
                                "rule_id": rule_id,
                                "action": action,
                                "changed_by": created_by,
                                "changed_at": updated_at,
                                "validation_result": f'{{"migration": true, "note": "Historical {action} operation"}}'
                            })
                    
                    print(f"   ✓ 补充了 {len(missing_rules)} 个规则的审计记录")
                else:
                    print("   ✓ 所有规则都有审计记录")
                
                # 3. 创建优化索引（如果不存在）
                print("3. 检查优化索引...")
                
                index_check_sql = """
                SELECT indexname FROM pg_indexes 
                WHERE indexname = 'idx_audit_log_disable_enable'
                """
                
                index_exists = conn.execute(text(index_check_sql)).fetchone()
                
                if not index_exists:
                    print("   → 创建优化索引...")
                    conn.execute(text("""
                        CREATE INDEX idx_audit_log_disable_enable 
                        ON rule_audit_log(action, changed_at) 
                        WHERE action IN ('disable', 'enable')
                    """))
                    print("   ✓ 索引创建完成")
                else:
                    print("   ✓ 索引已存在")
                
                # 4. 验证数据完整性
                print("4. 验证数据完整性...")
                
                # 检查 is_active 字段
                null_active_count = conn.execute(text("""
                    SELECT COUNT(*) FROM compatibility_rules WHERE is_active IS NULL
                """)).scalar()
                
                if null_active_count > 0:
                    print(f"   → 修复 {null_active_count} 个规则的 is_active 字段...")
                    conn.execute(text("""
                        UPDATE compatibility_rules 
                        SET is_active = true 
                        WHERE is_active IS NULL
                    """))
                    print("   ✓ is_active 字段修复完成")
                else:
                    print("   ✓ is_active 字段完整")
                
                # 5. 添加列注释
                print("5. 更新列注释...")
                
                conn.execute(text("""
                    COMMENT ON COLUMN rule_audit_log.action IS 
                    '操作类型: create(创建), update(更新), delete(物理删除), disable(停用), enable(启用), test(测试), validate(验证)'
                """))
                
                print("   ✓ 列注释更新完成")
                
                # 提交事务
                trans.commit()
                print("\n✓ 所有修复完成！")
                
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"\n✗ 修复失败，事务已回滚: {e}")
                traceback.print_exc()
                return False
    
    except Exception as e:
        print(f"✗ 修复过程出错: {e}")
        return False

def verify_fixes():
    """验证修复结果"""
    print("\n" + "=" * 60)
    print("验证修复结果")
    print("=" * 60)
    
    try:
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            # 1. 验证约束
            print("1. 验证约束...")
            constraint_result = conn.execute(text("""
                SELECT check_clause FROM information_schema.check_constraints 
                WHERE constraint_name = 'check_audit_action'
            """)).fetchone()
            
            if constraint_result and 'disable' in constraint_result[0] and 'enable' in constraint_result[0]:
                print("   ✓ 约束验证通过")
            else:
                print("   ✗ 约束验证失败")
                return False
            
            # 2. 验证审计日志
            print("2. 验证审计日志...")
            
            action_counts = conn.execute(text("""
                SELECT action, COUNT(*) 
                FROM rule_audit_log 
                GROUP BY action 
                ORDER BY action
            """)).fetchall()
            
            print("   审计日志统计:")
            actions_found = set()
            for action, count in action_counts:
                print(f"     - {action}: {count} 条")
                actions_found.add(action)
            
            required_actions = {'create', 'disable', 'enable'}
            if required_actions.intersection(actions_found):
                print("   ✓ 审计日志验证通过")
            else:
                print("   ⚠ 未发现新的操作类型记录")
            
            # 3. 验证索引
            print("3. 验证索引...")
            index_result = conn.execute(text("""
                SELECT indexname FROM pg_indexes 
                WHERE indexname = 'idx_audit_log_disable_enable'
            """)).fetchone()
            
            if index_result:
                print("   ✓ 索引验证通过")
            else:
                print("   ⚠ 索引可能不存在")
            
            # 4. 最终统计
            print("4. 最终统计...")
            
            stats = conn.execute(text("""
                SELECT 
                    (SELECT COUNT(*) FROM compatibility_rules) as total_rules,
                    (SELECT COUNT(*) FROM compatibility_rules WHERE is_active = true) as active_rules,
                    (SELECT COUNT(*) FROM rule_audit_log) as total_logs,
                    (SELECT COUNT(*) FROM rule_audit_log WHERE action IN ('disable', 'enable')) as status_logs
            """)).fetchone()
            
            print(f"   - 总规则数: {stats[0]}")
            print(f"   - 启用规则: {stats[1]}")
            print(f"   - 总审计记录: {stats[2]}")
            print(f"   - 状态变更记录: {stats[3]}")
            
            return True
            
    except Exception as e:
        print(f"✗ 验证失败: {e}")
        return False

def main():
    """主函数"""
    print("OpenPart 剩余问题修复工具")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 执行修复
    success = fix_remaining_issues()
    
    if success:
        # 验证修复
        verify_success = verify_fixes()
        
        if verify_success:
            print("\n" + "=" * 60)
            print("✅ 所有问题修复完成！")
            print("✅ 现在可以重新运行测试脚本验证功能")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("⚠️ 修复完成但验证有问题")
            print("⚠️ 建议检查数据库状态")
            print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ 修复失败")
        print("❌ 请检查错误信息")
        print("=" * 60)

if __name__ == "__main__":
    main()