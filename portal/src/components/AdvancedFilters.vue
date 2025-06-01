<!-- portal/src/components/AdvancedFilters.vue (标签页版本 - 集成兼容性筛选) -->
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

      <!-- 标签页导航 -->
      <div class="tabs-navigation">
        <button 
          @click="activeTab = 'traditional'"
          class="tab-btn"
          :class="{ active: activeTab === 'traditional' }"
        >
          <svg class="tab-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
          </svg>
          <span>传统筛选</span>
          <span v-if="hasTraditionalFilters" class="tab-badge traditional">{{ traditionalFiltersCount }}</span>
        </button>
        
        <button 
          @click="activeTab = 'compatibility'"
          class="tab-btn"
          :class="{ active: activeTab === 'compatibility' }"
        >
          <svg class="tab-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>兼容性筛选</span>
          <span v-if="hasCompatibilityFilters" class="tab-badge compatibility">{{ compatibilityFiltersCount }}</span>
        </button>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-section">
        <div class="loading-spinner"></div>
        <p>加载筛选选项...</p>
      </div>

      <!-- 标签页内容 -->
      <div v-else class="tabs-content">
        <!-- 传统筛选标签页 -->
        <div v-show="activeTab === 'traditional'" class="tab-panel traditional-panel">
          <!-- 快速操作栏 -->
          <div class="quick-actions">
            <button @click="clearTraditionalFilters" class="quick-btn clear-btn">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              清空传统筛选
            </button>
            
            <div class="active-filters-display">
              <span v-if="hasTraditionalFilters" class="active-count">
                已设置 {{ traditionalFiltersCount }} 个条件
              </span>
              <span v-else class="no-filters">
                未设置筛选条件
              </span>
            </div>
          </div>

          <!-- 传统筛选器区域 -->
          <div class="filters-container traditional-filters">
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
                    :class="{ active: traditionalFilters.categories.includes(category.value) }"
                  >
                    <input 
                      type="checkbox" 
                      :value="category.value"
                      :checked="traditionalFilters.categories.includes(category.value)"
                      @change="toggleTraditionalCategory(category.value, $event.target.checked)"
                    />
                    <span class="category-label">{{ category.label }}</span>
                    <span class="category-count">({{ category.count }})</span>
                  </label>
                </div>
                <div v-if="traditionalFilters.categories.length > 0" class="selected-categories">
                  <span class="selected-label">已选择:</span>
                  <div class="selected-tags">
                    <span 
                      v-for="category in traditionalFilters.categories" 
                      :key="category"
                      class="selected-tag"
                    >
                      {{ category }}
                      <button @click="toggleTraditionalCategory(category, false)" class="remove-tag">×</button>
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
                      :checked="traditionalFilters.boolean_filters[boolFilter.field] === true"
                      @change="toggleTraditionalBooleanFilter(boolFilter.field, $event.target.checked)"
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
                      v-model.number="traditionalFilters.numeric_filters[numFilter.field].min"
                      @input="onTraditionalFilterChange"
                      class="range-input min-input"
                    />
                    <span class="range-separator">-</span>
                    <input 
                      type="number" 
                      :min="numFilter.min"
                      :max="numFilter.max"
                      :step="numFilter.step"
                      :placeholder="`最大值 (${numFilter.max})`"
                      v-model.number="traditionalFilters.numeric_filters[numFilter.field].max"
                      @input="onTraditionalFilterChange"
                      class="range-input max-input"
                    />
                  </div>
                  
                  <!-- 范围滑块 -->
                  <div class="range-slider">
                    <div class="slider-track">
                      <div 
                        class="slider-range"
                        :style="getSliderRangeStyle(numFilter, traditionalFilters.numeric_filters[numFilter.field])"
                      ></div>
                      <input
                        type="range"
                        :min="numFilter.min"
                        :max="numFilter.max"
                        :step="numFilter.step"
                        v-model.number="traditionalFilters.numeric_filters[numFilter.field].min"
                        @input="onTraditionalFilterChange"
                        class="range-slider-input min-slider"
                      />
                      <input
                        type="range"
                        :min="numFilter.min"
                        :max="numFilter.max"
                        :step="numFilter.step"
                        v-model.number="traditionalFilters.numeric_filters[numFilter.field].max"
                        @input="onTraditionalFilterChange"
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
                    :class="{ active: traditionalFilters.enum_filters[enumFilter.field] && traditionalFilters.enum_filters[enumFilter.field].includes(option.value) }"
                  >
                    <input 
                      type="checkbox" 
                      :value="option.value"
                      :checked="traditionalFilters.enum_filters[enumFilter.field] && traditionalFilters.enum_filters[enumFilter.field].includes(option.value)"
                      @change="toggleTraditionalEnumOption(enumFilter.field, option.value, $event.target.checked)"
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

          <!-- 最近使用的筛选 -->
          <div v-if="recentFilters.length > 0" class="recent-filters-section">
            <h3 class="filter-title">最近使用的筛选</h3>
            <div class="recent-filters">
              <button 
                v-for="recent in recentFilters.slice(0, 3)" 
                :key="recent.hash"
                @click="loadRecentFilter(recent)"
                class="recent-filter-btn"
                :title="recent.description"
              >
                {{ recent.description.length > 40 ? recent.description.substring(0, 40) + '...' : recent.description }}
              </button>
            </div>
          </div>
        </div>

        <!-- 兼容性筛选标签页 -->
        <div v-show="activeTab === 'compatibility'" class="tab-panel compatibility-panel">
          <!-- 快速操作栏 -->
          <div class="quick-actions">
            <button @click="clearCompatibilityFilters" class="quick-btn clear-btn">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              清空兼容性筛选
            </button>
            
            <div class="active-filters-display">
              <span v-if="hasCompatibilityFilters" class="active-count compatibility">
                已选择 {{ compatibilityFilters.selectedParts.length }} 个零件
              </span>
              <span v-else class="no-filters">
                未选择零件
              </span>
            </div>
          </div>

          <!-- 智能提示 -->
          <div v-if="compatibilityCheckCount > 0" class="compatibility-hint">
            <div class="hint-content">
              <svg class="hint-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>检测到您的兼容性检查列表中有 {{ compatibilityCheckCount }} 个零件</span>
            </div>
            <button @click="importFromCompatibilityList" class="import-btn">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8l-8-8-8 8" />
              </svg>
              导入到筛选
            </button>
          </div>

          <!-- 兼容性筛选选项 -->
          <div class="compatibility-filters">
            <!-- 零件选择区域 -->
            <div class="filter-section">
              <h3 class="section-title">选择基准零件</h3>
              
              <!-- 零件搜索 -->
              <div class="part-search">
                <div class="search-input-wrapper">
                  <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <input
                    v-model="partSearchQuery"
                    type="text"
                    class="part-search-input"
                    placeholder="搜索零件名称或型号..."
                    @input="onPartSearchInput"
                    @focus="showPartSuggestions = true"
                    @blur="onPartSearchBlur"
                  />
                </div>
                
                <!-- 零件搜索结果 -->
                <div v-if="showPartSuggestions && (partSuggestions.length > 0 || partSearchLoading)" class="part-suggestions">
                  <div v-if="partSearchLoading" class="suggestion-loading">
                    <div class="loading-spinner small"></div>
                    <span>搜索中...</span>
                  </div>
                  
                  <div 
                    v-for="part in partSuggestions" 
                    :key="part.id"
                    class="part-suggestion-item"
                    @mousedown="addPartToCompatibility(part)"
                  >
                    <div class="part-info">
                      <span class="part-name">{{ part.name }}</span>
                      <span class="part-category">{{ part.category }}</span>
                    </div>
                    <button class="add-part-btn">
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>

              <!-- 已选择的零件 -->
              <div v-if="compatibilityFilters.selectedParts.length > 0" class="selected-parts">
                <div class="selected-parts-header">
                  <span class="selected-label">已选择的零件 ({{ compatibilityFilters.selectedParts.length }})</span>
                  <button v-if="compatibilityFilters.selectedParts.length > 1" @click="clearSelectedParts" class="clear-selected-btn">
                    清空
                  </button>
                </div>
                <div class="selected-parts-list">
                  <div 
                    v-for="part in compatibilityFilters.selectedParts" 
                    :key="part.id"
                    class="selected-part-item"
                  >
                    <div class="part-info">
                      <span class="part-name">{{ part.name }}</span>
                      <span class="part-category">{{ part.category }}</span>
                    </div>
                    <button @click="removePartFromCompatibility(part.id)" class="remove-part-btn">
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>

              <!-- 空状态提示 -->
              <div v-else class="empty-parts-hint">
                <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p>请选择至少一个零件作为兼容性检查的基准</p>
                <p class="hint-text">搜索并添加零件，系统将找出与它们兼容的其他零件</p>
              </div>
            </div>

            <!-- 兼容性选项 -->
            <div v-if="compatibilityFilters.selectedParts.length > 0" class="filter-section">
              <h3 class="section-title">兼容性设置</h3>
              
              <!-- 评分阈值 -->
              <div class="filter-group">
                <label class="filter-label">
                  最低兼容性评分
                  <span class="current-value">({{ compatibilityFilters.minScore }}分)</span>
                </label>
                <div class="score-slider">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    step="5"
                    v-model.number="compatibilityFilters.minScore"
                    @input="onCompatibilityFilterChange"
                    class="score-range"
                  />
                  <div class="score-labels">
                    <span class="score-label low">不兼容 (0)</span>
                    <span class="score-label medium">理论兼容 (50)</span>
                    <span class="score-label high">完全兼容 (100)</span>
                  </div>
                  <div class="score-grades">
                    <div class="grade-indicator" :class="{ active: compatibilityFilters.minScore >= 0 && compatibilityFilters.minScore < 50 }">
                      <span class="grade-text">不兼容</span>
                      <span class="grade-range">0-49分</span>
                    </div>
                    <div class="grade-indicator" :class="{ active: compatibilityFilters.minScore >= 50 && compatibilityFilters.minScore < 70 }">
                      <span class="grade-text">理论兼容</span>
                      <span class="grade-range">50-69分</span>
                    </div>
                    <div class="grade-indicator" :class="{ active: compatibilityFilters.minScore >= 70 && compatibilityFilters.minScore < 90 }">
                      <span class="grade-text">社区验证</span>
                      <span class="grade-range">70-89分</span>
                    </div>
                    <div class="grade-indicator" :class="{ active: compatibilityFilters.minScore >= 90 }">
                      <span class="grade-text">官方支持</span>
                      <span class="grade-range">90-100分</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 兼容性设置说明 -->
              <div class="filter-group">
                <label class="filter-label">兼容性设置说明</label>
                <div class="settings-help">
                  <div class="help-item">
                    <strong>评分说明：</strong>
                    <span>0-49分=不兼容，50-69分=理论兼容，70-89分=社区验证，90-100分=官方支持</span>
                  </div>
                  <div class="help-item">
                    <strong>分类筛选：</strong>
                    <span>可在"传统筛选"标签页中限制搜索的零件分类</span>
                  </div>
                </div>
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
import { partsAPI, debounce, advancedFiltersManager } from '../utils/api'
import { compatibilityCheckManager } from '../utils/compatibilityManager'

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
    const activeTab = ref('traditional')
    const metadata = ref({
      numeric_filters: [],
      enum_filters: [],
      boolean_filters: [],
      categories: []
    })
    
    // 传统筛选状态
    const traditionalFilters = ref({
      categories: [],
      numeric_filters: {},
      enum_filters: {},
      boolean_filters: {}
    })
    
    // 兼容性筛选状态
    const compatibilityFilters = ref({
      enabled: false,
      selectedParts: [],
      minScore: 70
    })
    
    // 零件搜索相关
    const partSearchQuery = ref('')
    const partSuggestions = ref([])
    const showPartSuggestions = ref(false)
    const partSearchLoading = ref(false)
    
    const expandedEnumFilters = ref(new Set())
    const maxDisplayOptions = 5
    const recentFilters = ref([])
    
    // 兼容性检查管理器状态
    const compatibilityCheckCount = computed(() => {
      return compatibilityCheckManager.getCheckCount()
    })
    
    // 计算属性
    const hasTraditionalFilters = computed(() => {
      return advancedFiltersManager.hasActiveFilters(traditionalFilters.value)
    })
    
    const traditionalFiltersCount = computed(() => {
      let count = 0
      if (traditionalFilters.value.categories && traditionalFilters.value.categories.length > 0) count++
      count += Object.keys(traditionalFilters.value.numeric_filters || {}).filter(key => {
        const range = traditionalFilters.value.numeric_filters[key]
        return range && (range.min !== null || range.max !== null)
      }).length
      count += Object.keys(traditionalFilters.value.enum_filters || {}).filter(key => 
        traditionalFilters.value.enum_filters[key] && traditionalFilters.value.enum_filters[key].length > 0
      ).length
      count += Object.keys(traditionalFilters.value.boolean_filters || {}).filter(key => 
        traditionalFilters.value.boolean_filters[key] !== null
      ).length
      return count
    })
    
    const hasCompatibilityFilters = computed(() => {
      return compatibilityFilters.value.enabled && compatibilityFilters.value.selectedParts.length > 0
    })
    
    const compatibilityFiltersCount = computed(() => {
      return compatibilityFilters.value.selectedParts.length
    })
    
    // 加载筛选器元数据
    const loadMetadata = async () => {
      loading.value = true
      try {
        const response = await partsAPI.getFiltersMetadata()
        metadata.value = response.data
        initializeFilters()
      } catch (error) {
        console.error('加载筛选器元数据失败:', error)
      }
      loading.value = false
    }
    
    // 初始化筛选器状态
    const initializeFilters = () => {
      // 初始化传统筛选器
      metadata.value.numeric_filters.forEach(filter => {
        if (!traditionalFilters.value.numeric_filters[filter.field]) {
          traditionalFilters.value.numeric_filters[filter.field] = {
            min: null,
            max: null
          }
        }
      })
      
      metadata.value.enum_filters.forEach(filter => {
        if (!traditionalFilters.value.enum_filters[filter.field]) {
          traditionalFilters.value.enum_filters[filter.field] = []
        }
      })
      
      metadata.value.boolean_filters.forEach(filter => {
        if (traditionalFilters.value.boolean_filters[filter.field] === undefined) {
          traditionalFilters.value.boolean_filters[filter.field] = null
        }
      })
      
      // 应用初始筛选条件
      if (props.initialFilters) {
        applyInitialFilters(props.initialFilters)
      }
    }
    
    // 应用初始筛选条件
    const applyInitialFilters = (initialFilters) => {
      // 处理传统筛选
      if (initialFilters.categories && Array.isArray(initialFilters.categories)) {
        traditionalFilters.value.categories = [...initialFilters.categories]
      } else if (initialFilters.category) {
        traditionalFilters.value.categories = [initialFilters.category]
      }
      
      if (initialFilters.numeric_filters) {
        Object.assign(traditionalFilters.value.numeric_filters, initialFilters.numeric_filters)
      }
      
      if (initialFilters.enum_filters) {
        Object.assign(traditionalFilters.value.enum_filters, initialFilters.enum_filters)
      }
      
      if (initialFilters.boolean_filters) {
        Object.assign(traditionalFilters.value.boolean_filters, initialFilters.boolean_filters)
      }
      
      // 处理兼容性筛选（如果有的话）
      if (initialFilters.compatibility) {
        Object.assign(compatibilityFilters.value, initialFilters.compatibility)
        if (compatibilityFilters.value.selectedParts.length > 0) {
          activeTab.value = 'compatibility'
        }
      }
    }
    
    // 零件搜索相关方法
    const debouncedPartSearch = debounce(async (query) => {
      if (!query.trim()) {
        partSuggestions.value = []
        partSearchLoading.value = false
        return
      }
      
      partSearchLoading.value = true
      
      try {
        const response = await partsAPI.search({ q: query, limit: 8 })
        partSuggestions.value = response.data || []
      } catch (error) {
        console.error('零件搜索失败:', error)
        partSuggestions.value = []
      }
      
      partSearchLoading.value = false
    }, 300)
    
    const onPartSearchInput = () => {
      debouncedPartSearch(partSearchQuery.value)
    }
    
    const onPartSearchBlur = () => {
      setTimeout(() => {
        showPartSuggestions.value = false
      }, 200)
    }
    
    const addPartToCompatibility = (part) => {
      if (compatibilityFilters.value.selectedParts.find(p => p.id === part.id)) {
        return // 已存在
      }
      
      if (compatibilityFilters.value.selectedParts.length >= 10) {
        return // 超出限制
      }
      
      compatibilityFilters.value.selectedParts.push({
        id: part.id,
        name: part.name,
        category: part.category
      })
      
      if (!compatibilityFilters.value.enabled) {
        compatibilityFilters.value.enabled = true
      }
      
      partSearchQuery.value = ''
      partSuggestions.value = []
      showPartSuggestions.value = false
      
      onCompatibilityFilterChange()
    }
    
    const removePartFromCompatibility = (partId) => {
      const index = compatibilityFilters.value.selectedParts.findIndex(p => p.id === partId)
      if (index > -1) {
        compatibilityFilters.value.selectedParts.splice(index, 1)
        
        if (compatibilityFilters.value.selectedParts.length === 0) {
          compatibilityFilters.value.enabled = false
        }
        
        onCompatibilityFilterChange()
      }
    }
    
    const clearSelectedParts = () => {
      compatibilityFilters.value.selectedParts = []
      compatibilityFilters.value.enabled = false
      onCompatibilityFilterChange()
    }
    
    const importFromCompatibilityList = () => {
      const checkList = compatibilityCheckManager.getCheckList()
      compatibilityFilters.value.selectedParts = checkList.map(part => ({
        id: part.id,
        name: part.name,
        category: part.category
      }))
      compatibilityFilters.value.enabled = true
      onCompatibilityFilterChange()
    }
    
    // 传统筛选方法
    const toggleTraditionalCategory = (category, checked) => {
      if (checked) {
        if (!traditionalFilters.value.categories.includes(category)) {
          traditionalFilters.value.categories.push(category)
        }
      } else {
        const index = traditionalFilters.value.categories.indexOf(category)
        if (index > -1) {
          traditionalFilters.value.categories.splice(index, 1)
        }
      }
      onTraditionalFilterChange()
    }
    
    const toggleTraditionalBooleanFilter = (field, checked) => {
      traditionalFilters.value.boolean_filters[field] = checked ? true : null
      onTraditionalFilterChange()
    }
    
    const toggleTraditionalEnumOption = (field, value, checked) => {
      if (!traditionalFilters.value.enum_filters[field]) {
        traditionalFilters.value.enum_filters[field] = []
      }
      
      const options = traditionalFilters.value.enum_filters[field]
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
      onTraditionalFilterChange()
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
    
    // 筛选条件变化时
    const onTraditionalFilterChange = () => {
      clearTimeout(onTraditionalFilterChange.timer)
      onTraditionalFilterChange.timer = setTimeout(() => {
        applyFilters()
      }, 300)
    }
    
    const onCompatibilityFilterChange = () => {
      clearTimeout(onCompatibilityFilterChange.timer)
      onCompatibilityFilterChange.timer = setTimeout(() => {
        applyFilters()
      }, 300)
    }
    
    // 应用筛选
    const applyFilters = () => {
      const combinedFilters = {
        traditional: JSON.parse(JSON.stringify(traditionalFilters.value)),
        compatibility: JSON.parse(JSON.stringify(compatibilityFilters.value)),
        activeTab: activeTab.value
      }
      
      emit('apply', combinedFilters)
    }
    
    // 获取滑块范围样式
    const getSliderRangeStyle = (numFilter, range) => {
      const min = range?.min ?? numFilter.min
      const max = range?.max ?? numFilter.max
      
      const totalRange = numFilter.max - numFilter.min
      const leftPercent = ((min - numFilter.min) / totalRange) * 100
      const rightPercent = ((numFilter.max - max) / totalRange) * 100
      
      return {
        left: `${leftPercent}%`,
        right: `${rightPercent}%`
      }
    }
    
    // 清空筛选
    const clearTraditionalFilters = () => {
      traditionalFilters.value.categories = []
      traditionalFilters.value.numeric_filters = {}
      traditionalFilters.value.enum_filters = {}
      traditionalFilters.value.boolean_filters = {}
      
      // 重新初始化空的筛选器结构
      if (metadata.value) {
        metadata.value.numeric_filters.forEach(filter => {
          traditionalFilters.value.numeric_filters[filter.field] = {
            min: null,
            max: null
          }
        })
        
        metadata.value.enum_filters.forEach(filter => {
          traditionalFilters.value.enum_filters[filter.field] = []
        })
        
        metadata.value.boolean_filters.forEach(filter => {
          traditionalFilters.value.boolean_filters[filter.field] = null
        })
      }
      
      onTraditionalFilterChange()
    }
    
    const clearCompatibilityFilters = () => {
      compatibilityFilters.value = {
        enabled: false,
        selectedParts: [],
        minScore: 70
      }
      onCompatibilityFilterChange()
    }
    
    // 加载最近筛选
    const loadRecentFilters = () => {
      recentFilters.value = advancedFiltersManager.getRecentFilters()
    }
    
    // 使用最近筛选
    const loadRecentFilter = (recent) => {
      traditionalFilters.value = { ...recent.filters }
      onTraditionalFilterChange()
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
        loadRecentFilters()
      }
    })
    
    // 智能切换标签页
    watch(() => compatibilityCheckCount.value, (newCount) => {
      if (newCount > 0 && activeTab.value === 'traditional' && compatibilityFilters.value.selectedParts.length === 0) {
        // 如果用户在兼容性检查列表中有零件，但兼容性筛选中没有，可以提示切换
      }
    })
    
    onMounted(() => {
      if (props.show) {
        loadMetadata()
        loadRecentFilters()
      }
    })
    
    return {
      loading,
      activeTab,
      metadata,
      traditionalFilters,
      compatibilityFilters,
      partSearchQuery,
      partSuggestions,
      showPartSuggestions,
      partSearchLoading,
      expandedEnumFilters,
      maxDisplayOptions,
      recentFilters,
      compatibilityCheckCount,
      hasTraditionalFilters,
      traditionalFiltersCount,
      hasCompatibilityFilters,
      compatibilityFiltersCount,
      getDisplayOptions,
      toggleEnumExpansion,
      toggleTraditionalCategory,
      toggleTraditionalBooleanFilter,
      toggleTraditionalEnumOption,
      onTraditionalFilterChange,
      onCompatibilityFilterChange,
      getSliderRangeStyle,
      clearTraditionalFilters,
      clearCompatibilityFilters,
      loadRecentFilter,
      closeModal,
      closeIfClickOutside,
      onPartSearchInput,
      onPartSearchBlur,
      addPartToCompatibility,
      removePartFromCompatibility,
      clearSelectedParts,
      importFromCompatibilityList
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

/* 标签页导航 */
.tabs-navigation {
  display: flex;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px 24px;
  border: none;
  background: none;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.tab-btn:hover {
  background: var(--bg-card);
  color: var(--text-primary);
}

.tab-btn.active {
  background: var(--bg-card);
  color: var(--primary);
  font-weight: 600;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--primary);
}

.tab-icon {
  width: 16px;
  height: 16px;
}

.tab-badge {
  background: var(--primary);
  color: white;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
  line-height: 1.2;
}

.tab-badge.traditional {
  background: var(--primary);
}

.tab-badge.compatibility {
  background: #10b981;
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

.loading-spinner.small {
  width: 20px;
  height: 20px;
  border-width: 2px;
  margin-bottom: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 标签页内容 */
.tabs-content {
  flex: 1;
  overflow-y: auto;
}

.tab-panel {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 快速操作栏 */
.quick-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
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

.active-count.compatibility {
  color: #10b981;
}

.no-filters {
  color: var(--text-muted);
  font-size: 14px;
}

/* 传统筛选器样式（保持原有样式） */
.traditional-filters {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 32px;
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

/* 兼容性筛选特定样式 */
.compatibility-panel {
  max-width: 800px;
  margin: 0 auto;
}

.compatibility-hint {
  background: color-mix(in srgb, #10b981 10%, transparent);
  border: 1px solid color-mix(in srgb, #10b981 20%, transparent);
  border-radius: 8px;
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.hint-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.hint-icon {
  width: 20px;
  height: 20px;
  color: #10b981;
  flex-shrink: 0;
}

.import-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.import-btn:hover {
  background: color-mix(in srgb, #10b981 90%, black);
}

.import-btn svg {
  width: 14px;
  height: 14px;
}

.compatibility-filters {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.filter-section {
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  background: var(--bg-secondary);
}

/* 零件搜索 */
.part-search {
  position: relative;
  margin-bottom: 16px;
}

.search-input-wrapper {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: var(--text-muted);
}

.part-search-input {
  width: 100%;
  padding: 10px 12px 10px 36px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  background: var(--bg-card);
  color: var(--text-primary);
  transition: all 0.2s ease;
}

.part-search-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--primary) 10%, transparent);
}

.part-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  box-shadow: var(--shadow-lg);
  z-index: 1000;
  margin-top: 4px;
  max-height: 200px;
  overflow-y: auto;
}

.suggestion-loading {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  color: var(--text-muted);
  font-size: 13px;
}

.part-suggestion-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-bottom: 1px solid var(--border-color);
}

.part-suggestion-item:last-child {
  border-bottom: none;
}

.part-suggestion-item:hover {
  background: var(--bg-secondary);
}

.part-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.part-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.part-category {
  font-size: 12px;
  color: var(--text-muted);
}

.add-part-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: var(--primary);
  color: white;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.add-part-btn:hover {
  background: color-mix(in srgb, var(--primary) 90%, black);
}

.add-part-btn svg {
  width: 12px;
  height: 12px;
}

/* 已选择的零件 */
.selected-parts {
  margin-top: 16px;
}

.selected-parts-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.selected-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.clear-selected-btn {
  padding: 4px 8px;
  font-size: 12px;
  color: #f43f5e;
  background: none;
  border: 1px solid #f43f5e;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-selected-btn:hover {
  background: #f43f5e;
  color: white;
}

.selected-parts-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.selected-part-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: var(--bg-card);
  border: 1px solid color-mix(in srgb, #10b981 20%, transparent);
  border-radius: 6px;
  transition: all 0.2s ease;
}

.selected-part-item:hover {
  border-color: #10b981;
}

.remove-part-btn {
  width: 20px;
  height: 20px;
  border: none;
  background: #f43f5e;
  color: white;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.remove-part-btn:hover {
  background: color-mix(in srgb, #f43f5e 90%, black);
}

.remove-part-btn svg {
  width: 10px;
  height: 10px;
}

/* 空状态 */
.empty-parts-hint {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-muted);
}

.empty-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 16px;
  color: var(--text-muted);
}

.empty-parts-hint p {
  margin: 0 0 8px;
  font-size: 14px;
}

.hint-text {
  font-size: 12px;
  color: var(--text-muted);
}

/* 评分滑块 */
.score-slider {
  margin-top: 8px;
}

.current-value {
  color: #10b981;
  font-weight: 600;
}

.score-range {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: var(--border-color);
  outline: none;
  -webkit-appearance: none;
  appearance: none;
  margin-bottom: 12px;
}

.score-range::-webkit-slider-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #10b981;
  cursor: pointer;
  -webkit-appearance: none;
  appearance: none;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.score-range::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #10b981;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.score-labels {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 16px;
}

.score-label.low { color: #f43f5e; }
.score-label.medium { color: #f59e0b; }
.score-label.high { color: #10b981; }

.score-grades {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.grade-indicator {
  text-align: center;
  padding: 8px 4px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  transition: all 0.2s ease;
}

.grade-indicator.active {
  border-color: #10b981;
  background: color-mix(in srgb, #10b981 10%, transparent);
}

.grade-text {
  display: block;
  font-size: 11px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.grade-range {
  display: block;
  font-size: 10px;
  color: var(--text-muted);
}

/* 兼容性设置说明 */
.settings-help {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: var(--bg-card);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.help-item {
  font-size: 12px;
  line-height: 1.4;
}

.help-item strong {
  color: var(--text-primary);
  margin-right: 4px;
}

.help-item span {
  color: var(--text-secondary);
}

/* 传统筛选样式（保持原有样式） */
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

.selected-categories {
  margin-top: 8px;
  padding: 8px;
  background: var(--bg-secondary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
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

/* 最近使用的筛选 */
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

/* 响应式设计 */
@media (max-width: 1024px) {
  .traditional-filters {
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
  
  .tab-panel {
    padding: 16px;
  }
  
  .traditional-filters {
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
  
  .tabs-navigation {
    flex-direction: row;
  }
  
  .tab-btn {
    padding: 12px 16px;
    font-size: 13px;
  }
  
  .tab-icon {
    width: 14px;
    height: 14px;
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
  
  .target-categories {
    justify-content: center;
  }
  
  .score-grades {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .filter-section {
    padding: 16px;
  }
}
</style>