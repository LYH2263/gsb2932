<template>
  <div class="course-detail-container" v-loading="loading">
    <el-backtop :right="40" :bottom="60" />
    
    <div v-if="course" class="course-header mb-5">
      <el-row :gutter="30">
        <el-col :xs="24" :sm="24" :md="16">
          <h1 class="title">{{ course.title }}</h1>
          <p class="description">{{ course.description }}</p>
          <div class="meta mb-4">
            <el-tag :type="getLevelType(course.level)" class="mr-2">{{ getLevelText(course.level) }}</el-tag>
            <span class="mr-4"><el-icon><User /></el-icon> {{ course.instructor }}</span>
            <span class="mr-4"><el-icon><UserFilled /></el-icon> {{ course.students_count }} 人学习</span>
            <span class="mr-4"><el-icon><StarFilled color="#ff9900"/></el-icon> {{ course.rating }}</span>
          </div>
          <div class="price-section mb-4" v-if="!course.is_free">
            <template v-if="currentDiscount">
              <span class="discount-price">¥{{ discountPrice }}</span>
              <span class="original-price">¥{{ course.price }}</span>
              <el-tag type="danger" class="ml-2" size="small">
                限时 {{ currentDiscount.discount_percentage }}% OFF
              </el-tag>
              <div class="countdown mt-2">
                <el-icon color="#f56c6c"><Clock /></el-icon>
                <span class="countdown-text">距结束还有 {{ countdownText }}</span>
              </div>
            </template>
            <template v-else>
              <span class="discount-price">¥{{ course.price }}</span>
            </template>
          </div>
          <div class="actions">
            <el-button type="primary" size="large" @click="handleJoin">
              <span v-if="isEnrolled">继续学习</span>
              <span v-else>{{ course.price === 0 ? '免费加入' : `¥${displayPrice} 购买` }}</span>
            </el-button>
            <el-button size="large" @click="toggleFavorite" :icon="isFavorited ? StarFilled : Star" />
          </div>
        </el-col>
        <el-col :xs="24" :sm="24" :md="8">
          <div class="course-media" @click="previewImage(course.cover_image)">
            <img :src="course.cover_image" class="cover-image" />
            <div class="discount-badge" v-if="currentDiscount">
              <el-icon><Clock /></el-icon>
              <span>限时优惠中</span>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <div v-if="course" class="course-content">
      <el-tabs v-model="activeTab" type="border-card">
        <el-tab-pane label="课程大纲" name="syllabus">
          <div class="syllabus-container">
            <el-collapse v-model="activeNames">
              <el-collapse-item v-for="(chapter, cIndex) in course.chapters" :key="chapter.id" :name="chapter.id">
                <template #title>
                  <div class="chapter-title-wrapper">
                    <span>{{ chapter.title }}</span>
                    <span v-if="getChapterProgressText(chapter)" class="chapter-progress-text">{{ getChapterProgressText(chapter) }}</span>
                  </div>
                </template>
                <div v-for="(lesson, lIndex) in chapter.lessons" :key="lesson.id" 
                     class="lesson-item"
                     :class="{ 'alternate-row': (cIndex + lIndex) % 2 !== 0, 'lesson-completed': isEnrolled && isLessonCompleted(lesson.id) }">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center">
                      <el-icon v-if="isEnrolled && isLessonCompleted(lesson.id)" class="mr-2 lesson-status-icon completed"><CircleCheck /></el-icon>
                      <el-icon v-else-if="isEnrolled" class="mr-2 lesson-status-icon incomplete"><CircleClose /></el-icon>
                      <el-icon class="mr-2" :color="getLessonTypeColor(lesson.type)">
                        <Document v-if="lesson.type === 'article'" />
                        <EditPen v-else-if="lesson.type === 'quiz'" />
                        <Monitor v-else-if="lesson.type === 'coding'" />
                        <Document v-else />
                      </el-icon>
                      <span>{{ lesson.title }}</span>
                    </div>
                    <div class="flex items-center">
                      <el-tag size="small" class="mr-2">{{ getLessonTypeText(lesson.type) }}</el-tag>
                      <span class="duration mr-4 text-gray">{{ formatDuration(lesson.duration) }}</span>
                      <el-button type="primary" link @click="startLesson(lesson)">开始学习</el-button>
                    </div>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="课程详情" name="details">
          <div class="details-content">
            <h3>关于课程</h3>
            <p>{{ course.description }}</p>
            
            <h3>你将学到</h3>
            <ul class="skill-list">
              <li v-for="(skill, i) in skills" :key="i">
                <el-icon color="#67C23A"><Check /></el-icon>
                {{ skill }}
              </li>
            </ul>
            
            <h3>面向人群</h3>
            <ul class="skill-list">
              <li v-for="(audience, i) in audiences" :key="i">
                <el-icon color="#409EFF"><User /></el-icon>
                {{ audience }}
              </li>
            </ul>
            
            <h3>前置知识</h3>
            <ul class="skill-list">
              <li v-for="(req, i) in requirements" :key="i">
                <el-icon color="#E6A23C"><Warning /></el-icon>
                {{ req }}
              </li>
            </ul>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="互动评价" name="reviews">
          <div class="reviews-section">
            <div class="rating-summary mb-4">
              <div class="rating-large">{{ course.rating }}</div>
              <el-rate v-model="course.rating" disabled show-score text-color="#ff9900" score-template="{value}" />
              <p class="text-gray">基于 {{ course.students_count }} 名学员的评价</p>
            </div>
            
            <el-divider>提交评价</el-divider>
            <div v-if="isEnrolled" class="review-form mb-4">
              <el-rate v-model="reviewForm.rating" show-text />
              <el-input
                v-model="reviewForm.content"
                type="textarea"
                :rows="4"
                placeholder="分享你的学习体验..."
                class="mt-2"
              />
              <el-button type="primary" class="mt-2" @click="submitReview">提交评价</el-button>
            </div>
            <div v-else class="text-center mb-4">
              <el-text type="info">学习完成后才能评价</el-text>
            </div>
            
            <el-divider>用户评价</el-divider>
            <div v-if="reviews.length === 0" class="text-center text-gray">
              暂无评价，成为第一个评价的人吧！
            </div>
            <div v-else class="review-item mb-4" v-for="review in displayedReviews" :key="review.id">
              <div class="flex items-center mb-2">
                <el-avatar :size="40" :src="review.avatar" icon="UserFilled" class="mr-2" />
                <div>
                  <span class="font-bold">{{ review.username }}</span>
                  <div class="text-gray text-xs">{{ formatDate(review.created_at) }}</div>
                </div>
                <el-rate :model-value="review.rating" disabled size="small" class="ml-auto" />
              </div>
              <p class="review-content">{{ review.content }}</p>
            </div>
            <div v-if="reviews.length > 3" class="text-center">
              <el-button text type="primary" @click="toggleShowReviews">
                {{ showAllReviews ? '收起' : '显示更多' }}
              </el-button>
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="问答讨论" name="qa">
          <div class="qa-section">
            <div v-if="authStore.isAuthenticated" class="question-form mb-4">
              <el-input
                v-model="newQuestion"
                type="textarea"
                :rows="3"
                placeholder="提出你的问题..."
                class="mb-2"
              />
              <el-button type="primary" @click="submitQuestion">提问</el-button>
            </div>
            <div v-else class="text-center mb-4">
              <el-text type="info">登录后才能提问</el-text>
            </div>
            
            <el-timeline v-if="questions.length > 0">
              <el-timeline-item
                v-for="(question, index) in displayedQuestions"
                :key="question.id"
                :type="index % 2 === 0 ? 'primary' : 'success'"
                :timestamp="formatDate(question.created_at)"
                placement="top"
              >
                <el-card shadow="hover" class="qa-card">
                  <div class="qa-header">
                    <div class="flex items-center">
                      <el-avatar :size="30" :src="question.author_avatar" class="mr-2" />
                      <span class="font-bold">{{ question.author_name }}</span>
                    </div>
                    <div class="qa-stats">
                      <span><el-icon><View /></el-icon> {{ question.views }}</span>
                      <span class="ml-2"><el-icon><ChatDotRound /></el-icon> {{ question.comments_count }}</span>
                    </div>
                  </div>
                  <h4 class="question-title">{{ question.title }}</h4>
                  <p class="question-content">{{ question.content }}</p>
                  
                  <div v-if="question.answers && question.answers.length > 0" class="answers-section mt-3">
                    <el-divider>回答</el-divider>
                    <div v-for="answer in question.answers.slice(0, 2)" :key="answer.id" class="answer-item">
                      <div class="flex items-center mb-1">
                        <el-avatar :size="24" :src="answer.author_avatar" class="mr-2" />
                        <span class="text-sm">{{ answer.author_name }}</span>
                      </div>
                      <p class="answer-content">{{ answer.content }}</p>
                    </div>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-else description="暂无问题，成为第一个提问的人吧！" />
            
            <div v-if="questions.length > 3" class="text-center mt-4">
              <el-button text type="primary" @click="toggleShowQuestions">
                {{ showAllQuestions ? '收起' : '显示更多' }}
              </el-button>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-dialog
      v-model="purchaseDialogVisible"
      title="购买课程"
      width="450px"
      center
      class="purchase-dialog"
    >
      <div class="purchase-content">
        <h3 class="text-center mb-3">{{ course?.title }}</h3>
        
        <div class="price-summary mb-4 p-3" :class="{ 'has-discount': hasAnyDiscount }">
          <div class="price-row" v-if="course?.price !== displayPrice">
            <span class="label">课程原价</span>
            <span class="value original-price">¥{{ course?.price }}</span>
          </div>
          <div class="price-row" v-if="courseDiscount > 0">
            <span class="label">限时折扣</span>
            <span class="value discount">-¥{{ courseDiscount.toFixed(2) }}</span>
          </div>
          <div class="price-row" v-if="couponDiscount > 0">
            <span class="label">优惠券抵扣</span>
            <span class="value discount">-¥{{ couponDiscount.toFixed(2) }}</span>
          </div>
          <el-divider class="my-2" />
          <div class="price-row final">
            <span class="label">应付金额</span>
            <span class="value final-price">¥{{ displayPrice }}</span>
          </div>
        </div>
        
        <div class="coupon-section mb-4">
          <div class="flex items-center gap-2">
            <el-input
              v-model="couponCode"
              placeholder="请输入优惠券码"
              size="large"
              class="flex-grow"
              @keyup.enter="applyCouponCode"
            >
              <template #prefix>
                <el-icon><Discount /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" size="large" @click="applyCouponCode" :loading="applyingCoupon">
              使用
            </el-button>
          </div>
          <div v-if="couponError" class="coupon-error mt-2">
            <el-icon color="#f56c6c"><WarningFilled /></el-icon>
            <span>{{ couponError }}</span>
          </div>
          <div v-if="couponSuccess" class="coupon-success mt-2">
            <el-icon color="#67c23a"><CircleCheckFilled /></el-icon>
            <span>{{ couponSuccess }}</span>
          </div>
          <div class="mt-2">
            <el-button type="primary" link size="small" @click="openClaimCouponDialog">
              <el-icon><Present /></el-icon> 领取优惠券
            </el-button>
          </div>
        </div>
        
        <el-divider>选择支付方式</el-divider>
        
        <el-radio-group v-model="paymentMethod" class="payment-methods mb-4">
          <el-radio label="wechat" border>
            <div class="flex items-center">
              <el-icon color="#09BB07" class="mr-1"><ChatDotRound /></el-icon> 微信支付
            </div>
          </el-radio>
          <el-radio label="alipay" border>
            <div class="flex items-center">
              <el-icon color="#1677FF" class="mr-1"><CreditCard /></el-icon> 支付宝
            </div>
          </el-radio>
        </el-radio-group>
        
        <div class="qr-placeholder mb-4">
          <div class="qr-code"></div>
          <p class="text-xs text-gray mt-1">请扫描二维码支付</p>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="purchaseDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handlePurchase" :loading="purchasing">
            确认支付 ¥{{ displayPrice }}
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <el-dialog
      v-model="claimCouponDialogVisible"
      title="领取优惠券"
      width="400px"
      center
    >
      <div class="claim-coupon-content">
        <el-input
          v-model="claimCode"
          placeholder="请输入优惠券码"
          size="large"
          class="mb-3"
          @keyup.enter="handleClaimCoupon"
        >
          <template #prefix>
            <el-icon><Present /></el-icon>
          </template>
        </el-input>
        <div class="text-center text-gray text-sm mb-4">
          <p>可用测试券码：</p>
          <p class="coupon-code-hint">NEWUSER10 (首单9折) | SAVE20 (满100减20) | VIP50 (满200享5折) | LEARN15 (满50减15)</p>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="claimCouponDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleClaimCoupon" :loading="claimingCoupon">
            立即领取
          </el-button>
        </span>
      </template>
    </el-dialog>

    <el-image-viewer v-if="showImageViewer" :url-list="[currentImageUrl]" @close="showImageViewer = false" />

    <el-dialog
      v-model="learningMode"
      fullscreen
      :show-close="false"
      class="learning-dialog"
    >
      <template #header="{ close, titleId, titleClass }">
        <div class="learning-header flex justify-between items-center">
          <h4 :id="titleId" :class="titleClass">{{ currentLesson?.title }}</h4>
          <div class="learning-actions">
            <el-button type="success" @click="completeLesson" v-if="isEnrolled" :loading="markingComplete" :disabled="currentLesson ? isLessonCompleted(currentLesson.id) : false">
              {{ currentLesson && isLessonCompleted(currentLesson.id) ? '已完成' : '标记完成' }}
            </el-button>
            <el-button @click="learningMode = false">退出学习模式</el-button>
          </div>
        </div>
      </template>
      
      <div class="learning-content flex h-full">
        <div class="content-area flex-grow" :class="{ 'with-sidebar': showNotesSidebar }">
          <div v-if="currentLesson?.type === 'article'" class="article-content">
            <h2>{{ currentLesson.title }}</h2>
            <div class="article-text" v-html="formatArticleContent(currentLesson.content)"></div>
            
            <el-divider>在浏览器中尝试</el-divider>
            <el-button type="primary" @click="openCodeSandbox">
              <el-icon><Monitor /></el-icon>
              打开代码沙盒
            </el-button>
          </div>
          
          <div v-else-if="currentLesson?.type === 'quiz'" class="quiz-content">
            <h3>即时小测验</h3>
            <p class="quiz-question">{{ currentQuizData.question }}</p>
            <el-radio-group v-model="selectedAnswer" class="quiz-options">
              <el-radio v-for="(option, i) in currentQuizData.options" :key="i" :label="option">
                {{ String.fromCharCode(65 + i) }}. {{ option }}
              </el-radio>
            </el-radio-group>
            <el-button type="primary" class="mt-4" @click="checkQuizAnswer" :loading="checkingQuiz">
              提交答案
            </el-button>
            <el-alert 
              v-if="quizResult" 
              :type="quizResult.correct ? 'success' : 'error'" 
              :title="quizResult.message" 
              class="mt-3" 
              show-icon
            />
          </div>
          
          <div v-else-if="currentLesson?.type === 'coding'" class="coding-content">
            <h2>{{ currentLesson.title }}</h2>
            <div class="article-text" v-html="formatArticleContent(currentLesson.content)"></div>
            <div class="code-section mt-4">
              <div class="sandbox-header flex justify-between items-center mb-2">
                <span class="font-bold">代码编辑器</span>
                <el-space>
                  <el-select v-model="codeLanguage" size="small" style="width: 120px">
                    <el-option label="JavaScript" value="javascript" />
                    <el-option label="Python" value="python" />
                  </el-select>
                  <el-button size="small" type="success" @click="runLessonCode" :loading="running">
                    <el-icon><Monitor /></el-icon> 运行
                  </el-button>
                </el-space>
              </div>
              <el-input
                type="textarea"
                :rows="10"
                :placeholder="getCodePlaceholder()"
                v-model="code"
                class="code-editor mb-4"
              />
              <div class="output-area">
                <div class="output-header flex justify-between items-center">
                  <span class="font-bold">输出结果</span>
                  <el-button size="small" text @click="clearOutput">清除</el-button>
                </div>
                <pre class="output-content">{{ output }}</pre>
              </div>
            </div>
          </div>
        </div>
        
        <div class="notes-sidebar" :class="{ 'expanded': showNotesSidebar }">
          <div class="notes-sidebar-header">
            <h4>笔记</h4>
            <el-button size="small" text @click="showNotesSidebar = !showNotesSidebar">
              <el-icon><Right v-if="!showNotesSidebar" /><ArrowLeft v-else /></el-icon>
            </el-button>
          </div>
          <div v-if="showNotesSidebar" class="notes-sidebar-content">
            <el-button type="primary" size="small" class="w-full mb-3" @click="openQuickNoteDialog">
              <el-icon><Plus /></el-icon> 新建笔记
            </el-button>
            <el-empty v-if="lessonNotes.length === 0" description="暂无笔记" :image-size="60" />
            <div v-else class="lesson-notes-list">
              <div v-for="note in lessonNotes" :key="note.id" class="lesson-note-item">
                <div class="lesson-note-title">{{ note.title }}</div>
                <div class="lesson-note-content text-sm text-gray">{{ truncateNoteContent(note.content, 60) }}</div>
                <div class="lesson-note-time text-xs text-gray">{{ formatNoteDate(note.updated_at || note.created_at) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <el-dialog v-model="quickNoteDialogVisible" title="新建笔记" width="800px" class="quick-note-dialog">
        <el-form :model="quickNoteForm" label-width="80px">
          <el-form-item label="标题">
            <el-input v-model="quickNoteForm.title" placeholder="笔记标题" />
          </el-form-item>
          <el-form-item label="内容">
            <MarkdownEditor v-model="quickNoteForm.content" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="quickNoteDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveQuickNote">保存</el-button>
        </template>
      </el-dialog>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { User, UserFilled, StarFilled, Star, Document, EditPen, Monitor, Check, Warning, View, ChatDotRound, CreditCard, CircleCheck, CircleClose, Right, ArrowLeft, Plus, Clock, Discount, WarningFilled, CircleCheckFilled, Present } from '@element-plus/icons-vue'
import { getCourse, enrollCourse, purchaseCourse, purchaseCourseWithCoupon, updateProgress, getCourseReviews, createCourseReview, getCourseQuestions, createCourseQuestion, markLessonComplete, getCourseProgress, getCourseDiscount, applyCoupon, claimCoupon } from '../api/course'
import { getFavorites, addFavorite, removeFavorite } from '../api/user'
import { executeCode } from '../api/sandbox'
import { getNotes, createNote } from '../api/notes'
import { useAuthStore } from '../stores/auth'
import MarkdownEditor from '../components/MarkdownEditor.vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const course = ref(null)
const activeTab = ref('syllabus')
const activeNames = ref([1])
const learningMode = ref(false)
const currentLesson = ref(null)
const code = ref('')
const codeLanguage = ref('javascript')
const output = ref('')
const running = ref(false)
const showImageViewer = ref(false)
const currentImageUrl = ref('')
const isFavorited = ref(false)

const purchaseDialogVisible = ref(false)
const paymentMethod = ref('wechat')
const purchasing = ref(false)

const isEnrolled = ref(false)
const currentProgress = ref(0)

const currentDiscount = ref(null)
const countdownText = ref('')
const countdownTimer = ref(null)
const courseDiscount = ref(0)
const couponDiscount = ref(0)
const couponCode = ref('')
const applyingCoupon = ref(false)
const couponError = ref('')
const couponSuccess = ref('')
const appliedCouponCode = ref('')

const claimCouponDialogVisible = ref(false)
const claimCode = ref('')
const claimingCoupon = ref(false)

const discountPrice = computed(() => {
  if (!currentDiscount.value || !course.value?.price) return course.value?.price || 0
  return (course.value.price * (1 - currentDiscount.value.discount_percentage / 100)).toFixed(2)
})

const hasAnyDiscount = computed(() => {
  return courseDiscount.value > 0 || couponDiscount.value > 0
})

const displayPrice = computed(() => {
  if (!course.value?.price) return '0.00'
  const price = course.value.price - courseDiscount.value - couponDiscount.value
  return Math.max(0, price).toFixed(2)
})

const updateCountdown = () => {
  if (!currentDiscount.value) return
  
  const now = new Date().getTime()
  const endTime = new Date(currentDiscount.value.end_at).getTime()
  const diff = endTime - now
  
  if (diff <= 0) {
    countdownText.value = '已结束'
    currentDiscount.value = null
    courseDiscount.value = 0
    if (countdownTimer.value) {
      clearInterval(countdownTimer.value)
    }
    return
  }
  
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  
  if (days > 0) {
    countdownText.value = `${days} 天 ${hours} 时`
  } else if (hours > 0) {
    countdownText.value = `${hours} 时 ${minutes} 分`
  } else {
    countdownText.value = `${minutes} 分钟`
  }
}

const loadDiscount = async () => {
  if (!course.value?.id || course.value.is_free) return
  try {
    const data = await getCourseDiscount(course.value.id)
    if (data && data.current_discount) {
      currentDiscount.value = data.current_discount
      courseDiscount.value = course.value.price - data.discount_price
      updateCountdown()
      countdownTimer.value = setInterval(updateCountdown, 60000)
    }
  } catch (error) {
    console.error('Failed to load discount:', error)
  }
}

const applyCouponCode = async () => {
  if (!couponCode.value.trim()) {
    couponError.value = '请输入优惠券码'
    couponSuccess.value = ''
    return
  }
  
  applyingCoupon.value = true
  couponError.value = ''
  couponSuccess.value = ''
  couponDiscount.value = 0
  
  try {
    const result = await applyCoupon(couponCode.value.trim(), course.value.id)
    if (result.valid) {
      couponSuccess.value = result.message
      couponDiscount.value = result.coupon_discount
      appliedCouponCode.value = couponCode.value.trim()
    } else {
      couponError.value = result.message
      appliedCouponCode.value = ''
    }
  } catch (error) {
    couponError.value = error?.response?.data?.detail || '优惠券验证失败'
  } finally {
    applyingCoupon.value = false
  }
}

const openClaimCouponDialog = () => {
  claimCode.value = ''
  claimCouponDialogVisible.value = true
}

const handleClaimCoupon = async () => {
  if (!claimCode.value.trim()) {
    ElMessage.warning('请输入优惠券码')
    return
  }
  
  claimingCoupon.value = true
  try {
    const result = await claimCoupon(claimCode.value.trim())
    if (result.success) {
      ElMessage.success(result.message)
      claimCouponDialogVisible.value = false
      couponCode.value = claimCode.value.trim()
      applyCouponCode()
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '领取失败')
  } finally {
    claimingCoupon.value = false
  }
}

const reviewForm = ref({
  rating: 5,
  content: ''
})

const newQuestion = ref('')
const reviews = ref([])
const questions = ref([])
const showAllReviews = ref(false)
const showAllQuestions = ref(false)

const selectedAnswer = ref('')
const checkingQuiz = ref(false)
const quizResult = ref(null)

const lessonProgressMap = ref({})
const courseProgressData = ref(null)
const markingComplete = ref(false)
const lessonStartTime = ref(null)

const showNotesSidebar = ref(true)
const lessonNotes = ref([])
const quickNoteDialogVisible = ref(false)
const quickNoteForm = ref({
  title: '',
  content: ''
})

const courseDetailMap = {
  'HTML5 入门基础': {
    skills: ['HTML 文档结构', '常用标签与语义化', '表单控件与验证', '多媒体与嵌入'],
    audiences: ['零基础前端学习者', '希望掌握网页结构的学习者', '设计师转前端'],
    requirements: ['具备基础电脑操作能力']
  },
  'CSS 样式与布局': {
    skills: ['选择器与层叠规则', '盒模型与定位', 'Flex 与 Grid 布局', '文字与色彩排版'],
    audiences: ['前端入门学习者', '需要提升页面布局能力的学习者', '希望优化视觉样式的开发者'],
    requirements: ['HTML 基础', '具备基础电脑操作能力']
  },
  'JavaScript 基础': {
    skills: ['变量与函数基础', '运算符与流程控制', 'DOM 操作', '事件与交互'],
    audiences: ['前端入门学习者', '准备学习框架的开发者', '希望掌握网页交互的学习者'],
    requirements: ['HTML/CSS 基础']
  },
  'Python 3 入门': {
    skills: ['语法与数据类型', '条件与循环', '函数与模块化', '文件读写'],
    audiences: ['零基础编程学习者', '需要掌握脚本能力的学习者', '希望入门数据处理的学习者'],
    requirements: ['具备基础逻辑思维']
  },
  'SQL 数据查询基础': {
    skills: ['SELECT 查询', '条件过滤与排序', '数据插入与更新', '基础数据清理'],
    audiences: ['数据分析入门学习者', '需要数据库查询能力的开发者', '产品或运营分析人员'],
    requirements: ['了解基础数据表概念']
  },
  'Web 前端三件套': {
    skills: ['页面结构搭建', '样式布局实践', 'DOM 交互开发', '表单与动画应用'],
    audiences: ['前端入门学习者', '希望系统学习前端的学习者', '转岗前端的开发者'],
    requirements: ['具备基础电脑操作能力']
  },
  'Vue 3 渐进式框架入门': {
    skills: ['响应式数据绑定', '模板语法与指令', '组件化开发', '组合式 API'],
    audiences: ['前端初学者', 'Vue 2 开发者升级', '想学习现代框架的开发者'],
    requirements: ['HTML/CSS 基础', 'JavaScript 基础']
  },
  'React 基础与 JSX': {
    skills: ['JSX 语法', '组件化思维', 'Props 与 State', '列表与条件渲染'],
    audiences: ['前端入门学习者', '希望学习 React 的开发者', '准备框架进阶的学习者'],
    requirements: ['JavaScript 基础', 'ES6 基础语法']
  }
}

const buildFallbackDetails = (currentCourse) => {
  const lessonTitles = currentCourse.chapters.flatMap((chapter) => chapter.lessons.map((lesson) => lesson.title))
  const skills = lessonTitles.slice(0, 4).map((title) => `掌握${title}`)
  const audiences = currentCourse.level === 'Beginner'
    ? ['零基础学习者', '需要打牢基础的学习者', '希望系统学习的开发者']
    : ['有一定基础的学习者', '希望提升技能的开发者', '正在准备项目的学习者']
  const requirements = currentCourse.level === 'Beginner'
    ? ['具备基础电脑操作能力']
    : ['具备对应基础课程知识']
  return { skills, audiences, requirements }
}

const courseDetails = computed(() => {
  if (!course.value) return { skills: [], audiences: [], requirements: [] }
  return courseDetailMap[course.value.title] || buildFallbackDetails(course.value)
})

const skills = computed(() => courseDetails.value.skills)
const audiences = computed(() => courseDetails.value.audiences)
const requirements = computed(() => courseDetails.value.requirements)

const currentQuizData = ref({
  question: 'console.log(typeof []) 的输出是什么？',
  options: ['object', 'array', 'null', 'undefined']
})

const isLessonCompleted = (lessonId) => {
  return lessonProgressMap.value[lessonId]?.completed === true
}

const getChapterProgressText = (chapter) => {
  if (!courseProgressData.value) return ''
  const ch = courseProgressData.value.chapters.find(c => c.chapter_id === chapter.id)
  if (!ch) return ''
  return `${ch.completed_count}/${ch.total_count} 已完成`
}

const totalLessons = computed(() => {
  if (!course.value) return 0
  return course.value.chapters.reduce((acc, chapter) => acc + chapter.lessons.length, 0)
})

const displayedReviews = computed(() => {
  return showAllReviews.value ? reviews.value : reviews.value.slice(0, 3)
})

const displayedQuestions = computed(() => {
  return showAllQuestions.value ? questions.value : questions.value.slice(0, 3)
})

const getLevelType = (level) => {
  switch (level) {
    case 'Beginner': return 'success'
    case 'Intermediate': return 'warning'
    case 'Advanced': return 'danger'
    default: return 'info'
  }
}

const getLevelText = (level) => {
  switch (level) {
    case 'Beginner': return '初级'
    case 'Intermediate': return '中级'
    case 'Advanced': return '高级'
    default: return level
  }
}

const getLessonTypeColor = (type) => {
  const colors = {
    'article': '#67C23A',
    'quiz': '#E6A23C',
    'coding': '#F56C6C'
  }
  return colors[type] || '#909399'
}

const getLessonTypeText = (type) => {
  const texts = {
    'article': '文章',
    'quiz': '测验',
    'coding': '代码'
  }
  return texts[type] || type
}

const completeLesson = async () => {
  if (!isEnrolled.value || !currentLesson.value || markingComplete.value) return
  
  if (isLessonCompleted(currentLesson.value.id)) {
    ElMessage.info('该课时已完成')
    learningMode.value = false
    return
  }
  
  markingComplete.value = true
  const elapsed = lessonStartTime.value ? Math.floor((Date.now() - lessonStartTime.value) / 1000) : 0
  
  try {
    const result = await markLessonComplete(course.value.id, currentLesson.value.id, elapsed)
    if (result.already_completed) {
      ElMessage.info(result.message || '该课时已完成')
      lessonProgressMap.value[currentLesson.value.id] = { completed: true }
    } else {
      lessonProgressMap.value[currentLesson.value.id] = { completed: true, study_duration: elapsed }
      ElMessage.success('课程完成！进度已更新')
    }
    
    if (courseProgressData.value) {
      const progress = await getCourseProgress(course.value.id)
      courseProgressData.value = progress
      currentProgress.value = progress.progress_percentage
    }
    
    learningMode.value = false
  } catch (error) {
    ElMessage.error('更新进度失败')
  } finally {
    markingComplete.value = false
  }
}

const runLessonCode = async () => {
  if (!code.value.trim()) {
    ElMessage.warning('请输入代码')
    return
  }
  
  running.value = true
  output.value = '正在运行...'
  
  try {
    const response = await executeCode(code.value, codeLanguage.value)
    output.value = response.output || '无输出'
  } catch (error) {
    output.value = `错误: ${error.message || '执行失败'}`
    ElMessage.error('代码执行失败')
  } finally {
    running.value = false
  }
}

const clearOutput = () => {
  output.value = ''
}

const getCodePlaceholder = () => {
  const placeholders = {
    'javascript': '// 在这里编写 JavaScript 代码\nconsole.log("Hello, World!");',
    'python': '# 在这里编写 Python 代码\nprint("Hello, World!")'
  }
  return placeholders[codeLanguage.value] || '// 在这里编写代码'
}

const formatArticleContent = (content) => {
  if (!content) return '课程内容...'
  return content.replace(/\n/g, '<br>')
}

const checkQuizAnswer = () => {
  if (!selectedAnswer.value) {
    ElMessage.warning('请选择答案')
    return
  }
  
  checkingQuiz.value = true
  setTimeout(() => {
    checkingQuiz.value = false
    const correct = selectedAnswer.value === 'object'
    quizResult.value = {
      correct,
      message: correct ? '回答正确！' : '回答错误，正确答案是 object'
    }
  }, 500)
}

const toggleFavorite = async () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    return
  }
  const nextState = !isFavorited.value
  try {
    if (nextState) {
      await addFavorite(course.value.id)
    } else {
      await removeFavorite(course.value.id)
    }
    isFavorited.value = nextState
    ElMessage.success(isFavorited.value ? '已添加收藏' : '已取消收藏')
  } catch (error) {
    ElMessage.error('收藏操作失败')
  }
}

