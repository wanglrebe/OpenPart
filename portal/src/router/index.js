import { createRouter, createWebHistory } from 'vue-router'

// 路由组件
import Home from '../views/Home.vue'
import Search from '../views/Search.vue'
import Detail from '../views/Detail.vue'

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
    path: '/:pathMatch(.*)*',
    redirect: '/'
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
  next()
})

export default router