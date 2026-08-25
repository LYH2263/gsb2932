<template>
  <div class="user-center-container">
    <el-backtop :right="40" :bottom="60" />
    
    <el-row :gutter="20">
      <el-col :xs="24" :sm="24" :md="6">
        <el-card class="profile-card mb-4" shadow="hover">
          <div class="user-profile text-center">
            <el-upload
              class="avatar-uploader"
              :show-file-list="false"
              :before-upload="beforeAvatarUpload"
            >
              <img v-if="authStore.user?.avatar" :src="authStore.user.avatar" class="avatar" />
              <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
            </el-upload>
            <h3 class="username mt-2">{{ authStore.user?.username }}</h3>
            <p class="text-gray">{{ authStore.user?.bio || '暂无个性签名' }}</p>
            <el-button type="primary" size="small" class="mt-2" @click="editProfileDialog = true">编辑资料</el-button>
          </div>
          <div class="stats mt-4">
            <el-row>
              <el-col :span="8" class="text-center">
                <div class="stat-value">{{ dashboard?.enrollments || 0 }}</div>
                <div class="stat-label">课程</div>
              </el-col>
              <el-col :span="8" class="text-center">
                <div class="stat-value">{{ dashboard?.posts_count || 0 }}</div>
                <div class="stat-label">帖子</div>
              </el-col>
              <el-col :span="8" class="text-center">
                <div class="stat-value">{{ dashboard?.total_study_time || 0 }}h</div>
                <div class="stat-label">学习时长</div>
              </el-col>
            </el-row>
          </div>
          <div class="achievements mt-4">
            <div 
              class="achievement-item" 
              v-for="achievement in achievements" 
              :key="achievement.achievement_id"
              :class="{ 'unlocked': achievement.unlocked, 'locked': !achievement.unlocked }"
              :title="achievement.progress_text"
            >
              <div class="achievement-icon-wrapper">
                <el-icon 
                  :color="achievement.unlocked ? '#ffd700' : '#c0c4cc'" 
                  :size="24"
                >
                  <component :is="getIconComponent(achievement.icon)" />
                </el-icon>
              </div>
              <span class="achievement-name">{{ achievement.name }}</span>
              <span v-if="achievement.unlocked" class="unlock-date">
                {{ formatUnlockDate(achievement.unlocked_at) }}
              </span>
              <span v-else class="progress-hint">
                {{ achievement.progress_text }}
              </span>
            </div>
          </div>
        </el-card>

        <el-menu
          :default-active="activeTab"
          class="sidebar-menu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="learning">
            <el-icon><Reading /></el-icon>
            <span>我的学习</span>
          </el-menu-item>
          <el-menu-item index="coupons">
            <el-icon><Discount /></el-icon>
            <span>我的优惠券</span>
          </el-menu-item>
          <el-menu-item index="projects">
             <el-icon><Folder /></el-icon>
            <span>我的项目</span>
          </el-menu-item>
          <el-menu-item index="favorites">
            <el-icon><Star /></el-icon>
            <span>我的收藏</span>
          </el-menu-item>
          <el-menu-item index="orders">
            <el-icon><Tickets /></el-icon>
            <span>订单记录</span>
          </el-menu-item>
           <el-menu-item index="settings">
            <el-icon><Setting /></el-icon>
            <span>账户设置</span>
          </el-menu-item>
        </el-menu>
      </el-col>

      <el-col :xs="24" :sm="24" :md="18">
        <el-card shadow="hover">
          <div v-if="activeTab === 'learning'">
            <h2 class="section-title">我的学习</h2>
            
            <el-tabs v-model="learningTab">
              <el-tab-pane label="正在学习" name="inprogress">
                <el-empty v-if="inProgressCourses.length === 0" description="暂无正在学习的课程" />
                <el-row :gutter="20" v-else>
                  <el-col :xs="24" :sm="12" :md="8" v-for="(course, index) in inProgressCourses" :key="course.id" class="mb-4">
                    <el-card shadow="hover" :body-style="{ padding: '0px' }" 
                             class="course-card" :class="{ 'alternate-row': index % 2 !== 0 }">
                      <img :src="course.cover_image" class="course-thumb" @click="previewImage(course.cover_image)" />
                      <div class="p-3">
                        <h4>{{ course.title }}</h4>
                        <el-progress :percentage="course.progress" :color="getProgressColor(course.progress)" class="mt-2" />
                        <div class="study-time-text mt-1">{{ formatStudyTime(course.study_duration) }}</div>
                        <el-button type="primary" size="small" class="mt-2 w-full" @click="router.push(`/courses/${course.id}`)">
                          继续学习
                        </el-button>
                      </div>
                    </el-card>
                  </el-col>
                </el-row>
              </el-tab-pane>
              <el-tab-pane label="已完成" name="completed">
                <el-empty v-if="completedCourses.length === 0" description="暂无已完成的课程" />
                <el-row :gutter="20" v-else>
                  <el-col :xs="24" :sm="12" :md="8" v-for="(course, index) in completedCourses" :key="course.id" class="mb-4">
                    <el-card shadow="hover" :body-style="{ padding: '0px' }" 
                             class="course-card" :class="{ 'alternate-row': index % 2 !== 0 }">
                      <img :src="course.cover_image" class="course-thumb" @click="previewImage(course.cover_image)" />
                      <div class="p-3">
                        <h4>{{ course.title }}</h4>
                        <el-tag type="success" size="small" class="mt-2">已完成</el-tag>
                        <div class="study-time-text mt-1">{{ formatStudyTime(course.study_duration) }}</div>
                        <el-button type="success" plain size="small" class="mt-2 w-full" @click="router.push(`/courses/${course.id}`)">
                          复习课程
                        </el-button>
                      </div>
                    </el-card>
                  </el-col>
                </el-row>
              </el-tab-pane>
            </el-tabs>

            <div class="mt-5" v-if="activeTab === 'learning'">
              <div class="flex justify-between items-center mb-4">
                <h3>学习日历</h3>
                <el-button text type="primary" @click="toggleCalendar">
                  {{ showCalendar ? '隐藏' : '显示' }}
                </el-button>
              </div>
              <el-collapse-transition>
                <el-calendar v-model="calendarValue" v-show="showCalendar" />
              </el-collapse-transition>
            </div>
            
            <div class="mt-5">
              <div class="flex justify-between items-center mb-4">
                <h3>学习笔记</h3>
                <div class="flex items-center gap-2">
                  <el-input
                    v-model="noteSearchKeyword"
                    placeholder="搜索笔记标题或内容"
                    style="width: 300px"
                    clearable
                    @input="searchNotes"
                  >
                    <template #prefix>
                      <el-icon><Search /></el-icon>
                    </template>
                  </el-input>
                  <el-button type="primary" @click="openAddNoteDialog">
                    <el-icon><Edit /></el-icon> 添加笔记
                  </el-button>
                </div>
              </div>
              <el-empty v-if="filteredNotes.length === 0" description="暂无学习笔记" />
              <div v-else class="notes-list">
                <div v-for="(note, index) in filteredNotes" :key="note.id" 
                     class="note-item" :class="{ 'alternate-row': index % 2 !== 0 }">
                  <el-card shadow="hover">
                    <div class="flex justify-between items-start">
                      <div class="note-content" style="flex: 1; cursor: pointer" @click="openEditNoteDialog(note)">
                        <h4>{{ note.title }}</h4>
                        <p class="text-gray text-sm">{{ truncateText(note.content, 100) }}</p>
                        <div class="note-meta text-xs text-gray">
                          {{ formatDate(note.updated_at || note.created_at) }}
                        </div>
                      </div>
                      <div class="note-actions">
                        <el-dropdown @command="(cmd) => handleNoteAction(cmd, note)">
                          <el-button size="small" text>
                            <el-icon><MoreFilled /></el-icon> 操作
                          </el-button>
                          <template #dropdown>
                            <el-dropdown-menu>
                              <el-dropdown-item command="edit">编辑</el-dropdown-item>
                              <el-dropdown-item command="export-md">导出 Markdown</el-dropdown-item>
                              <el-dropdown-item command="export-pdf">导出 PDF</el-dropdown-item>
                              <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                            </el-dropdown-menu>
                          </template>
                        </el-dropdown>
                      </div>
                    </div>
                  </el-card>
                </div>
              </div>
            </div>
          </div>

          <div v-else-if="activeTab === 'coupons'">
            <h2 class="section-title">我的优惠券</h2>
            
            <el-tabs v-model="couponTab" @tab-change="handleCouponTabChange">
              <el-tab-pane label="可使用" name="available">
                <el-empty v-if="myCoupons.available.length === 0" description="暂无可用优惠券" />
                <el-row :gutter="20" v-else>
                  <el-col :xs="24" :sm="12" :md="8" v-for="(userCoupon, index) in myCoupons.available" :key="`${userCoupon.coupon_id}-${index}`" class="mb-4">
                    <el-card shadow="hover" class="coupon-card available">
                      <div class="coupon-header">
                        <div class="coupon-value">
                          <span class="currency" v-if="userCoupon.coupon.discount_type === 'fixed'">¥</span>
                          <span class="amount">{{ getCouponDisplayValue(userCoupon.coupon) }}</span>
                          <span class="percent" v-if="userCoupon.coupon.discount_type === 'percentage'">%</span>
                        </div>
                        <div class="coupon-type">
                          {{ userCoupon.coupon.discount_type === 'fixed' ? '满减券' : '折扣券' }}
                        </div>
                      </div>
                      <div class="coupon-body">
                        <h4 class="coupon-code">{{ userCoupon.coupon.code }}</h4>
                        <p class="coupon-desc">
                          {{ userCoupon.coupon.discount_type === 'fixed' 
                            ? `满 ¥${userCoupon.coupon.min_purchase} 可用` 
                            : `满 ¥${userCoupon.coupon.min_purchase} 可用，最高折扣无上限` }}
                        </p>
                        <p class="coupon-expiry">
                          <el-icon><Clock /></el-icon>
                          {{ userCoupon.coupon.valid_until 
                            ? `有效期至 ${formatDate(userCoupon.coupon.valid_until)}` 
                            : '长期有效' }}
                        </p>
                      </div>
                      <div class="coupon-footer">
                        <el-button 
                          type="primary" 
                          size="small" 
                          class="w-full"
                          @click="router.push('/courses')"
                        >
                          立即使用
                        </el-button>
                      </div>
                    </el-card>
                  </el-col>
                </el-row>
              </el-tab-pane>
              
              <el-tab-pane label="已使用" name="used">
                <el-empty v-if="myCoupons.used.length === 0" description="暂无已使用优惠券" />
                <el-row :gutter="20" v-else>
                  <el-col :xs="24" :sm="12" :md="8" v-for="(userCoupon, index) in myCoupons.used" :key="`${userCoupon.coupon_id}-${index}`" class="mb-4">
                    <el-card shadow="hover" class="coupon-card used">
                      <div class="coupon-header">
                        <div class="coupon-value">
                          <span class="currency" v-if="userCoupon.coupon.discount_type === 'fixed'">¥</span>
                          <span class="amount">{{ getCouponDisplayValue(userCoupon.coupon) }}</span>
                          <span class="percent" v-if="userCoupon.coupon.discount_type === 'percentage'">%</span>
                        </div>
                        <div class="coupon-type">
                          {{ userCoupon.coupon.discount_type === 'fixed' ? '满减券' : '折扣券' }}
                        </div>
                      </div>
                      <div class="coupon-body">
                        <h4 class="coupon-code">{{ userCoupon.coupon.code }}</h4>
                        <p class="coupon-desc">
                          {{ userCoupon.coupon.discount_type === 'fixed' 
                            ? `满 ¥${userCoupon.coupon.min_purchase} 可用` 
                            : `满 ¥${userCoupon.coupon.min_purchase} 可用` }}
                        </p>
                        <p class="coupon-used">
                          <el-icon><CircleCheck /></el-icon>
                          {{ userCoupon.used_at ? `使用时间: ${formatDate(userCoupon.used_at)}` : '已使用' }}
                        </p>
                      </div>
                    </el-card>
                  </el-col>
                </el-row>
              </el-tab-pane>
              
              <el-tab-pane label="已过期" name="expired">
                <el-empty v-if="myCoupons.expired.length === 0" description="暂无已过期优惠券" />
                <el-row :gutter="20" v-else>
                  <el-col :xs="24" :sm="12" :md="8" v-for="(userCoupon, index) in myCoupons.expired" :key="`${userCoupon.coupon_id}-${index}`" class="mb-4">
                    <el-card shadow="hover" class="coupon-card expired">
                      <div class="coupon-header">
                        <div class="coupon-value">
                          <span class="currency" v-if="userCoupon.coupon.discount_type === 'fixed'">¥</span>
                          <span class="amount">{{ getCouponDisplayValue(userCoupon.coupon) }}</span>
                          <span class="percent" v-if="userCoupon.coupon.discount_type === 'percentage'">%</span>
                        </div>
                        <div class="coupon-type">
                          {{ userCoupon.coupon.discount_type === 'fixed' ? '满减券' : '折扣券' }}
                        </div>
                      </div>
                      <div class="coupon-body">
                        <h4 class="coupon-code">{{ userCoupon.coupon.code }}</h4>
                        <p class="coupon-desc">
                          {{ userCoupon.coupon.discount_type === 'fixed' 
                            ? `满 ¥${userCoupon.coupon.min_purchase} 可用` 
                            : `满 ¥${userCoupon.coupon.min_purchase} 可用` }}
                        </p>
                        <p class="coupon-expiry">
                          <el-icon><Warning /></el-icon>
                          {{ userCoupon.coupon.valid_until 
                            ? `已于 ${formatDate(userCoupon.coupon.valid_until)} 过期` 
                            : '已过期' }}
                        </p>
                      </div>
                    </el-card>
                  </el-col>
                </el-row>
              </el-tab-pane>
            </el-tabs>
            
            <div class="mt-5 p-4 claim-section">
              <h3 class="mb-3">领取优惠券</h3>
              <div class="flex gap-3" style="max-width: 500px">
                <el-input
                  v-model="claimCouponCode"
                  placeholder="请输入优惠券码"
                  size="large"
                  clearable
                  @keyup.enter="handleClaimCouponUserCenter"
                >
                  <template #prefix>
                    <el-icon><Present /></el-icon>
                  </template>
                </el-input>
                <el-button 
                  type="primary" 
                  size="large"
                  :loading="claimingCoupon"
                  @click="handleClaimCouponUserCenter"
                >
                  立即领取
                </el-button>
              </div>
              <p class="text-sm text-gray mt-3">
                <el-icon><InfoFilled /></el-icon>
                测试券码：NEWUSER10 (首单9折) | SAVE20 (满100减20) | VIP50 (满200享5折) | LEARN15 (满50减15)
              </p>
            </div>
          </div>

          <div v-else-if="activeTab === 'projects'">
            <div class="flex justify-between items-center mb-4">
              <h2 class="section-title">我的项目</h2>
              <el-button type="primary" @click="addProjectDialog = true">
                <el-icon><Plus /></el-icon> 新建项目
              </el-button>
            </div>
            <el-empty v-if="projects.length === 0" description="暂无项目" />
            <el-row :gutter="20" v-else>
              <el-col :xs="24" :sm="12" :md="8" v-for="(project, index) in projects" :key="project.id" class="mb-4">
                <el-card shadow="hover" class="project-card" :class="{ 'alternate-row': index % 2 !== 0 }">
                  <template #header>
                    <div class="flex justify-between items-center">
                      <span>{{ project.title }}</span>
                      <el-button size="small" text @click="deleteProject(project.id)">
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </div>
                  </template>
                  <el-tag size="small">{{ project.language }}</el-tag>
                  <div class="project-meta text-xs text-gray mt-2">
                    {{ formatDate(project.created_at) }}
                  </div>
                  <el-button type="primary" size="small" class="mt-2 w-full" @click="openProject(project)">
                    打开项目
                  </el-button>
                </el-card>
              </el-col>
            </el-row>
          </div>

           <div v-else-if="activeTab === 'favorites'">
            <h2 class="section-title">我的收藏</h2>
            <el-empty v-if="favorites.length === 0" description="暂无收藏的课程" />
            <el-row :gutter="20" v-else>
              <el-col :xs="24" :sm="12" :md="8" v-for="(course, index) in favorites" :key="course.id" class="mb-4">
                <CourseCard :course="course" :class="{ 'alternate-row': index % 2 !== 0 }" @click="router.push(`/courses/${course.id}`)" />
              </el-col>
            </el-row>
          </div>
          
           <div v-else-if="activeTab === 'orders'">
            <h2 class="section-title">订单记录</h2>
            <el-table :data="orders" style="width: 100%">
              <el-table-column prop="date" label="日期" width="150" />
              <el-table-column prop="order_number" label="订单号" width="180" />
              <el-table-column prop="course" label="课程" />
              <el-table-column prop="amount" label="金额" width="100">
                 <template #default="scope">
                   <span class="price">¥{{ scope.row.amount }}</span>
                 </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                 <template #default="scope">
                   <el-tag :type="scope.row.status === 'completed' ? 'success' : 'warning'">
                     {{ scope.row.status === 'completed' ? '已完成' : '待支付' }}
                   </el-tag>
                 </template>
              </el-table-column>
            </el-table>
          </div>

          <div v-else-if="activeTab === 'settings'">
            <h2 class="section-title">账户设置</h2>
            <el-form label-position="top" :model="settingsForm">
              <el-form-item label="用户名">
                <el-input v-model="settingsForm.username" disabled />
              </el-form-item>
              <el-form-item label="邮箱">
                <el-input v-model="settingsForm.email" disabled />
              </el-form-item>
              <el-form-item label="个性签名">
                <el-input v-model="settingsForm.bio" type="textarea" :rows="3" placeholder="写点什么..." />
              </el-form-item>
              <el-form-item label="新密码">
                <el-input v-model="settingsForm.password" type="password" placeholder="留空则不修改" />
              </el-form-item>
              <el-form-item label="确认密码">
                <el-input v-model="settingsForm.confirmPassword" type="password" placeholder="再次输入新密码" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveSettings">保存修改</el-button>
                <el-button @click="resetSettings">重置</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-image-viewer v-if="showImageViewer" :url-list="[currentImageUrl]" @close="showImageViewer = false" />

    <el-dialog v-model="editProfileDialog" title="编辑资料" width="500px">
      <el-form :model="profileForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="profileForm.username" disabled />
        </el-form-item>
        <el-form-item label="个性签名">
          <el-input v-model="profileForm.bio" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="头像">
          <el-upload
            class="avatar-uploader"
            :show-file-list="false"
            :before-upload="beforeAvatarUpload"
          >
            <img v-if="profileForm.avatar" :src="profileForm.avatar" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editProfileDialog = false">取消</el-button>
        <el-button type="primary" @click="saveProfile">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="noteDialogVisible" :title="editingNote ? '编辑笔记' : '添加笔记'" width="900px" class="note-dialog">
      <el-form :model="noteForm" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="noteForm.title" placeholder="笔记标题" />
        </el-form-item>
        <el-form-item label="课程">
          <el-select v-model="noteForm.course_id" placeholder="选择课程" style="width: 100%">
            <el-option v-for="course in inProgressCourses" :key="course.id" :label="course.title" :value="course.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容">
          <MarkdownEditor v-model="noteForm.content" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="noteDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveNote">{{ editingNote ? '更新' : '保存' }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="addProjectDialog" title="新建项目" width="500px">
      <el-form :model="projectForm" label-width="80px">
        <el-form-item label="项目名称">
          <el-input v-model="projectForm.title" placeholder="项目名称" />
        </el-form-item>
        <el-form-item label="编程语言">
          <el-select v-model="projectForm.language">
            <el-option label="JavaScript" value="javascript" />
            <el-option label="Python" value="python" />
            <el-option label="HTML" value="html" />
            <el-option label="CSS" value="css" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addProjectDialog = false">取消</el-button>
        <el-button type="primary" @click="saveProject">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { 
  Reading, Folder, Star, Tickets, Setting, Plus, Edit, Delete, Trophy, 
  User, Calendar, ChatDotRound, Clock, Medal, Search, MoreFilled, 
  Discount, CircleCheck, Warning, Present, InfoFilled
} from '@element-plus/icons-vue'
import { getDashboard, getProjects, getOrders, createProject, deleteProject as deleteProjectAPI, getFavorites, updateUserProfile, getUserAchievements, getEnrollmentsWithTime } from '../api/user'
import { getNotes, createNote, updateNote, deleteNote as deleteNoteAPI } from '../api/notes'
import { getMyCoupons, claimCoupon } from '../api/course'
import CourseCard from '../components/CourseCard.vue'
import MarkdownEditor from '../components/MarkdownEditor.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import html2canvas from 'html2canvas'
import { jsPDF } from 'jspdf'

const router = useRouter()
const authStore = useAuthStore()
const activeTab = ref('learning')
const learningTab = ref('inprogress')
const calendarValue = ref(new Date())
const showCalendar = ref(true)
const editProfileDialog = ref(false)
const noteDialogVisible = ref(false)
const addProjectDialog = ref(false)
const showImageViewer = ref(false)
const currentImageUrl = ref('')
const noteSearchKeyword = ref('')
const editingNote = ref(null)

const inProgressCourses = ref([])
const completedCourses = ref([])
const favorites = ref([])
const projects = ref([])
const notes = ref([])
const dashboard = ref(null)
const orders = ref([])
const achievements = ref([])

const couponTab = ref('available')
const myCoupons = reactive({
  available: [],
  used: [],
  expired: []
})
const claimCouponCode = ref('')
const claimingCoupon = ref(false)

const getCouponDisplayValue = (coupon) => {
  if (!coupon) return '0'
  if (coupon.discount_type === 'percentage') {
    return (100 - coupon.discount_value).toString()
  }
  return coupon.discount_value.toFixed(0)
}

const filteredNotes = computed(() => {
  if (!noteSearchKeyword.value) return notes.value
  const keyword = noteSearchKeyword.value.toLowerCase()
  return notes.value.filter(note => 
    note.title.toLowerCase().includes(keyword) || 
    note.content.toLowerCase().includes(keyword)
  )
})

const iconMap = {
  User,
  Reading,
  Calendar,
  ChatDotRound,
  Star,
  Clock,
  Medal,
  Trophy
}

const getIconComponent = (iconName) => {
  return iconMap[iconName] || Trophy
}

const formatUnlockDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')}`
}

