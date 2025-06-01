<!-- src/views/CompatibilityCheck.vue -->
<template>
  <div class="compatibility-check-page">
    <!-- 全局导航 -->
    <GlobalNavigation />
    
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div class="header-info">
            <h1 class="page-title">兼容性检查</h1>
            <p class="page-description">
              检查多个零件之间的兼容性，获得专业的配置建议
            </p>
          </div>
          
          <!-- 快速操作 -->
          <div class="quick-actions">
            <button 
              v-if="selectedParts.length >= 2"
              @click="performCompatibilityCheck"
              :disabled="isChecking"
              class="check-btn primary"
            >
              <svg v-if="isChecking" class="btn-icon spinning" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <svg v-else class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ isChecking ? '检查中...' : '开始检查' }}
            </button>
            
            <button 
              v-if="selectedParts.length > 0"
              @click="clearAllParts"
              class="clear-btn secondary"
            >
              <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              清空零件
            </button>
            
            <router-link to="/compatibility/guide" class="guide-btn outline">
              <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              使用指南
            </router-link>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 主要内容区域 -->
    <main class="main-content">
      <div class="container">
        <!-- 进度指示器 -->
        <div class="progress-indicator">
          <div class="progress-steps">
            <div class="progress-step" :class="{ active: selectedParts.length > 0, completed: selectedParts.length >= 2 }">
              <div class="step-icon">
                <svg v-if="selectedParts.length >= 2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <span v-else>1</span>
              </div>
              <div class="step-info">
                <div class="step-title">选择零件</div>
                <div class="step-description">添加2-10个零件</div>
              </div>
            </div>
            
            <div class="progress-connector" :class="{ active: selectedParts.length >= 2 }"></div>
            
            <div class="progress-step" :class="{ active: selectedParts.length >= 2, completed: hasCheckResult }">
              <div class="step-icon">
                <svg v-if="hasCheckResult" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <span v-else>2</span>
              </div>
              <div class="step-info">
                <div class="step-title">兼容性检查</div>
                <div class="step-description">分析零件兼容性</div>
              </div>
            </div>
            
            <div class="progress-connector" :class="{ active: hasCheckResult }"></div>
            
            <div class="progress-step" :class="{ active: hasCheckResult && showConfigAnalysis }">
              <div class="step-icon">
                <span>3</span>
              </div>
              <div class="step-info">
                <div class="step-title">配置优化</div>
                <div class="step-description">获取优化建议</div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 标签页导航 -->
        <div class="tabs-navigation">
          <button 
            class="tab-button"
            :class="{ active: activeTab === 'selection' }"
            @click="activeTab = 'selection'"
          >
            <svg class="tab-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            零件选择
            <span v-if="selectedParts.length > 0" class="tab-badge">{{ selectedParts.length }}</span>
          </button>
          
          <button 
            class="tab-button"
            :class="{ active: activeTab === 'results' }"
            @click="activeTab = 'results'"
            :disabled="!hasCheckResult"
          >
            <svg class="tab-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            检查结果
          </button>
          
          <button 
            class="tab-button"
            :class="{ active: activeTab === 'analysis' }"
            @click="activeTab = 'analysis'"
            :disabled="selectedParts.length === 0"
          >
            <svg class="tab-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            配置分析
            <span v-if="showConfigAnalysis" class="tab-badge info">智能</span>
          </button>
        </div>
        
        <!-- 标签页内容 -->
        <div class="tabs-content">
          <!-- 零件选择标签页 -->
          <div v-if="activeTab === 'selection'" class="tab-panel">
            <div class="selection-panel">
              <CompatibilityPartSelector
                v-model="selectedParts"
                :max-parts="10"
                @part-added="onPartAdded"
                @part-removed="onPartRemoved"
              />
              
              <!-- 快速操作提示 -->
              <div v-if="selectedParts.length >= 2" class="quick-check-notice">
                <div class="notice-content">
                  <div class="notice-icon">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div class="notice-text">
                    <p><strong>准备就绪！</strong> 已选择 {{ selectedParts.length }} 个零件，可以开始兼容性检查了。</p>
                    <p class="notice-hint">检查将分析所有零件对之间的兼容性，并提供详细报告。</p>
                  </div>
                  <button @click="performCompatibilityCheck" class="notice-action" :disabled="isChecking">
                    {{ isChecking ? '检查中...' : '立即检查' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 检查结果标签页 -->
          <div v-if="activeTab === 'results'" class="tab-panel">
            <div class="results-panel">
              <!-- 检查状态 -->
              <div v-if="isChecking" class="checking-state">
                <div class="checking-animation">
                  <div class="checking-icon">
                    <svg class="spinning" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  </div>
                  <h3>正在进行兼容性检查...</h3>
                  <p>正在分析 {{ selectedParts.length }} 个零件之间的兼容性，请稍候</p>
                  <div class="checking-progress">
                    <div class="progress-bar">
                      <div class="progress-fill" :style="{ width: `${checkingProgress}%` }"></div>
                    </div>
                    <span class="progress-text">{{ checkingProgress }}%</span>
                  </div>
                </div>
              </div>
              
              <!-- 检查结果 -->
              <div v-else-if="checkResult" class="compatibility-results">
                <CompatibilityResultDisplay
                  :result="checkResult"
                  :detailed="true"
                />
                
                <!-- 重新检查按钮 -->
                <div class="recheck-section">
                  <button @click="performCompatibilityCheck" class="recheck-btn">
                    <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    重新检查
                  </button>
                </div>
              </div>
              
              <!-- 无结果状态 -->
              <div v-else class="no-results-state">
                <div class="no-results-content">
                  <div class="no-results-icon">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <h3>尚未进行兼容性检查</h3>
                  <p>请先在"零件选择"标签页添加至少2个零件，然后开始检查</p>
                  <button @click="activeTab = 'selection'" class="goto-selection-btn">
                    前往选择零件
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 配置分析标签页 -->
          <div v-if="activeTab === 'analysis'" class="tab-panel">
            <div class="analysis-panel">
              <ConfigurationGapAnalysis
                :current-parts="selectedParts"
                @part-added="onPartAdded"
              />
            </div>
          </div>
        </div>
      </div>
    </main>
    
    <!-- 消息提示 -->
    <Transition name="message">
      <div v-if="message.show" class="message-overlay" @click="hideMessage">
        <div class="message-toast" :class="message.type" @click.stop>
          <div class="message-content">
            <svg v-if="message.type === 'success'" class="message-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <svg v-else-if="message.type === 'error'" class="message-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <svg v-else class="message-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{{ message.text }}</span>
          </div>
          <button v-if="message.action" class="message-action" @click="message.action.callback">
            {{ message.action.text }}
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GlobalNavigation from '../components/GlobalNavigation.vue'
import CompatibilityPartSelector from '../components/CompatibilityPartSelector.vue'
import CompatibilityResultDisplay from '../components/CompatibilityResultDisplay.vue'
import ConfigurationGapAnalysis from '../components/ConfigurationGapAnalysis.vue'
import { 
  partsAPI, 
  compatibilityAPI, 
  handleCompatibilityError
} from '../utils/api'
import { compatibilityCheckManager } from '../utils/compatibilityManager'

export default {
  name: 'CompatibilityCheck',
  components: {
    GlobalNavigation,
    CompatibilityPartSelector,
    CompatibilityResultDisplay,
    ConfigurationGapAnalysis
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    // 响应式数据
    const selectedParts = ref([])
    const checkResult = ref(null)
    const isChecking = ref(false)
    const checkingProgress = ref(0)
    const activeTab = ref('selection')
    const message = ref({
      show: false,
      type: 'info',
      text: '',
      action: null
    })
    
    // 计算属性
    const hasCheckResult = computed(() => checkResult.value !== null)
    const showConfigAnalysis = computed(() => selectedParts.value.length > 0)
    
    // URL参数解析
    const parseUrlParams = async () => {
      // 直接解析路由参数
      const params = {
        partIds: [],
        autoCheck: false,
        detailLevel: 'standard'
      }
      
      // 解析零件ID
      if (route.query.parts) {
        const parts = route.query.parts.split(',')
        params.partIds = parts
          .map(id => parseInt(id.trim()))
          .filter(id => !isNaN(id) && id > 0)
          .slice(0, 10) // 限制最多10个
      }
      
      // 解析自动检查参数
      if (route.query.auto === '1' || route.query.auto === 'true') {
        params.autoCheck = true
      }
      
      // 解析详细程度参数
      if (['basic', 'standard', 'detailed'].includes(route.query.detail)) {
        params.detailLevel = route.query.detail
      }
      
      if (params.partIds.length > 0) {
        try {
          // 从API获取零件详细信息
          const partDetails = await Promise.all(
            params.partIds.map(async (id) => {
              try {
                const response = await partsAPI.getPart(id)
                return response.data
              } catch (error) {
                console.warn(`获取零件${id}失败:`, error)
                return null
              }
            })
          )
          
          // 过滤掉获取失败的零件
          const validParts = partDetails.filter(part => part !== null)
          selectedParts.value = validParts
          
          // 同步到兼容性检查管理器
          compatibilityCheckManager.clearCheckList()
          validParts.forEach(part => {
            compatibilityCheckManager.addToCheck(part)
          })
          
          // 如果启用自动检查
          if (params.autoCheck && validParts.length >= 2) {
            nextTick(() => {
              performCompatibilityCheck()
            })
          }
          
          // 显示加载结果
          if (validParts.length !== params.partIds.length) {
            const failedCount = params.partIds.length - validParts.length
            showMessage({
              type: 'warning',
              text: `成功加载${validParts.length}个零件，${failedCount}个零件加载失败`
            })
          } else if (validParts.length > 0) {
            showMessage({
              type: 'success',
              text: `成功加载${validParts.length}个零件`
            })
          }
          
        } catch (error) {
          console.error('解析URL参数失败:', error)
          showMessage({
            type: 'error',
            text: '加载零件信息失败，请重新选择'
          })
        }
      }
    }
    
    // 兼容性检查
    const performCompatibilityCheck = async () => {
      if (selectedParts.value.length < 2) {
        showMessage({
          type: 'warning',
          text: '至少需要选择2个零件才能进行兼容性检查'
        })
        return
      }
      
      isChecking.value = true
      checkingProgress.value = 0
      activeTab.value = 'results'
      
      // 模拟进度更新
      const progressInterval = setInterval(() => {
        if (checkingProgress.value < 90) {
          checkingProgress.value += Math.random() * 20
        }
      }, 200)
      
      try {
        const partIds = selectedParts.value.map(part => part.id)
        
        const response = await compatibilityAPI.check({
          part_ids: partIds,
          detail_level: 'detailed',
          include_cache: true
        })
        
        checkResult.value = response.data || response
        checkingProgress.value = 100
        
        // 更新URL以反映当前状态
        const query = { ...route.query, parts: partIds.join(',') }
        router.replace({ query })
        
        showMessage({
          type: 'success',
          text: `兼容性检查完成！整体评分: ${checkResult.value.overall_score}分`
        })
        
      } catch (error) {
        console.error('兼容性检查失败:', error)
        const errorMessage = handleCompatibilityError(error)
        
        showMessage({
          type: 'error',
          text: `检查失败: ${errorMessage}`,
          action: {
            text: '重试',
            callback: () => {
              hideMessage()
              performCompatibilityCheck()
            }
          }
        })
        
        checkResult.value = null
        
      } finally {
        clearInterval(progressInterval)
        isChecking.value = false
        checkingProgress.value = 0
      }
    }
    
    // 零件管理
    const onPartAdded = (part) => {
      // 同步到兼容性检查管理器
      const result = compatibilityCheckManager.addToCheck(part)
      
      if (result.success) {
        showMessage({
          type: 'success',
          text: result.message
        })
        
        // 清除之前的检查结果（因为零件列表改变了）
        if (checkResult.value) {
          checkResult.value = null
          showMessage({
            type: 'info',
            text: '零件列表已更改，请重新进行兼容性检查'
          })
        }
      } else {
        showMessage({
          type: 'warning',
          text: result.message
        })
      }
    }
    
    const onPartRemoved = (part) => {
      // 从兼容性检查管理器中移除
      compatibilityCheckManager.removeFromCheck(part.id)
      
      showMessage({
        type: 'info',
        text: `已移除零件: ${part.name}`
      })
      
      // 清除检查结果
      if (checkResult.value) {
        checkResult.value = null
        
        if (selectedParts.value.length < 2) {
          activeTab.value = 'selection'
          showMessage({
            type: 'info',
            text: '零件不足，请添加更多零件进行检查'
          })
        }
      }
    }
    
    const clearAllParts = () => {
      selectedParts.value = []
      compatibilityCheckManager.clearCheckList()
      checkResult.value = null
      activeTab.value = 'selection'
      
      // 清除URL参数
      router.replace({ query: {} })
      
      showMessage({
        type: 'info',
        text: '已清空所有零件'
      })
    }
    
    // 消息提示
    const showMessage = (msg) => {
      message.value = {
        show: true,
        type: msg.type || 'info',
        text: msg.text,
        action: msg.action || null
      }
      
      // 自动隐藏（除非有操作按钮）
      if (!msg.action) {
        setTimeout(() => {
          hideMessage()
        }, 3000)
      }
    }
    
    const hideMessage = () => {
      message.value.show = false
    }
    
    // 监听器
    watch(() => route.query, () => {
      if (route.name === 'CompatibilityCheck') {
        parseUrlParams()
      }
    })
    
    // 从兼容性检查管理器同步初始状态
    const syncFromManager = () => {
      const managerList = compatibilityCheckManager.getCheckList()
      if (managerList.length > 0 && selectedParts.value.length === 0) {
        selectedParts.value = managerList
      }
    }
    
    // 生命周期
    onMounted(() => {
      syncFromManager()
      parseUrlParams()
    })
    
    return {
      selectedParts,
      checkResult,
      isChecking,
      checkingProgress,
      activeTab,
      message,
      hasCheckResult,
      showConfigAnalysis,
      performCompatibilityCheck,
      onPartAdded,
      onPartRemoved,
      clearAllParts,
      showMessage,
      hideMessage
    }
  }
}
</script>

<style scoped>
.compatibility-check-page {
  min-height: 100vh;
  background: var(--bg-primary);
}

/* 页面头部 */
.page-header {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  padding: 24px 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
}

.header-info {
  flex: 1;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.page-description {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

.quick-actions {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

.check-btn,
.clear-btn,
.guide-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.check-btn.primary {
  background: var(--primary);
  color: white;
}

.check-btn.primary:hover:not(:disabled) {
  background: var(--secondary);
  transform: translateY(-1px);
}

.check-btn.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.clear-btn.secondary {
  background: var(--bg-secondary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.clear-btn.secondary:hover {
  color: #f43f5e;
  border-color: #f43f5e;
  background: color-mix(in srgb, #f43f5e 5%, transparent);
}

.guide-btn.outline {
  background: transparent;
  color: var(--primary);
  border: 1px solid var(--primary);
}

.guide-btn.outline:hover {
  background: var(--primary);
  color: white;
}

.btn-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.btn-icon.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 主要内容 */
.main-content {
  padding: 32px 0;
}

/* 进度指示器 */
.progress-indicator {
  margin-bottom: 32px;
}

.progress-steps {
  display: flex;
  align-items: center;
  justify-content: center;
  max-width: 600px;
  margin: 0 auto;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  opacity: 0.5;
  transition: opacity 0.3s ease;
}

.progress-step.active {
  opacity: 1;
}

.progress-step.completed {
  opacity: 1;
}

.step-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--bg-secondary);
  border: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 8px;
  transition: all 0.3s ease;
}

.progress-step.active .step-icon {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

.progress-step.completed .step-icon {
  background: #10b981;
  border-color: #10b981;
  color: white;
}

.step-info {
  max-width: 120px;
}

.step-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.step-description {
  font-size: 12px;
  color: var(--text-muted);
}

.progress-connector {
  width: 80px;
  height: 2px;
  background: var(--border-color);
  margin: 0 16px;
  position: relative;
  top: -20px;
  transition: background-color 0.3s ease;
}

.progress-connector.active {
  background: var(--primary);
}

/* 标签页导航 */
.tabs-navigation {
  display: flex;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px 12px 0 0;
  overflow: hidden;
}

.tab-button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px 20px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.tab-button:hover:not(:disabled) {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.tab-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.tab-button.active {
  background: var(--primary);
  color: white;
}

.tab-button:not(:last-child)::after {
  content: '';
  position: absolute;
  right: 0;
  top: 20%;
  bottom: 20%;
  width: 1px;
  background: var(--border-color);
}

.tab-button.active::after {
  display: none;
}

.tab-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.tab-badge {
  background: white;
  color: var(--primary);
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  min-width: 18px;
  text-align: center;
}

.tab-button.active .tab-badge {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.tab-badge.info {
  background: #f59e0b;
  color: white;
}

.tab-button.active .tab-badge.info {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

/* 标签页内容 */
.tabs-content {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-top: none;
  border-radius: 0 0 12px 12px;
  min-height: 400px;
}

.tab-panel {
  padding: 24px;
}

/* 零件选择面板 */
.selection-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.quick-check-notice {
  background: color-mix(in srgb, var(--primary) 5%, transparent);
  border: 1px solid color-mix(in srgb, var(--primary) 20%, transparent);
  border-radius: 12px;
  padding: 20px;
}

.notice-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.notice-icon {
  width: 24px;
  height: 24px;
  color: var(--primary);
  flex-shrink: 0;
  margin-top: 2px;
}

.notice-text {
  flex: 1;
}

.notice-text p {
  margin: 0 0 4px 0;
  color: var(--text-primary);
  line-height: 1.5;
}

.notice-hint {
  font-size: 13px;
  color: var(--text-secondary);
}

.notice-action {
  padding: 8px 16px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.notice-action:hover:not(:disabled) {
  background: var(--secondary);
}

.notice-action:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 检查状态 */
.checking-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.checking-animation {
  text-align: center;
  max-width: 400px;
}

.checking-icon {
  width: 64px;
  height: 64px;
  color: var(--primary);
  margin: 0 auto 24px;
}

.checking-animation h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.checking-animation p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 24px 0;
  line-height: 1.5;
}

.checking-progress {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: var(--bg-secondary);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--secondary));
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  min-width: 40px;
  text-align: right;
}

/* 检查结果 */
.compatibility-results {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.recheck-section {
  display: flex;
  justify-content: center;
  padding: 20px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.recheck-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.recheck-btn:hover {
  background: var(--secondary);
  transform: translateY(-1px);
}

/* 无结果状态 */
.no-results-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.no-results-content {
  text-align: center;
  max-width: 400px;
}

.no-results-icon {
  width: 64px;
  height: 64px;
  color: var(--text-muted);
  margin: 0 auto 24px;
}

.no-results-content h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.no-results-content p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 24px 0;
  line-height: 1.5;
}

.goto-selection-btn {
  padding: 10px 20px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.goto-selection-btn:hover {
  background: var(--secondary);
  transform: translateY(-1px);
}

/* 分析面板 */
.analysis-panel {
  min-height: 400px;
}

/* 消息提示 */
.message-overlay {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
}

.message-toast {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: var(--shadow-lg);
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 300px;
  max-width: 500px;
}

.message-toast.success {
  border-color: #10b981;
  background: color-mix(in srgb, #10b981 5%, var(--bg-card));
}

.message-toast.error {
  border-color: #f43f5e;
  background: color-mix(in srgb, #f43f5e 5%, var(--bg-card));
}

.message-toast.warning {
  border-color: #f59e0b;
  background: color-mix(in srgb, #f59e0b 5%, var(--bg-card));
}

.message-toast.info {
  border-color: var(--primary);
  background: color-mix(in srgb, var(--primary) 5%, var(--bg-card));
}

.message-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.message-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.message-toast.success .message-icon {
  color: #10b981;
}

.message-toast.error .message-icon {
  color: #f43f5e;
}

.message-toast.warning .message-icon {
  color: #f59e0b;
}

.message-toast.info .message-icon {
  color: var(--primary);
}

.message-content span {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.4;
}

.message-action {
  padding: 6px 12px;
  font-size: 13px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.message-action:hover {
  background: var(--secondary);
}

/* 过渡动画 */
.message-enter-active,
.message-leave-active {
  transition: all 0.3s ease;
}

.message-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

.message-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .quick-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .progress-steps {
    flex-direction: column;
    gap: 20px;
  }
  
  .progress-connector {
    width: 2px;
    height: 40px;
    margin: 0;
    top: 0;
  }
  
  .step-info {
    max-width: none;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 16px 0;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .main-content {
    padding: 24px 0;
  }
  
  .tab-panel {
    padding: 16px;
  }
  
  .quick-actions {
    flex-direction: column;
    gap: 8px;
  }
  
  .check-btn,
  .clear-btn,
  .guide-btn {
    justify-content: center;
    width: 100%;
  }
  
  .tabs-navigation {
    flex-direction: column;
  }
  
  .tab-button {
    justify-content: flex-start;
    padding: 12px 16px;
  }
  
  .tab-button:not(:last-child)::after {
    display: none;
  }
  
  .notice-content {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .notice-action {
    align-self: flex-start;
  }
  
  .message-overlay {
    left: 16px;
    right: 16px;
    transform: none;
  }
  
  .message-toast {
    min-width: auto;
    max-width: none;
  }
}

@media (max-width: 480px) {
  .progress-steps {
    gap: 16px;
  }
  
  .step-icon {
    width: 40px;
    height: 40px;
  }
  
  .step-title {
    font-size: 13px;
  }
  
  .step-description {
    font-size: 11px;
  }
  
  .checking-icon,
  .no-results-icon {
    width: 48px;
    height: 48px;
  }
  
  .checking-animation h3,
  .no-results-content h3 {
    font-size: 18px;
  }
}
</style>