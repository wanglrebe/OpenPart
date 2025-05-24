<!-- frontend/src/App.vue -->
<template>
  <div id="app">
    <el-container>
      <el-header class="header">
        <h1>OpenPart 零件管理系统</h1>
        <el-menu mode="horizontal" :default-active="$route.path.split('/')[1]" router>
          <el-menu-item index="parts">零件管理</el-menu-item>
          <el-menu-item index="about">关于</el-menu-item>
        </el-menu>
      </el-header>
      
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
.header {
  background-color: #545c64;
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header h1 {
  margin: 0;
  color: white;
}

.el-menu--horizontal {
  border-bottom: none;
}
</style>