<script setup lang="ts">
import { sub } from 'date-fns'
import type { Period, Range } from '~/types'

const { isNotificationsSlideoverOpen } = useDashboard()

const items = [[{
  label: 'New mail',
  icon: 'i-lucide-send',
  to: '/home/inbox'
}, {
  label: 'New customer',
  icon: 'i-lucide-user-plus',
  to: '/home/customers'
}]]

const range = shallowRef<Range>({
  start: sub(new Date(), { days: 14 }),
  end: new Date()
})
const period = ref<Period>('daily')

// Removed manual refresh controls

const { getToken } = useAuth()
const token = await getToken()

// Fetch real data for dashboard stats
const { data: properties } = await useFetch<any[]>('/api/properties', {
  default: () => [],
  server: false,
  headers: token ? {
    'Authorization': `Bearer ${token}`
  } : {}
})
const { data: tenants } = await useFetch<any[]>('/api/tenants', {
  default: () => [],
  server: false,
  headers: token ? {
    'Authorization': `Bearer ${token}`
  } : {}
})
const { data: leases } = await useFetch<any[]>('/api/leases', {
  default: () => [],
  server: false,
  headers: token ? {
    'Authorization': `Bearer ${token}`
  } : {}
})

// Derived metrics
const totalProperties = computed(() => (properties.value || []).length)
const totalUnits = computed(() => (properties.value || []).reduce((sum: number, p: any) => sum + (p?.unitsCount || 0), 0))
const totalTenants = computed(() => (tenants.value || []).length)
const activeLeases = computed(() => (leases.value || []).filter((l: any) => l?.isActive === true || l?.status === 'active').length)

definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})
</script>

<template>
  <UDashboardPanel id="home">
    <template #header>
      <UDashboardNavbar title="Home" :ui="{ right: 'gap-3' }">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <UTooltip text="Notifications" :shortcuts="['N']">
            <UButton
              color="neutral"
              variant="ghost"
              square
              @click="isNotificationsSlideoverOpen = true"
            >
              <UChip color="error" inset>
                <UIcon name="i-lucide-bell" class="size-5 shrink-0" />
              </UChip>
            </UButton>
          </UTooltip>

          <UDropdownMenu :items="items">
            <UButton icon="i-lucide-plus" size="md" class="rounded-full" />
          </UDropdownMenu>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <!-- Real-time stats from project data -->
      <UPageGrid class="lg:grid-cols-4 gap-4 sm:gap-6 lg:gap-px mb-6">
        <UPageCard :icon="'i-lucide-users'" title="Tenants" variant="subtle" to="/home/tenants"
          :ui="{ container: 'gap-y-1.5', leading: 'p-2.5 rounded-full bg-(--ui-primary)/10 ring ring-inset ring-(--ui-primary)/25', title: 'font-normal text-(--ui-text-muted) text-xs uppercase' }"
          class="lg:rounded-none first:rounded-l-[calc(var(--ui-radius)*2)] last:rounded-r-[calc(var(--ui-radius)*2)] hover:z-1">
          <div class="flex items-center gap-2">
            <span class="text-2xl font-semibold text-(--ui-text-highlighted)">{{ totalTenants }}</span>
          </div>
        </UPageCard>

        <UPageCard :icon="'i-lucide-badge-check'" title="Active leases" variant="subtle" to="/home/leases"
          :ui="{ container: 'gap-y-1.5', leading: 'p-2.5 rounded-full bg-(--ui-primary)/10 ring ring-inset ring-(--ui-primary)/25', title: 'font-normal text-(--ui-text-muted) text-xs uppercase' }"
          class="lg:rounded-none first:rounded-l-[calc(var(--ui-radius)*2)] last:rounded-r-[calc(var(--ui-radius)*2)] hover:z-1">
          <div class="flex items-center gap-2">
            <span class="text-2xl font-semibold text-(--ui-text-highlighted)">{{ activeLeases }}</span>
          </div>
        </UPageCard>

        <UPageCard :icon="'i-lucide-building'" title="Properties" variant="subtle" to="/home/properties"
          :ui="{ container: 'gap-y-1.5', leading: 'p-2.5 rounded-full bg-(--ui-primary)/10 ring ring-inset ring-(--ui-primary)/25', title: 'font-normal text-(--ui-text-muted) text-xs uppercase' }"
          class="lg:rounded-none first:rounded-l-[calc(var(--ui-radius)*2)] last:rounded-r-[calc(var(--ui-radius)*2)] hover:z-1">
          <div class="flex items-center gap-2">
            <span class="text-2xl font-semibold text-(--ui-text-highlighted)">{{ totalProperties }}</span>
          </div>
        </UPageCard>

        <UPageCard :icon="'i-lucide-box'" title="Units" variant="subtle" to="/home/units"
          :ui="{ container: 'gap-y-1.5', leading: 'p-2.5 rounded-full bg-(--ui-primary)/10 ring ring-inset ring-(--ui-primary)/25', title: 'font-normal text-(--ui-text-muted) text-xs uppercase' }"
          class="lg:rounded-none first:rounded-l-[calc(var(--ui-radius)*2)] last:rounded-r-[calc(var(--ui-radius)*2)] hover:z-1">
          <div class="flex items-center gap-2">
            <span class="text-2xl font-semibold text-(--ui-text-highlighted)">{{ totalUnits }}</span>
          </div>
        </UPageCard>

      </UPageGrid>

      <UDashboardToolbar>
        <template #left>
          <!-- NOTE: The `-ms-1` class is used to align with the `DashboardSidebarCollapse` button here. -->
          <HomeDateRangePicker v-model="range" class="-ms-1" />

          <HomePeriodSelect v-model="period" :range="range" />
        </template>
      </UDashboardToolbar>

      <!-- Keep existing chart and sales -->
      <HomeChart :period="period" :range="range" />

      <!-- Recent Payments - now uses real API data filtered by date range -->
      <HomeRecentPayments :range="range" />


    </template>
  </UDashboardPanel>
</template>
