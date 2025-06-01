<!-- portal/src/views/Detail.vue (兼容性功能集成版本) -->
<template>
  <div class="detail-page">
    <!-- 头部导航 -->
    <header class="detail-header">
      <div class="container">
        <div class="detail-nav">
          <button class="back-btn" @click="goBack">
            <svg class="back-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            返回搜索
          </button>
          
          <div class="nav-actions">
            <ThemeToggle />
          </div>
        </div>
      </div>
    </header>
    
    <!-- 详情内容 -->
    <main class="detail-main">
      <div class="container">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>加载中...</p>
        </div>
        
        <!-- 错误状态 -->
        <div v-else-if="error" class="error-container">
          <div class="error-icon">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3>加载失败</h3>
          <p>{{ error }}</p>
          <button class="btn btn-primary" @click="loadPart">
            重试
          </button>
        </div>
        
        <!-- 零件详情 -->
        <div v-else-if="part" class="part-detail">
          <div class="detail-grid">
            <!-- 左侧：图片和基本信息 -->
            <div class="detail-left">
              <div class="part-image-container">
                <div class="image-wrapper" @click="showImageModal = true">
                  <img 
                    v-if="part.image_url && !imageError" 
                    :src="part.image_url" 
                    :alt="part.name"
                    class="part-image"
                    @error="onImageError"
                  />
                  <div v-else class="part-placeholder">
                    <svg class="placeholder-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                    <p>暂无图片</p>
                  </div>
                  
                  <!-- 放大图标 -->
                  <div v-if="part.image_url && !imageError" class="zoom-overlay">
                    <svg class="zoom-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                    </svg>
                  </div>
                </div>
              </div>

              <!-- 图片放大模态框 -->
              <div 
                v-if="showImageModal" 
                class="image-modal-overlay"
                @click="closeImageModal"
              >
                <div class="image-modal" @click.stop>
                  <button class="modal-close" @click="closeImageModal">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                  
                  <div class="modal-image-container">
                    <img 
                      :src="part.image_url" 
                      :alt="part.name"
                      class="modal-image"
                    />
                  </div>
                  
                  <div class="modal-info">
                    <h3>{{ part.name }}</h3>
                    <p v-if="part.category">{{ part.category }}</p>
                  </div>
                </div>
              </div>
              
              <!-- 操作按钮 -->
              <div class="action-buttons">
                <button 
                  class="btn btn-primary"
                  :class="{ active: isFavorited }"
                  @click="toggleFavorite"
                >
                  <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path 
                      stroke-linecap="round" 
                      stroke-linejoin="round" 
                      stroke-width="2" 
                      :d="isFavorited ? 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z' : 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z'"
                      :fill="isFavorited ? 'currentColor' : 'none'"
                    />
                  </svg>
                  {{ isFavorited ? '已收藏' : '收藏零件' }}
                </button>
                
                <button 
                  class="btn"
                  :class="isInComparison ? 'btn-secondary' : 'btn-outline'"
                  @click="toggleComparison"
                >
                  <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  {{ isInComparison ? '从对比中移除' : '添加到对比' }}
                  <span v-if="comparisonCount > 0" class="comparison-count">({{ comparisonCount }})</span>
                </button>

                <!-- 新增：兼容性检查按钮 -->
                <button 
                  class="btn"
                  :class="isInCompatibilityCheck ? 'btn-compatibility-active' : 'btn-compatibility'"
                  @click="toggleCompatibilityCheck"
                >
                  <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {{ isInCompatibilityCheck ? '从兼容性检查中移除' : '加入兼容性检查' }}
                  <span v-if="compatibilityCheckCount > 0" class="compatibility-count">({{ compatibilityCheckCount }})</span>
                </button>
                
                <!-- 对比建议按钮 -->
                <button 
                  v-if="comparisonSuggestions.length > 0"
                  class="btn btn-outline"
                  @click="showSuggestions = !showSuggestions"
                >
                  <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  智能对比建议
                </button>

                <!-- 新增：兼容性检查CTA按钮 -->
                <button 
                  v-if="compatibilityCheckCount >= 2"
                  class="btn btn-compatibility-cta"
                  @click="goToCompatibilityCheck"
                >
                  <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  兼容性检查 ({{ compatibilityCheckCount }}个零件)
                </button>
                
                <!-- 立即对比按钮 -->
                <button 
                  v-if="comparisonCount >= 2"
                  class="btn btn-primary comparison-cta"
                  @click="goToComparison"
                >
                  <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  立即对比 ({{ comparisonCount }}个零件)
                </button>
              </div>

              <!-- 新增：快速兼容性检查组件 -->
              <div v-if="showQuickCompatibilityCheck && compatibilityCheckCount > 0" class="quick-compatibility-check">
                <h4>快速兼容性检查</h4>
                <p class="quick-check-desc">与兼容性检查列表中的零件进行快速检查：</p>
                
                <div class="quick-check-results">
                  <template v-for="checkPart in filteredCompatibilityCheckList" :key="checkPart.id">
                    <div class="quick-check-item">
                      <div class="check-part-info">
                        <div class="check-part-image">
                          <img 
                            v-if="checkPart.image_url" 
                            :src="checkPart.image_url" 
                            :alt="checkPart.name"
                          />
                          <div v-else class="check-part-placeholder">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                            </svg>
                          </div>
                        </div>
                        <div class="check-part-details">
                          <span class="check-part-name">{{ checkPart.name }}</span>
                          <span v-if="checkPart.category" class="check-part-category">{{ checkPart.category }}</span>
                        </div>
                      </div>
                      
                      <div class="compatibility-result" v-if="quickCheckResults[checkPart.id]">
                        <div 
                          class="compatibility-badge"
                          :class="quickCheckResults[checkPart.id].grade"
                        >
                          <span class="grade-icon">{{ getGradeIcon(quickCheckResults[checkPart.id].grade) }}</span>
                          <span class="grade-text">{{ getGradeText(quickCheckResults[checkPart.id].grade) }}</span>
                          <span class="grade-score">{{ quickCheckResults[checkPart.id].score }}分</span>
                        </div>
                      </div>
                      
                      <div class="compatibility-result" v-else-if="quickCheckLoading[checkPart.id]">
                        <div class="loading-badge">
                          <div class="mini-spinner"></div>
                          <span>检查中...</span>
                        </div>
                      </div>
                      
                      <button 
                        v-else
                        class="quick-check-btn"
                        @click="performQuickCheck(checkPart.id)"
                      >
                        检查兼容性
                      </button>
                    </div>
                  </template>
                </div>
                
                <div class="quick-check-actions">
                  <button class="btn btn-outline btn-sm" @click="checkAllCompatibility">
                    <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    检查全部
                  </button>
                  <button class="btn btn-outline btn-sm" @click="showQuickCompatibilityCheck = false">
                    收起
                  </button>
                </div>
              </div>
              
              <!-- 对比建议面板 -->
              <div v-if="showSuggestions && comparisonSuggestions.length > 0" class="comparison-suggestions">
                <h4>对比建议</h4>
                <p class="suggestions-desc">基于当前零件为您推荐相似的零件进行对比：</p>
                
                <div class="suggestions-grid">
                  <div 
                    v-for="suggestion in comparisonSuggestions" 
                    :key="suggestion.id"
                    class="suggestion-card"
                    @click="addToComparisonAndGo(suggestion)"
                  >
                    <div class="suggestion-image">
                      <img 
                        v-if="suggestion.image_url" 
                        :src="suggestion.image_url" 
                        :alt="suggestion.name"
                      />
                      <div v-else class="suggestion-placeholder">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                        </svg>
                      </div>
                    </div>
                    <div class="suggestion-info">
                      <h5>{{ suggestion.name }}</h5>
                      <span v-if="suggestion.category">{{ suggestion.category }}</span>
                    </div>
                    <button class="suggestion-add-btn">
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>

              <!-- 新增：兼容零件推荐区域 -->
              <div v-if="showCompatibilityRecommendations" class="compatibility-recommendations">
                <h4>兼容零件推荐</h4>
                <p class="recommendations-desc">为当前零件推荐兼容的其他零件：</p>
                
                <div class="recommendations-loading" v-if="loadingRecommendations">
                  <div class="loading-spinner-sm"></div>
                  <span>正在获取推荐...</span>
                </div>
                
                <div v-else-if="compatibilityRecommendations.length > 0" class="recommendations-grid">
                  <div 
                    v-for="recommendation in compatibilityRecommendations" 
                    :key="recommendation.id"
                    class="recommendation-card"
                  >
                    <div class="recommendation-image">
                      <img 
                        v-if="recommendation.image_url" 
                        :src="recommendation.image_url" 
                        :alt="recommendation.name"
                      />
                      <div v-else class="recommendation-placeholder">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                        </svg>
                      </div>
                    </div>
                    
                    <div class="recommendation-info">
                      <h5>{{ recommendation.name }}</h5>
                      <span v-if="recommendation.category" class="recommendation-category">
                        {{ recommendation.category }}
                      </span>
                      
                      <div class="compatibility-info">
                        <div 
                          class="compatibility-grade-badge"
                          :class="recommendation.compatibility_grade || 'theoretical'"
                        >
                          <span class="grade-icon">{{ getGradeIcon(recommendation.compatibility_grade || 'theoretical') }}</span>
                          <span class="grade-text">{{ getGradeText(recommendation.compatibility_grade || 'theoretical') }}</span>
                          <span class="grade-score">{{ recommendation.compatibility_score || 60 }}分</span>
                        </div>
                        
                        <div v-if="recommendation.reasons && recommendation.reasons.length > 0" class="compatibility-reasons">
                          <small>{{ recommendation.reasons[0] }}</small>
                        </div>
                      </div>
                    </div>
                    
                    <div class="recommendation-actions">
                      <button 
                        class="btn btn-outline btn-sm"
                        @click="viewPartDetail(recommendation.id)"
                      >
                        查看详情
                      </button>
                      <button 
                        class="btn btn-compatibility btn-sm"
                        @click="addToCompatibilityCheck(recommendation)"
                      >
                        加入检查
                      </button>
                    </div>
                  </div>
                </div>
                
                <div v-else class="no-recommendations">
                  <p>暂无兼容零件推荐</p>
                  <small>可能是零件信息不足或者分类较为特殊</small>
                </div>
              </div>
            </div>
            
            <!-- 右侧：详细信息 -->
            <div class="detail-right">
              <div class="part-info">
                <div class="part-header">
                  <h1 class="part-name">{{ part.name }}</h1>
                  <span v-if="part.category" class="part-category">{{ part.category }}</span>
                </div>
                
                <p v-if="part.description" class="part-description">
                  {{ part.description }}
                </p>

                <!-- 新增：兼容性功能快捷入口 -->
                <div class="compatibility-shortcuts">
                  <button 
                    v-if="!showQuickCompatibilityCheck && compatibilityCheckCount > 0"
                    class="compatibility-shortcut-btn"
                    @click="showQuickCompatibilityCheck = true"
                  >
                    <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    快速兼容性检查
                  </button>
                  
                  <button 
                    v-if="!showCompatibilityRecommendations"
                    class="compatibility-shortcut-btn"
                    @click="loadCompatibilityRecommendations"
                  >
                    <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                    兼容零件推荐
                  </button>
                </div>
                
                <!-- 详细参数 -->
                <div v-if="part.properties && Object.keys(part.properties).length > 0" class="part-specifications">
                  <h3 class="spec-title">详细参数</h3>
                  <div class="spec-grid">
                    <div 
                      v-for="[key, value] in Object.entries(part.properties)" 
                      :key="key"
                      class="spec-item"
                    >
                      <div class="spec-key">{{ key }}</div>
                      <div class="spec-value">{{ value }}</div>
                    </div>
                  </div>
                </div>
                
                <!-- 元数据 -->
                <div class="part-metadata">
                  <h3 class="meta-title">其他信息</h3>
                  <div class="meta-grid">
                    <div class="meta-item">
                      <div class="meta-key">零件ID</div>
                      <div class="meta-value">#{{ part.id }}</div>
                    </div>
                    <div class="meta-item">
                      <div class="meta-key">创建时间</div>
                      <div class="meta-value">{{ formatDate(part.created_at) }}</div>
                    </div>
                    <div v-if="part.updated_at" class="meta-item">
                      <div class="meta-key">更新时间</div>
                      <div class="meta-value">{{ formatDate(part.updated_at) }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ThemeToggle from '../components/ThemeToggle.vue'
import { partsAPI, favoritesManager, comparisonManager, compatibilityAPI, compatibilityHelpers } from '../utils/api'
// 新增：导入兼容性检查管理器
import { compatibilityCheckManager } from '../utils/compatibilityManager'

export default {
  name: 'Detail',
  components: {
    ThemeToggle
  },
  props: {
    id: {
      type: [String, Number],
      required: true
    }
  },
  setup(props) {
    const route = useRoute()
    const router = useRouter()
    
    const part = ref(null)
    const loading = ref(false)
    const error = ref('')
    const imageError = ref(false)
    
    // 原有状态
    const isFavorited = ref(false)
    const isInComparison = ref(false)
    const comparisonCount = ref(0)
    const comparisonSuggestions = ref([])
    const showSuggestions = ref(false)
    const showImageModal = ref(false)

    // 新增：兼容性检查相关状态
    const isInCompatibilityCheck = ref(false)
    const compatibilityCheckCount = ref(0)
    const compatibilityCheckList = ref([])
    const showQuickCompatibilityCheck = ref(false)
    const quickCheckResults = ref({})
    const quickCheckLoading = ref({})

    // 新增：兼容零件推荐相关状态
    const showCompatibilityRecommendations = ref(false)
    const compatibilityRecommendations = ref([])
    const loadingRecommendations = ref(false)

    // 添加计算属性来确保数据响应性
    const filteredCompatibilityCheckList = computed(() => {
      if (!part.value || !compatibilityCheckList.value) return []
      return compatibilityCheckList.value.filter(p => p.id !== part.value.id)
    })
    
    const updateStatus = () => {
      if (part.value) {
        isFavorited.value = favoritesManager.isFavorited(part.value.id)
        isInComparison.value = comparisonManager.isInComparison(part.value.id)
        // 新增：更新兼容性检查状态
        isInCompatibilityCheck.value = compatibilityCheckManager.isInCheck(part.value.id)
      }
      comparisonCount.value = comparisonManager.getComparisonCount()
      // 新增：更新兼容性检查计数和列表
      compatibilityCheckCount.value = compatibilityCheckManager.getCheckCount()
      compatibilityCheckList.value = compatibilityCheckManager.getCheckList()
      
      console.log('状态更新:', {
        compatibilityCheckCount: compatibilityCheckCount.value,
        compatibilityCheckList: compatibilityCheckList.value,
        isInCompatibilityCheck: isInCompatibilityCheck.value
      })
    }
    
    const loadPart = async () => {
      loading.value = true
      error.value = ''
      
      try {
        const response = await partsAPI.getPart(props.id)
        part.value = response.data
        updateStatus()
        
        // 加载对比建议
        loadComparisonSuggestions()
      } catch (err) {
        console.error('加载零件详情失败:', err)
        error.value = '零件不存在或加载失败'
      }
      
      loading.value = false
    }
    
    const loadComparisonSuggestions = async () => {
      try {
        const response = await partsAPI.getComparisonSuggestions(props.id, 4)
        comparisonSuggestions.value = response.data
      } catch (err) {
        console.error('加载对比建议失败:', err)
        comparisonSuggestions.value = []
      }
    }

    // 新增：加载兼容零件推荐
    const loadCompatibilityRecommendations = async () => {
      if (!part.value) return
      
      loadingRecommendations.value = true
      showCompatibilityRecommendations.value = true
      
      try {
        const response = await compatibilityAPI.suggestions(part.value.id, {
          limit: 6,
          min_score: 60,
          categories: null
        })
        
        console.log('兼容性推荐API响应:', response.data) // 调试日志
        
        // 处理API返回的数据
        if (response.data && Array.isArray(response.data)) {
          compatibilityRecommendations.value = response.data.map(item => {
            console.log('处理推荐项:', item) // 调试日志
            return {
              id: item.id,
              name: item.name,
              category: item.category,
              image_url: item.image_url,
              compatibility_grade: 'theoretical', // 默认等级
              compatibility_score: 60, // 默认评分
              reasons: ['推荐零件']
            }
          })
        } else {
          compatibilityRecommendations.value = []
        }
        
        console.log('处理后的推荐列表:', compatibilityRecommendations.value) // 调试日志
      } catch (err) {
        console.error('加载兼容零件推荐失败:', err)
        compatibilityRecommendations.value = []
      }
      
      loadingRecommendations.value = false
    }

    // 新增：快速兼容性检查方法
    const performQuickCheck = async (targetPartId) => {
      if (!part.value) return
      
      console.log('执行快速兼容性检查:', part.value.id, 'vs', targetPartId) // 调试日志
      
      quickCheckLoading.value[targetPartId] = true
      
      try {
        const response = await compatibilityAPI.quickCheck(part.value.id, targetPartId)
        console.log('快速检查API响应:', response.data) // 调试日志
        
        quickCheckResults.value[targetPartId] = {
          compatible: response.data.compatible,
          score: response.data.score,
          grade: response.data.grade,
          warnings: response.data.warnings || []
        }
        
        console.log('快速检查结果已保存:', quickCheckResults.value[targetPartId]) // 调试日志
      } catch (err) {
        console.error('快速兼容性检查失败:', err)
        quickCheckResults.value[targetPartId] = {
          compatible: false,
          score: 0,
          grade: 'incompatible',
          warnings: ['检查失败']
        }
      }
      
      quickCheckLoading.value[targetPartId] = false
    }

    // 新增：检查全部兼容性
    const checkAllCompatibility = async () => {
      if (!part.value || compatibilityCheckList.value.length === 0) return
      
      const otherParts = compatibilityCheckList.value.filter(p => p.id !== part.value.id)
      
      for (const checkPart of otherParts) {
        if (!quickCheckResults.value[checkPart.id] && !quickCheckLoading.value[checkPart.id]) {
          await performQuickCheck(checkPart.id)
        }
      }
    }

    // 新增：获取等级图标和文本
    const getGradeIcon = (grade) => {
      return compatibilityHelpers.getGradeIcon(grade)
    }

    const getGradeText = (grade) => {
      const gradeInfo = compatibilityHelpers.formatGrade(grade)
      return gradeInfo.text
    }
    
    const toggleFavorite = () => {
      if (!part.value) return
      
      const result = favoritesManager.toggleFavorite(part.value)
      if (result.success) {
        updateStatus()
        console.log(result.message)
      } else {
        console.error(result.message)
      }
    }
    
    const toggleComparison = () => {
      if (!part.value) return
      
      let result
      if (isInComparison.value) {
        result = comparisonManager.removeFromComparison(part.value.id)
      } else {
        result = comparisonManager.addToComparison(part.value)
      }
      
      if (result.success) {
        updateStatus()
        console.log(result.message || (isInComparison.value ? '已从对比中移除' : '已添加到对比列表'))
      } else {
        console.error(result.message)
      }
    }

    // 新增：切换兼容性检查状态
    const toggleCompatibilityCheck = () => {
      if (!part.value) return
      
      let result
      if (isInCompatibilityCheck.value) {
        result = compatibilityCheckManager.removeFromCheck(part.value.id)
      } else {
        result = compatibilityCheckManager.addToCheck(part.value)
      }
      
      if (result.success) {
        updateStatus()
        console.log(result.message || (isInCompatibilityCheck.value ? '已从兼容性检查中移除' : '已加入兼容性检查'))
      } else {
        console.error(result.message)
      }
    }

    // 新增：添加零件到兼容性检查
    const addToCompatibilityCheck = (partData) => {
      const result = compatibilityCheckManager.addToCheck(partData)
      if (result.success) {
        updateStatus()
        console.log(`已将 ${partData.part_name || partData.name} 加入兼容性检查`)
      } else {
        console.error(result.message)
      }
    }

    // 新增：跳转到兼容性检查
    const goToCompatibilityCheck = () => {
      const checkUrl = compatibilityCheckManager.getCheckUrl()
      if (checkUrl) {
        router.push(checkUrl)
      }
    }
    
    const goToComparison = () => {
      const compareUrl = comparisonManager.getComparisonUrl()
      if (compareUrl) {
        router.push(compareUrl)
      }
    }
    
    const addToComparisonAndGo = (suggestion) => {
      // 添加当前零件到对比（如果还没有）
      if (!isInComparison.value) {
        comparisonManager.addToComparison(part.value)
      }
      
      // 添加建议的零件到对比
      const result = comparisonManager.addToComparison(suggestion)
      
      if (result.success) {
        // 直接跳转到对比页面
        const compareUrl = comparisonManager.getComparisonUrl()
        if (compareUrl) {
          router.push(compareUrl)
        }
      } else {
        console.error(result.message)
      }
    }
    
    const goBack = () => {
      if (window.history.length > 2) {
        router.go(-1)
      } else {
        router.push('/')
      }
    }
    
    const onImageError = () => {
      imageError.value = true
    }
    
    const closeImageModal = (event) => {
      showImageModal.value = false
    }

    const viewPartDetail = (partId) => {
      router.push(`/part/${partId}`)
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleString('zh-CN')
    }
    
    // 键盘事件监听
    const handleKeydown = (event) => {
      if (event.key === 'Escape' && showImageModal.value) {
        closeImageModal()
      }
    }
    
    // 监听存储变化，更新状态
    const handleStorageChange = (e) => {
      if (e.key === 'openpart_favorites' || 
          e.key === 'openpart_comparison' || 
          e.key === 'openpart_compatibility_check') {
        updateStatus()
      }
    }
    
    onMounted(() => {
      document.addEventListener('keydown', handleKeydown)
      window.addEventListener('storage', handleStorageChange)
      loadPart()
    })
    
    // 监听路由参数变化
    watch(() => props.id, (newId, oldId) => {
      if (newId !== oldId) {
        console.log('路由参数变化:', oldId, '->', newId)
        
        // 重置组件状态
        showQuickCompatibilityCheck.value = false
        showCompatibilityRecommendations.value = false
        quickCheckResults.value = {}
        quickCheckLoading.value = {}
        compatibilityRecommendations.value = []
        
        // 重新加载零件数据
        loadPart()
      }
    })
    
    onUnmounted(() => {
      document.removeEventListener('keydown', handleKeydown)
      window.removeEventListener('storage', handleStorageChange)
    })
    
    return {
      part,
      loading,
      error,
      imageError,
      isFavorited,
      isInComparison,
      comparisonCount,
      comparisonSuggestions,
      showSuggestions,
      showImageModal,
      // 新增：兼容性检查相关
      isInCompatibilityCheck,
      compatibilityCheckCount,
      compatibilityCheckList,
      filteredCompatibilityCheckList,
      showQuickCompatibilityCheck,
      quickCheckResults,
      quickCheckLoading,
      showCompatibilityRecommendations,
      compatibilityRecommendations,
      loadingRecommendations,
      // 方法
      loadPart,
      toggleFavorite,
      toggleComparison,
      toggleCompatibilityCheck,
      addToCompatibilityCheck,
      goToCompatibilityCheck,
      goToComparison,
      addToComparisonAndGo,
      goBack,
      onImageError,
      closeImageModal,
      viewPartDetail,
      formatDate,
      // 新增：兼容性检查相关方法
      loadCompatibilityRecommendations,
      performQuickCheck,
      checkAllCompatibility,
      getGradeIcon,
      getGradeText
    }
  }
}
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  background: var(--bg-primary);
}

