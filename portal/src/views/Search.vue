<template>
  <div class="search-page">
    <!-- 头部搜索栏 - 完全自定义布局，不依赖container -->
    <header class="search-header">
      <nav class="search-navigation">
        <div class="logo">
          <router-link to="/" style="text-decoration: none; color: inherit;">
            <h1>OpenPart</h1>
          </router-link>
          <span class="tagline">专门零件搜索</span>
        </div>
        
        <!-- 搜索框区域 -->
        <div class="search-box-container">
          <SearchBox 
            ref="searchBoxRef"
            :placeholder="'搜索零件、型号、参数...'"
            @search="onSearch"
          />
        </div>
        
        <div class="nav-actions">
          <ThemeToggle />
        </div>
      </nav>
    </header>
    
    <!-- 搜索结果区域 -->
    <main class="search-main">
      <div class="container">
        <!-- 筛选栏 -->
        <aside class="filters-sidebar">
          <div class="filter-section">
            <h3 class="filter-title">分类筛选</h3>
            <div class="filter-options">
              <label class="filter-option">
                <input 
                  type="radio" 
                  name="category" 
                  value="" 
                  v-model="filters.category"
                  @change="applyFilters"
                />
                <span>全部</span>
              </label>
              <label 
                v-for="category in availableCategories" 
                :key="category"
                class="filter-option"
              >
                <input 
                  type="radio" 
                  name="category" 
                  :value="category"
                  v-model="filters.category"
                  @change="applyFilters"
                />
                <span>{{ category }}</span>
              </label>
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
                <span v-else-if="filters.category">
                  {{ filters.category }} 分类
                </span>
                <span v-else>
                  所有零件
                </span>
              </h2>
              <p class="results-count">
                找到 {{ parts.length }} 个结果
              </p>
            </div>
            
            <!-- 排序选项 -->
            <div class="sort-options">
              <select v-model="sortBy" @change="sortResults" class="sort-select">
                <option value="name">按名称排序</option>
                <option value="category">按分类排序</option>
                <option value="created_at">按创建时间排序</option>
              </select>
            </div>
          </div>
          
          <!-- 加载状态 -->
          <div v-if="loading" class="loading-container">
            <div class="loading-spinner"></div>
            <p>搜索中...</p>
          </div>
          
          <!-- 无结果 -->
          <div v-else-if="parts.length === 0" class="no-results">
            <div class="no-results-icon">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3>未找到相关零件</h3>
            <p>尝试使用不同的关键词或筛选条件</p>
            <button class="btn btn-primary" @click="clearSearch">
              清除搜索条件
            </button>
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
        </div>
      </div>
    </main>
    
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
import SearchBox from '../components/SearchBox.vue'
import ThemeToggle from '../components/ThemeToggle.vue'
import PartCard from '../components/PartCard.vue'
import { partsAPI, favoritesManager, comparisonManager } from '../utils/api'

