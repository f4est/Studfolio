<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const portfolio = ref(null)
const loading = ref(true)
const error = ref(null)
const activeTab = ref('about')
const editMode = ref(false)
const isChangingVisibility = ref(false)

// Настройки темы и стиля портфолио
const portfolioTheme = ref('default') // default, dark, creative, minimal, corporate
const showThemeSelector = ref(false)

// Список доступных тем
const availableThemes = [
  { id: 'default', name: 'Стандартная', icon: '🎨' },
  { id: 'dark', name: 'Темная', icon: '🌙' },
  { id: 'creative', name: 'Креативная', icon: '✨' },
  { id: 'minimal', name: 'Минималистичная', icon: '⚪' },
  { id: 'corporate', name: 'Корпоративная', icon: '💼' }
]

// Форма для редактирования раздела "Обо мне"
const aboutForm = ref({
  content: '',
  photo: null
})

// Данные для образования, навыков, проектов и сертификатов
const educations = ref([])
const skills = ref([])
const projects = ref([])
const certificates = ref([])

// Формы для образования
const educationForm = ref({
  id: null,
  institution: '',
  degree: '',
  start_date: '',
  end_date: '',
  description: '',
  is_current: false
})

// Форма для навыков
const skillForm = ref({
  id: null,
  name: '',
  level: 3,
  category: ''
})

// Форма для проектов
const projectForm = ref({
  id: null,
  title: '',
  description: '',
  url: '',
  github_url: '',
  start_date: '',
  end_date: '',
  is_ongoing: false
})

// Форма для сертификатов
const certificateForm = ref({
  id: null,
  title: '',
  issuer: '',
  issue_date: '',
  expiration_date: '',
  description: '',
  credential_id: '',
  credential_url: '',
  file: null
})

// Форма для отзывов
const commentForm = ref({
  text: '',
  rating: 5,
  section: 'general'
})

// Список отзывов/комментариев
const comments = ref([])

// Ссылка на input file для загрузки файла сертификата
const certificateFileInput = ref(null)

// Флаги для отображения форм
const showEducationForm = ref(false)
const showSkillForm = ref(false)
const showProjectForm = ref(false)
const showCertificateForm = ref(false)
const showCommentForm = ref(false)

// Флаг для индикатора экспорта
const isExporting = ref(false)
const exportMessage = ref('')

// Вычисляемые стили в зависимости от выбранной темы
const themeStyles = computed(() => {
  switch (portfolioTheme.value) {
    case 'dark':
      return {
        mainBg: 'bg-gray-900',
        cardBg: 'bg-gray-800',
        textPrimary: 'text-white',
        textSecondary: 'text-gray-300',
        borderColor: 'border-gray-700',
        tabActive: 'border-blue-500 text-blue-500',
        tabInactive: 'text-gray-400 hover:text-gray-300',
        primary: 'bg-blue-600 hover:bg-blue-700 text-white',
        secondary: 'bg-gray-700 hover:bg-gray-600 text-white'
      }
    case 'creative':
      return {
        mainBg: 'bg-gradient-to-r from-purple-50 to-pink-50',
        cardBg: 'bg-white',
        textPrimary: 'text-purple-800',
        textSecondary: 'text-purple-600',
        borderColor: 'border-pink-200',
        tabActive: 'border-pink-500 text-pink-600',
        tabInactive: 'text-purple-500 hover:text-purple-700',
        primary: 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white',
        secondary: 'bg-white hover:bg-gray-100 text-pink-600 border border-pink-300'
      }
    case 'minimal':
      return {
        mainBg: 'bg-white',
        cardBg: 'bg-white',
        textPrimary: 'text-gray-900',
        textSecondary: 'text-gray-600',
        borderColor: 'border-gray-200',
        tabActive: 'border-gray-900 text-gray-900',
        tabInactive: 'text-gray-500 hover:text-gray-700',
        primary: 'bg-gray-900 hover:bg-gray-800 text-white',
        secondary: 'bg-white hover:bg-gray-100 text-gray-800 border border-gray-300'
      }
    case 'corporate':
      return {
        mainBg: 'bg-slate-50',
        cardBg: 'bg-white',
        textPrimary: 'text-slate-900',
        textSecondary: 'text-slate-600',
        borderColor: 'border-slate-200',
        tabActive: 'border-blue-700 text-blue-700',
        tabInactive: 'text-slate-600 hover:text-slate-800',
        primary: 'bg-blue-700 hover:bg-blue-800 text-white',
        secondary: 'bg-slate-200 hover:bg-slate-300 text-slate-800'
      }
    default:
      return {
        mainBg: 'bg-gray-100',
        cardBg: 'bg-white',
        textPrimary: 'text-primary',
        textSecondary: 'text-secondary-gray',
        borderColor: 'border-secondary-gray/30',
        tabActive: 'border-primary text-primary',
        tabInactive: 'text-secondary-gray hover:text-primary',
        primary: 'bg-primary hover:bg-primary/90 text-white',
        secondary: 'bg-secondary-gray/20 hover:bg-secondary-gray/30 text-gray-700'
      }
  }
})

// Сохранение выбранной темы
const saveTheme = async () => {
  try {
    if (!portfolio.value || !portfolio.value.id) return
    
    // В реальном приложении здесь нужно сохранять тему на сервере
    // Например, через API:
    // await api.patch(`/portfolio/portfolios/${portfolio.value.id}/`, {
    //   theme: portfolioTheme.value
    // })
    
    showThemeSelector.value = false
  } catch (err) {
    console.error('Error saving theme:', err)
    error.value = 'Не удалось сохранить тему портфолио.'
  }
}

// Получение портфолио
onMounted(async () => {
  try {
    const portfolioId = route.params.id
    const response = await api.get(`/portfolio/portfolios/${portfolioId}/`)
    
    portfolio.value = response.data
    console.log('Portfolio loaded:', portfolio.value)
    
    // Если у портфолио есть сохраненная тема, используем её
    if (portfolio.value.theme) {
      portfolioTheme.value = portfolio.value.theme
    }
    
    // Инициализация формы "Обо мне", если есть данные
    if (portfolio.value && portfolio.value.about) {
      aboutForm.value.content = portfolio.value.about.content || ''
    }
    
    // Загрузка данных образования, навыков, проектов и сертификатов
    await loadEducation()
    await loadSkills()
    await loadProjects()
    await loadCertificates()
    await loadComments()
    
  } catch (err) {
    console.error('Error fetching portfolio:', err)
    error.value = 'Не удалось загрузить портфолио. Пожалуйста, попробуйте позже.'
    
    // Перенаправляем на страницу со списком при ошибке 404
    if (err.response && err.response.status === 404) {
      setTimeout(() => {
        router.push('/portfolios')
      }, 2000)
    }
  } finally {
    loading.value = false
  }
})

// Загрузка данных об образовании
const loadEducation = async () => {
  try {
    const response = await api.get('/portfolio/education/')
    educations.value = response.data
  } catch (err) {
    console.error('Error fetching education:', err)
  }
}

// Загрузка навыков
const loadSkills = async () => {
  try {
    const response = await api.get('/portfolio/skills/')
    skills.value = response.data
  } catch (err) {
    console.error('Error fetching skills:', err)
  }
}

// Загрузка проектов
const loadProjects = async () => {
  try {
    const response = await api.get('/portfolio/projects/')
    projects.value = response.data
  } catch (err) {
    console.error('Error fetching projects:', err)
  }
}

