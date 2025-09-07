import { User } from '@/models/userModel'
import type { UserI } from '@/api/interfaces/UserI'

const user = ref<User | null>(null)

export function useUser() {
  function setUser(newUser: UserI) {
    user.value = User.fromObject(newUser)
    localStorage.setItem('user', JSON.stringify(user.value.toJSON()))
  }

  function getUser(): User | null {
    if (!user.value) {
      const stored = localStorage.getItem('user')
      if (stored) {
        user.value = User.fromObject(JSON.parse(stored))
      }
    }
    return user.value
  }

  // Reactive getter for computed properties
  const currentUser = computed(() => getUser())

  function updateUser(data: Partial<User>) {
    if (user.value) {
      user.value.update(data)
      localStorage.setItem('user', JSON.stringify(user.value.toJSON()))
    }
  }

  function clearUser() {
    user.value = null
    localStorage.removeItem('user')
  }

  return { user, setUser, getUser, currentUser, updateUser, clearUser }
}
