<!-- portal/src/components/GlobalNavigation.vue (新组件) -->
<template>
  <header class="global-nav">
    <div class="container">
      <div class="nav-content">
        <!-- Logo -->
        <router-link to="/" class="logo-link">
          <h1 class="logo">OpenPart</h1>
          <span class="tagline">零件搜索门户</span>
        </router-link>
        
        <!-- 预留搜索框位置（由具体页面决定是否显示） -->
        <div class="nav-search-slot">
          <slot name="search"></slot>
        </div>
        
        <!-- 桌面端导航菜单 -->
        <nav class="desktop-nav">
          <router-link 
            to="/favorites" 
            class="nav-link"
            :class="{ active: $route.path === '/favorites' }"
          >
            <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
            <span>收藏夹</span>
            <span v-if="favoritesCount > 0" class="nav-badge">{{ favoritesCount }}</span>
          </router-link>
          
          <router-link 
            to="/projects" 
            class="nav-link"
            :class="{ active: $route.path === '/projects' }"
          >
            <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <span>项目清单</span>
            <span v-if="projectsCount > 0" class="nav-badge">{{ projectsCount }}</span>
          </router-link>
          
          <!-- 对比按钮（有对比内容时显示） -->
          <button 
            v-if="comparisonCount > 0"
            @click="goToComparison"
            class="nav-link comparison-btn"
          >
            <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <span>对比</span>
            <span class="nav-badge comparison">{{ comparisonCount }}</span>
          </button>
          
          <ThemeToggle />
        </nav>
        
        <!-- 移动端菜单按钮 -->
        <div class="mobile-nav">
          <button 
            v-if="comparisonCount > 0"
            @click="goToComparison"
            class="mobile-comparison-btn"
            title="零件对比"
          >
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <span class="mobile-badge">{{ comparisonCount }}</span>
          </button>
          
          <button 
            @click="toggleMobileMenu" 
            class="mobile-menu-btn"
            :class="{ active: showMobileMenu }"
          >
            <svg v-if="!showMobileMenu" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            <svg v-else fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
    
    <!-- 移动端菜单 -->
    <div v-if="showMobileMenu" class="mobile-menu" @click="closeMobileMenu">
      <div class="mobile-menu-content" @click.stop>
        <nav class="mobile-nav-list">
          <router-link to="/" class="mobile-nav-item" @click="closeMobileMenu">
            <svg class="mobile-nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            <div class="mobile-nav-info">
              <span class="mobile-nav-title">首页</span>
              <span class="mobile-nav-desc">搜索和浏览零件</span>
            </div>
          </router-link>
          
          <router-link to="/favorites" class="mobile-nav-item" @click="closeMobileMenu">
            <svg class="mobile-nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
            <div class="mobile-nav-info">
              <span class="mobile-nav-title">我的收藏</span>
              <span class="mobile-nav-desc">{{ favoritesCount }} 个收藏零件</span>
            </div>
            <span v-if="favoritesCount > 0" class="mobile-nav-badge">{{ favoritesCount }}</span>
          </router-link>
          
          <router-link to="/projects" class="mobile-nav-item" @click="closeMobileMenu">
            <svg class="mobile-nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <div class="mobile-nav-info">
              <span class="mobile-nav-title">项目清单</span>
              <span class="mobile-nav-desc">{{ projectsCount }} 个项目</span>
            </div>
            <span v-if="projectsCount > 0" class="mobile-nav-badge">{{ projectsCount }}</span>
          </router-link>
          
          <div v-if="comparisonCount > 0" class="mobile-nav-item comparison-item" @click="goToComparison">
            <svg class="mobile-nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <div class="mobile-nav-info">
              <span class="mobile-nav-title">零件对比</span>
              <span class="mobile-nav-desc">{{ comparisonCount }} 个零件待对比</span>
            </div>
            <span class="mobile-nav-badge comparison">{{ comparisonCount }}</span>
          </div>
        </nav>
        
        <div class="mobile-menu-footer">
          <div class="theme-toggle-container">
            <span>深色模式</span>
            <ThemeToggle />
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ThemeToggle from './ThemeToggle.vue'
import { favoritesManager, comparisonManager } from '../utils/api'

export default {
  name: 'GlobalNavigation',
  components: {
    ThemeToggle
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const showMobileMenu = ref(false)
    const favoritesCount = ref(0)
    const projectsCount = ref(0)
    const comparisonCount = ref(0)
    
    // 更新计数
    const updateCounts = () => {
      favoritesCount.value = favoritesManager.getFavoritesCount()
      comparisonCount.value = comparisonManager.getComparisonCount()
      
      // 获取项目数量
      const projects = JSON.parse(localStorage.getItem('openpart_projects') || '[]')
      projectsCount.value = projects.length
    }
    
    // 移动端菜单控制
    const toggleMobileMenu = () => {
      showMobileMenu.value = !showMobileMenu.value
    }
    
    const closeMobileMenu = () => {
      showMobileMenu.value = false
    }
    
    // 跳转对比页面
    const goToComparison = () => {
      const compareUrl = comparisonManager.getComparisonUrl()
      if (compareUrl) {
        router.push(compareUrl)
        closeMobileMenu()
      }
    }
    
    // 监听存储变化
    const handleStorageChange = (e) => {
      if (['openpart_favorites', 'openpart_comparison', 'openpart_projects'].includes(e.key)) {
        updateCounts()
      }
    }
    
    // 监听路由变化，关闭移动菜单
    const unwatch = router.afterEach(() => {
      closeMobileMenu()
    })
    
    onMounted(() => {
      updateCounts()
      window.addEventListener('storage', handleStorageChange)
    })
    
    onUnmounted(() => {
      window.removeEventListener('storage', handleStorageChange)
      unwatch()
    })
    
    return {
      showMobileMenu,
      favoritesCount,
      projectsCount,
      comparisonCount,
      toggleMobileMenu,
      closeMobileMenu,
      goToComparison
    }
  }
}
</script>

