<template>
  <div class="home-container">
    <el-backtop :right="40" :bottom="60" />
    
    <div v-if="authStore.isAuthenticated" class="welcome-banner mb-4">
      <el-card shadow="never" class="banner-card">
        <div class="banner-content">
          <div class="greeting">
            <h2>你好，{{ authStore.user?.username }}，今天想学点什么？</h2>
            <p>今天是 {{ formatDate(new Date()) }}，继续你的编程之旅吧！</p>
          </div>

        </div>
      </el-card>
    </div>

    <el-carousel :interval="4000" height="350px" class="mb-5 carousel-container">
      <el-carousel-item v-for="(item, index) in carouselItems" :key="index">
        <div class="carousel-item" :style="{ backgroundImage: `linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.5)), url(${item.image})` }" @click="item.action">
          <div class="carousel-content">
            <h2>{{ item.title }}</h2>
            <p>{{ item.description }}</p>
            <el-button type="primary" @click.stop="item.action">立即开始</el-button>
          </div>
        </div>
      </el-carousel-item>
    </el-carousel>

    <div v-if="authStore.isAuthenticated" class="progress-section mb-5">
      <h2 class="section-title">学习进度概览</h2>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8">
          <el-card shadow="hover" class="progress-card">
            <template #header>
              <div class="card-header">
                <el-icon><Reading /></el-icon>
                <span>正在学习</span>
              </div>
            </template>
            <div class="current-course" v-if="currentEnrollment">
              <img :src="currentEnrollment.course?.cover_image" alt="课程封面" />
              <div class="course-info">
                <h4>{{ currentEnrollment.course?.title }}</h4>
                <el-progress :percentage="currentEnrollment.progress" :color="getProgressColor(currentEnrollment.progress)" />
                <el-button type="primary" size="small" @click="goToCourse(currentEnrollment.course_id)" class="mt-2">
                  继续学习
                </el-button>
              </div>
            </div>
            <el-empty v-else description="暂无正在学习的课程" />
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8">
          <el-card shadow="hover" class="stat-card">
            <div class="statistic-card">
              <el-statistic title="已完成课程" :value="dashboardData?.completed_courses || 0">
                <template #suffix>门</template>
              </el-statistic>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8">
          <el-card shadow="hover" class="stat-card">
            <div class="statistic-card">
              <el-statistic title="连续学习天数" :value="dashboardData?.consecutive_days || 0">
                <template #suffix>天</template>
              </el-statistic>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="courses-section mb-5">
      <div class="section-header">
        <h2 class="section-title">精选学习路径</h2>
        <el-button text type="primary" @click="viewAllCourses">查看全部</el-button>
      </div>
      <div v-if="!authStore.isAuthenticated" class="login-prompt">
        <el-alert
          title="登录后获取个性化推荐"
          type="info"
          :closable="false"
          show-icon
        >
          <template #default>
            <span>登录后系统将根据您的学习历史为您推荐更适合的课程</span>
            <el-button type="primary" size="small" @click="$router.push('/login')">立即登录</el-button>
          </template>
        </el-alert>
      </div>
      <div v-if="recommendationReason" class="recommendation-reason">
        <el-tag type="success" effect="light" class="reason-tag">
          <el-icon><MagicStick /></el-icon>
          <span>{{ recommendationReason }}</span>
        </el-tag>
      </div>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="6" v-for="course in recommendedCourses" :key="course.id">
          <CourseCard :course="course" @click="goToCourse(course.id)" />
        </el-col>
      </el-row>
    </div>

    <div class="courses-section mb-5">
      <div class="section-header">
        <h2 class="section-title">热门课程</h2>
        <el-button text type="primary" @click="viewAllCourses">查看全部</el-button>
      </div>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="6" v-for="course in hotCourses" :key="course.id">
          <div class="course-wrapper">
            <div v-if="course.new_enrollments > 0" class="trending-badge">
              <el-icon><TrendCharts /></el-icon>
              <span>近7天 {{ course.new_enrollments }} 人加入</span>
            </div>
            <CourseCard :course="course" @click="goToCourse(course.id)" />
          </div>
        </el-col>
      </el-row>
    </div>

    <div class="features-section mb-5">
      <h2 class="section-title">特色功能</h2>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8">
          <el-card shadow="hover" class="feature-card">
            <div class="feature-icon">
              <el-icon :size="48" color="#409EFF"><Monitor /></el-icon>
            </div>
            <h3>在线代码沙盒</h3>
            <p>无需配置环境，直接在浏览器中练习Vue组件和前端代码</p>
            <el-button type="primary" plain @click="$router.push('/sandbox')">立即尝试</el-button>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8">
          <el-card shadow="hover" class="feature-card">
            <div class="feature-icon">
              <el-icon :size="48" color="#67C23A"><Trophy /></el-icon>
            </div>
            <h3>互动挑战赛</h3>
            <p>每周一个前端小挑战，展示你的优秀作品，赢取奖励</p>
          <el-button type="success" plain @click="$router.push('/challenges')">参与挑战</el-button>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8">
          <el-card shadow="hover" class="feature-card">
            <div class="feature-icon">
              <el-icon :size="48" color="#E6A23C"><ChatDotRound /></el-icon>
            </div>
            <h3>社区热议</h3>
            <p>最新、最热的讨论帖展示，与同学交流学习心得</p>
            <el-button type="warning" plain @click="$router.push('/community')">加入讨论</el-button>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="community-section mb-5" v-if="posts.length > 0">
      <div class="section-header">
        <h2 class="section-title">社区热议</h2>
        <el-button text type="primary">查看更多</el-button>
      </div>
      <el-timeline class="timeline">
        <el-timeline-item
          v-for="(post, index) in displayPosts"
          :key="post.id"
          :type="index % 2 === 0 ? 'primary' : 'success'"
          :timestamp="formatDate(post.created_at)"
          placement="top"
        >
          <el-card shadow="hover" class="post-card">
            <div class="post-header">
              <h4>{{ post.title }}</h4>
              <div class="post-stats">
                <el-icon><View /></el-icon>
                <span>{{ post.views }}</span>
                <el-icon><ChatLineSquare /></el-icon>
                <span>{{ getCommentCount(post.id) }}</span>
              </div>
            </div>
            <p class="post-preview">{{ truncateText(post.content, 100) }}</p>
          </el-card>
        </el-timeline-item>
      </el-timeline>
      <div v-if="posts.length > 3" class="text-center">
        <el-button text type="primary" @click="toggleShowPosts">
          {{ showAllPosts ? '收起' : '显示更多' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import { Monitor, Trophy, ChatDotRound, Reading, Timer, View, ChatLineSquare, MagicStick, TrendCharts } from '@element-plus/icons-vue'
import { getRecommendedCourses, getTrendingCourses, getEnrolledCourses } from '../api/course'
import { getDashboard } from '../api/user'
import { getPosts, getChallenges } from '../api/community'
import CourseCard from '../components/CourseCard.vue'

const authStore = useAuthStore()
const router = useRouter()

const recommendedCourses = ref([])
const hotCourses = ref([])
const posts = ref([])
const currentEnrollment = ref(null)
const showAllPosts = ref(false)
const recommendationReason = ref('')
const isPersonalized = ref(false)
const dashboardData = ref(null)

const carouselItems = [
  {
    title: 'Vue 3 渐进式框架入门',
    description: '学习渐进式框架 Vue 3，掌握响应式、组件化与模板语法。',
    image: 'https://placehold.co/1200x400/42b883/ffffff?text=Vue+3+Masterclass',
    action: () => router.push('/courses/7')
  },
  {
    title: 'Python 3 入门',
    description: '从零开始学习 Python 3 语法与基础编程，开启编程之旅',
    image: 'https://placehold.co/1200x400/3776ab/ffffff?text=Python+3',
    action: () => router.push('/courses/4')
  },
  {
    title: 'React 基础与 JSX',
    description: '学习 React 的声明式开发、组件与单向数据流',
    image: 'https://placehold.co/1200x400/61dafb/ffffff?text=React',
    action: () => router.push('/courses/8')
  }
]

const displayPosts = computed(() => {
  return showAllPosts.value ? posts.value : posts.value.slice(0, 3)
})

onMounted(async () => {
  try {
    const [recommendedData, trendingData] = await Promise.all([
      getRecommendedCourses(8),
      getTrendingCourses(7, 8)
    ])
    
    recommendedCourses.value = recommendedData.courses.slice(0, 4)
    hotCourses.value = trendingData.slice(0, 4)
    isPersonalized.value = recommendedData.is_personalized
    
    if (recommendedData.is_personalized) {
      if (recommendedData.reason_course) {
        recommendationReason.value = `因为你学了 ${recommendedData.reason_course}`
      } else if (recommendedData.reason_tags && recommendedData.reason_tags.length > 0) {
        recommendationReason.value = `基于你的兴趣：${recommendedData.reason_tags.join('、')}`
      }
    }
    
    if (authStore.isAuthenticated) {
      await loadUserData()
    }
  } catch (error) {
    console.error('Failed to fetch courses', error)
  }
})

onUnmounted(() => {
})

const loadUserData = async () => {
  try {
    const [enrollments, dashboard] = await Promise.all([
      getEnrolledCourses(),
      getDashboard()
    ])
    currentEnrollment.value = enrollments.find(e => e.progress < 100) || enrollments[0]
    dashboardData.value = dashboard
    posts.value = await getPosts({ limit: 5 })
  } catch (error) {
    console.error('Failed to load user data', error)
  }
}

const formatDate = (date) => {
  const d = new Date(date)
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
}

const truncateText = (text, length) => {
  return text.length > length ? text.substring(0, length) + '...' : text
}

const getCommentCount = (postId) => {
  return Math.floor(Math.random() * 10) + 1
}

const toggleShowPosts = () => {
  showAllPosts.value = !showAllPosts.value
}

const goToCourse = (id) => {
  router.push(`/courses/${id}`)
}

const goToChallenge = () => {
  router.push('/challenges')
}

const viewAllCourses = () => {
  router.push('/courses')
}

const getProgressColor = (percentage) => {
  if (percentage < 30) return '#F56C6C'
  if (percentage < 70) return '#E6A23C'
  return '#67C23A'
}
</script>

<style scoped>
.home-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.welcome-banner {
  margin-bottom: 30px;
}

.banner-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.banner-card :deep(.el-card__body) {
  padding: 30px;
}

.banner-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
}

.banner-content h2 {
  margin: 0 0 10px;
  font-size: 28px;
}

.banner-content p {
  margin: 0;
  opacity: 0.9;
}



.carousel-container {
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 30px;
}

.carousel-item {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.carousel-item:hover {
  transform: scale(1.01);
}

.carousel-content {
  text-align: center;
  color: white;
  padding: 20px;
}

.carousel-content h2 {
  font-size: 36px;
  margin-bottom: 15px;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}

.carousel-content p {
  font-size: 18px;
  margin-bottom: 20px;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
}

.section-title {
  font-size: 24px;
  margin-bottom: 20px;
  border-left: 5px solid #409EFF;
  padding-left: 15px;
  color: #333;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.progress-card, .stat-card {
  height: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  font-size: 16px;
}

.current-course {
  display: flex;
  align-items: center;
  gap: 15px;
}

.current-course img {
  width: 120px;
  height: 68px;
  object-fit: cover;
  border-radius: 8px;
}

.course-info {
  flex: 1;
}

.course-info h4 {
  margin: 0 0 10px;
  font-size: 16px;
}

.statistic-card {
  text-align: center;
  padding: 20px 0;
}

.feature-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  text-align: center;
  transition: transform 0.3s, box-shadow 0.3s;
  border: none; /* 可选：如果需要去除边框让其更自然 */
}

.feature-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 20px;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.15);
}

