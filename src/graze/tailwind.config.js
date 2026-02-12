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
        'graze-green': {
          50: '#e6f9ef',
          100: '#b3efd1',
          200: '#80e5b3',
          300: '#4ddb95',
          400: '#1ad177',
          500: '#06C167',
          600: '#05a85a',
          700: '#048f4d',
          800: '#037640',
          900: '#025d33',
        },
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
