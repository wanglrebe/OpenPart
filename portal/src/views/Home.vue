<!-- portal/src/views/Home.vue (优化版本 - 重新设计页脚) -->
<template>
  <div class="home">
    <!-- 全局导航 -->
    <GlobalNavigation />
    
    <!-- 主要内容区 -->
    <main class="main">
      <div class="hero-section">
        <div class="container container-sm">
          <div class="hero-content">
            <h2 class="hero-title">
              {{ config.hero.title }}
              <span class="highlight">{{ config.hero.highlight }}</span>
            </h2>
            <p class="hero-subtitle">
              {{ config.hero.subtitle }}
            </p>
            
            <!-- 搜索框 -->
            <div class="search-section">
              <SearchBox 
                :size="'large'"
                :auto-focus="true"
                :placeholder="config.hero.searchPlaceholder"
                @search="onSearch"
              />
              
              <!-- 热门搜索 -->
              <div class="popular-searches">
                <span class="popular-label">热门搜索:</span>
                <button 
                  v-for="tag in config.popularTags" 
                  :key="tag"
                  class="popular-tag"
                  @click="searchTag(tag)"
                >
                  {{ tag }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 功能快捷入口 -->
      <section class="features-section">
        <div class="container">
          <div class="features-grid">
            <router-link to="/search" class="feature-card">
              <div class="feature-icon search">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3>搜索零件</h3>
              <p>浏览数千个电子零件</p>
            </router-link>
            
            <router-link to="/favorites" class="feature-card favorites">
              <div class="feature-icon">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
              <h3>我的收藏</h3>
              <p>{{ favoritesCount }} 个收藏零件</p>
              <div v-if="favoritesCount > 0" class="feature-badge">{{ favoritesCount }}</div>
            </router-link>
            
            <router-link to="/projects" class="feature-card projects">
              <div class="feature-icon">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <h3>项目清单</h3>
              <p>{{ projectsCount }} 个进行中项目</p>
              <div v-if="projectsCount > 0" class="feature-badge">{{ projectsCount }}</div>
            </router-link>
            
            <div 
              v-if="comparisonCount > 0"
              @click="goToComparison"
              class="feature-card comparison active"
            >
              <div class="feature-icon">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3>零件对比</h3>
              <p>{{ comparisonCount }} 个零件待对比</p>
              <div class="feature-badge comparison">{{ comparisonCount }}</div>
            </div>
          </div>
        </div>
      </section>
      
      <!-- 统计信息 -->
      <section class="stats-section">
        <div class="container">
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-number">{{ displayStats.totalParts }}</div>
              <div class="stat-label">零件总数</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ displayStats.totalCategories }}</div>
              <div class="stat-label">分类数量</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ displayStats.searchCount }}</div>
              <div class="stat-label">搜索次数</div>
            </div>
          </div>
        </div>
      </section>
      
      <!-- 分类展示 -->
      <section class="categories-section">
        <div class="container">
          <h3 class="section-title">浏览分类</h3>
          <div class="categories-grid">
            <div 
              v-for="category in categories" 
              :key="category"
              class="category-card"
              @click="searchCategory(category)"
            >
              <div class="category-icon">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <h4 class="category-name">{{ category }}</h4>
            </div>
          </div>
        </div>
      </section>
    </main>
    
    <!-- 页脚 -->
    <footer class="footer">
      <div class="container">
        <div class="footer-content">
          <!-- 项目介绍 -->
          <div class="footer-section">
            <h5>OpenPart</h5>
            <p>专业的电子零件搜索门户，提供全面的零件信息和项目管理功能，助力您的电子项目开发。</p>
          </div>
          
          <!-- 快速链接 -->
          <div class="footer-section">
            <h5>快速链接</h5>
            <ul>
              <li><a href="#" @click.prevent>关于项目</a></li>
              <li><a href="#" @click.prevent>帮助反馈</a></li>
            </ul>
          </div>
          
          <!-- 项目信息 -->
          <div class="footer-section">
            <h5>项目信息</h5>
            <ul>
              <li><a href="https://github.com/wanglrebe/OpenPart/" target="_blank" rel="noopener noreferrer">GitHub 仓库</a></li>
              <li><span class="footer-text">开源协议: MIT</span></li>
            </ul>
          </div>
        </div>
        
        <div class="footer-bottom">
          <p>&copy; 2024 OpenPart. 开源零件搜索平台</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import GlobalNavigation from '../components/GlobalNavigation.vue'
