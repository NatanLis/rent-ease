// client/nuxt.config.js
const config = {
  apiServer: process.env.NODE_ENV !== 'production' ? 'http://localhost:8000' : '/api',
  env: process.env.ENV || 'dev'   // dev, beta, prod
}

export default defineNuxtConfig({
  devtools: { enabled: true },
  ssr: false,

  runtimeConfig: {
    public: {
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
          hid: 'og:title',
          property: 'og:title',
          content: 'rent.ease'
        },
        {
          hid: 'og:description',
          property: 'og:description',
          content: 'Make renting easy'
        },
        {
          hid: 'og:site_name',
          property: 'og:site_name',
          content: 'rent.ease'
        },
      ],
      // link: [{ rel: 'icon', type: 'image/x-icon', href: favicon }]
    }
  },

  modules: [
    '@nuxt/ui',
    '@nuxt/eslint',
    // '@pinia/nuxt'
  ],

  vite: {
    resolve: {
      alias: {
        'node:crypto': 'crypto-browserify'
      }
    },
    esbuild: {
      tsconfigRaw: {
        compilerOptions: {
          experimentalDecorators: true
        }
      }
    }
  },

  css: ['@/assets/styles/main.scss'],
  compatibilityDate: '2025-02-01',
})
