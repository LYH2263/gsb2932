import request from '../utils/request'

export function getDashboard() {
  return request({
    url: '/user/dashboard',
    method: 'get'
  })
}

export function getFavorites() {
  return request({
    url: '/user/favorites',
    method: 'get'
  })
}

export function getProjects() {
  return request({
    url: '/user/projects',
    method: 'get'
  })
}

export function createProject(data) {
  return request({
    url: '/user/projects',
    method: 'post',
    data
  })
}

export function deleteProject(projectId) {
  return request({
    url: `/user/projects/${projectId}`,
    method: 'delete'
  })
}

export function getOrders() {
  return request({
    url: '/user/orders',
    method: 'get'
  })
}

export function addFavorite(courseId) {
  return request({
    url: `/user/favorites/${courseId}`,
    method: 'post'
  })
}

export function removeFavorite(courseId) {
  return request({
    url: `/user/favorites/${courseId}`,
    method: 'delete'
  })
}

export function updateUserProfile(data) {
  return request({
    url: '/auth/me',
    method: 'put',
    data
  })
}

export function getEnrollmentsWithTime() {
  return request({
    url: '/user/enrollments-with-time',
    method: 'get'
  })
}

export function getUserAchievements() {
  return request({
    url: '/user/achievements',
    method: 'get'
  })
}