const settingsForm = reactive({
  username: '',
  email: '',
  bio: '',
  password: '',
  confirmPassword: ''
})

const profileForm = reactive({
  username: '',
  bio: '',
  avatar: ''
})

const noteForm = reactive({
  title: '',
  content: '',
  course_id: null
})

const projectForm = reactive({
  title: '',
  language: 'javascript'
})

onMounted(async () => {
  try {
    settingsForm.username = authStore.user?.username || ''
    settingsForm.email = authStore.user?.email || ''
    settingsForm.bio = authStore.user?.bio || ''
    profileForm.username = authStore.user?.username || ''
    profileForm.bio = authStore.user?.bio || ''
    profileForm.avatar = authStore.user?.avatar || ''
    
    const enrollments = await getEnrollmentsWithTime()
    dashboard.value = await getDashboard()
    const all = enrollments.map(enrollment => ({
      id: enrollment.course.id,
      course_id: enrollment.course.id,
      title: enrollment.course.title,
      cover_image: enrollment.course.cover_image || 'https://placehold.co/300x200/409EFF/ffffff?text=Course',
      progress: enrollment.progress,
      study_duration: enrollment.study_duration || 0
    }))
    inProgressCourses.value = all.filter(c => c.progress < 100)
    completedCourses.value = all.filter(c => c.progress >= 100)

    projects.value = await getProjects()
    notes.value = await getNotes()
    favorites.value = await getFavorites()
    const orderList = await getOrders()
    orders.value = orderList.map(order => ({
      date: formatDate(order.created_at),
      order_number: order.order_number,
      course: order.course_title || '课程订单',
      amount: order.total_amount,
      status: order.status
    }))
    
    const achievementData = await getUserAchievements()
    if (achievementData && achievementData.achievements) {
      achievements.value = achievementData.achievements
    } else {
      achievements.value = achievementData || []
    }
    
    loadCoupons()
  } catch (error) {
    console.error('Failed to load user data', error)
  }
})

