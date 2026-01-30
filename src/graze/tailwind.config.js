/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Density label colors
        'density-excellent': '#22c55e',
        'density-good': '#eab308',
        'density-average': '#f97316',
        'density-low': '#9ca3af',
      },
    },
  },
  plugins: [],
}