const submitReview = async () => {
  if (!reviewForm.value.content.trim()) {
    ElMessage.warning('请输入评价内容')
    return
  }
  try {
    const created = await createCourseReview(course.value.id, {
      rating: reviewForm.value.rating,
      content: reviewForm.value.content,
      course_id: course.value.id
    })
    reviews.value.unshift(created)
    ElMessage.success('评价提交成功')
    reviewForm.value = { rating: 5, content: '' }
  } catch (error) {
    ElMessage.error('评价提交失败')
  }
}

const submitQuestion = async () => {
  if (!newQuestion.value.trim()) {
    ElMessage.warning('请输入问题')
    return
  }
  try {
    const created = await createCourseQuestion(course.value.id, {
      title: newQuestion.value.substring(0, 50),
      content: newQuestion.value,
      course_id: course.value.id
    })
    questions.value.unshift(created)
    ElMessage.success('问题发布成功')
    newQuestion.value = ''
  } catch (error) {
    ElMessage.error('问题发布失败')
  }
}

const toggleShowReviews = () => {
  showAllReviews.value = !showAllReviews.value
}

const toggleShowQuestions = () => {
  showAllQuestions.value = !showAllQuestions.value
}

const openCodeSandbox = () => {
  router.push('/sandbox')
}

const previewImage = (url) => {
  currentImageUrl.value = url
  showImageViewer.value = true
}

