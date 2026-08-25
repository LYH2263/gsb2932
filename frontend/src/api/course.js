import request from '../utils/request'

export function getCourses(params) {
  return request({
    url: '/courses/',
    method: 'get',
    params
  })
}

export function getCourse(id) {
  return request({
    url: `/courses/${id}`,
    method: 'get'
  })
}

export function enrollCourse(id) {
  return request({
    url: `/courses/${id}/enroll`,
    method: 'post'
  })
}

export function getEnrolledCourses() {
  return request({
    url: '/courses/enrolled',
    method: 'get'
  })
}

export function updateProgress(id, progress, lastLessonId) {
  return request({
    url: `/courses/${id}/progress`,
    method: 'put',
    data: {
      progress,
      last_lesson_id: lastLessonId
    }
  })
}

export function toggleFavorite(courseId) {
  return request({
    url: `/user/favorites/${courseId}`,
    method: 'post'
  })
}

export function getCourseReviews(courseId) {
  return request({
    url: `/courses/${courseId}/reviews`,
    method: 'get'
  })
}

export function createCourseReview(courseId, data) {
  return request({
    url: `/courses/${courseId}/reviews`,
    method: 'post',
    data
  })
}

export function purchaseCourse(courseId) {
  return request({
    url: `/courses/${courseId}/purchase`,
    method: 'post'
  })
}

export function getCourseQuestions(courseId) {
  return request({
    url: `/courses/${courseId}/questions`,
    method: 'get'
  })
}

export function createCourseQuestion(courseId, data) {
  return request({
    url: `/courses/${courseId}/questions`,
    method: 'post',
    data
  })
}

export function markLessonComplete(courseId, lessonId, studyDuration = 0) {
  return request({
    url: `/courses/${courseId}/lessons/${lessonId}/complete`,
    method: 'post',
    data: { study_duration: studyDuration }
  })
}

export function getCourseProgress(courseId) {
  return request({
    url: `/courses/${courseId}/progress`,
    method: 'get'
  })
}

export function getRecommendedCourses(limit) {
  return request({
    url: '/courses/recommended',
    method: 'get',
    params: { limit }
  })
}

export function getTrendingCourses(days, limit) {
  return request({
    url: '/courses/trending',
    method: 'get',
    params: { days, limit }
  })
}

export function getCourseDiscount(courseId) {
  return request({
    url: `/coupons/course/${courseId}/discount`,
    method: 'get'
  })
}

export function getCoursesWithDiscounts() {
  return request({
    url: '/coupons/with-discounts',
    method: 'get'
  })
}

export function applyCoupon(code, courseId) {
  return request({
    url: '/coupons/apply',
    method: 'post',
    data: { code, course_id: courseId }
  })
}

export function claimCoupon(code) {
  return request({
    url: `/coupons/claim/${code}`,
    method: 'post'
  })
}

export function getMyCoupons() {
  return request({
    url: '/coupons/my',
    method: 'get'
  })
}

export function purchaseCourseWithCoupon(courseId, couponCode) {
  return request({
    url: `/courses/${courseId}/purchase`,
    method: 'post',
    data: { coupon_code: couponCode }
  })
}
