<!-- portal/src/views/Search.vue (最终修复版本 - 解决排序和筛选问题) -->
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
              <span v-if="hasActiveAdvancedFilters" class="filter-badge">{{ activeFiltersCount }}</span>
            </button>
          </div>

          <!-- 活跃筛选条件显示 -->
          <div v-if="hasActiveAdvancedFilters" class="active-filters-section">
            <div class="active-filters-header">
              <h3 class="filter-title">当前筛选</h3>
              <button @click="clearAdvancedFilters" class="clear-filters-btn">
                清除全部
              </button>
            </div>
            <div class="active-filters">
              <div class="filter-description">
                {{ activeFiltersDescription }}
              </div>
              <button @click="showAdvancedFilters = true" class="edit-filters-btn">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                编辑筛选
              </button>
            </div>
          </div>

          <!-- 最近使用的筛选 -->
          <div v-if="recentFilters.length > 0" class="recent-filters-section">
            <h3 class="filter-title">最近使用</h3>
            <div class="recent-filters">
              <button 
                v-for="recent in recentFilters.slice(0, 3)" 
                :key="recent.hash"
                @click="loadRecentFilter(recent)"
                class="recent-filter-btn"
                :title="recent.description"
              >
                {{ recent.description.length > 30 ? recent.description.substring(0, 30) + '...' : recent.description }}
              </button>
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
                <span v-else-if="hasActiveAdvancedFilters">
                  筛选结果
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
            <p>搜索中...</p>
          </div>
          
          <!-- 无结果 -->
          <div v-else-if="parts.length === 0 && !loading" class="no-results">
            <div class="no-results-icon">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3>未找到相关零件</h3>
            <p v-if="hasActiveAdvancedFilters">尝试调整筛选条件或搜索关键词</p>
            <p v-else>尝试使用不同的关键词或筛选条件</p>
            <div class="no-results-actions">
              <button v-if="hasActiveAdvancedFilters" class="btn btn-outline" @click="clearAllFilters">
                清除筛选条件
              </button>
              <button class="btn btn-primary" @click="showAdvancedFilters = true">
                使用高级筛选
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
      :initial-filters="advancedFilters"
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
import { partsAPI, favoritesManager, comparisonManager, advancedFiltersManager, filtersUtils } from '../utils/api'

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
    
    // 筛选器状态
    const showAdvancedFilters = ref(false)
    const advancedFilters = ref({
      categories: [],
      numeric_filters: {},
      enum_filters: {},
      boolean_filters: {}
    })
    const filtersMetadata = ref(null)
    const recentFilters = ref([])
    
    // 消息提示状态
    const message = ref({
      show: false,
      type: 'info',
      text: '',
      action: null
    })
    
    // 计算属性
    const hasActiveAdvancedFilters = computed(() => {
      return advancedFiltersManager.hasActiveFilters(advancedFilters.value)
    })
    
    const activeFiltersCount = computed(() => {
      let count = 0
      if (advancedFilters.value.categories && advancedFilters.value.categories.length > 0) count++
      count += Object.keys(advancedFilters.value.numeric_filters || {}).filter(key => {
        const range = advancedFilters.value.numeric_filters[key]
        return range && (range.min !== null || range.max !== null)
      }).length
      count += Object.keys(advancedFilters.value.enum_filters || {}).filter(key => 
        advancedFilters.value.enum_filters[key] && advancedFilters.value.enum_filters[key].length > 0
      ).length
      count += Object.keys(advancedFilters.value.boolean_filters || {}).filter(key => 
        advancedFilters.value.boolean_filters[key] !== null
      ).length
      return count
    })
    
    const activeFiltersDescription = computed(() => {
      if (!filtersMetadata.value) return ''
      return filtersUtils.formatFilterDisplay(advancedFilters.value, filtersMetadata.value)
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
      const startTime = Date.now()
      
      try {
        const params = buildSearchParams()
        params.skip = currentPage.value * limit.value
        params.limit = limit.value
        params.sort_by = sortBy.value
        params.sort_order = sortOrder.value
        
        console.log('发送搜索请求:', params) // 调试日志
        
        // 统一使用高级搜索API，支持排序
        const response = await partsAPI.advancedSearch(params)
        
        const newParts = response.data || []
        console.log('搜索结果:', newParts.length, '个零件') // 调试日志
        
        if (resetPagination) {
          parts.value = newParts
        } else {
          // 保持滚动位置
          const scrollPosition = window.pageYOffset
          parts.value.push(...newParts)
          nextTick(() => {
            window.scrollTo(0, scrollPosition)
          })
        }
        
        // 更新总数（简化处理）
        if (resetPagination) {
          totalResults.value = newParts.length >= limit.value ? newParts.length * 2 : newParts.length
        } else if (newParts.length < limit.value) {
          totalResults.value = parts.value.length
        }
        
        // 更新可用的数值排序字段
        updateAvailableOptions()
        
        searchDuration.value = Date.now() - startTime
        
        // 保存最近使用的筛选
        if (hasActiveAdvancedFilters.value) {
          advancedFiltersManager.saveRecentFilter(advancedFilters.value)
          loadRecentFilters()
        }
        
      } catch (error) {
        console.error('搜索失败:', error)
        if (resetPagination) {
          parts.value = []
          totalResults.value = 0
        }
        showMessage({
          type: 'error',
          text: '搜索失败，请重试'
        })
      }
      
      loading.value = false
    }
    
    // 构建搜索参数
    const buildSearchParams = () => {
      const params = {}
      
      if (searchQuery.value) {
        params.q = searchQuery.value
      }
      
      // 处理分类筛选
      if (advancedFilters.value.categories && advancedFilters.value.categories.length > 0) {
        if (advancedFilters.value.categories.length === 1) {
          params.category = advancedFilters.value.categories[0]
        } else {
          params.categories = advancedFilters.value.categories.join(',')
        }
      }
      
      // 处理数值筛选
      if (advancedFilters.value.numeric_filters) {
        const numericParts = []
        Object.entries(advancedFilters.value.numeric_filters).forEach(([field, range]) => {
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
      if (advancedFilters.value.enum_filters) {
        const enumParts = []
        Object.entries(advancedFilters.value.enum_filters).forEach(([field, values]) => {
          if (Array.isArray(values) && values.length > 0) {
            // 确保值不包含特殊字符
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
      if (advancedFilters.value.boolean_filters) {
        const booleanParts = []
        Object.entries(advancedFilters.value.boolean_filters).forEach(([field, value]) => {
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
      // 更新可用的数值排序字段
      if (filtersMetadata.value && filtersMetadata.value.numeric_filters) {
        availableNumericSorts.value = filtersMetadata.value.numeric_filters
          .filter(field => field.count > 10)
          .slice(0, 5)
      }
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
    
    // 应用高级筛选（不关闭弹窗）
    const onApplyAdvancedFilters = (filters) => {
      console.log('应用筛选条件:', filters) // 调试日志
      
      // 深拷贝并清理数据
      const cleanFilters = {
        categories: Array.isArray(filters.categories) ? [...filters.categories] : [],
        numeric_filters: { ...filters.numeric_filters },
        enum_filters: {},
        boolean_filters: { ...filters.boolean_filters }
      }
      
      // 清理枚举筛选
      if (filters.enum_filters) {
        Object.entries(filters.enum_filters).forEach(([field, values]) => {
          if (Array.isArray(values) && values.length > 0) {
            const cleanValues = values.filter(v => v && typeof v === 'string' && v.trim())
            if (cleanValues.length > 0) {
              cleanFilters.enum_filters[field] = cleanValues
            }
          }
        })
      }
      
      advancedFilters.value = cleanFilters
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
    
    // 清除高级筛选
    const clearAdvancedFilters = () => {
      console.log('清除筛选条件') // 调试日志
      
      // 完全重置筛选条件
      advancedFilters.value = {
        categories: [],
        numeric_filters: {},
        enum_filters: {},
        boolean_filters: {}
      }
      
      updateURL()
      searchParts(true)
      showMessage({
        type: 'info',
        text: '筛选条件已清除'
      })
    }
    
    // 清除所有筛选
    const clearAllFilters = () => {
      advancedFilters.value = {
        categories: [],
        numeric_filters: {},
        enum_filters: {},
        boolean_filters: {}
      }
      searchQuery.value = ''
      updateURL()
      searchParts(true)
    }
    
    // 加载最近筛选
    const loadRecentFilters = () => {
      recentFilters.value = advancedFiltersManager.getRecentFilters()
    }
    
    // 使用最近筛选
    const loadRecentFilter = (recent) => {
      advancedFilters.value = { ...recent.filters }
      updateURL()
      searchParts(true)
      showMessage({
        type: 'success',
        text: '已应用最近使用的筛选条件'
      })
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
      
      // 添加筛选参数到URL
      const filterQuery = filtersUtils.filtersToQuery(advancedFilters.value)
      Object.assign(query, filterQuery)
      
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
      
      // 解析筛选参数
      const parsedFilters = filtersUtils.queryToFilters(route.query)
      advancedFilters.value = parsedFilters
      
      console.log('从URL初始化筛选条件:', advancedFilters.value) // 调试日志
      
      // 设置搜索框的值
      nextTick(() => {
        if (searchBoxRef.value && searchQuery.value) {
          searchBoxRef.value.searchQuery = searchQuery.value
        }
      })
    }
    
    // 加载筛选元数据
    const loadFiltersMetadata = async () => {
      try {
        const response = await partsAPI.getFiltersMetadata()
        filtersMetadata.value = response.data
        console.log('筛选元数据:', filtersMetadata.value) // 调试日志
      } catch (error) {
        console.error('加载筛选元数据失败:', error)
      }
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
    
    onMounted(async () => {
      await loadFiltersMetadata()
      loadRecentFilters()
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
      showAdvancedFilters,
      advancedFilters,
      recentFilters,
      message,
      hasActiveAdvancedFilters,
      activeFiltersCount,
      activeFiltersDescription,
      canLoadMore,
      remainingPages,
      onSearch,
      onSortChange,
      toggleSortOrder,
      onApplyAdvancedFilters,
      onPreviewFilters,
      clearAdvancedFilters,
      clearAllFilters,
      loadRecentFilter,
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
/* 样式保持与之前相同 */
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
  margin-bottom: 12px;
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

.active-filters {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-description {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
  padding: 8px;
  background: var(--bg-card);
  border-radius: 4px;
  border: 1px solid var(--border-color);
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
}

.edit-filters-btn:hover {
  background: var(--primary);
  color: white;
}

.edit-filters-btn svg {
  width: 12px;
  height: 12px;
}

.recent-filters-section {
  border-top: 1px solid var(--border-color);
  padding-top: 16px;
}

.recent-filters {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.recent-filter-btn {
  text-align: left;
  font-size: 11px;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 6px 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  line-height: 1.3;
}

.recent-filter-btn:hover {
  background: var(--bg-card);
  border-color: var(--primary);
  color: var(--primary);
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
  
  .filter-description {
    font-size: 11px;
  }
  
  .recent-filter-btn {
    font-size: 10px;
    padding: 4px 6px;
  }
}
</style>