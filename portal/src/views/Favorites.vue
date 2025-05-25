<!-- portal/src/views/Favorites.vue (新页面) -->
<template>
  <div class="favorites-page">
    <!-- 头部导航 -->
    <header class="favorites-header">
      <div class="container">
        <div class="favorites-nav">
          <router-link to="/" class="logo-link">
            <h1 class="logo">OpenPart</h1>
          </router-link>
          
          <h2 class="page-title">我的收藏</h2>
          
          <div class="nav-actions">
            <ThemeToggle />
          </div>
        </div>
      </div>
    </header>
    
    <!-- 主要内容 -->
    <main class="favorites-main">
      <div class="container">
        <!-- 收藏概览 -->
        <div class="favorites-summary">
          <div class="summary-stats">
            <div class="stat-item">
              <span class="stat-number">{{ favorites.length }}</span>
              <span class="stat-label">收藏零件</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ uniqueCategories.length }}</span>
              <span class="stat-label">涉及分类</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ selectedFavorites.length }}</span>
              <span class="stat-label">已选择</span>
            </div>
          </div>
          
          <div class="summary-actions">
            <button 
              class="btn btn-outline"
              @click="exportFavorites"
              :disabled="favorites.length === 0"
            >
              <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
              导出收藏
            </button>
            
            <label class="btn btn-outline import-btn">
              <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
              </svg>
              导入收藏
              <input 
                type="file" 
                accept=".json"
                @change="importFavorites"
                style="display: none;"
              />
            </label>
          </div>
        </div>
        
        <!-- 操作栏 -->
        <div class="favorites-controls">
          <!-- 搜索框 -->
          <div class="search-section">
            <div class="search-input-container">
              <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                v-model="searchQuery"
                type="text"
                class="search-input"
                placeholder="搜索收藏的零件..."
                @input="filterFavorites"
              />
              <button 
                v-if="searchQuery" 
                @click="clearSearch"
                class="clear-button"
              >
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
          
          <!-- 筛选和排序 -->
          <div class="filter-section">
            <select v-model="selectedCategory" @change="filterFavorites" class="category-select">
              <option value="">所有分类</option>
              <option v-for="category in uniqueCategories" :key="category" :value="category">
                {{ category }}
              </option>
            </select>
            
            <select v-model="sortBy" @change="sortFavorites" class="sort-select">
              <option value="addedAt">按收藏时间</option>
              <option value="name">按名称排序</option>
              <option value="category">按分类排序</option>
            </select>
          </div>
          
          <!-- 批量操作 -->
          <div class="batch-controls">
            <button 
              class="selection-toggle"
              :class="{ active: selectionMode }"
              @click="toggleSelectionMode"
            >
              <svg class="selection-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ selectionMode ? '退出选择' : '批量选择' }}
            </button>
            
            <div v-if="selectionMode" class="batch-actions">
              <button class="btn btn-sm" @click="selectAll">
                {{ isAllSelected ? '取消全选' : '全选' }}
              </button>
              
              <button 
                class="btn btn-primary btn-sm"
                @click="batchCompare"
                :disabled="selectedFavorites.length < 2"
              >
                对比选中 ({{ selectedFavorites.length }})
              </button>
              
              <button 
                class="btn btn-danger btn-sm"
                @click="batchDelete"
                :disabled="selectedFavorites.length === 0"
              >
                删除选中 ({{ selectedFavorites.length }})
              </button>
            </div>
          </div>
        </div>
        
        <!-- 收藏列表 -->
        <div class="favorites-content">
          <!-- 空状态 -->
          <div v-if="favorites.length === 0" class="empty-state">
            <div class="empty-icon">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <h3>还没有收藏任何零件</h3>
            <p>在搜索和详情页面点击收藏按钮来添加你感兴趣的零件</p>
            <router-link to="/search" class="btn btn-primary">
              去搜索零件
            </router-link>
          </div>
          
          <!-- 无搜索结果 -->
          <div v-else-if="filteredFavorites.length === 0" class="no-results">
            <div class="no-results-icon">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3>没有找到匹配的收藏</h3>
            <p>尝试调整搜索关键词或筛选条件</p>
            <button class="btn btn-outline" @click="clearFilters">
              清除筛选条件
            </button>
          </div>
          
          <!-- 收藏网格 -->
          <div v-else class="favorites-grid">
            <div 
              v-for="favorite in filteredFavorites" 
              :key="favorite.id"
              class="favorite-item"
              :class="{
                'selection-mode': selectionMode,
                'selected': selectedFavorites.includes(favorite.id)
              }"
            >
              <!-- 选择框 -->
              <div v-if="selectionMode" class="selection-checkbox">
                <input 
                  type="checkbox" 
                  :value="favorite.id"
                  :checked="selectedFavorites.includes(favorite.id)"
                  @change="toggleSelection(favorite.id)"
                />
              </div>
              
              <!-- 零件卡片 -->
              <div class="favorite-card">
                <div class="favorite-image">
                  <img 
                    v-if="favorite.image_url" 
                    :src="favorite.image_url" 
                    :alt="favorite.name"
                    class="favorite-img"
                  />
                  <div v-else class="favorite-placeholder">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                  </div>
                </div>
                
                <div class="favorite-content">
                  <div class="favorite-header">
                    <h3 class="favorite-name" @click="goToDetail(favorite.id)">
                      {{ favorite.name }}
                    </h3>
                    <span v-if="favorite.category" class="favorite-category">
                      {{ favorite.category }}
                    </span>
                  </div>
                  
                  <p v-if="favorite.description" class="favorite-description">
                    {{ favorite.description }}
                  </p>
                  
                  <div class="favorite-meta">
                    <span class="favorite-time">
                      {{ formatTime(favorite.addedAt) }}
                    </span>
                  </div>
                </div>
                
                <div class="favorite-actions">
                  <button 
                    class="action-btn compare-btn"
                    @click="addToComparison(favorite)"
                    :class="{ active: isInComparison(favorite.id) }"
                    :title="isInComparison(favorite.id) ? '从对比中移除' : '添加到对比'"
                  >
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </button>
                  
                  <button 
                    class="action-btn remove-btn"
                    @click="removeFavorite(favorite.id)"
                    title="取消收藏"
                  >
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
    
    <!-- 消息提示 -->
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import ThemeToggle from '../components/ThemeToggle.vue'
import { favoritesManager, comparisonManager } from '../utils/api'

