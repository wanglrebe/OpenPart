<template>
  <div class="about">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>关于 OpenPart</span>
        </div>
      </template>
      
      <div class="content">
        <h2>OpenPart - 开源零件数据管理系统</h2>
        <p>OpenPart 是一个开源的零件数据管理系统，旨在为个人和组织提供简单、高效的零件信息管理解决方案。</p>
        
        <h3>主要特性</h3>
        <ul>
          <li>零件信息的增删改查</li>
          <li>灵活的自定义属性系统</li>
          <li>基于插件的扩展架构</li>
          <li>现代化的 Web 界面</li>
          <li>完全开源，免费使用</li>
        </ul>
        
        <h3>技术栈</h3>
        <ul>
          <li>后端：FastAPI + PostgreSQL</li>
          <li>前端：Vue 3 + Element Plus</li>
          <li>数据库：PostgreSQL with JSON support</li>
        </ul>
        
        <p style="margin-top: 30px;">
          <strong>版本：</strong>0.1.0 (MVP)<br>
          <strong>许可证：</strong>MIT License<br>
          <strong>项目地址：</strong><a href="https://github.com/your-username/OpenPart" target="_blank">GitHub</a>
        </p>
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'About'
}
</script>

<style scoped>
.content {
  line-height: 1.6;
}

.content h2 {
  color: #409EFF;
  margin-bottom: 20px;
}

.content h3 {
  color: #606266;
  margin-top: 25px;
  margin-bottom: 15px;
}

.content ul {
  padding-left: 20px;
}

.content li {
  margin-bottom: 8px;
}
</style>