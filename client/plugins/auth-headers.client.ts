export default defineNuxtPlugin(() => {
  const { getToken } = useAuth()
  
  // Add auth headers to all fetch requests
  $fetch.create({
    onRequest({ request, options }) {
      const token = getToken()
      if (token) {
        options.headers = {
          ...options.headers,
          'Authorization': `Bearer ${token}`
        }
      }
    }
  })
})
