const token = ref<string | null>(null)
const isValidating = ref<boolean>(false)

export function useAuth() {
  function setToken(accessToken: string) {
    token.value = accessToken
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', accessToken)
    }
  }

  function getToken(): string | null {
    if (!token.value && typeof window !== 'undefined') {
      const stored = localStorage.getItem('access_token')
      if (stored) {
        token.value = stored
      }
    }
    return token.value
  }

  function clearToken() {
    token.value = null
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
    }
  }

  async function validateToken(): Promise<boolean> {
    const currentToken = getToken()

    if (!currentToken) {
      return false
    }

    isValidating.value = true

    try {
      const response = await fetch('http://localhost:8000/api/auth/me', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${currentToken}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const userData = await response.json()
        const { setUser } = useUser()
        setUser(userData)
        return true
      } else {
        clearToken()
        return false
      }
    } catch (error) {
      console.error('Error validating token:', error)
      clearToken()
      return false
    } finally {
      isValidating.value = false
    }
  }

  async function isAuthenticated(): Promise<boolean> {
    if (!getToken()) {
      return false
    }
    return await validateToken()
  }

  return {
    token,
    isValidating,
    setToken,
    getToken,
    clearToken,
    validateToken,
    isAuthenticated
  }
}
