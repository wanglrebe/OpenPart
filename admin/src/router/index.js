// admin/src/router/index.js - 更新版本，添加兼容性编辑器路由

import { createRouter, createWebHistory } from 'vue-router'
import { setupRouterGuards } from './guards'

// 导入页面组件
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import PartsAdmin from '../views/PartsAdmin.vue'
import ImportExport from '../views/ImportExport.vue'
import CrawlerPlugins from '../views/CrawlerPlugins.vue'
import CompatibilityEditor from '../views/CompatibilityEditor.vue'  // 🆕 新增兼容性编辑器

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { 
      requiresAuth: false,
      title: '登录'
    }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { 
      requiresAuth: true,
      title: '仪表板'
    }
  },
  {
    path: '/parts',
    name: 'PartsAdmin',
    component: PartsAdmin,
    meta: { 
      requiresAuth: true,
      title: '零件管理'
    }
  },
  {
    path: '/import-export',
    name: 'ImportExport',
    component: ImportExport,
    meta: { 
      requiresAuth: true,
      title: '数据管理'
    }
  },
  {
    path: '/crawler-plugins',
    name: 'CrawlerPlugins',
    component: CrawlerPlugins,
    meta: { 
      requiresAuth: true,
      title: '插件管理'
    }
  },
  // 🆕 新增兼容性编辑器路由
  {
    path: '/compatibility',
    name: 'CompatibilityEditor',
    component: CompatibilityEditor,
    meta: { 
      requiresAuth: true,
      title: '兼容性配置编辑器',
      description: '管理兼容性规则和经验数据'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 设置路由守卫
setupRouterGuards(router)

// 🆕 路由元信息处理
router.afterEach((to) => {
  // 设置页面标题
  if (to.meta && to.meta.title) {
    document.title = `${to.meta.title} - OpenPart 管理后台`
  } else {
    document.title = 'OpenPart 管理后台'
  }
})

export default router