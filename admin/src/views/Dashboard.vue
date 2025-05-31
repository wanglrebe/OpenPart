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
        
        <!-- 🆕 新增兼容性规则统计卡片 -->
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon compatibility">
                <el-icon><Connection /></el-icon>
              </div>
              <div class="stat-info">
                <h3>{{ compatibilityStats.totalRules }}</h3>
                <p>兼容性规则</p>
                <small>{{ compatibilityStats.activeRules }} 启用</small>
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
              <!-- 🆕 新增兼容性配置快速入口 -->
              <el-button type="primary" @click="$router.push('/compatibility')" class="compatibility-btn">
                <el-icon><Connection /></el-icon>
                兼容性配置
                <el-tag type="success" size="small" style="margin-left: 8px;">NEW</el-tag>
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
              <div class="card-header">
                <span>系统信息</span>
                <!-- 🆕 兼容性系统状态指示器 -->
                <el-tag 
                  :type="compatibilitySystemStatus.type"
                  size="small"
                >
                  {{ compatibilitySystemStatus.text }}
                </el-tag>
              </div>
            </template>
            <div class="system-info">
              <p><strong>版本：</strong>OpenPart v1.0.0</p>
              <p><strong>后端API：</strong>FastAPI + PostgreSQL</p>
              <p><strong>前端：</strong>Vue 3 + Element Plus + Monaco Editor</p>
              <p><strong>🆕 兼容性引擎：</strong>{{ compatibilityStats.engineVersion }}</p>
              <p><strong>🆕 活跃规则：</strong>{{ compatibilityStats.activeRules }}/{{ compatibilityStats.totalRules }}</p>
              <p><strong>🆕 经验数据：</strong>{{ compatibilityStats.totalExperiences }} 条记录</p>
              <p><strong>最后登录：</strong>{{ formatTime(currentUser?.last_login) }}</p>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 🆕 新增兼容性系统概览卡片 -->
      <el-row :gutter="20" class="content-row">
        <el-col :span="24">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>🎯 兼容性系统概览</span>
                <el-button 
                  type="primary" 
                  size="small"
                  @click="$router.push('/compatibility')"
                >
                  进入配置编辑器
                </el-button>
              </div>
            </template>
            
            <el-row :gutter="16">
              <el-col :span="8">
                <div class="overview-item">
                  <h4>📋 规则管理</h4>
                  <p>{{ compatibilityStats.totalRules }} 个规则，{{ compatibilityStats.activeRules }} 个启用</p>
                  <p class="overview-desc">基于安全表达式的兼容性检查规则</p>
                </div>
              </el-col>
              
              <el-col :span="8">
                <div class="overview-item">
                  <h4>📚 经验数据</h4>
                  <p>{{ compatibilityStats.totalExperiences }} 条经验，{{ compatibilityStats.verifiedExperiences }} 已验证</p>
                  <p class="overview-desc">真实用户兼容性使用经验</p>
                </div>
              </el-col>
              
              <el-col :span="8">
                <div class="overview-item">
                  <h4>🛡️ 安全机制</h4>
                  <p>{{ compatibilityStats.securityFeatures || '多层验证' }}</p>
                  <p class="overview-desc">表达式沙箱执行，完整审计日志</p>
                </div>
              </el-col>
            </el-row>
            
            <!-- 🆕 最近的兼容性活动 -->
            <el-divider>最近活动</el-divider>
            <div class="recent-activity">
              <el-timeline>
                <el-timeline-item
                  v-for="activity in recentCompatibilityActivity"
                  :key="activity.id"
                  :timestamp="activity.timestamp"
                  placement="top"
                >
                  <el-tag :type="activity.type" size="small">{{ activity.action }}</el-tag>
                  {{ activity.description }}
                </el-timeline-item>
              </el-timeline>
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
  Download, Upload, Tools, Connection  // 🆕 添加连接图标
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import NavBar from '../components/NavBar.vue'
import { partsAPI, authAPI, compatibilityAPI } from '../utils/api'  // 🆕 导入兼容性API
import { auth } from '../utils/auth'

