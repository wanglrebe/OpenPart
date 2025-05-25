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