export default {
  name: 'Favorites',
  components: {
    ThemeToggle
  },
  setup() {
    const router = useRouter()
    
    // 基础状态
    const favorites = ref([])
    const filteredFavorites = ref([])
    const searchQuery = ref('')
    const selectedCategory = ref('')
    const sortBy = ref('addedAt')
    
    // 选择模式
    const selectionMode = ref(false)
    const selectedFavorites = ref([])
    
    // 消息提示
    const toast = ref({
      show: false,
      type: 'info',
      message: '',
      action: null
    })
    
    // 计算属性
    const uniqueCategories = computed(() => {
      const categories = favorites.value
        .map(f => f.category)
        .filter(Boolean)
      return [...new Set(categories)].sort()
    })
    
    const isAllSelected = computed(() => {
      return filteredFavorites.value.length > 0 && 
             selectedFavorites.value.length === filteredFavorites.value.length
    })
    
    // 加载收藏列表
    const loadFavorites = () => {
      favorites.value = favoritesManager.getFavoritesList()
      filterFavorites()
    }
    
    // 搜索和筛选
    const filterFavorites = () => {
      let filtered = [...favorites.value]
      
      // 按关键词筛选
      if (searchQuery.value.trim()) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(f => 
          f.name.toLowerCase().includes(query) ||
          (f.category && f.category.toLowerCase().includes(query)) ||
          (f.description && f.description.toLowerCase().includes(query))
        )
      }
      
      // 按分类筛选
      if (selectedCategory.value) {
        filtered = filtered.filter(f => f.category === selectedCategory.value)
      }
      
      filteredFavorites.value = filtered
      sortFavorites()
    }
    
    // 排序
    const sortFavorites = () => {
      const sorted = [...filteredFavorites.value]
      
      switch (sortBy.value) {
        case 'name':
          sorted.sort((a, b) => a.name.localeCompare(b.name))
          break
        case 'category':
          sorted.sort((a, b) => (a.category || '').localeCompare(b.category || ''))
          break
        case 'addedAt':
        default:
          sorted.sort((a, b) => new Date(b.addedAt) - new Date(a.addedAt))
          break
      }
      
      filteredFavorites.value = sorted
    }
    
    // 清除搜索和筛选
    const clearSearch = () => {
      searchQuery.value = ''
      filterFavorites()
    }
    
    const clearFilters = () => {
      searchQuery.value = ''
      selectedCategory.value = ''
      filterFavorites()
    }
    
    // 选择模式相关
    const toggleSelectionMode = () => {
      selectionMode.value = !selectionMode.value
      if (!selectionMode.value) {
        selectedFavorites.value = []
      }
    }
    
    const toggleSelection = (favoriteId) => {
      const index = selectedFavorites.value.indexOf(favoriteId)
      if (index > -1) {
        selectedFavorites.value.splice(index, 1)
      } else {
        selectedFavorites.value.push(favoriteId)
      }
    }
    
    const selectAll = () => {
      if (isAllSelected.value) {
        selectedFavorites.value = []
      } else {
        selectedFavorites.value = filteredFavorites.value.map(f => f.id)
      }
    }
    
    // 批量操作
    const batchCompare = () => {
      if (selectedFavorites.value.length < 2) {
        showToast({
          type: 'error',
          message: '至少需要选择2个零件进行对比'
        })
        return
      }
      
      if (selectedFavorites.value.length > 6) {
        showToast({
          type: 'error',
          message: '最多只能同时对比6个零件'
        })
        return
      }
      
      const ids = selectedFavorites.value.join(',')
      router.push(`/compare?ids=${ids}`)
    }
    
    const batchDelete = async () => {
      if (selectedFavorites.value.length === 0) return
      
      const confirmDelete = confirm(`确定要删除选中的 ${selectedFavorites.value.length} 个收藏吗？`)
      if (!confirmDelete) return
      
      let successCount = 0
      selectedFavorites.value.forEach(favoriteId => {
        const result = favoritesManager.removeFromFavorites(favoriteId)
        if (result.success) {
          successCount++
        }
      })
      
      if (successCount > 0) {
        showToast({
          type: 'success',
          message: `成功删除 ${successCount} 个收藏`
        })
        
        selectedFavorites.value = []
        selectionMode.value = false
        loadFavorites()
      }
    }
    
    // 单个操作
    const goToDetail = (partId) => {
      router.push(`/part/${partId}`)
    }
    
    const addToComparison = (favorite) => {
      const result = comparisonManager.toggleComparison ? 
        comparisonManager.toggleComparison(favorite) :
        (comparisonManager.isInComparison(favorite.id) ? 
          comparisonManager.removeFromComparison(favorite.id) :
          comparisonManager.addToComparison(favorite))
      
      if (result.success) {
        showToast({
          type: 'success',
          message: result.message
        })
      } else {
        showToast({
          type: 'error',
          message: result.message
        })
      }
    }
    
    const isInComparison = (favoriteId) => {
      return comparisonManager.isInComparison(favoriteId)
    }
    
    const removeFavorite = (favoriteId) => {
      const result = favoritesManager.removeFromFavorites(favoriteId)
      if (result.success) {
        showToast({
          type: 'success',
          message: '已取消收藏'
        })
        loadFavorites()
      } else {
        showToast({
          type: 'error',
          message: result.message
        })
      }
    }
    
    // 导入导出
    const exportFavorites = () => {
      const result = favoritesManager.exportFavorites()
      if (result.success) {
        showToast({
          type: 'success',
          message: result.message
        })
      }
    }
    
    const importFavorites = async (event) => {
      const file = event.target.files[0]
      if (!file) return
      
      const result = await favoritesManager.importFavorites(file)
      
      if (result.success) {
        showToast({
          type: 'success',
          message: result.message
        })
        loadFavorites()
      } else {
        showToast({
          type: 'error',
          message: result.message
        })
      }
      
      // 清除文件输入
      event.target.value = ''
    }
    
    // 工具函数
    const formatTime = (timestamp) => {
      if (!timestamp) return ''
      
      const date = new Date(timestamp)
      const now = new Date()
      const diffMs = now - date
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
      
      if (diffDays === 0) return '今天收藏'
      if (diffDays === 1) return '昨天收藏'
      if (diffDays < 7) return `${diffDays}天前收藏`
      if (diffDays < 30) return `${Math.floor(diffDays / 7)}周前收藏`
      
      return date.toLocaleDateString('zh-CN')
    }
    
    // 消息提示
    const showToast = (options) => {
      toast.value = {
        show: true,
        type: options.type || 'info',
        message: options.message,
        action: options.action || null
      }
      
      if (!options.action) {
        setTimeout(() => {
          hideToast()
        }, 3000)
      }
    }
    
    const hideToast = () => {
      toast.value.show = false
    }
    
    // 监听存储变化
    const handleStorageChange = (e) => {
      if (e.key === 'openpart_favorites') {
        loadFavorites()
      }
    }
    
    onMounted(() => {
      loadFavorites()
      window.addEventListener('storage', handleStorageChange)
    })
    
    onUnmounted(() => {
      window.removeEventListener('storage', handleStorageChange)
    })
    
    return {
      favorites,
      filteredFavorites,
      searchQuery,
      selectedCategory,
      sortBy,
      selectionMode,
      selectedFavorites,
      toast,
      uniqueCategories,
      isAllSelected,
      filterFavorites,
      sortFavorites,
      clearSearch,
      clearFilters,
      toggleSelectionMode,
      toggleSelection,
      selectAll,
      batchCompare,
      batchDelete,
      goToDetail,
      addToComparison,
      isInComparison,
      removeFavorite,
      exportFavorites,
      importFavorites,
      formatTime,
      showToast,
      hideToast
    }
  }
}
</script>

