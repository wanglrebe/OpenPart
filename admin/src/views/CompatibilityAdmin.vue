<template>
  <div class="compatibility-admin">
    <NavBar />
    
    <el-main class="main-content">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-left">
          <h1>兼容性管理</h1>
          <p>管理兼容性规则、经验数据和系统监控</p>
        </div>
        <div class="header-right">
          <el-badge :value="systemStats.high_risk_operations" :hidden="systemStats.high_risk_operations === 0" type="danger">
            <el-button @click="refreshAll" :loading="globalLoading">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </el-badge>
        </div>
      </div>

      <!-- 标签页导航 -->
      <el-tabs v-model="activeTab" class="main-tabs" @tab-click="handleTabClick">
        <!-- 规则管理标签页 -->
        <el-tab-pane label="规则管理" name="rules">
          <template #label>
            <span class="tab-label">
              <el-icon><Setting /></el-icon>
              规则管理
              <el-badge 
                :value="ruleStats.active_rules" 
                :max="99" 
                :hidden="ruleStats.active_rules === 0"
                type="primary"
              />
            </span>
          </template>
          
          <CompatibilityRules 
            ref="rulesComponentRef"
            @stats-updated="updateRuleStats"
          />
        </el-tab-pane>

        <!-- 经验管理标签页 -->
        <el-tab-pane label="经验管理" name="experiences">
          <template #label>
            <span class="tab-label">
              <el-icon><Document /></el-icon>
              经验管理
              <el-badge 
                :value="experienceStats.verified_experiences" 
                :max="99" 
                :hidden="experienceStats.verified_experiences === 0"
                type="success"
              />
            </span>
          </template>
          
          <CompatibilityExperiences 
            ref="experiencesComponentRef"
            @stats-updated="updateExperienceStats"
          />
        </el-tab-pane>

        <!-- 系统监控标签页 -->
        <el-tab-pane label="系统监控" name="monitor">
          <template #label>
            <span class="tab-label">
              <el-icon><Monitor /></el-icon>
              系统监控
              <el-badge 
                :value="systemStats.high_risk_operations" 
                :max="99" 
                :hidden="systemStats.high_risk_operations === 0"
                type="warning"
              />
            </span>
          </template>
          
          <CompatibilityMonitor 
            ref="monitorComponentRef"
            @stats-updated="updateSystemStats"
          />
        </el-tab-pane>
      </el-tabs>
    </el-main>
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { Refresh, Setting, Document, Monitor } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import NavBar from '../components/NavBar.vue'
import CompatibilityRules from '../components/CompatibilityRules.vue'
import CompatibilityExperiences from '../components/CompatibilityExperiences.vue'
import CompatibilityMonitor from '../components/CompatibilityMonitor.vue'
import { compatibilitySystem } from '../utils/api'