const formatDate = (date) => {
  const d = new Date(date)
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
}

onMounted(async () => {
  loading.value = true
  try {
    const data = await getCourse(route.params.id)
    course.value = data
    
    if (authStore.isAuthenticated) {
      try {
        const enrollments = await (await import('../api/course')).getEnrolledCourses()
        const enrollment = enrollments.find(e => e.course_id === parseInt(route.params.id))
        if (enrollment) {
          isEnrolled.value = true
          currentProgress.value = enrollment.progress
        }
        const favoriteCourses = await getFavorites()
        isFavorited.value = favoriteCourses.some(f => f.id === course.value.id)
        
        if (isEnrolled.value) {
          try {
            const progressData = await getCourseProgress(route.params.id)
            courseProgressData.value = progressData
            currentProgress.value = progressData.progress_percentage
            for (const chapter of progressData.chapters) {
              for (const lesson of chapter.lessons) {
                lessonProgressMap.value[lesson.lesson_id] = {
                  completed: lesson.completed,
                  study_duration: lesson.study_duration
                }
              }
            }
          } catch (e) {
            console.error('Failed to load lesson progress', e)
          }
        }
      } catch (e) {
        console.error('Failed to check enrollment', e)
      }
    }
    
    loadDiscount()
    
    reviews.value = await getCourseReviews(route.params.id)
    questions.value = await getCourseQuestions(route.params.id)
  } catch (error) {
    console.error('Failed to fetch course', error)
    ElMessage.error('加载课程详情失败')
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  if (countdownTimer.value) {
    clearInterval(countdownTimer.value)
  }
})

watch(purchaseDialogVisible, (val) => {
  if (!val) {
    couponCode.value = ''
    couponDiscount.value = 0
    couponError.value = ''
    couponSuccess.value = ''
    appliedCouponCode.value = ''
  }
})

const handleJoin = async () => {
  if (!authStore.token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  if (isEnrolled.value) {
    ElMessage.success('继续学习...')
    if (course.value.chapters.length > 0 && course.value.chapters[0].lessons.length > 0) {
      startLesson(course.value.chapters[0].lessons[0])
    }
    return
  }
  
  // Check if course is paid
  if (course.value.price > 0) {
    purchaseDialogVisible.value = true
    return
  }

  try {
    await enrollCourse(course.value.id)
    ElMessage.success('成功加入课程！')
    isEnrolled.value = true
  } catch (error) {
    ElMessage.error('加入课程失败')
  }
}

const handlePurchase = async () => {
  purchasing.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    const couponToUse = appliedCouponCode.value || undefined
    if (couponToUse) {
      await purchaseCourseWithCoupon(course.value.id, couponToUse)
    } else {
      await purchaseCourse(course.value.id)
    }
    
    ElMessage.success('支付成功！已加入课程')
    isEnrolled.value = true
    purchaseDialogVisible.value = false
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '支付失败，请重试')
  } finally {
    purchasing.value = false
  }
}

