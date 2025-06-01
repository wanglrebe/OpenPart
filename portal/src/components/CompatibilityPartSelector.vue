<!-- src/components/CompatibilityPartSelector.vue -->
<template>
  <div class="compatibility-part-selector" :class="{ compact: compactMode }">
    <!-- 已选择的零件列表 -->
    <div v-if="selectedParts.length > 0" class="selected-parts-section">
      <div class="section-header">
        <h3 class="section-title">已选择零件 ({{ selectedParts.length }}/{{ maxParts }})</h3>
        <button 
          v-if="selectedParts.length > 0"
          @click="clearAllParts"
          class="clear-all-btn"
          title="清空所有零件"
        >
          <svg class="clear-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          清空
        </button>
      </div>
      
      <div class="selected-parts-grid">
        <div 
          v-for="(part, index) in selectedParts" 
          :key="part.id"
          class="selected-part-card"
          :draggable="!compactMode"
          @dragstart="handleDragStart(index, $event)"
          @dragover.prevent
          @drop="handleDrop(index, $event)"
        >
          <div class="part-info">
            <div class="part-image">
              <img 
                v-if="part.image_url" 
                :src="part.image_url" 
                :alt="part.name"
                @error="handleImageError"
              />
              <div v-else class="part-placeholder">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
            </div>
            
            <div class="part-details">
              <h4 class="part-name">{{ part.name }}</h4>
              <p class="part-category">{{ part.category || '未分类' }}</p>
              <p v-if="!compactMode && part.description" class="part-description">
                {{ truncateText(part.description, 60) }}
              </p>
            </div>
          </div>
          
          <div class="part-actions">
            <div v-if="!compactMode" class="drag-handle" title="拖拽排序">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </div>
            <button 
              @click="removePart(part.id)"
              class="remove-btn"
              title="移除零件"
            >
              <svg class="remove-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 零件搜索和添加区域 -->
    <div class="part-search-section">
      <div class="section-header">
        <h3 class="section-title">
          {{ selectedParts.length === 0 ? '选择零件进行兼容性检查' : '添加更多零件' }}
        </h3>
        <div class="parts-counter">
          <span class="counter-text">{{ selectedParts.length }}/{{ maxParts }}</span>
          <div class="counter-bar">
            <div 
              class="counter-fill" 
              :style="{ width: `${(selectedParts.length / maxParts) * 100}%` }"
            ></div>
          </div>
        </div>
      </div>
      
      <!-- 搜索框 -->
      <div class="search-box">
        <div class="search-input-wrapper">
          <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            v-model="searchQuery"
            @input="debouncedSearch"
            type="text"
            class="search-input"
            placeholder="搜索零件名称、型号或分类..."
            :disabled="selectedParts.length >= maxParts"
          />
          <button 
            v-if="searchQuery"
            @click="clearSearch"
            class="clear-search-btn"
          >
            <svg class="clear-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
      
      <!-- 分类筛选 -->
      <div v-if="!compactMode && availableCategories.length > 0" class="category-filter">
        <button
          v-for="category in availableCategories.slice(0, 6)"
          :key="category"
          @click="filterByCategory(category)"
          class="category-btn"
          :class="{ active: selectedCategory === category }"
        >
          {{ category }}
        </button>
        <button 
          v-if="selectedCategory"
          @click="clearCategoryFilter"
          class="category-btn clear"
        >
          清除筛选
        </button>
      </div>
      
      <!-- 搜索结果 -->
      <div class="search-results">
        <!-- 加载状态 -->
        <div v-if="searching" class="loading-state">
          <div class="loading-spinner"></div>
          <p>搜索中...</p>
        </div>
        
        <!-- 无结果 -->
        <div v-else-if="searchQuery && searchResults.length === 0" class="no-results">
          <div class="no-results-icon">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <p>未找到相关零件</p>
          <button @click="clearSearch" class="btn btn-sm btn-outline">清除搜索</button>
        </div>
        
        <!-- 数量限制提示 -->
        <div v-else-if="selectedParts.length >= maxParts" class="limit-notice">
          <div class="notice-icon">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p>已达到最大零件数量限制 ({{ maxParts }}个)</p>
          <p class="notice-hint">请移除部分零件后再添加新的</p>
        </div>
        
        <!-- 搜索结果列表 -->
        <div v-else-if="searchResults.length > 0" class="results-grid">
          <div 
            v-for="part in filteredResults" 
            :key="part.id"
            class="result-card"
            :class="{ disabled: isPartSelected(part.id) }"
          >
            <div class="result-info">
              <div class="result-image">
                <img 
                  v-if="part.image_url" 
                  :src="part.image_url" 
                  :alt="part.name"
                  @error="handleImageError"
                />
                <div v-else class="result-placeholder">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </div>
              </div>
              
              <div class="result-details">
                <h4 class="result-name">{{ part.name }}</h4>
                <p class="result-category">{{ part.category || '未分类' }}</p>
                <p v-if="!compactMode && part.description" class="result-description">
                  {{ truncateText(part.description, 80) }}
                </p>
              </div>
            </div>
            
            <div class="result-actions">
              <button 
                v-if="isPartSelected(part.id)"
                disabled
                class="add-btn added"
              >
                <svg class="check-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                已添加
              </button>
              <button 
                v-else
                @click="addPart(part)"
                class="add-btn"
                :disabled="selectedParts.length >= maxParts"
              >
                <svg class="add-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                添加
              </button>
            </div>
          </div>
        </div>
        
        <!-- 默认提示 -->
        <div v-else-if="!searchQuery" class="search-prompt">
          <div class="prompt-icon">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <p>输入关键词搜索零件</p>
          <p class="prompt-hint">支持搜索零件名称、型号、分类等</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { partsAPI, debounce } from '../utils/api'

