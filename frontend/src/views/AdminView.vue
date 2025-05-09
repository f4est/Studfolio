<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import api from '@/api'

const router = useRouter()
const authStore = useAuthStore()

// Проверяем, имеет ли пользователь права администратора или преподавателя
const isAuthorized = computed(() => {
  return authStore.isAdmin || authStore.isTeacher
})

// Если пользователь не имеет прав, перенаправляем на главную
if (!isAuthorized.value) {
  router.push('/')
}

// Состояние данных
const users = ref([])
const portfolios = ref([])
const activeTab = ref('users')
const loading = ref(false)
const error = ref(null)
const userToEdit = ref(null)
const showEditModal = ref(false)

// Информационное сообщение
const message = ref('')
const messageType = ref('success') // success, error, warning

// Загрузка данных
onMounted(async () => {
  if (isAuthorized.value) {
    await fetchUsers()
    await fetchPortfolios()
  }
})

// Получение списка пользователей
const fetchUsers = async () => {
  try {
    loading.value = true
    error.value = null
    
    const response = await api.get('/users/')
    users.value = response.data.results || response.data
  } catch (err) {
    console.error('Error fetching users:', err)
    error.value = 'Не удалось загрузить список пользователей'
  } finally {
    loading.value = false
  }
}

// Получение списка портфолио
const fetchPortfolios = async () => {
  try {
    loading.value = true
    error.value = null
    
    const response = await api.get('/portfolio/portfolios/')
    portfolios.value = response.data.results || response.data
  } catch (err) {
    console.error('Error fetching portfolios:', err)
    error.value = 'Не удалось загрузить список портфолио'
  } finally {
    loading.value = false
  }
}

// Открытие модального окна для редактирования пользователя
const editUser = (user) => {
  userToEdit.value = { ...user }
  showEditModal.value = true
}

// Сохранение изменений пользователя
const saveUser = async () => {
  try {
    loading.value = true
    error.value = null
    
    await api.put(`/users/${userToEdit.value.id}/`, userToEdit.value)
    
    // Обновляем список пользователей
    await fetchUsers()
    
    // Закрываем модальное окно
    showEditModal.value = false
    
    // Показываем сообщение об успехе
    message.value = 'Пользователь успешно обновлен'
    messageType.value = 'success'
    
    // Скрываем сообщение через 3 секунды
    setTimeout(() => {
      message.value = ''
    }, 3000)
  } catch (err) {
    console.error('Error updating user:', err)
    error.value = 'Не удалось обновить пользователя'
  } finally {
    loading.value = false
  }
}

// Удаление пользователя
const deleteUser = async (userId) => {
  if (!confirm('Вы уверены, что хотите удалить этого пользователя?')) return
  
  try {
    loading.value = true
    error.value = null
    
    await api.delete(`/users/${userId}/`)
    
    // Обновляем список пользователей
    await fetchUsers()
    
    // Показываем сообщение об успехе
    message.value = 'Пользователь успешно удален'
    messageType.value = 'success'
    
    // Скрываем сообщение через 3 секунды
    setTimeout(() => {
      message.value = ''
    }, 3000)
  } catch (err) {
    console.error('Error deleting user:', err)
    error.value = 'Не удалось удалить пользователя'
  } finally {
    loading.value = false
  }
}

// Удаление портфолио
const deletePortfolio = async (portfolioId) => {
  if (!confirm('Вы уверены, что хотите удалить это портфолио?')) return
  
  try {
    loading.value = true
    error.value = null
    
    await api.delete(`/portfolio/portfolios/${portfolioId}/`)
    
    // Обновляем список портфолио
    await fetchPortfolios()
    
    // Показываем сообщение об успехе
    message.value = 'Портфолио успешно удалено'
    messageType.value = 'success'
    
    // Скрываем сообщение через 3 секунды
    setTimeout(() => {
      message.value = ''
    }, 3000)
  } catch (err) {
    console.error('Error deleting portfolio:', err)
    error.value = 'Не удалось удалить портфолио'
  } finally {
    loading.value = false
  }
}

// Форматирование даты
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU')
}
</script>