/* Favorites.vue 样式完整版 */
<style scoped>
.favorites-page {
  min-height: 100vh;
  background: var(--bg-primary);
}

/* 头部导航 */
.favorites-header {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  padding: 16px 0;
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(8px);
}

.favorites-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-link {
  text-decoration: none;
  flex-shrink: 0;
}

.logo {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary);
  margin: 0;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

/* 主要内容 */
.favorites-main {
  padding: 24px 0;
}

/* 收藏概览 */
.favorites-summary {
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

.import-btn {
  position: relative;
  cursor: pointer;
}

/* 操作栏 */
.favorites-controls {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 搜索框 */
.search-section {
  flex: 1;
}

.search-input-container {
  position: relative;
  display: flex;
  align-items: center;
  max-width: 400px;
}

.search-input {
  width: 100%;
  padding: 12px 40px 12px 40px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary);
  background: var(--bg-card);
}

.search-icon {
  position: absolute;
  left: 12px;
  width: 16px;
  height: 16px;
  color: var(--text-muted);
  pointer-events: none;
}

.clear-button {
  position: absolute;
  right: 12px;
  width: 16px;
  height: 16px;
  border: none;
  background: none;
  color: var(--text-muted);
  cursor: pointer;
}

/* 筛选区域 */
.filter-section {
  display: flex;
  gap: 12px;
  align-items: center;
}

.category-select,
.sort-select {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 14px;
}

/* 批量操作 */
.batch-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.selection-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.selection-toggle:hover {
  background: var(--bg-primary);
  border-color: var(--primary);
}

.selection-toggle.active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.selection-icon {
  width: 16px;
  height: 16px;
}

.batch-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  animation: slideInRight 0.3s ease;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.btn-sm {
  padding: 6px 12px;
  font-size: 13px;
}

.btn-danger {
  background: #f43f5e;
  color: white;
  border: 1px solid #f43f5e;
}

.btn-danger:hover {
  background: #e11d48;
  border-color: #e11d48;
}

.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 收藏内容区域 */
.favorites-content {
  min-height: 400px;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-icon {
  width: 80px;
  height: 80px;
  color: var(--text-muted);
  margin-bottom: 24px;
}

.empty-state h3 {
  font-size: 24px;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.empty-state p {
  color: var(--text-secondary);
  margin: 0 0 32px 0;
  max-width: 400px;
  line-height: 1.6;
}

/* 无结果状态 */
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

/* 收藏网格 */
.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.favorite-item {
  position: relative;
  transition: all 0.2s ease;
}

.favorite-item.selection-mode {
  padding: 8px;
  border: 2px solid transparent;
  border-radius: 16px;
  background: var(--bg-secondary);
}

.favorite-item.selection-mode.selected {
  border-color: var(--primary);
  background: color-mix(in srgb, var(--primary) 10%, var(--bg-secondary));
}

.selection-checkbox {
  position: absolute;
  top: 4px;
  left: 4px;
  width: 24px;
  height: 24px;
  background: var(--bg-card);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  box-shadow: var(--shadow-sm);
}

.selection-checkbox input[type="checkbox"] {
  width: 16px;
  height: 16px;
  margin: 0;
  cursor: pointer;
  accent-color: var(--primary);
}

/* 收藏卡片 */
.favorite-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.favorite-item.selection-mode .favorite-card {
  margin: 8px;
  border-radius: 8px;
}

.favorite-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--primary);
}

.favorite-image {
  width: 100%;
  height: 160px;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.favorite-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: white;
  transition: transform 0.3s ease;
}

.favorite-card:hover .favorite-img {
  transform: scale(1.02);
}

.favorite-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: var(--text-muted);
}