export default {
  name: 'CompatibilityPartSelector',
  props: {
    modelValue: {
      type: Array,
      default: () => []
    },
    maxParts: {
      type: Number,
      default: 10
    },
    compactMode: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'part-added', 'part-removed'],
  setup(props, { emit }) {
    // 响应式数据
    const searchQuery = ref('')
    const searchResults = ref([])
    const availableCategories = ref([])
    const selectedCategory = ref('')
    const searching = ref(false)
    const draggedIndex = ref(null)

    // 计算属性
    const selectedParts = computed({
      get: () => props.modelValue,
      set: (value) => emit('update:modelValue', value)
    })

    const filteredResults = computed(() => {
      if (!selectedCategory.value) return searchResults.value
      return searchResults.value.filter(part => part.category === selectedCategory.value)
    })

    // 工具函数
    const truncateText = (text, maxLength) => {
      if (!text || text.length <= maxLength) return text
      return text.substring(0, maxLength) + '...'
    }

    const handleImageError = (event) => {
      event.target.style.display = 'none'
    }

    const isPartSelected = (partId) => {
      return selectedParts.value.some(part => part.id === partId)
    }

    // 搜索相关方法
    const searchParts = async () => {
      if (!searchQuery.value.trim()) {
        searchResults.value = []
        return
      }

      searching.value = true
      try {
        const response = await partsAPI.search({
          q: searchQuery.value,
          limit: 50
        })
        searchResults.value = response.data
        
        // 提取分类
        const categories = new Set(response.data.map(p => p.category).filter(Boolean))
        availableCategories.value = Array.from(categories)
        
      } catch (error) {
        console.error('搜索零件失败:', error)
        searchResults.value = []
      }
      searching.value = false
    }

    const debouncedSearch = debounce(searchParts, 300)

    const clearSearch = () => {
      searchQuery.value = ''
      searchResults.value = []
      selectedCategory.value = ''
    }

    const filterByCategory = (category) => {
      selectedCategory.value = selectedCategory.value === category ? '' : category
    }

    const clearCategoryFilter = () => {
      selectedCategory.value = ''
    }

    // 零件管理方法
    const addPart = (part) => {
      if (selectedParts.value.length >= props.maxParts) {
        return
      }

      if (isPartSelected(part.id)) {
        return
      }

      const newParts = [...selectedParts.value, part]
      selectedParts.value = newParts
      emit('part-added', part)
    }

    const removePart = (partId) => {
      const newParts = selectedParts.value.filter(part => part.id !== partId)
      const removedPart = selectedParts.value.find(part => part.id === partId)
      selectedParts.value = newParts
      if (removedPart) {
        emit('part-removed', removedPart)
      }
    }

    const clearAllParts = () => {
      const oldParts = [...selectedParts.value]
      selectedParts.value = []
      oldParts.forEach(part => emit('part-removed', part))
    }

    // 拖拽排序方法
    const handleDragStart = (index, event) => {
      draggedIndex.value = index
      event.dataTransfer.effectAllowed = 'move'
    }

    const handleDrop = (dropIndex, event) => {
      event.preventDefault()
      
      if (draggedIndex.value === null || draggedIndex.value === dropIndex) {
        return
      }

      const newParts = [...selectedParts.value]
      const draggedItem = newParts.splice(draggedIndex.value, 1)[0]
      newParts.splice(dropIndex, 0, draggedItem)
      
      selectedParts.value = newParts
      draggedIndex.value = null
    }

    // 初始化
    onMounted(() => {
      // 如果有预选零件，可以在这里处理
    })

    return {
      // 数据
      searchQuery,
      searchResults,
      availableCategories,
      selectedCategory,
      searching,
      selectedParts,
      filteredResults,
      
      // 方法
      truncateText,
      handleImageError,
      isPartSelected,
      debouncedSearch,
      clearSearch,
      filterByCategory,
      clearCategoryFilter,
      addPart,
      removePart,
      clearAllParts,
      handleDragStart,
      handleDrop
    }
  }
}
</script>

