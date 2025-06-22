export const siteConfig = {
  // 站点基本信息
  title: 'OpenPart',
  subtitle: '零件搜索门户',
  description: '搜索数千个零件的详细规格参数，找到最适合您项目的零件',
  
  // 首页配置
  hero: {
    title: '发现完美的',
    highlight: '零件', // 通用化，去掉"电子"限定
    subtitle: '搜索数千个零件的详细规格参数，找到最适合您项目的零件',
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
  
  // 热门搜索标签（可根据实际应用场景调整）
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
    projectDescription: '通用的零件搜索数据平台，提供全面的零件信息和项目管理功能，助力您的项目开发。',
    copyright: '© 2024 OpenPart. 开源零件搜索平台'
  }
}