const loadCoupons = async () => {
  try {
    const data = await getMyCoupons()
    myCoupons.available = data.available || []
    myCoupons.used = data.used || []
    myCoupons.expired = data.expired || []
  } catch (error) {
    console.error('Failed to load coupons:', error)
  }
}

const handleCouponTabChange = () => {
  // 可以在这里根据tab切换做额外处理
}

const handleClaimCouponUserCenter = async () => {
  if (!claimCouponCode.value.trim()) {
    ElMessage.warning('请输入优惠券码')
    return
  }
  
  claimingCoupon.value = true
  try {
    const result = await claimCoupon(claimCouponCode.value.trim())
    if (result.success) {
      ElMessage.success(result.message)
      claimCouponCode.value = ''
      loadCoupons()
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '领取失败')
  } finally {
    claimingCoupon.value = false
  }
}

const handleMenuSelect = (key) => {
  activeTab.value = key
  if (key === 'coupons') {
    loadCoupons()
  }
}

const toggleCalendar = () => {
  showCalendar.value = !showCalendar.value
}

const getProgressColor = (percentage) => {
  if (percentage < 30) return '#F56C6C'
  if (percentage < 70) return '#E6A23C'
  return '#67C23A'
}

const formatStudyTime = (totalSeconds) => {
  if (!totalSeconds || totalSeconds <= 0) return '累计学习 0 分钟'
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  if (hours > 0) {
    return `累计学习 ${hours} 小时 ${minutes} 分钟`
  }
  return `累计学习 ${minutes} 分钟`
}

