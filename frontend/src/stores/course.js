import { defineStore } from 'pinia'
import { getCourses, getCourse } from '../api/course'

export const useCourseStore = defineStore('course', {
  state: () => ({
    courses: [],
    currentCourse: null,
    loading: false
  }),
  actions: {
    async fetchCourses(params) {
      this.loading = true
      try {
        const response = await getCourses(params)
        this.courses = response
      } finally {
        this.loading = false
      }
    },
    async fetchCourseDetail(id) {
      this.loading = true
      try {
        const response = await getCourse(id)
        this.currentCourse = response
      } finally {
        this.loading = false
      }
    }
  }
})
