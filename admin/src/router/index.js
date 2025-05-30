// admin/src/router/index.js (更新版本 - 添加兼容性管理路由)
import { createRouter, createWebHistory } from 'vue-router'
import { setupRouterGuards } from './guards'

// 导入页面组件
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import PartsAdmin from '../views/PartsAdmin.vue'
import ImportExport from '../views/ImportExport.vue'
import CrawlerPlugins from '../views/CrawlerPlugins.vue'
import CompatibilityAdmin from '../views/CompatibilityAdmin.vue'  // 新增兼容性管理

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
    path: '/crawler-plugins',
    name: 'CrawlerPlugins',
    component: CrawlerPlugins,
    meta: { requiresAuth: true }
  },
  {
    path: '/compatibility',  // 新增兼容性管理路由
    name: 'CompatibilityAdmin',
    component: CompatibilityAdmin,
    meta: { 
      requiresAuth: true,
      title: '兼容性管理'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 设置路由守卫
setupRouterGuards(router)

export default router