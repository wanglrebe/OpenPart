<!-- portal/src/views/Compare.vue (增强版 - 添加错误零件清理功能) -->
<template>
  <div class="compare-page">
    <!-- 头部导航 -->
    <header class="compare-header">
      <div class="container">
        <div class="compare-nav">
          <button class="back-btn" @click="goBack">
            <svg class="back-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            返回
          </button>
          
          <h1 class="page-title">零件对比</h1>
          
          <div class="nav-actions">
            <ThemeToggle />
          </div>
        </div>
      </div>
    </header>
    
    <!-- 对比内容 -->
    <main class="compare-main">
      <div class="container">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>正在加载对比数据...</p>
        </div>
        
        <!-- 错误状态 - 增强版 -->
        <div v-else-if="error" class="error-container">
          <div class="error-icon">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3>加载失败</h3>
          <p class="error-message">{{ error }}</p>
          
          <!-- 检测到无效零件时的特殊处理 -->
          <div v-if="isInvalidPartsError" class="invalid-parts-notice">
            <div class="notice-content">
              <svg class="notice-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div class="notice-text">
                <h4>检测到无效零件</h4>
                <p>对比列表中可能包含已被删除的零件，导致无法正常加载。</p>
                <div v-if="invalidPartIds.length > 0" class="invalid-parts-list">
                  <span>无效零件ID：{{ invalidPartIds.join(', ') }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 操作按钮组 -->
          <div class="error-actions">
            <button class="btn btn-outline" @click="loadComparison">
              <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              重试
            </button>
            
            <button 
              v-if="isInvalidPartsError" 
              class="btn btn-warning" 
              @click="cleanInvalidParts"
              :disabled="cleaningParts"
            >
              <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              {{ cleaningParts ? '清理中...' : '清理无效零件' }}
            </button>
            
            <button class="btn btn-primary" @click="goToSearch">
              <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              重新搜索零件
            </button>
            
            <button class="btn btn-secondary" @click="clearAllComparison">
              <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              清空对比列表
            </button>
          </div>
        </div>
        
        <!-- 对比结果 -->
        <div v-else-if="comparisonData" class="comparison-content">
          <!-- 对比概览 -->
          <div class="comparison-summary">
            <div class="summary-stats">
              <div class="stat-item">
                <span class="stat-number">{{ comparisonData.comparison_count }}</span>
                <span class="stat-label">零件对比</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ comparisonData.total_attributes }}</span>
                <span class="stat-label">对比属性</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ comparisonData.differences.different_attributes.length }}</span>
                <span class="stat-label">存在差异</span>
              </div>
            </div>
            
            <div class="summary-actions">
              <button class="btn btn-outline" @click="exportComparison">
                <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
                导出对比
              </button>
              <button class="btn btn-primary" @click="addToFavorites">
                <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
                加入收藏
              </button>
            </div>
          </div>
          
          <!-- 单零件提示 -->
          <div v-if="comparisonData.comparison_count === 1" class="single-part-notice">
            <div class="notice-content">
              <svg class="notice-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div class="notice-text">
                <h4>单零件查看模式</h4>
                <p>当前仅有1个零件，添加更多零件以进行对比分析</p>
              </div>
            </div>
            <button class="btn btn-primary" @click="goToSearch">
              <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              添加更多零件
            </button>
          </div>
          
          <!-- 零件预览卡片 -->
          <div class="parts-preview">
            <div 
              v-for="(part, index) in comparisonData.parts_info" 
              :key="part.id"
              class="part-preview-card"
            >
              <div class="part-image">
                <img 
                  v-if="part.image_url" 
                  :src="part.image_url" 
                  :alt="part.name"
                  class="part-img"
                />
                <div v-else class="part-placeholder">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </div>
              </div>
              <div class="part-info">
                <h3 class="part-name">{{ part.name }}</h3>
                <span v-if="part.category" class="part-category">{{ part.category }}</span>
              </div>
              <button 
                class="remove-part-btn"
                @click.stop="removePart(index)"
                :title="`移除 ${part.name}`"
              >
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
          
          <!-- 对比表格 -->
          <div class="comparison-table-container">
            <div class="table-controls">
              <div class="filter-options">
                <label class="filter-option">
                  <input 
                    type="checkbox" 
                    v-model="showIdentical"
                  />
                  <span>显示相同属性</span>
                </label>
                <label class="filter-option">
                  <input 
                    type="checkbox" 
                    v-model="showMissing"
                  />
                  <span>显示缺失数据</span>
                </label>
              </div>
              
              <!-- 单零件模式的特殊提示 -->
              <div v-if="comparisonData.comparison_count === 1" class="single-mode-tip">
                <span>单零件查看模式 - 显示所有属性</span>
              </div>
            </div>
            
            <div class="table-wrapper">
              <table class="comparison-table">
                <thead>
                  <tr>
                    <th class="attribute-column">属性</th>
                    <th 
                      v-for="part in comparisonData.parts_info" 
                      :key="part.id"
                      class="part-column"
                    >
                      {{ part.name }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <!-- 基本信息 -->
                  <tr class="section-header">
                    <td :colspan="comparisonData.comparison_count + 1">基本信息</td>
                  </tr>
                  <tr
                    v-for="(values, attribute) in filteredBasicComparison"
                    :key="'basic-' + attribute"
                    :class="getRowClass(attribute, values)"
                  >
                    <td class="attribute-name">{{ attribute }}</td>
                    <td 
                      v-for="(value, index) in values"
                      :key="index"
                      :class="getCellClass(value, values)"
                    >
                      {{ value }}
                    </td>
                  </tr>
                  
                  <!-- 自定义属性 -->
                  <tr v-if="Object.keys(filteredPropertiesComparison).length > 0" class="section-header">
                    <td :colspan="comparisonData.comparison_count + 1">自定义属性</td>
                  </tr>
                  <tr
                    v-for="(values, attribute) in filteredPropertiesComparison"
                    :key="'prop-' + attribute"
                    :class="getRowClass(attribute, values)"
                  >
                    <td class="attribute-name">{{ attribute }}</td>
                    <td 
                      v-for="(value, index) in values"
                      :key="index"
                      :class="getCellClass(value, values)"
                    >
                      {{ value }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </main>
    
    <!-- 消息提示组件 -->
    <div v-if="toast.show" class="toast-overlay" @click="hideToast">
      <div class="toast-message" :class="toast.type">
        <div class="toast-content">
          <svg v-if="toast.type === 'success'" class="toast-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <svg v-else-if="toast.type === 'error'" class="toast-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
          <svg v-else class="toast-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="toast-text">{{ toast.message }}</span>
        </div>
        <button v-if="toast.action" class="toast-action" @click.stop="toast.action.callback">
          {{ toast.action.text }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ThemeToggle from '../components/ThemeToggle.vue'
import { partsAPI, comparisonManager, favoritesManager } from '../utils/api'

export default {
  name: 'Compare',
  components: {
    ThemeToggle
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    const comparisonData = ref(null)
    const loading = ref(false)
    const error = ref('')
    const showIdentical = ref(false)
    const showMissing = ref(true)
    const cleaningParts = ref(false)
    const invalidPartIds = ref([])
    
    // 消息提示状态
    const toast = ref({
      show: false,
      type: 'info',
      message: '',
      action: null
    })
    
    // 从URL参数获取要对比的零件ID
    const partIds = computed(() => {
      const ids = route.query.ids
      if (typeof ids === 'string') {
        return ids.split(',').map(id => parseInt(id)).filter(id => !isNaN(id))
      } else if (Array.isArray(ids)) {
        return ids.map(id => parseInt(id)).filter(id => !isNaN(id))
      }
      return []
    })
    
    // 检测是否是无效零件错误
    const isInvalidPartsError = computed(() => {
      return error.value && (
        error.value.includes('未找到零件') || 
        error.value.includes('not found') ||
        error.value.includes('404') ||
        invalidPartIds.value.length > 0
      )
    })
    
    // 过滤后的基本对比数据
    const filteredBasicComparison = computed(() => {
      if (!comparisonData.value) return {}
      
      const filtered = {}
      const skipKeys = ['零件ID']
      
      for (const [key, values] of Object.entries(comparisonData.value.basic_comparison)) {
        if (skipKeys.includes(key)) continue
        
        // 单零件模式下显示所有属性
        if (comparisonData.value.comparison_count === 1) {
          filtered[key] = values
          continue
        }
        
        const hasIdentical = isIdentical(values)
        const hasMissing = values.includes('—')
        
        if (!showIdentical.value && hasIdentical && !hasMissing) continue
        if (!showMissing.value && hasMissing) continue
        
        filtered[key] = values
      }
      
      return filtered
    })
    
    // 过滤后的属性对比数据
    const filteredPropertiesComparison = computed(() => {
      if (!comparisonData.value) return {}
      
      const filtered = {}
      
      for (const [key, values] of Object.entries(comparisonData.value.properties_comparison)) {
        // 单零件模式下显示所有属性
        if (comparisonData.value.comparison_count === 1) {
          filtered[key] = values
          continue
        }
        
        const hasIdentical = isIdentical(values)
        const hasMissing = values.includes('—')
        
        if (!showIdentical.value && hasIdentical && !hasMissing) continue
        if (!showMissing.value && hasMissing) continue
        
        filtered[key] = values
      }
      
      return filtered
    })
    
    const loadComparison = async () => {
      if (partIds.value.length === 0) {
        error.value = '没有指定要对比的零件'
        return
      }
      
      loading.value = true
      error.value = ''
      invalidPartIds.value = []
      
      try {
        console.log('尝试加载对比数据，零件ID:', partIds.value)
        const response = await partsAPI.compare(partIds.value)
        comparisonData.value = response.data
        console.log('对比数据加载成功')
      } catch (err) {
        console.error('加载对比数据失败:', err)
        
        // 分析错误类型并提取无效的零件ID
        const errorMessage = err.response?.data?.detail || err.message || '加载对比数据失败'
        error.value = errorMessage
        
        // 尝试从错误信息中提取无效的零件ID
        if (errorMessage.includes('未找到零件')) {
          try {
            // 提取错误信息中的ID列表，例如: "未找到零件: [1, 2, 3]"
            const match = errorMessage.match(/\[([^\]]+)\]/)
            if (match) {
              const extractedIds = match[1].split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id))
              invalidPartIds.value = extractedIds
              console.log('提取到无效零件ID:', extractedIds)
            }
          } catch (e) {
            console.warn('无法解析错误信息中的零件ID:', e)
            // 如果无法解析，假设所有ID都可能有问题
            invalidPartIds.value = [...partIds.value]
          }
        }
        
        // 如果是404错误或零件不存在，尝试检测哪些零件无效
        if (err.response?.status === 404 || errorMessage.includes('not found')) {
          invalidPartIds.value = [...partIds.value]
        }
      }
      
      loading.value = false
    }
    
    // 清理无效零件
    const cleanInvalidParts = async () => {
      if (cleaningParts.value) return
      
      cleaningParts.value = true
      
      try {
        console.log('开始清理无效零件...')
        
        // 方案1: 如果我们知道具体哪些零件无效，直接移除它们
        if (invalidPartIds.value.length > 0) {
          console.log('移除已知的无效零件ID:', invalidPartIds.value)
          invalidPartIds.value.forEach(invalidId => {
            comparisonManager.removeFromComparison(invalidId)
          })
        } else {
          // 方案2: 逐个验证零件是否存在
          console.log('逐个验证零件有效性...')
          const validIds = []
          const invalidIds = []
          
          for (const partId of partIds.value) {
            try {
              await partsAPI.getPart(partId)
              validIds.push(partId)
              console.log(`零件 ${partId} 有效`)
            } catch (err) {
              invalidIds.push(partId)
              console.log(`零件 ${partId} 无效:`, err.response?.status)
              comparisonManager.removeFromComparison(partId)
            }
          }
          
          invalidPartIds.value = invalidIds
          console.log('验证完成，有效:', validIds, '无效:', invalidIds)
        }
        
        // 获取清理后的零件列表
        const remainingParts = comparisonManager.getComparisonList()
        console.log('清理后剩余零件:', remainingParts)
        
        if (remainingParts.length === 0) {
          // 如果没有有效零件了，显示提示并跳转到搜索页面
          showToast({
            type: 'info',
            message: '已清理所有无效零件，对比列表为空',
            action: {
              text: '去搜索零件',
              callback: () => {
                router.push('/search')
              }
            }
          })
        } else {
          // 如果还有有效零件，重新加载对比页面
          const validIds = remainingParts.map(part => part.id)
          await router.replace({
            name: 'Compare',
            query: { ids: validIds.join(',') }
          })
          
          showToast({
            type: 'success',
            message: `已清理 ${invalidPartIds.value.length} 个无效零件，剩余 ${validIds.length} 个零件`
          })
        }
        
      } catch (err) {
        console.error('清理无效零件时出错:', err)
        showToast({
          type: 'error',
          message: '清理过程中出现错误，请尝试手动清空对比列表'
        })
      }
      
      cleaningParts.value = false
    }
    
    // 清空所有对比零件
    const clearAllComparison = async () => {
      try {
        // 确认操作
        if (!confirm('确定要清空整个对比列表吗？此操作不可撤销。')) {
          return
        }
        
        console.log('清空所有对比零件')
        comparisonManager.clearComparison()
        
        showToast({
          type: 'success',
          message: '已清空对比列表'
        })
        
        // 跳转到首页或搜索页面
        router.push('/search')
        
      } catch (err) {
        console.error('清空对比列表失败:', err)
        showToast({
          type: 'error',
          message: '清空失败，请刷新页面重试'
        })
      }
    }
    
    const isIdentical = (values) => {
      const uniqueValues = new Set(values.filter(v => v !== '—'))
      return uniqueValues.size <= 1
    }
    
    const getRowClass = (attribute, values) => {
      // 单零件模式下不需要差异样式
      if (comparisonData.value?.comparison_count === 1) {
        return 'row-single'
      }
      
      const differences = comparisonData.value?.differences
      if (!differences) return ''
      
      if (differences.different_attributes.includes(attribute)) {
        return 'row-different'
      } else if (differences.identical_attributes.includes(attribute)) {
        return 'row-identical'
      } else if (differences.unique_attributes.includes(attribute)) {
        return 'row-unique'
      }
      return ''
    }
    
    const getCellClass = (value, values) => {
      if (value === '—') return 'cell-missing'
      
      // 单零件模式下不需要差异样式
      if (comparisonData.value?.comparison_count === 1) {
        return 'cell-single'
      }
      
      const uniqueValues = new Set(values.filter(v => v !== '—'))
      if (uniqueValues.size > 1) {
        return 'cell-different'
      }
      return 'cell-identical'
    }
    
    // 修复的移除零件函数
    const removePart = async (index) => {
      console.log('removePart called with index:', index)
      
      if (!comparisonData.value || !comparisonData.value.parts_info) {
        console.error('comparisonData 或 parts_info 不存在')
        return
      }
      
      const partToRemove = comparisonData.value.parts_info[index]
      if (!partToRemove) {
        console.error('未找到要移除的零件，索引:', index)
        return
      }
      
      console.log('准备移除零件:', partToRemove.name, 'ID:', partToRemove.id)
      
      // 从对比管理器中移除零件
      const result = comparisonManager.removeFromComparison(partToRemove.id)
      console.log('移除结果:', result)
      
      if (result.success) {
        // 获取当前的零件ID列表，移除指定索引的ID
        const currentIds = [...partIds.value]
        currentIds.splice(index, 1)
        
        console.log('剩余零件ID:', currentIds)
        
        if (currentIds.length === 0) {
          // 如果没有零件了，返回首页
          console.log('零件为空，返回首页')
          router.push('/')
        } else {
          // 更新URL并重新加载数据
          console.log('更新URL并重新加载数据')
          await router.replace({
            name: 'Compare',
            query: { ids: currentIds.join(',') }
          })
          // URL更新后会触发watch，自动重新加载数据
        }
      } else {
        console.error('移除失败:', result.message)
        alert(result.message || '移除失败，请重试')
      }
    }
    
    const goToSearch = () => {
      router.push('/search')
    }
    
    const exportComparison = () => {
      if (!comparisonData.value) return
      
      const csvData = []
      const headers = ['属性', ...comparisonData.value.parts_info.map(p => p.name)]
      csvData.push(headers)
      
      // 添加基本信息
      for (const [key, values] of Object.entries(comparisonData.value.basic_comparison)) {
        if (key === '零件ID') continue
        csvData.push([key, ...values])
      }
      
      // 添加属性信息
      for (const [key, values] of Object.entries(comparisonData.value.properties_comparison)) {
        csvData.push([key, ...values])
      }
      
      const csvContent = csvData.map(row => row.join(',')).join('\n')
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', '零件对比.csv')
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    }
    
    const addToFavorites = () => {
      if (!comparisonData.value || !comparisonData.value.parts_info) {
        console.error('没有零件可以收藏')
        return
      }

      const parts = comparisonData.value.parts_info
      let successCount = 0
      let alreadyFavoritedCount = 0
      let errorCount = 0
      const errorMessages = []

      // 逐个添加零件到收藏
      parts.forEach(part => {
        // 构造完整的零件对象（API需要的格式）
        const fullPart = {
          id: part.id,
          name: part.name,
          category: part.category,
          image_url: part.image_url,
          description: `从对比列表添加 - ${new Date().toLocaleDateString()}` // 添加描述标记来源
        }

        const result = favoritesManager.addToFavorites(fullPart)
        
        if (result.success) {
          successCount++
        } else if (result.message && result.message.includes('已在收藏列表中')) {
          alreadyFavoritedCount++
        } else {
          errorCount++
          if (result.message) {
            errorMessages.push(`${part.name}: ${result.message}`)
          }
        }
      })

      // 显示操作结果
      if (successCount > 0) {
        const message = `成功收藏 ${successCount} 个零件` + 
          (alreadyFavoritedCount > 0 ? `，其中 ${alreadyFavoritedCount} 个已在收藏夹中` : '') +
          (errorCount > 0 ? `，${errorCount} 个添加失败` : '')
        
        showToast({
          type: 'success',
          message: message,
          action: successCount > 0 ? {
            text: '查看收藏夹',
            callback: () => {
              router.push('/favorites')
            }
          } : null
        })
      } else if (alreadyFavoritedCount === parts.length) {
        showToast({
          type: 'info',
          message: '所有零件均已在收藏夹中'
        })
      } else {
        showToast({
          type: 'error',
          message: `收藏失败：${errorMessages.join(', ')}`
        })
      }
    }
    
    const goBack = () => {
      if (window.history.length > 2) {
        router.go(-1)
      } else {
        router.push('/')
      }
    }
    
    // 消息提示函数
    const showToast = (options) => {
      toast.value = {
        show: true,
        type: options.type || 'info',
        message: options.message,
        action: options.action || null
      }
      
      // 如果没有操作按钮，3秒后自动隐藏
      if (!options.action) {
        setTimeout(() => {
          hideToast()
        }, 3000)
      }
    }
    
    const hideToast = () => {
      toast.value.show = false
    }
    
    // 监听路由变化，重新加载数据
    watch(() => route.query.ids, () => {
      console.log('路由参数变化，重新加载对比数据')
      loadComparison()
    })
    
    onMounted(() => {
      loadComparison()
    })
    
    return {
      comparisonData,
      loading,
      error,
      showIdentical,
      showMissing,
      toast,
      cleaningParts,
      invalidPartIds,
      isInvalidPartsError,
      filteredBasicComparison,
      filteredPropertiesComparison,
      loadComparison,
      cleanInvalidParts,
      clearAllComparison,
      getRowClass,
      getCellClass,
      removePart,
      goToSearch,
      exportComparison,
      addToFavorites,
      goBack,
      showToast,
      hideToast
    }
  }
}
</script>