const startLesson = (lesson) => {
  currentLesson.value = lesson
  learningMode.value = true
  quizResult.value = null
  selectedAnswer.value = ''
  lessonStartTime.value = Date.now()
  
  if (lesson.type === 'coding') {
    code.value = getCodePlaceholder()
    output.value = ''
  } else if (lesson.type === 'quiz') {
    currentQuizData.value = {
      question: 'console.log(typeof []) 的输出是什么？',
      options: ['object', 'array', 'null', 'undefined']
    }
  }

  loadLessonNotes()
}

const formatDuration = (seconds) => {
  const min = Math.floor(seconds / 60)
  const sec = seconds % 60
  return `${min}:${sec < 10 ? '0' : ''}${sec}`
}

const loadLessonNotes = async () => {
  if (!currentLesson.value || !authStore.isAuthenticated || !course.value) return
  try {
    lessonNotes.value = await getNotes({ 
      course_id: course.value.id,
      lesson_id: currentLesson.value.id 
    })
  } catch (error) {
    console.error('Failed to load lesson notes', error)
  }
}

const truncateNoteContent = (content, length) => {
  return content.length > length ? content.substring(0, length) + '...' : content
}

const formatNoteDate = (date) => {
  const d = new Date(date)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
}

const openQuickNoteDialog = () => {
  quickNoteForm.value = {
    title: `${currentLesson.value?.title || '课程'} - 笔记`,
    content: ''
  }
  quickNoteDialogVisible.value = true
}

