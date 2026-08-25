import axios from 'axios'
import { ElMessage } from 'element-plus'

const service = axios.create({
  baseURL: '/api',
  timeout: 5000
})

let achievementHandler = null

export const setAchievementHandler = (handler) => {
  achievementHandler = handler
}

const processNewAchievements = (data) => {
  if (data && data.new_achievements && data.new_achievements.length > 0) {
    if (achievementHandler) {
      data.new_achievements.forEach(achievement => {
        achievementHandler(achievement)
      })
    }
  }
}

service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.log(error)
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  response => {
    const res = response.data
    processNewAchievements(res)
    return res
  },
  error => {
    console.log('err' + error)
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    } else {
      ElMessage({
        message: error.message || 'Error',
        type: 'error',
        duration: 5 * 1000
      })
    }
    return Promise.reject(error)
  }
)

export default service
