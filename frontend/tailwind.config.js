/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        pnb: {
          red: '#8B0000',
          'red-light': '#B91C1C',
          gold: '#F59E0B',
          'gold-dark': '#B8860B',
          dark: '#1A1A2E',
        },
      },
    },
  },
  plugins: [],
}
