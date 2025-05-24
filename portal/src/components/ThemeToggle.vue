<template>
  <button 
    @click="toggleTheme" 
    class="theme-toggle"
    :title="currentTheme === 'light' ? '切换到暗黑模式' : '切换到明亮模式'"
  >
    <svg 
      v-if="currentTheme === 'light'" 
      class="icon" 
      fill="none" 
      stroke="currentColor" 
      viewBox="0 0 24 24"
    >
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
    </svg>
    <svg 
      v-else 
      class="icon" 
      fill="none" 
      stroke="currentColor" 
      viewBox="0 0 24 24"
    >
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
    </svg>
  </button>
</template>

<script>
import { useTheme } from '../utils/theme'

export default {
  name: 'ThemeToggle',
  setup() {
    const { currentTheme, toggleTheme } = useTheme()
    
    return {
      currentTheme,
      toggleTheme
    }
  }
}
</script>

<style scoped>
.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: var(--bg-card);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: var(--shadow-sm);
}

.theme-toggle:hover {
  background: var(--bg-secondary);
  transform: scale(1.05);
  box-shadow: var(--shadow-md);
}

.icon {
  width: 20px;
  height: 20px;
}
</style>