.favorite-placeholder svg {
  width: 48px;
  height: 48px;
}

.favorite-content {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.favorite-header {
  margin-bottom: 8px;
}

.favorite-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
  cursor: pointer;
  transition: color 0.2s ease;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.favorite-name:hover {
  color: var(--primary);
}

.favorite-category {
  display: inline-block;
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 500;
  color: var(--primary);
  background: color-mix(in srgb, var(--primary) 10%, transparent);
  border-radius: 4px;
}

.favorite-description {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 12px 0;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.favorite-meta {
  margin-top: auto;
  padding-top: 8px;
  border-top: 1px solid var(--border-color);
}

.favorite-time {
  font-size: 12px;
  color: var(--text-muted);
}

/* 收藏操作按钮 */
.favorite-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 4px;
  opacity: 0;
  transform: translateY(-4px);
  transition: all 0.3s ease;
}

.favorite-card:hover .favorite-actions {
  opacity: 1;
  transform: translateY(0);
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.9);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  backdrop-filter: blur(8px);
}

[data-theme="dark"] .action-btn {
  background: rgba(15, 23, 42, 0.9);
}

.action-btn:hover {
  transform: scale(1.1);
}

.compare-btn:hover,
.compare-btn.active {
  background: var(--primary);
  color: white;
}

