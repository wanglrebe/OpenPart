// admin/src/router/index.js (更新版本 - 添加插件管理路由)
import { createRouter, createWebHistory } from 'vue-router'
import { setupRouterGuards } from './guards'

// 导入页面组件
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import PartsAdmin from '../views/PartsAdmin.vue'
import ImportExport from '../views/ImportExport.vue'
import CrawlerPlugins from '../views/CrawlerPlugins.vue'  // 新增

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/parts',
    name: 'PartsAdmin',
    component: PartsAdmin,
    meta: { requiresAuth: true }
  },
  {
    path: '/import-export',
    name: 'ImportExport',
    component: ImportExport,
    meta: { requiresAuth: true }
  },
  {
    path: '/crawler-plugins',  // 新增爬虫插件管理路由
    name: 'CrawlerPlugins',
    component: CrawlerPlugins,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 设置路由守卫
setupRouterGuards(router)

export default router