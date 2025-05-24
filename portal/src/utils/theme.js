import { ref } from 'vue'

const currentTheme = ref(localStorage.getItem('theme') || 'light')

export function useTheme() {
  const toggleTheme = () => {
    currentTheme.value = currentTheme.value === 'light' ? 'dark' : 'light'
    localStorage.setItem('theme', currentTheme.value)
    updateTheme()
  }
  
  const setTheme = (theme) => {
    currentTheme.value = theme
    localStorage.setItem('theme', theme)
    updateTheme()
  }
  
  const updateTheme = () => {
    document.documentElement.setAttribute('data-theme', currentTheme.value)
    document.body.setAttribute('data-theme', currentTheme.value)
  }
  
  const initTheme = () => {
    // 检测系统偏好
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    const savedTheme = localStorage.getItem('theme')
    
    if (!savedTheme) {
      currentTheme.value = prefersDark ? 'dark' : 'light'
      localStorage.setItem('theme', currentTheme.value)
    }
    
    updateTheme()
    
    // 监听系统主题变化
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem('theme')) {
        currentTheme.value = e.matches ? 'dark' : 'light'
        updateTheme()
      }
    })
  }
  
  return {
    currentTheme,
    toggleTheme,
    setTheme,
    initTheme
  }
}