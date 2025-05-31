# auth_debug.py
"""
认证问题诊断脚本

使用方法:
python auth_debug.py

这个脚本会：
1. 检查API服务是否正常运行
2. 检查数据库中的用户数据
3. 尝试不同的认证方式
4. 提供创建管理员用户的方法
"""

import requests
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.core.config import settings
    print("✓ 成功导入配置")
except ImportError as e:
    print(f"✗ 导入配置失败: {e}")
    print("请确保在项目根目录下运行此脚本")
    sys.exit(1)

API_BASE_URL = "http://localhost:8000"

def check_api_health():
    """检查API服务健康状态"""
    print("🔍 检查API服务状态...")
    
    try:
        # 检查健康端点
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API服务正常运行")
            health_data = response.json()
            print(f"   状态: {health_data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ API健康检查失败: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务，请检查服务是否启动")
        return False
    except Exception as e:
        print(f"❌ API健康检查异常: {e}")
        return False

def check_auth_endpoint():
    """检查认证端点"""
    print("\n🔍 检查认证端点...")
    
    try:
        # 尝试访问认证端点（应该返回422，因为没有提供数据）
        response = requests.post(f"{API_BASE_URL}/api/auth/token")
        
        if response.status_code == 422:
            print("✅ 认证端点可访问（返回验证错误，这是正常的）")
            return True
        elif response.status_code == 404:
            print("❌ 认证端点不存在，请检查路由配置")
            return False
        else:
            print(f"⚠️ 认证端点响应异常: HTTP {response.status_code}")
            print(f"   响应内容: {response.text}")
            return True
    except Exception as e:
        print(f"❌ 检查认证端点异常: {e}")
        return False

