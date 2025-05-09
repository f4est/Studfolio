import { defineStore } from 'pinia'
import api from '@/api'
import { jwtDecode } from 'jwt-decode'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    accessToken: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    loading: false,
    error: null
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.accessToken && !!state.user,
    isTeacher: (state) => state.user?.role === 'teacher',
    isAdmin: (state) => state.user?.role === 'admin' || state.user?.is_superuser,
    isStudent: (state) => state.user?.role === 'student',
    userFullName: (state) => {
      if (!state.user) return ''
      return state.user.first_name && state.user.last_name 
        ? `${state.user.first_name} ${state.user.last_name}`
        : state.user.username
    }
  },
  
  actions: {
    async login(username, password) {
      this.loading = true
      this.error = null
      
      try {
        const response = await api.post('/users/login/', { username, password })
        
        const { user, access, refresh } = response.data
        
        // Сохраняем в хранилище
        this.setUserData(user, access, refresh)
        
        return user
      } catch (error) {
        this.error = error.response?.data?.error || 'Ошибка входа в систему'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async register(userData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await api.post('/users/', userData)
        return response.data
      } catch (error) {
        this.error = error.response?.data || 'Ошибка при регистрации'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async logout() {
      // Очищаем данные пользователя
      this.user = null
      this.accessToken = null
      this.refreshToken = null
      
      // Удаляем из localStorage
      localStorage.removeItem('user')
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    },
    
    setUserData(user, accessToken, refreshToken) {
      this.user = user
      this.accessToken = accessToken
      this.refreshToken = refreshToken
      
      // Сохраняем в localStorage
      localStorage.setItem('user', JSON.stringify(user))
      localStorage.setItem('access_token', accessToken)
      localStorage.setItem('refresh_token', refreshToken)
    },
    
    checkTokenExpiration() {
      if (!this.accessToken) return false
      
      try {
        const decoded = jwtDecode(this.accessToken)
        const currentTime = Date.now() / 1000
        
        if (decoded.exp < currentTime) {
          // Токен истек, нужно выйти
          this.logout()
          return false
        }
        
        return true
      } catch (error) {
        console.error('Error decoding token:', error)
        this.logout()
        return false
      }
    }
  }
}) 