const truncateText = (text, length) => {
  return text.length > length ? text.substring(0, length) + '...' : text
}

const formatDate = (date) => {
  const d = new Date(date)
  return `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}`
}

const beforeAvatarUpload = (file) => {
  const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
  if (!isJPG) {
    ElMessage.error('只能上传 JPG/PNG 图片!')
    return false
  }
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }
  
  const reader = new FileReader()
  reader.onload = (e) => {
    profileForm.avatar = e.target.result
  }
  reader.readAsDataURL(file)
  return false
}

const previewImage = (url) => {
  currentImageUrl.value = url
  showImageViewer.value = true
}

const saveProfile = async () => {
  try {
    const updated = await updateUserProfile({
      avatar: profileForm.avatar,
      bio: profileForm.bio
    })
    authStore.user = updated
    localStorage.setItem('user', JSON.stringify(updated))
    settingsForm.bio = updated.bio || ''
    ElMessage.success('资料保存成功')
    editProfileDialog.value = false
  } catch (error) {
    ElMessage.error('资料保存失败')
  }
}

const saveSettings = async () => {
  if (settingsForm.password && settingsForm.password !== settingsForm.confirmPassword) {
    ElMessage.error('两次密码不一致')
    return
  }
  try {
    const payload = { bio: settingsForm.bio }
    if (settingsForm.password) {
      payload.password = settingsForm.password
    }
    const updated = await updateUserProfile(payload)
    authStore.user = updated
    localStorage.setItem('user', JSON.stringify(updated))
    profileForm.bio = updated.bio || ''
    settingsForm.password = ''
    settingsForm.confirmPassword = ''
    ElMessage.success('设置保存成功')
  } catch (error) {
    ElMessage.error('设置保存失败')
  }
}