<style scoped>
.global-nav {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(8px);
}

.nav-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0;
  gap: 24px;
}

/* Logo */
.logo-link {
  text-decoration: none;
  flex-shrink: 0;
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.logo {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary);
  margin: 0;
}

.tagline {
  font-size: 12px;
  color: var(--text-muted);
}

/* 导航搜索框插槽 */
.nav-search-slot {
  flex: 1;
  max-width: 500px;
  min-width: 300px;
  display: flex;
  align-items: center;
}

/* 确保搜索框不影响导航高度 */
.nav-search-slot :deep(.search-box) {
  margin: 0;
  width: 100%;
}

.nav-search-slot :deep(.search-input) {
  height: 40px;
  padding: 8px 40px 8px 40px;
}

/* 桌面端导航 */
.desktop-nav {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 8px;
  text-decoration: none;
  color: var(--text-secondary);
  transition: all 0.2s ease;
  position: relative;
  border: 1px solid transparent;
  background: none;
  cursor: pointer;
  font-size: 14px;
}

.nav-link:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-color: var(--border-color);
}

.nav-link.active {
  background: color-mix(in srgb, var(--primary) 10%, transparent);
  color: var(--primary);
  border-color: color-mix(in srgb, var(--primary) 20%, transparent);
}

.nav-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.nav-badge {
  background: var(--primary);
  color: white;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
  line-height: 1.2;
}

.nav-badge.comparison {
  background: #f59e0b;
}

.comparison-btn {
  background: color-mix(in srgb, #f59e0b 10%, transparent);
  border-color: color-mix(in srgb, #f59e0b 20%, transparent);
  color: #f59e0b;
}

.comparison-btn:hover {
  background: #f59e0b;
  color: white;
}

/* 移动端导航 */
.mobile-nav {
  display: none;
  align-items: center;
  gap: 8px;
}

.mobile-menu-btn,
.mobile-comparison-btn {
  width: 40px;
  height: 40px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-card);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  position: relative;
}

.mobile-menu-btn:hover,
.mobile-comparison-btn:hover {
  background: var(--bg-secondary);
  border-color: var(--primary);
}

.mobile-menu-btn.active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.mobile-comparison-btn {
  background: color-mix(in srgb, #f59e0b 10%, transparent);
  border-color: color-mix(in srgb, #f59e0b 20%, transparent);
  color: #f59e0b;
}

.mobile-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  background: #f59e0b;
  color: white;
  font-size: 10px;
  font-weight: 600;
  padding: 1px 4px;
  border-radius: 8px;
  min-width: 16px;
  text-align: center;
  line-height: 1.2;
}

.mobile-menu-btn svg,
.mobile-comparison-btn svg {
  width: 20px;
  height: 20px;
}

/* 移动端菜单 */
.mobile-menu {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  padding-top: 80px;
}

.mobile-menu-content {
  background: var(--bg-card);
  border-radius: 12px 0 0 12px;
  width: 280px;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
  animation: slideInRight 0.3s ease;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.mobile-nav-list {
  padding: 20px 0;
}

.mobile-nav-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 20px;
  text-decoration: none;
  color: var(--text-primary);
  transition: background-color 0.2s ease;
  cursor: pointer;
  position: relative;
}

.mobile-nav-item:hover {
  background: var(--bg-secondary);
}

.mobile-nav-item.router-link-active {
  background: color-mix(in srgb, var(--primary) 10%, transparent);
  border-right: 3px solid var(--primary);
}

.mobile-nav-item.comparison-item {
  background: color-mix(in srgb, #f59e0b 5%, transparent);
}

.mobile-nav-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  color: var(--text-secondary);
}

.mobile-nav-info {
  flex: 1;
  min-width: 0;
}

.mobile-nav-title {
  display: block;
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.mobile-nav-desc {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
}

.mobile-nav-badge {
  background: var(--primary);
  color: white;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 20px;
  text-align: center;
}

.mobile-nav-badge.comparison {
  background: #f59e0b;
}

.mobile-menu-footer {
  padding: 20px;
  border-top: 1px solid var(--border-color);
}

.theme-toggle-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  color: var(--text-secondary);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .nav-search {
    max-width: 400px;
    min-width: 200px;
  }
  
  .tagline {
    display: none;
  }
}

@media (max-width: 768px) {
  .desktop-nav {
    display: none;
  }
  
  .mobile-nav {
    display: flex;
  }
  
  /* 移动端搜索框插槽显示处理 */
  .nav-search-slot {
    display: flex;
    min-width: 200px;
    max-width: none;
    margin: 0 12px;
  }
  
  /* 如果插槽为空则隐藏 */
  .nav-search-slot:empty {
    display: none;
  }
  
  .nav-content {
    gap: 12px;
  }
  
  .logo {
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .mobile-menu-content {
    width: 100%;
    border-radius: 0;
  }
  
  .mobile-menu {
    padding-top: 70px;
  }
}
</style>