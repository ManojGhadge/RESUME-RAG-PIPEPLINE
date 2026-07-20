// tailwind.config.cjs
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx,html}'],
  theme: {
    extend: {
      colors: {
        primary: '#0d9488', // deep teal accent
        neutral: {
          50: '#f8fafc', // warm off-white background
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
        serif: ['Fraunces', 'ui-serif', 'Georgia'],
      },
    },
  },
  plugins: [],
};
