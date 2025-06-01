import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api/public/parts',
  timeout: 10000
})

// 响应拦截器
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API错误:', error)
    return Promise.reject(error)
  }
)

// 防抖函数
export function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

// API方法
export const partsAPI = {
  // 搜索零件
  search(params = {}) {
    return api.get('/search', { params })
  },
  
  // 获取零件列表
  getParts(params = {}) {
    return api.get('/', { params })
  },
  
  // 获取零件详情
  getPart(id) {
    return api.get(`/${id}`)
  },
  
  // 获取搜索建议
  getSuggestions(query) {
    return api.get('/suggestions', { params: { q: query } })
  },
  
  // 获取分类列表
  getCategories() {
    return api.get('/categories/')
  },

  // 新增：对比零件
  compare(partIds) {
    return axios.post('/api/public/compare/compare', partIds)
  },
  
  // 新增：获取对比建议
  getComparisonSuggestions(partId, limit = 5) {
    return axios.get(`/api/public/compare/compare-suggestions/${partId}`, {
      params: { limit }
    })
  }
}

// 新增：对比状态管理
class ComparisonManager {
  constructor() {
    this.storageKey = 'openpart_comparison'
    this.maxItems = 6 // 最多对比6个零件
  }
  
  // 获取对比列表
  getComparisonList() {
    const stored = localStorage.getItem(this.storageKey)
    try {
      const parsed = stored ? JSON.parse(stored) : []
      // 确保返回的是数组
      return Array.isArray(parsed) ? parsed : []
    } catch (error) {
      console.error('解析对比列表失败:', error)
      // 清除损坏的数据
      localStorage.removeItem(this.storageKey)
      return []
    }
  }
  
  // 添加到对比
  addToComparison(part) {
    let list = this.getComparisonList()
    
    // 检查是否已存在（严格检查ID类型）
    const partId = parseInt(part.id)
    const existingIndex = list.findIndex(p => parseInt(p.id) === partId)
    
    if (existingIndex !== -1) {
      return { success: false, message: '该零件已在对比列表中' }
    }
    
    // 检查数量限制
    if (list.length >= this.maxItems) {
      return { success: false, message: `最多只能对比${this.maxItems}个零件` }
    }
    
    // 添加新零件
    const newItem = {
      id: partId,
      name: part.name,
      category: part.category,
      image_url: part.image_url,
      addedAt: Date.now()
    }
    
    list.push(newItem)
    
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(list))
      // 触发存储事件，通知其他组件更新
      window.dispatchEvent(new StorageEvent('storage', {
        key: this.storageKey,
        newValue: JSON.stringify(list),
        storageArea: localStorage
      }))
    } catch (error) {
      console.error('保存对比列表失败:', error)
      return { success: false, message: '保存失败，请重试' }
    }
    
    return { success: true, message: '已添加到对比列表', count: list.length }
  }
  
  // 从对比中移除
  removeFromComparison(partId) {
    let list = this.getComparisonList()
    const targetId = parseInt(partId)
    
    // 过滤掉要移除的零件
    const newList = list.filter(p => parseInt(p.id) !== targetId)
    
    if (newList.length === list.length) {
      return { success: false, message: '零件不在对比列表中' }
    }
    
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(newList))
      // 触发存储事件
      window.dispatchEvent(new StorageEvent('storage', {
        key: this.storageKey,
        newValue: JSON.stringify(newList),
        storageArea: localStorage
      }))
    } catch (error) {
      console.error('保存对比列表失败:', error)
      return { success: false, message: '移除失败，请重试' }
    }
    
    return { success: true, message: '已从对比列表移除', count: newList.length }
  }
  
  // 清空对比列表
  clearComparison() {
    try {
      localStorage.removeItem(this.storageKey)
      // 触发存储事件
      window.dispatchEvent(new StorageEvent('storage', {
        key: this.storageKey,
        newValue: null,
        storageArea: localStorage
      }))
    } catch (error) {
      console.error('清空对比列表失败:', error)
      return { success: false, message: '清空失败，请重试' }
    }
    
    return { success: true, count: 0 }
  }
  
  // 检查零件是否在对比中
  isInComparison(partId) {
    const list = this.getComparisonList()
    const targetId = parseInt(partId)
    return list.some(p => parseInt(p.id) === targetId)
  }
  
  // 获取对比数量
  getComparisonCount() {
    return this.getComparisonList().length
  }
  
  // 获取对比URL
  getComparisonUrl() {
    const list = this.getComparisonList()
    if (list.length < 2) return null
    
    const ids = list.map(p => p.id).join(',')
    return `/compare?ids=${ids}`
  }
}


