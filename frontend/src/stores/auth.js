import { defineStore } from 'pinia'
import { login, register, getInfo } from '../api/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user')) || null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async login(userInfo) {
      try {
        const response = await login(userInfo)
        this.token = response.access_token
        localStorage.setItem('token', this.token)
        const user = await getInfo()
        this.user = user
        localStorage.setItem('user', JSON.stringify(user))
        return response
      } catch (error) {
        throw error
      }
    },
    async fetchUser() {
      if (!this.token) return null
      const user = await getInfo()
      this.user = user
      localStorage.setItem('user', JSON.stringify(user))
      return user
    },
    async register(userInfo) {
      try {
        await register(userInfo)
      } catch (error) {
        throw error
      }
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})
