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

export default api