import SearchBox from '../components/SearchBox.vue'
import { partsAPI, statsAPI, favoritesManager, comparisonManager } from '../utils/api'
import { siteConfig } from '../config/site'

export default {
  name: 'Home',
  components: {
    GlobalNavigation,
    SearchBox
  },
  setup() {
    const router = useRouter()
    const config = siteConfig
    const categories = ref([])
    const realTimeStats = ref({
      totalParts: 0,
      totalCategories: 0,
      searchCount: '0'
    })
    
    // 功能卡片状态
    const favoritesCount = ref(0)
    const projectsCount = ref(0)
    const comparisonCount = ref(0)
    
    // 显示的统计数据
    const displayStats = computed(() => {
      if (config.stats.enableRealTimeStats) {
        return realTimeStats.value
      } else {
        return {
          totalParts: realTimeStats.value.totalParts || 0,
          totalCategories: realTimeStats.value.totalCategories || 0,
          searchCount: config.stats.searchCountDisplay
        }
      }
    })
    
    // 更新功能卡片计数
    const updateFeatureCounts = () => {
      favoritesCount.value = favoritesManager.getFavoritesCount()
      comparisonCount.value = comparisonManager.getComparisonCount()
      
      // 获取项目数量
      const projects = JSON.parse(localStorage.getItem('openpart_projects') || '[]')
      projectsCount.value = projects.length
    }
    
    const loadData = async () => {
      try {
        // 获取分类
        const categoriesResponse = await partsAPI.getCategories()
        categories.value = categoriesResponse.data
        
        // 获取统计数据
        if (config.stats.enableRealTimeStats) {
          const stats = await statsAPI.getRealTimeStats()
          realTimeStats.value = stats
        } else {
          // 只获取基本数据用于显示
          const partsResponse = await partsAPI.getParts({ limit: 100 })
          realTimeStats.value.totalParts = partsResponse.data.length
          realTimeStats.value.totalCategories = categories.value.length
        }
        
      } catch (error) {
        console.error('加载数据失败:', error)
      }
    }
    
    const onSearch = (query) => {
      // 增加搜索计数
      statsAPI.incrementSearchCount()
      
      router.push({
        name: 'Search',
        query: { q: query }
      })
    }
    
    const searchTag = (tag) => {
      statsAPI.incrementSearchCount()
      
      router.push({
        name: 'Search',
        query: { q: tag }
      })
    }
    
    const searchCategory = (category) => {
      router.push({
        name: 'Search',
        query: { category: category }
      })
    }
    
    const goToComparison = () => {
      const compareUrl = comparisonManager.getComparisonUrl()
      if (compareUrl) {
        router.push(compareUrl)
      }
    }
    
    // 监听存储变化
    const handleStorageChange = (e) => {
      if (['openpart_favorites', 'openpart_comparison', 'openpart_projects'].includes(e.key)) {
        updateFeatureCounts()
      }
    }
    
    onMounted(() => {
      loadData()
      updateFeatureCounts()
      window.addEventListener('storage', handleStorageChange)
    })
    
    onUnmounted(() => {
      window.removeEventListener('storage', handleStorageChange)
    })
    
    return {
      config,
      categories,
      displayStats,
      favoritesCount,
      projectsCount,
      comparisonCount,
      onSearch,
      searchTag,
      searchCategory,
      goToComparison
    }
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 主要内容 */
.main {
  flex: 1;
}

.hero-section {
  padding: 80px 0 120px;
  background: linear-gradient(135deg, 
    color-mix(in srgb, var(--primary) 5%, var(--bg-primary)),
    color-mix(in srgb, var(--secondary) 3%, var(--bg-primary))
  );
  position: relative;
  overflow: visible;
  z-index: 10;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 30% 20%, 
    color-mix(in srgb, var(--primary) 8%, transparent) 0%,
    transparent 50%
  );
}

.hero-content {
  text-align: center;
  position: relative;
  z-index: 1;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 16px 0;
  line-height: 1.2;
}

.highlight {
  color: var(--primary);
  position: relative;
}

.highlight::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--primary), var(--secondary));
  border-radius: 2px;
}

