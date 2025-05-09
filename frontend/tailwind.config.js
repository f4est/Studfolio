/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary': '#2563EB',
        'dark-text': '#1F2937',
        'secondary-gray': '#C1C2CC',
        'bg-light': '#F3F4F6',
        'success': '#059669',
        'warning': '#D97706',
        'error': '#DC2626',
      },
    },
  },
  plugins: [],
} 