// 导出对比管理器实例
export const comparisonManager = new ComparisonManager()

// 新增：收藏管理器（基础版本）
class FavoritesManager {
  constructor() {
    this.storageKey = 'openpart_favorites'
    this.maxItems = 100 // 最多收藏100个零件
  }
  
  // 获取收藏列表
  getFavoritesList() {
    const stored = localStorage.getItem(this.storageKey)
    return stored ? JSON.parse(stored) : []
  }
  
  // 添加到收藏
  addToFavorites(part) {
    let list = this.getFavoritesList()
    
    // 检查是否已存在
    if (list.find(p => p.id === part.id)) {
      return { success: false, message: '该零件已在收藏列表中' }
    }
    
    // 检查数量限制
    if (list.length >= this.maxItems) {
      return { success: false, message: `最多只能收藏${this.maxItems}个零件` }
    }
    
    list.unshift({
      id: part.id,
      name: part.name,
      category: part.category,
      image_url: part.image_url,
      description: part.description,
      addedAt: Date.now()
    })
    
    localStorage.setItem(this.storageKey, JSON.stringify(list))
    return { success: true, message: '已添加到收藏夹', count: list.length }
  }
  
  // 从收藏中移除
  removeFromFavorites(partId) {
    let list = this.getFavoritesList()
    const targetId = parseInt(partId)
    const newList = list.filter(p => parseInt(p.id) !== targetId)
    
    if (newList.length === list.length) {
      return { success: false, message: '零件不在收藏夹中' }
    }
    
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(newList))
      // 触发存储事件
      window.dispatchEvent(new StorageEvent('storage', {
        key: this.storageKey,
        newValue: JSON.stringify(newList),
        storageArea: localStorage
      }))
    } catch (error) {
      console.error('保存收藏列表失败:', error)
      return { success: false, message: '移除失败，请重试' }
    }
    
    return { success: true, count: newList.length }
  }
  
  // 检查零件是否已收藏
  isFavorited(partId) {
    const list = this.getFavoritesList()
    const targetId = parseInt(partId)
    return list.some(p => parseInt(p.id) === targetId)
  }
  
  // 切换收藏状态
  toggleFavorite(part) {
    const partId = parseInt(part.id)
    
    if (this.isFavorited(partId)) {
      const result = this.removeFromFavorites(partId)
      return {
        ...result,
        message: result.success ? '已取消收藏' : result.message,
        action: 'remove'
      }
    } else {
      const result = this.addToFavorites(part)
      return {
        ...result,
        message: result.success ? '已添加到收藏夹' : result.message,
        action: 'add'
      }
    }
  }
  
  // 获取收藏数量
  getFavoritesCount() {
    return this.getFavoritesList().length
  }
  
  // 清空收藏
  clearFavorites() {
    localStorage.removeItem(this.storageKey)
    return { success: true, count: 0 }
  }
  
  // 导出收藏列表
  exportFavorites() {
    const list = this.getFavoritesList()
    const dataStr = JSON.stringify(list, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    
    const link = document.createElement('a')
    link.href = URL.createObjectURL(dataBlob)
    link.download = `我的收藏_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    return { success: true, message: '收藏列表已导出' }
  }
  
  // 导入收藏列表
  async importFavorites(file) {
    try {
      const text = await file.text()
      const importedList = JSON.parse(text)
      
      if (!Array.isArray(importedList)) {
        throw new Error('无效的收藏列表格式')
      }
      
      // 验证数据格式
      for (const item of importedList) {
        if (!item.id || !item.name) {
          throw new Error('收藏列表数据格式不正确')
        }
      }
      
      // 合并现有收藏（去重）
      const currentList = this.getFavoritesList()
      const currentIds = new Set(currentList.map(p => p.id))
      
      const newItems = importedList.filter(item => !currentIds.has(item.id))
      const mergedList = [...currentList, ...newItems]
      
      // 检查数量限制
      if (mergedList.length > this.maxItems) {
        throw new Error(`导入后将超过收藏上限(${this.maxItems}个)`)
      }
      
      localStorage.setItem(this.storageKey, JSON.stringify(mergedList))
      
      return { 
        success: true, 
        message: `成功导入${newItems.length}个新收藏`, 
        count: mergedList.length 
      }
      
    } catch (error) {
      return { success: false, message: error.message }
    }
  }
}

// 导出收藏管理器实例
export const favoritesManager = new FavoritesManager()

// 零件缓存管理器
class PartsCacheManager {
  constructor() {
    this.cache = new Map()
  }
  
  // 获取零件信息
  async getPartInfo(partId) {
    if (this.cache.has(partId)) {
      return this.cache.get(partId)
    }
    
    try {
      const response = await partsAPI.getPart(partId)
      const partInfo = response.data
      this.cache.set(partId, partInfo)
      return partInfo
    } catch (error) {
      console.error('获取零件信息失败:', error)
      return { id: partId, name: `零件 #${partId}`, category: '', description: '' }
    }
  }
  
  // 预加载零件信息
  async preloadParts(partIds) {
    const promises = partIds
      .filter(id => !this.cache.has(id))
      .map(id => this.getPartInfo(id))
    
    await Promise.all(promises)
  }
}

