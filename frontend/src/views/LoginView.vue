<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const handleLogin = async () => {
  if (!username.value || !password.value) {
    error.value = 'Пожалуйста, заполните все поля'
    return
  }
  
  loading.value = true
  
  try {
    await authStore.login(username.value, password.value)
    
    // Перенаправление пользователя после успешного входа
    const redirectPath = route.query.redirect || '/'
    router.push(redirectPath)
  } catch (err) {
    error.value = err.response?.data?.error || 'Ошибка входа в систему'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-md mx-auto">
    <div class="bg-white p-8 rounded-lg shadow">
      <h1 class="text-2xl font-bold mb-6 text-center text-primary">Вход в систему</h1>
      
      <div v-if="error" class="mb-4 p-3 bg-error/10 border border-error text-error rounded">
        {{ error }}
      </div>
      
      <form @submit.prevent="handleLogin">
        <div class="mb-4">
          <label for="username" class="form-label">Имя пользователя</label>
          <input
            id="username"
            v-model="username"
            type="text"
            class="form-input"
            placeholder="Введите имя пользователя"
            required
          />
        </div>
        
        <div class="mb-6">
          <label for="password" class="form-label">Пароль</label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="form-input"
            placeholder="Введите пароль"
            required
          />
        </div>
        
        <button
          type="submit"
          class="btn btn-primary w-full"
          :disabled="loading"
        >
          <span v-if="loading">Вход...</span>
          <span v-else>Войти</span>
        </button>
      </form>
      
      <div class="mt-4 text-center">
        <router-link to="/register" class="text-primary hover:underline">
          Нет аккаунта? Зарегистрироваться
        </router-link>
      </div>
    </div>
  </div>
</template> 