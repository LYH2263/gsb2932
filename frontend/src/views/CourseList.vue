<template>
  <div class="course-list-container">
    <el-backtop :right="40" :bottom="60" />
    
    <el-card shadow="never" class="search-section mb-4">
      <el-row :gutter="20" align="middle">
        <el-col :xs="24" :sm="24" :md="16">
          <el-space wrap>
            <el-select v-model="filters.level" placeholder="难度" clearable style="width: 120px">
              <el-option label="初级" value="Beginner" />
              <el-option label="中级" value="Intermediate" />
              <el-option label="高级" value="Advanced" />
            </el-select>
            <el-select v-model="filters.techStack" placeholder="技术栈" clearable style="width: 150px">
              <el-option label="Vue" value="vue" />
              <el-option label="React" value="react" />
              <el-option label="Python" value="python" />
              <el-option label="JavaScript" value="javascript" />
              <el-option label="CSS" value="css" />
            </el-select>
            <el-select v-model="filters.price" placeholder="价格" clearable style="width: 120px">
              <el-option label="免费" value="free" />
              <el-option label="付费" value="paid" />
            </el-select>
            <el-select v-model="filters.sort" placeholder="排序" style="width: 120px">
              <el-option label="热度" value="popularity" />
              <el-option label="最新" value="newest" />
              <el-option label="评分" value="rating" />
            </el-select>
            <el-button @click="resetFilters">重置筛选</el-button>
          </el-space>
        </el-col>
        <el-col :xs="24" :sm="24" :md="8">
          <div class="search-actions">
            <el-input
              v-model="searchQuery"
              placeholder="搜索课程名称、简介..."
              prefix-icon="Search"
              clearable
              size="large"
              @input="handleSearch"
            >
              <template #append>
                <el-button @click="handleSearch">搜索</el-button>
              </template>
            </el-input>
            <div class="view-toggle">
              <el-radio-group v-model="viewMode" size="large">
                <el-radio-button label="grid">
                  <el-icon><Grid /></el-icon> 网格
                </el-radio-button>
                <el-radio-button label="list">
                  <el-icon><List /></el-icon> 列表
                </el-radio-button>
              </el-radio-group>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <div class="result-count mb-4">
      <el-text type="info">共找到 {{ filteredCourses.length }} 门课程</el-text>
    </div>

    <el-row :gutter="20" v-if="showSidebar">
      <el-col :xs="24" :sm="24" :md="4">
        <el-card shadow="never" class="sidebar-card">
          <template #header>
            <span>学习路径</span>
          </template>
          <div class="path-item" v-for="path in learningPaths" :key="path.name">
            <el-link @click="filterByPath(path)">{{ path.name }}</el-link>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="20">
        <div v-loading="loading" class="courses-display">
          <el-empty v-if="filteredCourses.length === 0" description="暂无匹配的课程" />
          
          <el-row :gutter="20" v-else-if="viewMode === 'grid'">
            <el-col :xs="24" :sm="12" :md="6" v-for="(course, index) in paginatedCourses" :key="course.id" class="mb-4">
              <CourseCard :course="course" :class="{ 'alternate-row': index % 2 !== 0 }" @click="goToCourse(course.id)" />
            </el-col>
          </el-row>

          <div v-else class="list-view">
            <el-card 
              v-for="(course, index) in paginatedCourses" 
              :key="course.id" 
              shadow="hover" 
              class="mb-4 course-list-item" 
              :class="{ 'alternate-row': index % 2 !== 0 }"
              @click="goToCourse(course.id)"
            >
              <div class="flex">
                <img :src="course.cover_image" class="list-image" @click.stop="previewImage(course.cover_image)" />
                <div class="list-content ml-4 flex-grow">
                  <div class="flex justify-between">
                    <h3>{{ course.title }}</h3>
                    <div class="price">{{ course.price === 0 ? '免费' : '¥' + course.price }}</div>
                  </div>
                  <p class="description text-gray">{{ course.description }}</p>
                  <div class="meta flex items-center mt-2">
                    <el-tag :type="getLevelType(course.level)" size="small">{{ getLevelText(course.level) }}</el-tag>
                    <span class="mr-4">{{ course.instructor }}</span>
                    <el-rate v-model="course.rating" disabled show-score text-color="#ff9900" score-template="{value}" />
                    <span class="ml-2 text-gray">({{ course.students_count }}人学习)</span>
                  </div>
                </div>
                <div class="list-actions">
                  <el-button type="primary" @click.stop="goToCourse(course.id)">查看详情</el-button>
                </div>
              </div>
            </el-card>
          </div>

          <div v-if="filteredCourses.length > pageSize" class="pagination text-center mt-4">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[12, 24, 36, 48]"
              :total="filteredCourses.length"
              layout="total, sizes, prev, pager, next, jumper"
            />
          </div>
        </div>
      </el-col>
    </el-row>

    <div v-else v-loading="loading" class="courses-display">
      <el-empty v-if="filteredCourses.length === 0" description="暂无匹配的课程" />
      
      <el-row :gutter="20" v-else-if="viewMode === 'grid'">
        <el-col :xs="24" :sm="12" :md="6" v-for="(course, index) in paginatedCourses" :key="course.id" class="mb-4">
          <CourseCard :course="course" :class="{ 'alternate-row': index % 2 !== 0 }" @click="goToCourse(course.id)" />
        </el-col>
      </el-row>

      <div v-else class="list-view">
        <el-card 
          v-for="(course, index) in paginatedCourses" 
          :key="course.id" 
          shadow="hover" 
          class="mb-4 course-list-item" 
          :class="{ 'alternate-row': index % 2 !== 0 }"
          @click="goToCourse(course.id)"
        >
          <div class="flex">
            <img :src="course.cover_image" class="list-image" @click.stop="previewImage(course.cover_image)" />
            <div class="list-content ml-4 flex-grow">
              <div class="flex justify-between">
                <h3>{{ course.title }}</h3>
                <div class="price">{{ course.price === 0 ? '免费' : '¥' + course.price }}</div>
              </div>
              <p class="description text-gray">{{ course.description }}</p>
              <div class="meta flex items-center mt-2">
                <el-tag :type="getLevelType(course.level)" size="small">{{ getLevelText(course.level) }}</el-tag>
                <span class="mr-4">{{ course.instructor }}</span>
                <el-rate v-model="course.rating" disabled show-score text-color="#ff9900" score-template="{value}" />
                <span class="ml-2 text-gray">({{ course.students_count }}人学习)</span>
              </div>
            </div>
            <div class="list-actions">
              <el-button type="primary" @click.stop="goToCourse(course.id)">查看详情</el-button>
            </div>
          </div>
        </el-card>
      </div>

      <div v-if="filteredCourses.length > pageSize" class="pagination text-center mt-4">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[12, 24, 36, 48]"
          :total="filteredCourses.length"
          layout="total, sizes, prev, pager, next, jumper"
        />
      </div>
    </div>

    <el-image-viewer v-if="showImageViewer" :url-list="[currentImageUrl]" @close="showImageViewer = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Grid, List } from '@element-plus/icons-vue'