// 导出零件缓存管理器实例
export const partsCacheManager = new PartsCacheManager()

export const statsAPI = {
  // 获取实时统计
  async getRealTimeStats() {
    try {
      const [partsResponse, categoriesResponse] = await Promise.all([
        partsAPI.getParts({ limit: 1 }),
        partsAPI.getCategories()
      ])
      
      // 获取总数需要特殊处理，这里简化处理
      const parts = await partsAPI.getParts({ limit: 1000 })
      
      return {
        totalParts: parts.data.length,
        totalCategories: categoriesResponse.data.length,
        searchCount: this.getSearchCount()
      }
    } catch (error) {
      console.error('获取统计数据失败:', error)
      return {
        totalParts: 0,
        totalCategories: 0,
        searchCount: 0
      }
    }
  },
  
  // 获取搜索次数（可以从localStorage或API获取）
  getSearchCount() {
    const count = parseInt(localStorage.getItem('searchCount') || '0')
    return count > 1000 ? `${Math.floor(count/1000)}k+` : count.toString()
  },
  
  // 增加搜索次数
  incrementSearchCount() {
    const current = parseInt(localStorage.getItem('searchCount') || '0')
    localStorage.setItem('searchCount', (current + 1).toString())
  }
}

// 缓存管理
class Cache {
  constructor(ttl = 5 * 60 * 1000) { // 默认5分钟过期
    this.cache = new Map()
    this.ttl = ttl
  }
  
  set(key, value) {
    const expiry = Date.now() + this.ttl
    this.cache.set(key, { value, expiry })
  }
  
  get(key) {
    const item = this.cache.get(key)
    if (!item) return null
    
    if (Date.now() > item.expiry) {
      this.cache.delete(key)
      return null
    }
    
    return item.value
  }
  
  clear() {
    this.cache.clear()
  }
}

export const searchCache = new Cache()

// 兼容性API工具集扩展 - 添加到现有的 src/utils/api.js 文件末尾

// ==================== 兼容性API集合 ====================

/**
 * 兼容性检查API
 * 基于后端 /api/public/compatibility/ 端点
 */