export default {
  name: 'Dashboard',
  components: {
    NavBar,
    Box, Collection, User, CircleCheck, Plus, Search, UserFilled,
    Download, Upload, Tools, Connection  // 🆕 添加连接图标
  },
  setup() {
    const currentUser = ref(auth.getUser())
    
    // 原有统计数据
    const statistics = reactive({
      totalParts: 0,
      totalCategories: 0,
      totalUsers: 0
    })
    
    // 🆕 新增兼容性系统统计
    const compatibilityStats = reactive({
      totalRules: 0,
      activeRules: 0,
      totalExperiences: 0,
      verifiedExperiences: 0,
      engineVersion: 'v1.0.0',
      securityFeatures: '多层验证'
    })
    
    // 🆕 兼容性系统状态
    const compatibilitySystemStatus = reactive({
      type: 'success',
      text: '正常运行'
    })
    
    // 🆕 最近的兼容性活动
    const recentCompatibilityActivity = ref([])
    
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
    
    // 🆕 加载兼容性系统统计
    const loadCompatibilityStats = async () => {
      try {
        // 获取兼容性系统统计
        const statsResponse = await compatibilityAPI.system.stats()
        const stats = statsResponse.data
        
        compatibilityStats.totalRules = stats.total_rules || 0
        compatibilityStats.activeRules = stats.active_rules || 0
        compatibilityStats.totalExperiences = stats.total_experiences || 0
        compatibilityStats.verifiedExperiences = stats.verified_experiences || 0
        
        // 更新系统状态
        if (compatibilityStats.activeRules === 0) {
          compatibilitySystemStatus.type = 'warning'
          compatibilitySystemStatus.text = '未配置规则'
        } else if (compatibilityStats.activeRules < 5) {
          compatibilitySystemStatus.type = 'info'
          compatibilitySystemStatus.text = '规则较少'
        } else {
          compatibilitySystemStatus.type = 'success'
          compatibilitySystemStatus.text = '正常运行'
        }
        
        // 获取最近的审计日志作为活动
        const auditResponse = await compatibilityAPI.system.auditLog({ 
          page: 1, 
          size: 5 
        })
        
        recentCompatibilityActivity.value = auditResponse.data.map(log => ({
          id: log.id,
          action: getActionLabel(log.action),
          description: getActivityDescription(log),
          timestamp: new Date(log.changed_at).toLocaleString(),
          type: getActivityType(log.action)
        }))
        
      } catch (error) {
        console.error('加载兼容性统计失败:', error)
        // 设置默认状态
        compatibilitySystemStatus.type = 'danger'
        compatibilitySystemStatus.text = '加载失败'
      }
    }
    
    // 🆕 辅助函数：获取操作标签
    const getActionLabel = (action) => {
      const labels = {
        create: '创建',
        update: '更新',
        delete: '删除',
        disable: '停用',
        enable: '启用',
        test: '测试',
        validate: '验证'
      }
      return labels[action] || action
    }
    
    // 🆕 辅助函数：获取活动描述
    const getActivityDescription = (log) => {
      if (log.rule_name) {
        return `规则 "${log.rule_name}"`
      } else if (log.rule_id) {
        return `规则 ID: ${log.rule_id}`
      } else {
        return '兼容性配置'
      }
    }
    
    // 🆕 辅助函数：获取活动类型
    const getActivityType = (action) => {
      const types = {
        create: 'success',
        update: 'info',
        delete: 'danger',
        disable: 'warning',
        enable: 'success',
        test: 'info',
        validate: 'info'
      }
      return types[action] || 'info'
    }
    
    const showUserManagement = () => {
      ElMessage.info('用户管理功能开发中...')
    }
    
    const formatTime = (timeString) => {
      if (!timeString) return '未知'
      return new Date(timeString).toLocaleString('zh-CN')
    }
    
    onMounted(async () => {
      await Promise.all([
        loadStatistics(),
        loadCompatibilityStats()  // 🆕 加载兼容性统计
      ])
    })
    
    return {
      currentUser,
      statistics,
      compatibilityStats,              // 🆕 兼容性统计
      compatibilitySystemStatus,       // 🆕 系统状态
      recentCompatibilityActivity,     // 🆕 最近活动
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

/* 🆕 兼容性图标样式 */
.stat-icon.compatibility {
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

.stat-info small {
  color: #67C23A;
  font-size: 12px;
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

/* 🆕 兼容性按钮特殊样式 */
.compatibility-btn {
  position: relative;
  background: linear-gradient(135deg, #409EFF, #67C23A);
  border: none;
}

.compatibility-btn:hover {
  background: linear-gradient(135deg, #66b1ff, #85ce61);
}

.system-info p {
  margin: 10px 0;
  color: #606266;
}

/* 🆕 卡片头部样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 🆕 概览项目样式 */
.overview-item {
  text-align: center;
  padding: 16px;
  border-radius: 8px;
  background: #f8f9fa;
  margin-bottom: 16px;
}

.overview-item h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 16px;
}

.overview-item p {
  margin: 4px 0;
  color: #606266;
  font-size: 14px;
}

.overview-desc {
  color: #909399 !important;
  font-size: 12px !important;
}

/* 🆕 最近活动样式 */
.recent-activity {
  max-height: 300px;
  overflow-y: auto;
  padding: 16px 0;
}

/* 🆕 时间线项目样式 */
:deep(.el-timeline-item__content) {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-row .el-col {
    margin-bottom: 20px;
  }
  
  .overview-item {
    margin-bottom: 12px;
    padding: 12px;
  }
  
  .recent-activity {
    max-height: 200px;
  }
}

/* 🆕 新功能动画效果 */
@keyframes newFeatureGlow {
  0% { box-shadow: 0 0 5px rgba(103, 194, 58, 0.3); }
  50% { box-shadow: 0 0 20px rgba(103, 194, 58, 0.6); }
  100% { box-shadow: 0 0 5px rgba(103, 194, 58, 0.3); }
}

.compatibility-btn {
  animation: newFeatureGlow 2s ease-in-out infinite;
}
</style>