/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // BioAI Hub Brand Colors (based on Figma designs)
        primary: {
          50: '#eef2ff',
          100: '#e0e7ff',
          500: '#3b50a6',
          600: '#2e4b8e',
          700: '#1e3a8a',
          800: '#1e3a8a',
          900: '#1a237e',
        },
        secondary: {
          50: '#f0fdf4',
          100: '#dcfce7',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
        },
        // Semantic colors
        validated: '#22c55e',    // Green for validated badge
        sandbox: '#94a3b8',      // Gray for sandbox badge
        pending: '#f59e0b',      // Amber for pending validation
      },
    },
  },
  plugins: [],
}
