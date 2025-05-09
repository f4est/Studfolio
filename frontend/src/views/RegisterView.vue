<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()
const router = useRouter()

const username = ref('')
const email = ref('')
const firstName = ref('')
const lastName = ref('')
const password = ref('')
const confirmPassword = ref('')
const role = ref('student')
const error = ref('')
const loading = ref(false)

const handleRegister = async () => {
  if (!username.value || !email.value || !password.value || !confirmPassword.value) {
    error.value = 'Пожалуйста, заполните все обязательные поля'
    return
  }
  
  if (password.value !== confirmPassword.value) {
    error.value = 'Пароли не совпадают'
    return
  }
  
  loading.value = true
  
  try {
    const userData = {
      username: username.value,
      email: email.value,
      first_name: firstName.value,
      last_name: lastName.value,
      password: password.value,
      role: role.value
    }
    
    await authStore.register(userData)
    
    // После успешной регистрации перенаправляем на страницу входа
    router.push('/login')
  } catch (err) {
    error.value = err.response?.data || 'Ошибка при регистрации'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-md mx-auto">
    <div class="bg-white p-8 rounded-lg shadow">
      <h1 class="text-2xl font-bold mb-6 text-center text-primary">Регистрация</h1>
      
      <div v-if="error" class="mb-4 p-3 bg-error/10 border border-error text-error rounded">
        {{ error }}
      </div>
      
      <form @submit.prevent="handleRegister">
        <div class="mb-4">
          <label for="username" class="form-label">Имя пользователя <span class="text-error">*</span></label>
          <input
            id="username"
            v-model="username"
            type="text"
            class="form-input"
            placeholder="Введите имя пользователя"
            required
          />
        </div>
        
        <div class="mb-4">
          <label for="email" class="form-label">Email <span class="text-error">*</span></label>
          <input
            id="email"
            v-model="email"
            type="email"
            class="form-input"
            placeholder="Введите email"
            required
          />
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label for="first-name" class="form-label">Имя</label>
            <input
              id="first-name"
              v-model="firstName"
              type="text"
              class="form-input"
              placeholder="Введите имя"
            />
          </div>
          
          <div>
            <label for="last-name" class="form-label">Фамилия</label>
            <input
              id="last-name"
              v-model="lastName"
              type="text"
              class="form-input"
              placeholder="Введите фамилию"
            />
          </div>
        </div>
        
        <div class="mb-4">
          <label for="password" class="form-label">Пароль <span class="text-error">*</span></label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="form-input"
            placeholder="Введите пароль"
            required
          />
        </div>
        
        <div class="mb-4">
          <label for="confirm-password" class="form-label">Подтверждение пароля <span class="text-error">*</span></label>
          <input
            id="confirm-password"
            v-model="confirmPassword"
            type="password"
            class="form-input"
            placeholder="Повторите пароль"
            required
          />
        </div>
        
        <div class="mb-6">
          <label for="role" class="form-label">Роль <span class="text-error">*</span></label>
          <select
            id="role"
            v-model="role"
            class="form-input"
            required
          >
            <option value="student">Студент</option>
            <option value="teacher">Преподаватель</option>
          </select>
        </div>
        
        <button
          type="submit"
          class="btn btn-primary w-full"
          :disabled="loading"
        >
          <span v-if="loading">Регистрация...</span>
          <span v-else>Зарегистрироваться</span>
        </button>
      </form>
      
      <div class="mt-4 text-center">
        <router-link to="/login" class="text-primary hover:underline">
          Уже есть аккаунт? Войти
        </router-link>
      </div>
    </div>
  </div>
</template> 