/* 头部导航 */
.detail-header {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  padding: 16px 0;
}

.detail-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: none;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: var(--bg-secondary);
  border-color: var(--primary);
}

.back-icon {
  width: 16px;
  height: 16px;
}

/* 主要内容 */
.detail-main {
  padding: 32px 0;
}

/* 加载和错误状态 */
.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
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

.error-icon {
  width: 64px;
  height: 64px;
  color: var(--text-muted);
  margin-bottom: 16px;
}

/* 零件详情 */
.detail-grid {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 48px;
  align-items: start;
}

.detail-left {
  position: sticky;
  top: 100px;
}

.part-image-container {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 24px;
}

.part-image {
  width: 100%;
  height: 300px;
  object-fit: cover;
}

.part-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: var(--text-muted);
}

.placeholder-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 12px;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.btn.active {
  background: var(--secondary) !important;
  color: white;
  border-color: var(--secondary);
}

.comparison-count {
  margin-left: 4px;
  font-weight: 600;
  color: var(--secondary);
}

.btn.btn-secondary .comparison-count {
  color: white;
}

/* 新增：兼容性相关按钮样式 */
.btn-compatibility {
  background: transparent;
  color: #10b981;
  border: 1px solid #10b981;
}

.btn-compatibility:hover {
  background: #10b981;
  color: white;
}