export const compatibilityAPI = {
  /**
   * 兼容性检查 (2-10个零件)
   */
  check(data) {
    return axios.post('/api/public/compatibility/check', {  // 直接使用axios，不用api实例
      part_ids: data.part_ids,
      include_cache: data.include_cache !== false,
      detail_level: data.detail_level || 'standard'
    })
  },

  /**
   * 兼容性搜索
   */
  search(data) {
    return axios.post('/api/public/compatibility/search', {
      selected_parts: data.selected_parts,
      target_categories: data.target_categories || null,
      min_compatibility_score: data.min_compatibility_score || 50,
      limit: data.limit || 20,
      include_theoretical: data.include_theoretical !== false
    })
  },

  /**
   * 快速兼容性检查 (两个零件)
   */
  quickCheck(partAId, partBId) {
    return axios.get('/api/public/compatibility/quick-check', {
      params: { 
        part_a_id: partAId, 
        part_b_id: partBId 
      }
    })
  },

  /**
   * 获取兼容性建议
   */
  suggestions(partId, params = {}) {
    return axios.get(`/api/public/compatibility/suggestions/${partId}`, { 
      params: {
        limit: params.limit || 10,
        min_score: params.min_score || 70,
        categories: params.categories || null
      }
    })
  },

  /**
   * 获取系统状态
   */
  systemStatus() {
    return axios.get('/api/public/compatibility/system-status')
  },

  /**
   * 获取兼容性知识库
   */
  knowledgeBase(params = {}) {
    return axios.get('/api/public/compatibility/knowledge-base', { params })
  },

  /**
   * 获取外部反馈渠道信息
   */
  feedbackChannels() {
    return axios.get('/api/public/compatibility/feedback-channels')
  },

  /**
   * 获取API使用示例
   */
  examples() {
    return axios.get('/api/public/compatibility/examples')
  },

  /**
   * 获取版本信息
   */
  version() {
    return axios.get('/api/public/compatibility/version')
  }
}

// ==================== 兼容性辅助函数 ====================

/**
 * 兼容性相关的辅助函数
 */
