<!-- portal/src/components/PartSelector.vue (新组件) -->
<template>
  <div class="part-selector-overlay" @click="closeModal">
    <div class="part-selector-modal" @click.stop>
      <div class="modal-header">
        <h3>选择零件</h3>
        <div class="header-info">
          <span class="category-name">{{ targetCategory }}</span>
          <span class="requirement-badge" :class="{ required: isRequired }">
            {{ isRequired ? '必需' : '可选' }}
          </span>
        </div>
        <button class="close-btn" @click="closeModal">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="modal-content">
        <!-- 搜索和筛选 -->
        <div class="search-section">
          <div class="search-input-container">
            <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              class="search-input"
              :placeholder="`搜索${targetCategory}...`"
              @input="searchParts"
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

          <div class="filter-section">
            <select 
              v-model="selectedCategory" 
              @change="filterParts"
              class="category-filter"
            >
              <option value="">所有分类</option>
              <option 
                v-for="category in availableCategories" 
                :key="category"
                :value="category"
              >
                {{ category }}
              </option>
            </select>

            <div class="suggestions" v-if="suggestions.length > 0">
              <span class="suggestions-label">建议:</span>
              <button 
                v-for="suggestion in suggestions"
                :key="suggestion"
                class="suggestion-tag"
                @click="applySuggestion(suggestion)"
              >
                {{ suggestion }}
              </button>
            </div>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>搜索零件中...</p>
        </div>

        <!-- 零件列表 -->
        <div v-else-if="filteredParts.length > 0" class="parts-list">
          <div 
            v-for="part in filteredParts" 
            :key="part.id"
            class="part-option"
            :class="{ selected: selectedPart?.id === part.id }"
            @click="selectPart(part)"
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
              <h4 class="part-name">{{ part.name }}</h4>
              <span v-if="part.category" class="part-category">{{ part.category }}</span>
              <p v-if="part.description" class="part-description">
                {{ part.description }}
              </p>

              <!-- 关键参数展示 -->
              <div v-if="part.properties" class="key-specs">
                <div 
                  v-for="[key, value] in getKeySpecs(part.properties)" 
                  :key="key"
                  class="spec-item"
                >
                  <span class="spec-key">{{ key }}:</span>
                  <span class="spec-value">{{ value }}</span>
                </div>
              </div>
            </div>

            <div class="part-actions">
              <button 
                class="detail-btn"
                @click.stop="viewPartDetail(part)"
                title="查看详情"
              >
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </button>

              <div class="selection-indicator" v-if="selectedPart?.id === part.id">
                <svg fill="currentColor" viewBox="0 0 24 24">
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- 无结果 -->
        <div v-else class="no-results">
          <div class="no-results-icon">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <h4>未找到合适的零件</h4>
          <p>尝试调整搜索条件或分类筛选</p>
          <button class="btn btn-outline" @click="clearFilters">
            清除筛选条件
          </button>
        </div>
      </div>

      <div class="modal-footer">
        <div class="selection-info">
          <span v-if="selectedPart" class="selected-part-name">
            已选择: {{ selectedPart.name }}
          </span>
          <span v-else class="no-selection">
            请选择一个零件
          </span>
        </div>

        <div class="footer-actions">
          <button class="btn btn-outline" @click="closeModal">
            取消
          </button>
          <button 
            class="btn btn-primary"
            :disabled="!selectedPart"
            @click="confirmSelection"
          >
            确认选择
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { partsAPI } from '../utils/api'

