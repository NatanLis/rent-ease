<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'
import { breakpointsTailwind, useBreakpoints } from '@vueuse/core'
import type { Mail } from '~/types'
const router = useRouter()
const route = useRoute()

const tabItems = [{
  label: 'All',
  value: 'all'
}, {
  label: 'Unread',
  value: 'unread'
}]
const selectedTab = ref('all')

const { data: mails, refresh: refreshMails, error: mailsError } = await useFetch<Mail[]>('/api/mails', {
  default: () => [],
  server: false
})
// ↓ Temporary safeguard
const safeMails = computed(() => mails.value ?? [])

// Filter mails based on the selected tab
const filteredMails = computed(() => {
  const list = safeMails.value
  if (selectedTab.value === 'unread') {
    return list.filter(mail => !!mail.unread)
  }
  return list
})

const selectedMail = ref<Mail | null>()

const isMailPanelOpen = computed({
  get() {
    return !!selectedMail.value
  },
  set(value: boolean) {
    if (!value) {
      selectedMail.value = null
    }
  }
})

// Reset selected mail if it's not in the filtered mails
watch(filteredMails, () => {
  if (!filteredMails.value.find(mail => mail.id === selectedMail.value?.id)) {
    selectedMail.value = null
  }
})
// Sync selected thread with URL (?thread=ID) so selection survives refresh/hmr
watch(selectedMail, (m) => {
  const q = { ...route.query }
  if (m?.id) q.thread = String(m.id)
  else delete q.thread
  router.replace({ query: q })
})

onMounted(() => {
  const threadFromQuery = route.query.thread as string | undefined
  if (!threadFromQuery) return
  const found = mails.value?.find(m => String(m.id) === threadFromQuery)
  if (found) selectedMail.value = found
})

// ---- replace your existing watch(selectedMail, ...) with this:
watch(selectedMail, async (newMail) => {
  // only run in the browser (avoid server-side watch during SSR)
  if (!process.client) return
  if (!newMail) return

  // If it's unread, mark server-side then reload the inbox list
  if (newMail.unread) {
    try {
      // Mark as read on the server (PATCH /api/mails/:id)
      await $fetch(`/api/mails/${newMail.id}`, { method: 'PATCH' })
    } catch (err) {
      console.error('Failed to mark thread read:', err)
      // continue to try refresh below even if PATCH failed
    }

    // Re-fetch the full mail list from server so filteredMails recalculates correctly
    try {
      await refreshMails()
      // Re-bind selectedMail to the fresh object from mails.value (ensures reactivity)
      const updated = mails.value?.find(m => m.id === newMail.id)
      if (updated) {
        selectedMail.value = updated
      } else {
        // fallback: keep what we have
        newMail.unread = false
      }
    } catch (err) {
      console.error('Failed to refresh mails after marking read:', err)
      // fallback local update to keep UI consistent
      const idx = mails.value?.findIndex(m => m.id === newMail.id)
      if (typeof idx === 'number' && idx !== -1) mails.value[idx].unread = false
      newMail.unread = false
    }
  }
})

const breakpoints = useBreakpoints(breakpointsTailwind)
const isMobile = breakpoints.smaller('lg')

definePageMeta({
  layout: 'dashboard',
})
</script>

<template>
    <UDashboardPanel
      id="inbox-1"
      :default-size="25"
      :min-size="20"
      :max-size="30"
      resizable
    >
      <UDashboardNavbar title="Inbox">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
        <template #trailing>
          <UBadge :label="filteredMails.length" variant="subtle" />
        </template>

        <template #right>
          <UTabs
            v-model="selectedTab"
            :items="tabItems"
            class="w-32"
            :content="false"
            size="xs"
          />
        </template>
      </UDashboardNavbar>
      <InboxList v-model="selectedMail" :mails="filteredMails" />
    </UDashboardPanel>

    <InboxMail v-if="selectedMail" :mail="selectedMail" @close="selectedMail = null" />

    <div v-else class="hidden lg:flex flex-1 items-center justify-center">
      <UIcon name="i-lucide-inbox" class="size-32 text-(--ui-text-dimmed)" />
    </div>

    <ClientOnly>
      <USlideover v-if="isMobile" v-model:open="isMailPanelOpen">
        <template #content>
          <InboxMail v-if="selectedMail" :mail="selectedMail" @close="selectedMail = null" />
        </template>
      </USlideover>
    </ClientOnly>
</template>
