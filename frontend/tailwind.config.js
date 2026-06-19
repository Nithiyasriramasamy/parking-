/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: '#1a1a2e',
        card: '#22223b',
        primary: '#4ea8de',
        danger: '#e63946',
        warning: '#f4a261',
        success: '#2a9d8f'
      }
    },
  },
  plugins: [],
}