export default {
  name: 'PartSelector',
  props: {
    targetCategory: {
      type: String,
      default: '' // 提供默认值，避免 undefined
    },
    isRequired: {
      type: Boolean,
      default: false // 提供默认值
    },
    currentPartId: {
      type: [String, Number], // 允许字符串和数字类型
      default: null
    },
    templateItem: {
      type: Object,
      default: () => null // 使用函数返回默认值
    }
  },
  emits: ['close', 'select', 'view-detail'],
  setup(props, { emit }) {
    const searchQuery = ref('')
    const selectedCategory = ref('')
    const selectedPart = ref(null)
    const allParts = ref([])
    const filteredParts = ref([])
    const availableCategories = ref([])
    const loading = ref(false)

    // 智能建议
    const suggestions = computed(() => {
      const suggestions = []
      
      // 基于目标分类的建议
      if (props.targetCategory) {
        suggestions.push(props.targetCategory)
      }

      // 基于模板条目的建议关键词
      if (props.templateItem?.notes) {
        const notes = props.templateItem.notes.toLowerCase()
        if (notes.includes('arduino')) suggestions.push('Arduino')
        if (notes.includes('5v') || notes.includes('5V')) suggestions.push('5V')
        if (notes.includes('3.3v') || notes.includes('3.3V')) suggestions.push('3.3V')
      }

      return [...new Set(suggestions)].slice(0, 3)
    })

    // 加载零件数据
    const loadParts = async () => {
      loading.value = true
      
      try {
        const response = await partsAPI.getParts({ limit: 100 })
        allParts.value = response.data
        
        // 提取可用分类
        const categories = new Set(allParts.value.map(p => p.category).filter(Boolean))
        availableCategories.value = Array.from(categories).sort()
        
        // 初始筛选
        filterParts()
        
      } catch (error) {
        console.error('加载零件失败:', error)
        allParts.value = []
      }
      
      loading.value = false
    }

    // 搜索零件
    const searchParts = () => {
      filterParts()
    }

    // 筛选零件
    const filterParts = () => {
      let filtered = [...allParts.value]

      // 按分类筛选
      if (selectedCategory.value) {
        filtered = filtered.filter(p => p.category === selectedCategory.value)
      }

      // 按关键词搜索
      if (searchQuery.value.trim()) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(p => 
          p.name.toLowerCase().includes(query) ||
          (p.category && p.category.toLowerCase().includes(query)) ||
          (p.description && p.description.toLowerCase().includes(query)) ||
          (p.properties && JSON.stringify(p.properties).toLowerCase().includes(query))
        )
      }

      // 优先显示目标分类的零件
      if (props.targetCategory && !selectedCategory.value && !searchQuery.value.trim()) {
        const targetParts = filtered.filter(p => 
          p.category && p.category.toLowerCase().includes(props.targetCategory.toLowerCase())
        )
        const otherParts = filtered.filter(p => 
          !p.category || !p.category.toLowerCase().includes(props.targetCategory.toLowerCase())
        )
        filtered = [...targetParts, ...otherParts]
      }

      filteredParts.value = filtered.slice(0, 50) // 限制显示数量
    }

    // 获取关键参数（显示前3个重要参数）
    const getKeySpecs = (properties) => {
      if (!properties || typeof properties !== 'object') return []
      
      const entries = Object.entries(properties)
      
      // 优先显示重要参数
      const priorityKeys = ['电压', '功率', '电流', '阻值', '容量', '频率', '接口', '封装']
      const priorityEntries = entries.filter(([key]) => 
        priorityKeys.some(pk => key.includes(pk))
      )
      const otherEntries = entries.filter(([key]) => 
        !priorityKeys.some(pk => key.includes(pk))
      )
      
      return [...priorityEntries, ...otherEntries].slice(0, 3)
    }

    // 选择零件
    const selectPart = (part) => {
      selectedPart.value = part
    }

    // 应用建议
    const applySuggestion = (suggestion) => {
      searchQuery.value = suggestion
      searchParts()
    }

    // 清除搜索
    const clearSearch = () => {
      searchQuery.value = ''
      searchParts()
    }

    // 清除筛选
    const clearFilters = () => {
      searchQuery.value = ''
      selectedCategory.value = ''
      filterParts()
    }

    // 查看零件详情
    const viewPartDetail = (part) => {
      emit('view-detail', part)
    }

    // 确认选择
    const confirmSelection = () => {
      if (selectedPart.value) {
        emit('select', selectedPart.value)
      }
    }

    // 关闭弹窗
    const closeModal = () => {
      emit('close')
    }

    // 监听当前选择的零件
    watch(() => props.currentPartId, (newId) => {
      if (newId && allParts.value.length > 0) {
        const currentPart = allParts.value.find(p => p.id === newId)
        if (currentPart) {
          selectedPart.value = currentPart
        }
      }
    })

    onMounted(() => {
      loadParts()
    })

    return {
      searchQuery,
      selectedCategory,
      selectedPart,
      filteredParts,
      availableCategories,
      loading,
      suggestions,
      loadParts,
      searchParts,
      filterParts,
      getKeySpecs,
      selectPart,
      applySuggestion,
      clearSearch,
      clearFilters,
      viewPartDetail,
      confirmSelection,
      closeModal
    }
  }
}
</script>

/* PartSelector.vue 样式完整版 */
<style scoped>
.part-selector-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  backdrop-filter: blur(4px);
}