// Загрузка сертификатов
const loadCertificates = async () => {
  try {
    const response = await api.get('/portfolio/certificates/')
    certificates.value = response.data
  } catch (err) {
    console.error('Error fetching certificates:', err)
  }
}

// Загрузка комментариев
const loadComments = async () => {
  try {
    const portfolioId = route.params.id
    const response = await api.get(`/portfolio/comments/?portfolio=${portfolioId}`)
    comments.value = response.data
  } catch (err) {
    console.error('Error fetching comments:', err)
  }
}

// Вычисляемое свойство для проверки, является ли текущий пользователь владельцем портфолио
const isOwner = computed(() => {
  if (!portfolio.value || !authStore.user || !portfolio.value.user) return false
  return portfolio.value.user.id === authStore.user.id
})

// Вычисляемое свойство для проверки, может ли пользователь редактировать портфолио
const canEdit = computed(() => {
  return isOwner.value || authStore.isAdmin || authStore.isTeacher
})

// Метод для сохранения раздела "Обо мне"
const saveAboutSection = async () => {
  try {
    loading.value = true
    
    if (portfolio.value.about) {
      // Обновление существующего раздела
      await api.put(`/portfolio/about/${portfolio.value.about.id}/`, {
        content: aboutForm.value.content
      })
    } else {
      // Создание нового раздела
      await api.post('/portfolio/about/', {
        content: aboutForm.value.content
      })
    }
    
    // Обновление данных в портфолио
    const portfolioId = route.params.id
    const response = await api.get(`/portfolio/portfolios/${portfolioId}/`)
    portfolio.value = response.data
    
    editMode.value = false
  } catch (err) {
    console.error('Error saving about section:', err)
    error.value = 'Не удалось сохранить раздел "Обо мне". Пожалуйста, попробуйте позже.'
  } finally {
    loading.value = false
  }
}

// Методы для работы с образованием
const openEducationForm = (education = null) => {
  if (education) {
    // Редактирование существующего образования
    educationForm.value = { ...education }
    // Преобразование дат в формат гггг-мм-дд для input type="date"
    educationForm.value.start_date = formatDateForInput(education.start_date)
    educationForm.value.end_date = formatDateForInput(education.end_date)
  } else {
    // Создание нового образования
    educationForm.value = {
      id: null,
      institution: '',
      degree: '',
      start_date: '',
      end_date: '',
      description: '',
      is_current: false
    }
  }
  showEducationForm.value = true
}

const closeEducationForm = () => {
  showEducationForm.value = false
  educationForm.value = {
    id: null,
    institution: '',
    degree: '',
    start_date: '',
    end_date: '',
    description: '',
    is_current: false
  }
}

const saveEducation = async () => {
  try {
    loading.value = true
    
    // Подготовка данных для отправки
    const educationData = { ...educationForm.value }
    
    // Проверяем наличие обязательных полей
    if (!educationData.institution || !educationData.degree || !educationData.start_date) {
      error.value = 'Пожалуйста, заполните название учебного заведения, специальность и дату начала обучения'
      loading.value = false
      return
    }
    
    // Форматируем даты для корректной передачи на сервер
    try {
      if (typeof educationData.start_date === 'string') {
        const startDate = new Date(educationData.start_date)
        educationData.start_date = startDate.toISOString().split('T')[0]
      }
      
      if (educationData.end_date && typeof educationData.end_date === 'string') {
        const endDate = new Date(educationData.end_date)
        educationData.end_date = endDate.toISOString().split('T')[0]
      }
    } catch (dateErr) {
      console.error('Error formatting dates:', dateErr)
      error.value = 'Неверный формат даты. Пожалуйста, проверьте даты.'
      loading.value = false
      return
    }
    
    // Если текущее место учебы, то конечная дата не нужна
    if (educationData.is_current) {
      educationData.end_date = null
    } else if (!educationData.end_date) {
      // Если не текущее место учебы, но конечная дата не указана
      error.value = 'Пожалуйста, укажите дату окончания или отметьте как текущее место учебы'
      loading.value = false
      return
    }
    
    console.log('Sending education data:', educationData)
    
    if (educationData.id) {
      // Обновление существующего
      await api.put(`/portfolio/education/${educationData.id}/`, educationData)
    } else {
      // Создание нового
      await api.post('/portfolio/education/', educationData)
    }
    
    // Обновление списка образования
    await loadEducation()
    
    // Закрытие формы
    closeEducationForm()
    error.value = null
  } catch (err) {
    console.error('Error saving education:', err)
    if (err.response && err.response.data) {
      // Вывод ошибки валидации с сервера
      const errorMessages = Object.values(err.response.data).flat().join(', ')
      error.value = `Не удалось сохранить информацию об образовании: ${errorMessages}`
    } else {
      error.value = 'Не удалось сохранить информацию об образовании. Проверьте правильность заполнения полей.'
    }
  } finally {
    loading.value = false
  }
}

const deleteEducation = async (id) => {
  if (!confirm('Вы уверены, что хотите удалить эту запись об образовании?')) return
  
  try {
    loading.value = true
    await api.delete(`/portfolio/education/${id}/`)
    await loadEducation()
  } catch (err) {
    console.error('Error deleting education:', err)
    error.value = 'Не удалось удалить информацию об образовании. Пожалуйста, попробуйте позже.'
  } finally {
    loading.value = false
  }
}

// Метод для экспорта портфолио в PDF
const exportPdf = async () => {
  if (!portfolio.value || !portfolio.value.id) return
  
  try {
    isExporting.value = true
    exportMessage.value = 'Генерация PDF...'
    
    const portfolioId = portfolio.value.id
    const url = `/api/portfolio/portfolios/${portfolioId}/export_pdf/`
    
    // Открываем новое окно для загрузки PDF
    const downloadWindow = window.open(url, '_blank')
    
    // Если браузер блокирует новое окно, показываем сообщение
    if (!downloadWindow || downloadWindow.closed || typeof downloadWindow.closed === 'undefined') {
      exportMessage.value = 'Файл готов к загрузке, но браузер заблокировал открытие нового окна'
    } else {
      exportMessage.value = 'PDF успешно сгенерирован!'
      
      // Скрываем сообщение через 3 секунды
      setTimeout(() => {
        exportMessage.value = ''
      }, 3000)
    }
  } catch (err) {
    console.error('Error exporting PDF:', err)
    exportMessage.value = 'Не удалось сгенерировать PDF. Пожалуйста, попробуйте позже.'
  } finally {
    isExporting.value = false
  }
}

// Форматирование даты
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU')
}

// Форматирование даты для полей ввода
const formatDateForInput = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toISOString().split('T')[0]
}

// Методы для работы с навыками
const openSkillForm = (skill = null) => {
  if (skill) {
    // Редактирование существующего навыка
    skillForm.value = { ...skill }
  } else {
    // Создание нового навыка
    skillForm.value = {
      id: null,
      name: '',
      level: 3,
      category: ''
    }
  }
  showSkillForm.value = true
}

const closeSkillForm = () => {
  showSkillForm.value = false
  skillForm.value = {
    id: null,
    name: '',
    level: 3,
    category: ''
  }
}

