<template>
  <div class="search-box">
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
    
    <!-- 搜索建议 -->
    <div 
      v-if="showSuggestions && suggestions.length > 0" 
      class="suggestions-dropdown"
    >
      <div 
        v-for="suggestion in suggestions" 
        :key="suggestion"
        class="suggestion-item"
        @mousedown="selectSuggestion(suggestion)"
      >
        <svg class="suggestion-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        {{ suggestion }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { partsAPI, debounce } from '../utils/api'

export default {
  name: 'SearchBox',
  props: {
    placeholder: {
      type: String,
      default: '搜索零件、型号、参数...'
    },
    size: {
      type: String,
      default: 'normal', // 'large' | 'normal'
      validator: value => ['large', 'normal'].includes(value)
    },
    autoFocus: {
      type: Boolean,
      default: false
    }
  },
  emits: ['search'],
  setup(props, { emit }) {
    const router = useRouter()
    const searchInput = ref(null)
    const searchQuery = ref('')
    const suggestions = ref([])
    const showSuggestions = ref(false)
    
    // 防抖获取建议
    const debouncedGetSuggestions = debounce(async (query) => {
      if (!query.trim()) {
        suggestions.value = []
        return
      }
      
      try {
        const response = await partsAPI.getSuggestions(query)
        suggestions.value = response.data
      } catch (error) {
        console.error('获取搜索建议失败:', error)
        suggestions.value = []
      }
    }, 300)
    
    const onInput = () => {
      debouncedGetSuggestions(searchQuery.value)
    }
    
    const onSearch = () => {
      if (!searchQuery.value.trim()) return
      
      showSuggestions.value = false
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
    
    // 自动聚焦
    if (props.autoFocus) {
      nextTick(() => {
        searchInput.value?.focus()
      })
    }
    
    return {
      searchInput,
      searchQuery,
      suggestions,
      showSuggestions,
      onInput,
      onSearch,
      selectSuggestion,
      onBlur,
      clearSearch
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
  z-index: 10;
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
</style>