import { getCourses } from '../api/course'
import CourseCard from '../components/CourseCard.vue'
import { ElImageViewer } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const searchQuery = ref('')
const viewMode = ref('grid')
const showSidebar = ref(true)
const showImageViewer = ref(false)
const currentImageUrl = ref('')
const currentPage = ref(1)
const pageSize = ref(12)

const filters = ref({
  level: '',
  techStack: '',
  price: '',
  sort: ''
})

const courses = ref([])

const learningPaths = [
  { name: '前端工程师入门', tech: ['vue', 'javascript', 'css'] },
  { name: 'Python 数据分析', tech: ['python'] },
  { name: '全栈开发', tech: ['vue', 'python', 'javascript'] },
  { name: 'UI/UX 设计', tech: ['css'] }
]

onMounted(async () => {
  loading.value = true
  try {
    const data = await getCourses({ limit: 100 })
    courses.value = data
  } catch (error) {
    console.error('Failed to fetch courses', error)
  } finally {
    loading.value = false
  }
})

const filteredCourses = computed(() => {
  return courses.value.filter(course => {
    const matchesSearch = course.title.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                          course.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesLevel = !filters.value.level || course.level === filters.value.level
    const matchesPrice = !filters.value.price || (filters.value.price === 'free' ? course.price === 0 : course.price > 0)
    
    let matchesTech = true
    if (filters.value.techStack) {
      const tech = filters.value.techStack.toLowerCase()
      matchesTech = course.title.toLowerCase().includes(tech) || 
                    course.description.toLowerCase().includes(tech) ||
                    (course.tags && course.tags.some(t => t.toLowerCase().includes(tech)))
    }
    
    return matchesSearch && matchesLevel && matchesPrice && matchesTech
  }).sort((a, b) => {
    if (filters.value.sort === 'popularity') return b.students_count - a.students_count
    if (filters.value.sort === 'rating') return b.rating - a.rating
    return 0
  })
})