export const compatibilityHelpers = {
  /**
   * 格式化兼容度等级
   * @param {string} grade - 兼容度等级
   * @returns {Object} 格式化后的等级信息
   */
  formatGrade(grade) {
    const grades = {
      official_support: { 
        text: '官方支持', 
        color: '#67C23A', 
        icon: '✅',
        description: '官方确认兼容，完全支持',
        scoreRange: '90-100分'
      },
      unofficial_support: { 
        text: '社区验证', 
        color: '#409EFF', 
        icon: '🔷',
        description: '用户验证可用，可能有限制',
        scoreRange: '70-89分'
      },
      theoretical: { 
        text: '理论兼容', 
        color: '#E6A23C', 
        icon: '⚠️',
        description: '理论上兼容，建议实际测试',
        scoreRange: '50-69分'
      },
      incompatible: { 
        text: '不兼容', 
        color: '#F56C6C', 
        icon: '❌',
        description: '不兼容或存在已知问题',
        scoreRange: '0-49分'
      }
    }
    return grades[grade] || grades.incompatible
  },

  /**
   * 格式化兼容性评分
   * @param {number} score - 评分 (0-100)
   * @returns {Object} 格式化后的评分信息
   */
  formatScore(score) {
    const normalizedScore = Math.max(0, Math.min(100, score))
    
    return {
      value: normalizedScore,
      percentage: normalizedScore,
      color: normalizedScore >= 90 ? '#67C23A' : 
             normalizedScore >= 70 ? '#409EFF' : 
             normalizedScore >= 50 ? '#E6A23C' : '#F56C6C',
      grade: normalizedScore >= 90 ? 'official_support' :
             normalizedScore >= 70 ? 'unofficial_support' :
             normalizedScore >= 50 ? 'theoretical' : 'incompatible',
      status: normalizedScore >= 50 ? 'compatible' : 'incompatible'
    }
  },

  /**
   * 获取兼容度等级对应的颜色
   * @param {string} grade - 兼容度等级
   * @returns {string} 颜色值
   */
  getGradeColor(grade) {
    const gradeInfo = this.formatGrade(grade)
    return gradeInfo.color
  },

  /**
   * 获取兼容度等级对应的图标
   * @param {string} grade - 兼容度等级
   * @returns {string} 图标
   */
  getGradeIcon(grade) {
    const gradeInfo = this.formatGrade(grade)
    return gradeInfo.icon
  },

  /**
   * 批量检查兼容性
   * @param {Array} partIdGroups - 零件ID组合数组
   * @param {Object} options - 选项
   * @returns {Promise<Array>} 检查结果数组
   */
  async batchCheck(partIdGroups, options = {}) {
    const results = []
    
    for (const group of partIdGroups) {
      try {
        const result = await compatibilityAPI.check({
          part_ids: group,
          include_cache: options.include_cache !== false,
          detail_level: options.detail_level || 'standard'
        })
        results.push({
          success: true,
          parts: group,
          data: result.data
        })
      } catch (error) {
        results.push({
          success: false,
          parts: group,
          error: error.message || '检查失败'
        })
      }
    }
    
    return results
  },

  /**
   * 分析兼容性检查结果
   * @param {Object} result - 兼容性检查结果
   * @returns {Object} 分析总结
   */
  analyzeResult(result) {
    if (!result || !result.part_combinations) {
      return {
        summary: '无有效结果',
        issues: ['检查结果为空'],
        recommendations: ['请重新进行兼容性检查']
      }
    }

    const combinations = result.part_combinations
    const incompatiblePairs = combinations.filter(c => !c.is_compatible)
    const lowScorePairs = combinations.filter(c => c.is_compatible && c.compatibility_score < 70)
    
    const issues = []
    const recommendations = []

    // 分析不兼容问题
    if (incompatiblePairs.length > 0) {
      issues.push(`发现${incompatiblePairs.length}个不兼容组合`)
      recommendations.push('建议更换不兼容的零件')
    }

    // 分析低评分问题
    if (lowScorePairs.length > 0) {
      issues.push(`${lowScorePairs.length}个组合兼容性较低`)
      recommendations.push('考虑优化配置以获得更好兼容性')
    }

    // 分析警告信息
    const allWarnings = combinations.flatMap(c => c.warnings || [])
    if (allWarnings.length > 0) {
      issues.push(`存在${allWarnings.length}个警告信息`)
      recommendations.push('请注意查看详细警告说明')
    }

    const summary = result.is_overall_compatible ? 
      `整体兼容，评分${result.overall_score}分` :
      `存在兼容性问题，评分${result.overall_score}分`

    return {
      summary,
      issues,
      recommendations,
      stats: {
        totalPairs: combinations.length,
        compatiblePairs: combinations.filter(c => c.is_compatible).length,
        incompatiblePairs: incompatiblePairs.length,
        lowScorePairs: lowScorePairs.length,
        overallScore: result.overall_score,
        overallGrade: result.overall_compatibility_grade
      }
    }
  },

  /**
   * 格式化执行时间
   * @param {number} timeInSeconds - 执行时间（秒）
   * @returns {string} 格式化的时间字符串
   */
  formatExecutionTime(timeInSeconds) {
    if (timeInSeconds < 1) {
      return `${Math.round(timeInSeconds * 1000)}ms`
    } else {
      return `${timeInSeconds.toFixed(2)}s`
    }
  },

  /**
   * 创建兼容性报告
   * @param {Object} result - 兼容性检查结果
   * @param {Array} partsList - 零件列表
   * @returns {Object} 格式化的报告
   */
  createReport(result, partsList) {
    const analysis = this.analyzeResult(result)
    const timestamp = new Date().toLocaleString('zh-CN')
    
    return {
      meta: {
        title: '零件兼容性检查报告',
        generateTime: timestamp,
        partCount: partsList.length,
        executionTime: this.formatExecutionTime(result.execution_time || 0)
      },
      parts: partsList.map(part => ({
        id: part.id,
        name: part.name,
        category: part.category
      })),
      summary: {
        overallScore: result.overall_score,
        overallGrade: this.formatGrade(result.overall_compatibility_grade),
        isCompatible: result.is_overall_compatible,
        analysis: analysis.summary
      },
      details: result.part_combinations?.map(combo => ({
        partA: combo.part_a_name,
        partB: combo.part_b_name,
        score: combo.compatibility_score,
        grade: this.formatGrade(combo.compatibility_grade),
        compatible: combo.is_compatible,
        warnings: combo.warnings || []
      })) || [],
      issues: analysis.issues,
      recommendations: [...analysis.recommendations, ...(result.recommendations || [])],
      cached: result.cached || false
    }
  }
}

// ==================== 统一错误处理 ====================

/**
 * 兼容性API统一错误处理
 * @param {Error} error - 错误对象
 * @returns {string} 用户友好的错误信息
 */
