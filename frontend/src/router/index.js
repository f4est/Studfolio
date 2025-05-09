import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import PortfoliosView from '@/views/PortfoliosView.vue'
import PortfolioView from '@/views/PortfolioView.vue'
import AdminView from '@/views/AdminView.vue'
import NotFoundView from '@/views/NotFoundView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    {
      path: '/portfolios',
      name: 'portfolios',
      component: PortfoliosView
    },
    {
      path: '/portfolio/:id',
      name: 'portfolio',
      component: PortfolioView,
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundView
    }
  ]
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Проверка, требуется ли аутентификация для маршрута
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } 
  // Проверка, требуется ли роль администратора для маршрута
  else if (to.meta.requiresAdmin && !(authStore.isAdmin || authStore.isTeacher)) {
    next({ name: 'home' })
  }
  else {
    next()
  }
})

export default router 