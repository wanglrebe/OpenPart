<!-- src/views/CompatibilityGuide.vue -->
<template>
  <div class="compatibility-guide-page">
    <!-- 全局导航 -->
    <GlobalNavigation />
    
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div class="breadcrumb">
            <router-link to="/" class="breadcrumb-link">首页</router-link>
            <span class="breadcrumb-separator">/</span>
            <router-link to="/compatibility" class="breadcrumb-link">兼容性检查</router-link>
            <span class="breadcrumb-separator">/</span>
            <span class="breadcrumb-current">使用指南</span>
          </div>
          
          <h1 class="page-title">兼容性检查指南</h1>
          <p class="page-description">
            了解如何使用兼容性检查功能，学习零件兼容性知识，获得最佳配置建议
          </p>
        </div>
      </div>
    </div>
    
    <!-- 主要内容 -->
    <main class="main-content">
      <div class="container">
        <div class="guide-layout">
          <!-- 侧边导航 -->
          <aside class="guide-sidebar">
            <nav class="guide-nav">
              <div class="nav-section">
                <h3 class="nav-title">快速开始</h3>
                <ul class="nav-list">
                  <li class="nav-item">
                    <a href="#getting-started" class="nav-link" @click="scrollToSection('getting-started')">
                      开始使用
                    </a>
                  </li>
                  <li class="nav-item">
                    <a href="#basic-workflow" class="nav-link" @click="scrollToSection('basic-workflow')">
                      基本流程
                    </a>
                  </li>
                </ul>
              </div>
              
              <div class="nav-section">
                <h3 class="nav-title">兼容性知识</h3>
                <ul class="nav-list">
                  <li class="nav-item">
                    <a href="#compatibility-grades" class="nav-link" @click="scrollToSection('compatibility-grades')">
                      兼容性等级
                    </a>
                  </li>
                  <li class="nav-item">
                    <a href="#common-rules" class="nav-link" @click="scrollToSection('common-rules')">
                      常见规则
                    </a>
                  </li>
                  <li class="nav-item">
                    <a href="#configuration-patterns" class="nav-link" @click="scrollToSection('configuration-patterns')">
                      配置模式
                    </a>
                  </li>
                </ul>
              </div>
              
              <div class="nav-section">
                <h3 class="nav-title">高级功能</h3>
                <ul class="nav-list">
                  <li class="nav-item">
                    <a href="#advanced-features" class="nav-link" @click="scrollToSection('advanced-features')">
                      高级功能
                    </a>
                  </li>
                  <li class="nav-item">
                    <a href="#troubleshooting" class="nav-link" @click="scrollToSection('troubleshooting')">
                      问题排查
                    </a>
                  </li>
                </ul>
              </div>
              
              <div class="nav-section">
                <h3 class="nav-title">社区贡献</h3>
                <ul class="nav-list">
                  <li class="nav-item">
                    <a href="#feedback" class="nav-link" @click="scrollToSection('feedback')">
                      反馈渠道
                    </a>
                  </li>
                  <li class="nav-item">
                    <a href="#faq" class="nav-link" @click="scrollToSection('faq')">
                      常见问题
                    </a>
                  </li>
                </ul>
              </div>
            </nav>
          </aside>
          
          <!-- 指南内容 -->
          <div class="guide-content">
            <!-- 开始使用 -->
            <section id="getting-started" class="guide-section">
              <h2 class="section-title">开始使用</h2>
              <div class="section-content">
                <p class="intro-text">
                  兼容性检查功能帮助您验证多个零件之间的兼容性，确保您的项目配置能够正常工作。
                </p>
                
                <div class="feature-cards">
                  <div class="feature-card">
                    <div class="feature-icon">
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <h3 class="feature-title">智能检查</h3>
                    <p class="feature-description">基于专业规则和用户经验，提供准确的兼容性评估</p>
                  </div>
                  
                  <div class="feature-card">
                    <div class="feature-icon">
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                    </div>
                    <h3 class="feature-title">详细报告</h3>
                    <p class="feature-description">生成完整的兼容性报告，包含评分、建议和问题说明</p>
                  </div>
                  
                  <div class="feature-card">
                    <div class="feature-icon">
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                    </div>
                    <h3 class="feature-title">配置优化</h3>
                    <p class="feature-description">识别配置模式，提供缺失零件建议和兼容性优化</p>
                  </div>
                </div>
                
                <div class="quick-start-button">
                  <router-link to="/compatibility" class="start-btn">
                    <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                    立即开始检查
                  </router-link>
                </div>
              </div>
            </section>
            
            <!-- 基本流程 -->
            <section id="basic-workflow" class="guide-section">
              <h2 class="section-title">基本流程</h2>
              <div class="section-content">
                <div class="workflow-steps">
                  <div class="workflow-step">
                    <div class="step-number">1</div>
                    <div class="step-content">
                      <h3 class="step-title">选择零件</h3>
                      <p class="step-description">
                        在零件选择器中搜索并添加您要检查的零件。系统支持2-10个零件的兼容性检查。
                      </p>
                      <ul class="step-tips">
                        <li>使用关键词搜索零件名称、型号或分类</li>
                        <li>可以按分类筛选搜索结果</li>
                        <li>支持拖拽排序已选零件</li>
                      </ul>
                    </div>
                  </div>
                  
                  <div class="workflow-step">
                    <div class="step-number">2</div>
                    <div class="step-content">
                      <h3 class="step-title">开始检查</h3>
                      <p class="step-description">
                        点击"开始检查"按钮，系统将分析所有零件对之间的兼容性。
                      </p>
                      <ul class="step-tips">
                        <li>检查过程通常需要几秒钟时间</li>
                        <li>系统会显示实时进度</li>
                        <li>检查结果会自动缓存以提高速度</li>
                      </ul>
                    </div>
                  </div>
                  
                  <div class="workflow-step">
                    <div class="step-number">3</div>
                    <div class="step-content">
                      <h3 class="step-title">查看结果</h3>
                      <p class="step-description">
                        查看详细的兼容性报告，包括整体评分、零件对矩阵和优化建议。
                      </p>
                      <ul class="step-tips">
                        <li>整体评分反映整个配置的兼容性</li>
                        <li>矩阵显示每对零件的具体兼容情况</li>
                        <li>注意查看警告和优化建议</li>
                      </ul>
                    </div>
                  </div>
                  
                  <div class="workflow-step">
                    <div class="step-number">4</div>
                    <div class="step-content">
                      <h3 class="step-title">配置优化</h3>
                      <p class="step-description">
                        使用配置分析功能，获得智能推荐和缺失零件建议。
                      </p>
                      <ul class="step-tips">
                        <li>系统会识别常见的配置模式</li>
                        <li>提供缺失类别的优先级建议</li>
                        <li>可一键添加推荐零件</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </section>
            
            <!-- 兼容性等级 -->
            <section id="compatibility-grades" class="guide-section">
              <h2 class="section-title">兼容性等级说明</h2>
              <div class="section-content">
                <p class="intro-text">
                  系统使用四级评分体系来表示零件之间的兼容性程度：
                </p>
                
                <div class="grades-list">
                  <div class="grade-item official">
                    <div class="grade-indicator">
                      <span class="grade-icon">✅</span>
                      <span class="grade-score">90-100分</span>
                    </div>
                    <div class="grade-info">
                      <h3 class="grade-title">官方支持</h3>
                      <p class="grade-description">
                        官方确认兼容，完全支持。这些零件组合经过制造商测试和验证，可以安全使用。
                      </p>
                      <div class="grade-example">
                        <strong>示例：</strong> Intel CPU与同平台Intel主板
                      </div>
                    </div>
                  </div>
                  
                  <div class="grade-item unofficial">
                    <div class="grade-indicator">
                      <span class="grade-icon">🔷</span>
                      <span class="grade-score">70-89分</span>
                    </div>
                    <div class="grade-info">
                      <h3 class="grade-title">社区验证</h3>
                      <p class="grade-description">
                        用户验证可用，可能有限制。这些组合虽未获得官方确认，但有用户成功使用的经验。
                      </p>
                      <div class="grade-example">
                        <strong>示例：</strong> 超频内存在标准主板上使用
                      </div>
                    </div>
                  </div>
                  
                  <div class="grade-item theoretical">
                    <div class="grade-indicator">
                      <span class="grade-icon">⚠️</span>
                      <span class="grade-score">50-69分</span>
                    </div>
                    <div class="grade-info">
                      <h3 class="grade-title">理论兼容</h3>
                      <p class="grade-description">
                        理论上兼容，建议实际测试。这些组合在技术规格上应该兼容，但缺少实际验证。
                      </p>
                      <div class="grade-example">
                        <strong>示例：</strong> 新发布的零件与现有零件的组合
                      </div>
                    </div>
                  </div>
                  
                  <div class="grade-item incompatible">
                    <div class="grade-indicator">
                      <span class="grade-icon">❌</span>
                      <span class="grade-score">0-49分</span>
                    </div>
                    <div class="grade-info">
                      <h3 class="grade-title">不兼容</h3>
                      <p class="grade-description">
                        不兼容或存在已知问题。
                      </p>
                        <p class="grade-description">
                        不兼容或存在已知问题。这些零件组合可能导致系统无法正常工作或存在安全风险。
                      </p>
                      <div class="grade-example">
                        <strong>示例：</strong> DDR4内存与只支持DDR3的主板
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>
            
            <!-- 常见规则 -->
            <section id="common-rules" class="guide-section">
              <h2 class="section-title">常见兼容性规则</h2>
              <div class="section-content">
                <div class="rules-grid">
                  <div class="rule-card">
                    <div class="rule-header">
                      <div class="rule-icon power">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                      </div>
                      <h3 class="rule-title">电源功率兼容性</h3>
                    </div>
                    <p class="rule-description">
                      检查电源功率是否满足所有组件的需求，确保系统稳定运行。
                    </p>
                    <div class="rule-formula">
                      <code>电源额定功率 ≥ 所有组件功耗总和 × 1.2</code>
                    </div>
                  </div>
                  
                  <div class="rule-card">
                    <div class="rule-header">
                      <div class="rule-icon interface">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v14a2 2 0 002 2z" />
                        </svg>
                      </div>
                      <h3 class="rule-title">接口兼容性</h3>
                    </div>
                    <p class="rule-description">
                      验证连接器和接口类型是否匹配，确保零件能够正确连接。
                    </p>
                    <div class="rule-formula">
                      <code>CPU插槽 = 主板插槽</code>
                    </div>
                  </div>
                  
                  <div class="rule-card">
                    <div class="rule-header">
                      <div class="rule-icon size">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                        </svg>
                      </div>
                      <h3 class="rule-title">尺寸兼容性</h3>
                    </div>
                    <p class="rule-description">
                      确保物理尺寸和空间要求匹配，避免安装冲突。
                    </p>
                    <div class="rule-formula">
                      <code>显卡长度 ≤ 机箱最大支持长度</code>
                    </div>
                  </div>
                  
                  <div class="rule-card">
                    <div class="rule-header">
                      <div class="rule-icon frequency">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                        </svg>
                      </div>
                      <h3 class="rule-title">频率兼容性</h3>
                    </div>
                    <p class="rule-description">
                      检查工作频率和时序兼容性，确保信号传输正常。
                    </p>
                    <div class="rule-formula">
                      <code>内存频率 ≤ 主板最大支持频率</code>
                    </div>
                  </div>
                </div>
              </div>
            </section>
            
            <!-- 配置模式 -->
            <section id="configuration-patterns" class="guide-section">
              <h2 class="section-title">常见配置模式</h2>
              <div class="section-content">
                <p class="intro-text">
                  系统内置了多种常见的配置模式识别，帮助您快速完善配置：
                </p>
                
                <div class="patterns-grid">
                  <div class="pattern-card">
                    <div class="pattern-header">
                      <div class="pattern-icon computer">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                        </svg>
                      </div>
                      <h3 class="pattern-title">计算机配置</h3>
                    </div>
                    <p class="pattern-description">完整的台式机硬件配置</p>
                    <div class="pattern-components">
                      <h4>必需组件：</h4>
                      <ul>
                        <li>处理器 (CPU)</li>
                        <li>主板</li>
                        <li>内存条</li>
                        <li>存储设备</li>
                        <li>电源供应器</li>
                      </ul>
                      <h4>可选组件：</h4>
                      <ul>
                        <li>独立显卡</li>
                        <li>CPU散热器</li>
                        <li>机箱</li>
                      </ul>
                    </div>
                  </div>
                  
                  <div class="pattern-card">
                    <div class="pattern-header">
                      <div class="pattern-icon arduino">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                        </svg>
                      </div>
                      <h3 class="pattern-title">Arduino项目</h3>
                    </div>
                    <p class="pattern-description">基础Arduino开发项目配置</p>
                    <div class="pattern-components">
                      <h4>必需组件：</h4>
                      <ul>
                        <li>Arduino开发板</li>
                        <li>实验面包板</li>
                        <li>连接线</li>
                        <li>电阻器</li>
                      </ul>
                      <h4>可选组件：</h4>
                      <ul>
                        <li>传感器模块</li>
                        <li>LED指示灯</li>
                        <li>电源模块</li>
                      </ul>
                    </div>
                  </div>
                  
                  <div class="pattern-card">
                    <div class="pattern-header">
                      <div class="pattern-icon iot">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
                        </svg>
                      </div>
                      <h3 class="pattern-title">物联网设备</h3>
                    </div>
                    <p class="pattern-description">连网智能设备配置</p>
                    <div class="pattern-components">
                      <h4>必需组件：</h4>
                      <ul>
                        <li>微控制器</li>
                        <li>无线通信模块</li>
                        <li>传感器</li>
                        <li>电源管理模块</li>
                      </ul>
                      <h4>可选组件：</h4>
                      <ul>
                        <li>数据存储</li>
                        <li>显示模块</li>
                        <li>保护外壳</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </section>
            
            <!-- 高级功能 -->
            <section id="advanced-features" class="guide-section">
              <h2 class="section-title">高级功能</h2>
              <div class="section-content">
                <div class="advanced-features">
                  <div class="feature-section">
                    <h3 class="feature-section-title">URL参数导入</h3>
                    <p>您可以通过URL参数直接加载零件进行检查：</p>
                    <div class="code-example">
                      <code>/compatibility?parts=1,2,3&auto=1</code>
                    </div>
                    <ul class="feature-list">
                      <li><code>parts</code>: 零件ID列表，用逗号分隔</li>
                      <li><code>auto</code>: 设为1时自动开始检查</li>
                      <li><code>detail</code>: 详细程度 (basic/standard/detailed)</li>
                    </ul>
                  </div>
                  
                  <div class="feature-section">
                    <h3 class="feature-section-title">批量操作</h3>
                    <p>支持批量添加和管理零件：</p>
                    <ul class="feature-list">
                      <li>从项目一键导入所有零件</li>
                      <li>批量添加推荐零件</li>
                      <li>拖拽排序零件优先级</li>
                    </ul>
                  </div>
                  
                  <div class="feature-section">
                    <h3 class="feature-section-title">结果导出</h3>
                    <p>将兼容性检查结果导出为报告：</p>
                    <ul class="feature-list">
                      <li>生成详细的文本报告</li>
                      <li>包含评分、建议和问题说明</li>
                      <li>便于分享和存档</li>
                    </ul>
                  </div>
                  
                  <div class="feature-section">
                    <h3 class="feature-section-title">智能缓存</h3>
                    <p>系统自动缓存检查结果以提高性能：</p>
                    <ul class="feature-list">
                      <li>相同零件组合会快速返回缓存结果</li>
                      <li>缓存有效期24小时</li>
                      <li>支持强制刷新检查</li>
                    </ul>
                  </div>
                </div>
              </div>
            </section>
            
            <!-- 问题排查 -->
            <section id="troubleshooting" class="guide-section">
              <h2 class="section-title">问题排查</h2>
              <div class="section-content">
                <div class="troubleshooting-items">
                  <div class="trouble-item">
                    <h3 class="trouble-title">🔍 找不到想要的零件</h3>
                    <div class="trouble-solutions">
                      <p><strong>解决方案：</strong></p>
                      <ul>
                        <li>尝试使用不同的关键词搜索</li>
                        <li>检查零件名称拼写是否正确</li>
                        <li>使用分类筛选缩小搜索范围</li>
                        <li>尝试搜索零件的通用名称而非具体型号</li>
                      </ul>
                    </div>
                  </div>
                  
                  <div class="trouble-item">
                    <h3 class="trouble-title">⚠️ 兼容性检查失败</h3>
                    <div class="trouble-solutions">
                      <p><strong>可能原因：</strong></p>
                      <ul>
                        <li>网络连接问题</li>
                        <li>服务器暂时不可用</li>
                        <li>零件信息不完整</li>
                      </ul>
                      <p><strong>解决方案：</strong></p>
                      <ul>
                        <li>检查网络连接</li>
                        <li>稍后重试</li>
                        <li>尝试减少零件数量</li>
                      </ul>
                    </div>
                  </div>
                  
                  <div class="trouble-item">
                    <h3 class="trouble-title">❓ 结果不准确</h3>
                    <div class="trouble-solutions">
                      <p><strong>注意事项：</strong></p>
                      <ul>
                        <li>系统基于现有规则和经验数据</li>
                        <li>新产品可能缺少兼容性数据</li>
                        <li>特殊配置需要额外验证</li>
                      </ul>
                      <p><strong>建议：</strong></p>
                      <ul>
                        <li>查阅官方兼容性列表</li>
                        <li>参考用户社区经验</li>
                        <li>进行实际测试验证</li>
                      </ul>
                    </div>
                  </div>
                  
                  <div class="trouble-item">
                    <h3 class="trouble-title">🐛 页面加载慢</h3>
                    <div class="trouble-solutions">
                      <p><strong>优化建议：</strong></p>
                      <ul>
                        <li>清除浏览器缓存</li>
                        <li>减少同时检查的零件数量</li>
                        <li>使用现代浏览器</li>
                        <li>检查网络连接速度</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </section>
            
            <!-- 反馈渠道 -->
            <section id="feedback" class="guide-section">
              <h2 class="section-title">反馈渠道</h2>
              <div class="section-content">
                <p class="intro-text">
                  您的反馈和贡献对改善系统至关重要。我们欢迎通过以下渠道提供意见：
                </p>
                
                <div v-if="feedbackChannels.length > 0" class="feedback-channels">
                  <div 
                    v-for="channel in feedbackChannels" 
                    :key="channel.name"
                    class="feedback-channel"
                  >
                    <div class="channel-header">
                      <div class="channel-icon" :class="channel.type">
                        <svg v-if="channel.type === 'github'" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                        </svg>
                        <svg v-else-if="channel.type === 'email'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                        <svg v-else-if="channel.type === 'discord'" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
                        </svg>
                        <svg v-else fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                        </svg>
                      </div>
                      <h3 class="channel-name">{{ channel.name }}</h3>
                    </div>
                    <p class="channel-description">{{ channel.description }}</p>
                    <div v-if="channel.guidelines" class="channel-guidelines">
                      <strong>使用指南：</strong> {{ channel.guidelines }}
                    </div>
                    <a :href="channel.url" target="_blank" rel="noopener noreferrer" class="channel-link">
                      访问 {{ channel.name }}
                      <svg class="external-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                    </a>
                  </div>
                </div>
                
                <div v-else class="loading-feedback">
                  <div class="loading-icon">
                    <svg class="spinning" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  </div>
                  <p>加载反馈渠道信息...</p>
                </div>
              </div>
            </section>
            
            <!-- 常见问题 -->
            <section id="faq" class="guide-section">
              <h2 class="section-title">常见问题</h2>
              <div class="section-content">
                <div class="faq-list">
                  <div class="faq-item">
                    <h3 class="faq-question">Q: 为什么有些零件显示"理论兼容"？</h3>
                    <div class="faq-answer">
                      <p>A: "理论兼容"表示根据技术规格这些零件应该可以一起工作，但缺少实际验证或用户反馈。建议：</p>
                      <ul>
                        <li>查看制造商的兼容性列表</li>
                        <li>寻找类似配置的用户评价</li>
                        <li>如果可能，先进行小规模测试</li>
                      </ul>
                    </div>
                  </div>
                  
                  <div class="faq-item">
                    <h3 class="faq-question">Q: 系统支持检查多少个零件？</h3>
                    <div class="faq-answer">
                      <p>A: 系统支持同时检查2-10个零件的兼容性。选择更多零件会提供更全面的分析，但也会增加检查时间。</p>
                    </div>
                  </div>
                  
                  <div class="faq-item">
                    <h3 class="faq-question">Q: 如何提高兼容性检查的准确性？</h3>
                    <div class="faq-answer">
                      <p>A: 准确性取决于零件信息的完整性：</p>
                      <ul>
                        <li>确保选择了正确的零件型号</li>
                        <li>关注系统给出的警告信息</li>
                        <li>结合其他资源进行验证</li>
                        <li>向社区贡献您的使用经验</li>
                      </ul>
                    </div>
                  </div>
                  
                  <div class="faq-item">
                    <h3 class="faq-question">Q: 配置分析功能如何工作？</h3>
                    <div class="faq-answer">
                      <p>A: 配置分析会：</p>
                      <ul>
                        <li>识别您当前配置符合的模式（如计算机配置、Arduino项目等）</li>
                        <li>分析缺失的关键零件类别</li>
                        <li>推荐兼容的零件来完善配置</li>
                        <li>提供配置完整度评估</li>
                      </ul>
                    </div>
                  </div>
                  
                  <div class="faq-item">
                    <h3 class="faq-question">Q: 能否保存检查结果？</h3>
                    <div class="faq-answer">
                      <p>A: 是的，您可以：</p>
                      <ul>
                        <li>导出详细的兼容性报告</li>
                        <li>通过URL分享检查配置</li>
                        <li>将零件添加到项目中长期保存</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import GlobalNavigation from '../components/GlobalNavigation.vue'