<style scoped>
/* 现有样式保持不变，添加新的错误处理样式 */

/* 无效零件提示样式 */
.invalid-parts-notice {
  background: color-mix(in srgb, #f59e0b 8%, var(--bg-card));
  border: 1px solid color-mix(in srgb, #f59e0b 30%, var(--border-color));
  border-radius: 12px;
  padding: 20px;
  margin: 20px 0;
}

.notice-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.notice-icon {
  width: 24px;
  height: 24px;
  color: #f59e0b;
  flex-shrink: 0;
  margin-top: 2px;
}

.notice-text h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.notice-text p {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.invalid-parts-list {
  font-size: 13px;
  color: var(--text-muted);
  background: color-mix(in srgb, #f59e0b 10%, transparent);
  padding: 8px 12px;
  border-radius: 6px;
  border-left: 3px solid #f59e0b;
}

/* 错误操作按钮组 */
.error-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
  margin-top: 24px;
}

.error-actions .btn {
  min-width: 140px;
}

/* 按钮样式增强 */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  border: 1px solid;
  background: none;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.btn-primary:hover:not(:disabled) {
  background: var(--secondary);
  border-color: var(--secondary);
}

.btn-outline {
  color: var(--text-primary);
  border-color: var(--border-color);
}

.btn-outline:hover:not(:disabled) {
  background: var(--bg-secondary);
  border-color: var(--primary);
  color: var(--primary);
}

.btn-warning {
  background: #f59e0b;
  color: white;
  border-color: #f59e0b;
}

.btn-warning:hover:not(:disabled) {
  background: #d97706;
  border-color: #d97706;
}

.btn-secondary {
  background: var(--text-muted);
  color: white;
  border-color: var(--text-muted);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--text-secondary);
  border-color: var(--text-secondary);
}

.btn-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

/* 错误消息样式 */
.error-message {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 8px 0 16px 0;
  text-align: center;
  max-width: 500px;
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .error-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .error-actions .btn {
    min-width: auto;
    justify-content: center;
  }
  
  .invalid-parts-notice {
    padding: 16px;
    margin: 16px 0;
  }
  
  .notice-content {
    flex-direction: column;
    gap: 12px;
  }
  
  .notice-icon {
    align-self: flex-start;
  }
}

@media (max-width: 480px) {
  .invalid-parts-list {
    font-size: 12px;
    word-break: break-all;
  }
  
  .error-message {
    font-size: 13px;
  }
}

/* 保持所有原有样式... */
.compare-page {
  min-height: 100vh;
  background: var(--bg-primary);
}

/* 头部导航 */
.compare-header {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  padding: 16px 0;
}

.compare-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: none;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: var(--bg-secondary);
  border-color: var(--primary);
}

.back-icon {
  width: 16px;
  height: 16px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

/* 主要内容 */
.compare-main {
  padding: 24px 0;
}

/* 加载和错误状态 */
.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

.error-icon {
  width: 64px;
  height: 64px;
  color: var(--text-muted);
  margin-bottom: 16px;
}

/* 对比概览 */
.comparison-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}

.summary-stats {
  display: flex;
  gap: 32px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.summary-actions {
  display: flex;
  gap: 12px;
}

/* 单零件提示样式 */
.single-part-notice {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: color-mix(in srgb, #3b82f6 5%, var(--bg-card));
  border: 1px solid color-mix(in srgb, #3b82f6 20%, var(--border-color));
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 24px;
}

.notice-content {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.notice-icon {
  width: 24px;
  height: 24px;
  color: #3b82f6;
  flex-shrink: 0;
}

.notice-text h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.notice-text p {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.single-mode-tip {
  font-size: 13px;
  color: var(--text-muted);
  font-style: italic;
}

/* 单零件模式下的行样式 */
.row-single {
  background: var(--bg-card);
}

.cell-single {
  color: var(--text-primary);
  font-weight: 500;
}

/* 响应式设计更新 */
@media (max-width: 768px) {
  .single-part-notice {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .notice-content {
    flex-direction: column;
    gap: 12px;
  }
}

/* 保持所有原有样式... */
.compare-page {
  min-height: 100vh;
  background: var(--bg-primary);
}

/* 头部导航 */
.compare-header {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  padding: 16px 0;
}

.compare-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: none;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: var(--bg-secondary);
  border-color: var(--primary);
}

.back-icon {
  width: 16px;
  height: 16px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

/* 消息提示样式 */
.toast-overlay {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  animation: toastSlideIn 0.3s ease;
}

@keyframes toastSlideIn {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.toast-message {
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
  cursor: pointer;
}

.toast-message.success {
  border-color: #10b981;
  background: color-mix(in srgb, #10b981 5%, var(--bg-card));
}

.toast-message.error {
  border-color: #f43f5e;
  background: color-mix(in srgb, #f43f5e 5%, var(--bg-card));
}

.toast-message.info {
  border-color: var(--primary);
  background: color-mix(in srgb, var(--primary) 5%, var(--bg-card));
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.toast-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.toast-message.success .toast-icon {
  color: #10b981;
}

.toast-message.error .toast-icon {
  color: #f43f5e;
}

.toast-message.info .toast-icon {
  color: var(--primary);
}

.toast-text {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.4;
}

.toast-action {
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

.toast-action:hover {
  background: var(--secondary);
}

/* 主要内容 */
.compare-main {
  padding: 24px 0;
}

/* 加载和错误状态 */
.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

.error-icon {
  width: 64px;
  height: 64px;
  color: var(--text-muted);
  margin-bottom: 16px;
}

/* 对比概览 */
.comparison-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}

.summary-stats {
  display: flex;
  gap: 32px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.summary-actions {
  display: flex;
  gap: 12px;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

/* 零件预览 */
.parts-preview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.part-preview-card {
  position: relative;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  text-align: center;
}

.part-image {
  width: 80px;
  height: 80px;
  margin: 0 auto 12px;
  background: var(--bg-secondary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.part-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: white;
}

.part-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.part-placeholder svg {
  width: 32px;
  height: 32px;
}

.part-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.part-category {
  font-size: 12px;
  color: var(--text-secondary);
  padding: 2px 8px;
  background: var(--bg-secondary);
  border-radius: 4px;
}

.remove-part-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 50%;
  background: rgba(244, 63, 94, 0.1);
  color: #f43f5e;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.2s ease;
}

.part-preview-card:hover .remove-part-btn {
  opacity: 1;
}

.remove-part-btn:hover {
  background: #f43f5e;
  color: white;
}

.remove-part-btn svg {
  width: 12px;
  height: 12px;
}

/* 对比表格 */
.comparison-table-container {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

.table-controls {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.filter-options {
  display: flex;
  gap: 24px;
}

.filter-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-secondary);
}

.filter-option input[type="checkbox"] {
  margin: 0;
}

.table-wrapper {
  overflow-x: auto;
}

.comparison-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.comparison-table th,
.comparison-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.comparison-table th {
  background: var(--bg-secondary);
  font-weight: 600;
  color: var(--text-primary);
  position: sticky;
  top: 0;
  z-index: 1;
}

.attribute-column {
  min-width: 150px;
  font-weight: 600;
  background: var(--bg-card);
  position: sticky;
  left: 0;
  border-right: 1px solid var(--border-color);
  z-index: 2;
}

.part-column {
  min-width: 120px;
  text-align: center;
}

.section-header td {
  background: var(--bg-secondary);
  font-weight: 600;
  color: var(--primary);
  text-align: center;
  padding: 8px 16px;
}

.attribute-name {
  font-weight: 500;
  color: var(--text-primary);
  background: var(--bg-card);
  position: sticky;
  left: 0;
  border-right: 1px solid var(--border-color);
  z-index: 1;
}

/* 行状态样式 */
.row-different {
  background: color-mix(in srgb, #f59e0b 5%, transparent);
}

.row-identical {
  background: color-mix(in srgb, #10b981 5%, transparent);
}

.row-unique {
  background: color-mix(in srgb, #3b82f6 5%, transparent);
}

/* 单元格状态样式 */
.cell-different {
  font-weight: 600;
  color: #f59e0b;
  background: color-mix(in srgb, #f59e0b 10%, transparent);
}

.cell-identical {
  color: var(--text-secondary);
}

.cell-missing {
  color: var(--text-muted);
  font-style: italic;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .comparison-summary {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .summary-stats {
    justify-content: center;
  }
  
  .parts-preview {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 12px;
  }
}

@media (max-width: 768px) {
  .compare-main {
    padding: 16px 0;
  }
  
  .comparison-summary {
    padding: 16px;
    margin-bottom: 16px;
  }
  
  .summary-stats {
    gap: 20px;
  }
  
  .stat-number {
    font-size: 24px;
  }
  
  .parts-preview {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 8px;
  }
  
  .part-preview-card {
    padding: 12px;
  }
  
  .part-image {
    width: 60px;
    height: 60px;
  }
  
  .comparison-table th,
  .comparison-table td {
    padding: 8px 12px;
    font-size: 13px;
  }
  
  .attribute-column {
    min-width: 120px;
  }
  
  .part-column {
    min-width: 100px;
  }
  
  .filter-options {
    flex-direction: column;
    gap: 12px;
  }
  
  .remove-part-btn {
    opacity: 1; /* 移动端始终显示删除按钮 */
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>