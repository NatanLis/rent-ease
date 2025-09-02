const token = ref<string | null>(null)

export function useAuth() {
  function setToken(accessToken: string) {
    token.value = accessToken
    localStorage.setItem('access_token', accessToken)
  }

  function getToken(): string | null {
    if (!token.value) {
      token.value = localStorage.getItem('access_token')
    }
    return token.value
  }

  function clearToken() {
    token.value = null
    localStorage.removeItem('access_token')
  }

  return { token, setToken, getToken, clearToken }
}