import { compatibilityAPI } from '../utils/api'

export default {
  name: 'CompatibilityGuide',
  components: {
    GlobalNavigation
  },
  setup() {
    const feedbackChannels = ref([])
    const loadingFeedback = ref(false)
    
    // 加载反馈渠道信息
    const loadFeedbackChannels = async () => {
      loadingFeedback.value = true
      try {
        const response = await compatibilityAPI.feedbackChannels()
        feedbackChannels.value = response.channels || []
      } catch (error) {
        console.error('加载反馈渠道失败:', error)
        // 使用默认渠道
        feedbackChannels.value = [
          {
            name: 'GitHub Issues',
            type: 'github',
            url: 'https://github.com/wanglrebe/OpenPart/issues',
            description: '通过GitHub Issues报告兼容性问题或贡献经验',
            guidelines: '请使用 "compatibility" 标签，并提供详细的零件信息和测试结果'
          },
          {
            name: '邮件反馈',
            type: 'email',
            url: 'mailto:feedback@openpart.org',
            description: '通过邮件发送兼容性报告',
            guidelines: '邮件标题请以 [兼容性] 开头，并附上相关文档或图片'
          }
        ]
      } finally {
        loadingFeedback.value = false
      }
    }
    
    // 平滑滚动到指定区域
    const scrollToSection = (sectionId) => {
      const element = document.getElementById(sectionId)
      if (element) {
        element.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        })
      }
    }
    
    onMounted(() => {
      loadFeedbackChannels()
    })
    
    return {
      feedbackChannels,
      loadingFeedback,
      scrollToSection
    }
  }
}
</script>

