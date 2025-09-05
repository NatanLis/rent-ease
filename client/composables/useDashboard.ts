import { createSharedComposable } from '@vueuse/core'

const _useDashboard = () => {
  const route = useRoute()
  const router = useRouter()
  const isNotificationsSlideoverOpen = ref(false)

  defineShortcuts({
    'g-h': () => router.push('/home'),
    'g-i': () => router.push('/home/inbox'),
    'g-c': () => router.push('/home/customers'),
    'g-t': () => router.push('/home/tenants'),
    'g-l': () => router.push('/home/leases'),
    'g-p': () => router.push('/home/properties'),
    'g-u': () => router.push('/home/units'),
    'g-s': () => router.push('/home/settings'),
    'n': () => isNotificationsSlideoverOpen.value = !isNotificationsSlideoverOpen.value
  })

  watch(() => route.fullPath, () => {
    isNotificationsSlideoverOpen.value = false
  })

  return {
    isNotificationsSlideoverOpen
  }
}

export const useDashboard = createSharedComposable(_useDashboard)
