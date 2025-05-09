<script setup>
import { ref, onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import api from '@/api'

const authStore = useAuthStore()
const portfolios = ref([])
const loading = ref(true)
const error = ref(null)

// Форма для создания портфолио
const portfolioForm = ref({
  title: '',
  is_public: true,
  theme: 'default'
})

// Флаг для отображения формы создания портфолио
const showCreateForm = ref(false)

// Список доступных тем/шаблонов
const availableThemes = [
  { id: 'default', name: 'Стандартная', icon: '🎨', description: 'Универсальный шаблон с нейтральными цветами' },
  { id: 'dark', name: 'Темная', icon: '🌙', description: 'Темный фон с яркими акцентами' },
  { id: 'creative', name: 'Креативная', icon: '✨', description: 'Яркий дизайн для творческих специальностей' },
  { id: 'minimal', name: 'Минималистичная', icon: '⚪', description: 'Строгий минималистичный дизайн' },
  { id: 'corporate', name: 'Корпоративная', icon: '💼', description: 'Профессиональный дизайн для бизнеса' }
]

// Параметры поиска и фильтрации
const searchQuery = ref('')
const selectedFilter = ref('all') // all, student, teacher, skills

// Вычисляем, есть ли у текущего пользователя портфолио
const hasPortfolio = computed(() => {
  if (!authStore.isAuthenticated || !authStore.user || portfolios.value.length === 0) {
    return false
  }
  return portfolios.value.some(p => p.user && p.user.id === authStore.user.id)
})

// Открытие формы создания портфолио
const openCreateForm = () => {
  portfolioForm.value = {
    title: `Портфолио ${authStore.user.username}`,
    is_public: true,
    theme: 'default'
  }
  showCreateForm.value = true
}

// Закрытие формы создания портфолио
const closeCreateForm = () => {
  showCreateForm.value = false
}

// Создание портфолио
const createPortfolio = async () => {
  try {
    loading.value = true
    const response = await api.post('/portfolio/portfolios/', portfolioForm.value)
    
    // Добавляем новое портфолио в список
    portfolios.value.unshift(response.data)
    
    // Закрываем форму
    showCreateForm.value = false
  } catch (err) {
    console.error('Error creating portfolio:', err)
    error.value = 'Не удалось создать портфолио. Пожалуйста, попробуйте позже.'
  } finally {
    loading.value = false
  }
}

// Функция поиска портфолио
const searchPortfolios = async () => {
  try {
    loading.value = true
    
    // Формируем параметры запроса
    const params = {}
    
    // Добавляем строку поиска, если она есть
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    
    // Добавляем фильтры
    if (selectedFilter.value === 'student') {
      params.role = 'student'
    } else if (selectedFilter.value === 'teacher') {
      params.role = 'teacher'
    }
    
    const response = await api.get('/portfolio/portfolios/', { params })
    portfolios.value = response.data.results || response.data
    console.log('Filtered portfolios loaded:', portfolios.value)
  } catch (err) {
    console.error('Error searching portfolios:', err)
    error.value = 'Не удалось выполнить поиск. Пожалуйста, попробуйте позже.'
  } finally {
    loading.value = false
  }
}

// Сброс поиска и фильтров
const resetFilters = async () => {
  searchQuery.value = ''
  selectedFilter.value = 'all'
  await loadPortfolios()
}

// Загрузка всех портфолио
const loadPortfolios = async () => {
  try {
    loading.value = true
    const response = await api.get('/portfolio/portfolios/')
    portfolios.value = response.data.results || response.data
    console.log('Portfolios loaded:', portfolios.value)
  } catch (err) {
    console.error('Error fetching portfolios:', err)
    error.value = 'Не удалось загрузить портфолио. Пожалуйста, попробуйте позже.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadPortfolios()
})

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU')
}
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">Портфолио студентов</h1>
      
      <button
        v-if="authStore.isStudent && !hasPortfolio && !showCreateForm"
        @click="openCreateForm"
        class="btn btn-primary"
      >
        Создать портфолио
      </button>
    </div>
    
    <div v-if="error" class="p-4 mb-6 bg-error/10 border border-error text-error rounded">
      {{ error }}
    </div>
    
    <!-- Панель поиска и фильтрации -->
    <div v-if="!showCreateForm" class="bg-white p-4 rounded-lg shadow mb-6">
      <form @submit.prevent="searchPortfolios" class="space-y-4">
        <div class="flex flex-col md:flex-row gap-4">
          <div class="flex-grow">
            <label for="search-input" class="block text-sm font-medium text-gray-700 mb-1">
              Поиск портфолио
            </label>
            <input
              id="search-input"
              v-model="searchQuery"
              type="text"
              class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
              placeholder="Поиск по имени, навыкам, образованию..."
            />
          </div>
          
          <div class="md:w-1/4">
            <label for="filter-select" class="block text-sm font-medium text-gray-700 mb-1">
              Фильтр
            </label>
            <select
              id="filter-select"
              v-model="selectedFilter"
              class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
            >
              <option value="all">Все портфолио</option>
              <option value="student">Только студенты</option>
              <option value="teacher">Только преподаватели</option>
            </select>
          </div>
        </div>
        
        <div class="flex justify-end space-x-2">
          <button
            type="button"
            @click="resetFilters"
            class="px-3 py-1.5 bg-gray-100 text-gray-700 rounded border border-gray-300 hover:bg-gray-200 text-sm"
          >
            Сбросить
          </button>
          
          <button
            type="submit"
            class="px-3 py-1.5 bg-primary text-white rounded hover:bg-primary/90 text-sm"
            :disabled="loading"
          >
            <span v-if="loading">Поиск...</span>
            <span v-else>Найти</span>
          </button>
        </div>
      </form>
    </div>
    
    <!-- Форма создания портфолио -->
    <div v-if="showCreateForm" class="bg-white p-6 rounded-lg shadow mb-6">
      <h2 class="text-xl font-bold mb-4">Создание нового портфолио</h2>
      
      <form @submit.prevent="createPortfolio">
        <div class="mb-4">
          <label for="portfolio-title" class="block text-sm font-medium text-gray-700 mb-1">
            Название портфолио
          </label>
          <input
            id="portfolio-title"
            v-model="portfolioForm.title"
            type="text"
            class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
            placeholder="Введите название портфолио"
            required
          />
        </div>
        
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Видимость портфолио
          </label>
          <div class="flex items-center space-x-4">
            <label class="inline-flex items-center">
              <input
                type="radio"
                v-model="portfolioForm.is_public"
                :value="true"
                class="form-radio text-primary"
              />
              <span class="ml-2">Публичное</span>
            </label>
            
            <label class="inline-flex items-center">
              <input
                type="radio"
                v-model="portfolioForm.is_public"
                :value="false"
                class="form-radio text-primary"
              />
              <span class="ml-2">Приватное</span>
            </label>
          </div>
        </div>
        
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-3">
            Выберите шаблон оформления
          </label>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div
              v-for="theme in availableThemes"
              :key="theme.id"
              class="border rounded-lg p-4 cursor-pointer transition-all"
              :class="[
                portfolioForm.theme === theme.id 
                  ? 'border-primary bg-primary/5' 
                  : 'border-gray-200 hover:border-primary/30'
              ]"
              @click="portfolioForm.theme = theme.id"
            >
              <div class="flex items-center mb-2">
                <span class="text-2xl mr-2">{{ theme.icon }}</span>
                <span class="font-medium">{{ theme.name }}</span>
              </div>
              <p class="text-sm text-gray-600">{{ theme.description }}</p>
            </div>
          </div>
        </div>
        
        <div class="flex justify-end space-x-2">
          <button
            type="button"
            @click="closeCreateForm"
            class="px-4 py-2 bg-gray-100 text-gray-700 rounded border border-gray-300 hover:bg-gray-200"
          >
            Отмена
          </button>
          
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="loading"
          >
            <span v-if="loading">Создание...</span>
            <span v-else>Создать портфолио</span>
          </button>
        </div>
      </form>
    </div>
    
    <div v-if="loading && !showCreateForm" class="text-center py-8">
      <p class="text-secondary-gray">Загрузка портфолио...</p>
    </div>
    
    <div v-else-if="portfolios.length === 0 && !showCreateForm" class="bg-white p-8 rounded-lg shadow text-center">
      <p class="text-lg mb-4">Портфолио не найдены</p>
      
      <button
        v-if="authStore.isAuthenticated && authStore.isStudent"
        @click="openCreateForm"
        class="btn btn-primary"
      >
        Создать мое первое портфолио
      </button>
      
      <p v-else-if="!authStore.isAuthenticated" class="mt-4">
        <RouterLink to="/login" class="text-primary hover:underline">Войдите</RouterLink>
        или
        <RouterLink to="/register" class="text-primary hover:underline">зарегистрируйтесь</RouterLink>
        чтобы создать портфолио.
      </p>
    </div>
    
    <div v-else-if="!showCreateForm" class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="portfolio in portfolios"
        :key="portfolio.id"
        class="bg-white rounded-lg shadow overflow-hidden hover:shadow-md transition-shadow"
      >
        <div class="p-6">
          <div class="flex justify-between items-start mb-3">
            <h2 class="text-xl font-bold text-primary">{{ portfolio.title || 'Портфолио' }}</h2>
            <span v-if="portfolio.is_public" class="text-xs px-2 py-1 bg-success/10 text-success rounded">
              Публичное
            </span>
            <span v-else class="text-xs px-2 py-1 bg-secondary-gray/10 text-secondary-gray rounded">
              Приватное
            </span>
          </div>
          
          <p v-if="portfolio.user" class="text-sm mb-4">
            Студент: {{ portfolio.user.first_name || '' }} {{ portfolio.user.last_name || portfolio.user.username || 'Студент' }}
          </p>
          <p v-else class="text-sm mb-4">Студент: Неизвестно</p>
          
          <div class="text-xs text-secondary-gray mb-4">
            Обновлено: {{ formatDate(portfolio.updated_at) }}
          </div>
          
          <!-- Показываем иконку темы, если она есть -->
          <div v-if="portfolio.theme" class="mb-4 text-xs">
            <span class="mr-1">Тема:</span>
            <span class="inline-flex items-center">
              {{ availableThemes.find(t => t.id === portfolio.theme)?.name || 'Стандартная' }}
              <span class="ml-1">{{ availableThemes.find(t => t.id === portfolio.theme)?.icon || '🎨' }}</span>
            </span>
          </div>
          
          <RouterLink
            :to="`/portfolio/${portfolio.id}`"
            class="btn btn-primary w-full"
          >
            Просмотреть
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template> 