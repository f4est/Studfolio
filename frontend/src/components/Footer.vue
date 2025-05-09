<script setup>
const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="bg-white shadow mt-auto py-4">
    <div class="container mx-auto px-4">
      <div class="flex flex-col md:flex-row justify-between items-center">
        <div class="text-secondary-gray text-sm mb-2 md:mb-0">
          © {{ new Date().getFullYear() }} Портфолио студентов. Все права защищены.
        </div>
        
        <div class="flex space-x-4">
          <a href="#" class="text-secondary-gray hover:text-primary text-sm">О проекте</a>
          <a href="#" class="text-secondary-gray hover:text-primary text-sm">Контакты</a>
          <a href="#" class="text-secondary-gray hover:text-primary text-sm">Правила</a>
        </div>
      </div>
    </div>
  </footer>
</template> 