export default {
  name: 'Search',
  components: {
    SearchBox,
    ThemeToggle,
    PartCard
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const searchBoxRef = ref(null)
    
    const parts = ref([])
    const availableCategories = ref([])
    const loading = ref(false)
    const searchQuery = ref('')
    const sortBy = ref('name')
    
    // 消息提示状态
    const message = ref({
      show: false,
      type: 'info',
      text: '',
      action: null
    })
    
    const filters = ref({
      category: ''
    })
    
    // 搜索零件
    const searchParts = async () => {
      loading.value = true
      
      try {
        const params = {}
        
        if (searchQuery.value) {
          params.q = searchQuery.value
        }
        
        if (filters.value.category) {
          params.category = filters.value.category
        }
        
        const response = await partsAPI.search(params)
        parts.value = response.data
        
        // 提取可用分类
        const categories = new Set(parts.value.map(p => p.category).filter(Boolean))
        availableCategories.value = Array.from(categories)
        
        sortResults()
        
      } catch (error) {
        console.error('搜索失败:', error)
        parts.value = []
      }
      
      loading.value = false
    }
    
    // 排序结果
    const sortResults = () => {
      const sortedParts = [...parts.value]
      
      switch (sortBy.value) {
        case 'name':
          sortedParts.sort((a, b) => a.name.localeCompare(b.name))
          break
        case 'category':
          sortedParts.sort((a, b) => (a.category || '').localeCompare(b.category || ''))
          break
        case 'created_at':
          sortedParts.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
          break
      }
      
      parts.value = sortedParts
    }
    
    // 应用筛选
    const applyFilters = () => {
      // 更新URL查询参数
      const query = { ...route.query }
      
      if (filters.value.category) {
        query.category = filters.value.category
      } else {
        delete query.category
      }
      
      router.replace({ query })
      searchParts()
    }
    
    // 处理搜索
    const onSearch = (query) => {
      searchQuery.value = query
      router.replace({ query: { q: query } })
      searchParts()
    }
    
    // 清除搜索
    const clearSearch = () => {
      searchQuery.value = ''
      filters.value.category = ''
      router.replace({ query: {} })
      searchParts()
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
    
    // 初始化搜索参数
    const initializeSearch = () => {
      searchQuery.value = route.query.q || ''
      filters.value.category = route.query.category || ''
      
      // 设置搜索框的值
      nextTick(() => {
        if (searchBoxRef.value && searchQuery.value) {
          searchBoxRef.value.searchQuery = searchQuery.value
        }
      })
    }
    
    // 监听路由变化
    watch(() => route.query, () => {
      initializeSearch()
      searchParts()
    })
    
    onMounted(() => {
      initializeSearch()
      searchParts()
    })
    
    return {
      searchBoxRef,
      parts,
      availableCategories,
      loading,
      searchQuery,
      sortBy,
      filters,
      message,
      searchParts,
      sortResults,
      applyFilters,
      onSearch,
      clearSearch,
      onFavorite,
      onCompare,
      showMessage,
      hideMessage
    }
  }
}
</script>

<style scoped>
.search-page {
  min-height: 100vh;
  background: var(--bg-primary);
}

/* 隐藏搜索提示 */
.search-box-container :deep(.search-tips) {
  display: none !important;
}

/* 头部导航 - 模拟主页的容器边距效果 */
.search-header {
  padding: 16px 0;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(8px);
}

.search-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  max-width: 1200px;  /* 与主页container相同的最大宽度 */
  margin: 0 auto;     /* 居中对齐，与主页一致 */
  padding: 0 20px;    /* 与main.css中container相同的内边距 */
}

.logo {
  flex-shrink: 0;
}

.logo h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--primary);
}

.tagline {
  font-size: 12px;
  color: var(--text-muted);
  margin-left: 8px;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

/* 搜索框容器 */
.search-box-container {
  flex: 1;
  min-width: 300px;
  max-width: 600px;
  margin: 0 24px;
}

/* 主要内容 */
.search-main {
  padding: 24px 0;
}

.container {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 32px;
  align-items: start;
}

/* 筛选侧边栏 */
.filters-sidebar {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  position: sticky;
  top: 100px;
}

.filter-section {
  margin-bottom: 24px;
}

.filter-section:last-child {
  margin-bottom: 0;
}

.filter-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.filter-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: background-color 0.2s ease;
}

.filter-option:hover {
  background: var(--bg-secondary);
}

.filter-option input[type="radio"] {
  margin: 0;
}

.filter-option span {
  font-size: 14px;
  color: var(--text-secondary);
}

/* 结果内容 */
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

.sort-select {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-card);
  color: var(--text-primary);
  font-size: 14px;
}

/* 加载状态 */
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

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 无结果 */
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

/* 结果网格 */
.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

/* 消息提示样式 */
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
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .filters-sidebar {
    position: static;
    order: 2;
  }
  
  .results-content {
    order: 1;
  }
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .container {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .filters-sidebar {
    position: static;
    order: 2;
  }
  
  .results-content {
    order: 1;
  }
}

@media (max-width: 768px) {
  .search-navigation {
    padding: 0 16px; /* 移动端边距与main.css一致 */
    gap: 12px;
  }
  
  .logo h1 {
    font-size: 20px;
  }
  
  .search-box-container {
    min-width: 200px;
    max-width: none;
    margin: 0 12px;
  }
  
  .results-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .results-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
  }
  
  .filters-sidebar {
    padding: 16px;
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
  .search-nav {
    gap: 8px;
  }
  
  .search-box-container {
    min-width: 150px;
  }
  
  .logo {
    font-size: 16px;
  }
}
</style>