.btn-compatibility-active {
  background: #10b981 !important;
  color: white;
  border-color: #10b981;
}

.compatibility-count {
  margin-left: 4px;
  font-weight: 600;
  color: #10b981;
}

.btn-compatibility-active .compatibility-count {
  color: white;
}

.btn-compatibility-cta {
  background: linear-gradient(135deg, #10b981, #059669);
  border: none;
  color: white;
  animation: pulse-glow-green 2s infinite;
}

@keyframes pulse-glow-green {
  0%, 100% {
    box-shadow: 0 0 0 rgba(16, 185, 129, 0.7);
  }
  50% {
    box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
  }
}

.comparison-cta {
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  border: none;
  color: white;
  animation: pulse-glow 2s infinite;
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 0 rgba(100, 116, 139, 0.7);
  }
  50% {
    box-shadow: 0 0 20px rgba(100, 116, 139, 0.4);
  }
}

/* 新增：快速兼容性检查面板样式 */
.quick-compatibility-check {
  margin-top: 24px;
  padding: 20px;
  background: var(--bg-card);
  border: 1px solid #10b981;
  border-radius: 12px;
  animation: slideDown 0.3s ease;
}

.quick-compatibility-check h4 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #10b981;
}

.quick-check-desc {
  margin: 0 0 16px 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.quick-check-results {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.quick-check-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.check-part-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.check-part-image {
  width: 40px;
  height: 40px;
  background: var(--bg-card);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
}

.check-part-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.check-part-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.check-part-placeholder svg {
  width: 20px;
  height: 20px;
}

.check-part-details {
  flex: 1;
  min-width: 0;
}

.check-part-name {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.check-part-category {
  font-size: 12px;
  color: var(--text-secondary);
  background: color-mix(in srgb, var(--primary) 10%, transparent);
  padding: 2px 6px;
  border-radius: 3px;
  margin-top: 2px;
  display: inline-block;
}

.compatibility-result {
  flex-shrink: 0;
}

.compatibility-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.compatibility-badge.official_support {
  background: color-mix(in srgb, #10b981 15%, transparent);
  color: #10b981;
}

.compatibility-badge.unofficial_support {
  background: color-mix(in srgb, #3b82f6 15%, transparent);
  color: #3b82f6;
}

.compatibility-badge.theoretical {
  background: color-mix(in srgb, #f59e0b 15%, transparent);
  color: #f59e0b;
}

.compatibility-badge.incompatible {
  background: color-mix(in srgb, #ef4444 15%, transparent);
  color: #ef4444;
}

.loading-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: var(--bg-primary);
  border-radius: 6px;
  font-size: 12px;
  color: var(--text-secondary);
}

.mini-spinner {
  width: 12px;
  height: 12px;
  border: 2px solid var(--border-color);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.quick-check-btn {
  padding: 4px 12px;
  font-size: 12px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quick-check-btn:hover {
  background: #059669;
}

.quick-check-actions {
  display: flex;
  gap: 8px;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

/* 新增：兼容性功能快捷入口样式 */
.compatibility-shortcuts {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.compatibility-shortcut-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--bg-secondary);
  color: #10b981;
  border: 1px solid #10b981;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  font-weight: 500;
}

.compatibility-shortcut-btn:hover {
  background: #10b981;
  color: white;
}

.compatibility-shortcut-btn .btn-icon {
  width: 16px;
  height: 16px;
}

/* 新增：兼容零件推荐样式 */
.compatibility-recommendations {
  margin-top: 24px;
  padding: 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  animation: slideDown 0.3s ease;
}

.compatibility-recommendations h4 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.recommendations-desc {
  margin: 0 0 16px 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.recommendations-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px;
  color: var(--text-secondary);
}

.loading-spinner-sm {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-color);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.recommendation-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  transition: all 0.2s ease;
}

.recommendation-card:hover {
  background: var(--bg-primary);
  border-color: #10b981;
  box-shadow: var(--shadow-md);
}

.recommendation-image {
  width: 60px;
  height: 60px;
  background: var(--bg-card);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  margin-bottom: 12px;
}

.recommendation-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.recommendation-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.recommendation-placeholder svg {
  width: 24px;
  height: 24px;
}

.recommendation-info {
  margin-bottom: 12px;
}

.recommendation-info h5 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.recommendation-category {
  font-size: 12px;
  color: var(--primary);
  background: color-mix(in srgb, var(--primary) 10%, transparent);
  padding: 2px 6px;
  border-radius: 3px;
  margin-bottom: 8px;
  display: inline-block;
}

.compatibility-info {
  margin-bottom: 12px;
}

.compatibility-grade-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  margin-bottom: 4px;
}

.compatibility-grade-badge.official_support {
  background: color-mix(in srgb, #10b981 15%, transparent);
  color: #10b981;
}

.compatibility-grade-badge.unofficial_support {
  background: color-mix(in srgb, #3b82f6 15%, transparent);
  color: #3b82f6;
}

.compatibility-grade-badge.theoretical {
  background: color-mix(in srgb, #f59e0b 15%, transparent);
  color: #f59e0b;
}

.compatibility-grade-badge.incompatible {
  background: color-mix(in srgb, #ef4444 15%, transparent);
  color: #ef4444;
}

.compatibility-reasons {
  font-size: 11px;
  color: var(--text-muted);
  font-style: italic;
}

.recommendation-actions {
  display: flex;
  gap: 8px;
}

.no-recommendations {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-muted);
}

.no-recommendations p {
  margin: 0 0 4px 0;
  font-size: 14px;
}

.no-recommendations small {
  font-size: 12px;
}

/* 对比建议面板 */
.comparison-suggestions {
  margin-top: 24px;
  padding: 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.comparison-suggestions h4 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.suggestions-desc {
  margin: 0 0 16px 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.suggestions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.suggestion-card {
  position: relative;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 12px;
}

.suggestion-card:hover {
  background: var(--bg-primary);
  border-color: var(--primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.suggestion-image {
  width: 40px;
  height: 40px;
  background: var(--bg-card);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
}

.suggestion-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.suggestion-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.suggestion-placeholder svg {
  width: 20px;
  height: 20px;
}

.suggestion-info {
  flex: 1;
  min-width: 0;
}

.suggestion-info h5 {
  margin: 0 0 2px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.suggestion-info span {
  font-size: 12px;
  color: var(--text-secondary);
  background: color-mix(in srgb, var(--primary) 10%, transparent);
  padding: 2px 6px;
  border-radius: 3px;
}

.suggestion-add-btn {
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 50%;
  background: var(--primary);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.suggestion-add-btn:hover {
  background: var(--secondary);
  transform: scale(1.1);
}

.suggestion-add-btn svg {
  width: 12px;
  height: 12px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .action-buttons {
    flex-direction: row;
    flex-wrap: wrap;
  }
  
  .comparison-cta,
  .btn-compatibility-cta {
    flex: 1 1 100%;
  }

  .compatibility-shortcuts {
    flex-direction: column;
  }

  .recommendations-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
  }
  
  .suggestions-grid {
    grid-template-columns: 1fr;
  }
  
  .suggestion-card {
    padding: 10px;
    gap: 10px;
  }
  
  .suggestion-image {
    width: 36px;
    height: 36px;
  }
  
  .comparison-suggestions,
  .quick-compatibility-check,
  .compatibility-recommendations {
    padding: 16px;
    margin-top: 16px;
  }

  .quick-check-item {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .quick-check-actions {
    justify-content: center;
  }

  .recommendation-actions {
    flex-direction: column;
  }
}

.btn-icon {
  width: 16px;
  height: 16px;
}

/* 详细信息 */
.part-info {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 32px;
}

.part-header {
  margin-bottom: 24px;
}

.part-name {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 12px 0;
  line-height: 1.2;
}

.part-category {
  display: inline-block;
  padding: 6px 12px;
  font-size: 14px;
  font-weight: 500;
  color: var(--primary);
  background: color-mix(in srgb, var(--primary) 10%, transparent);
  border-radius: 6px;
}

.part-description {
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0 0 32px 0;
}

.spec-title,
.meta-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--primary);
}

.spec-grid,
.meta-grid {
  display: grid;
  gap: 12px;
}

.spec-item,
.meta-item {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
}

.spec-item:last-child,
.meta-item:last-child {
  border-bottom: none;
}

.spec-key,
.meta-key {
  font-weight: 500;
  color: var(--text-secondary);
}

.spec-value,
.meta-value {
  font-weight: 600;
  color: var(--text-primary);
}

.part-specifications {
  margin-bottom: 32px;
}

.image-wrapper {
  position: relative;
  cursor: pointer;
}

.zoom-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-wrapper:hover .zoom-overlay {
  opacity: 1;
}

.zoom-icon {
  width: 32px;
  height: 32px;
  color: white;
}

/* 模态框样式 */
.image-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  backdrop-filter: blur(8px);
}

.image-modal {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

[data-theme="dark"] .image-modal {
  background: var(--bg-card);
}

.modal-close {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
  transition: background-color 0.2s ease;
}

.modal-close:hover {
  background: rgba(0, 0, 0, 0.7);
}

.modal-close svg {
  width: 16px;
  height: 16px;
}

.modal-image-container {
  display: flex;
  align-items: center;
  justify-content: center;
  max-height: 80vh;
}

.modal-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.modal-info {
  padding: 16px 20px;
  background: var(--bg-card);
  border-top: 1px solid var(--border-color);
}

.modal-info h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  color: var(--text-primary);
}

.modal-info p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .detail-grid {
    grid-template-columns: 1fr;
    gap: 32px;
  }
  
  .detail-left {
    position: static;
    order: 2;
  }
  
  .detail-right {
    order: 1;
  }
  
  .part-image-container {
    margin-bottom: 16px;
  }
  
  .action-buttons {
    flex-direction: row;
  }
}

@media (max-width: 768px) {
  .detail-main {
    padding: 20px 0;
  }
  
  .part-info {
    padding: 20px;
  }
  
  .part-name {
    font-size: 24px;
  }
  
  .part-description {
    font-size: 15px;
  }
  
  .spec-item,
  .meta-item {
    grid-template-columns: 1fr;
    gap: 4px;
  }
  
  .spec-key,
  .meta-key {
    font-size: 13px;
  }
  
  .spec-value,
  .meta-value {
    font-size: 15px;
    font-weight: 500;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .image-modal {
    max-width: 95vw;
    max-height: 95vh;
  }
  
  .modal-image-container {
    max-height: 75vh;
  }
}
</style>