export default {
  name: 'CompatibilityAdmin',
  components: {
    NavBar,
    CompatibilityRules,
    CompatibilityExperiences,
    CompatibilityMonitor,
    Refresh,
    Setting,
    Document,
    Monitor
  },
  setup() {
    const activeTab = ref('rules')
    const globalLoading = ref(false)
    
    // 组件引用
    const rulesComponentRef = ref()
    const experiencesComponentRef = ref()
    const monitorComponentRef = ref()
    
    // 统计数据
    const ruleStats = reactive({
      total_rules: 0,
      active_rules: 0
    })
    
    const experienceStats = reactive({
      total_experiences: 0,
      verified_experiences: 0,
      pending_experiences: 0
    })
    
    const systemStats = reactive({
      total_checks_today: 0,
      cache_hit_rate: 0,
      high_risk_operations: 0,
      avg_check_time: 0
    })

    // 加载系统统计信息
    const loadSystemStats = async () => {
      try {
        const response = await compatibilitySystem.stats()
        
        // 更新规则统计
        Object.assign(ruleStats, {
          total_rules: response.data.total_rules || 0,
          active_rules: response.data.active_rules || 0
        })
        
        // 更新经验统计
        Object.assign(experienceStats, {
          total_experiences: response.data.total_experiences || 0,
          verified_experiences: response.data.verified_experiences || 0,
          pending_experiences: response.data.pending_experiences || 0
        })
        
        // 更新系统统计
        Object.assign(systemStats, {
          total_checks_today: response.data.total_checks_today || 0,
          cache_hit_rate: response.data.cache_hit_rate || 0,
          avg_check_time: response.data.avg_check_time || 0
        })
        
      } catch (error) {
        console.error('加载系统统计失败:', error)
      }
    }

    // 加载安全报告获取高风险操作数
    const loadSecurityStats = async () => {
      try {
        const response = await compatibilitySystem.securityReport({ days: 7 })
        systemStats.high_risk_operations = response.data.high_risk_operations || 0
      } catch (error) {
        console.error('加载安全统计失败:', error)
      }
    }

    // 统计更新回调
    const updateRuleStats = (stats) => {
      Object.assign(ruleStats, stats)
    }

    const updateExperienceStats = (stats) => {
      Object.assign(experienceStats, stats)
    }

    const updateSystemStats = (stats) => {
      Object.assign(systemStats, stats)
    }

    // 标签页切换处理
    const handleTabClick = async (tab) => {
      await nextTick()
      
      // 根据切换的标签页刷新对应组件
      switch (tab.name) {
        case 'rules':
          if (rulesComponentRef.value?.refresh) {
            rulesComponentRef.value.refresh()
          }
          break
        case 'experiences':
          if (experiencesComponentRef.value?.refresh) {
            experiencesComponentRef.value.refresh()
          }
          break
        case 'monitor':
          if (monitorComponentRef.value?.refresh) {
            monitorComponentRef.value.refresh()
          }
          break
      }
    }

    // 全局刷新
    const refreshAll = async () => {
      globalLoading.value = true
      
      try {
        // 并行加载所有统计数据
        await Promise.all([
          loadSystemStats(),
          loadSecurityStats()
        ])
        
        // 刷新当前活跃的组件
        await handleTabClick({ name: activeTab.value })
        
        ElMessage.success('数据刷新成功')
        
      } catch (error) {
        console.error('刷新失败:', error)
        ElMessage.error('数据刷新失败')
      }
      
      globalLoading.value = false
    }

    // 页面加载时初始化
    onMounted(async () => {
      await refreshAll()
    })

    return {
      activeTab,
      globalLoading,
      
      // 组件引用
      rulesComponentRef,
      experiencesComponentRef,
      monitorComponentRef,
      
      // 统计数据
      ruleStats,
      experienceStats,
      systemStats,
      
      // 方法
      handleTabClick,
      refreshAll,
      updateRuleStats,
      updateExperienceStats,
      updateSystemStats
    }
  }
}
</script>

<style scoped>
.compatibility-admin {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  background: #f5f5f5;
  padding: 20px;
  overflow: hidden;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left h1 {
  margin: 0 0 5px 0;
  color: #303133;
  font-size: 24px;
}

.header-left p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 10px;
  align-items: center;
}

.main-tabs {
  height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 5px;
}

:deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
}

:deep(.el-tab-pane) {
  height: 100%;
  overflow: hidden;
}

:deep(.el-tabs__nav-wrap) {
  background: white;
  border-radius: 6px 6px 0 0;
  border: 1px solid #e4e7ed;
  border-bottom: none;
  padding: 0 10px;
}

:deep(.el-tabs__header) {
  margin: 0;
}

:deep(.el-tabs__item) {
  font-weight: 500;
  padding: 0 20px;
}

:deep(.el-tabs__item.is-active) {
  color: #409eff;
  background: rgba(64, 158, 255, 0.05);
  border-radius: 6px 6px 0 0;
}

:deep(.el-badge__content) {
  top: 8px;
  right: -5px;
}

.tab-label :deep(.el-badge) {
  margin-left: 5px;
}

/* 确保子组件占满高度 */
:deep(.el-tab-pane > div) {
  height: 100%;
}
</style>