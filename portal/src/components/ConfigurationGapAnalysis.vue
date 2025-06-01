<!-- src/components/ConfigurationGapAnalysis.vue -->
<template>
  <div class="configuration-gap-analysis">
    <!-- 分析概览 -->
    <div class="analysis-overview">
      <div class="overview-header">
        <h3 class="overview-title">配置缺失分析</h3>
        <div class="analysis-status" :class="analysisStatus.type">
          <div class="status-icon">
            <svg v-if="analysisStatus.type === 'complete'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <svg v-else-if="analysisStatus.type === 'partial'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <svg v-else fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <span class="status-text">{{ analysisStatus.text }}</span>
        </div>
      </div>
      
      <div class="overview-stats">
        <div class="stat-item">
          <div class="stat-number">{{ currentParts.length }}</div>
          <div class="stat-label">当前零件</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ detectedPatterns.length }}</div>
          <div class="stat-label">匹配模式</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ missingCategories.length }}</div>
          <div class="stat-label">缺失类别</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ recommendations.length }}</div>
          <div class="stat-label">推荐零件</div>
        </div>
      </div>
    </div>

    <!-- 配置模式识别 -->
    <div v-if="detectedPatterns.length > 0" class="detected-patterns">
      <h4 class="section-title">识别的配置模式</h4>
      <div class="patterns-grid">
        <div 
          v-for="pattern in detectedPatterns" 
          :key="pattern.id"
          class="pattern-card"
          :class="{ complete: pattern.completeness >= 80, partial: pattern.completeness >= 40 }"
        >
          <div class="pattern-header">
            <div class="pattern-info">
              <h5 class="pattern-name">{{ pattern.name }}</h5>
              <p class="pattern-description">{{ pattern.description }}</p>
            </div>
            <div class="pattern-progress">
              <div class="progress-circle">
                <svg width="60" height="60" viewBox="0 0 60 60">
                  <circle
                    cx="30"
                    cy="30"
                    r="25"
                    fill="none"
                    stroke="var(--bg-secondary)"
                    stroke-width="4"
                  />
                  <circle
                    cx="30"
                    cy="30"
                    r="25"
                    fill="none"
                    :stroke="getCompletenessColor(pattern.completeness)"
                    stroke-width="4"
                    stroke-linecap="round"
                    :stroke-dasharray="circumference"
                    :stroke-dashoffset="getStrokeDashoffset(pattern.completeness)"
                    transform="rotate(-90 30 30)"
                  />
                </svg>
                <div class="progress-text">
                  <span class="progress-number">{{ Math.round(pattern.completeness) }}</span>
                  <span class="progress-percent">%</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="pattern-components">
            <h6 class="components-title">必需组件:</h6>
            <div class="components-list">
              <div 
                v-for="component in pattern.requiredComponents" 
                :key="component.category"
                class="component-item"
                :class="{ 
                  satisfied: component.satisfied, 
                  missing: !component.satisfied,
                  optional: component.optional 
                }"
              >
                <div class="component-status">
                  <svg v-if="component.satisfied" class="status-icon satisfied" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <svg v-else class="status-icon missing" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
                <span class="component-name">{{ component.name }}</span>
                <span v-if="component.optional" class="optional-badge">可选</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 缺失类别分析 -->
    <div v-if="missingCategories.length > 0" class="missing-categories">
      <h4 class="section-title">缺失的关键类别</h4>
      <div class="categories-grid">
        <div 
          v-for="category in missingCategories" 
          :key="category.name"
          class="category-card"
          :class="category.priority"
        >
          <div class="category-header">
            <div class="category-icon" :class="category.priority">
              <svg v-if="category.priority === 'high'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              <svg v-else-if="category.priority === 'medium'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <svg v-else fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="category-info">
              <h5 class="category-name">{{ category.name }}</h5>
              <p class="category-reason">{{ category.reason }}</p>
            </div>
            <div class="priority-badge" :class="category.priority">
              {{ getPriorityText(category.priority) }}
            </div>
          </div>
          
          <div v-if="category.suggestions?.length > 0" class="category-suggestions">
            <div class="suggestions-header">
              <span class="suggestions-title">推荐零件:</span>
              <button 
                @click="loadSuggestions(category)"
                class="load-suggestions-btn"
                :disabled="loadingSuggestions[category.name]"
              >
                <svg v-if="loadingSuggestions[category.name]" class="loading-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <svg v-else class="refresh-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                更新
              </button>
            </div>
            <div class="suggestions-list">
              <div 
                v-for="suggestion in category.suggestions.slice(0, 3)" 
                :key="suggestion.id"
                class="suggestion-item"
              >
                <div class="suggestion-info">
                  <span class="suggestion-name">{{ suggestion.name }}</span>
                  <span class="suggestion-category">{{ suggestion.category }}</span>
                </div>
                <div class="suggestion-actions">
                  <button 
                    @click="addRecommendedPart(suggestion)"
                    class="add-suggestion-btn"
                    :disabled="isPartAlreadySelected(suggestion.id)"
                  >
                    <svg v-if="isPartAlreadySelected(suggestion.id)" class="check-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <svg v-else class="add-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    {{ isPartAlreadySelected(suggestion.id) ? '已添加' : '添加' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 智能推荐 -->
    <div v-if="recommendations.length > 0" class="smart-recommendations">
      <div class="recommendations-header">
        <h4 class="section-title">智能推荐</h4>
        <div class="recommendations-actions">
          <button 
            @click="refreshRecommendations"
            class="refresh-btn"
            :disabled="loadingRecommendations"
          >
            <svg class="refresh-icon" :class="{ spinning: loadingRecommendations }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            刷新推荐
          </button>
          <button 
            v-if="recommendations.length > 3"
            @click="addAllRecommended"
            class="add-all-btn"
          >
            <svg class="add-all-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            添加全部推荐
          </button>
        </div>
      </div>
      
      <div class="recommendations-grid">
        <div 
          v-for="recommendation in recommendations.slice(0, 6)" 
          :key="recommendation.part_id"
          class="recommendation-card"
        >
          <div class="recommendation-header">
            <div class="recommendation-image">
              <img 
                v-if="recommendation.image_url" 
                :src="recommendation.image_url" 
                :alt="recommendation.part_name"
                @error="handleImageError"
              />
              <div v-else class="image-placeholder">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
            </div>
            
            <div class="recommendation-info">
              <h5 class="recommendation-name">{{ recommendation.part_name }}</h5>
              <p class="recommendation-category">{{ recommendation.part_category }}</p>
              <div class="compatibility-info">
                <span class="compatibility-score" :style="{ color: getGradeColor(recommendation.compatibility_grade) }">
                  {{ recommendation.compatibility_score }}分
                </span>
                <span class="compatibility-grade">{{ getGradeText(recommendation.compatibility_grade) }}</span>
              </div>
            </div>
          </div>
          
          <div class="recommendation-reasons">
            <h6 class="reasons-title">推荐理由:</h6>
            <ul class="reasons-list">
              <li v-for="reason in recommendation.reasons.slice(0, 2)" :key="reason" class="reason-item">
                {{ reason }}
              </li>
            </ul>
          </div>
          
          <div class="recommendation-actions">
            <button 
              @click="addRecommendedPart(recommendation)"
              class="add-recommendation-btn"
              :disabled="isPartAlreadySelected(recommendation.part_id)"
            >
              <svg v-if="isPartAlreadySelected(recommendation.part_id)" class="check-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <svg v-else class="add-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              {{ isPartAlreadySelected(recommendation.part_id) ? '已添加' : '添加到检查' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 无推荐时的提示 -->
    <div v-if="currentParts.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      </div>
      <h4 class="empty-title">开始配置分析</h4>
      <p class="empty-description">添加零件后，系统将自动分析配置完整性并提供优化建议</p>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { compatibilityAPI, compatibilityHelpers } from '../utils/api'

export default {
  name: 'ConfigurationGapAnalysis',
  props: {
    currentParts: {
      type: Array,
      default: () => []
    }
  },
  emits: ['part-added'],
  setup(props, { emit }) {
    // 响应式数据
    const detectedPatterns = ref([])
    const missingCategories = ref([])
    const recommendations = ref([])
    const loadingRecommendations = ref(false)
    const loadingSuggestions = ref({})
    
    // 配置模式库
    const configurationPatterns = [
      {
        id: 'computer_build',
        name: '计算机配置',
        description: '完整的计算机硬件配置',
        requiredComponents: [
          { category: 'CPU', name: '处理器', optional: false },
          { category: '主板', name: '主板', optional: false },
          { category: '内存', name: '内存条', optional: false },
          { category: '存储', name: '存储设备', optional: false },
          { category: '电源', name: '电源供应器', optional: false },
          { category: '显卡', name: '显卡', optional: true },
          { category: '散热器', name: 'CPU散热器', optional: true },
          { category: '机箱', name: '机箱', optional: true }
        ],
        priority: 'high'
      },
      {
        id: 'arduino_project',
        name: 'Arduino项目',
        description: '基础Arduino开发项目配置',
        requiredComponents: [
          { category: '开发板', name: 'Arduino开发板', optional: false },
          { category: '面包板', name: '实验面包板', optional: false },
          { category: '跳线', name: '连接线', optional: false },
          { category: '电阻', name: '电阻器', optional: false },
          { category: '传感器', name: '传感器模块', optional: true },
          { category: 'LED', name: 'LED指示灯', optional: true },
          { category: '电源模块', name: '电源模块', optional: true }
        ],
        priority: 'medium'
      },
      {
        id: 'power_system',
        name: '电源系统',
        description: '稳定的电源供应系统',
        requiredComponents: [
          { category: '电源', name: '主电源', optional: false },
          { category: '电容', name: '滤波电容', optional: false },
          { category: '电感', name: '电感器', optional: true },
          { category: '保险丝', name: '保护电路', optional: false },
          { category: '稳压器', name: '电压稳压器', optional: true },
          { category: '散热片', name: '散热组件', optional: true }
        ],
        priority: 'high'
      },
      {
        id: 'iot_device',
        name: '物联网设备',
        description: '连网智能设备配置',
        requiredComponents: [
          { category: '微控制器', name: '主控芯片', optional: false },
          { category: '无线模块', name: '通信模块', optional: false },
          { category: '传感器', name: '数据采集传感器', optional: false },
          { category: '电源管理', name: '电源管理模块', optional: false },
          { category: '存储', name: '数据存储', optional: true },
          { category: '显示屏', name: '显示模块', optional: true },
          { category: '外壳', name: '保护外壳', optional: true }
        ],
        priority: 'medium'
      }
    ]
    
    // 计算属性
    const circumference = 2 * Math.PI * 25 // r=25
    
    const analysisStatus = computed(() => {
      if (props.currentParts.length === 0) {
        return { type: 'empty', text: '等待添加零件' }
      }
      
      const totalPatterns = detectedPatterns.value.length
      const completePatterns = detectedPatterns.value.filter(p => p.completeness >= 80).length
      const partialPatterns = detectedPatterns.value.filter(p => p.completeness >= 40 && p.completeness < 80).length
      
      if (completePatterns > 0) {
        return { type: 'complete', text: `${completePatterns}个配置完整` }
      } else if (partialPatterns > 0) {
        return { type: 'partial', text: `${partialPatterns}个配置部分完整` }
      } else if (totalPatterns > 0) {
        return { type: 'incomplete', text: '配置不完整，需要添加更多零件' }
      } else {
        return { type: 'unknown', text: '未识别到标准配置模式' }
      }
    })
    
    // 工具方法
    const getCompletenessColor = (completeness) => {
      if (completeness >= 80) return '#10b981'
      if (completeness >= 60) return '#f59e0b'
      if (completeness >= 40) return '#f97316'
      return '#f43f5e'
    }
    
    const getStrokeDashoffset = (completeness) => {
      const progress = completeness / 100
      return circumference * (1 - progress)
    }
    
    const getPriorityText = (priority) => {
      const priorityMap = {
        'high': '高优先级',
        'medium': '中优先级',
        'low': '低优先级'
      }
      return priorityMap[priority] || priority
    }
    
    const getGradeColor = (grade) => compatibilityHelpers.getGradeColor(grade)
    const getGradeText = (grade) => compatibilityHelpers.formatGrade(grade).text
    
    const handleImageError = (event) => {
      event.target.style.display = 'none'
    }
    
    const isPartAlreadySelected = (partId) => {
      return props.currentParts.some(part => part.id === partId)
    }
    
    // 分析方法
    const analyzeConfiguration = () => {
      if (props.currentParts.length === 0) {
        detectedPatterns.value = []
        missingCategories.value = []
        return
      }
      
      const currentCategories = new Set(props.currentParts.map(part => part.category).filter(Boolean))
      const patterns = []
      
      // 分析每个配置模式
      configurationPatterns.forEach(pattern => {
        const requiredComponents = pattern.requiredComponents.filter(comp => !comp.optional)
        const optionalComponents = pattern.requiredComponents.filter(comp => comp.optional)
        
        const satisfiedRequired = requiredComponents.filter(comp => 
          currentCategories.has(comp.category)
        )
        const satisfiedOptional = optionalComponents.filter(comp => 
          currentCategories.has(comp.category)
        )
        
        // 计算完整度
        const requiredWeight = 0.8
        const optionalWeight = 0.2
        const requiredCompleteness = (satisfiedRequired.length / requiredComponents.length) * requiredWeight
        const optionalCompleteness = (satisfiedOptional.length / optionalComponents.length) * optionalWeight
        const totalCompleteness = (requiredCompleteness + optionalCompleteness) * 100
        
        // 只显示有一定匹配度的模式
        if (satisfiedRequired.length > 0 || totalCompleteness > 20) {
          patterns.push({
            ...pattern,
            completeness: Math.round(totalCompleteness),
            satisfiedRequired: satisfiedRequired.length,
            totalRequired: requiredComponents.length,
            satisfiedOptional: satisfiedOptional.length,
            totalOptional: optionalComponents.length,
            requiredComponents: pattern.requiredComponents.map(comp => ({
              ...comp,
              satisfied: currentCategories.has(comp.category)
            }))
          })
        }
      })
      
      // 按完整度排序
      detectedPatterns.value = patterns.sort((a, b) => b.completeness - a.completeness)
      
      // 分析缺失类别
      analyzeMissingCategories()
    }
    
    const analyzeMissingCategories = () => {
      const missing = []
      const currentCategories = new Set(props.currentParts.map(part => part.category).filter(Boolean))
      
      // 基于检测到的模式分析缺失
      detectedPatterns.value.forEach(pattern => {
        if (pattern.completeness >= 30) { // 只分析有一定匹配度的模式
          pattern.requiredComponents.forEach(comp => {
            if (!comp.satisfied && !comp.optional) {
              const existingMissing = missing.find(m => m.name === comp.category)
              if (!existingMissing) {
                missing.push({
                  name: comp.category,
                  reason: `${pattern.name}配置缺少${comp.name}`,
                  priority: pattern.priority,
                  patterns: [pattern.name],
                  suggestions: []
                })
              } else {
                existingMissing.patterns.push(pattern.name)
                if (pattern.priority === 'high' && existingMissing.priority !== 'high') {
                  existingMissing.priority = 'high'
                }
              }
            }
          })
        }
      })
      
      // 通用缺失分析
      if (props.currentParts.length > 0) {
        const commonMissing = analyzeCommonMissing(currentCategories)
        commonMissing.forEach(item => {
          const existing = missing.find(m => m.name === item.name)
          if (!existing) {
            missing.push(item)
          }
        })
      }
      
      // 按优先级排序
      const priorityOrder = { 'high': 3, 'medium': 2, 'low': 1 }
      missingCategories.value = missing.sort((a, b) => 
        priorityOrder[b.priority] - priorityOrder[a.priority]
      )
    }
    
    const analyzeCommonMissing = (currentCategories) => {
      const missing = []
      
      // 检查常见的缺失模式
      if (currentCategories.has('CPU') && !currentCategories.has('主板')) {
        missing.push({
          name: '主板',
          reason: '有CPU但缺少主板',
          priority: 'high',
          patterns: ['通用'],
          suggestions: []
        })
      }
      
      if (currentCategories.has('主板') && !currentCategories.has('内存')) {
        missing.push({
          name: '内存',
          reason: '有主板但缺少内存',
          priority: 'high',
          patterns: ['通用'],
          suggestions: []
        })
      }
      
      if ((currentCategories.has('CPU') || currentCategories.has('主板')) && !currentCategories.has('电源')) {
        missing.push({
          name: '电源',
          reason: '系统缺少电源供应',
          priority: 'high',
          patterns: ['通用'],
          suggestions: []
        })
      }
      
      if (currentCategories.has('开发板') && !currentCategories.has('面包板')) {
        missing.push({
          name: '面包板',
          reason: '开发项目通常需要实验面包板',
          priority: 'medium',
          patterns: ['通用'],
          suggestions: []
        })
      }
      
      return missing
    }
    
    // 推荐方法
    const loadRecommendations = async () => {
      if (props.currentParts.length === 0) {
        recommendations.value = []
        return
      }
      
      loadingRecommendations.value = true
      
      try {
        const partIds = props.currentParts.map(part => part.id)
        const response = await compatibilityAPI.search({
          selected_parts: partIds,
          target_categories: missingCategories.value.map(cat => cat.name),
          min_compatibility_score: 50,
          limit: 10,
          include_theoretical: true
        })
        
        recommendations.value = response.matches || []
        
      } catch (error) {
        console.error('加载推荐失败:', error)
        recommendations.value = []
      }
      
      loadingRecommendations.value = false
    }
    
    const loadSuggestions = async (category) => {
      loadingSuggestions.value[category.name] = true
      
      try {
        // 为每个当前零件获取建议
        const allSuggestions = []
        
        for (const part of props.currentParts.slice(0, 3)) { // 限制查询数量
          try {
            const suggestions = await compatibilityAPI.suggestions(part.id, {
              categories: category.name,
              limit: 3,
              min_score: 60
            })
            allSuggestions.push(...suggestions)
          } catch (error) {
            console.warn(`获取零件${part.id}的建议失败:`, error)
          }
        }
        
        // 去重并限制数量
        const uniqueSuggestions = allSuggestions.filter((suggestion, index, self) => 
          index === self.findIndex(s => s.id === suggestion.id)
        ).slice(0, 5)
        
        category.suggestions = uniqueSuggestions
        
      } catch (error) {
        console.error('加载建议失败:', error)
        category.suggestions = []
      }
      
      loadingSuggestions.value[category.name] = false
    }
    
    const refreshRecommendations = () => {
      loadRecommendations()
    }
    
    // 添加零件方法
    const addRecommendedPart = (partOrRecommendation) => {
      // 标准化零件数据
      const part = {
        id: partOrRecommendation.part_id || partOrRecommendation.id,
        name: partOrRecommendation.part_name || partOrRecommendation.name,
        category: partOrRecommendation.part_category || partOrRecommendation.category,
        image_url: partOrRecommendation.image_url,
        description: partOrRecommendation.description
      }
      
      if (!isPartAlreadySelected(part.id)) {
        emit('part-added', part)
      }
    }
    
    const addAllRecommended = () => {
      const availableRecommendations = recommendations.value.filter(rec => 
        !isPartAlreadySelected(rec.part_id)
      )
      
      availableRecommendations.slice(0, 3).forEach(rec => {
        addRecommendedPart(rec)
      })
    }
    
    // 监听器
    watch(() => props.currentParts, () => {
      analyzeConfiguration()
      if (props.currentParts.length > 0) {
        loadRecommendations()
      }
    }, { deep: true, immediate: true })
    
    // 生命周期
    onMounted(() => {
      analyzeConfiguration()
      if (props.currentParts.length > 0) {
        loadRecommendations()
      }
    })
    
    return {
      detectedPatterns,
      missingCategories,
      recommendations,
      loadingRecommendations,
      loadingSuggestions,
      circumference,
      analysisStatus,
      getCompletenessColor,
      getStrokeDashoffset,
      getPriorityText,
      getGradeColor,
      getGradeText,
      handleImageError,
      isPartAlreadySelected,
      loadSuggestions,
      refreshRecommendations,
      addRecommendedPart,
      addAllRecommended
    }
  }
}
</script>

<style scoped>
.configuration-gap-analysis {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 分析概览 */
.analysis-overview {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.overview-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.analysis-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
}

.analysis-status.complete {
  background: color-mix(in srgb, #10b981 15%, transparent);
  color: #10b981;
}

.analysis-status.partial {
  background: color-mix(in srgb, #f59e0b 15%, transparent);
  color: #f59e0b;
}

.analysis-status.incomplete {
  background: color-mix(in srgb, #f43f5e 15%, transparent);
  color: #f43f5e;
}

.analysis-status.unknown,
.analysis-status.empty {
  background: var(--bg-secondary);
  color: var(--text-muted);
}

.status-icon {
  width: 16px;
  height: 16px;
}

.overview-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 20px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: var(--text-muted);
}

/* 配置模式 */
.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.patterns-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.pattern-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.2s ease;
}

.pattern-card.complete {
  border-left: 4px solid #10b981;
}

.pattern-card.partial {
  border-left: 4px solid #f59e0b;
}

.pattern-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.pattern-info {
  flex: 1;
}

.pattern-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.pattern-description {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
}

.pattern-progress {
  flex-shrink: 0;
}

.progress-circle {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.progress-text {
  position: absolute;
  display: flex;
  align-items: baseline;
  gap: 1px;
}

.progress-number {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.progress-percent {
  font-size: 10px;
  color: var(--text-muted);
}

.pattern-components {
  margin-top: 16px;
}

.components-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.components-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.component-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 6px;
  font-size: 13px;
}

.component-item.satisfied {
  background: color-mix(in srgb, #10b981 10%, transparent);
}

.component-item.missing {
  background: color-mix(in srgb, #f43f5e 10%, transparent);
}

.component-item.optional {
  opacity: 0.7;
}

.component-status {
  flex-shrink: 0;
}

.status-icon {
  width: 14px;
  height: 14px;
}

.status-icon.satisfied {
  color: #10b981;
}

.status-icon.missing {
  color: #f43f5e;
}

.component-name {
  flex: 1;
  color: var(--text-primary);
}

.optional-badge {
  background: var(--text-muted);
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 500;
}

/* 缺失类别 */
.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.category-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
}

.category-card.high {
  border-left: 4px solid #f43f5e;
}

.category-card.medium {
  border-left: 4px solid #f59e0b;
}

.category-card.low {
  border-left: 4px solid #10b981;
}

.category-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.category-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  margin-top: 2px;
}

.category-icon.high {
  color: #f43f5e;
}

.category-icon.medium {
  color: #f59e0b;
}

.category-icon.low {
  color: #10b981;
}

.category-info {
  flex: 1;
}

.category-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.category-reason {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
}

.priority-badge {
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 500;
  flex-shrink: 0;
}

.priority-badge.high {
  background: color-mix(in srgb, #f43f5e 15%, transparent);
  color: #f43f5e;
}

.priority-badge.medium {
  background: color-mix(in srgb, #f59e0b 15%, transparent);
  color: #f59e0b;
}

.priority-badge.low {
  background: color-mix(in srgb, #10b981 15%, transparent);
  color: #10b981;
}

.category-suggestions {
  border-top: 1px solid var(--border-color);
  padding-top: 12px;
}

.suggestions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.suggestions-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.load-suggestions-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  font-size: 11px;
  background: transparent;
  color: var(--primary);
  border: 1px solid var(--primary);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.load-suggestions-btn:hover:not(:disabled) {
  background: var(--primary);
  color: white;
}

.load-suggestions-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-icon {
  width: 12px;
  height: 12px;
  animation: spin 1s linear infinite;
}

.refresh-icon {
  width: 12px;
  height: 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.suggestion-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px;
  background: var(--bg-primary);
  border-radius: 6px;
  font-size: 12px;
}

.suggestion-info {
  flex: 1;
  min-width: 0;
}

.suggestion-name {
  color: var(--text-primary);
  font-weight: 500;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.suggestion-category {
  color: var(--text-muted);
  font-size: 11px;
}

.add-suggestion-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 6px;
  font-size: 10px;
  background: transparent;
  color: var(--primary);
  border: 1px solid var(--primary);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.add-suggestion-btn:hover:not(:disabled) {
  background: var(--primary);
  color: white;
}

.add-suggestion-btn:disabled {
  background: #10b981;
  border-color: #10b981;
  color: white;
  cursor: not-allowed;
}

.add-icon,
.check-icon {
  width: 10px;
  height: 10px;
}

/* 智能推荐 */
.recommendations-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.recommendations-actions {
  display: flex;
  gap: 8px;
}

.refresh-btn,
.add-all-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  font-size: 13px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-card);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.refresh-btn:hover,
.add-all-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-icon.spinning {
  animation: spin 1s linear infinite;
}

.refresh-icon,
.add-all-icon {
  width: 14px;
  height: 14px;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.recommendation-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  transition: all 0.2s ease;
}

.recommendation-card:hover {
  border-color: var(--primary);
  box-shadow: var(--shadow-sm);
}

.recommendation-header {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.recommendation-image {
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

.recommendation-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-placeholder {
  color: var(--text-muted);
}

.image-placeholder svg {
  width: 24px;
  height: 24px;
}

.recommendation-info {
  flex: 1;
  min-width: 0;
}

.recommendation-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin: 0 0 4px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recommendation-category {
  font-size: 12px;
  color: var(--text-muted);
  margin: 0 0 6px 0;
}

.compatibility-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.compatibility-score {
  font-size: 14px;
  font-weight: 600;
}

.compatibility-grade {
  font-size: 11px;
  color: var(--text-muted);
}

.recommendation-reasons {
  margin-bottom: 12px;
}

.reasons-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  margin: 0 0 6px 0;
}

.reasons-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.reason-item {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 3px;
  line-height: 1.3;
}

.reason-item::before {
  content: '•';
  color: var(--primary);
  font-weight: bold;
  display: inline-block;
  width: 1em;
}

.recommendation-actions {
  display: flex;
  justify-content: center;
}

.add-recommendation-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  font-size: 13px;
  background: transparent;
  color: var(--primary);
  border: 1px solid var(--primary);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
  justify-content: center;
}

.add-recommendation-btn:hover:not(:disabled) {
  background: var(--primary);
  color: white;
}

.add-recommendation-btn:disabled {
  background: #10b981;
  border-color: #10b981;
  color: white;
  cursor: not-allowed;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.empty-icon {
  width: 64px;
  height: 64px;
  color: var(--text-muted);
  margin-bottom: 16px;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.empty-description {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  max-width: 400px;
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .patterns-grid {
    grid-template-columns: 1fr;
  }
  
  .recommendations-grid {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  }
  
  .overview-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .configuration-gap-analysis {
    gap: 16px;
  }
  
  .analysis-overview {
    padding: 16px;
  }
  
  .overview-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .overview-stats {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
  
  .pattern-header {
    flex-direction: column;
    gap: 12px;
  }
  
  .categories-grid {
    grid-template-columns: 1fr;
  }
  
  .recommendations-grid {
    grid-template-columns: 1fr;
  }
  
  .recommendations-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .recommendations-actions {
    width: 100%;
    justify-content: flex-end;
  }
}

@media (max-width: 480px) {
  .analysis-overview,
  .pattern-card,
  .category-card,
  .recommendation-card {
    padding: 12px;
  }
  
  .overview-stats {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .stat-number {
    font-size: 20px;
  }
  
  .pattern-name,
  .category-name {
    font-size: 14px;
  }
  
  .recommendations-actions {
    flex-direction: column;
    gap: 8px;
  }
  
  .refresh-btn,
  .add-all-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>