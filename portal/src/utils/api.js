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
  }
}

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