const saveSkill = async () => {
  try {
    loading.value = true
    
    // Проверяем наличие обязательных полей
    if (!skillForm.value.name) {
      error.value = 'Пожалуйста, заполните название навыка'
      loading.value = false
      return
    }
    
    // Создаем копию данных формы
    const skillData = { ...skillForm.value }
    
    // Убедимся, что уровень в пределах от 1 до 5 и это число
    skillData.level = Math.max(1, Math.min(5, parseInt(skillData.level) || 3))
    
    // Если категория не указана, используем "Общие"
    if (!skillData.category || skillData.category.trim() === '') {
      skillData.category = 'Общие'
    }
    
    console.log('Sending skill data:', skillData)
    
    if (skillData.id) {
      // Обновление существующего
      await api.put(`/portfolio/skills/${skillData.id}/`, skillData)
    } else {
      // Создание нового
      await api.post('/portfolio/skills/', skillData)
    }
    
    // Обновление списка навыков
    await loadSkills()
    
    // Закрытие формы
    closeSkillForm()
    error.value = null
  } catch (err) {
    console.error('Error saving skill:', err)
    if (err.response && err.response.data) {
      // Вывод ошибки валидации с сервера
      const errorMessages = Object.values(err.response.data).flat().join(', ')
      error.value = `Не удалось сохранить навык: ${errorMessages}`
    } else {
      error.value = 'Не удалось сохранить навык. Проверьте правильность заполнения полей.'
    }
  } finally {
    loading.value = false
  }
}

const deleteSkill = async (id) => {
  if (!confirm('Вы уверены, что хотите удалить этот навык?')) return
  
  try {
    loading.value = true
    await api.delete(`/portfolio/skills/${id}/`)
    await loadSkills()
  } catch (err) {
    console.error('Error deleting skill:', err)
    error.value = 'Не удалось удалить навык. Пожалуйста, попробуйте позже.'
  } finally {
    loading.value = false
  }
}

// Группировка навыков по категориям
const groupedSkills = computed(() => {
  const groups = {}
  
  skills.value.forEach(skill => {
    const category = skill.category || 'Общие'
    if (!groups[category]) {
      groups[category] = []
    }
    groups[category].push(skill)
  })
  
  return groups
})

// Методы для работы с проектами
const openProjectForm = (project = null) => {
  if (project) {
    // Редактирование существующего проекта
    projectForm.value = { ...project }
    // Преобразование дат в формат гггг-мм-дд для input type="date"
    projectForm.value.start_date = formatDateForInput(project.start_date)
    projectForm.value.end_date = formatDateForInput(project.end_date)
  } else {
    // Создание нового проекта
    projectForm.value = {
      id: null,
      title: '',
      description: '',
      url: '',
      github_url: '',
      start_date: '',
      end_date: '',
      is_ongoing: false
    }
  }
  showProjectForm.value = true
}

const closeProjectForm = () => {
  showProjectForm.value = false
  projectForm.value = {
    id: null,
    title: '',
    description: '',
    url: '',
    github_url: '',
    start_date: '',
    end_date: '',
    is_ongoing: false
  }
}

const saveProject = async () => {
  try {
    loading.value = true
    
    // Подготовка данных для отправки
    const projectData = { ...projectForm.value }
    
    // Проверяем обязательные поля
    if (!projectData.title || !projectData.description || !projectData.start_date) {
      error.value = 'Пожалуйста, заполните название, описание и дату начала проекта'
      loading.value = false
      return
    }
    
    // Обработка дат для корректной передачи на сервер
    // Если проект продолжается, то конечная дата не нужна
    if (projectData.is_ongoing) {
      projectData.end_date = null
    } else if (!projectData.end_date) {
      // Если проект не продолжается, но конечная дата не указана
      error.value = 'Пожалуйста, укажите дату завершения проекта или отметьте, что проект в процессе'
      loading.value = false
      return
    }
    
    // Проверяем формат дат
    try {
      if (typeof projectData.start_date === 'string') {
        const startDate = new Date(projectData.start_date)
        projectData.start_date = startDate.toISOString().split('T')[0]
      }
      
      if (projectData.end_date && typeof projectData.end_date === 'string') {
        const endDate = new Date(projectData.end_date)
        projectData.end_date = endDate.toISOString().split('T')[0]
      }
    } catch (dateErr) {
      console.error('Error formatting dates:', dateErr)
      error.value = 'Неверный формат даты. Пожалуйста, проверьте даты.'
      loading.value = false
      return
    }
    
    console.log('Sending project data:', projectData)
    
    if (projectData.id) {
      // Обновление существующего
      await api.put(`/portfolio/projects/${projectData.id}/`, projectData)
    } else {
      // Создание нового
      await api.post('/portfolio/projects/', projectData)
    }
    
    // Обновление списка проектов
    await loadProjects()
    
    // Закрытие формы
    closeProjectForm()
    error.value = null
  } catch (err) {
    console.error('Error saving project:', err)
    if (err.response && err.response.data) {
      // Вывод ошибки валидации с сервера
      const errorMessages = Object.values(err.response.data).flat().join(', ')
      error.value = `Не удалось сохранить проект: ${errorMessages}`
    } else {
      error.value = 'Не удалось сохранить проект. Пожалуйста, проверьте правильность заполнения всех полей.'
    }
  } finally {
    loading.value = false
  }
}

const deleteProject = async (id) => {
  if (!confirm('Вы уверены, что хотите удалить этот проект?')) return
  
  try {
    loading.value = true
    await api.delete(`/portfolio/projects/${id}/`)
    await loadProjects()
  } catch (err) {
    console.error('Error deleting project:', err)
    error.value = 'Не удалось удалить проект. Пожалуйста, попробуйте позже.'
  } finally {
    loading.value = false
  }
}

// Методы для работы с сертификатами
const openCertificateForm = (certificate = null) => {
  if (certificate) {
    // Редактирование существующего сертификата
    certificateForm.value = { ...certificate }
    // Преобразование дат в формат гггг-мм-дд для input type="date"
    certificateForm.value.issue_date = formatDateForInput(certificate.issue_date)
    certificateForm.value.expiration_date = formatDateForInput(certificate.expiration_date)
    // Файл не передается через API, поэтому очищаем его
    certificateForm.value.file = null
  } else {
    // Создание нового сертификата
    certificateForm.value = {
      id: null,
      title: '',
      issuer: '',
      issue_date: '',
      expiration_date: '',
      description: '',
      credential_id: '',
      credential_url: '',
      file: null
    }
  }
  showCertificateForm.value = true
}

const closeCertificateForm = () => {
  showCertificateForm.value = false
  certificateForm.value = {
    id: null,
    title: '',
    issuer: '',
    issue_date: '',
    expiration_date: '',
    description: '',
    credential_id: '',
    credential_url: '',
    file: null
  }
}

// Обработчик выбора файла сертификата
const handleCertificateFileChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    certificateForm.value.file = file
  }
}

