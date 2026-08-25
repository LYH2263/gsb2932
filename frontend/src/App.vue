<template>
  <el-container>
    <el-header v-if="!isLoginPage">
      <div class="header-container">
        <div class="logo-area" @click="router.push('/')">
          <img style="width: 40px; margin-right: 10px" :src="logo" alt="Logo" />
          <span>ProgLearn</span>
        </div>
        
        <el-menu 
          :default-active="activeIndex" 
          class="el-menu-demo" 
          mode="horizontal" 
          router
          :ellipsis="false"
        >
          <el-menu-item index="/courses">课程</el-menu-item>
          <el-menu-item index="/community">社区</el-menu-item>
          <el-menu-item index="/challenges">挑战赛</el-menu-item>
          <el-menu-item index="/sandbox">代码沙盒</el-menu-item>
        </el-menu>
        
        <div class="user-area">
          <template v-if="!authStore.isAuthenticated">
            <el-button type="primary" link @click="router.push('/login')">登录 / 注册</el-button>
          </template>
          <template v-else>
            <el-dropdown trigger="click" @command="handleUserCommand">
              <span class="avatar-trigger">
                <el-avatar :size="32" :src="authStore.user?.avatar">
                  <el-icon><User /></el-icon>
                </el-avatar>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="user">用户中心</el-dropdown-item>
                  <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </div>
      </div>
    </el-header>
    
    <el-main :class="{ 'no-padding': isLoginPage, 'login-page': isLoginPage }">
      <router-view />
    </el-main>
    
    <AchievementNotification 
      v-if="currentAchievement"
      :achievement="currentAchievement"
      :visible="notificationVisible"
      @close="hideNotification"
    />

  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, watchEffect, provide } from 'vue'
import { useAuthStore } from './stores/auth'
import { useRouter, useRoute } from 'vue-router'
import { User } from '@element-plus/icons-vue'
import logo from './assets/vue.svg'
import AchievementNotification from './components/AchievementNotification.vue'
import { setAchievementHandler } from './utils/request'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const activeIndex = computed(() => route.path)
const isLoginPage = computed(() => route.path === '/login')

const currentAchievement = ref(null)
const notificationVisible = ref(false)
const achievementQueue = ref([])

const showAchievementNotification = (achievement) => {
  achievementQueue.value.push(achievement)
  if (!notificationVisible.value) {
    displayNextAchievement()
  }
}

const displayNextAchievement = () => {
  if (achievementQueue.value.length > 0) {
    currentAchievement.value = achievementQueue.value.shift()
    notificationVisible.value = true
  }
}

const hideNotification = () => {
  notificationVisible.value = false
  currentAchievement.value = null
  setTimeout(() => {
    displayNextAchievement()
  }, 300)
}

provide('showAchievement', showAchievementNotification)

setAchievementHandler((achievement) => {
  showAchievementNotification(achievement)
})

onMounted(async () => {
  if (authStore.token && !authStore.user) {
    try {
      await authStore.fetchUser()
    } catch (error) {
      authStore.logout()
    }
  }
})

watchEffect(() => {
  document.body.classList.toggle('no-scroll', isLoginPage.value)
  document.documentElement.classList.toggle('no-scroll', isLoginPage.value)
})

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

const handleUserCommand = (command) => {
  if (command === 'user') {
    router.push('/user')
  } else if (command === 'logout') {
    handleLogout()
  }
}
</script>

<style scoped>
.header-container {
  display: flex;
  align-items: center;
  height: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.logo-area {
  display: flex;
  align-items: center;
  cursor: pointer;
  margin-right: 40px;
  font-weight: bold;
  font-size: 18px;
  color: #303133;
}

.el-menu-demo {
  flex-grow: 1;
  border-bottom: none !important;
  background: transparent;
}

.user-area {
  margin-left: auto;
  display: flex;
  align-items: center;
}

.avatar-trigger {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.el-header {
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 1000;
  background: #ffffff;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.el-main.no-padding {
  padding: 0;
  overflow: hidden;
}

.el-main.login-page {
  min-height: 100vh;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at top left, #e6f1ff 0%, #f7f9fc 45%, #f7f0ff 100%);
}

</style>