export const handleCompatibilityError = (error) => {
  console.error('兼容性API错误:', error)
  
  if (error.response) {
    const status = error.response.status
    const detail = error.response.data?.detail || ''
    
    switch (status) {
      case 400:
        if (detail.includes('零件')) {
          return detail
        }
        return '请求参数错误，请检查零件选择'
      case 404:
        if (detail.includes('零件')) {
          return '部分零件不存在，请检查零件列表'
        }
        return '请求的资源不存在'
      case 429:
        return '请求过于频繁，请稍后再试'
      case 500:
        return '服务器内部错误，请稍后重试'
      case 503:
        return '兼容性检查服务暂时不可用'
      default:
        return detail || `服务器错误 (${status})`
    }
  } else if (error.request) {
    return '网络连接失败，请检查网络状态'
  } else {
    return error.message || '未知错误，请重试'
  }
}

// ==================== 缓存管理 ====================

/**
 * 兼容性检查结果缓存管理
 */
class CompatibilityCache {
  constructor(ttl = 5 * 60 * 1000) { // 默认5分钟过期
    this.cache = new Map()
    this.ttl = ttl
  }
  
  /**
   * 生成缓存键
   * @param {Array} partIds - 零件ID数组
   * @returns {string} 缓存键
   */
  generateKey(partIds) {
    return partIds.sort((a, b) => a - b).join(',')
  }
  
  /**
   * 设置缓存
   * @param {Array} partIds - 零件ID数组
   * @param {Object} result - 检查结果
   */
  set(partIds, result) {
    const key = this.generateKey(partIds)
    const expiry = Date.now() + this.ttl
    this.cache.set(key, { result, expiry })
  }
  
  /**
   * 获取缓存
   * @param {Array} partIds - 零件ID数组
   * @returns {Object|null} 缓存的结果或null
   */
  get(partIds) {
    const key = this.generateKey(partIds)
    const item = this.cache.get(key)
    
    if (!item) return null
    
    if (Date.now() > item.expiry) {
      this.cache.delete(key)
      return null
    }
    
    return item.result
  }
  
  /**
   * 清除过期缓存
   */
  cleanup() {
    const now = Date.now()
    for (const [key, item] of this.cache.entries()) {
      if (now > item.expiry) {
        this.cache.delete(key)
      }
    }
  }
  
  /**
   * 清空所有缓存
   */
  clear() {
    this.cache.clear()
  }
}

// 导出缓存实例
export const compatibilityCache = new CompatibilityCache()

// 定期清理过期缓存
setInterval(() => {
  compatibilityCache.cleanup()
}, 60000) // 每分钟清理一次

// ==================== 便捷封装方法 ====================

/**
 * 快速兼容性检查（带缓存）
 * @param {Array} partIds - 零件ID数组
 * @param {Object} options - 选项
 * @returns {Promise<Object>} 检查结果
 */
export const quickCompatibilityCheck = async (partIds, options = {}) => {
  // 先尝试从缓存获取
  if (options.useCache !== false) {
    const cached = compatibilityCache.get(partIds)
    if (cached) {
      return { ...cached, cached: true }
    }
  }
  
  try {
    const response = await compatibilityAPI.check({
      part_ids: partIds,
      include_cache: options.include_cache !== false,
      detail_level: options.detail_level || 'standard'
    })
    
    const result = response.data
    
    // 缓存结果
    if (options.useCache !== false) {
      compatibilityCache.set(partIds, result)
    }
    
    return result
  } catch (error) {
    throw new Error(handleCompatibilityError(error))
  }
}

/**
 * 获取零件的兼容性建议（带缓存）
 * @param {number} partId - 零件ID
 * @param {Object} options - 选项
 * @returns {Promise<Array>} 建议零件列表
 */
export const getCompatibilitySuggestions = async (partId, options = {}) => {
  try {
    const response = await compatibilityAPI.suggestions(partId, options)
    return response.data
  } catch (error) {
    console.error('获取兼容性建议失败:', error)
    return []
  }
}

/**
 * 搜索兼容零件（增强版）
 * @param {Array} selectedParts - 已选零件ID数组
 * @param {Object} filters - 筛选条件
 * @returns {Promise<Object>} 搜索结果
 */
export const searchCompatibleParts = async (selectedParts, filters = {}) => {
  try {
    const response = await compatibilityAPI.search({
      selected_parts: selectedParts,
      target_categories: filters.categories,
      min_compatibility_score: filters.minScore || 50,
      limit: filters.limit || 20,
      include_theoretical: filters.includeTheoretical !== false
    })
    
    return response.data
  } catch (error) {
    throw new Error(handleCompatibilityError(error))
  }
}

export default api