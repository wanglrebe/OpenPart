<template>
  <div class="dashboard">
    <NavBar />
    
    <el-main class="main-content">
      <div class="dashboard-header">
        <h1>仪表板</h1>
        <p>欢迎使用 OpenPart 管理后台</p>
      </div>
      
      <el-row :gutter="20" class="stats-row">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon parts">
                <el-icon><Box /></el-icon>
              </div>
              <div class="stat-info">
                <h3>{{ statistics.totalParts }}</h3>
                <p>总零件数</p>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon categories">
                <el-icon><Collection /></el-icon>
              </div>
              <div class="stat-info">
                <h3>{{ statistics.totalCategories }}</h3>
                <p>零件类别</p>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon users">
                <el-icon><User /></el-icon>
              </div>
              <div class="stat-info">
                <h3>{{ statistics.totalUsers }}</h3>
                <p>管理员用户</p>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon online">
                <el-icon><CircleCheck /></el-icon>
              </div>
              <div class="stat-info">
                <h3>在线</h3>
                <p>系统状态</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" class="content-row">
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>快速操作</span>
            </template>
            <div class="quick-actions">
              <el-button type="primary" @click="$router.push('/parts')">
                <el-icon><Plus /></el-icon>
                添加零件
              </el-button>
              <el-button type="success" @click="$router.push('/parts')">
                <el-icon><Search /></el-icon>
                管理零件
              </el-button>
              <el-button type="warning" @click="$router.push('/import-export')">
                <el-icon><Download /></el-icon>
                数据导出
              </el-button>
              <el-button type="info" @click="$router.push('/import-export')">
                <el-icon><Upload /></el-icon>
                数据导入
              </el-button>
              <el-button type="primary" @click="$router.push('/crawler-plugins')">
                <el-icon><Tools /></el-icon>
                插件管理
              </el-button>
              <el-button type="info" @click="showUserManagement">
                <el-icon><UserFilled /></el-icon>
                用户管理
              </el-button>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>系统信息</span>
            </template>
            <div class="system-info">
              <p><strong>版本：</strong>OpenPart v0.2.0</p>
              <p><strong>后端API：</strong>FastAPI + PostgreSQL</p>
              <p><strong>前端：</strong>Vue 3 + Element Plus</p>
              <p><strong>最后登录：</strong>{{ formatTime(currentUser?.last_login) }}</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-main>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { 
  Box, Collection, User, CircleCheck, Plus, Search, UserFilled,
  Download, Upload, Tools  // 添加这行
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import NavBar from '../components/NavBar.vue'
import { partsAPI, authAPI } from '../utils/api'
import { auth } from '../utils/auth'

export default {
  name: 'Dashboard',
  components: {
  NavBar,
  Box, Collection, User, CircleCheck, Plus, Search, UserFilled,
  Download, Upload, Tools  // 添加这行
  },
  setup() {
    const currentUser = ref(auth.getUser())
    const statistics = reactive({
      totalParts: 0,
      totalCategories: 0,
      totalUsers: 0
    })
    
    const loadStatistics = async () => {
      try {
        // 获取零件统计
        const partsResponse = await partsAPI.getParts({ limit: 1000 })
        const parts = partsResponse.data
        statistics.totalParts = parts.length
        
        // 计算类别数
        const categories = new Set(parts.map(p => p.category).filter(Boolean))
        statistics.totalCategories = categories.size
        
        // 获取用户统计
        const usersResponse = await authAPI.getUsers()
        statistics.totalUsers = usersResponse.data.length
        
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    }
    
    const showUserManagement = () => {
      ElMessage.info('用户管理功能开发中...')
    }
    
    const formatTime = (timeString) => {
      if (!timeString) return '未知'
      return new Date(timeString).toLocaleString('zh-CN')
    }
    
    onMounted(() => {
      loadStatistics()
    })
    
    return {
      currentUser,
      statistics,
      showUserManagement,
      formatTime
    }
  }
}
</script>

<style scoped>
.dashboard {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  background: #f5f5f5;
  padding: 20px;
}

.dashboard-header {
  margin-bottom: 30px;
}

.dashboard-header h1 {
  color: #303133;
  margin-bottom: 10px;
}

.dashboard-header p {
  color: #909399;
  margin: 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  height: 100px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
  color: white;
}

.stat-icon.parts {
  background: #409EFF;
}

.stat-icon.categories {
  background: #67C23A;
}

.stat-icon.users {
  background: #E6A23C;
}

.stat-icon.online {
  background: #F56C6C;
}

.stat-info h3 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.stat-info p {
  margin: 5px 0 0 0;
  color: #909399;
  font-size: 14px;
}

.content-row {
  margin-top: 20px;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.quick-actions .el-button {
  justify-content: flex-start;
}

.system-info p {
  margin: 10px 0;
  color: #606266;
}
</style>