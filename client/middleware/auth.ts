export default defineNuxtRouteMiddleware(async (to: any) => {
  console.log('Auth middleware running for:', to.path)

  if (to.path === '/LogIn') {
    return
  }

  const { getToken, isAuthenticated } = useAuth()
  const token = getToken()

  console.log('Token exists:', !!token)

  if (!token) {
    console.log('No token, redirecting to login')
    return navigateTo('/LogIn')
  }

  console.log('Validating token...')
  const isValid = await isAuthenticated()
  console.log('Token valid:', isValid)

  if (!isValid) {
    console.log('Invalid token, redirecting to login')
    return navigateTo('/LogIn')
  }

  console.log('Auth middleware passed')
})