.hero-subtitle {
  font-size: 18px;
  color: var(--text-secondary);
  margin: 0 0 40px 0;
  line-height: 1.6;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.search-section {
  max-width: 600px;
  margin: 0 auto;
}

.popular-searches {
  margin-top: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 8px;
}

.popular-label {
  font-size: 14px;
  color: var(--text-muted);
  margin-right: 8px;
}

.popular-tag {
  padding: 6px 12px;
  font-size: 13px;
  color: var(--primary);
  background: color-mix(in srgb, var(--primary) 10%, transparent);
  border: 1px solid color-mix(in srgb, var(--primary) 20%, transparent);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.popular-tag:hover {
  background: var(--primary);
  color: white;
  transform: translateY(-1px);
}

/* 功能快捷入口 */
.features-section {
  padding: 60px 0;
  background: var(--bg-card);
  position: relative;
  z-index: 1;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
}

.feature-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  text-decoration: none;
  color: inherit;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  display: block;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--primary);
}

.feature-card.favorites:hover {
  border-color: #e11d48;
}

.feature-card.projects:hover {
  border-color: #0ea5e9;
}

.feature-card.comparison {
  background: color-mix(in srgb, #f59e0b 5%, var(--bg-primary));
  border-color: color-mix(in srgb, #f59e0b 20%, var(--border-color));
}

.feature-card.comparison:hover {
  border-color: #f59e0b;
  background: color-mix(in srgb, #f59e0b 10%, var(--bg-primary));
}

.feature-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 16px;
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--primary) 10%, transparent);
  border-radius: 12px;
}

.feature-card.favorites .feature-icon {
  color: #e11d48;
  background: color-mix(in srgb, #e11d48 10%, transparent);
}

.feature-card.projects .feature-icon {
  color: #0ea5e9;
  background: color-mix(in srgb, #0ea5e9 10%, transparent);
}

.feature-card.comparison .feature-icon {
  color: #f59e0b;
  background: color-mix(in srgb, #f59e0b 15%, transparent);
}

.feature-icon svg {
  width: 24px;
  height: 24px;
}

.feature-card h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.feature-card p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.feature-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: var(--primary);
  color: white;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 12px;
  min-width: 24px;
  text-align: center;
}

.feature-badge.comparison {
  background: #f59e0b;
}

/* 统计信息 */
.stats-section {
  padding: 60px 0;
  background: var(--bg-secondary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 40px;
  text-align: center;
}

.stat-item {
  padding: 20px;
}

.stat-number {
  font-size: 36px;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

/* 分类展示 */
.categories-section {
  padding: 80px 0;
}

.section-title {
  text-align: center;
  font-size: 32px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 48px 0;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
}

.category-card {
  padding: 32px 24px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--primary);
}

.category-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 16px;
  color: var(--primary);
}

.category-icon svg {
  width: 100%;
  height: 100%;
}

.category-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

/* 页脚 */
.footer {
  background: var(--bg-secondary);
  padding: 48px 0 24px;
  margin-top: auto;
}

.footer-content {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 48px;
  margin-bottom: 32px;
}

.footer-section h5 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.footer-section p {
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.6;
  font-size: 14px;
}

.footer-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-section li {
  margin-bottom: 8px;
}

.footer-section a {
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.2s ease;
  font-size: 14px;
}

.footer-section a:hover {
  color: var(--primary);
}

.footer-text {
  color: var(--text-secondary);
  font-size: 14px;
}

.footer-bottom {
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
  text-align: center;
}

.footer-bottom p {
  color: var(--text-muted);
  margin: 0;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-section {
    padding: 60px 0 80px;
  }
  
  .hero-title {
    font-size: 32px;
  }
  
  .hero-subtitle {
    font-size: 16px;
  }
  
  .popular-searches {
    justify-content: flex-start;
  }
  
  .features-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
  }
  
  .feature-card {
    padding: 20px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 24px;
  }
  
  .stat-number {
    font-size: 28px;
  }
  
  .section-title {
    font-size: 24px;
  }
  
  .categories-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px;
  }
  
  .category-card {
    padding: 24px 16px;
  }
  
  .footer-content {
    grid-template-columns: 1fr;
    gap: 32px;
  }
}
</style>