const resetSettings = () => {
  settingsForm.password = ''
  settingsForm.confirmPassword = ''
}

const openAddNoteDialog = () => {
  editingNote.value = null
  noteForm.title = ''
  noteForm.content = ''
  noteForm.course_id = inProgressCourses.value.length > 0 ? inProgressCourses.value[0].id : null
  noteDialogVisible.value = true
}

const openEditNoteDialog = (note) => {
  editingNote.value = note
  noteForm.title = note.title
  noteForm.content = note.content
  noteForm.course_id = note.course_id
  noteDialogVisible.value = true
}

const searchNotes = async () => {
  try {
    notes.value = await getNotes({ search: noteSearchKeyword.value })
  } catch (error) {
    console.error('Search notes failed', error)
  }
}

const saveNote = async () => {
  if (!noteForm.title || !noteForm.content || !noteForm.course_id) {
    ElMessage.warning('请填写完整的笔记信息')
    return
  }
  try {
    if (editingNote.value) {
      const updated = await updateNote(editingNote.value.id, {
        title: noteForm.title,
        content: noteForm.content,
        course_id: noteForm.course_id
      })
      const index = notes.value.findIndex(n => n.id === editingNote.value.id)
      if (index !== -1) {
        notes.value[index] = updated
      }
      ElMessage.success('笔记更新成功')
    } else {
      const created = await createNote({
        title: noteForm.title,
        content: noteForm.content,
        course_id: noteForm.course_id
      })
      notes.value.unshift(created)
      ElMessage.success('笔记添加成功')
    }
    noteDialogVisible.value = false
    editingNote.value = null
    noteForm.title = ''
    noteForm.content = ''
    noteForm.course_id = null
  } catch (error) {
    ElMessage.error(editingNote.value ? '笔记更新失败' : '笔记添加失败')
  }
}