const saveQuickNote = async () => {
  if (!quickNoteForm.value.title || !quickNoteForm.value.content) {
    ElMessage.warning('请填写完整的笔记信息')
    return
  }
  try {
    await createNote({
      title: quickNoteForm.value.title,
      content: quickNoteForm.value.content,
      course_id: course.value.id,
      lesson_id: currentLesson.value?.id
    })
    ElMessage.success('笔记保存成功')
    quickNoteDialogVisible.value = false
    await loadLessonNotes()
  } catch (error) {
    ElMessage.error('笔记保存失败')
  }
}

watch(currentLesson, (newVal) => {
  if (newVal) {
    loadLessonNotes()
  } else {
    lessonNotes.value = []
  }
})
</script>

<style scoped>
.course-detail-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.course-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 12px;
}

.title {
  font-size: 28px;
  margin-bottom: 10px;
}

.description {
  font-size: 16px;
  margin-bottom: 20px;
  opacity: 0.95;
  line-height: 1.6;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 15px;
  font-size: 14px;
  opacity: 0.9;
}

.course-media {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  height: 200px;
  background: #000;
  cursor: pointer;
  transition: transform 0.3s;
}

.course-media:hover {
  transform: scale(1.02);
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.8;
}

.lesson-item {
  padding: 12px 15px;
  border-bottom: 1px solid #eee;
  transition: background-color 0.2s;
}

