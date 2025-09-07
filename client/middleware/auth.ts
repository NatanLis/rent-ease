export default defineNuxtRouteMiddleware((to) => {
  const { getToken } = useAuth()
  
  // Sprawdź czy użytkownik jest zalogowany
  if (!getToken()) {
    // Przekieruj na stronę logowania jeśli nie jest zalogowany
    return navigateTo('/LogIn')
  }
})
