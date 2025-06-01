<!-- portal/src/views/Search.vue (更新版本 - 支持兼容性筛选标签页) -->
<template>
  <div class="search-page">
    <!-- 全局导航（带搜索框） -->
    <GlobalNavigation>
      <template #search>
        <div class="nav-search-wrapper">
          <SearchBox 
            ref="searchBoxRef"
            :placeholder="'搜索零件、型号、参数...'"
            @search="onSearch"
          />
        </div>
      </template>
    </GlobalNavigation>
    
    <!-- 搜索结果区域 -->
    <main class="search-main">
      <div class="container">
        <!-- 筛选栏 -->
        <aside class="filters-sidebar">
          <!-- 高级筛选按钮 -->
          <div class="filter-section">
            <button @click="showAdvancedFilters = true" class="advanced-filter-btn primary">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
              </svg>
              高级筛选
              <span v-if="hasActiveFilters" class="filter-badge">{{ totalActiveFiltersCount }}</span>
            </button>
          </div>

          <!-- 活跃筛选条件显示 -->
          <div v-if="hasActiveFilters" class="active-filters-section">
            <div class="active-filters-header">
              <h3 class="filter-title">当前筛选</h3>
              <button @click="clearAllFilters" class="clear-filters-btn">
                清除全部
              </button>
            </div>
            
            <!-- 兼容性筛选状态 -->
            <div v-if="hasCompatibilityFilters" class="active-filter-item compatibility">
              <div class="filter-type-header">
                <svg class="filter-type-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="filter-type-label">兼容性筛选</span>
                <span class="filter-type-count">{{ compatibilityFiltersCount }}个零件</span>
              </div>
              <div class="filter-description">
                评分≥{{ currentFilters.compatibility.minScore }}分
              </div>
            </div>
            
            <!-- 传统筛选状态 -->
            <div v-if="hasTraditionalFilters" class="active-filter-item traditional">
              <div class="filter-type-header">
                <svg class="filter-type-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
                </svg>
                <span class="filter-type-label">传统筛选</span>
                <span class="filter-type-count">{{ traditionalFiltersCount }}个条件</span>
              </div>
              <div class="filter-description">
                {{ traditionalFiltersDescription }}
              </div>
            </div>
            
            <button @click="showAdvancedFilters = true" class="edit-filters-btn">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              编辑筛选条件
            </button>
          </div>

          <!-- 智能提示 -->
          <div v-if="compatibilityCheckCount > 0 && !hasCompatibilityFilters" class="compatibility-suggestion">
            <div class="suggestion-content">
              <svg class="suggestion-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>您有{{ compatibilityCheckCount }}个零件待检查兼容性</span>
            </div>
            <button @click="openCompatibilityFilters" class="suggestion-btn">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              启用兼容性筛选
            </button>
          </div>

          <!-- 搜索统计 -->
          <div v-if="searchPerformed" class="search-stats">
            <div class="stats-header">
              <h3 class="filter-title">搜索统计</h3>
            </div>
            <div class="stats-content">
              <div class="stat-item">
                <span class="stat-label">搜索模式:</span>
                <span class="stat-value" :class="searchMode">
                  {{ searchModeText }}
                </span>
              </div>
              <div class="stat-item">
                <span class="stat-label">执行时间:</span>
                <span class="stat-value">{{ searchDuration }}ms</span>
              </div>
              <div v-if="searchMode === 'hybrid'" class="stat-item">
                <span class="stat-label">筛选步骤:</span>
                <span class="stat-value">兼容性 → 传统筛选</span>
              </div>
            </div>
          </div>
        </aside>
        
        <!-- 结果内容 -->
        <div class="results-content">
          <!-- 结果信息 -->
          <div class="results-header">
            <div class="results-info">
              <h2 class="results-title">
                <span v-if="searchQuery">
                  "{{ searchQuery }}" 的搜索结果
                </span>
                <span v-else-if="hasCompatibilityFilters">
                  兼容性筛选结果
                </span>
                <span v-else-if="hasTraditionalFilters">
                  高级筛选结果
                </span>
                <span v-else>
                  所有零件
                </span>
              </h2>
              <p class="results-count">
                找到 {{ totalResults }} 个结果
                <span v-if="parts.length < totalResults">
                  (显示前 {{ parts.length }} 个)
                </span>
                <span v-if="searchDuration > 0" class="search-duration">
                  ({{ searchDuration }}ms)
                </span>
              </p>
            </div>
            
            <!-- 排序和视图选项 -->
            <div class="results-controls">
              <select v-model="sortBy" @change="onSortChange" class="sort-select">
                <option value="name">按名称排序</option>
                <option value="category">按分类排序</option>
                <option value="created_at">按创建时间排序</option>
                <option v-if="hasCompatibilityFilters" value="compatibility_score">按兼容性评分排序</option>
                <option v-for="numField in availableNumericSorts" :key="numField.field" :value="numField.field">
                  按{{ numField.label }}排序
                </option>
              </select>
              
              <button @click="toggleSortOrder" class="sort-order-btn" :title="`排序: ${sortOrder === 'asc' ? '升序' : '降序'}`">
                <svg v-if="sortOrder === 'asc'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
                </svg>
                <svg v-else fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4" />
                </svg>
              </button>
            </div>
          </div>
          
          <!-- 加载状态 -->
          <div v-if="loading && parts.length === 0" class="loading-container">
            <div class="loading-spinner"></div>
            <p>{{ loadingText }}</p>
          </div>
          
          <!-- 无结果 -->
          <div v-else-if="parts.length === 0 && !loading" class="no-results">
            <div class="no-results-icon">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3>未找到相关零件</h3>
            <p v-if="hasCompatibilityFilters">
              尝试降低兼容性评分要求或调整其他筛选条件
            </p>
            <p v-else-if="hasTraditionalFilters">
              尝试调整筛选条件或搜索关键词
            </p>
            <p v-else>
              尝试使用不同的关键词或筛选条件
            </p>
            <div class="no-results-actions">
              <button v-if="hasActiveFilters" class="btn btn-outline" @click="clearAllFilters">
                清除所有筛选条件
              </button>
              <button class="btn btn-primary" @click="showAdvancedFilters = true">
                使用高级筛选
              </button>
              <button v-if="!hasCompatibilityFilters && compatibilityCheckCount > 0" class="btn btn-secondary" @click="openCompatibilityFilters">
                启用兼容性筛选
              </button>
            </div>
          </div>
          
          <!-- 结果网格 -->
          <div v-else class="results-grid">
            <PartCard 
              v-for="part in parts" 
              :key="part.id"
              :part="part"
              @favorite="onFavorite"
              @compare="onCompare"
              @message="showMessage"
            />
          </div>

          <!-- 加载更多 -->
          <div v-if="canLoadMore" class="load-more-section">
            <div v-if="loading" class="loading-more">
              <div class="loading-spinner small"></div>
              <span>加载更多...</span>
            </div>
            <button v-else @click="loadMore" class="load-more-btn">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
              </svg>
              加载更多 (剩余 {{ remainingPages }} 页)
            </button>
          </div>
        </div>
      </div>
    </main>

    <!-- 高级筛选器模态框 -->
    <AdvancedFilters
      :show="showAdvancedFilters"
      :initial-filters="currentFilters"
      @close="showAdvancedFilters = false"
      @apply="onApplyAdvancedFilters"
      @preview="onPreviewFilters"
    />
    
    <!-- 消息提示组件 -->
    <div v-if="message.show" class="message-overlay" @click="hideMessage">
      <div class="message-toast" :class="message.type">
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
  </div>
