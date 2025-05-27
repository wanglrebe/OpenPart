<template>
  <el-header class="navbar">
    <div class="navbar-left">
      <h2>OpenPart 管理后台</h2>
    </div>
    
    <div class="navbar-center">
      <el-menu 
        mode="horizontal" 
        :default-active="$route.name"
        router
      >
        <el-menu-item index="Dashboard">仪表板</el-menu-item>
        <el-menu-item index="/parts">零件管理</el-menu-item>
        <el-menu-item index="/import-export">数据管理</el-menu-item>  <!-- 新增菜单项 -->
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { User, ArrowDown } from '@element-plus/icons-vue'
import { auth } from '../utils/auth'
import { authAPI } from '../utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'NavBar',
  components: {
    User,
    ArrowDown
  },
  setup() {
    const router = useRouter()
    const currentUser = ref(null)

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
</style>