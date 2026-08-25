import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import CourseList from '../views/CourseList.vue'
import CourseDetail from '../views/CourseDetail.vue'
import UserCenter from '../views/UserCenter.vue'
import CodeSandbox from '../views/CodeSandbox.vue'
import SharedSandbox from '../views/SharedSandbox.vue'
import Community from '../views/Community.vue'
import Challenge from '../views/Challenge.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/courses',
      name: 'courses',
      component: CourseList,
      meta: { requiresAuth: true }
    },
    {
      path: '/courses/:id',
      name: 'course-detail',
      component: CourseDetail,
      meta: { requiresAuth: true }
    },
    {
      path: '/user',
      name: 'user',
      component: UserCenter,
      meta: { requiresAuth: true }
    },
    {
      path: '/sandbox',
      name: 'sandbox',
      component: CodeSandbox,
      meta: { requiresAuth: true }
    },
    {
      path: '/sandbox/shared/:shareToken',
      name: 'shared-sandbox',
      component: SharedSandbox
    },
    {
      path: '/community',
      name: 'community',
      component: Community
    },
    {
      path: '/challenges',
      name: 'challenges',
      component: Challenge,
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
