/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#006d77',       // deep teal — accent colour
        cream: '#f5f0eb',         // warm off-white background
        ink: '#1a1a1a',           // near-black text
        muted: '#6b7280',         // secondary text
        surface: '#ffffff',       // card backgrounds
        'primary-dark': '#004f58',
        'primary-light': '#e8f4f5',
        'match-yes': '#166534',   // matching skill text
        'match-yes-bg': '#dcfce7',
        'match-no': '#9a3412',    // missing skill text
        'match-no-bg': '#ffedd5',
      },
      fontFamily: {
        display: ["'Fraunces'", 'Georgia', 'serif'],
        body: ["'Inter'", 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
