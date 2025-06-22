<!-- src/views/About.vue -->
<template>
  <div class="about-page">
    <!-- 全局导航 -->
    <GlobalNavigation />
    
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <div class="breadcrumb">
          <router-link to="/" class="breadcrumb-link">首页</router-link>
          <span class="breadcrumb-separator">/</span>
          <span class="breadcrumb-current">关于项目</span>
        </div>
        
        <h1 class="page-title">关于 OpenPart</h1>
        <p class="page-description">
          通用零件搜索数据平台
        </p>
      </div>
    </div>
    
    <!-- 主要内容 -->
    <main class="main-content">
      <div class="container container-sm">
        
        <!-- 项目简介 -->
        <section class="project-intro">
          <h2>项目简介</h2>
          <div class="intro-content">
            <p>
              OpenPart 是一个通用的零件搜索数据平台，旨在为用户提供便捷的零件搜索、对比和管理功能。
              项目设计时考虑了通用性，不针对特定类型的零件，可以灵活适配各种应用场景。
            </p>
            <p>
              项目的初衷是解决在查找和比较零件时信息分散、缺乏统一平台的问题。
              通过集成搜索、对比、兼容性检查和项目管理功能，为用户提供一站式的零件信息服务。
            </p>
          </div>
        </section>
        
        <!-- 主要功能 -->
        <section class="features-section">
          <h2>主要功能</h2>
          <div class="features-grid">
            <div class="feature-item">
              <div class="feature-icon">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3>零件搜索</h3>
              <p>支持多关键词搜索，按分类筛选，查看详细参数信息</p>
            </div>
            
            <div class="feature-item">
              <div class="feature-icon">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3>参数对比</h3>
              <p>同时对比多个零件的参数，帮助做出选择</p>
            </div>
            
            <div class="feature-item">
              <div class="feature-icon">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3>兼容性检查</h3>
              <p>检查多个零件之间的兼容性，提供配置建议</p>
            </div>
            
            <div class="feature-item">
              <div class="feature-icon">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <h3>项目管理</h3>
              <p>创建项目清单，管理零件收藏夹</p>
            </div>
          </div>
        </section>
        
        <!-- 技术信息 -->
        <section class="tech-section">
          <h2>技术信息</h2>
          <div class="tech-content">
            <div class="tech-info">
              <div class="tech-item">
                <strong>前端框架：</strong> Vue 3 + Vite
              </div>
              <div class="tech-item">
                <strong>开源协议：</strong> MIT License
              </div>
            </div>
          </div>
        </section>
        
        <!-- 开发者 -->
        <section class="developer-section">
          <h2>开发者</h2>
          <div class="developers-grid">
            <div class="developer-card" @click="openGitHubProfile('wanglrebe')">
              <div class="developer-avatar">
                <img 
                  src="https://github.com/wanglrebe.png" 
                  alt="wanglrebe"
                  @error="handleAvatarError"
                />
              </div>
              <div class="developer-info">
                <h3>wanglrebe</h3>
                <p>项目创建者</p>
              </div>
            </div>
            <!-- 预留位置给其他贡献者 -->
          </div>
        </section>
        
        <!-- 项目仓库与支持 -->
        <section class="repository-section">
          <h2>项目仓库</h2>
          <div class="repo-actions">
            <a 
              href="https://github.com/wanglrebe/OpenPart" 
              target="_blank" 
              rel="noopener noreferrer"
              class="action-card primary"
            >
              <div class="action-icon">
                <svg fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
              </div>
              <div class="action-content">
                <h3>查看源码</h3>
                <p>浏览完整项目代码</p>
              </div>
            </a>
            
            <a 
              href="https://github.com/wanglrebe/OpenPart/stargazers" 
              target="_blank" 
              rel="noopener noreferrer"
              class="action-card"
            >
              <div class="action-icon">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                </svg>
              </div>
              <div class="action-content">
                <h3>给项目 Star</h3>
                <p>支持项目发展</p>
              </div>
            </a>
            
            <a 
              href="https://github.com/wanglrebe/OpenPart/issues" 
              target="_blank" 
              rel="noopener noreferrer"
              class="action-card"
            >
              <div class="action-icon">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                </svg>
              </div>
              <div class="action-content">
                <h3>反馈问题</h3>
                <p>报告 bug 或提出建议</p>
              </div>
            </a>
            
            <div class="action-card disabled" title="赞助功能开发中">
              <div class="action-icon">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
              <div class="action-content">
                <h3>赞助项目</h3>
                <p>正在准备中...</p>
              </div>
            </div>
          </div>
        </section>
        
      </div>
    </main>
  </div>
