// client/nuxt.config.js
const config = {
  apiServer: process.env.NODE_ENV !== 'production' ? 'http://localhost:8000/api' : '/api',
  env: process.env.ENV || 'dev'   // dev, beta, prod
}

export default defineNuxtConfig({
  devtools: { enabled: true },
  ssr: false,

  // disabled for local dev
  runtimeConfig: {
    public: {
      // apiURL: 'http://localhost:8000/api',
      apiURL: config.apiServer,
      env: config.env,
    }
  },

  nitro: {
    devProxy: {
      '/api/': {
        target: config.apiServer,
        changeOrigin: true,
        headers: { 'Connection': 'keep-alive' }
      }
    }
  },

  app: {
    head: {
      title: 'Rent Ease',
      meta: [
        { charset: 'utf-8' },
        {
          property: 'og:title',
          content: 'rent.ease'
        },
        {
          property: 'og:description',
          content: 'Make renting easy'
        },
        {
          property: 'og:site_name',
          content: 'rent.ease'
        },
      ],
      link: [{ rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }]
    }
  },

  modules: [
    '@nuxt/ui-pro',
    '@nuxt/eslint',
    '@nuxt/image',
    '@nuxt/content'
    // '@pinia/nuxt'
  ],

  colorMode: {
    preference: 'dark'
  },

  vite: {
    esbuild: {
      tsconfigRaw: {
        compilerOptions: {
          experimentalDecorators: true
        }
      }
    }
  },

// delete this later
  routeRules: {
    '/api/**': {
      cors: true
    }
  },

  css: ['@/assets/styles/main.css'],
  compatibilityDate: '2025-09-05',
})