<style scoped>
.compatibility-guide-page {
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
  font-size: 32px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.page-description {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.6;
  max-width: 600px;
}

/* 主要内容 */
.main-content {
  padding: 32px 0;
}

.guide-layout {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 40px;
  align-items: start;
}

/* 侧边导航 */
.guide-sidebar {
  position: sticky;
  top: 100px;
}

.guide-nav {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px 0;
}

.nav-section {
  margin-bottom: 24px;
}

.nav-section:last-child {
  margin-bottom: 0;
}

.nav-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
  padding: 0 20px;
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  margin-bottom: 4px;
}

.nav-link {
  display: block;
  padding: 8px 20px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 13px;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
}

.nav-link:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-left-color: var(--primary);
}

/* 指南内容 */
.guide-content {
  max-width: none;
}

.guide-section {
  margin-bottom: 48px;
  scroll-margin-top: 100px;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 24px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--border-color);
}

.section-content {
  line-height: 1.6;
}

.intro-text {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0 0 24px 0;
}

/* 功能卡片 */
.feature-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.feature-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  transition: all 0.2s ease;
}

.feature-card:hover {
  border-color: var(--primary);
  box-shadow: var(--shadow-md);
}

.feature-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 16px;
  color: var(--primary);
  background: color-mix(in srgb, var(--primary) 10%, transparent);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.feature-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.feature-description {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.quick-start-button {
  text-align: center;
}

.start-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: var(--primary);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.start-btn:hover {
  background: var(--secondary);
  transform: translateY(-1px);
}

.btn-icon {
  width: 16px;
  height: 16px;
}

/* 工作流程 */
.workflow-steps {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.workflow-step {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.step-number {
  width: 40px;
  height: 40px;
  background: var(--primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.step-description {
  color: var(--text-secondary);
  margin: 0 0 12px 0;
}

.step-tips {
  list-style: none;
  padding: 0;
  margin: 0;
}

.step-tips li {
  color: var(--text-muted);
  font-size: 14px;
  margin-bottom: 4px;
  padding-left: 16px;
  position: relative;
}

.step-tips li::before {
  content: '•';
  color: var(--primary);
  position: absolute;
  left: 0;
}

/* 等级说明 */
.grades-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.grade-item {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.grade-item.official {
  border-left: 4px solid #67C23A;
}

.grade-item.unofficial {
  border-left: 4px solid #409EFF;
}

.grade-item.theoretical {
  border-left: 4px solid #E6A23C;
}

.grade-item.incompatible {
  border-left: 4px solid #F56C6C;
}

.grade-indicator {
  text-align: center;
  flex-shrink: 0;
}

.grade-icon {
  font-size: 24px;
  display: block;
  margin-bottom: 8px;
}

.grade-score {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
}

.grade-info {
  flex: 1;
}

.grade-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.grade-description {
  color: var(--text-secondary);
  margin: 0 0 12px 0;
}

.grade-example {
  font-size: 14px;
  color: var(--text-muted);
  background: var(--bg-secondary);
  padding: 8px 12px;
  border-radius: 6px;
}

/* 规则卡片 */
.rules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.rule-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
}

.rule-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.rule-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.rule-icon.power {
  color: #f59e0b;
}

.rule-icon.interface {
  color: #06b6d4;
}

.rule-icon.size {
  color: #8b5cf6;
}

.rule-icon.frequency {
  color: #f43f5e;
}

.rule-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.rule-description {
  color: var(--text-secondary);
  margin: 0 0 12px 0;
}

.rule-formula {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 8px 12px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: var(--text-primary);
}

/* 配置模式 */
.patterns-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
}

.pattern-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
}

.pattern-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.pattern-icon {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
}

.pattern-icon.computer {
  color: #06b6d4;
}

.pattern-icon.arduino {
  color: #10b981;
}

.pattern-icon.iot {
  color: #8b5cf6;
}

.pattern-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.pattern-description {
  color: var(--text-secondary);
  margin: 0 0 16px 0;
  font-size: 14px;
}

.pattern-components h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 12px 0 6px 0;
}

.pattern-components ul {
  list-style: none;
  padding: 0;
  margin: 0 0 12px 0;
}

.pattern-components li {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 4px;
  padding-left: 16px;
  position: relative;
}

.pattern-components li::before {
  content: '•';
  color: var(--primary);
  position: absolute;
  left: 0;
}

/* 高级功能 */
.advanced-features {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.feature-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
}

.feature-section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.feature-section p {
  color: var(--text-secondary);
  margin: 0 0 12px 0;
}

.code-example {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 12px;
  margin: 12px 0;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  color: var(--text-primary);
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.feature-list li {
  color: var(--text-secondary);
  margin-bottom: 6px;
  padding-left: 16px;
  position: relative;
}

.feature-list li::before {
  content: '•';
  color: var(--primary);
  position: absolute;
  left: 0;
}

.feature-list code {
  background: var(--bg-secondary);
  padding: 2px 4px;
  border-radius: 3px;
  font-size: 12px;
}

/* 问题排查 */
.troubleshooting-items {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.trouble-item {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
}

.trouble-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.trouble-solutions p {
  color: var(--text-secondary);
  margin: 0 0 8px 0;
}

.trouble-solutions ul {
  list-style: none;
  padding: 0;
  margin: 0 0 12px 0;
}

.trouble-solutions li {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 4px;
  padding-left: 16px;
  position: relative;
}

.trouble-solutions li::before {
  content: '•';
  color: var(--primary);
  position: absolute;
  left: 0;
}

/* 反馈渠道 */
.feedback-channels {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.feedback-channel {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
}

.channel-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.channel-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.channel-icon.github {
  color: #333;
}

.channel-icon.email {
  color: #ea4335;
}

.channel-icon.discord {
  color: #5865f2;
}

.channel-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.channel-description {
  color: var(--text-secondary);
  margin: 0 0 12px 0;
}

.channel-guidelines {
  font-size: 13px;
  color: var(--text-muted);
  background: var(--bg-secondary);
  padding: 8px 12px;
  border-radius: 6px;
  margin-bottom: 12px;
}

.channel-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.channel-link:hover {
  color: var(--secondary);
}

.external-icon {
  width: 14px;
  height: 14px;
}

.loading-feedback {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: center;
  padding: 40px;
  color: var(--text-muted);
}

.loading-icon {
  width: 20px;
  height: 20px;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 常见问题 */
.faq-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.faq-item {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
}

.faq-question {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.faq-answer p {
  color: var(--text-secondary);
  margin: 0 0 8px 0;
}

.faq-answer ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.faq-answer li {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 4px;
  padding-left: 16px;
  position: relative;
}

.faq-answer li::before {
  content: '•';
  color: var(--primary);
  position: absolute;
  left: 0;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .guide-layout {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .guide-sidebar {
    position: static;
    order: 2;
  }
  
  .guide-content {
    order: 1;
  }
  
  .feature-cards {
    grid-template-columns: 1fr;
  }
  
  .patterns-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-title {
    font-size: 24px;
  }
  
  .section-title {
    font-size: 20px;
  }
  
  .workflow-step {
    flex-direction: column;
    gap: 12px;
  }
  
  .step-number {
    align-self: flex-start;
  }
  
  .grade-item {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
  
  .rules-grid {
    grid-template-columns: 1fr;
  }
  
  .feedback-channels {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: 16px 0;
  }
  
  .guide-section {
    margin-bottom: 32px;
  }
  
  .feature-card,
  .pattern-card,
  .rule-card,
  .trouble-item,
  .feedback-channel,
  .faq-item {
    padding: 16px;
  }
}
</style>