<style scoped>
.compatibility-part-selector {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.compatibility-part-selector.compact {
  gap: 16px;
}

/* 区域标题 */
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.compact .section-title {
  font-size: 16px;
}

.clear-all-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  font-size: 13px;
  color: var(--text-muted);
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-all-btn:hover {
  color: #f43f5e;
  border-color: #f43f5e;
  background: color-mix(in srgb, #f43f5e 5%, transparent);
}

.clear-icon {
  width: 14px;
  height: 14px;
}

/* 已选择零件区域 */
.selected-parts-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
}

.compact .selected-parts-section {
  padding: 16px;
}

.selected-parts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.compact .selected-parts-grid {
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
}

.selected-part-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: grab;
  transition: all 0.2s ease;
}

.selected-part-card:active {
  cursor: grabbing;
}

.selected-part-card:hover {
  border-color: var(--primary);
  box-shadow: var(--shadow-sm);
}

.part-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.part-image,
.result-image {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  overflow: hidden;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.compact .part-image,
.compact .result-image {
  width: 40px;
  height: 40px;
}

.part-image img,
.result-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.part-placeholder,
.result-placeholder {
  color: var(--text-muted);
}

.part-placeholder svg,
.result-placeholder svg {
  width: 24px;
  height: 24px;
}

.part-details,
.result-details {
  flex: 1;
  min-width: 0;
}

.part-name,
.result-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin: 0 0 4px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.part-category,
.result-category {
  font-size: 12px;
  color: var(--text-muted);
  margin: 0 0 4px 0;
}

.part-description,
.result-description {
  font-size: 11px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.3;
}

.part-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.drag-handle {
  width: 20px;
  height: 20px;
  color: var(--text-muted);
  cursor: grab;
}

.drag-handle svg {
  width: 100%;
  height: 100%;
}

.remove-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.remove-btn:hover {
  color: #f43f5e;
  background: color-mix(in srgb, #f43f5e 10%, transparent);
}

.remove-icon {
  width: 14px;
  height: 14px;
}

/* 计数器 */
.parts-counter {
  display: flex;
  align-items: center;
  gap: 8px;
}

.counter-text {
  font-size: 13px;
  color: var(--text-muted);
  font-weight: 500;
}

.counter-bar {
  width: 60px;
  height: 4px;
  background: var(--bg-secondary);
  border-radius: 2px;
  overflow: hidden;
}

.counter-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--secondary));
  transition: width 0.3s ease;
}

/* 搜索区域 */
.part-search-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
}

.compact .part-search-section {
  padding: 16px;
}

.search-box {
  margin-bottom: 16px;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 12px;
  width: 16px;
  height: 16px;
  color: var(--text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 12px 40px 12px 40px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--primary) 10%, transparent);
}

.search-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.clear-search-btn {
  position: absolute;
  right: 8px;
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.clear-search-btn:hover {
  color: var(--text-primary);
  background: var(--bg-secondary);
}

/* 分类筛选 */
.category-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.category-btn {
  padding: 6px 12px;
  font-size: 13px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.category-btn:hover {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.category-btn.active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.category-btn.clear {
  background: transparent;
  color: var(--text-muted);
}

.category-btn.clear:hover {
  color: #f43f5e;
  border-color: #f43f5e;
  background: color-mix(in srgb, #f43f5e 5%, transparent);
}

/* 搜索结果 */
.search-results {
  min-height: 200px;
}

.loading-state,
.no-results,
.search-prompt,
.limit-notice {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.compact .loading-state,
.compact .no-results,
.compact .search-prompt,
.compact .limit-notice {
  padding: 30px 15px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.no-results-icon,
.prompt-icon,
.notice-icon {
  width: 48px;
  height: 48px;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.no-results p,
.search-prompt p,
.limit-notice p {
  color: var(--text-secondary);
  margin: 0 0 8px 0;
}

.prompt-hint,
.notice-hint {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 12px;
}

.compact .results-grid {
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 8px;
}

.result-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.2s ease;
}

.result-card:hover:not(.disabled) {
  border-color: var(--primary);
  box-shadow: var(--shadow-sm);
}

.result-card.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.result-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.result-actions {
  flex-shrink: 0;
}

.add-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  font-size: 13px;
  border: 1px solid var(--primary);
  border-radius: 6px;
  background: transparent;
  color: var(--primary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.add-btn:hover:not(:disabled) {
  background: var(--primary);
  color: white;
}

.add-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.add-btn.added {
  background: #10b981;
  border-color: #10b981;
  color: white;
}

.add-icon,
.check-icon {
  width: 14px;
  height: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .selected-parts-grid {
    grid-template-columns: 1fr;
  }
  
  .results-grid {
    grid-template-columns: 1fr;
  }
  
  .category-filter {
    gap: 6px;
  }
  
  .category-btn {
    padding: 4px 8px;
    font-size: 12px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .parts-counter {
    align-self: flex-end;
  }
}

@media (max-width: 480px) {
  .compatibility-part-selector {
    gap: 16px;
  }
  
  .selected-parts-section,
  .part-search-section {
    padding: 16px;
  }
  
  .selected-part-card,
  .result-card {
    padding: 10px;
    gap: 10px;
  }
  
  .part-image,
  .result-image {
    width: 36px;
    height: 36px;
  }
  
  .part-name,
  .result-name {
    font-size: 13px;
  }
  
  .part-category,
  .result-category {
    font-size: 11px;
  }
}
</style>