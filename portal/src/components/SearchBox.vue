<template>
  <div class="search-box">
    
    <!-- 搜索建议 -->
    <div class="search-box" :class="{ large: size === 'large' }">
    <div class="search-input-container">
      <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      
      <input
        ref="searchInput"
        v-model="searchQuery"
        type="text"
        class="search-input"
        :placeholder="placeholder"
        @input="onInput"
        @keyup.enter="onSearch"
        @focus="showSuggestions = true"
        @blur="onBlur"
      />
      
      <button 
        v-if="searchQuery" 
        @click="clearSearch"
        class="clear-button"
        type="button"
      >
        <svg class="clear-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
    
    <!-- 搜索提示 -->
    <div v-if="searchQuery && showSearchTips" class="search-tips">
      <div class="search-tip">
        <svg class="tip-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ searchTip }}</span>
      </div>
    </div>
    
    <!-- 搜索建议 -->
    <div 
      v-if="showSuggestions && (suggestions.length > 0 || isLoading)" 
      class="suggestions-dropdown"
    >
      <div v-if="isLoading" class="suggestion-loading">
        <div class="loading-spinner"></div>
        <span>搜索中...</span>
      </div>
      
      <div 
        v-for="suggestion in suggestions" 
        :key="suggestion"
        class="suggestion-item"
        @mousedown="selectSuggestion(suggestion)"
      >
        <svg class="suggestion-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <span class="suggestion-text">{{ suggestion }}</span>
        <span v-if="suggestion.includes(' ')" class="suggestion-badge">多词</span>
      </div>
      
      <!-- 搜索历史 -->
      <div v-if="searchHistory.length > 0 && !searchQuery" class="search-history">
        <div class="history-header">最近搜索</div>
        <div 
          v-for="(historyItem, index) in searchHistory.slice(0, 5)" 
          :key="index"
          class="suggestion-item history-item"
          @mousedown="selectSuggestion(historyItem)"
        >
          <svg class="suggestion-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="suggestion-text">{{ historyItem }}</span>
          <button 
            @click.stop="removeFromHistory(index)"
            class="remove-history"
          >
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
  </div>
</template>

<script>
import { ref, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { partsAPI, debounce } from '../utils/api'
import { siteConfig } from '../config/site'

export default {
  name: 'SearchBox',
  props: {
    placeholder: {
      type: String,
      default: siteConfig.search.placeholder
    },
    size: {
      type: String,
      default: 'normal',
      validator: value => ['large', 'normal'].includes(value)
    },
    autoFocus: {
      type: Boolean,
      default: false
    },
    showSearchTips: {
      type: Boolean,
      default: true
    }
  },
  emits: ['search'],
  setup(props, { emit }) {
    const router = useRouter()
    const searchInput = ref(null)
    const searchQuery = ref('')
    const suggestions = ref([])
    const showSuggestions = ref(false)
    const isLoading = ref(false)
    const searchHistory = ref([])
    
    // 加载搜索历史
    const loadSearchHistory = () => {
      const history = JSON.parse(localStorage.getItem('searchHistory') || '[]')
      searchHistory.value = history
    }
    
    // 保存搜索历史
    const saveToHistory = (query) => {
      if (!query.trim()) return
      
      let history = JSON.parse(localStorage.getItem('searchHistory') || '[]')
      
      // 移除重复项
      history = history.filter(item => item !== query)
      
      // 添加到开头
      history.unshift(query)
      
      // 限制历史记录数量
      history = history.slice(0, 10)
      
      localStorage.setItem('searchHistory', JSON.stringify(history))
      searchHistory.value = history
    }
    
    // 从历史记录中删除
    const removeFromHistory = (index) => {
      searchHistory.value.splice(index, 1)
      localStorage.setItem('searchHistory', JSON.stringify(searchHistory.value))
    }
    
    // 防抖获取建议
    const debouncedGetSuggestions = debounce(async (query) => {
      if (!query.trim()) {
        suggestions.value = []
        isLoading.value = false
        return
      }
      
      isLoading.value = true
      
      try {
        const response = await partsAPI.getSuggestions(query)
        suggestions.value = response.data
      } catch (error) {
        console.error('获取搜索建议失败:', error)
        suggestions.value = []
      }
      
      isLoading.value = false
    }, 300)
    
    const onInput = () => {
      debouncedGetSuggestions(searchQuery.value)
    }
    
    const onSearch = () => {
      if (!searchQuery.value.trim()) return
      
      showSuggestions.value = false
      
      // 保存到搜索历史
      saveToHistory(searchQuery.value)
      
      emit('search', searchQuery.value)
      
      // 导航到搜索页面
      router.push({
        name: 'Search',
        query: { q: searchQuery.value }
      })
    }
    
    const selectSuggestion = (suggestion) => {
      searchQuery.value = suggestion
      nextTick(() => {
        onSearch()
      })
    }
    
    const onBlur = () => {
      // 延迟隐藏建议，以便点击建议项
      setTimeout(() => {
        showSuggestions.value = false
      }, 200)
    }
    
    const clearSearch = () => {
      searchQuery.value = ''
      suggestions.value = []
      searchInput.value?.focus()
    }
    
    onMounted(() => {
      loadSearchHistory()
      
      if (props.autoFocus) {
        nextTick(() => {
          searchInput.value?.focus()
        })
      }
    })
    
    return {
      searchInput,
      searchQuery,
      suggestions,
      showSuggestions,
      isLoading,
      searchHistory,
      onInput,
      onSearch,
      selectSuggestion,
      onBlur,
      clearSearch,
      removeFromHistory,
      searchTip: siteConfig.search.searchTip,
      showSearchTips: siteConfig.search.showSearchTips
    }
  }
}
</script>

<style scoped>
.search-box {
  position: relative;
  width: 100%;
}

.search-input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input {
  width: 100%;
  padding: 16px 50px 16px 50px;
  border: 2px solid var(--border-color);
  border-radius: 12px;
  font-size: 16px;
  background: var(--bg-card);
  color: var(--text-primary);
  transition: all 0.3s ease;
  box-shadow: var(--shadow-sm);
}

.search-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--primary) 10%, transparent);
  transform: translateY(-1px);
}

