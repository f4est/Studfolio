<script setup>
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()
</script>

<template>
  <div>
    <section class="py-12 bg-white rounded-lg shadow mb-8">
      <div class="max-w-3xl mx-auto text-center">
        <h1 class="text-4xl font-bold text-primary mb-4">Портфолио студентов</h1>
        <p class="text-xl text-dark-text mb-8">
          Создавайте, храните и делитесь своими достижениями в одном месте
        </p>
        <div class="flex justify-center space-x-4">
          <RouterLink 
            v-if="!authStore.isAuthenticated" 
            to="/register" 
            class="btn btn-primary"
          >
            Начать сейчас
          </RouterLink>
          <RouterLink 
            v-else 
            to="/portfolios" 
            class="btn btn-primary"
          >
            Просмотреть портфолио
          </RouterLink>
          <RouterLink to="/portfolios" class="btn btn-secondary">
            Узнать больше
          </RouterLink>
        </div>
      </div>
    </section>
    
    <section class="mb-8">
      <h2 class="text-2xl font-bold mb-6 text-center">Что вы можете делать?</h2>
      <div class="grid md:grid-cols-3 gap-6">
        <div class="bg-white p-6 rounded-lg shadow">
          <h3 class="text-xl font-bold mb-3 text-primary">Создавайте портфолио</h3>
          <p class="text-dark-text">
            Структурируйте ваши достижения, навыки и проекты в профессиональном формате
          </p>
        </div>
        <div class="bg-white p-6 rounded-lg shadow">
          <h3 class="text-xl font-bold mb-3 text-primary">Получайте обратную связь</h3>
          <p class="text-dark-text">
            Преподаватели могут комментировать и оценивать различные разделы вашего портфолио
          </p>
        </div>
        <div class="bg-white p-6 rounded-lg shadow">
          <h3 class="text-xl font-bold mb-3 text-primary">Экспортируйте в PDF</h3>
          <p class="text-dark-text">
            Создавайте профессиональные PDF-отчеты для презентации ваших достижений
          </p>
        </div>
      </div>
    </section>
    
    <section class="bg-white p-8 rounded-lg shadow">
      <h2 class="text-2xl font-bold mb-6 text-center">Начните сейчас</h2>
      <p class="text-center mb-6">
        Создайте свой профиль и начните формировать свое портфолио уже сегодня!
      </p>
      <div class="flex justify-center">
        <RouterLink 
          v-if="!authStore.isAuthenticated" 
          to="/register" 
          class="btn btn-primary"
        >
          Регистрация
        </RouterLink>
        <RouterLink 
          v-else 
          to="/portfolios" 
          class="btn btn-primary"
        >
          Перейти к портфолио
        </RouterLink>
      </div>
    </section>
  </div>
</template> 