.remove-btn:hover {
  background: #f43f5e;
  color: white;
}

.action-btn svg {
  width: 16px;
  height: 16px;
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

/* 响应式设计 */
@media (max-width: 1024px) {
  .favorites-summary {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .summary-stats {
    justify-content: center;
  }
  
  .favorites-controls {
    gap: 12px;
  }
  
  .batch-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .batch-actions {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .favorites-nav {
    flex-wrap: wrap;
    gap: 12px;
  }
  
  .page-title {
    font-size: 20px;
  }
  
  .favorites-main {
    padding: 16px 0;
  }
  
  .favorites-summary {
    padding: 16px;
    margin-bottom: 16px;
  }
  
  .summary-stats {
    gap: 20px;
  }
  
  .stat-number {
    font-size: 24px;
  }
  
  .favorites-controls {
    padding: 16px;
  }
  
  .filter-section {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .favorites-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
  }
  
  .favorite-actions {
    opacity: 1;
    transform: translateY(0);
  }
  
  .toast-overlay {
    left: 16px;
    right: 16px;
    transform: none;
  }
  
  .toast-message {
    min-width: auto;
    max-width: none;
  }
}

@media (max-width: 480px) {
  .favorites-grid {
    grid-template-columns: 1fr;
  }
  
  .summary-stats {
    flex-direction: column;
    gap: 16px;
  }
}

/* 动画增强 */
.favorite-item {
  animation: fadeInUp 0.3s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.favorite-item.selection-mode {
  animation: selectionModeEnter 0.2s ease;
}

@keyframes selectionModeEnter {
  from {
    transform: scale(0.98);
    opacity: 0.8;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}
</style>