.search-input::placeholder {
  color: var(--text-muted);
}

.search-icon {
  position: absolute;
  left: 16px;
  width: 20px;
  height: 20px;
  color: var(--text-muted);
  pointer-events: none;
  z-index: 1;
}

.clear-button {
  position: absolute;
  right: 16px;
  width: 20px;
  height: 20px;
  border: none;
  background: none;
  color: var(--text-muted);
  cursor: pointer;
  transition: color 0.2s ease;
  z-index: 1;
}

.clear-button:hover {
  color: var(--text-primary);
}

.clear-icon {
  width: 16px;
  height: 16px;
}

.suggestions-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: var(--shadow-lg);
  z-index: 9999; /* 增加z-index值 */
  margin-top: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.suggestion-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  gap: 12px;
}

.suggestion-item:hover {
  background: var(--bg-secondary);
}

.suggestion-item:first-child {
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

.suggestion-item:last-child {
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
}

.suggestion-icon {
  width: 16px;
  height: 16px;
  color: var(--text-muted);
  flex-shrink: 0;
}

/* 大尺寸样式 */
.search-box.large .search-input {
  padding: 20px 60px 20px 60px;
  font-size: 18px;
  border-radius: 16px;
}

.search-box.large .search-icon {
  left: 20px;
  width: 24px;
  height: 24px;
}

.search-box.large .clear-button {
  right: 20px;
  width: 24px;
  height: 24px;
}

.search-tips {
  margin-top: 8px;
}

.search-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: color-mix(in srgb, var(--secondary) 10%, transparent);
  border: 1px solid color-mix(in srgb, var(--secondary) 20%, transparent);
  border-radius: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.tip-icon {
  width: 16px;
  height: 16px;
  color: var(--secondary);
  flex-shrink: 0;
}

/* 建议下拉框增强 */
.suggestion-loading {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  color: var(--text-muted);
  font-size: 14px;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--border-color);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.suggestion-text {
  flex: 1;
}

.suggestion-badge {
  font-size: 10px;
  padding: 2px 6px;
  background: var(--accent);
  color: white;
  border-radius: 10px;
  font-weight: 500;
}

/* 搜索历史 */
.search-history {
  border-top: 1px solid var(--border-color);
  margin-top: 4px;
  padding-top: 4px;
}

.history-header {
  padding: 8px 16px 4px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.history-item {
  position: relative;
}

.remove-history {
  width: 16px;
  height: 16px;
  border: none;
  background: none;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.2s ease;
}

.history-item:hover .remove-history {
  opacity: 1;
}

.remove-history:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.remove-history svg {
  width: 12px;
  height: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-input {
    padding: 14px 45px 14px 45px;
    font-size: 15px;
  }
  
  .search-icon {
    left: 14px;
    width: 18px;
    height: 18px;
  }
  
  .clear-button {
    right: 14px;
    width: 18px;
    height: 18px;
  }
}

@media (max-width: 768px) {
  .search-tips {
    margin-top: 6px;
  }
  
  .search-tip {
    padding: 6px 10px;
    font-size: 12px;
  }
  
  .tip-icon {
    width: 14px;
    height: 14px;
  }
  
  .suggestion-loading {
    padding: 10px 14px;
    font-size: 13px;
  }
  
  .loading-spinner {
    width: 14px;
    height: 14px;
  }
  
  .remove-history {
    opacity: 1; /* 移动端始终显示删除按钮 */
  }
}
</style>