def check_database_users():
    """检查数据库中的用户"""
    print("\n🔍 检查数据库用户...")
    
    try:
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            # 检查users表是否存在
            table_check = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'users'
                )
            """)).scalar()
            
            if not table_check:
                print("❌ users表不存在，需要创建基础表结构")
                return False
            
            print("✅ users表存在")
            
            # 查询所有用户
            users = conn.execute(text("""
                SELECT id, username, email, role, is_active, created_at 
                FROM users 
                ORDER BY id
            """)).fetchall()
            
            if not users:
                print("⚠️ 数据库中没有用户，需要创建管理员用户")
                return False
            
            print(f"✅ 找到 {len(users)} 个用户:")
            for user in users:
                status = "启用" if user[4] else "禁用"
                print(f"   - ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 角色: {user[3]}, 状态: {status}")
            
            return True
            
    except SQLAlchemyError as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 检查用户失败: {e}")
        return False

def test_authentication(username, password):
    """测试用户认证"""
    print(f"\n🔐 测试用户认证: {username}")
    
    try:
        auth_data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/auth/token",
            data=auth_data,  # 使用 form data
            timeout=10
        )
        
        print(f"   请求数据: {auth_data}")
        print(f"   响应状态码: {response.status_code}")
        print(f"   响应内容: {response.text}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ 认证成功!")
            print(f"   Token类型: {token_data.get('token_type')}")
            print(f"   Token前缀: {token_data.get('access_token', '')[:50]}...")
            return True
        elif response.status_code == 401:
            print("❌ 认证失败: 用户名或密码错误")
            return False
        elif response.status_code == 422:
            print("❌ 请求格式错误")
            error_detail = response.json()
            print(f"   错误详情: {error_detail}")
            return False
        else:
            print(f"❌ 未知错误: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 认证测试异常: {e}")
        return False

def create_admin_user():
    """创建管理员用户"""
    print("\n👤 创建管理员用户...")
    
    try:
        engine = create_engine(settings.database_url)
        
        # 导入密码哈希功能
        from app.auth.security import get_password_hash
        
        username = "openpart_admin"
        password = "openpart123"
        email = "admin@openpart.org"
        
        hashed_password = get_password_hash(password)
        
        with engine.connect() as conn:
            trans = conn.begin()
            
            try:
                # 检查用户是否已存在
                existing = conn.execute(text("""
                    SELECT id FROM users WHERE username = :username
                """), {"username": username}).fetchone()
                
                if existing:
                    print(f"⚠️ 用户 {username} 已存在")
                    trans.rollback()
                    return username, password
                
                # 创建用户
                result = conn.execute(text("""
                    INSERT INTO users (username, email, hashed_password, role, is_active)
                    VALUES (:username, :email, :hashed_password, 'admin', true)
                    RETURNING id
                """), {
                    "username": username,
                    "email": email,
                    "hashed_password": hashed_password
                })
                
                user_id = result.fetchone()[0]
                trans.commit()
                
                print(f"✅ 管理员用户创建成功:")
                print(f"   用户名: {username}")
                print(f"   密码: {password}")
                print(f"   邮箱: {email}")
                print(f"   用户ID: {user_id}")
                
                return username, password
                
            except Exception as e:
                trans.rollback()
                print(f"❌ 创建用户失败: {e}")
                return None, None
                
    except Exception as e:
        print(f"❌ 创建管理员用户异常: {e}")
        return None, None

def verify_password_hash():
    """验证密码哈希功能"""
    print("\n🔒 验证密码哈希功能...")
    
    try:
        from app.auth.security import get_password_hash, verify_password
        
        test_password = "test123"
        hashed = get_password_hash(test_password)
        
        print(f"   原密码: {test_password}")
        print(f"   哈希值: {hashed}")
        
        # 验证密码
        is_valid = verify_password(test_password, hashed)
        print(f"   验证结果: {is_valid}")
        
        if is_valid:
            print("✅ 密码哈希功能正常")
            return True
        else:
            print("❌ 密码哈希功能异常")
            return False
            
    except Exception as e:
        print(f"❌ 密码哈希验证异常: {e}")
        return False

def main():
    """主函数"""
    print("🔍 OpenPart 认证问题诊断工具")
    print("=" * 60)
    
    # 1. 检查API服务
    if not check_api_health():
        print("\n❌ API服务异常，请先修复服务问题")
        return
    
    # 2. 检查认证端点
    if not check_auth_endpoint():
        print("\n❌ 认证端点异常，请检查路由配置")
        return
    
    # 3. 验证密码哈希功能
    if not verify_password_hash():
        print("\n❌ 密码哈希功能异常")
        return
    
    # 4. 检查数据库用户
    has_users = check_database_users()
    
    # 5. 如果没有用户，创建管理员用户
    if not has_users:
        print("\n🔧 数据库中没有用户，创建管理员用户...")
        username, password = create_admin_user()
        
        if username and password:
            print(f"\n✅ 管理员用户已创建，请使用以下凭据:")
            print(f"   用户名: {username}")
            print(f"   密码: {password}")
        else:
            print("\n❌ 创建管理员用户失败")
            return
    else:
        # 使用现有用户测试
        username = "openpart_admin"  # 或者其他已知用户名
        password = "openpart123"     # 对应密码
    
    # 6. 测试常见的用户名密码组合
    test_credentials = [
        ("openpart_user", "openpart"),
        ("openpart_admin", "openpart123"),
        ("admin", "admin"),
        ("admin", "openpart"),
        ("openpart_user", "openpart123"),
    ]
    
    print("\n🔐 测试常见认证凭据...")
    
    success = False
    for username, password in test_credentials:
        if test_authentication(username, password):
            print(f"\n🎉 找到有效凭据:")
            print(f"   用户名: {username}")
            print(f"   密码: {password}")
            print(f"\n请在测试脚本中使用这些凭据:")
            print(f"   ADMIN_USERNAME = \"{username}\"")
            print(f"   ADMIN_PASSWORD = \"{password}\"")
            success = True
            break
    
    if not success:
        print("\n❌ 所有测试凭据都失败了")
        print("\n🔧 建议的解决方案:")
        print("1. 检查数据库中的用户数据是否正确")
        print("2. 重新创建管理员用户")
        print("3. 检查密码哈希是否正确")
        print("4. 确保认证逻辑没有问题")
        
        # 提供手动创建用户的SQL
        print("\n📝 手动创建管理员用户的SQL:")
        print("```sql")
        print("-- 删除现有用户（如果存在）")
        print("DELETE FROM users WHERE username = 'openpart_admin';")
        print("")
        print("-- 创建新管理员用户")
        print("INSERT INTO users (username, email, hashed_password, role, is_active)")
        print("VALUES (")
        print("  'openpart_admin',")
        print("  'admin@openpart.org',")
        print("  '$2b$12$example_hash_here',  -- 需要使用真实的密码哈希")
        print("  'admin',")
        print("  true")
        print(");")
        print("```")

if __name__ == "__main__":
    main()