<!-- portal/src/components/AdvancedFilters.vue (最终修复版本) -->
<template>
  <div class="advanced-filters-overlay" v-if="show" @click="closeIfClickOutside">
    <div class="advanced-filters-modal" @click.stop>
      <!-- 标题栏 -->
      <div class="modal-header">
        <h2 class="modal-title">
          <svg class="title-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
          </svg>
          高级筛选器
        </h2>
        <button @click="closeModal" class="close-btn">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-section">
        <div class="loading-spinner"></div>
        <p>加载筛选选项...</p>
      </div>

      <!-- 筛选器内容 -->
      <div v-else class="modal-content">
        <!-- 快速操作栏 -->
        <div class="quick-actions">
          <button @click="clearAllFilters" class="quick-btn clear-btn">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            清空全部筛选
          </button>
          
          <div class="active-filters-display">
            <span v-if="hasActiveFilters" class="active-count">
              已设置 {{ activeFiltersCount }} 个筛选条件
            </span>
            <span v-else class="no-filters">
              未设置筛选条件
            </span>
          </div>
        </div>

        <!-- 筛选器区域 -->
        <div class="filters-container">
          <!-- 左侧：分类和基础筛选 -->
          <div class="filters-section basic-filters">
            <h3 class="section-title">分类筛选</h3>
            
            <!-- 分类筛选（支持多选） -->
            <div v-if="metadata.categories && metadata.categories.length > 0" class="filter-group">
              <label class="filter-label">选择分类 (可多选)</label>
              <div class="category-grid">
                <label 
                  v-for="category in metadata.categories" 
                  :key="category.value"
                  class="category-option"
                  :class="{ active: filters.categories.includes(category.value) }"
                >
                  <input 
                    type="checkbox" 
                    :value="category.value"
                    :checked="filters.categories.includes(category.value)"
                    @change="toggleCategory(category.value, $event.target.checked)"
                  />
                  <span class="category-label">{{ category.label }}</span>
                  <span class="category-count">({{ category.count }})</span>
                </label>
              </div>
              <div v-if="filters.categories.length > 0" class="selected-categories">
                <span class="selected-label">已选择:</span>
                <div class="selected-tags">
                  <span 
                    v-for="category in filters.categories" 
                    :key="category"
                    class="selected-tag"
                  >
                    {{ category }}
                    <button @click="toggleCategory(category, false)" class="remove-tag">×</button>
                  </span>
                </div>
              </div>
            </div>

            <!-- 布尔筛选器 -->
            <div v-if="metadata.boolean_filters && metadata.boolean_filters.length > 0" class="filter-group">
              <label class="filter-label">状态筛选</label>
              <div class="boolean-filters">
                <label 
                  v-for="boolFilter in metadata.boolean_filters" 
                  :key="boolFilter.field"
                  class="boolean-option"
                >
                  <input 
                    type="checkbox" 
                    :checked="filters.boolean_filters[boolFilter.field] === true"
                    @change="toggleBooleanFilter(boolFilter.field, $event.target.checked)"
                  />
                  <span class="boolean-label">{{ boolFilter.label }}</span>
                  <span class="boolean-count">({{ boolFilter.true_count }})</span>
                </label>
              </div>
            </div>
          </div>

          <!-- 中间：数值筛选 -->
          <div v-if="metadata.numeric_filters && metadata.numeric_filters.length > 0" class="filters-section numeric-filters">
            <h3 class="section-title">数值筛选</h3>
            
            <div 
              v-for="numFilter in metadata.numeric_filters" 
              :key="numFilter.field"
              class="filter-group numeric-filter-group"
            >
              <label class="filter-label">
                {{ numFilter.label }}
                <span v-if="numFilter.unit" class="unit">({{ numFilter.unit }})</span>
                <span class="filter-count">({{ numFilter.count }} 个零件)</span>
              </label>
              
              <div class="numeric-range">
                <div class="range-inputs">
                  <input 
                    type="number" 
                    :min="numFilter.min"
                    :max="numFilter.max"
                    :step="numFilter.step"
                    :placeholder="`最小值 (${numFilter.min})`"
                    v-model.number="filters.numeric_filters[numFilter.field].min"
                    @input="onFilterChange"
                    class="range-input min-input"
                  />
                  <span class="range-separator">-</span>
                  <input 
                    type="number" 
                    :min="numFilter.min"
                    :max="numFilter.max"
                    :step="numFilter.step"
                    :placeholder="`最大值 (${numFilter.max})`"
                    v-model.number="filters.numeric_filters[numFilter.field].max"
                    @input="onFilterChange"
                    class="range-input max-input"
                  />
                </div>
                
                <!-- 范围滑块 -->
                <div class="range-slider">
                  <div class="slider-track">
                    <div 
                      class="slider-range"
                      :style="getSliderRangeStyle(numFilter)"
                    ></div>
                    <input
                      type="range"
                      :min="numFilter.min"
                      :max="numFilter.max"
                      :step="numFilter.step"
                      v-model.number="filters.numeric_filters[numFilter.field].min"
                      @input="onFilterChange"
                      class="range-slider-input min-slider"
                    />
                    <input
                      type="range"
                      :min="numFilter.min"
                      :max="numFilter.max"
                      :step="numFilter.step"
                      v-model.number="filters.numeric_filters[numFilter.field].max"
                      @input="onFilterChange"
                      class="range-slider-input max-slider"
                    />
                  </div>
                  <div class="slider-labels">
                    <span>{{ numFilter.min }}{{ numFilter.unit }}</span>
                    <span>{{ numFilter.max }}{{ numFilter.unit }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 右侧：枚举筛选 -->
          <div v-if="metadata.enum_filters && metadata.enum_filters.length > 0" class="filters-section enum-filters">
            <h3 class="section-title">选项筛选</h3>
            
            <div 
              v-for="enumFilter in metadata.enum_filters" 
              :key="enumFilter.field"
              class="filter-group enum-filter-group"
            >
              <label class="filter-label">
                {{ enumFilter.label }}
                <span class="filter-count">({{ enumFilter.count }} 个零件)</span>
              </label>
              
              <div class="enum-options" :class="{ expanded: expandedEnumFilters.has(enumFilter.field) }">
                <label 
                  v-for="(option, index) in getDisplayOptions(enumFilter)" 
                  :key="option.value"
                  class="enum-option"
                  :class="{ active: filters.enum_filters[enumFilter.field] && filters.enum_filters[enumFilter.field].includes(option.value) }"
                >
                  <input 
                    type="checkbox" 
                    :value="option.value"
                    :checked="filters.enum_filters[enumFilter.field] && filters.enum_filters[enumFilter.field].includes(option.value)"
                    @change="toggleEnumOption(enumFilter.field, option.value, $event.target.checked)"
                  />
                  <span class="option-label">{{ option.label }}</span>
                  <span class="option-count">({{ option.count }})</span>
                </label>
                
                <!-- 展开/收起按钮 -->
                <button 
                  v-if="enumFilter.options.length > maxDisplayOptions"
                  @click="toggleEnumExpansion(enumFilter.field)"
                  class="expand-btn"
                >
                  {{ expandedEnumFilters.has(enumFilter.field) ? '收起' : `+${enumFilter.options.length - maxDisplayOptions} 更多` }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { partsAPI } from '../utils/api'

export default {
  name: 'AdvancedFilters',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    initialFilters: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['close', 'apply', 'preview'],
  setup(props, { emit }) {
    const loading = ref(false)
    const metadata = ref({
      numeric_filters: [],
      enum_filters: [],
      boolean_filters: [],
      categories: []
    })
    
    const filters = ref({
      categories: [],
      numeric_filters: {},
      enum_filters: {},
      boolean_filters: {}
    })
    
    const expandedEnumFilters = ref(new Set())
    const maxDisplayOptions = 5
    
    // 计算属性
    const hasActiveFilters = computed(() => {
      return filters.value.categories.length > 0 ||
             Object.keys(filters.value.numeric_filters).some(key => {
               const range = filters.value.numeric_filters[key]
               return range && (range.min !== null || range.max !== null)
             }) ||
             Object.keys(filters.value.enum_filters).some(key => 
               filters.value.enum_filters[key] && filters.value.enum_filters[key].length > 0
             ) ||
             Object.keys(filters.value.boolean_filters).some(key => 
               filters.value.boolean_filters[key] !== null
             )
    })
    
    const activeFiltersCount = computed(() => {
      let count = 0
      if (filters.value.categories.length > 0) count++
      count += Object.keys(filters.value.numeric_filters).filter(key => {
        const range = filters.value.numeric_filters[key]
        return range && (range.min !== null || range.max !== null)
      }).length
      count += Object.keys(filters.value.enum_filters).filter(key => 
        filters.value.enum_filters[key] && filters.value.enum_filters[key].length > 0
      ).length
      count += Object.keys(filters.value.boolean_filters).filter(key => 
        filters.value.boolean_filters[key] !== null
      ).length
      return count
    })
    
    // 加载筛选器元数据
    const loadMetadata = async () => {
      loading.value = true
      try {
        const response = await partsAPI.getFiltersMetadata()
        metadata.value = response.data
        
        // 初始化筛选器状态
        initializeFilters()
      } catch (error) {
        console.error('加载筛选器元数据失败:', error)
      }
      loading.value = false
    }
    
    // 初始化筛选器状态
    const initializeFilters = () => {
      // 初始化数值筛选器
      metadata.value.numeric_filters.forEach(filter => {
        if (!filters.value.numeric_filters[filter.field]) {
          filters.value.numeric_filters[filter.field] = {
            min: null,
            max: null
          }
        }
      })
      
      // 初始化枚举筛选器
      metadata.value.enum_filters.forEach(filter => {
        if (!filters.value.enum_filters[filter.field]) {
          filters.value.enum_filters[filter.field] = []
        }
      })
      
      // 初始化布尔筛选器
      metadata.value.boolean_filters.forEach(filter => {
        if (filters.value.boolean_filters[filter.field] === undefined) {
          filters.value.boolean_filters[filter.field] = null
        }
      })
      
      // 应用初始筛选条件
      if (props.initialFilters) {
        applyInitialFilters(props.initialFilters)
      }
    }
    
    // 应用初始筛选条件
    const applyInitialFilters = (initialFilters) => {
      // 处理分类（支持多选）
      if (initialFilters.categories && Array.isArray(initialFilters.categories)) {
        filters.value.categories = [...initialFilters.categories]
      } else if (initialFilters.category) {
        filters.value.categories = [initialFilters.category]
      }
      
      if (initialFilters.numeric_filters) {
        Object.assign(filters.value.numeric_filters, initialFilters.numeric_filters)
      }
      
      if (initialFilters.enum_filters) {
        Object.assign(filters.value.enum_filters, initialFilters.enum_filters)
      }
      
      if (initialFilters.boolean_filters) {
        Object.assign(filters.value.boolean_filters, initialFilters.boolean_filters)
      }
    }
    
    // 获取显示的选项
    const getDisplayOptions = (enumFilter) => {
      if (expandedEnumFilters.value.has(enumFilter.field)) {
        return enumFilter.options
      }
      return enumFilter.options.slice(0, maxDisplayOptions)
    }
    
    // 切换枚举筛选器的展开状态
    const toggleEnumExpansion = (field) => {
      if (expandedEnumFilters.value.has(field)) {
        expandedEnumFilters.value.delete(field)
      } else {
        expandedEnumFilters.value.add(field)
      }
    }
    
    // 切换分类选择
    const toggleCategory = (category, checked) => {
      if (checked) {
        if (!filters.value.categories.includes(category)) {
          filters.value.categories.push(category)
        }
      } else {
        const index = filters.value.categories.indexOf(category)
        if (index > -1) {
          filters.value.categories.splice(index, 1)
        }
      }
      onFilterChange()
    }
    
    // 切换布尔筛选器
    const toggleBooleanFilter = (field, checked) => {
      filters.value.boolean_filters[field] = checked ? true : null
      onFilterChange()
    }
    
    // 切换枚举选项
    const toggleEnumOption = (field, value, checked) => {
      if (!filters.value.enum_filters[field]) {
        filters.value.enum_filters[field] = []
      }
      
      const options = filters.value.enum_filters[field]
      if (checked) {
        if (!options.includes(value)) {
          options.push(value)
        }
      } else {
        const index = options.indexOf(value)
        if (index > -1) {
          options.splice(index, 1)
        }
      }
      onFilterChange()
    }
    
    // 筛选条件变化时（实时应用）
    const onFilterChange = () => {
      // 防抖应用筛选
      clearTimeout(onFilterChange.timer)
      onFilterChange.timer = setTimeout(() => {
        emit('apply', JSON.parse(JSON.stringify(filters.value)))
      }, 300)
    }
    
    // 获取滑块范围样式
    const getSliderRangeStyle = (numFilter) => {
      const min = filters.value.numeric_filters[numFilter.field]?.min ?? numFilter.min
      const max = filters.value.numeric_filters[numFilter.field]?.max ?? numFilter.max
      
      const range = numFilter.max - numFilter.min
      const leftPercent = ((min - numFilter.min) / range) * 100
      const rightPercent = ((numFilter.max - max) / range) * 100
      
      return {
        left: `${leftPercent}%`,
        right: `${rightPercent}%`
      }
    }
    
    // 清空所有筛选
    const clearAllFilters = () => {
      console.log('清空所有筛选条件')
      
      // 完全重置筛选条件
      filters.value.categories = []
      filters.value.numeric_filters = {}
      filters.value.enum_filters = {}
      filters.value.boolean_filters = {}
      
      // 重新初始化空的筛选器结构
      if (metadata.value) {
        metadata.value.numeric_filters.forEach(filter => {
          filters.value.numeric_filters[filter.field] = {
            min: null,
            max: null
          }
        })
        
        metadata.value.enum_filters.forEach(filter => {
          filters.value.enum_filters[filter.field] = []
        })
        
        metadata.value.boolean_filters.forEach(filter => {
          filters.value.boolean_filters[filter.field] = null
        })
      }
      
      // 触发筛选变化
      onFilterChange()
    }
    
    // 关闭模态框
    const closeModal = () => {
      emit('close')
    }
    
    // 点击外部关闭
    const closeIfClickOutside = (event) => {
      if (event.target === event.currentTarget) {
        closeModal()
      }
    }
    
    // 监听显示状态
    watch(() => props.show, (newVal) => {
      if (newVal) {
        loadMetadata()
      }
    })
    
    onMounted(() => {
      if (props.show) {
        loadMetadata()
      }
    })
    
    return {
      loading,
      metadata,
      filters,
      expandedEnumFilters,
      maxDisplayOptions,
      hasActiveFilters,
      activeFiltersCount,
      getDisplayOptions,
      toggleEnumExpansion,
      toggleCategory,
      toggleBooleanFilter,
      toggleEnumOption,
      onFilterChange,
      getSliderRangeStyle,
      clearAllFilters,
      closeModal,
      closeIfClickOutside
    }
  }
}
</script>

<style scoped>
.advanced-filters-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.advanced-filters-modal {
  background: var(--bg-card);
  border-radius: 16px;
  box-shadow: var(--shadow-lg);
  width: 100%;
  max-width: 1200px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  animation: slideInUp 0.3s ease;
}

@keyframes slideInUp {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* 标题栏 */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.title-icon {
  width: 24px;
  height: 24px;
  color: var(--primary);
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.close-btn svg {
  width: 18px;
  height: 18px;
}

/* 加载状态 */
.loading-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
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
  to { transform: rotate(360deg); }
}

/* 内容区域 */
.modal-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* 快速操作栏 */
.quick-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.quick-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quick-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.quick-btn svg {
  width: 14px;
  height: 14px;
}

.clear-btn:hover {
  border-color: #f43f5e;
  color: #f43f5e;
  background: color-mix(in srgb, #f43f5e 5%, transparent);
}

.active-filters-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.active-count {
  color: var(--primary);
  font-weight: 500;
  font-size: 14px;
}

.no-filters {
  color: var(--text-muted);
  font-size: 14px;
}

/* 筛选器容器 */
.filters-container {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 32px;
  margin-bottom: 24px;
}

.filters-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--primary);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.filter-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.unit, .filter-count {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: normal;
}

/* 分类筛选 */
.category-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

.category-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.category-option:hover {
  background: var(--bg-secondary);
  border-color: var(--primary);
}

.category-option.active {
  background: color-mix(in srgb, var(--primary) 10%, transparent);
  border-color: var(--primary);
  color: var(--primary);
}

.category-option input[type="checkbox"] {
  margin: 0;
}

.category-label {
  flex: 1;
  font-size: 13px;
}

.category-count {
  font-size: 11px;
  color: var(--text-muted);
}

/* 已选择的分类标签 */
.selected-categories {
  margin-top: 8px;
  padding: 8px;
  background: var(--bg-secondary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.selected-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
  display: block;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.selected-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 6px;
  background: var(--primary);
  color: white;
  border-radius: 4px;
  font-size: 11px;
}

.remove-tag {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  padding: 0;
  width: 14px;
  height: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s ease;
}

.remove-tag:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* 布尔筛选 */
.boolean-filters {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.boolean-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  cursor: pointer;
}

.boolean-label {
  flex: 1;
  font-size: 13px;
  color: var(--text-secondary);
}

.boolean-count {
  font-size: 11px;
  color: var(--text-muted);
}

/* 数值筛选 */
.numeric-filter-group {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  background: var(--bg-secondary);
}

.numeric-range {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.range-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
}

.range-input {
  flex: 1;
  padding: 6px 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 12px;
  background: var(--bg-card);
  color: var(--text-primary);
}

.range-separator {
  color: var(--text-muted);
  font-weight: 500;
}

/* 范围滑块 */
.range-slider {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.slider-track {
  position: relative;
  height: 6px;
  background: var(--border-color);
  border-radius: 3px;
}

.slider-range {
  position: absolute;
  height: 100%;
  background: var(--primary);
  border-radius: 3px;
}

.range-slider-input {
  position: absolute;
  width: 100%;
  height: 6px;
  background: none;
  pointer-events: none;
  -webkit-appearance: none;
  appearance: none;
}

.range-slider-input::-webkit-slider-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--primary);
  cursor: pointer;
  pointer-events: all;
  -webkit-appearance: none;
  appearance: none;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.range-slider-input::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--primary);
  cursor: pointer;
  pointer-events: all;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--text-muted);
}

/* 枚举筛选 */
.enum-filter-group {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  background: var(--bg-secondary);
}

.enum-options {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 200px;
  overflow: hidden;
  transition: max-height 0.3s ease;
}

.enum-options.expanded {
  max-height: 400px;
  overflow-y: auto;
}

.enum-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.enum-option:hover {
  background: var(--bg-card);
}

.enum-option.active {
  background: color-mix(in srgb, var(--primary) 10%, transparent);
  color: var(--primary);
}

.option-label {
  flex: 1;
  font-size: 12px;
}

.option-count {
  font-size: 10px;
  color: var(--text-muted);
}

.expand-btn {
  margin-top: 8px;
  padding: 4px 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.expand-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .filters-container {
    grid-template-columns: 1fr 1fr;
    gap: 24px;
  }
  
  .enum-filters {
    grid-column: 1 / -1;
  }
}

@media (max-width: 768px) {
  .advanced-filters-overlay {
    padding: 10px;
  }
  
  .advanced-filters-modal {
    max-height: 95vh;
  }
  
  .modal-header {
    padding: 16px;
  }
  
  .modal-content {
    padding: 16px;
  }
  
  .filters-container {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .quick-actions {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .active-filters-display {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .range-inputs {
    flex-direction: column;
    gap: 4px;
  }
  
  .range-separator {
    align-self: center;
  }
  
  .selected-tags {
    justify-content: center;
  }
}
</style>