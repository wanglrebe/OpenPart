<template>
  <div class="home">
    <!-- 头部导航 -->
    <header class="header">
      <div class="container">
        <div class="nav">
          <div class="logo">
            <h1>OpenPart</h1>
            <span class="tagline">零件搜索门户</span>
          </div>
          
          <div class="nav-actions">
            <ThemeToggle />
          </div>
        </div>
      </div>
    </header>
    
    <!-- 主要内容区 -->
    <main class="main">
      <div class="hero-section">
        <div class="container container-sm">
          <div class="hero-content">
            <h2 class="hero-title">
              发现完美的
              <span class="highlight">电子零件</span>
            </h2>
            <p class="hero-subtitle">
              搜索数千个电子元件的详细规格参数，找到最适合您项目的零件
            </p>
            
            <!-- 搜索框 -->
            <div class="search-section">
              <SearchBox 
                :size="'large'"
                :auto-focus="true"
                placeholder="搜索零件型号、参数或分类..."
                @search="onSearch"
              />
              
              <!-- 热门搜索 -->
              <div class="popular-searches">
                <span class="popular-label">热门搜索:</span>
                <button 
                  v-for="tag in popularTags" 
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
      
      <!-- 统计信息 -->
      <section class="stats-section">
        <div class="container">
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-number">{{ stats.totalParts }}</div>
              <div class="stat-label">零件总数</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ stats.totalCategories }}</div>
              <div class="stat-label">分类数量</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ stats.searchCount }}</div>
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
          <div class="footer-section">
            <h5>OpenPart</h5>
            <p>开源零件数据管理系统</p>
          </div>
          <div class="footer-section">
            <h5>功能</h5>
            <ul>
              <li>零件搜索</li>
              <li>参数对比</li>
              <li>分类浏览</li>
            </ul>
          </div>
          <div class="footer-section">
            <h5>关于</h5>
            <ul>
              <li>项目介绍</li>
              <li>使用帮助</li>
              <li>GitHub</li>
            </ul>
          </div>
        </div>
        <div class="footer-bottom">
          <p>&copy; 2024 OpenPart. 开源项目.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ThemeToggle from '../components/ThemeToggle.vue'
import SearchBox from '../components/SearchBox.vue'
import { partsAPI } from '../utils/api'

export default {
  name: 'Home',
  components: {
    ThemeToggle,
    SearchBox
  },
  setup() {
    const router = useRouter()
    const categories = ref([])
    const stats = ref({
      totalParts: 0,
      totalCategories: 0,
      searchCount: '1000+'
    })
    
    const popularTags = [
      'Arduino', '电阻', '5V', 'LED', '微控制器'
    ]
    
    const loadData = async () => {
      try {
        // 获取分类
        const categoriesResponse = await partsAPI.getCategories()
        categories.value = categoriesResponse.data
        
        // 获取零件统计
        const partsResponse = await partsAPI.getParts({ limit: 1000 })
        stats.value.totalParts = partsResponse.data.length
        stats.value.totalCategories = categories.value.length
        
      } catch (error) {
        console.error('加载数据失败:', error)
      }
    }
    
    const onSearch = (query) => {
      router.push({
        name: 'Search',
        query: { q: query }
      })
    }
    
    const searchTag = (tag) => {
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
    
    onMounted(() => {
      loadData()
    })
    
    return {
      categories,
      stats,
      popularTags,
      onSearch,
      searchTag,
      searchCategory
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

/* 头部导航 */
.header {
  padding: 16px 0;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(8px);
}

.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--primary);
}

.tagline {
  font-size: 12px;
  color: var(--text-muted);
  margin-left: 8px;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
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
  overflow: hidden;
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

/* 统计信息 */
.stats-section {
  padding: 60px 0;
  background: var(--bg-card);
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
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 32px;
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
}

.footer-section a:hover {
  color: var(--primary);
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
    gap: 24px;
  }
}
</style>