<script setup>
import { useAuthStore } from '@/store/auth'
import { useRouter } from 'vue-router'
import { ref } from 'vue'

const authStore = useAuthStore()
const router = useRouter()
const showMobileMenu = ref(false)

const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value
}

const logout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<template>
  <header class="bg-white shadow">
    <div class="container mx-auto px-4 py-3">
      <div class="flex items-center justify-between">
        <!-- Логотип и название сайта -->
        <div class="flex items-center">
          <router-link to="/" class="text-xl font-bold text-primary">
            Портфолио студентов
          </router-link>
        </div>
        
        <!-- Навигация для десктопа -->
        <nav class="hidden md:flex items-center space-x-6">
          <router-link to="/" class="nav-link">
            Главная
          </router-link>
          
          <router-link to="/portfolios" class="nav-link">
            Портфолио
          </router-link>
          
          <!-- Ссылка на админ-панель для администраторов и преподавателей -->
          <router-link 
            v-if="authStore.isAdmin || authStore.isTeacher" 
            to="/admin" 
            class="nav-link"
          >
            Администрирование
          </router-link>
          
          <!-- Меню пользователя -->
          <div v-if="authStore.isAuthenticated" class="relative inline-block text-left group">
            <button 
              type="button" 
              class="flex items-center space-x-1 text-secondary-gray hover:text-primary focus:outline-none"
            >
              <span>{{ authStore.userFullName || authStore.user.username }}</span>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            
            <div class="absolute right-0 w-48 mt-2 origin-top-right bg-white border border-secondary-gray/20 rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300">
              <div class="py-1">
                <router-link 
                  v-if="authStore.isStudent"
                  to="/portfolios" 
                  class="block px-4 py-2 text-sm text-secondary-gray hover:bg-secondary-gray/10"
                >
                  Мое портфолио
                </router-link>
                
                <button 
                  @click="logout" 
                  class="block w-full text-left px-4 py-2 text-sm text-secondary-gray hover:bg-secondary-gray/10"
                >
                  Выйти
                </button>
              </div>
            </div>
          </div>
          
          <!-- Кнопки авторизации для неавторизованных пользователей -->
          <template v-else>
            <router-link to="/login" class="nav-link">
              Войти
            </router-link>
            
            <router-link to="/register" class="btn btn-primary">
              Регистрация
            </router-link>
          </template>
        </nav>
        
        <!-- Кнопка мобильного меню -->
        <button 
          @click="toggleMobileMenu" 
          class="md:hidden text-secondary-gray focus:outline-none"
        >
          <svg v-if="!showMobileMenu" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <!-- Мобильное меню -->
      <div v-show="showMobileMenu" class="md:hidden mt-4">
        <div class="flex flex-col space-y-3 py-3">
          <router-link 
            to="/" 
            class="nav-link block"
            @click="showMobileMenu = false"
          >
            Главная
          </router-link>
          
          <router-link 
            to="/portfolios" 
            class="nav-link block"
            @click="showMobileMenu = false"
          >
            Портфолио
          </router-link>
          
          <!-- Ссылка на админ-панель для администраторов и преподавателей -->
          <router-link 
            v-if="authStore.isAdmin || authStore.isTeacher" 
            to="/admin" 
            class="nav-link block"
            @click="showMobileMenu = false"
          >
            Администрирование
          </router-link>
          
          <!-- Кнопки авторизации для неавторизованных пользователей -->
          <template v-if="!authStore.isAuthenticated">
            <router-link 
              to="/login" 
              class="nav-link block"
              @click="showMobileMenu = false"
            >
              Войти
            </router-link>
            
            <router-link 
              to="/register" 
              class="btn btn-primary block text-center"
              @click="showMobileMenu = false"
            >
              Регистрация
            </router-link>
          </template>
          
          <!-- Кнопка выхода для авторизованных пользователей -->
          <button 
            v-else
            @click="logout"
            class="text-left nav-link block"
          >
            Выйти ({{ authStore.userFullName || authStore.user.username }})
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.nav-link {
  @apply text-secondary-gray hover:text-primary transition-colors duration-200;
}
</style> 