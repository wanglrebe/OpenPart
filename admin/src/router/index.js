// admin/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { setupRouterGuards } from './guards'

// 导入页面组件
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import PartsAdmin from '../views/PartsAdmin.vue'

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
    path: '/parts',  // 确保这个路径正确
    name: 'PartsAdmin',
    component: PartsAdmin,
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