</template>

<script>
import GlobalNavigation from '../components/GlobalNavigation.vue'

export default {
  name: 'About',
  components: {
    GlobalNavigation
  },
  methods: {
    // 头像加载失败处理
    handleAvatarError(event) {
      // 可以设置一个默认头像
      event.target.src = '/default-avatar.png'
    },
    
    // 打开GitHub个人主页
    openGitHubProfile(username) {
      window.open(`https://github.com/${username}`, '_blank')
    }
  }
}
</script>

<style scoped>
.about-page {
  min-height: 100vh;
  background: var(--bg-primary);
}

/* 页面头部 */
.page-header {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  padding: 24px 0;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 14px;
}

.breadcrumb-link {
  color: var(--primary);
  text-decoration: none;
  transition: color 0.2s ease;
}

.breadcrumb-link:hover {
  color: var(--secondary);
}

.breadcrumb-separator {
  color: var(--text-muted);
}

.breadcrumb-current {
  color: var(--text-secondary);
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.page-description {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
}

/* 主要内容 */
.main-content {
  padding: 40px 0;
}

/* 通用区块样式 */
section {
  margin-bottom: 48px;
}

section:last-child {
  margin-bottom: 0;
}

section h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 20px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--border-color);
}

/* 项目介绍 */
.intro-content p {
  color: var(--text-secondary);
  line-height: 1.7;
  margin-bottom: 16px;
}

/* 功能展示 */
.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.feature-item {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  transition: all 0.2s ease;
}

.feature-item:hover {
  border-color: var(--primary);
  transform: translateY(-2px);
}

.feature-icon {
  width: 32px;
  height: 32px;
  color: var(--primary);
  margin: 0 auto 12px;
}

.feature-item h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.feature-item p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

/* 技术信息 */
.tech-info {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
}

.tech-item {
  margin-bottom: 12px;
  font-size: 14px;
  color: var(--text-secondary);
}

.tech-item:last-child {
  margin-bottom: 0;
}

.tech-item strong {
  color: var(--text-primary);
}

/* 开发者网格 */
.developers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.developer-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.developer-card:hover {
  border-color: var(--primary);
  transform: translateY(-2px);
}

.developer-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  margin: 0 auto 12px;
  border: 2px solid var(--border-color);
  transition: border-color 0.2s ease;
}

.developer-card:hover .developer-avatar {
  border-color: var(--primary);
}

.developer-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.developer-info h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.developer-info p {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
}

/* 项目仓库和支持 */
.repo-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.action-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s ease;
}

.action-card:hover {
  border-color: var(--primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.action-card.primary {
  border-color: var(--primary);
  background: linear-gradient(135deg, 
    color-mix(in srgb, var(--primary) 5%, var(--bg-card)),
    var(--bg-card)
  );
}

.action-card.primary:hover {
  background: linear-gradient(135deg, 
    color-mix(in srgb, var(--primary) 10%, var(--bg-card)),
    var(--bg-card)
  );
}

.action-card.disabled {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
}

.action-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  color: var(--primary);
}

.action-content h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.action-content p {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .repo-actions {
    grid-template-columns: 1fr;
  }
  
  .developers-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
  
  .page-title {
    font-size: 24px;
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: 24px 0;
  }
  
  section {
    margin-bottom: 32px;
  }
  
  .feature-item,
  .tech-info,
  .developer-card,
  .action-card {
    padding: 16px;
  }
  
  .action-card {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }
}
</style>