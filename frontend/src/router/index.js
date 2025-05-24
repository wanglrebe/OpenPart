import { createRouter, createWebHistory } from 'vue-router'
import PartsList from '../views/PartsList.vue'
import About from '../views/About.vue'

const routes = [
  {
    path: '/',
    redirect: '/parts'
  },
  {
    path: '/parts',
    name: 'Parts',
    component: PartsList
  },
  {
    path: '/about',
    name: 'About',
    component: About
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router