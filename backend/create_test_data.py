# backend/create_test_data.py
"""
创建测试数据，用于兼容性API测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.part import Part
from app.models.compatibility import CompatibilityRule, CompatibilityExperience
from app.auth.models import User, UserRole
from app.auth.security import get_password_hash

def create_test_data():
    """创建测试数据"""
    print("🚀 开始创建测试数据...")
    
    db = SessionLocal()
    
    try:
        # 1. 创建测试管理员用户（如果不存在）
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print("✅ 创建了管理员用户: admin/admin123")
        else:
            print("✅ 管理员用户已存在")
        
        # 2. 创建测试零件
        test_parts = [
            Part(
                name="Intel Core i7-12700K",
                category="CPU",
                description="Intel 第12代处理器",
                properties={
                    "voltage": 12,
                    "power_consumption": 125,
                    "socket": "LGA1700",
                    "frequency": 3600,
                    "cores": 12,
                    "tdp": 125
                }
            ),
            Part(
                name="华硕 ROG Maximus Z690",
                category="主板",
                description="华硕高端主板",
                properties={
                    "voltage": 12,
                    "max_power": 200,
                    "socket": "LGA1700",
                    "min_freq": 2000,
                    "max_freq": 5000,
                    "form_factor": "ATX",
                    "max_memory": 128
                }
            ),
            Part(
                name="海盗船 RM750x",
                category="电源",
                description="750W模组化电源",
                properties={
                    "voltage": 12,
                    "wattage": 750,
                    "efficiency": 80,
                    "form_factor": "ATX",
                    "modular": True
                }
            ),
            Part(
                name="RTX 4070 Ti",
                category="显卡",
                description="NVIDIA RTX 4070 Ti显卡",
                properties={
                    "voltage": 12,
                    "power_consumption": 285,
                    "length": 305,
                    "width": 137,
                    "height": 61,
                    "pcie_slots": 2.75
                }
            ),
            Part(
                name="Kingston Fury DDR5-5600",
                category="内存",
                description="金士顿DDR5内存",
                properties={
                    "voltage": 1.25,
                    "frequency": 5600,
                    "capacity": 16,
                    "type": "DDR5",
                    "timing": "40-40-40-80"
                }
            ),
            Part(
                name="九州风神 AK620",
                category="散热器",
                description="九州风神双塔风冷散热器",
                properties={
                    "socket": "LGA1700",
                    "max_power": 250,
                    "height": 160,
                    "fan_count": 2,
                    "noise_level": 24.6
                }
            )
        ]
        
        # 检查零件是否已存在，避免重复创建
        existing_parts = {}
        for part in test_parts:
            existing = db.query(Part).filter(Part.name == part.name).first()
            if not existing:
                db.add(part)
                db.commit()
                db.refresh(part)
                existing_parts[part.name] = part
                print(f"✅ 创建零件: {part.name} (ID: {part.id})")
            else:
                existing_parts[part.name] = existing
                print(f"✅ 零件已存在: {part.name} (ID: {existing.id})")
        
        # 3. 创建兼容性规则
        rules = [
            {
                "name": "接口匹配检查",
                "description": "CPU和主板的接口必须匹配",
                "rule_expression": "part_a.socket == part_b.socket",
                "category_a": "CPU",
                "category_b": "主板",
                "weight": 100,
                "is_blocking": True
            },
            {
                "name": "CPU功耗检查",
                "description": "CPU功耗不能超过主板最大支持功率",
                "rule_expression": "part_a.power_consumption <= part_b.max_power",
                "category_a": "CPU",
                "category_b": "主板",
                "weight": 90,
                "is_blocking": False
            },
            {
                "name": "散热器兼容性",
                "description": "散热器必须支持CPU接口",
                "rule_expression": "part_a.socket == part_b.socket",
                "category_a": "CPU",
                "category_b": "散热器",
                "weight": 100,
                "is_blocking": True
            },
            {
                "name": "散热器功率检查",
                "description": "散热器最大功率应大于CPU TDP",
                "rule_expression": "part_a.tdp <= part_b.max_power",
                "category_a": "CPU",
                "category_b": "散热器",
                "weight": 85,
                "is_blocking": False
            },
            {
                "name": "电源功率检查",
                "description": "电源功率必须足够",
                "rule_expression": "safe_get(part_a, 'power_consumption', 0) + safe_get(part_b, 'power_consumption', 0) <= 600",
                "category_a": "CPU",
                "category_b": "显卡",
                "weight": 95,
                "is_blocking": True
            },
            {
                "name": "内存频率兼容",
                "description": "内存频率应在主板支持范围内",
                "rule_expression": "part_a.frequency >= part_b.min_freq and part_a.frequency <= part_b.max_freq",
                "category_a": "内存",
                "category_b": "主板",
                "weight": 80,
                "is_blocking": False
            }
        ]
        
        for rule_data in rules:
            existing = db.query(CompatibilityRule).filter(
                CompatibilityRule.name == rule_data["name"]
            ).first()
            
            if not existing:
                rule = CompatibilityRule(
                    **rule_data,
                    created_by=admin_user.id
                )
                db.add(rule)
                db.commit()
                db.refresh(rule)
                print(f"✅ 创建规则: {rule.name} (ID: {rule.id})")
            else:
                print(f"✅ 规则已存在: {rule_data['name']}")
        
        # 4. 创建兼容性经验
        cpu = existing_parts["Intel Core i7-12700K"]
        motherboard = existing_parts["华硕 ROG Maximus Z690"]
        cooler = existing_parts["九州风神 AK620"]
        
        experiences = [
            {
                "part_a_id": cpu.id,
                "part_b_id": motherboard.id,
                "compatibility_status": "compatible",
                "compatibility_score": 95,
                "notes": "完美兼容，性能表现优秀",
                "source": "admin",
                "verification_status": "verified"
            },
            {
                "part_a_id": cpu.id,
                "part_b_id": cooler.id,
                "compatibility_status": "compatible",
                "compatibility_score": 90,
                "notes": "兼容性良好，温度控制理想",
                "source": "admin",
                "verification_status": "verified"
            }
        ]
        
        for exp_data in experiences:
            existing = db.query(CompatibilityExperience).filter(
                CompatibilityExperience.part_a_id == exp_data["part_a_id"],
                CompatibilityExperience.part_b_id == exp_data["part_b_id"]
            ).first()
            
            if not existing:
                experience = CompatibilityExperience(
                    **exp_data,
                    added_by=admin_user.id
                )
                db.add(experience)
                db.commit()
                db.refresh(experience)
                print(f"✅ 创建经验: 零件{exp_data['part_a_id']} + 零件{exp_data['part_b_id']}")
            else:
                print(f"✅ 经验已存在: 零件{exp_data['part_a_id']} + 零件{exp_data['part_b_id']}")
        
        print("\n🎉 测试数据创建完成！")
        print("\n📊 数据统计:")
        print(f"  - 零件数量: {db.query(Part).count()}")
        print(f"  - 兼容性规则: {db.query(CompatibilityRule).count()}")
        print(f"  - 兼容性经验: {db.query(CompatibilityExperience).count()}")
        print(f"  - 用户数量: {db.query(User).count()}")
        
        print("\n🧪 可以测试的API示例:")
        print("1. 健康检查:")
        print("   GET http://localhost:8000/api/public/compatibility/health")
        print()
        print("2. 兼容性检查:")
        print(f"   POST http://localhost:8000/api/public/compatibility/check")
        print(f'   Body: {{"part_ids": [{cpu.id}, {motherboard.id}], "detail_level": "standard"}}')
        print()
        print("3. 兼容性搜索:")
        print(f"   POST http://localhost:8000/api/public/compatibility/search")
        print(f'   Body: {{"selected_parts": [{cpu.id}], "target_categories": ["主板", "散热器"], "limit": 5}}')
        print()
        print("4. 快速检查:")
        print(f"   GET http://localhost:8000/api/public/compatibility/quick-check/{cpu.id}/{motherboard.id}")
        
    except Exception as e:
        print(f"❌ 创建测试数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()