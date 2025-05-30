<template>
  <div class="compatibility-monitor">
    <!-- 统计卡片区域 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card rules-card">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon><Setting /></el-icon>
              </div>
              <div class="stat-info">
                <h3>{{ systemStats.active_rules }}/{{ systemStats.total_rules }}</h3>
                <p>活跃规则</p>
                <div class="stat-progress">
                  <el-progress 
                    :percentage="ruleActivePercentage" 
                    :show-text="false" 
                    :stroke-width="4"
                    color="#409eff"
                  />
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card experiences-card">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-info">
                <h3>{{ systemStats.verified_experiences }}/{{ systemStats.total_experiences }}</h3>
                <p>已验证经验</p>
                <div class="stat-progress">
                  <el-progress 
                    :percentage="experienceVerifiedPercentage" 
                    :show-text="false" 
                    :stroke-width="4"
                    color="#67c23a"
                  />
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card checks-card">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon><DataAnalysis /></el-icon>
              </div>
              <div class="stat-info">
                <h3>{{ systemStats.total_checks_today }}</h3>
                <p>今日检查次数</p>
                <div class="stat-sub">
                  缓存命中率: {{ (systemStats.cache_hit_rate * 100).toFixed(1) }}%
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card security-card">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon><Lock /></el-icon>
              </div>
              <div class="stat-info">
                <h3>{{ securityStats.high_risk_operations }}</h3>
                <p>高风险操作</p>
                <div class="stat-sub">
                  平均响应: {{ systemStats.avg_check_time }}s
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 功能按钮区域 -->
    <div class="actions-section">
      <el-card>
        <template #header>
          <span>系统管理</span>
        </template>
        
        <div class="action-buttons">
          <el-button type="primary" @click="refreshStats" :loading="statsLoading">
            <el-icon><Refresh /></el-icon>
            刷新统计
          </el-button>
          
          <el-button type="warning" @click="clearCache" :loading="cacheClearing">
            <el-icon><Delete /></el-icon>
            清理缓存
          </el-button>
          
          <el-button @click="showSecurityReport = true">
            <el-icon><Lock /></el-icon>
            安全报告
          </el-button>
          
          <el-button @click="showSystemStatus = true">
            <el-icon><Monitor /></el-icon>
            系统状态
          </el-button>
          
          <el-button @click="showAuditLogDialog = true">
            <el-icon><Document /></el-icon>
            审计日志
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 热门类别统计 -->
    <div class="categories-section">
      <el-card>
        <template #header>
          <span>热门类别统计</span>
        </template>
        
        <div class="categories-chart">
          <div v-if="topCategories.length > 0" class="category-bars">
            <div 
              v-for="category in topCategories.slice(0, 8)" 
              :key="category.category"
              class="category-bar"
            >
              <div class="category-info">
                <span class="category-name">{{ category.category }}</span>
                <span class="category-count">{{ category.rule_count }}</span>
              </div>
              <div class="category-progress">
                <el-progress 
                  :percentage="(category.rule_count / maxCategoryCount) * 100" 
                  :show-text="false"
                  :stroke-width="8"
                  color="#409eff"
                />
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无类别数据" />
        </div>
      </el-card>
    </div>

    <!-- 安全报告对话框 -->
    <el-dialog
      title="安全状态报告"
      v-model="showSecurityReport"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-loading="securityReportLoading" class="security-report">
        <div v-if="securityReport" class="report-content">
          <!-- 概览统计 -->
          <div class="report-overview">
            <el-row :gutter="20">
              <el-col :span="8">
                <div class="overview-item">
                  <h4>{{ securityReport.total_rules }}</h4>
                  <p>总规则数</p>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="overview-item">
                  <h4>{{ securityReport.active_rules }}</h4>
                  <p>活跃规则</p>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="overview-item high-risk">
                  <h4>{{ securityReport.high_risk_operations }}</h4>
                  <p>高风险操作</p>
                </div>
              </el-col>
            </el-row>
          </div>

          <!-- 风险操作统计 -->
          <el-divider>风险操作统计（最近7天）</el-divider>
          <div class="risk-stats">
            <div class="risk-item high">
              <span class="risk-label">高风险</span>
              <span class="risk-value">{{ securityReport.high_risk_operations }}</span>
            </div>
            <div class="risk-item medium">
              <span class="risk-label">中风险</span>
              <span class="risk-value">{{ securityReport.medium_risk_operations }}</span>
            </div>
            <div class="risk-item low">
              <span class="risk-label">低风险</span>
              <span class="risk-value">{{ securityReport.low_risk_operations }}</span>
            </div>
          </div>

          <!-- 安全建议 -->
          <el-divider>安全建议</el-divider>
          <div class="security-recommendations">
            <el-alert
              v-for="(recommendation, index) in securityReport.security_recommendations"
              :key="index"
              :title="recommendation"
              type="info"
              :closable="false"
              show-icon
              style="margin-bottom: 10px"
            />
          </div>

          <!-- 最近违规操作 -->
          <el-divider>最近违规操作</el-divider>
          <div class="recent-violations">
            <el-table 
              :data="securityReport.recent_violations" 
              size="small"
              max-height="200"
            >
              <el-table-column prop="action" label="操作" width="80" />
              <el-table-column prop="risk_level" label="风险" width="80">
                <template #default="scope">
                  <el-tag :type="getRiskLevelType(scope.row.risk_level)" size="small">
                    {{ getRiskLevelText(scope.row.risk_level) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="changed_at" label="时间" width="150">
                <template #default="scope">
                  {{ formatTime(scope.row.changed_at) }}
                </template>
              </el-table-column>
              <el-table-column prop="ip_address" label="IP地址" show-overflow-tooltip />
            </el-table>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showSecurityReport = false">关闭</el-button>
        <el-button type="primary" @click="loadSecurityReport">刷新报告</el-button>
      </template>
    </el-dialog>

    <!-- 系统状态对话框 -->
    <el-dialog
      title="系统状态"
      v-model="showSystemStatus"
      width="600px"
    >
      <div v-loading="systemStatusLoading" class="system-status">
        <div v-if="systemStatus" class="status-content">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="系统状态">
              <el-tag :type="getSystemStatusType(systemStatus.system_status)">
                {{ systemStatus.status_text }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="健康评分">
              <div class="health-score">
                <el-progress 
                  :percentage="systemStatus.health_score" 
                  :color="getHealthScoreColor(systemStatus.health_score)"
                />
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="兼容性检查">
              <el-tag :type="systemStatus.capabilities.compatibility_check ? 'success' : 'danger'">
                {{ systemStatus.capabilities.compatibility_check ? '可用' : '不可用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="经验查询">
              <el-tag :type="systemStatus.capabilities.experience_lookup ? 'success' : 'danger'">
                {{ systemStatus.capabilities.experience_lookup ? '可用' : '不可用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="缓存系统">
              <el-tag :type="systemStatus.capabilities.caching ? 'success' : 'danger'">
                {{ systemStatus.capabilities.caching ? '运行中' : '停止' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="最后更新">
              {{ formatTime(systemStatus.last_updated) }}
            </el-descriptions-item>
          </el-descriptions>

          <el-divider>系统消息</el-divider>
          <div class="system-messages">
            <el-alert
              v-for="(message, index) in systemStatus.messages"
              :key="index"
              :title="message"
              :type="index === 0 ? 'success' : 'info'"
              :closable="false"
              show-icon
              style="margin-bottom: 8px"
            />
          </div>

          <el-divider>统计信息</el-divider>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="总规则数">
              {{ systemStatus.statistics.total_rules }}
            </el-descriptions-item>
            <el-descriptions-item label="活跃规则">
              {{ systemStatus.statistics.active_rules }}
            </el-descriptions-item>
            <el-descriptions-item label="已验证经验">
              {{ systemStatus.statistics.verified_experiences }}
            </el-descriptions-item>
            <el-descriptions-item label="缓存条目">
              {{ systemStatus.statistics.cache_entries }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showSystemStatus = false">关闭</el-button>
        <el-button type="primary" @click="loadSystemStatus">刷新状态</el-button>
      </template>
    </el-dialog>

    <!-- 审计日志对话框 -->
    <el-dialog
      title="审计日志"
      v-model="showAuditLogDialog"
      width="1000px"
      :close-on-click-modal="false"
    >
      <div class="audit-log-container">
        <!-- 筛选器 -->
        <div class="audit-filters">
          <el-form :model="auditFilters" inline>
            <el-form-item label="操作类型">
              <el-select v-model="auditFilters.action" placeholder="全部" clearable>
                <el-option label="创建" value="create" />
                <el-option label="更新" value="update" />
                <el-option label="删除" value="delete" />
                <el-option label="测试" value="test" />
                <el-option label="验证" value="validate" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="风险等级">
              <el-select v-model="auditFilters.risk_level" placeholder="全部" clearable>
                <el-option label="高风险" value="high" />
                <el-option label="中风险" value="medium" />
                <el-option label="低风险" value="low" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="时间范围">
              <el-select v-model="auditFilters.days" placeholder="7天">
                <el-option label="1天" :value="1" />
                <el-option label="7天" :value="7" />
                <el-option label="30天" :value="30" />
                <el-option label="90天" :value="90" />
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="loadAuditLogs">查询</el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 审计日志表格 -->
        <div class="audit-log-table">
          <el-table 
            :data="auditLogs" 
            v-loading="auditLogLoading"
            size="small"
            max-height="400"
          >
            <el-table-column prop="action" label="操作" width="80">
              <template #default="scope">
                <el-tag :type="getActionType(scope.row.action)" size="small">
                  {{ getActionText(scope.row.action) }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="risk_level" label="风险" width="80">
              <template #default="scope">
                <el-tag :type="getRiskLevelType(scope.row.risk_level)" size="small">
                  {{ getRiskLevelText(scope.row.risk_level) }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="rule_name" label="规则名称" width="150" show-overflow-tooltip />
            
            <el-table-column prop="operator_username" label="操作者" width="100" />
            
            <el-table-column prop="changed_at" label="操作时间" width="150">
              <template #default="scope">
                {{ formatTime(scope.row.changed_at) }}
              </template>
            </el-table-column>
            
            <el-table-column prop="ip_address" label="IP地址" width="120" />
            
            <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-button 
                  size="small" 
                  type="primary"
                  @click="viewAuditDetails(scope.row)"
                >
                  详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showAuditLogDialog = false">关闭</el-button>
        <el-button type="primary" @click="exportAuditLogs">导出日志</el-button>
      </template>
    </el-dialog>

    <!-- 审计详情对话框 -->
    <el-dialog
      title="审计日志详情"
      v-model="showAuditDetailsDialog"
      width="600px"
    >
      <div v-if="currentAuditLog" class="audit-details">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="操作类型">
            <el-tag :type="getActionType(currentAuditLog.action)">
              {{ getActionText(currentAuditLog.action) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="风险等级">
            <el-tag :type="getRiskLevelType(currentAuditLog.risk_level)">
              {{ getRiskLevelText(currentAuditLog.risk_level) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="规则名称">
            {{ currentAuditLog.rule_name || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="操作者">
            {{ currentAuditLog.operator_username || `ID: ${currentAuditLog.changed_by}` }}
          </el-descriptions-item>
          <el-descriptions-item label="操作时间">
            {{ formatTime(currentAuditLog.changed_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="IP地址">
            {{ currentAuditLog.ip_address || '未知' }}
          </el-descriptions-item>
          <el-descriptions-item label="用户代理" v-if="currentAuditLog.user_agent">
            <div class="user-agent">{{ currentAuditLog.user_agent }}</div>
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="currentAuditLog.old_expression || currentAuditLog.new_expression" class="expression-changes">
          <el-divider>表达式变更</el-divider>
          
          <div v-if="currentAuditLog.old_expression" class="expression-section">
            <h5>原表达式:</h5>
            <pre class="expression-code">{{ currentAuditLog.old_expression }}</pre>
          </div>
          
          <div v-if="currentAuditLog.new_expression" class="expression-section">
            <h5>新表达式:</h5>
            <pre class="expression-code">{{ currentAuditLog.new_expression }}</pre>
          </div>
        </div>

        <div v-if="currentAuditLog.validation_result" class="validation-result">
          <el-divider>验证结果</el-divider>
          <pre class="validation-json">{{ JSON.stringify(currentAuditLog.validation_result, null, 2) }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  Setting, Document, DataAnalysis, Lock, Refresh, Delete, 
  Monitor
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { compatibilitySystem } from '../utils/api'

export default {
  name: 'CompatibilityMonitor',
  components: {
    Setting, Document, DataAnalysis, Lock, Refresh, Delete, 
    Monitor
  },
  emits: ['stats-updated'],
  setup(props, { emit }) {
    const statsLoading = ref(false)
    const cacheClearing = ref(false)
    const securityReportLoading = ref(false)
    const systemStatusLoading = ref(false)
    const auditLogLoading = ref(false)
    
    // 统计数据
    const systemStats = reactive({
      total_rules: 0,
      active_rules: 0,
      total_experiences: 0,
      verified_experiences: 0,
      total_checks_today: 0,
      cache_hit_rate: 0,
      avg_check_time: 0
    })
    
    const securityStats = reactive({
      high_risk_operations: 0,
      medium_risk_operations: 0,
      low_risk_operations: 0
    })
    
    const topCategories = ref([])
    
    // 对话框状态
    const showSecurityReport = ref(false)
    const showSystemStatus = ref(false)
    const showAuditLogDialog = ref(false)
    const showAuditDetailsDialog = ref(false)
    
    // 报告数据
    const securityReport = ref(null)
    const systemStatus = ref(null)
    const auditLogs = ref([])
    const currentAuditLog = ref(null)
    
    // 审计日志筛选
    const auditFilters = reactive({
      action: '',
      risk_level: '',
      days: 7
    })

    // 计算属性
    const ruleActivePercentage = computed(() => {
      return systemStats.total_rules > 0 
        ? (systemStats.active_rules / systemStats.total_rules) * 100 
        : 0
    })
    
    const experienceVerifiedPercentage = computed(() => {
      return systemStats.total_experiences > 0 
        ? (systemStats.verified_experiences / systemStats.total_experiences) * 100 
        : 0
    })
    
    const maxCategoryCount = computed(() => {
      return topCategories.value.length > 0 
        ? Math.max(...topCategories.value.map(c => c.rule_count))
        : 1
    })

    // 加载系统统计
    const loadSystemStats = async () => {
      try {
        const response = await compatibilitySystem.stats()
        Object.assign(systemStats, response.data)
        
        // 提取热门类别
        topCategories.value = response.data.top_categories || []
        
        // 更新父组件统计
        emit('stats-updated', {
          high_risk_operations: securityStats.high_risk_operations
        })
        
      } catch (error) {
        console.error('加载系统统计失败:', error)
      }
    }

    // 加载安全统计
    const loadSecurityStats = async () => {
      try {
        const response = await compatibilitySystem.securityReport({ days: 7 })
        Object.assign(securityStats, {
          high_risk_operations: response.data.high_risk_operations || 0,
          medium_risk_operations: response.data.medium_risk_operations || 0,
          low_risk_operations: response.data.low_risk_operations || 0
        })
      } catch (error) {
        console.error('加载安全统计失败:', error)
      }
    }

    // 刷新统计
    const refreshStats = async () => {
      statsLoading.value = true
      
      try {
        await Promise.all([
          loadSystemStats(),
          loadSecurityStats()
        ])
        ElMessage.success('统计数据已刷新')
      } catch (error) {
        ElMessage.error('刷新统计数据失败')
      }
      
      statsLoading.value = false
    }

    // 清理缓存
    const clearCache = async () => {
      try {
        await ElMessageBox.confirm(
          '确定要清理所有兼容性检查缓存吗？这将影响系统性能。',
          '确认清理缓存',
          {
            confirmButtonText: '确定清理',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        cacheClearing.value = true
        await compatibilitySystem.clearCache()
        
        ElMessage.success('缓存清理成功')
        refreshStats()
        
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('清理缓存失败')
        }
      }
      
      cacheClearing.value = false
    }

    // 加载安全报告
    const loadSecurityReport = async () => {
      securityReportLoading.value = true
      
      try {
        const response = await compatibilitySystem.securityReport({ days: 7 })
        securityReport.value = response.data
      } catch (error) {
        console.error('加载安全报告失败:', error)
        ElMessage.error('加载安全报告失败')
      }
      
      securityReportLoading.value = false
    }

    // 加载系统状态
    const loadSystemStatus = async () => {
      systemStatusLoading.value = true
      
      try {
        const response = await compatibilitySystem.systemStatus()
        systemStatus.value = response.data
      } catch (error) {
        console.error('加载系统状态失败:', error)
        ElMessage.error('加载系统状态失败')
      }
      
      systemStatusLoading.value = false
    }

    // 加载审计日志
    const loadAuditLogs = async () => {
      auditLogLoading.value = true
      
      try {
        const response = await compatibilitySystem.auditLog({
          action: auditFilters.action || undefined,
          risk_level: auditFilters.risk_level || undefined,
          days: auditFilters.days,
          page: 1,
          size: 100
        })
        auditLogs.value = response.data
      } catch (error) {
        console.error('加载审计日志失败:', error)
        ElMessage.error('加载审计日志失败')
      }
      
      auditLogLoading.value = false
    }

    // 查看审计详情
    const viewAuditDetails = (auditLog) => {
      currentAuditLog.value = auditLog
      showAuditDetailsDialog.value = true
    }

    // 导出审计日志
    const exportAuditLogs = () => {
      if (auditLogs.value.length === 0) {
        ElMessage.warning('没有可导出的日志')
        return
      }
      
      const exportData = auditLogs.value.map(log => ({
        id: log.id,
        action: log.action,
        risk_level: log.risk_level,
        rule_name: log.rule_name,
        operator: log.operator_username,
        changed_at: log.changed_at,
        ip_address: log.ip_address,
        old_expression: log.old_expression,
        new_expression: log.new_expression
      }))
      
      const jsonData = JSON.stringify(exportData, null, 2)
      const blob = new Blob([jsonData], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      
      const link = document.createElement('a')
      link.href = url
      link.download = `audit_logs_${new Date().toISOString().slice(0, 10)}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      URL.revokeObjectURL(url)
      ElMessage.success('审计日志导出成功')
    }

    // 工具函数
    const getRiskLevelType = (level) => {
      const typeMap = {
        'high': 'danger',
        'medium': 'warning',
        'low': 'success'
      }
      return typeMap[level] || 'info'
    }

    const getRiskLevelText = (level) => {
      const textMap = {
        'high': '高',
        'medium': '中',
        'low': '低'
      }
      return textMap[level] || level
    }

    const getActionType = (action) => {
      const typeMap = {
        'create': 'success',
        'update': 'warning',
        'delete': 'danger',
        'test': 'info',
        'validate': 'primary'
      }
      return typeMap[action] || 'info'
    }

    const getActionText = (action) => {
      const textMap = {
        'create': '创建',
        'update': '更新',
        'delete': '删除',
        'test': '测试',
        'validate': '验证'
      }
      return textMap[action] || action
    }

    const getSystemStatusType = (status) => {
      const typeMap = {
        'excellent': 'success',
        'good': 'success',
        'limited': 'warning',
        'poor': 'danger',
        'unknown': 'info'
      }
      return typeMap[status] || 'info'
    }

    const getHealthScoreColor = (score) => {
      if (score >= 90) return '#67c23a'
      if (score >= 70) return '#e6a23c'
      if (score >= 50) return '#409eff'
      return '#f56c6c'
    }

    const formatTime = (timeString) => {
      if (!timeString) return ''
      return new Date(timeString).toLocaleString('zh-CN')
    }

    // 对外暴露的刷新方法
    const refresh = async () => {
      await refreshStats()
    }

    // 组件挂载
    onMounted(() => {
      refreshStats()
    })

    return {
      // 响应式数据
      statsLoading,
      cacheClearing,
      securityReportLoading,
      systemStatusLoading,
      auditLogLoading,
      
      // 统计数据
      systemStats,
      securityStats,
      topCategories,
      ruleActivePercentage,
      experienceVerifiedPercentage,
      maxCategoryCount,
      
      // 对话框状态
      showSecurityReport,
      showSystemStatus,
      showAuditLogDialog,
      showAuditDetailsDialog,
      
      // 报告数据
      securityReport,
      systemStatus,
      auditLogs,
      currentAuditLog,
      auditFilters,
      
      // 方法
      refreshStats,
      clearCache,
      loadSecurityReport,
      loadSystemStatus,
      loadAuditLogs,
      viewAuditDetails,
      exportAuditLogs,
      refresh,
      
      // 工具函数
      getRiskLevelType,
      getRiskLevelText,
      getActionType,
      getActionText,
      getSystemStatusType,
      getHealthScoreColor,
      formatTime
    }
  }
}
</script>

<style scoped>
.compatibility-monitor {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f5f5;
  overflow-y: auto;
}

.stats-section {
  flex-shrink: 0;
}

.stat-card {
  height: 120px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  margin-right: 16px;
  flex-shrink: 0;
}

.rules-card .stat-icon {
  background: linear-gradient(135deg, #409eff, #67c23a);
}

.experiences-card .stat-icon {
  background: linear-gradient(135deg, #67c23a, #e6a23c);
}

.checks-card .stat-icon {
  background: linear-gradient(135deg, #e6a23c, #f56c6c);
}

.security-card .stat-icon {
  background: linear-gradient(135deg, #f56c6c, #409eff);
}

.stat-info {
  flex: 1;
}

.stat-info h3 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.stat-info p {
  margin: 0 0 8px 0;
  color: #909399;
  font-size: 14px;
}

.stat-progress {
  margin-top: 8px;
}

.stat-sub {
  font-size: 12px;
  color: #909399;
}

.actions-section {
  flex-shrink: 0;
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.categories-section {
  flex: 1;
  min-height: 300px;
}

.categories-chart {
  padding: 20px 0;
}

.category-bars {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.category-bar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.category-info {
  min-width: 120px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category-name {
  font-weight: 500;
  color: #303133;
}

.category-count {
  color: #409eff;
  font-weight: 600;
}

.category-progress {
  flex: 1;
}

.security-report {
  max-height: 600px;
  overflow-y: auto;
}

.report-overview {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 6px;
  margin-bottom: 20px;
}

.overview-item {
  text-align: center;
}

.overview-item h4 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #303133;
}

.overview-item.high-risk h4 {
  color: #f56c6c;
}

.overview-item p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.risk-stats {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin: 20px 0;
}

.risk-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  border-radius: 6px;
  min-width: 80px;
}

.risk-item.high {
  background: rgba(245, 108, 108, 0.1);
  border: 1px solid #f56c6c;
}

.risk-item.medium {
  background: rgba(230, 162, 60, 0.1);
  border: 1px solid #e6a23c;
}

.risk-item.low {
  background: rgba(103, 194, 58, 0.1);
  border: 1px solid #67c23a;
}

.risk-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.risk-value {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.security-recommendations {
  margin: 20px 0;
}

.recent-violations {
  margin: 20px 0;
}

.system-status {
  max-height: 500px;
  overflow-y: auto;
}

.health-score {
  width: 200px;
}

.system-messages {
  margin: 20px 0;
}

.audit-log-container {
  max-height: 600px;
  overflow-y: auto;
}

.audit-filters {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
  margin-bottom: 16px;
}

.audit-log-table {
  margin-bottom: 16px;
}

.audit-details {
  max-height: 500px;
  overflow-y: auto;
}

.user-agent {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  word-break: break-all;
}

.expression-changes {
  margin: 20px 0;
}

.expression-section {
  margin: 12px 0;
}

.expression-section h5 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.expression-code {
  background: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 12px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  color: #303133;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
}

.validation-result {
  margin: 20px 0;
}

.validation-json {
  background: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 12px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  color: #303133;
  margin: 0;
  white-space: pre;
  overflow-x: auto;
  max-height: 200px;
}

:deep(.el-progress-bar__outer) {
  background-color: #f0f2f5;
}

:deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
}

:deep(.el-table .cell) {
  padding: 8px 12px;
}
</style>