</template>

<script>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GlobalNavigation from '../components/GlobalNavigation.vue'
import SearchBox from '../components/SearchBox.vue'
import PartCard from '../components/PartCard.vue'
import AdvancedFilters from '../components/AdvancedFilters.vue'
import { partsAPI, compatibilityAPI, handleCompatibilityError, advancedFiltersManager, filtersUtils } from '../utils/api'
import { compatibilityCheckManager } from '../utils/compatibilityManager'

export default {
  name: 'Search',
  components: {
    GlobalNavigation,
    SearchBox,
    PartCard,
    AdvancedFilters
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const searchBoxRef = ref(null)
    
    const parts = ref([])
    const totalResults = ref(0)
    const availableNumericSorts = ref([])
    const loading = ref(false)
    const searchQuery = ref('')
    const sortBy = ref('name')
    const sortOrder = ref('asc')
    const searchDuration = ref(0)
    const limit = ref(20)
    const currentPage = ref(0)
    const searchPerformed = ref(false)
    
    // 筛选器状态
    const showAdvancedFilters = ref(false)
    const currentFilters = ref({
      traditional: {
        categories: [],
        numeric_filters: {},
        enum_filters: {},
        boolean_filters: {}
      },
      compatibility: {
        enabled: false,
        selectedParts: [],
        minScore: 70
      },
      activeTab: 'traditional'
    })
    
    // 消息提示状态
    const message = ref({
      show: false,
      type: 'info',
      text: '',
      action: null
    })
    
    // 兼容性检查管理器状态
    const compatibilityCheckCount = computed(() => {
      return compatibilityCheckManager.getCheckCount()
    })
    
    // 计算属性
    const hasTraditionalFilters = computed(() => {
      return advancedFiltersManager.hasActiveFilters(currentFilters.value.traditional)
    })
    
    const hasCompatibilityFilters = computed(() => {
      return currentFilters.value.compatibility.enabled && currentFilters.value.compatibility.selectedParts.length > 0
    })
    
    const hasActiveFilters = computed(() => {
      return hasTraditionalFilters.value || hasCompatibilityFilters.value
    })
    
    const traditionalFiltersCount = computed(() => {
      let count = 0
      const filters = currentFilters.value.traditional
      if (filters.categories && filters.categories.length > 0) count++
      count += Object.keys(filters.numeric_filters || {}).filter(key => {
        const range = filters.numeric_filters[key]
        return range && (range.min !== null || range.max !== null)
      }).length
      count += Object.keys(filters.enum_filters || {}).filter(key => 
        filters.enum_filters[key] && filters.enum_filters[key].length > 0
      ).length
      count += Object.keys(filters.boolean_filters || {}).filter(key => 
        filters.boolean_filters[key] !== null
      ).length
      return count
    })
    
    const compatibilityFiltersCount = computed(() => {
      return currentFilters.value.compatibility.selectedParts.length
    })
    
    const totalActiveFiltersCount = computed(() => {
      return traditionalFiltersCount.value + (hasCompatibilityFilters.value ? 1 : 0)
    })
    
    const traditionalFiltersDescription = computed(() => {
      try {
        return filtersUtils.formatFilterDisplay(currentFilters.value.traditional, null)
      } catch (error) {
        return '筛选条件格式错误'
      }
    })
    
    const searchMode = computed(() => {
      if (hasCompatibilityFilters.value && hasTraditionalFilters.value) {
        return 'hybrid' // 混合模式：兼容性 + 传统
      } else if (hasCompatibilityFilters.value) {
        return 'compatibility' // 纯兼容性模式
      } else if (hasTraditionalFilters.value) {
        return 'traditional' // 传统筛选模式
      } else {
        return 'basic' // 基础搜索模式
      }
    })
    
    const searchModeText = computed(() => {
      switch (searchMode.value) {
        case 'hybrid': return '混合筛选'
        case 'compatibility': return '兼容性筛选'
        case 'traditional': return '传统筛选'
        default: return '基础搜索'
      }
    })
    
    const loadingText = computed(() => {
      switch (searchMode.value) {
        case 'hybrid': return '执行兼容性检查并应用传统筛选...'
        case 'compatibility': return '检查零件兼容性...'
        case 'traditional': return '应用高级筛选...'
        default: return '搜索中...'
      }
    })
    
    const canLoadMore = computed(() => {
      return !loading.value && parts.value.length < totalResults.value && parts.value.length > 0
    })
    
    const remainingPages = computed(() => {
      const remaining = totalResults.value - parts.value.length
      return Math.ceil(remaining / limit.value)
    })
    
    // 搜索零件
    const searchParts = async (resetPagination = true) => {
      if (resetPagination) {
        currentPage.value = 0
        parts.value = []
      }
      
      loading.value = true
      searchPerformed.value = true
      const startTime = Date.now()
      
      try {
        let results = []
        
        // 根据搜索模式执行不同的搜索策略
        if (searchMode.value === 'compatibility' || searchMode.value === 'hybrid') {
          // 第一步：执行兼容性搜索
          results = await performCompatibilitySearch()
          
          // 第二步：在兼容性结果上应用传统筛选（如果是混合模式）
          if (searchMode.value === 'hybrid' && results.length > 0) {
            results = await applyTraditionalFiltersOnResults(results)
          }
        } else {
          // 传统搜索或基础搜索
          results = await performTraditionalSearch()
        }
        
        // 第三步：应用文字搜索筛选
        if (searchQuery.value && results.length > 0) {
          results = applyTextSearchOnResults(results)
        }
        
        // 应用排序到结果
        if (results.length > 0) {
          results = applySortingToResults(results)
        }
        
        // 应用分页
        const startIndex = currentPage.value * limit.value
        const endIndex = startIndex + limit.value
        const paginatedResults = results.slice(startIndex, endIndex)
        
        if (resetPagination) {
          parts.value = paginatedResults
          totalResults.value = results.length
        } else {
          // 保持滚动位置
          const scrollPosition = window.pageYOffset
          parts.value.push(...paginatedResults)
          nextTick(() => {
            window.scrollTo(0, scrollPosition)
          })
        }
        
        // 更新可用的排序选项
        updateAvailableOptions()
        
        searchDuration.value = Date.now() - startTime
        
        // 保存最近使用的筛选
        if (hasActiveFilters.value) {
          advancedFiltersManager.saveRecentFilter(currentFilters.value.traditional)
        }
        
      } catch (error) {
        console.error('搜索失败:', error)
        if (resetPagination) {
          parts.value = []
          totalResults.value = 0
        }
        
        let errorMessage = '搜索失败，请重试'
        if (hasCompatibilityFilters.value) {
          errorMessage = handleCompatibilityError(error)
        }
        
        showMessage({
          type: 'error',
          text: errorMessage
        })
      }
      
      loading.value = false
    }
    
    // 执行兼容性搜索
    const performCompatibilitySearch = async () => {
      try {
        // 检查是否有有效的零件ID
        const selectedPartIds = currentFilters.value.compatibility.selectedParts
          .map(p => parseInt(p.id))
          .filter(id => !isNaN(id) && id > 0)
        
        if (selectedPartIds.length === 0) {
          console.warn('没有有效的零件ID用于兼容性搜索')
          return []
        }
        
        // 根据后端API要求构建参数
        const compatibilityParams = {
          selected_parts: selectedPartIds, // 确保是数字数组
          min_compatibility_score: parseInt(currentFilters.value.compatibility.minScore) || 50,
          include_theoretical: true, // 始终包含，通过评分控制
          target_categories: null, // 移除，通过传统筛选控制
          limit: Math.min(1000, 100) // 限制在合理范围内
        }
        
        console.log('执行兼容性搜索 - 处理后的参数:', compatibilityParams)
        
        const response = await compatibilityAPI.search(compatibilityParams)
        console.log('兼容性搜索响应:', response.data)
        
        // 将兼容性搜索结果转换为零件列表
        const compatibilityResults = response.data?.matches || []
        
        if (compatibilityResults.length === 0) {
          console.log('兼容性搜索无结果')
          return []
        }
        
        console.log(`兼容性搜索找到 ${compatibilityResults.length} 个匹配零件`)
        
        // 获取零件的完整信息
        const partIds = compatibilityResults.map(match => parseInt(match.part_id)).filter(id => !isNaN(id))
        
        if (partIds.length === 0) {
          console.warn('兼容性搜索结果中没有有效的零件ID')
          return []
        }
        
        try {
          const partsResponse = await partsAPI.getParts({ 
            ids: partIds.join(','),
            limit: partIds.length
          })
          
          console.log(`获取到 ${partsResponse.data.length} 个零件的详细信息`)
          
          // 合并兼容性信息到零件数据
          const partsWithCompatibility = partsResponse.data.map(part => {
            const compatibilityInfo = compatibilityResults.find(r => parseInt(r.part_id) === parseInt(part.id))
            return {
              ...part,
              compatibility_score: compatibilityInfo?.compatibility_score || 0,
              compatibility_grade: compatibilityInfo?.compatibility_grade || 'unknown'
            }
          })
          
          return partsWithCompatibility
        } catch (partsError) {
          console.error('获取零件详细信息失败:', partsError)
          // 如果获取零件详细信息失败，返回基础的零件信息
          return compatibilityResults.map(match => ({
            id: parseInt(match.part_id),
            name: match.part_name || `零件 ${match.part_id}`,
            category: match.part_category || '未知分类',
            compatibility_score: match.compatibility_score || 0,
            compatibility_grade: match.compatibility_grade || 'unknown'
          }))
        }
        
        return []
      } catch (error) {
        console.error('兼容性搜索失败:', error)
        throw error
      }
    }
    
    // 执行传统搜索
    const performTraditionalSearch = async () => {
      const params = buildTraditionalSearchParams()
      params.skip = currentPage.value * limit.value
      params.limit = Math.max(limit.value, 100) // 获取更多结果用于前端处理
      params.sort_by = sortBy.value
      params.sort_order = sortOrder.value
      
      console.log('执行传统搜索:', params)
      
      const response = await partsAPI.advancedSearch(params)
      return response.data || []
    }
    
    // 应用排序到结果
    const applySortingToResults = (results) => {
      if (!results || results.length === 0) return results
      
      return [...results].sort((a, b) => {
        let valueA, valueB
        
        switch (sortBy.value) {
          case 'name':
            valueA = (a.name || '').toLowerCase()
            valueB = (b.name || '').toLowerCase()
            break
          case 'category':
            valueA = (a.category || '').toLowerCase()
            valueB = (b.category || '').toLowerCase()
            break
          case 'created_at':
            valueA = new Date(a.created_at || 0)
            valueB = new Date(b.created_at || 0)
            break
          case 'compatibility_score':
            // 兼容性评分排序（仅在兼容性搜索时可用）
            valueA = a.compatibility_score || 0
            valueB = b.compatibility_score || 0
            break
          default:
            // 数值字段排序
            valueA = a.properties?.[sortBy.value] || a[sortBy.value] || 0
            valueB = b.properties?.[sortBy.value] || b[sortBy.value] || 0
            break
        }
        
        // 应用排序顺序
        if (sortOrder.value === 'asc') {
          return valueA < valueB ? -1 : valueA > valueB ? 1 : 0
        } else {
          return valueA > valueB ? -1 : valueA < valueB ? 1 : 0
        }
      })
    }
    const applyTraditionalFiltersOnResults = async (results) => {
      if (!hasTraditionalFilters.value || results.length === 0) {
        return results
      }
      
      try {
        // 提取零件ID
        const partIds = results.map(part => part.id)
        
        // 构建传统搜索参数，限制在兼容性结果范围内
        const params = buildTraditionalSearchParams()
        params.ids = partIds.join(',')
        params.limit = partIds.length
        
        console.log('在兼容性结果上应用传统筛选:', params)
        
        const response = await partsAPI.advancedSearch(params)
        const filteredResults = response.data || []
        
        // 保持兼容性信息
        return filteredResults.map(part => {
          const originalPart = results.find(r => r.id === part.id)
          return {
            ...part,
            compatibility_score: originalPart?.compatibility_score,
            compatibility_grade: originalPart?.compatibility_grade
          }
        })
      } catch (error) {
        console.error('应用传统筛选失败:', error)
        return results // 失败时返回原始结果
      }
    }
    
    // 在结果上应用文字搜索
    const applyTextSearchOnResults = (results) => {
      if (!searchQuery.value || results.length === 0) {
        return results
      }
      
      const query = searchQuery.value.toLowerCase()
      return results.filter(part => 
        part.name.toLowerCase().includes(query) ||
        (part.description && part.description.toLowerCase().includes(query)) ||
        (part.category && part.category.toLowerCase().includes(query))
      )
    }
    
    // 构建传统搜索参数
    const buildTraditionalSearchParams = () => {
      const params = {}
      
      if (searchQuery.value) {
        params.q = searchQuery.value
      }
      
      const filters = currentFilters.value.traditional
      
      // 处理分类筛选
      if (filters.categories && filters.categories.length > 0) {
        if (filters.categories.length === 1) {
          params.category = filters.categories[0]
        } else {
          params.categories = filters.categories.join(',')
        }
      }
      
      // 处理数值筛选
      if (filters.numeric_filters) {
        const numericParts = []
        Object.entries(filters.numeric_filters).forEach(([field, range]) => {
          if (range && (range.min !== null || range.max !== null)) {
            const min = range.min ?? ''
            const max = range.max ?? ''
            numericParts.push(`${field}:${min}:${max}`)
          }
        })
        if (numericParts.length > 0) {
          params.numeric_filters = numericParts.join(',')
        }
      }
      
      // 处理枚举筛选
      if (filters.enum_filters) {
        const enumParts = []
        Object.entries(filters.enum_filters).forEach(([field, values]) => {
          if (Array.isArray(values) && values.length > 0) {
            const cleanValues = values.filter(v => v && typeof v === 'string' && v.trim())
            if (cleanValues.length > 0) {
              enumParts.push(`${field}:${cleanValues.join(',')}`)
            }
          }
        })
        if (enumParts.length > 0) {
          params.enum_filters = enumParts.join('|')
        }
      }
      
      // 处理布尔筛选
      if (filters.boolean_filters) {
        const booleanParts = []
        Object.entries(filters.boolean_filters).forEach(([field, value]) => {
          if (value !== null && value !== undefined) {
            booleanParts.push(`${field}:${value}`)
          }
        })
        if (booleanParts.length > 0) {
          params.boolean_filters = booleanParts.join(',')
        }
      }
      
      return params
    }
    
    // 更新可用选项
    const updateAvailableOptions = () => {
      // 可以从结果中动态检测可用的数值排序字段
      availableNumericSorts.value = []
    }
    
    // 处理搜索
    const onSearch = (query) => {
      searchQuery.value = query
      updateURL()
      searchParts(true)
    }
    
    // 处理排序变化
    const onSortChange = () => {
      updateURL()
      searchParts(true)
    }
    
    // 切换排序顺序
    const toggleSortOrder = () => {
      sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
      updateURL()
      searchParts(true)
    }
    
    // 应用高级筛选
    const onApplyAdvancedFilters = (filters) => {
      console.log('应用筛选条件:', filters)
      
      // 验证兼容性筛选数据
      if (filters.compatibility && filters.compatibility.enabled) {
        console.log('兼容性筛选详情:', {
          enabled: filters.compatibility.enabled,
          selectedPartsCount: filters.compatibility.selectedParts?.length || 0,
          selectedParts: filters.compatibility.selectedParts,
          minScore: filters.compatibility.minScore
        })
        
        // 验证零件ID的有效性
        const validPartIds = filters.compatibility.selectedParts
          ?.map(p => parseInt(p.id))
          .filter(id => !isNaN(id) && id > 0) || []
        
        if (validPartIds.length === 0) {
          showMessage({
            type: 'error',
            text: '兼容性筛选中没有有效的零件，请重新选择零件'
          })
          return
        }
        
        console.log('有效的零件ID:', validPartIds)
      }
      
      // 深拷贝筛选条件
      currentFilters.value = {
        traditional: JSON.parse(JSON.stringify(filters.traditional || {})),
        compatibility: JSON.parse(JSON.stringify(filters.compatibility || {})),
        activeTab: filters.activeTab || 'traditional'
      }
      
      console.log('已更新的当前筛选:', currentFilters.value)
      
      updateURL()
      searchParts(true)
      
      showMessage({
        type: 'success',
        text: '筛选条件已应用'
      })
    }
    
    // 预览筛选结果
    const onPreviewFilters = (data) => {
      console.log('预览结果:', data)
    }
    
    // 清除所有筛选
    const clearAllFilters = () => {
      console.log('清除所有筛选条件')
      
      currentFilters.value = {
        traditional: {
          categories: [],
          numeric_filters: {},
          enum_filters: {},
          boolean_filters: {}
        },
        compatibility: {
          enabled: false,
          selectedParts: [],
          minScore: 70
        },
        activeTab: 'traditional'
      }
      
      searchQuery.value = ''
      updateURL()
      searchParts(true)
      
      showMessage({
        type: 'info',
        text: '所有筛选条件已清除'
      })
    }
    
    // 打开兼容性筛选
    const openCompatibilityFilters = () => {
      // 如果有兼容性检查列表，自动导入
      const checkList = compatibilityCheckManager.getCheckList()
      if (checkList.length > 0) {
        currentFilters.value.compatibility.selectedParts = checkList.map(part => ({
          id: part.id,
          name: part.name,
          category: part.category
        }))
        currentFilters.value.compatibility.enabled = true
      }
      
      currentFilters.value.activeTab = 'compatibility'
      showAdvancedFilters.value = true
    }
    
    // 加载更多结果
    const loadMore = () => {
      currentPage.value++
      searchParts(false)
    }
    
    // 更新URL
    const updateURL = () => {
      const query = {}
      
      if (searchQuery.value) {
        query.q = searchQuery.value
      }
      
      // 添加传统筛选参数到URL
      if (hasTraditionalFilters.value) {
        const filterQuery = filtersUtils.filtersToQuery(currentFilters.value.traditional)
        Object.assign(query, filterQuery)
      }
      
      // 添加兼容性筛选参数到URL
      if (hasCompatibilityFilters.value) {
        query.compatibility_enabled = '1'
        
        const partIds = currentFilters.value.compatibility.selectedParts
          .map(p => parseInt(p.id))
          .filter(id => !isNaN(id) && id > 0)
        
        if (partIds.length > 0) {
          query.compatibility_parts = partIds.join(',')
        }
        
        const minScore = parseInt(currentFilters.value.compatibility.minScore)
        if (!isNaN(minScore) && minScore !== 70) { // 只保存非默认值
          query.compatibility_min_score = minScore
        }
      }
      
      // 添加活跃标签
      if (currentFilters.value.activeTab !== 'traditional') {
        query.active_tab = currentFilters.value.activeTab
      }
      
      // 添加排序参数
      if (sortBy.value !== 'name') {
        query.sort_by = sortBy.value
      }
      if (sortOrder.value !== 'asc') {
        query.sort_order = sortOrder.value
      }
      
      router.replace({ query })
    }
    
    // 从URL初始化参数
    const initializeFromURL = () => {
      searchQuery.value = route.query.q || ''
      sortBy.value = route.query.sort_by || 'name'
      sortOrder.value = route.query.sort_order || 'asc'
      
      // 解析传统筛选参数
      const parsedTraditionalFilters = filtersUtils.queryToFilters(route.query)
      currentFilters.value.traditional = parsedTraditionalFilters
      
      // 解析兼容性筛选参数
      if (route.query.compatibility_enabled === '1') {
        currentFilters.value.compatibility.enabled = true
        
        if (route.query.compatibility_parts) {
          const partIds = route.query.compatibility_parts.split(',')
            .map(id => parseInt(id.trim()))
            .filter(id => !isNaN(id) && id > 0)
          
          // 从兼容性检查管理器获取零件信息，如果没有则创建简单的零件对象
          const checkList = compatibilityCheckManager.getCheckList()
          currentFilters.value.compatibility.selectedParts = partIds.map(id => {
            const existingPart = checkList.find(p => parseInt(p.id) === id)
            return existingPart || { 
              id, 
              name: `零件 ${id}`, 
              category: '未知分类' 
            }
          })
        }
        
        if (route.query.compatibility_min_score) {
          const score = parseInt(route.query.compatibility_min_score)
          if (!isNaN(score) && score >= 0 && score <= 100) {
            currentFilters.value.compatibility.minScore = score
          }
        }
      }
      
      // 解析活跃标签
      currentFilters.value.activeTab = route.query.active_tab || 'traditional'
      
      console.log('从URL初始化筛选条件:', currentFilters.value)
      
      // 设置搜索框的值
      nextTick(() => {
        if (searchBoxRef.value && searchQuery.value) {
          searchBoxRef.value.searchQuery = searchQuery.value
        }
      })
    }
    
    // 收藏零件
    const onFavorite = (part) => {
      console.log('收藏零件:', part.name)
    }
    
    // 添加到对比
    const onCompare = (part) => {
      console.log('添加到对比:', part.name)
    }
    
    // 消息提示
    const showMessage = (msg) => {
      message.value = {
        show: true,
        type: msg.type || 'info',
        text: msg.text,
        action: msg.action || null
      }
      
      // 3秒后自动隐藏（除非有操作按钮）
      if (!msg.action) {
        setTimeout(() => {
          hideMessage()
        }, 3000)
      }
    }
    
    const hideMessage = () => {
      message.value.show = false
    }
    
    // 监听路由变化
    watch(() => route.query, () => {
      initializeFromURL()
      searchParts(true)
    })
    
    // 监听兼容性检查列表变化
    watch(() => compatibilityCheckCount.value, (newCount, oldCount) => {
      // 可以在这里添加智能提示逻辑
    })
    
    onMounted(() => {
      initializeFromURL()
      searchParts(true)
    })
    
    return {
      searchBoxRef,
      parts,
      totalResults,
      availableNumericSorts,
      loading,
      searchQuery,
      sortBy,
      sortOrder,
      searchDuration,
      searchPerformed,
      showAdvancedFilters,
      currentFilters,
      message,
      compatibilityCheckCount,
      hasTraditionalFilters,
      hasCompatibilityFilters,
      hasActiveFilters,
      traditionalFiltersCount,
      compatibilityFiltersCount,
      totalActiveFiltersCount,
      traditionalFiltersDescription,
      searchMode,
      searchModeText,
      loadingText,
      canLoadMore,
      remainingPages,
      onSearch,
      onSortChange,
      toggleSortOrder,
      onApplyAdvancedFilters,
      onPreviewFilters,
      clearAllFilters,
      openCompatibilityFilters,
      loadMore,
      onFavorite,
      onCompare,
      showMessage,
      hideMessage
    }
  }
}
</script>

