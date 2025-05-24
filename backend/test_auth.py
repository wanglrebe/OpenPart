# backend/init_secure_db.py
from app.core.database import engine, Base, SessionLocal
from app.models.part import Part
from app.auth.models import User, UserRole
from app.auth.security import get_password_hash

def create_tables():
    """创建所有数据库表"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")

def create_default_admin():
    """创建默认管理员用户"""
    db = SessionLocal()
    try:
        # 检查是否已存在管理员
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("默认管理员用户已存在，跳过创建")
            return
        
        # 创建默认管理员
        admin_user = User(
            username="admin",
            email="admin@openpart.local",
            hashed_password=get_password_hash("admin123"),  # 请在生产环境中更改！
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("默认管理员用户创建成功！")
        print("用户名: admin")
        print("密码: admin123")
        print("⚠️  请在生产环境中立即更改默认密码！")
        
    except Exception as e:
        print(f"创建管理员用户时出错: {e}")
        db.rollback()
    finally:
        db.close()

def add_sample_parts():
    """添加示例零件数据"""
    db = SessionLocal()
    try:
        # 检查是否已有数据
        existing_parts = db.query(Part).count()
        if existing_parts > 0:
            print("数据库中已有零件数据，跳过示例数据创建")
            return
        
        sample_parts = [
            Part(
                name="Arduino Uno R3",
                category="微控制器",
                description="基于ATmega328P的微控制器开发板",
                properties={
                    "电压": "5V",
                    "数字IO": "14",
                    "模拟输入": "6",
                    "闪存": "32KB",
                    "SRAM": "2KB",
                    "EEPROM": "1KB"
                }
            ),
            Part(
                name="电阻 10kΩ",
                category="电阻",
                description="1/4W 碳膜电阻",
                properties={
                    "阻值": "10kΩ",
                    "功率": "0.25W",
                    "精度": "±5%",
                    "温度系数": "±200ppm/°C"
                }
            ),
            Part(
                name="LED 5mm 红色",
                category="LED",
                description="5mm直插红色LED灯",
                properties={
                    "颜色": "红色",
                    "尺寸": "5mm",
                    "正向电压": "2.0V",
                    "正向电流": "20mA",
                    "发光强度": "2000-3000mcd"
                }
            )
        ]
        
        for part in sample_parts:
            db.add(part)
        
        db.commit()
        print(f"已添加 {len(sample_parts)} 个示例零件")
        
    except Exception as e:
        print(f"添加示例数据时出错: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=== OpenPart 安全数据库初始化 ===")
    
    # 1. 创建表
    create_tables()
    
    # 2. 创建默认管理员
    create_default_admin()
    
    # 3. 添加示例数据
    add_sample_parts()
    
    print("\n=== 初始化完成 ===")
    print("后端服务启动命令:")
    print("uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("\n测试API:")
    print("1. 管理员登录: POST /api/auth/token")
    print("2. 公开搜索: GET /api/public/parts/")
    print("3. 管理员管理: GET /api/admin/parts/ (需要token)")

# backend/test_auth.py (测试脚本)
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_public_api():
    """测试公开API"""
    print("=== 测试公开API ===")
    
    # 测试搜索零件
    response = requests.get(f"{BASE_URL}/public/parts/")
    if response.status_code == 200:
        parts = response.json()
        print(f"✅ 公开搜索成功，找到 {len(parts)} 个零件")
    else:
        print(f"❌ 公开搜索失败: {response.status_code}")

def test_admin_login():
    """测试管理员登录"""
    print("\n=== 测试管理员登录 ===")
    
    # 登录
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        token_data = response.json()
        token = token_data["access_token"]
        print("✅ 登录成功，获得token")
        
        # 测试管理员API
        headers = {"Authorization": f"Bearer {token}"}
        
        # 获取用户信息
        user_response = requests.get(f"{BASE_URL}/auth/users/me", headers=headers)
        if user_response.status_code == 200:
            user_info = user_response.json()
            print(f"✅ 获取用户信息成功: {user_info['username']} ({user_info['role']})")
        
        # 测试管理员零件API
        parts_response = requests.get(f"{BASE_URL}/admin/parts/", headers=headers)
        if parts_response.status_code == 200:
            parts = parts_response.json()
            print(f"✅ 管理员API访问成功，找到 {len(parts)} 个零件")
        
        return token
    else:
        print(f"❌ 登录失败: {response.status_code} - {response.text}")
        return None

def test_unauthorized_access():
    """测试未授权访问"""
    print("\n=== 测试权限控制 ===")
    
    # 尝试无token访问管理员API
    response = requests.get(f"{BASE_URL}/admin/parts/")
    if response.status_code in [401, 403]:  # 接受401或403都是正确的
        print("✅ 未授权访问被正确拦截")
    else:
        print(f"❌ 权限控制失效: {response.status_code}")

if __name__ == "__main__":
    print("=== OpenPart 认证系统测试 ===")
    print("请确保后端服务正在运行 (uvicorn app.main:app --reload)")
    input("按 Enter 键开始测试...")
    
    test_public_api()
    test_admin_login()
    test_unauthorized_access()
    
    print("\n=== 测试完成 ===")