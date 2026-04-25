/** @type {import('tailwindcss').Config} */
// NOTA: actualmente el proyecto usa StyleSheet de React Native (no tailwind/NativeWind).
// Si se decide adoptar NativeWind, completar este archivo y añadir el preset.
module.exports = {
  content: [
    './app/**/*.{js,jsx,ts,tsx}',
    './components/**/*.{js,jsx,ts,tsx}',
    './hooks/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