<style scoped>
/* 基础样式保持与原版本相同 */
.search-page {
  min-height: 100vh;
  background: var(--bg-primary);
}

.nav-search-wrapper {
  width: 100%;
}

.nav-search-wrapper :deep(.search-input) {
  height: 36px;
  padding: 8px 40px 8px 40px;
  font-size: 14px;
  border-radius: 8px;
}

.nav-search-wrapper :deep(.search-icon) {
  width: 16px;
  height: 16px;
}

.nav-search-wrapper :deep(.clear-icon) {
  width: 14px;
  height: 14px;
}

.nav-search-wrapper :deep(.search-tips) {
  display: none !important;
}

.search-main {
  padding: 24px 0;
}

.container {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 32px;
  align-items: start;
}

.filters-sidebar {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  position: sticky;
  top: 100px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.filter-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.advanced-filter-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 12px 16px;
  border: 2px solid var(--primary);
  border-radius: 8px;
  background: var(--primary);
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.advanced-filter-btn:hover {
  background: color-mix(in srgb, var(--primary) 90%, black);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.advanced-filter-btn svg {
  width: 16px;
  height: 16px;
}

.filter-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  background: var(--accent);
  color: white;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
  line-height: 1.2;
  border: 2px solid var(--bg-card);
}

.filter-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

/* 活跃筛选条件显示 */
.active-filters-section {
  border: 1px solid var(--primary);
  border-radius: 8px;
  padding: 16px;
  background: color-mix(in srgb, var(--primary) 5%, transparent);
}

.active-filters-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.clear-filters-btn {
  font-size: 11px;
  color: #f43f5e;
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.clear-filters-btn:hover {
  background: color-mix(in srgb, #f43f5e 10%, transparent);
}

.active-filter-item {
  margin-bottom: 12px;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.active-filter-item.compatibility {
  background: color-mix(in srgb, #10b981 5%, transparent);
  border-color: color-mix(in srgb, #10b981 20%, transparent);
}

.active-filter-item.traditional {
  background: color-mix(in srgb, var(--primary) 5%, transparent);
  border-color: color-mix(in srgb, var(--primary) 20%, transparent);
}

.filter-type-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.filter-type-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.filter-type-icon {
  color: var(--primary);
}

.active-filter-item.compatibility .filter-type-icon {
  color: #10b981;
}

.filter-type-label {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 13px;
}

.filter-type-count {
  font-size: 11px;
  color: var(--text-muted);
  font-weight: normal;
}

.filter-description {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
}

.edit-filters-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--primary);
  background: none;
  border: 1px solid var(--primary);
  border-radius: 4px;
  padding: 4px 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  align-self: flex-start;
  margin-top: 8px;
}

.edit-filters-btn:hover {
  background: var(--primary);
  color: white;
}

.edit-filters-btn svg {
  width: 12px;
  height: 12px;
}

/* 智能提示 */
.compatibility-suggestion {
  background: color-mix(in srgb, #10b981 10%, transparent);
  border: 1px solid color-mix(in srgb, #10b981 20%, transparent);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.suggestion-content {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
}

.suggestion-icon {
  width: 16px;
  height: 16px;
  color: #10b981;
  flex-shrink: 0;
}

.suggestion-content span {
  font-size: 12px;
  color: var(--text-secondary);
}

.suggestion-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.suggestion-btn:hover {
  background: color-mix(in srgb, #10b981 90%, black);
}

.suggestion-btn svg {
  width: 12px;
  height: 12px;
}

/* 搜索统计 */
.search-stats {
  border-top: 1px solid var(--border-color);
  padding-top: 16px;
}

.stats-header {
  margin-bottom: 12px;
}

.stats-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.stat-label {
  color: var(--text-secondary);
}

.stat-value {
  font-weight: 500;
  color: var(--text-primary);
}

.stat-value.hybrid {
  color: #8b5cf6;
}

.stat-value.compatibility {
  color: #10b981;
}

.stat-value.traditional {
  color: var(--primary);
}

.stat-value.basic {
  color: var(--text-secondary);
}

.results-content {
  min-height: 500px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.results-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.results-count {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
}

.search-duration {
  color: var(--text-muted);
  font-size: 12px;
}

.results-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sort-select {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-card);
  color: var(--text-primary);
  font-size: 14px;
}

.sort-order-btn {
  width: 32px;
  height: 32px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-card);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.sort-order-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.sort-order-btn svg {
  width: 16px;
  height: 16px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
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

.loading-spinner.small {
  width: 20px;
  height: 20px;
  border-width: 2px;
  margin-bottom: 8px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.no-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.no-results-icon {
  width: 64px;
  height: 64px;
  color: var(--text-muted);
  margin-bottom: 16px;
}

.no-results h3 {
  font-size: 20px;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.no-results p {
  color: var(--text-secondary);
  margin: 0 0 24px 0;
}

.no-results-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  gap: 8px;
  border: none;
}

.btn-primary {
  background: var(--primary);
  color: white;
}

.btn-primary:hover {
  background: color-mix(in srgb, var(--primary) 90%, black);
  transform: translateY(-1px);
}

.btn-secondary {
  background: var(--secondary);
  color: white;
}

.btn-secondary:hover {
  background: color-mix(in srgb, var(--secondary) 90%, black);
}

.btn-outline {
  background: transparent;
  color: var(--primary);
  border: 1px solid var(--primary);
}

.btn-outline:hover {
  background: var(--primary);
  color: white;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.load-more-section {
  display: flex;
  justify-content: center;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.loading-more {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 14px;
}

.load-more-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-card);
  color: var(--text-primary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.load-more-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
  transform: translateY(-1px);
  background: color-mix(in srgb, var(--primary) 5%, var(--bg-card));
}

.load-more-btn svg {
  width: 16px;
  height: 16px;
}

.message-overlay {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  animation: messageSlideIn 0.3s ease;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
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

/* 响应式设计 */
@media (max-width: 1024px) {
  .container {
    grid-template-columns: 260px 1fr;
    gap: 24px;
  }
}

@media (max-width: 768px) {
  .container {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .filters-sidebar {
    position: static;
    order: 2;
    padding: 16px;
  }
  
  .results-content {
    order: 1;
  }
  
  .results-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .results-controls {
    width: 100%;
    justify-content: space-between;
  }
  
  .results-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
  }
  
  .no-results-actions {
    flex-direction: column;
    width: 100%;
    max-width: 300px;
  }
  
  .active-filters-section {
    padding: 12px;
  }
  
  .active-filter-item {
    margin-bottom: 8px;
    padding: 8px;
  }
  
  .filter-type-header {
    gap: 6px;
  }
  
  .filter-description {
    font-size: 11px;
  }
  
  .compatibility-suggestion {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .suggestion-content {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .results-grid {
    grid-template-columns: 1fr;
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
  
  .search-stats {
    font-size: 11px;
  }
  
  .stat-item {
    font-size: 11px;
  }
  
  .active-filters-header {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }
  
  .edit-filters-btn {
    align-self: center;
  }
}
</style>