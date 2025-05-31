<template>
  <el-header class="navbar">
    <div class="navbar-left">
      <h2>OpenPart 管理后台</h2>
    </div>
    
    <div class="navbar-center">
      <el-menu 
        mode="horizontal" 
        :default-active="currentRoute"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          仪表板
        </el-menu-item>
        <el-menu-item index="/parts">
          <el-icon><Box /></el-icon>
          零件管理
        </el-menu-item>
        <!-- 🆕 新增兼容性管理菜单项 -->
        <el-menu-item index="/compatibility">
          <el-icon><Connection /></el-icon>
          兼容性配置
        </el-menu-item>
        <el-menu-item index="/import-export">
          <el-icon><Download /></el-icon>
          数据管理
        </el-menu-item>
        <el-menu-item index="/crawler-plugins">
          <el-icon><Tools /></el-icon>
          插件管理
        </el-menu-item>
      </el-menu>
    </div>
    
    <div class="navbar-right">
      <el-dropdown @command="handleCommand">
        <span class="user-info">
          <el-icon><User /></el-icon>
          {{ currentUser?.username || '管理员' }}
          <el-icon><ArrowDown /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">个人资料</el-dropdown-item>
            <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </el-header>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  User, ArrowDown, Odometer, Box, Connection, Download, Tools 
} from '@element-plus/icons-vue'
import { auth } from '../utils/auth'
import { authAPI } from '../utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'NavBar',
  components: {
    User,
    ArrowDown,
    Odometer,
    Box,
    Connection,  // 🆕 新增兼容性图标
    Download,
    Tools
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    const currentUser = ref(null)

    // 计算当前路由，确保与菜单项的 index 匹配
    const currentRoute = computed(() => {
      const path = route.path
      
      // 根据路径返回对应的菜单项 index
      if (path === '/' || path === '/dashboard') {
        return '/dashboard'
      } else if (path === '/parts') {
        return '/parts'
      } else if (path === '/compatibility') {  // 🆕 新增路由匹配
        return '/compatibility'
      } else if (path === '/import-export') {
        return '/import-export'
      } else if (path === '/crawler-plugins') {
        return '/crawler-plugins'
      }
      
      // 默认返回当前路径
      return path
    })

    onMounted(async () => {
      // 获取用户信息
      currentUser.value = auth.getUser()
      
      // 如果没有用户信息，尝试从API获取
      if (!currentUser.value) {
        try {
          const response = await authAPI.getCurrentUser()
          currentUser.value = response.data
          auth.setUser(response.data)
        } catch (error) {
          console.error('获取用户信息失败:', error)
        }
      }
    })

    const handleCommand = async (command) => {
      switch (command) {
        case 'profile':
          ElMessage.info('个人资料功能开发中...')
          break
        case 'logout':
          try {
            await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
              confirmButtonText: '确定',
              cancelButtonText: '取消',
              type: 'warning'
            })
            
            auth.logout()
            ElMessage.success('已退出登录')
            router.push('/login')
          } catch (error) {
            // 用户取消
          }
          break
      }
    }

    return {
      currentUser,
      currentRoute,
      handleCommand
    }
  }
}
</script>

<style scoped>
.navbar {
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.navbar-left h2 {
  color: #409EFF;
  margin: 0;
}

.navbar-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.navbar-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #606266;
  gap: 5px;
}

.user-info:hover {
  color: #409EFF;
}

.el-menu--horizontal {
  border-bottom: none;
}

/* 🆕 兼容性菜单项的特殊样式 */
.el-menu-item[index="/compatibility"] {
  position: relative;
}

.el-menu-item[index="/compatibility"]:after {
  content: 'NEW';
  position: absolute;
  top: 8px;
  right: 8px;
  background: #67C23A;
  color: white;
  font-size: 10px;
  padding: 1px 4px;
  border-radius: 2px;
  font-weight: bold;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .navbar {
    padding: 0 10px;
  }
  
  .navbar-left h2 {
    font-size: 16px;
  }
  
  .navbar-center .el-menu {
    font-size: 14px;
  }
  
  .el-menu-item span {
    display: none;
  }
  
  .el-menu-item .el-icon {
    margin-right: 0;
  }
}
</style>