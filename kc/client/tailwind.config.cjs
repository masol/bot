/** @type {import('tailwindcss').Config} */
module.exports = {
  future: {
    purgeLayersByDefault: true,
    removeDeprecatedGapUtilities: true,
  },
  relative: true,
  content: [
    "./src/**/*.{html,js,svelte,ts}",
    './node_modules/tw-elements/dist/js/**/*.{html,js,svelte,ts}',
    "./node_modules/flowbite-svelte/**/*.{html,js,svelte,ts}"
  ],
  // enabled: "production",
  // safelist: [
  //   {
  //     pattern: /./
  //   }
  // ],
  theme: {
    minHeight: {
      '3/4s': '79vh',
    },
    ripple: theme => ({
      colors: theme('colors')
    }),
    extend: {},
  },
  plugins: [
    require('flowbite/plugin'),
    require('tw-elements/dist/plugin'),
    require('tailwindcss-ripple')()
  ],
  darkMode: 'class'
}