const paginatedCourses = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredCourses.value.slice(start, end)
})

watch([filters, searchQuery], () => {
  currentPage.value = 1
})

watch(pageSize, () => {
  currentPage.value = 1
})

const handleSearch = () => {
  currentPage.value = 1
}

const resetFilters = () => {
  filters.value = {
    level: '',
    techStack: '',
    price: '',
    sort: ''
  }
  searchQuery.value = ''
  currentPage.value = 1
}

const filterByPath = (path) => {
  filters.value.techStack = path.tech[0]
}

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

const goToCourse = (id) => {
  router.push(`/courses/${id}`)
}

const previewImage = (url) => {
  currentImageUrl.value = url
  showImageViewer.value = true
}
</script>

<style scoped>
.course-list-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.search-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.search-section :deep(.el-card__body) {
  padding: 20px;
}

.search-section :deep(.el-input__wrapper) {
  background: white;
}

.search-actions {
  display: flex;
  flex-direction: row;
  gap: 12px;
  align-items: center;
  justify-content: flex-end;
}

.search-actions .el-input {
  width: auto;
  flex: 1;
  min-width: 200px;
}

.view-toggle {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.result-count {
  text-align: right;
}

.sidebar-card {
  position: sticky;
  top: 20px;
}

.path-item {
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.path-item:last-child {
  border-bottom: none;
}

.path-item .el-link {
  display: block;
  width: 100%;
}

.list-view .course-list-item {
  cursor: pointer;
  transition: transform 0.2s;
}

.list-view .course-list-item:hover {
  transform: translateX(5px);
}

.list-image {
  width: 200px;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.3s;
}

.list-image:hover {
  transform: scale(1.05);
}

.list-content {
  flex: 1;
}

.list-content h3 {
  margin: 0 0 10px;
  font-size: 18px;
  color: #333;
}

.description {
  margin: 0 0 12px;
  color: #666;
  line-height: 1.6;
}

.list-actions {
  display: flex;
  align-items: center;
}

.price {
  font-size: 20px;
  font-weight: bold;
  color: #F56C6C;
}

.alternate-row {
  background-color: #fafafa;
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

.items-center {
  align-items: center;
}

.ml-4 {
  margin-left: 1rem;
}

.mr-4 {
  margin-right: 1rem;
}

.ml-2 {
  margin-left: 0.5rem;
}

.mb-4 {
  margin-bottom: 1rem;
}

.mt-2 {
  margin-top: 0.5rem;
}

.mt-4 {
  margin-top: 1rem;
}

.text-right {
  text-align: right;
}

.text-center {
  text-align: center;
}

.text-gray {
  color: #999;
}

@media (max-width: 768px) {
  .list-image {
    width: 120px;
    height: 80px;
  }
  
  .list-content h3 {
    font-size: 16px;
  }
  
  .list-actions {
    display: none;
  }
}
</style>