.part-selector-modal {
  background: var(--bg-card);
  border-radius: 16px;
  width: 800px;
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  animation: modalSlideIn 0.3s ease;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* 模态框头部 */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  color: var(--text-primary);
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.category-name {
  font-size: 14px;
  color: var(--text-secondary);
  background: var(--bg-card);
  padding: 4px 12px;
  border-radius: 6px;
  font-weight: 500;
}

.requirement-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.requirement-badge.required {
  background: color-mix(in srgb, #f59e0b 15%, transparent);
  color: #f59e0b;
}

.requirement-badge:not(.required) {
  background: color-mix(in srgb, var(--text-muted) 15%, transparent);
  color: var(--text-muted);
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: var(--bg-card);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: var(--primary);
  color: white;
}

.close-btn svg {
  width: 16px;
  height: 16px;
}

/* 模态框内容 */
.modal-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* 搜索区域 */
.search-section {
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-card);
}

.search-input-container {
  position: relative;
  display: flex;
  align-items: center;
  margin-bottom: 16px;
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

.filter-section {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.category-filter {
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 13px;
  min-width: 120px;
}

.suggestions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.suggestions-label {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
}

.suggestion-tag {
  padding: 4px 8px;
  font-size: 12px;
  background: color-mix(in srgb, var(--primary) 10%, transparent);
  color: var(--primary);
  border: 1px solid color-mix(in srgb, var(--primary) 20%, transparent);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.suggestion-tag:hover {
  background: var(--primary);
  color: white;
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
  width: 32px;
  height: 32px;
  border: 2px solid var(--border-color);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

/* 零件列表 */
.parts-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  max-height: 400px;
}

.part-option {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  border: 2px solid transparent;
  border-radius: 12px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--bg-secondary);
}

.part-option:hover {
  background: var(--bg-card);
  border-color: var(--primary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.part-option.selected {
  border-color: var(--primary);
  background: color-mix(in srgb, var(--primary) 8%, var(--bg-card));
}

.part-image {
  width: 60px;
  height: 60px;
  background: var(--bg-card);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
}

.part-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
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
  width: 24px;
  height: 24px;
}

.part-info {
  flex: 1;
  min-width: 0;
}

.part-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.part-category {
  display: inline-block;
  font-size: 12px;
  color: var(--primary);
  background: color-mix(in srgb, var(--primary) 10%, transparent);
  padding: 2px 6px;
  border-radius: 3px;
  margin-bottom: 8px;
}

.part-description {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.4;
  margin: 0 0 12px 0;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.key-specs {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.spec-item {
  font-size: 12px;
  color: var(--text-secondary);
}

.spec-key {
  font-weight: 500;
  margin-right: 4px;
}

.spec-value {
  color: var(--text-primary);
  font-weight: 600;
}

.part-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.detail-btn {
  width: 32px;
  height: 32px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-card);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.detail-btn:hover {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.detail-btn svg {
  width: 16px;
  height: 16px;
}

.selection-indicator {
  width: 24px;
  height: 24px;
  background: var(--primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: checkMark 0.3s ease;
}

@keyframes checkMark {
  from {
    transform: scale(0);
  }
  to {
    transform: scale(1);
  }
}

.selection-indicator svg {
  width: 14px;
  height: 14px;
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
  width: 48px;
  height: 48px;
  color: var(--text-muted);
  margin-bottom: 16px;
}

.no-results h4 {
  font-size: 18px;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.no-results p {
  color: var(--text-secondary);
  margin: 0 0 20px 0;
}

/* 模态框底部 */
.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.selection-info {
  flex: 1;
  min-width: 0;
}

.selected-part-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.no-selection {
  font-size: 14px;
  color: var(--text-muted);
}

.footer-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.btn-outline {
  background: transparent;
  color: var(--text-primary);
  border-color: var(--border-color);
}

.btn-outline:hover {
  background: var(--bg-card);
  border-color: var(--primary);
}

.btn-primary {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.btn-primary:hover {
  background: var(--secondary);
  border-color: var(--secondary);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary:disabled:hover {
  background: var(--primary);
  border-color: var(--primary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .part-selector-modal {
    width: 100%;
    height: 100vh;
    max-height: 100vh;
    border-radius: 0;
  }
  
  .modal-header {
    padding: 16px 20px;
  }
  
  .modal-header h3 {
    font-size: 18px;
  }
  
  .header-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .search-section {
    padding: 16px 20px;
  }
  
  .filter-section {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .category-filter {
    min-width: auto;
  }
  
  .part-option {
    padding: 12px;
    gap: 12px;
  }
  
  .part-image {
    width: 50px;
    height: 50px;
  }
  
  .part-name {
    font-size: 15px;
  }
  
  .part-description {
    font-size: 12px;
  }
  
  .key-specs {
    gap: 8px;
  }
  
  .spec-item {
    font-size: 11px;
  }
  
  .part-actions {
    flex-direction: row;
  }
  
  .detail-btn {
    width: 28px;
    height: 28px;
  }
  
  .selection-indicator {
    width: 20px;
    height: 20px;
  }
  
  .modal-footer {
    padding: 16px 20px;
    flex-direction: column;
    gap: 12px;
  }
  
  .footer-actions {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .part-selector-overlay {
    padding: 0;
  }
  
  .suggestions {
    justify-content: flex-start;
  }
  
  .key-specs {
    flex-direction: column;
    gap: 4px;
  }
  
  .spec-item {
    display: flex;
    justify-content: space-between;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 动画增强 */
.part-option {
  animation: partOptionEnter 0.2s ease;
}

@keyframes partOptionEnter {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 滚动条样式 */
.parts-list::-webkit-scrollbar {
  width: 6px;
}

.parts-list::-webkit-scrollbar-track {
  background: var(--bg-secondary);
  border-radius: 3px;
}

.parts-list::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

.parts-list::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
}
</style>