.feature-icon {
  margin-bottom: 20px;
}

.feature-card h3 {
  margin: 15px 0 10px;
  font-size: 20px;
  color: #333;
}

.feature-card p {
  color: #666;
  margin-bottom: 20px;
  line-height: 1.6;
  flex-grow: 1; /* 让段落占据剩余空间，从而把按钮推到底部 */
}

.timeline {
  padding: 20px 0;
}

.post-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.post-card:hover {
  transform: translateX(5px);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.post-header h4 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.post-stats {
  display: flex;
  gap: 10px;
  color: #999;
  font-size: 14px;
}

.post-stats span {
  margin-left: 3px;
}

.post-preview {
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

.text-center {
  text-align: center;
  padding: 10px;
}

.mb-4 {
  margin-bottom: 1rem;
}

.mb-5 {
  margin-bottom: 2rem;
}

.mt-2 {
  margin-top: 0.5rem;
}

.login-prompt {
  margin-bottom: 20px;
}

.login-prompt :deep(.el-alert__content) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
}

.recommendation-reason {
  margin-bottom: 16px;
}

.reason-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  font-size: 14px;
  border-radius: 20px;
}

.reason-tag .el-icon {
  font-size: 16px;
}

.course-wrapper {
  position: relative;
  height: 100%;
}

.trending-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  z-index: 10;
  background: linear-gradient(135deg, #f56c6c, #e6a23c);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 4px;
  box-shadow: 0 2px 8px rgba(245, 108, 108, 0.4);
}

.trending-badge .el-icon {
  font-size: 14px;
}

@media (max-width: 768px) {
  .banner-content {
    flex-direction: column;
    text-align: center;
    gap: 15px;
  }
  
  .carousel-content h2 {
    font-size: 24px;
  }
  
  .section-title {
    font-size: 20px;
  }

  .login-prompt :deep(.el-alert__content) {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