.lesson-item:hover {
  background-color: #f5f7fa;
}

.lesson-item.lesson-completed {
  background-color: #f0f9eb;
}

.lesson-status-icon.completed {
  color: #67C23A;
  font-size: 18px;
}

.lesson-status-icon.incomplete {
  color: #C0C4CC;
  font-size: 18px;
}

.chapter-title-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.chapter-progress-text {
  font-size: 12px;
  color: #67C23A;
  background: #f0f9eb;
  padding: 2px 8px;
  border-radius: 10px;
  white-space: nowrap;
}

.alternate-row {
  background-color: #fafafa;
}

.mr-2 { margin-right: 0.5rem; }
.mr-4 { margin-right: 1rem; }
.ml-2 { margin-left: 0.5rem; }
.ml-auto { margin-left: auto; }
.mb-2 { margin-bottom: 0.5rem; }
.mb-3 { margin-bottom: 0.75rem; }
.mb-4 { margin-bottom: 1rem; }
.mb-5 { margin-bottom: 2rem; }
.mt-2 { margin-top: 0.5rem; }
.mt-3 { margin-top: 0.75rem; }
.mt-4 { margin-top: 1rem; }

.text-gray { color: #999; }
.text-sm { font-size: 12px; }
.text-xs { font-size: 11px; }
.text-center { text-align: center; }
.font-bold { font-weight: bold; }

.details-content h3 {
  color: #333;
  margin: 25px 0 15px;
  border-bottom: 2px solid #409EFF;
  padding-bottom: 10px;
}

.skill-list {
  list-style: none;
  padding: 0;
}

.skill-list li {
  padding: 10px 0;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #555;
}

.rating-summary {
  text-align: center;
  padding: 30px 0;
}

.rating-large {
  font-size: 48px;
  font-weight: bold;
  color: #ff9900;
}

.review-item {
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 8px;
}

.review-content {
  color: #555;
  line-height: 1.6;
  margin-top: 10px;
}

.qa-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.qa-card:hover {
  transform: translateX(5px);
}

.qa-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.qa-stats {
  display: flex;
  gap: 10px;
  font-size: 12px;
  color: #999;
}

.question-title {
  margin: 10px 0;
  color: #333;
}

.question-content {
  color: #666;
  line-height: 1.6;
}

.answer-item {
  padding: 10px;
  background: #f9f9f9;
  border-radius: 4px;
  margin-top: 10px;
}

.answer-content {
  color: #555;
  margin: 5px 0 0 0;
}

.flex { display: flex; }
.flex-grow { flex-grow: 1; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }

.learning-content {
  height: calc(100vh - 100px);
}

.content-area {
  padding: 30px;
  background: #f5f7fa;
  overflow-y: auto;
}

.article-content h2 {
  color: #333;
  margin-bottom: 20px;
}

.article-text {
  color: #555;
  line-height: 1.8;
  font-size: 16px;
}

.quiz-content {
  max-width: 600px;
  margin: 0 auto;
}

.quiz-question {
  font-size: 18px;
  color: #333;
  margin: 20px 0;
  font-weight: 500;
}

.quiz-options {
  display: block;
  margin: 20px 0;
}

.quiz-options .el-radio {
  display: block;
  margin: 15px 0;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  transition: all 0.2s;
}

.quiz-options .el-radio:hover {
  border-color: #409EFF;
  background: #f0f7ff;
}

.half-width {
  width: 50%;
}

.sandbox-area {
  border-left: 1px solid #ddd;
  display: flex;
  flex-direction: column;
  background: #1e1e1e;
}

.sandbox-header {
  padding: 15px;
  border-bottom: 1px solid #333;
  background: #252526;
  color: white;
}

.code-editor {
  flex: 1;
  background: #1e1e1e;
}

.code-editor :deep(.el-textarea__inner) {
  background: #1e1e1e;
  color: #d4d4d4;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  border: none;
}

.output-area {
  height: 200px;
  background: #1e1e1e;
  border-top: 1px solid #333;
}

.output-header {
  padding: 10px 15px;
  background: #252526;
  color: #888;
  font-size: 12px;
}

.output-content {
  padding: 15px;
  margin: 0;
  color: #4ec9b0;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  overflow-y: auto;
  max-height: 150px;
}

@media (max-width: 768px) {
  .course-header {
    padding: 20px;
  }
  
  .title {
    font-size: 22px;
  }
  
  .half-width {
    width: 100%;
  }
  
  .sandbox-area {
    border-left: none;
    border-top: 1px solid #ddd;
  }
}

.content-area.with-sidebar {
  width: calc(100% - 300px);
}

.notes-sidebar {
  width: 50px;
  background: #f8f9fa;
  border-left: 1px solid #e4e7ed;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.notes-sidebar.expanded {
  width: 300px;
}

.notes-sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 15px;
  background: #f0f2f5;
  border-bottom: 1px solid #e4e7ed;
  min-height: 48px;
}

