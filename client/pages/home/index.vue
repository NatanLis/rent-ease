<script setup lang="ts">
import { sub } from 'date-fns'
import type { Period, Range } from '~/types'
import { h, resolveComponent } from 'vue'
import type { Payment } from '~/data/payments'
import { mockPayments } from '~/data/payments'

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

// Fetch real data for dashboard stats
const { data: properties } = await useFetch<any[]>('/api/properties', { default: () => [], server: false })
const { data: tenants } = await useFetch<any[]>('/api/tenants', { default: () => [], server: false })
const { data: leases } = await useFetch<any[]>('/api/leases', { default: () => [], server: false })

// Derived metrics
const totalProperties = computed(() => (properties.value || []).length)
const totalUnits = computed(() => (properties.value || []).reduce((sum: number, p: any) => sum + (p?.unitsCount || 0), 0))
const totalTenants = computed(() => (tenants.value || []).length)
const activeLeases = computed(() => (leases.value || []).filter((l: any) => l?.isActive === true || l?.status === 'active').length)

// Recent payments for dashboard (last 5 by createdAt)
const recentPayments = computed<Payment[]>(() => {
  return [...mockPayments]
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    .slice(0, 5)
})

const UBadge = resolveComponent('UBadge')
const formatPLN = new Intl.NumberFormat('pl-PL', { style: 'currency', currency: 'PLN' }).format
const formatDate = (dateString: string) => new Date(dateString).toLocaleDateString('pl-PL')
const statusColor = (status: Payment['status']) => ({ Paid: 'success', Pending: 'warning', Overdue: 'error' }[status] || 'neutral')

definePageMeta({
  layout: 'dashboard',
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

      <UDashboardToolbar>
        <template #left>
          <!-- NOTE: The `-ms-1` class is used to align with the `DashboardSidebarCollapse` button here. -->
          <HomeDateRangePicker v-model="range" class="-ms-1" />

          <HomePeriodSelect v-model="period" :range="range" />
        </template>
      </UDashboardToolbar>
    </template>

    <template #body>
      <!-- Real-time stats from project data -->
      <UPageGrid class="lg:grid-cols-4 gap-4 sm:gap-6 lg:gap-px mb-6">
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
      </UPageGrid>

      <!-- Keep existing chart and sales -->
      <HomeChart :period="period" :range="range" />

      <!-- Recent Payments from Payments page -->
      <UCard class="mt-6">
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold">Recent Payments</h3>
            <UButton to="/home/payments" color="primary" variant="soft" size="xs">View all</UButton>
          </div>
        </template>

        <UTable
          :data="recentPayments"
          :columns="[
            { accessorKey: 'id', header: 'ID', cell: ({ row }) => `#${row.original.id}` },
            { accessorKey: 'createdAt', header: 'Created', cell: ({ row }) => formatDate(row.original.createdAt) },
            { accessorKey: 'documentType', header: 'Type' },
            { accessorKey: 'grossValue', header: 'Amount', cell: ({ row }) => formatPLN(row.original.grossValue) },
            { accessorKey: 'receiver', header: 'Receiver' },
            { accessorKey: 'status', header: 'Status', cell: ({ row }) => h(UBadge, { variant: 'subtle', class: 'capitalize', color: statusColor(row.original.status) }, () => row.original.status) }
          ]
          "
        />
      </UCard>

      
    </template>
  </UDashboardPanel>
</template>
