export const siteConfig = {
  // 站点基本信息
  title: 'OpenPart',
  subtitle: '零件搜索门户',
  description: '搜索数千个电子元件的详细规格参数，找到最适合您项目的零件',
  
  // 首页配置
  hero: {
    title: '发现完美的',
    highlight: '电子零件', // 可改为：机械零件、汽车配件等
    subtitle: '搜索数千个电子元件的详细规格参数，找到最适合您项目的零件',
    searchPlaceholder: '搜索零件型号、参数或分类...'
  },

  // 搜索配置
  search: {
    placeholder: '搜索零件型号、参数或分类... 支持多词搜索',
    searchTip: '支持多词搜索，如："电阻 5V" 或 "Arduino 开发板"',
    showSearchTips: true,
    enableSearchHistory: true,
    maxHistoryItems: 10
  },
  
  // 热门搜索标签
  popularTags: [
    'Arduino', 
    '电阻', 
    '5V', 
    'LED', 
    '微控制器'
  ],
  
  // 统计数据
  stats: {
    searchCountDisplay: '1000+', // 显示的搜索次数
    enableRealTimeStats: false,  // 是否启用实时统计
  },
  
  // 页脚信息
  footer: {
    sections: [
      {
        title: 'OpenPart',
        content: '开源零件数据管理系统'
      },
      {
        title: '功能',
        links: [
          { text: '零件搜索', url: '/search' },
          { text: '参数对比', url: '#' },
          { text: '分类浏览', url: '#' }
        ]
      },
      {
        title: '关于',
        links: [
          { text: '项目介绍', url: '#' },
          { text: '使用帮助', url: '#' },
          { text: 'GitHub', url: 'https://github.com' }
        ]
      }
    ],
    copyright: '© 2024 OpenPart. 开源项目.'
  }
}