<template>
  <div>
    <div v-if="!isAuthorized" class="text-center py-12">
      <p class="text-error">У вас нет доступа к этой странице.</p>
      <button @click="router.push('/')" class="btn btn-primary mt-4">
        Вернуться на главную
      </button>
    </div>
    
    <div v-else>
      <h1 class="text-2xl font-bold mb-6">Панель администратора</h1>
      
      <!-- Вкладки -->
      <div class="mb-6 border-b border-secondary-gray/30">
        <div class="flex">
          <button 
            @click="activeTab = 'users'" 
            class="px-4 py-2 font-medium"
            :class="activeTab === 'users' ? 'text-primary border-b-2 border-primary' : 'text-secondary-gray'"
          >
            Пользователи
          </button>
          
          <button 
            @click="activeTab = 'portfolios'" 
            class="px-4 py-2 font-medium"
            :class="activeTab === 'portfolios' ? 'text-primary border-b-2 border-primary' : 'text-secondary-gray'"
          >
            Портфолио
          </button>
        </div>
      </div>
      
      <!-- Информационное сообщение -->
      <div v-if="message" class="mb-4 p-3 rounded" :class="{
        'bg-success/10 border border-success text-success': messageType === 'success',
        'bg-error/10 border border-error text-error': messageType === 'error',
        'bg-warning/10 border border-warning text-warning': messageType === 'warning'
      }">
        {{ message }}
      </div>
      
      <!-- Ошибка -->
      <div v-if="error" class="mb-4 p-3 bg-error/10 border border-error text-error rounded">
        {{ error }}
      </div>
      
      <!-- Загрузка данных -->
      <div v-if="loading" class="text-center py-8">
        <p class="text-secondary-gray">Загрузка данных...</p>
      </div>
      
      <!-- Вкладка "Пользователи" -->
      <div v-else-if="activeTab === 'users'" class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Имя пользователя</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Имя</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Роль</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Действия</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="user in users" :key="user.id">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ user.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ user.username }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ user.email }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ user.first_name }} {{ user.last_name }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                  :class="{
                    'bg-green-100 text-green-800': user.role === 'admin',
                    'bg-blue-100 text-blue-800': user.role === 'teacher',
                    'bg-gray-100 text-gray-800': user.role === 'student'
                  }"
                >
                  {{ user.role === 'admin' ? 'Администратор' : 
                     user.role === 'teacher' ? 'Преподаватель' : 'Студент' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <button 
                  @click="editUser(user)" 
                  class="text-primary hover:underline mr-2"
                >
                  Редактировать
                </button>
                <button 
                  @click="deleteUser(user.id)" 
                  class="text-error hover:underline"
                  :disabled="user.id === authStore.user?.id"
                >
                  Удалить
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Вкладка "Портфолио" -->
      <div v-else-if="activeTab === 'portfolios'" class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Заголовок</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Пользователь</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Статус</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Обновлено</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Действия</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="portfolio in portfolios" :key="portfolio.id">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ portfolio.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ portfolio.title }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ portfolio.user ? (portfolio.user.username || '') : '' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                  :class="{
                    'bg-green-100 text-green-800': portfolio.is_public,
                    'bg-gray-100 text-gray-800': !portfolio.is_public
                  }"
                >
                  {{ portfolio.is_public ? 'Публичное' : 'Приватное' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(portfolio.updated_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <button 
                  @click="router.push(`/portfolio/${portfolio.id}`)" 
                  class="text-primary hover:underline mr-2"
                >
                  Просмотр
                </button>
                <button 
                  @click="deletePortfolio(portfolio.id)" 
                  class="text-error hover:underline"
                >
                  Удалить
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Модальное окно для редактирования пользователя -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">Редактирование пользователя</h2>
        
        <div class="mb-4">
          <label class="form-label">Имя пользователя</label>
          <input v-model="userToEdit.username" type="text" class="form-input" />
        </div>
        
        <div class="mb-4">
          <label class="form-label">Email</label>
          <input v-model="userToEdit.email" type="email" class="form-input" />
        </div>
        
        <div class="mb-4">
          <label class="form-label">Имя</label>
          <input v-model="userToEdit.first_name" type="text" class="form-input" />
        </div>
        
        <div class="mb-4">
          <label class="form-label">Фамилия</label>
          <input v-model="userToEdit.last_name" type="text" class="form-input" />
        </div>
        
        <div class="mb-4">
          <label class="form-label">Роль</label>
          <select v-model="userToEdit.role" class="form-input">
            <option value="student">Студент</option>
            <option value="teacher">Преподаватель</option>
            <option value="admin">Администратор</option>
          </select>
        </div>
        
        <div class="flex justify-end space-x-2">
          <button @click="showEditModal = false" class="btn btn-secondary">
            Отмена
          </button>
          <button @click="saveUser" class="btn btn-primary" :disabled="loading">
            Сохранить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.form-label {
  @apply block text-sm font-medium text-gray-700 mb-1;
}

.form-input {
  @apply mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50;
}
</style>