const exportMarkdown = (note) => {
  const content = `# ${note.title}\n\n${note.content}`
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${note.title}.md`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  ElMessage.success('Markdown 导出成功')
}

const exportPDF = async (note) => {
  try {
    const content = `
      <div style="padding: 40px; font-family: Arial, sans-serif;">
        <h1 style="color: #333; border-bottom: 2px solid #409EFF; padding-bottom: 10px;">${note.title}</h1>
        <div style="margin-top: 20px; line-height: 1.8; color: #555;">
          ${note.content.replace(/\n/g, '<br>')}
        </div>
      </div>
    `
    const container = document.createElement('div')
    container.innerHTML = content
    container.style.position = 'absolute'
    container.style.left = '-9999px'
    container.style.width = '800px'
    container.style.background = 'white'
    document.body.appendChild(container)
    
    const canvas = await html2canvas(container, {
      scale: 2,
      useCORS: true,
      backgroundColor: '#ffffff'
    })
    
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')
    const pdfWidth = pdf.internal.pageSize.getWidth()
    const pdfHeight = (canvas.height * pdfWidth) / canvas.width
    
    pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight)
    pdf.save(`${note.title}.pdf`)
    
    document.body.removeChild(container)
    ElMessage.success('PDF 导出成功')
  } catch (error) {
    console.error('PDF export error:', error)
    ElMessage.error('PDF 导出失败')
  }
}

const handleNoteAction = (command, note) => {
  switch (command) {
    case 'edit':
      openEditNoteDialog(note)
      break
    case 'export-md':
      exportMarkdown(note)
      break
    case 'export-pdf':
      exportPDF(note)
      break
    case 'delete':
      deleteNote(note.id)
      break
  }
}

const deleteNote = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这条笔记吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteNoteAPI(id)
    notes.value = notes.value.filter(n => n.id !== id)
    ElMessage.success('笔记删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('笔记删除失败')
    }
  }
}

const saveProject = async () => {
  if (!projectForm.title) {
    ElMessage.warning('请输入项目名称')
    return
  }
  try {
    const created = await createProject({
      title: projectForm.title,
      language: projectForm.language,
      code: ''
    })
    projects.value.unshift(created)
    ElMessage.success('项目创建成功')
    addProjectDialog.value = false
    projectForm.title = ''
  } catch (error) {
    ElMessage.error('项目创建失败')
  }
}

const deleteProject = async (id) => {
  try {
    await deleteProjectAPI(id)
    projects.value = projects.value.filter(p => p.id !== id)
    ElMessage.success('项目删除成功')
  } catch (error) {
    ElMessage.error('项目删除失败')
  }
}

const openProject = (project) => {
  router.push('/sandbox')
}
</script>

<style scoped>
.user-center-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.text-center {
  text-align: center;
}

.text-gray {
  color: #999;
}

.text-sm {
  font-size: 12px;
}

.text-xs {
  font-size: 11px;
}

.mt-2 { margin-top: 0.5rem; }
.mt-4 { margin-top: 1rem; }
.mt-5 { margin-top: 2rem; }
.mb-4 { margin-bottom: 1rem; }
.p-3 { padding: 0.75rem; }

.profile-card {
  position: sticky;
  top: 20px;
}

.avatar-uploader {
  cursor: pointer;
  position: relative;
  overflow: hidden;
  border-radius: 50%;
  width: 100px;
  height: 100px;
  margin: 0 auto;
}

.avatar-uploader :deep(.el-upload) {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed #d9d9d9;
  border-radius: 50%;
  transition: all 0.3s;
}

.avatar-uploader :deep(.el-upload:hover) {
  border-color: #409EFF;
}

.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
}

.username {
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  font-size: 12px;
  color: #666;
}

.achievements {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.achievement-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 8px;
  border-radius: 12px;
  transition: all 0.3s;
  cursor: pointer;
  position: relative;
}

.achievement-item.unlocked {
  background: linear-gradient(135deg, rgba(255, 249, 230, 0.6) 0%, rgba(255, 245, 214, 0.6) 100%);
  border: 1px solid rgba(255, 215, 0, 0.3);
}

.achievement-item.unlocked:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 193, 7, 0.2);
}

.achievement-item.locked {
  background: rgba(245, 245, 245);
  opacity: 0.7;
}

.achievement-icon-wrapper {
  position: relative;
}

.achievement-item.unlocked .achievement-icon-wrapper::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
  background: radial-gradient(circle, rgba(255, 215, 0, 0.4) 0%, transparent 70%);
  border-radius: 50%;
  z-index: -1;
}

.achievement-name {
  font-size: 11px;
  font-weight: 600;
  color: #1f2a44;
  text-align: center;
}

.achievement-item.locked .achievement-name {
  color: #909399;
}

.unlock-date {
  font-size: 10px;
  color: #e6a23c;
}

.progress-hint {
  font-size: 10px;
  color: #909399;
  text-align: center;
  line-height: 1.3;
  max-width: 100px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.sidebar-menu {
  border-right: none;
}

.section-title {
  margin-top: 0;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #409EFF;
  color: #333;
}

.course-thumb {
  width: 100%;
  height: 140px;
  object-fit: cover;
  cursor: pointer;
}

.course-card h4 {
  margin: 0 0 10px;
  font-size: 14px;
  color: #333;
}

.study-time-text {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.project-card {
  cursor: pointer;
}

.project-meta {
  margin-top: 10px;
}

.note-item {
  margin-bottom: 15px;
}

.note-content h4 {
  margin: 0 0 5px;
  color: #333;
}

.note-content p {
  margin: 5px 0;
}

.note-meta {
  margin-top: 10px;
}

.alternate-row {
  background-color: #fafafa;
}

.price {
  color: #F56C6C;
  font-weight: bold;
}

.flex {
  display: flex;
}

.flex-grow {
  flex: 1;
}

.justify-between {
  justify-content: space-between;
}

.justify-center {
  justify-content: center;
}

.items-center {
  align-items: center;
}

.items-start {
  align-items: flex-start;
}

.w-full {
  width: 100%;
}

:deep(.el-calendar-table .el-calendar-day) {
  height: 80px;
}

@media (max-width: 768px) {
  .profile-card {
    position: static;
  }
  
  .course-thumb {
    height: 120px;
  }
}

:deep(.note-dialog .el-dialog__body) {
  padding-top: 10px;
}

.coupon-card {
  border-radius: 12px;
  overflow: hidden;
  position: relative;
}

.coupon-card.available {
  background: linear-gradient(135deg, #fff 0%, #f0f9ff 100%);
  border: 2px solid #409eff;
}

.coupon-card.used {
  background: #f5f7fa;
  border: 2px solid #c0c4cc;
  opacity: 0.8;
}

.coupon-card.expired {
  background: #f5f7fa;
  border: 2px dashed #c0c4cc;
  opacity: 0.6;
}

.coupon-header {
  background: linear-gradient(135deg, #409eff 0%, #337ecc 100%);
  color: white;
  padding: 20px;
  text-align: center;
  position: relative;
}

.coupon-card.used .coupon-header,
.coupon-card.expired .coupon-header {
  background: linear-gradient(135deg, #909399 0%, #606266 100%);
}

.coupon-value {
  display: flex;
  align-items: baseline;
  justify-content: center;
  font-weight: bold;
}

.coupon-value .currency {
  font-size: 18px;
  margin-right: 2px;
}

.coupon-value .amount {
  font-size: 48px;
  line-height: 1;
}

.coupon-value .percent {
  font-size: 24px;
  margin-left: 2px;
}

.coupon-type {
  margin-top: 8px;
  font-size: 14px;
  opacity: 0.9;
}

.coupon-body {
  padding: 16px;
}

.coupon-code {
  margin: 0 0 8px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  font-family: 'Courier New', monospace;
}

.coupon-desc {
  margin: 0 0 8px;
  font-size: 13px;
  color: #606266;
}

.coupon-expiry, .coupon-used {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0;
  font-size: 12px;
  color: #909399;
}

.coupon-footer {
  padding: 12px 16px;
  border-top: 1px dashed #e4e7ed;
}

.claim-section {
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border-radius: 12px;
}

.mb-3 {
  margin-bottom: 0.75rem;
}

.mt-5 {
  margin-top: 1.25rem;
}

.p-4 {
  padding: 1rem;
}

.text-sm {
  font-size: 12px;
}

.text-gray {
  color: #909399;
}

.gap-3 {
  gap: 0.75rem;
}

.flex {
  display: flex;
}

.w-full {
  width: 100%;
}
</style>