const saveCertificate = async () => {
  try {
    loading.value = true
    
    // Проверяем наличие обязательных полей
    if (!certificateForm.value.title || !certificateForm.value.issuer || !certificateForm.value.issue_date) {
      error.value = 'Пожалуйста, заполните название, кем выдан и дату выдачи сертификата'
      loading.value = false
      return
    }
    
    // Создаем FormData для отправки файлов
    const formData = new FormData()
    
    // Форматируем даты
    try {
      let issueDate = certificateForm.value.issue_date
      if (typeof issueDate === 'string') {
        const date = new Date(issueDate)
        issueDate = date.toISOString().split('T')[0]
      }
      formData.append('issue_date', issueDate)
      
      if (certificateForm.value.expiration_date) {
        let expirationDate = certificateForm.value.expiration_date
        if (typeof expirationDate === 'string') {
          const date = new Date(expirationDate)
          expirationDate = date.toISOString().split('T')[0]
        }
        formData.append('expiration_date', expirationDate)
      }
    } catch (dateErr) {
      console.error('Error formatting dates:', dateErr)
      error.value = 'Неверный формат даты. Пожалуйста, проверьте даты.'
      loading.value = false
      return
    }
    
    // Добавляем все остальные поля формы в FormData
    formData.append('title', certificateForm.value.title)
    formData.append('issuer', certificateForm.value.issuer)
    
    if (certificateForm.value.description) {
      formData.append('description', certificateForm.value.description)
    }
    
    if (certificateForm.value.credential_id) {
      formData.append('credential_id', certificateForm.value.credential_id)
    }
    
    if (certificateForm.value.credential_url) {
      formData.append('credential_url', certificateForm.value.credential_url)
    }
    
    // Добавляем ID для редактирования
    if (certificateForm.value.id) {
      formData.append('id', certificateForm.value.id)
    }
    
    // Добавляем файл, если он выбран
    if (certificateForm.value.file) {
      formData.append('file', certificateForm.value.file)
    }
    
    console.log('Sending certificate data with fields:', Object.fromEntries(formData.entries()))
    
    if (certificateForm.value.id) {
      // Обновление существующего
      await api.put(`/portfolio/certificates/${certificateForm.value.id}/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    } else {
      // Создание нового
      await api.post('/portfolio/certificates/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    }
    
    // Обновление списка сертификатов
    await loadCertificates()
    
    // Закрытие формы
    closeCertificateForm()
    error.value = null
  } catch (err) {
    console.error('Error saving certificate:', err)
    if (err.response && err.response.data) {
      // Вывод ошибки валидации с сервера
      const errorMessages = Object.values(err.response.data).flat().join(', ')
      error.value = `Не удалось сохранить сертификат: ${errorMessages}`
    } else {
      error.value = 'Не удалось сохранить сертификат. Проверьте правильность заполнения полей.'
    }
  } finally {
    loading.value = false
  }
}

const deleteCertificate = async (id) => {
  if (!confirm('Вы уверены, что хотите удалить этот сертификат?')) return
  
  try {
    loading.value = true
    await api.delete(`/portfolio/certificates/${id}/`)
    await loadCertificates()
  } catch (err) {
    console.error('Error deleting certificate:', err)
    error.value = 'Не удалось удалить сертификат. Пожалуйста, попробуйте позже.'
  } finally {
    loading.value = false
  }
}

// Метод для изменения публичности портфолио
const togglePortfolioVisibility = async () => {
  if (!portfolio.value || !portfolio.value.id) return
  
  try {
    isChangingVisibility.value = true
    
    // Изменяем значение на противоположное
    const newValue = !portfolio.value.is_public
    
    // Отправляем запрос на обновление
    await api.patch(`/portfolio/portfolios/${portfolio.value.id}/`, {
      is_public: newValue
    })
    
    // Обновляем локальное значение
    portfolio.value.is_public = newValue
    
    // Показываем сообщение об успехе
    error.value = `Портфолио теперь ${newValue ? 'публичное' : 'приватное'}`
    
    // Через 3 секунды убираем сообщение
    setTimeout(() => {
      if (error.value === `Портфолио теперь ${newValue ? 'публичное' : 'приватное'}`) {
    error.value = null
  } catch (err) {
    console.error('Error updating portfolio visibility:', err)
    error.value = 'Не удалось изменить публичность портфолио. Пожалуйста, попробуйте позже.'
  } finally {
    isChangingVisibility.value = false
  }
}

// Добавление/редактирование комментария
const saveComment = async () => {
  try {
    loading.value = true
    
    if (!commentForm.value.text || !commentForm.value.rating) {
      error.value = 'Пожалуйста, добавьте текст отзыва и оценку'
      loading.value = false
      return
    }
    
    // Убедимся, что рейтинг в допустимых пределах
    commentForm.value.rating = Math.max(1, Math.min(5, parseInt(commentForm.value.rating) || 5))
    
    // Создаем объект данных для отправки
    const commentData = {
      ...commentForm.value,
      portfolio: portfolio.value.id
    }
    
    console.log('Sending comment data:', commentData)
    
    // Отправляем запрос
    await api.post('/portfolio/comments/', commentData)
    
    // Обновляем список комментариев
    await loadComments()
    
    // Сбрасываем форму
    commentForm.value = {
      text: '',
      rating: 5,
      section: 'general'
    }
    
    showCommentForm.value = false
    error.value = null
  } catch (err) {
    console.error('Error saving comment:', err)
    error.value = 'Не удалось сохранить отзыв. Пожалуйста, попробуйте позже.'
  } finally {
    loading.value = false
  }
}

// Форматирование даты для комментариев
const formatDateTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('ru-RU')
}

// Расчет среднего рейтинга
const averageRating = computed(() => {
  if (!comments.value.length) return 0
  
  const sum = comments.value.reduce((acc, comment) => {
    return acc + (comment.rating || 0)
  }, 0)
  
  return (sum / comments.value.length).toFixed(1)
})

// Удаление комментария
const deleteComment = async (id) => {
  if (!confirm('Вы уверены, что хотите удалить этот отзыв?')) return
  
  try {
    loading.value = true
    await api.delete(`/portfolio/comments/${id}/`)
    
    // Обновляем список комментариев
    await loadComments()
    
    error.value = null
  } catch (err) {
    console.error('Error deleting comment:', err)
    error.value = 'Не удалось удалить отзыв. Пожалуйста, попробуйте позже.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div :class="[themeStyles.mainBg, 'min-h-screen']">
    <div v-if="loading" class="text-center py-12">
      <p class="text-secondary-gray">Загрузка портфолио...</p>
    </div>
    
    <div v-else-if="error" class="container mx-auto px-4 py-8">
      <div class="p-4 bg-error/10 border border-error text-error rounded">
        {{ error }}
      </div>
    </div>
    
    <div v-else-if="portfolio" class="container mx-auto px-4 py-8">
      <!-- Шапка портфолио -->
      <div :class="[themeStyles.cardBg, 'p-6 rounded-lg shadow mb-6']">
        <div class="flex flex-col md:flex-row md:justify-between md:items-center">
          <div>
            <h1 :class="[themeStyles.textPrimary, 'text-2xl font-bold mb-2']">{{ portfolio.title || 'Портфолио' }}</h1>
            <p v-if="portfolio.user" :class="[themeStyles.textSecondary]">
              {{ portfolio.user.first_name || '' }} {{ portfolio.user.last_name || portfolio.user.username || 'Студент' }}
            </p>
            <p v-else :class="[themeStyles.textSecondary]">Студент: Неизвестно</p>
            
            <!-- Индикатор публичности портфолио -->
            <div class="mt-2 flex items-center">
              <span 
                class="px-2 py-1 text-xs rounded-full"
                :class="portfolio.is_public ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'"
              >
                {{ portfolio.is_public ? 'Публичное' : 'Приватное' }}
              </span>
              
              <button 
                v-if="canEdit"
                @click="togglePortfolioVisibility"
                class="ml-2 text-xs text-primary hover:underline"
                :disabled="isChangingVisibility"
              >
                {{ isChangingVisibility ? 'Изменение...' : 'Изменить' }}
              </button>
            </div>
          </div>
          
          <div class="mt-4 md:mt-0 flex flex-wrap gap-2">
            <button 
              v-if="canEdit" 
              @click="showThemeSelector = !showThemeSelector" 
              class="flex items-center space-x-1 px-3 py-1.5 rounded text-sm"
              :class="[themeStyles.secondary]"
            >
              <span>Тема портфолио</span>
              <span>{{ availableThemes.find(t => t.id === portfolioTheme)?.icon || '🎨' }}</span>
            </button>
            
            <button 
              v-if="canEdit" 
              @click="editMode = !editMode" 
              class="px-3 py-1.5 rounded text-sm"
              :class="[themeStyles.secondary]"
            >
              {{ editMode ? 'Просмотр' : 'Редактировать' }}
            </button>
            
            <button 
              @click="exportPdf" 
              class="flex items-center px-3 py-1.5 rounded text-sm"
              :class="[themeStyles.primary]"
              :disabled="isExporting"
            >
              <span v-if="isExporting">Экспорт...</span>
              <span v-else>Экспорт PDF</span>
            </button>
          </div>
        </div>
        
        <!-- Сообщение о статусе экспорта -->
        <div v-if="exportMessage" class="absolute top-full right-0 mt-2 p-2 rounded shadow-md text-sm"
          :class="exportMessage.includes('успешно') ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'"
        >
          {{ exportMessage }}
        </div>
        
        <!-- Селектор темы -->
        <div v-if="showThemeSelector" class="mt-4 p-3 rounded" :class="[`${themeStyles.borderColor} border`]">
          <h3 :class="[themeStyles.textPrimary, 'text-base font-medium mb-3']">Выберите тему оформления</h3>
          
          <div class="grid grid-cols-2 md:grid-cols-5 gap-2 mb-3">
            <button
              v-for="theme in availableThemes"
              :key="theme.id"
              @click="portfolioTheme = theme.id"
              class="flex flex-col items-center p-2 rounded border transition-all"
              :class="[
                portfolioTheme === theme.id 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-200 hover:border-blue-300'
              ]"
            >
              <span class="text-2xl mb-1">{{ theme.icon }}</span>
              <span class="text-sm">{{ theme.name }}</span>
            </button>
          </div>
          
          <div class="flex justify-end">
            <button 
              @click="saveTheme"
              class="px-3 py-1.5 rounded text-sm"
              :class="[themeStyles.primary]"
            >
              Сохранить тему
            </button>
          </div>
        </div>
      </div>
      
      <!-- Вкладки портфолио -->
      <div :class="[`${themeStyles.borderColor} border-b mb-6`]">
        <div class="flex overflow-x-auto">
          <button 
            @click="activeTab = 'about'" 
            class="px-4 py-2 font-medium"
            :class="[
              activeTab === 'about' 
                ? `${themeStyles.tabActive} border-b-2` 
                : themeStyles.tabInactive
            ]"
          >
            Обо мне
          </button>
          
          <button 
            @click="activeTab = 'education'" 
            class="px-4 py-2 font-medium"
            :class="[
              activeTab === 'education' 
                ? `${themeStyles.tabActive} border-b-2` 
                : themeStyles.tabInactive
            ]"
          >
            Образование
          </button>
          
          <button 
            @click="activeTab = 'skills'" 
            class="px-4 py-2 font-medium"
            :class="[
              activeTab === 'skills' 
                ? `${themeStyles.tabActive} border-b-2` 
                : themeStyles.tabInactive
            ]"
          >
            Навыки
          </button>
          
          <button 
            @click="activeTab = 'projects'" 
            class="px-4 py-2 font-medium"
            :class="[
              activeTab === 'projects' 
                ? `${themeStyles.tabActive} border-b-2` 
                : themeStyles.tabInactive
            ]"
          >
            Проекты
          </button>
          
          <button 
            @click="activeTab = 'certificates'" 
            class="px-4 py-2 font-medium"
            :class="[
              activeTab === 'certificates' 
                ? `${themeStyles.tabActive} border-b-2` 
                : themeStyles.tabInactive
            ]"
          >
            Сертификаты
          </button>
          
          <button 
            @click="activeTab = 'comments'" 
            class="px-4 py-2 font-medium"
            :class="[
              activeTab === 'comments' 
                ? `${themeStyles.tabActive} border-b-2` 
                : themeStyles.tabInactive
            ]"
          >
            Отзывы
          </button>
        </div>
      </div>
      
      <!-- Содержимое вкладки "Обо мне" -->
      <div v-if="activeTab === 'about'" :class="[themeStyles.cardBg, 'p-6 rounded-lg shadow']">
        <div v-if="editMode">
          <form @submit.prevent="saveAboutSection">
            <div class="mb-4">
              <label for="about-content" class="form-label" :class="[themeStyles.textPrimary]">О себе</label>
              <textarea
                id="about-content"
                v-model="aboutForm.content"
                rows="6"
                class="form-input"
                placeholder="Расскажите о себе..."
              ></textarea>
            </div>
            
            <div class="flex justify-end">
              <button 
                type="button" 
                @click="editMode = false" 
                class="mr-2 px-3 py-1.5 rounded text-sm"
                :class="[themeStyles.secondary]"
              >
                Отмена
              </button>
              <button 
                type="submit" 
                class="px-3 py-1.5 rounded text-sm"
                :class="[themeStyles.primary]"
                :disabled="loading"
              >
                Сохранить
              </button>
            </div>
          </form>
        </div>
        
        <div v-else>
          <div v-if="portfolio.about" class="prose">
            <p :class="[themeStyles.textSecondary]">{{ portfolio.about.content }}</p>
          </div>
          
          <div v-else class="text-center py-8">
            <p :class="[themeStyles.textSecondary]" v-if="canEdit">
              Нет информации в разделе "Обо мне". 
              <button 
                @click="editMode = true" 
                class="hover:underline"
                :class="[themeStyles.tabActive]"
              >
                Добавить
              </button>
            </p>
            <p :class="[themeStyles.textSecondary]" v-else>
              Нет информации в разделе "Обо мне".
            </p>
          </div>
        </div>
      </div>
      
      <!-- Вкладка "Образование" -->
      <div v-else-if="activeTab === 'education'" :class="[themeStyles.cardBg, 'p-6 rounded-lg shadow']">
        <!-- Кнопка добавления образования -->
        <div v-if="canEdit && !showEducationForm" class="mb-6 flex justify-end">
          <button 
            @click="openEducationForm()" 
            class="btn btn-primary"
          >
            Добавить образование
          </button>
        </div>
        
        <!-- Форма добавления/редактирования образования -->
        <div v-if="showEducationForm" class="mb-6 bg-secondary-gray/5 p-4 rounded-lg border border-secondary-gray/20">
          <h3 class="text-lg font-semibold mb-4">
            {{ educationForm.id ? 'Редактирование образования' : 'Добавление образования' }}
          </h3>
          
          <form @submit.prevent="saveEducation">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label for="institution" class="form-label" :class="[themeStyles.textPrimary]">Учебное заведение</label>
                <input
                  id="institution"
                  v-model="educationForm.institution"
                  type="text"
                  class="form-input"
                  placeholder="Название учебного заведения"
                  required
                />
              </div>
              
              <div>
                <label for="degree" class="form-label" :class="[themeStyles.textPrimary]">Специальность/Степень</label>
                <input
                  id="degree"
                  v-model="educationForm.degree"
                  type="text"
                  class="form-input"
                  placeholder="Например: Бакалавр информатики"
                  required
                />
              </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label for="start-date" class="form-label" :class="[themeStyles.textPrimary]">Дата начала</label>
                <input
                  id="start-date"
                  v-model="educationForm.start_date"
                  type="date"
                  class="form-input"
                  required
                />
              </div>
              
              <div>
                <label for="end-date" class="form-label" :class="[themeStyles.textPrimary]">Дата окончания</label>
                <input
                  id="end-date"
                  v-model="educationForm.end_date"
                  type="date"
                  class="form-input"
                  :disabled="educationForm.is_current"
                />
                
                <div class="mt-2">
                  <label class="inline-flex items-center">
                    <input 
                      type="checkbox" 
                      v-model="educationForm.is_current"
                      class="form-checkbox"
                    />
                    <span class="ml-2" :class="[themeStyles.textPrimary]">Обучаюсь в настоящее время</span>
                  </label>
                </div>
              </div>
            </div>
            
            <div class="mb-4">
              <label for="description" class="form-label" :class="[themeStyles.textPrimary]">Описание</label>
              <textarea
                id="description"
                v-model="educationForm.description"
                rows="3"
                class="form-input"
                placeholder="Дополнительная информация об образовании..."
              ></textarea>
            </div>
            
            <div class="flex justify-end space-x-2">
              <button 
                type="button" 
                @click="closeEducationForm" 
                class="btn btn-secondary"
              >
                Отмена
              </button>
              <button 
                type="submit" 
                class="btn btn-primary"
                :disabled="loading"
              >
                Сохранить
              </button>
            </div>
          </form>
        </div>
        
        <!-- Список образования -->
        <div v-if="educations.length > 0" class="space-y-6">
          <div 
            v-for="edu in educations" 
            :key="edu.id"
            class="border-b border-secondary-gray/20 pb-4 last:border-0"
          >
            <div class="flex justify-between items-start">
              <div>
                <h3 class="text-lg font-semibold text-primary">{{ edu.institution }}</h3>
                <p class="text-secondary-gray">{{ edu.degree }}</p>
                <p class="text-sm text-secondary-gray">
                  {{ formatDate(edu.start_date) }} — {{ edu.is_current ? 'настоящее время' : formatDate(edu.end_date) }}
                </p>
              </div>
              
              <div v-if="canEdit" class="flex space-x-2">
                <button 
                  @click="openEducationForm(edu)" 
                  class="text-primary hover:underline text-sm"
                >
                  Редактировать
                </button>
                <button 
                  @click="deleteEducation(edu.id)" 
                  class="text-error hover:underline text-sm"
                >
                  Удалить
                </button>
              </div>
            </div>
            
            <p v-if="edu.description" class="mt-2">{{ edu.description }}</p>
          </div>
        </div>
        
        <!-- Нет данных об образовании -->
        <div v-else-if="!showEducationForm" class="text-center py-8">
          <p class="text-secondary-gray" v-if="canEdit">
            Нет информации об образовании.
            <button 
              @click="openEducationForm()" 
              class="text-primary hover:underline"
            >
              Добавить
            </button>
          </p>
          <p class="text-secondary-gray" v-else>
            Нет информации об образовании.
          </p>
        </div>
      </div>
      
      <!-- Вкладка "Навыки" -->
      <div v-else-if="activeTab === 'skills'" :class="[themeStyles.cardBg, 'p-6 rounded-lg shadow']">
        <!-- Кнопка добавления навыка -->
        <div v-if="canEdit && !showSkillForm" class="mb-6 flex justify-end">
          <button 
            @click="openSkillForm()" 
            class="btn btn-primary"
          >
            Добавить навык
          </button>
        </div>
        
        <!-- Форма добавления/редактирования навыка -->
        <div v-if="showSkillForm" class="mb-6 bg-secondary-gray/5 p-4 rounded-lg border border-secondary-gray/20">
          <h3 class="text-lg font-semibold mb-4">
            {{ skillForm.id ? 'Редактирование навыка' : 'Добавление навыка' }}
          </h3>
          
          <form @submit.prevent="saveSkill">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label for="skill-name" class="form-label" :class="[themeStyles.textPrimary]">Название навыка</label>
                <input
                  id="skill-name"
                  v-model="skillForm.name"
                  type="text"
                  class="form-input"
                  placeholder="Например: JavaScript"
                  required
                />
              </div>
              
              <div>
                <label for="skill-category" class="form-label" :class="[themeStyles.textPrimary]">Категория</label>
                <input
                  id="skill-category"
                  v-model="skillForm.category"
                  type="text"
                  class="form-input"
                  placeholder="Например: Программирование"
                />
              </div>
            </div>
            
            <div class="mb-4">
              <label for="skill-level" class="form-label" :class="[themeStyles.textPrimary]">Уровень владения ({{ skillForm.level }}/5)</label>
              <input
                id="skill-level"
                v-model="skillForm.level"
                type="range"
                min="1"
                max="5"
                step="1"
                class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              
              <div class="flex justify-between text-xs text-secondary-gray mt-1">
                <span>Начинающий</span>
                <span>Средний</span>
                <span>Эксперт</span>
              </div>
            </div>
            
            <div class="flex justify-end space-x-2">
              <button 
                type="button" 
                @click="closeSkillForm" 
                class="btn btn-secondary"
              >
                Отмена
              </button>
              <button 
                type="submit" 
                class="btn btn-primary"
                :disabled="loading"
              >
                Сохранить
              </button>
            </div>
          </form>
        </div>
        
        <!-- Список навыков по категориям -->
        <div v-if="Object.keys(groupedSkills).length > 0">
          <div 
            v-for="(categorySkills, category) in groupedSkills" 
            :key="category"
            class="mb-8 last:mb-0"
          >
            <h3 class="text-lg font-semibold text-primary border-b border-secondary-gray/20 pb-2 mb-4">
              {{ category }}
            </h3>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div 
                v-for="skill in categorySkills" 
                :key="skill.id"
                class="bg-secondary-gray/5 p-3 rounded-lg relative"
              >
                <div class="flex justify-between items-center mb-2">
                  <h4 class="font-medium">{{ skill.name }}</h4>
                  
                  <div v-if="canEdit" class="flex space-x-2">
                    <button 
                      @click="openSkillForm(skill)" 
                      class="text-primary hover:underline text-sm"
                    >
                      Изменить
                    </button>
                    <button 
                      @click="deleteSkill(skill.id)" 
                      class="text-error hover:underline text-sm"
                    >
                      Удалить
                    </button>
                  </div>
                </div>
                
                <div class="w-full bg-gray-200 rounded-full h-2.5">
                  <div 
                    class="bg-primary h-2.5 rounded-full" 
                    :style="{ width: `${(skill.level / 5) * 100}%` }"
                  ></div>
                </div>
                <div class="flex justify-between text-xs text-secondary-gray mt-1">
                  <span>{{ skill.level }}/5</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Нет навыков -->
        <div v-else-if="!showSkillForm" class="text-center py-8">
          <p class="text-secondary-gray" v-if="canEdit">
            Нет добавленных навыков.
            <button 
              @click="openSkillForm()" 
              class="text-primary hover:underline"
            >
              Добавить
            </button>
          </p>
          <p class="text-secondary-gray" v-else>
            Нет добавленных навыков.
          </p>
        </div>
      </div>
      
      <!-- Вкладка "Проекты" -->
      <div v-else-if="activeTab === 'projects'" :class="[themeStyles.cardBg, 'p-6 rounded-lg shadow']">
        <!-- Кнопка добавления проекта -->
        <div v-if="canEdit && !showProjectForm" class="mb-6 flex justify-end">
          <button 
            @click="openProjectForm()" 
            class="btn btn-primary"
          >
            Добавить проект
          </button>
        </div>
        
        <!-- Форма добавления/редактирования проекта -->
        <div v-if="showProjectForm" class="mb-6 bg-secondary-gray/5 p-4 rounded-lg border border-secondary-gray/20">
          <h3 class="text-lg font-semibold mb-4">
            {{ projectForm.id ? 'Редактирование проекта' : 'Добавление проекта' }}
          </h3>
          
          <form @submit.prevent="saveProject">
            <div class="mb-4">
              <label for="project-title" class="form-label" :class="[themeStyles.textPrimary]">Название проекта</label>
              <input
                id="project-title"
                v-model="projectForm.title"
                type="text"
                class="form-input"
                placeholder="Название вашего проекта"
                required
              />
            </div>
            
            <div class="mb-4">
              <label for="project-description" class="form-label" :class="[themeStyles.textPrimary]">Описание проекта</label>
              <textarea
                id="project-description"
                v-model="projectForm.description"
                rows="4"
                class="form-input"
                placeholder="Опишите ваш проект..."
                required
              ></textarea>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label for="project-url" class="form-label">URL проекта</label>
                <input
                  id="project-url"
                  v-model="projectForm.url"
                  type="url"
                  class="form-input"
                  placeholder="https://example.com"
                />
              </div>
              
              <div>
                <label for="project-github" class="form-label">GitHub URL</label>
                <input
                  id="project-github"
                  v-model="projectForm.github_url"
                  type="url"
                  class="form-input"
                  placeholder="https://github.com/username/repo"
                />
              </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label for="project-start-date" class="form-label">Дата начала</label>
                <input
                  id="project-start-date"
                  v-model="projectForm.start_date"
                  type="date"
                  class="form-input"
                  required
                />
              </div>
              
              <div>
                <label for="project-end-date" class="form-label">Дата завершения</label>
                <input
                  id="project-end-date"
                  v-model="projectForm.end_date"
                  type="date"
                  class="form-input"
                  :disabled="projectForm.is_ongoing"
                />
                
                <div class="mt-2">
                  <label class="inline-flex items-center">
                    <input 
                      type="checkbox" 
                      v-model="projectForm.is_ongoing"
                      class="form-checkbox"
                    />
                    <span class="ml-2">Проект в процессе выполнения</span>
                  </label>
                </div>
              </div>
            </div>
            
            <div class="flex justify-end space-x-2">
              <button 
                type="button" 
                @click="closeProjectForm" 
                class="btn btn-secondary"
              >
                Отмена
              </button>
              <button 
                type="submit" 
                class="btn btn-primary"
                :disabled="loading"
              >
                Сохранить
              </button>
            </div>
          </form>
        </div>
        
        <!-- Список проектов -->
        <div v-if="projects.length > 0" class="space-y-8">
          <div 
            v-for="project in projects" 
            :key="project.id"
            class="border-b border-secondary-gray/20 pb-6 last:border-0"
          >
            <div class="flex justify-between items-start">
              <h3 class="text-xl font-semibold text-primary">{{ project.title }}</h3>
              
              <div v-if="canEdit" class="flex space-x-2">
                <button 
                  @click="openProjectForm(project)" 
                  class="text-primary hover:underline text-sm"
                >
                  Редактировать
                </button>
                <button 
                  @click="deleteProject(project.id)" 
                  class="text-error hover:underline text-sm"
                >
                  Удалить
                </button>
              </div>
            </div>
            
            <p class="text-sm text-secondary-gray mb-3">
              {{ formatDate(project.start_date) }} — {{ project.is_ongoing ? 'настоящее время' : formatDate(project.end_date) }}
            </p>
            
            <p class="mb-4">{{ project.description }}</p>
            
            <div class="flex flex-wrap gap-2">
              <a 
                v-if="project.url" 
                :href="project.url" 
                target="_blank" 
                class="text-sm text-primary hover:underline flex items-center"
              >
                <span>Посмотреть проект</span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
              
              <a 
                v-if="project.github_url" 
                :href="project.github_url" 
                target="_blank" 
                class="text-sm text-primary hover:underline flex items-center"
              >
                <span>GitHub</span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
          </div>
        </div>
        
        <!-- Нет проектов -->
        <div v-else-if="!showProjectForm" class="text-center py-8">
          <p class="text-secondary-gray" v-if="canEdit">
            Нет добавленных проектов.
            <button 
              @click="openProjectForm()" 
              class="text-primary hover:underline"
            >
              Добавить
            </button>
          </p>
          <p class="text-secondary-gray" v-else>
            Нет добавленных проектов.
          </p>
        </div>
      </div>
      
      <!-- Вкладка "Сертификаты" -->
      <div v-else-if="activeTab === 'certificates'" class="bg-white p-6 rounded-lg shadow">
        <!-- Кнопка добавления сертификата -->
        <div v-if="canEdit && !showCertificateForm" class="mb-6 flex justify-end">
          <button 
            @click="openCertificateForm()" 
            class="btn btn-primary"
          >
            Добавить сертификат
          </button>
        </div>
        
        <!-- Форма добавления/редактирования сертификата -->
        <div v-if="showCertificateForm" class="mb-6 bg-secondary-gray/5 p-4 rounded-lg border border-secondary-gray/20">
          <h3 class="text-lg font-semibold mb-4">
            {{ certificateForm.id ? 'Редактирование сертификата' : 'Добавление сертификата' }}
          </h3>
          
          <form @submit.prevent="saveCertificate">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label for="certificate-title" class="form-label">Название сертификата</label>
                <input
                  id="certificate-title"
                  v-model="certificateForm.title"
                  type="text"
                  class="form-input"
                  placeholder="Название сертификата"
                  required
                />
              </div>
              
              <div>
                <label for="certificate-issuer" class="form-label">Кем выдан</label>
                <input
                  id="certificate-issuer"
                  v-model="certificateForm.issuer"
                  type="text"
                  class="form-input"
                  placeholder="Организация, выдавшая сертификат"
                  required
                />
              </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label for="certificate-issue-date" class="form-label">Дата выдачи</label>
                <input
                  id="certificate-issue-date"
                  v-model="certificateForm.issue_date"
                  type="date"
                  class="form-input"
                  required
                />
              </div>
              
              <div>
                <label for="certificate-expiration-date" class="form-label">Дата истечения (если есть)</label>
                <input
                  id="certificate-expiration-date"
                  v-model="certificateForm.expiration_date"
                  type="date"
                  class="form-input"
                />
              </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label for="certificate-id" class="form-label">ID сертификата</label>
                <input
                  id="certificate-id"
                  v-model="certificateForm.credential_id"
                  type="text"
                  class="form-input"
                  placeholder="Уникальный идентификатор сертификата"
                />
              </div>
              
              <div>
                <label for="certificate-url" class="form-label">URL сертификата</label>
                <input
                  id="certificate-url"
                  v-model="certificateForm.credential_url"
                  type="url"
                  class="form-input"
                  placeholder="https://example.com/verify"
                />
              </div>
            </div>
            
            <div class="mb-4">
              <label for="certificate-description" class="form-label">Описание</label>
              <textarea
                id="certificate-description"
                v-model="certificateForm.description"
                rows="3"
                class="form-input"
                placeholder="Дополнительная информация о сертификате..."
              ></textarea>
            </div>
            
            <div class="flex justify-end space-x-2">
              <button 
                type="button" 
                @click="closeCertificateForm" 
                class="btn btn-secondary"
              >
                Отмена
              </button>
              <button 
                type="submit" 
                class="btn btn-primary"
                :disabled="loading"
              >
                Сохранить
              </button>
            </div>
          </form>
        </div>
        
        <!-- Список сертификатов -->
        <div v-if="certificates.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div 
            v-for="certificate in certificates" 
            :key="certificate.id"
            class="bg-white border border-secondary-gray/20 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow"
          >
            <div class="border-b border-secondary-gray/10 bg-secondary-gray/5 p-4">
              <div class="flex justify-between items-start">
                <h3 class="text-lg font-semibold text-primary">{{ certificate.title }}</h3>
                
                <div v-if="canEdit" class="flex space-x-2">
                  <button 
                    @click="openCertificateForm(certificate)" 
                    class="text-primary hover:underline text-sm"
                  >
                    Изменить
                  </button>
                  <button 
                    @click="deleteCertificate(certificate.id)" 
                    class="text-error hover:underline text-sm"
                  >
                    Удалить
                  </button>
                </div>
              </div>
              <p class="text-sm text-secondary-gray">{{ certificate.issuer }}</p>
            </div>
            
            <div class="p-4">
              <div class="mb-3">
                <div class="text-sm font-medium">Дата выдачи:</div>
                <div>{{ formatDate(certificate.issue_date) }}</div>
              </div>
              
              <div v-if="certificate.expiration_date" class="mb-3">
                <div class="text-sm font-medium">Действителен до:</div>
                <div>{{ formatDate(certificate.expiration_date) }}</div>
              </div>
              
              <div v-if="certificate.description" class="mb-3">
                <div class="text-sm font-medium">Описание:</div>
                <div>{{ certificate.description }}</div>
              </div>
              
              <div v-if="certificate.credential_id" class="mb-3">
                <div class="text-sm font-medium">ID:</div>
                <div class="text-sm font-mono">{{ certificate.credential_id }}</div>
              </div>
              
              <div class="flex flex-wrap gap-2 mt-4">
                <a 
                  v-if="certificate.credential_url" 
                  :href="certificate.credential_url" 
                  target="_blank" 
                  class="text-primary hover:underline flex items-center"
                >
                  <span>Проверить сертификат</span>
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
                
                <a 
                  v-if="certificate.file" 
                  :href="certificate.file" 
                  target="_blank" 
                  class="text-primary hover:underline flex items-center"
                >
                  <span>Просмотреть файл</span>
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Нет сертификатов -->
        <div v-else-if="!showCertificateForm" class="text-center py-8">
          <p class="text-secondary-gray" v-if="canEdit">
            Нет добавленных сертификатов.
            <button 
              @click="openCertificateForm()" 
              class="text-primary hover:underline"
            >
              Добавить
            </button>
          </p>
          <p class="text-secondary-gray" v-else>
            Нет добавленных сертификатов.
          </p>
        </div>
      </div>
      
      <!-- Вкладка "Отзывы" -->
      <div v-else-if="activeTab === 'comments'" class="bg-white p-6 rounded-lg shadow">
        <!-- Кнопка добавления комментария -->
        <div v-if="canEdit && !showCommentForm" class="mb-6 flex justify-end">
          <button 
            @click="showCommentForm = true" 
            class="btn btn-primary"
          >
            Добавить отзыв
          </button>
        </div>
        
        <!-- Форма добавления/редактирования комментария -->
        <div v-if="showCommentForm" class="mb-6 bg-secondary-gray/5 p-4 rounded-lg border border-secondary-gray/20">
          <h3 class="text-lg font-semibold mb-4">
            Добавление отзыва
          </h3>
          
          <form @submit.prevent="saveComment">
            <div class="mb-4">
              <label for="comment-text" class="form-label">Текст отзыва</label>
              <textarea
                id="comment-text"
                v-model="commentForm.text"
                rows="3"
                class="form-input"
                placeholder="Напишите ваш отзыв..."
                required
              ></textarea>
            </div>
            
            <div class="mb-4">
              <label for="comment-rating" class="form-label">Оценка</label>
              <input
                id="comment-rating"
                v-model="commentForm.rating"
                type="range"
                min="1"
                max="5"
                step="1"
                class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
            </div>
            
            <div class="flex justify-end space-x-2">
              <button 
                type="button" 
                @click="showCommentForm = false" 
                class="btn btn-secondary"
              >
                Отмена
              </button>
              <button 
                type="submit" 
                class="btn btn-primary"
                :disabled="loading"
              >
                Сохранить
              </button>
            </div>
          </form>
        </div>
        
        <!-- Список комментариев -->
        <div v-if="comments.length > 0" class="space-y-6">
          <div 
            v-for="comment in comments" 
            :key="comment.id"
            class="border-b border-secondary-gray/20 pb-4 last:border-0"
          >
            <div class="flex justify-between items-start">
              <div>
                <p class="text-secondary-gray">{{ comment.text }}</p>
                <p class="text-sm text-secondary-gray">Оценка: {{ comment.rating }}/5</p>
              </div>
              
              <div v-if="canEdit" class="flex space-x-2">
                <button 
                  @click="deleteComment(comment.id)" 
                  class="text-error hover:underline text-sm"
                >
                  Удалить
                </button>
              </div>
            </div>
            
            <p class="text-sm text-secondary-gray">{{ formatDateTime(comment.created_at) }}</p>
          </div>
        </div>
        
        <!-- Нет комментариев -->
        <div v-else-if="!showCommentForm" class="text-center py-8">
          <p class="text-secondary-gray" v-if="canEdit">
            Нет добавленных отзывов.
            <button 
              @click="showCommentForm = true" 
              class="text-primary hover:underline"
            >
              Добавить
            </button>
          </p>
          <p class="text-secondary-gray" v-else>
            Нет добавленных отзывов.
          </p>
        </div>
      </div>
    </div>
    
    <div v-else class="text-center py-12">
      <p class="text-error">Портфолио не найдено или у вас нет прав для его просмотра.</p>
      <button @click="router.push('/portfolios')" class="btn btn-primary mt-4">
        Вернуться к списку портфолио
      </button>
    </div>
  </div>
</template>

<style scoped>
.form-label {
  @apply block text-sm font-medium text-gray-700 mb-1;
}

.form-input {
  @apply block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50;
}

.form-checkbox {
  @apply rounded border-gray-300 text-primary focus:ring-primary;
}
</style> 