// portal/src/router/index.js (更新版本 - 添加项目详情页面)
import { createRouter, createWebHistory } from 'vue-router'

// 路由组件
import Home from '../views/Home.vue'
import Search from '../views/Search.vue'
import Detail from '../views/Detail.vue'
import Compare from '../views/Compare.vue'
import Favorites from '../views/Favorites.vue'
import Projects from '../views/Projects.vue'
import ProjectDetail from '../views/ProjectDetail.vue'  // 新增

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      title: 'OpenPart - 零件搜索门户'
    }
  },
  {
    path: '/search',
    name: 'Search',
    component: Search,
    meta: {
      title: '搜索结果 - OpenPart'
    }
  },
  {
    path: '/part/:id',
    name: 'Detail',
    component: Detail,
    props: true,
    meta: {
      title: '零件详情 - OpenPart'
    }
  },
  {
    path: '/compare',
    name: 'Compare',
    component: Compare,
    meta: {
      title: '零件对比 - OpenPart'
    },
    beforeEnter: (to, from, next) => {
      // 检查是否有要对比的零件ID
      const ids = to.query.ids
      if (!ids || (typeof ids === 'string' && ids.split(',').length < 1)) {
        // 如果没有零件ID，重定向到首页
        next('/')
      } else {
        next()
      }
    }
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: Favorites,
    meta: {
      title: '我的收藏 - OpenPart'
    }
  },
  {
    path: '/projects',
    name: 'Projects',
    component: Projects,
    meta: {
      title: '项目清单 - OpenPart'
    }
  },
  {
    path: '/projects/:id',  // 新增项目详情页面路由
    name: 'ProjectDetail',
    component: ProjectDetail,
    props: true,
    meta: {
      title: '项目详情 - OpenPart'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  },
  {
    path: '/compatibility',
    name: 'CompatibilityCheck',
    component: () => import('../views/CompatibilityCheck.vue'),
    meta: {
      title: '兼容性检查 - OpenPart',
      description: '检查零件之间的兼容性，获取专业建议',
      requiresAuth: false, // 公开访问
      showInNavigation: true, // 在导航中显示
      icon: 'compatibility-check' // 导航图标标识
    },
    // 支持查询参数：?parts=1,2,3 用于直接加载零件列表
    beforeEnter: (to, from, next) => {
      // 验证parts参数格式
      if (to.query.parts) {
        const partIds = to.query.parts.split(',').map(id => parseInt(id.trim()))
        const validIds = partIds.filter(id => !isNaN(id) && id > 0)
        
        if (validIds.length !== partIds.length) {
          // 清理无效的ID参数
          next({
            name: 'CompatibilityCheck',
            query: { 
              ...to.query, 
              parts: validIds.length > 0 ? validIds.join(',') : undefined 
            }
          })
          return
        }
        
        // 限制零件数量 (最多10个)
        if (validIds.length > 10) {
          console.warn('零件数量超过限制，只保留前10个')
          next({
            name: 'CompatibilityCheck',
            query: { 
              ...to.query, 
              parts: validIds.slice(0, 10).join(',') 
            }
          })
          return
        }
      }
      
      next()
    }
  },
  {
    path: '/compatibility/guide',
    name: 'CompatibilityGuide',
    component: () => import('../views/CompatibilityGuide.vue'),
    meta: {
      title: '兼容性指南 - OpenPart',
      description: '了解零件兼容性知识，学习如何正确搭配零件',
      requiresAuth: false, // 公开访问
      showInNavigation: false, // 不在主导航显示
      parentRoute: 'CompatibilityCheck' // 父级路由
    }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue'),
    meta: {
      title: '关于项目 - OpenPart'
    }
  }

]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守卫 - 更新页面标题
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title
  }
  if (to.name === 'CompatibilityCheck') {
    const partIds = to.query.parts
    if (partIds) {
      const count = partIds.split(',').length
      document.title = `兼容性检查 (${count}个零件) - OpenPart`
    } else {
      document.title = to.meta.title || 'OpenPart'
    }
  } else if (to.meta.title) {
    document.title = to.meta.title
  }
  
  next()
})



// ==================== 路由辅助函数 ====================

/**
 * 生成兼容性检查路由
 * @param {Array} partIds - 零件ID数组
 * @param {Object} options - 可选参数
 * @returns {Object} 路由对象
 */
export const createCompatibilityRoute = (partIds, options = {}) => {
  const query = {}
  
  // 添加零件ID参数
  if (partIds && partIds.length > 0) {
    const validIds = partIds.filter(id => !isNaN(parseInt(id)) && parseInt(id) > 0)
    if (validIds.length > 0) {
      query.parts = validIds.slice(0, 10).join(',') // 限制最多10个
    }
  }
  
  // 添加其他查询参数
  if (options.autoCheck) {
    query.auto = '1' // 自动开始检查
  }
  
  if (options.detailLevel) {
    query.detail = options.detailLevel // basic/standard/detailed
  }
  
  return {
    name: 'CompatibilityCheck',
    query: Object.keys(query).length > 0 ? query : undefined
  }
}

/**
 * 解析兼容性检查路由参数
 * @param {Object} route - 路由对象
 * @returns {Object} 解析后的参数
 */
