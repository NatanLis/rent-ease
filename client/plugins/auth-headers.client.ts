export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.hook('fetch:request', (fetchOptions: any) => {
    const { getToken } = useAuth()
    const token = getToken()

    if (token) {
      fetchOptions.headers = {
        ...fetchOptions.headers,
        'Authorization': `Bearer ${token}`
      }
    }
  })

  nuxtApp.hook('fetch:error', (error: any) => {
    if (error.response?.status === 401) {
      const { clearToken } = useAuth()
      clearToken()
      navigateTo('/LogIn')
    }
  })
})