.notes-sidebar-header h4 {
  margin: 0;
  font-size: 14px;
  color: #303133;
  white-space: nowrap;
}

.notes-sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.lesson-notes-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.lesson-note-item {
  padding: 10px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  cursor: pointer;
  transition: all 0.2s;
}

.lesson-note-item:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

.lesson-note-title {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.lesson-note-content {
  color: #606266;
  margin-bottom: 4px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.lesson-note-time {
  color: #909399;
}

.coding-content {
  height: 100%;
  overflow-y: auto;
}

.coding-content .code-section {
  background: #1e1e1e;
  border-radius: 8px;
  padding: 15px;
}

.coding-content .code-section :deep(.el-textarea__inner) {
  background: #1e1e1e;
  color: #d4d4d4;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  border: 1px solid #333;
}

:deep(.quick-note-dialog .el-dialog__body) {
  padding-top: 10px;
}
</style>

.purchase-dialog .el-dialog__body {
  padding-top: 10px;
}

.price-tag {
  font-size: 24px;
  color: #f56c6c;
  font-weight: bold;
}

.payment-methods {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.payment-methods .el-radio {
  margin-right: 0;
  width: 100%;
  height: 50px;
}

.qr-placeholder {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.qr-code {
  width: 150px;
  height: 150px;
  background: #fff;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect x='0' y='0' width='100' height='100' fill='%23ffffff'/%3E%3Cpath d='M10 10h30v30h-30zM50 10h10v10h-10zM70 10h20v20h-20zM10 50h10v10h-10zM30 50h10v10h-10zM50 50h40v40h-40zM10 70h30v20h-30z' fill='%23333333'/%3E%3C/svg%3E");
  background-size: cover;
  border: 1px solid #eee;
}

.price-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.price-section .discount-price {
  font-size: 32px;
  font-weight: bold;
  color: #f56c6c;
}

.price-section .original-price {
  font-size: 18px;
  color: #909399;
  text-decoration: line-through;
  margin-left: 10px;
}

.countdown {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.countdown-text {
  color: #f56c6c;
  font-weight: 600;
}

.course-media {
  position: relative;
}

.course-media .discount-badge {
  position: absolute;
  top: 15px;
  left: 15px;
  background: linear-gradient(135deg, #f56c6c 0%, #e6a23c 100%);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 4px 12px rgba(245, 108, 108, 0.3);
}

.price-summary {
  background: #f8f9fa;
  border-radius: 8px;
}

.price-summary.has-discount {
  background: linear-gradient(135deg, #fff5f5 0%, #fff0e6 100%);
  border: 1px solid #fecaca;
}

.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
}

.price-row .label {
  color: #606266;
  font-size: 14px;
}

.price-row .value {
  font-size: 14px;
  color: #303133;
}

.price-row .value.original-price {
  text-decoration: line-through;
  color: #909399;
}

.price-row .value.discount {
  color: #f56c6c;
  font-weight: 600;
}

.price-row.final {
  padding-top: 12px;
}

.price-row.final .label {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.price-row.final .final-price {
  font-size: 24px;
  font-weight: bold;
  color: #f56c6c;
}

.coupon-error, .coupon-success {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.coupon-error {
  color: #f56c6c;
}

.coupon-success {
  color: #67c23a;
}

.coupon-code-hint {
  background: #f5f7fa;
  padding: 8px 12px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #606266;
  word-break: break-all;
}

.my-2 {
  margin: 0.5rem 0;
}

.ml-2 {
  margin-left: 0.5rem;
}

.mt-2 {
  margin-top: 0.5rem;
}

.mb-3 {
  margin-bottom: 0.75rem;
}

.text-center {
  text-align: center;
}

.text-gray {
  color: #909399;
}

.text-sm {
  font-size: 12px;
}
