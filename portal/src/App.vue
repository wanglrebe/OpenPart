<template>
  <div id="app" :data-theme="currentTheme">
    <router-view />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useTheme } from './utils/theme'

export default {
  name: 'App',
  setup() {
    const { currentTheme, initTheme } = useTheme()
    
    onMounted(() => {
      initTheme()
    })
    
    return {
      currentTheme
    }
  }
}
</script>

<style>
#app {
  min-height: 100vh;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  transition: all 0.3s ease;
}
</style>