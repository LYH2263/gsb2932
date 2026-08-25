<template>
  <el-card :body-style="{ padding: '0px' }" shadow="hover" class="course-card" @click="$emit('click')">
    <div class="course-cover">
      <img :src="course.cover_image" alt="课程封面" @error="handleImageError" />
      <div class="course-tag">
        <el-tag :type="getLevelType(course.level)" size="small">{{ getLevelText(course.level) }}</el-tag>
      </div>
      <div class="course-price" v-if="!course.is_free">
        <template v-if="currentDiscount">
          <span class="price discount-price">¥{{ discountPrice }}</span>
          <span class="original-price">¥{{ course.price }}</span>
        </template>
        <template v-else>
          <span class="price">¥{{ course.price }}</span>
        </template>
      </div>
      <div class="discount-badge" v-if="currentDiscount">
        <el-icon><Clock /></el-icon>
        <span>距结束 {{ countdownText }}</span>
      </div>
    </div>
    <div class="course-content">
      <h3 class="course-title">{{ course.title }}</h3>
      <p class="course-desc">{{ truncateText(course.description, 50) }}</p>
      <div class="course-meta">
        <div class="meta-item">
          <el-icon><User /></el-icon>
          <span>{{ course.students_count }}人学习</span>
        </div>
        <div class="meta-item">
          <el-icon><Star /></el-icon>
          <span>{{ course.rating }}</span>
        </div>
      </div>
      <div class="course-footer">
        <span class="instructor">{{ course.instructor }}</span>
        <el-icon class="favorite-icon" @click.stop="toggleFavorite">
          <component :is="isFavorited ? StarFilled : Star" />
        </el-icon>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { User, Star, StarFilled, Clock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { getCourseDiscount } from '../api/course'

const props = defineProps({
  course: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['click'])

const authStore = useAuthStore()

const currentDiscount = ref(null)
const countdownText = ref('')
const countdownTimer = ref(null)

const discountPrice = computed(() => {
  if (!currentDiscount.value || !props.course.price) return props.course.price
  return (props.course.price * (1 - currentDiscount.value.discount_percentage / 100)).toFixed(2)
})

const isFavorited = computed(() => {
  return authStore.isAuthenticated && authStore.user?.favorites?.includes(props.course.id)
})

const updateCountdown = () => {
  if (!currentDiscount.value) return
  
  const now = new Date().getTime()
  const endTime = new Date(currentDiscount.value.end_at).getTime()
  const diff = endTime - now
  
  if (diff <= 0) {
    countdownText.value = '已结束'
    currentDiscount.value = null
    if (countdownTimer.value) {
      clearInterval(countdownTimer.value)
    }
    return
  }
  
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  
  if (days > 0) {
    countdownText.value = `还有 ${days} 天 ${hours} 时`
  } else {
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
    countdownText.value = `还有 ${hours} 时 ${minutes} 分`
  }
}

const loadDiscount = async () => {
  if (props.course.is_free) return
  try {
    const data = await getCourseDiscount(props.course.id)
    if (data && data.current_discount) {
      currentDiscount.value = data.current_discount
      updateCountdown()
      countdownTimer.value = setInterval(updateCountdown, 60000)
    }
  } catch (error) {
    console.error('Failed to load discount:', error)
  }
}

const handleImageError = (e) => {
  e.target.src = 'https://placehold.co/300x200/409EFF/ffffff?text=Course'
}

const truncateText = (text, length) => {
  return text.length > length ? text.substring(0, length) + '...' : text
}

const getLevelText = (level) => {
  const map = {
    'Beginner': '初级',
    'Intermediate': '中级',
    'Advanced': '高级'
  }
  return map[level] || level
}

const getLevelType = (level) => {
  const map = {
    'Beginner': 'success',
    'Intermediate': 'warning',
    'Advanced': 'danger'
  }
  return map[level] || ''
}

const toggleFavorite = async () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    return
  }
  try {
    const { toggleFavorite } = await import('../api/course')
    await toggleFavorite(props.course.id)
    ElMessage.success(isFavorited.value ? '已取消收藏' : '已添加收藏')
  } catch (error) {
    console.error(error)
  }
}

onMounted(() => {
  if (props.course.current_discount) {
    currentDiscount.value = props.course.current_discount
    updateCountdown()
    countdownTimer.value = setInterval(updateCountdown, 60000)
  } else {
    loadDiscount()
  }
})

onUnmounted(() => {
  if (countdownTimer.value) {
    clearInterval(countdownTimer.value)
  }
})
</script>

<style scoped>
.course-card {
  height: 100%;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  border-radius: 8px;
  overflow: hidden;
}

.course-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.12);
}

.course-cover {
  position: relative;
  height: 160px;
  overflow: hidden;
}

.course-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.course-card:hover .course-cover img {
  transform: scale(1.05);
}

.course-tag {
  position: absolute;
  top: 10px;
  left: 10px;
}

.course-price {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0,0,0,0.7);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: bold;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.original-price {
  text-decoration: line-through;
  font-size: 11px;
  opacity: 0.7;
  font-weight: normal;
}

.discount-price {
  color: #f56c6c;
}

.discount-badge {
  position: absolute;
  bottom: 10px;
  left: 10px;
  background: linear-gradient(135deg, #f56c6c 0%, #e6a23c 100%);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
  box-shadow: 0 2px 8px rgba(245, 108, 108, 0.3);
}

.course-content {
  padding: 15px;
}

.course-title {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.course-desc {
  margin: 0 0 12px;
  font-size: 13px;
  color: #666;
  line-height: 1.5;
  height: 40px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.course-meta {
  display: flex;
  gap: 15px;
  margin-bottom: 12px;
  font-size: 13px;
  color: #999;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.course-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 10px;
  border-top: 1px solid #eee;
}

.instructor {
  font-size: 12px;
  color: #666;
}

.favorite-icon {
  color: #E6A23C;
  cursor: pointer;
  font-size: 18px;
  transition: transform 0.2s;
}

.favorite-icon:hover {
  transform: scale(1.2);
}

@media (max-width: 768px) {
  .course-cover {
    height: 140px;
  }
}
</style>