export const parseCompatibilityRoute = (route) => {
  const params = {
    partIds: [],
    autoCheck: false,
    detailLevel: 'standard'
  }
  
  // 解析零件ID
  if (route.query.parts) {
    const parts = route.query.parts.split(',')
    params.partIds = parts
      .map(id => parseInt(id.trim()))
      .filter(id => !isNaN(id) && id > 0)
      .slice(0, 10) // 限制最多10个
  }
  
  // 解析自动检查参数
  if (route.query.auto === '1' || route.query.auto === 'true') {
    params.autoCheck = true
  }
  
  // 解析详细程度参数
  if (['basic', 'standard', 'detailed'].includes(route.query.detail)) {
    params.detailLevel = route.query.detail
  }
  
  return params
}

/**
 * 检查是否为兼容性相关路由
 * @param {Object} route - 路由对象
 * @returns {boolean} 是否为兼容性路由
 */
export const isCompatibilityRoute = (route) => {
  return route.name === 'CompatibilityCheck' || 
         route.name === 'CompatibilityGuide' ||
         route.path.startsWith('/compatibility')
}

/**
 * 获取兼容性功能的面包屑导航
 * @param {Object} route - 当前路由
 * @returns {Array} 面包屑数组
 */
export const getCompatibilityBreadcrumbs = (route) => {
  const breadcrumbs = [
    { name: '首页', path: '/' }
  ]
  
  if (route.name === 'CompatibilityCheck') {
    breadcrumbs.push({ name: '兼容性检查', path: '/compatibility' })
  } else if (route.name === 'CompatibilityGuide') {
    breadcrumbs.push(
      { name: '兼容性检查', path: '/compatibility' },
      { name: '兼容性指南', path: '/compatibility/guide' }
    )
  }
  
  return breadcrumbs
}

// ==================== SEO和元信息配置 ====================

/**
 * 兼容性页面的SEO元信息配置
 */
export const compatibilityMetaConfig = {
  CompatibilityCheck: {
    title: '零件兼容性检查工具',
    description: '专业的电子零件兼容性检查工具，支持多零件组合检查，提供详细的兼容性分析和建议',
    keywords: '零件兼容性,电子元件,兼容性检查,硬件搭配,电路设计',
    ogType: 'website',
    ogTitle: '零件兼容性检查 - OpenPart',
    ogDescription: '快速检查电子零件之间的兼容性，获得专业的搭配建议',
    twitterCard: 'summary_large_image'
  },
  CompatibilityGuide: {
    title: '零件兼容性指南',
    description: '学习零件兼容性知识，了解如何正确搭配电子元件，避免兼容性问题',
    keywords: '兼容性指南,零件搭配,电子设计,硬件选型,兼容性知识',
    ogType: 'article',
    ogTitle: '零件兼容性指南 - OpenPart',
    ogDescription: '全面的零件兼容性知识库，帮助您做出正确的硬件选择'
  }
}

// ==================== 导航菜单配置 ====================

/**
 * 兼容性功能在导航菜单中的配置
 */
export const compatibilityNavigationConfig = {
  // 主导航项配置
  mainNavItem: {
    name: 'compatibility',
    title: '兼容性检查',
    path: '/compatibility',
    icon: 'compatibility-check', // 对应图标组件或图标类名
    badge: 'dynamic', // 动态徽章，显示检查列表数量
    order: 30, // 在导航中的排序位置
    showCondition: 'always', // 显示条件：always/hasItems/loggedIn
    mobileVisible: true // 在移动端导航中是否显示
  },
  
  // 子菜单配置
  subMenuItems: [
    {
      name: 'compatibility-check',
      title: '兼容性检查',
      path: '/compatibility',
      description: '检查零件兼容性'
    },
    {
      name: 'compatibility-guide',
      title: '兼容性指南',
      path: '/compatibility/guide',
      description: '学习兼容性知识'
    }
  ]
}

// ==================== 路由权限配置 ====================

/**
 * 兼容性功能的权限配置
 */
export const compatibilityPermissions = {
  // 基础兼容性检查 - 所有用户可访问
  'compatibility:check': {
    roles: ['*'], // 所有角色
    description: '基础兼容性检查功能'
  },
  
  // 高级功能 - 可以根据需要添加权限控制
  'compatibility:advanced': {
    roles: ['user', 'premium', 'admin'],
    description: '高级兼容性分析功能'
  },
  
  // 批量检查 - 可以限制频率
  'compatibility:batch': {
    roles: ['user', 'premium', 'admin'],
    rateLimit: {
      requests: 10,
      window: '1h'
    },
    description: '批量兼容性检查'
  }
}

// ==================== 路由数据预加载配置 ====================

/**
 * 兼容性页面的数据预加载配置
 */
export const compatibilityDataLoaders = {
  // 兼容性检查页面预加载
  CompatibilityCheck: async (route) => {
    const promises = []
    
    // 如果有零件ID参数，预加载零件信息
    const params = parseCompatibilityRoute(route)
    if (params.partIds.length > 0) {
      // 这里可以预加载零件信息
      // promises.push(partsAPI.getParts({ ids: params.partIds }))
    }
    
    // 预加载系统状态
    // promises.push(compatibilityAPI.systemStatus())
    
    try {
      const results = await Promise.allSettled(promises)
      return {
        preloadedData: results,
        success: true
      }
    } catch (error) {
      console.warn('预加载数据失败:', error)
      return {
        preloadedData: null,
        success: false,
        error: error.message
      }
    }
  }
}

export default router