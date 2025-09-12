<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import { upperFirst } from 'scule'
import { getPaginationRowModel, type Row } from '@tanstack/table-core'
import RecurringPaymentModal from '~/components/leases/RecurringPaymentModal.vue'

const UButton = resolveComponent('UButton')
const UBadge = resolveComponent('UBadge')
const UDropdownMenu = resolveComponent('UDropdownMenu')
const UCheckbox = resolveComponent('UCheckbox')
const UAvatar = resolveComponent('UAvatar')
const UIcon = resolveComponent('UIcon')

const toast = useToast()
const table = useTemplateRef('table')

// Define lease type based on backend LeaseResponse
interface Lease {
  id: number
  unit_id: number
  tenant_id: number
  start_date: string
  end_date: string | null
  is_active: boolean
  user: {
    id: number
    email: string
    first_name: string
    last_name: string
    avatar_url?: string
  }
  unit: {
    id: number
    name: string
    monthly_rent: number
    property: {
      id: number
      title: string
      address: string
    }
  }
}

const columnFilters = ref([{
  id: 'tenantEmail',
  value: ''
}])
const columnVisibility = ref()
const rowSelection = ref({})

const { getToken } = useAuth()
const token = await getToken()

const route = useRoute()

// Use reactive data instead of useFetch
const data = ref<Lease[]>([])
const status = ref<'pending' | 'error' | 'success'>('pending')

// Recurring payment modal state
const isRecurringPaymentModalOpen = ref(false)
const selectedLeaseForRecurringPayment = ref<Lease | null>(null)

// Property filter from URL parameter
const propertyFilter = ref<string | null>(null)
// Unit filter from URL parameter
const unitFilter = ref<string | null>(null)
// Unit data for displaying unit name when filtering by unit
const unitData = ref<{ id: number; name: string; property: { title: string } } | null>(null)

// Check for property filter in URL
onMounted(async () => {
  if (route.query.propertyId) {
    propertyFilter.value = route.query.propertyId as string
  }
  if (route.query.unitId) {
    unitFilter.value = route.query.unitId as string
    await fetchUnitData(unitFilter.value)
  }
  refreshLeases()
})

// Watch for route changes
watch(() => route.query.propertyId, (newPropertyId) => {
  propertyFilter.value = newPropertyId as string || null
})

watch(() => route.query.unitId, async (newUnitId) => {
  unitFilter.value = newUnitId as string || null
  if (newUnitId) {
    await fetchUnitData(newUnitId as string)
  } else {
    unitData.value = null
  }
})

// Computed filtered data
const filteredData = computed(() => {
  let result = dataWithTenantEmail.value

  // Filter by property if propertyFilter is set
  if (propertyFilter.value) {
    result = result.filter(lease => lease.unit?.property?.id.toString() === propertyFilter.value)
  }

  // Filter by unit if unitFilter is set
  if (unitFilter.value) {
    result = result.filter(lease => lease.unit_id.toString() === unitFilter.value)
  }

  return result
})

// Get property name for better UX
const propertyName = computed(() => {
  if (!propertyFilter.value || filteredData.value.length === 0) return null
  return filteredData.value[0]?.unit?.property?.title
})

// Get unit name for better UX
const unitName = computed(() => {
  if (!unitFilter.value) return null
  // Try to get from fetched unit data first
  if (unitData.value) {
    return unitData.value.name
  }
  // Fallback to filteredData if available
  if (filteredData.value.length > 0) {
    return filteredData.value[0]?.unit?.name
  }
  return null
})

// Function to clear property filter
function clearPropertyFilter() {
  propertyFilter.value = null
  navigateTo('/home/leases')
}

// Function to clear unit filter
function clearUnitFilter() {
  unitFilter.value = null
  unitData.value = null
  navigateTo('/home/leases')
}

// Add computed property for tenant email filtering
const dataWithTenantEmail = computed(() => {
  return data.value.map(lease => ({
    ...lease,
    tenantEmail: lease.user?.email || 'unknown@example.com'
  }))
})

// Get user role to determine which endpoint to use
const { getUser } = useUser()
const user = getUser()

// Use different endpoints based on user role
const endpoint = user?.isAdmin() ? '/api/leases/all' : '/api/leases/owner'

// Function to end a lease
async function endLease(lease: Lease) {
  try {
    const token = getToken()

    // Prepare the lease end data according to backend schema
    const endData = {
      unit_id: lease.unit_id,
      tenant_id: lease.tenant_id,
      start_date: lease.start_date,
      end_date: new Date().toISOString().split('T')[0] // Current date in YYYY-MM-DD format
    }

    await $fetch(`/api/leases/${lease.id}/end`, {
      method: 'PATCH',
      headers: token ? {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      } : {
        'Content-Type': 'application/json'
      },
      body: endData
    })

    toast.add({
      title: 'Success',
      description: `Lease for ${lease.user?.first_name} ${lease.user?.last_name} has been ended.`,
      color: 'success'
    })

    // Refresh the leases data
    await refreshLeases()

  } catch (error: any) {
    console.error('Error ending lease:', error)

    let errorMessage = 'Failed to end lease'
    if (error.data?.detail) {
      errorMessage = error.data.detail
    }

    toast.add({
      title: 'Error',
      description: errorMessage,
      color: 'error'
    })
  }
}

// Function to activate a lease
async function activateLease(lease: Lease) {
  try {
    const token = getToken()

    await $fetch(`/api/leases/${lease.id}/activate`, {
      method: 'PATCH',
      headers: token ? {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      } : {
        'Content-Type': 'application/json'
      }
    })

    toast.add({
      title: 'Success',
      description: `Lease for ${lease.user?.first_name} ${lease.user?.last_name} has been activated.`,
      color: 'success'
    })

    // Refresh the leases data
    await refreshLeases()

  } catch (error: any) {
    console.error('Error activating lease:', error)

    let errorMessage = 'Failed to activate lease'
    if (error.data?.detail) {
      errorMessage = error.data.detail
    }

    toast.add({
      title: 'Error',
      description: errorMessage,
      color: 'error'
    })
  }
}

// Function to refresh leases data
async function refreshLeases() {
  try {
    status.value = 'pending'
    const result = await $fetch<Lease[]>(endpoint, {
      headers: token ? {
        'Authorization': `Bearer ${token}`
      } : {}
    })
    data.value = result
    status.value = 'success'
  } catch (error) {
    status.value = 'error'
  }
}

// Provide refresh function for child components
provide('refreshLeases', refreshLeases)

// Function to fetch unit data when filtering by unit
async function fetchUnitData(unitId: string) {
  try {
    const result = await $fetch(`/api/units/${unitId}`, {
      headers: token ? {
        'Authorization': `Bearer ${token}`
      } : {}
    })
    unitData.value = result
  } catch (error) {
    console.error('Error fetching unit data:', error)
    unitData.value = null
  }
}

// Computed property to get selected active leases
const selectedActiveLeases = computed(() => {
  if (!table?.value?.tableApi) return []

  const selectedRows = table.value.tableApi.getFilteredSelectedRowModel().rows
  return selectedRows.filter(row => row.original.is_active)
})

// Function to end multiple leases
async function endSelectedLeases() {
  const activeLeases = selectedActiveLeases.value

  if (activeLeases.length === 0) {
    toast.add({
      title: 'No active leases selected',
      description: 'Please select at least one active lease to end.',
      color: 'warning'
    })
    return
  }

  try {
    // End all selected active leases
    const promises = activeLeases.map(row => {
      const lease = row.original
      const endData = {
        unit_id: lease.unit_id,
        tenant_id: lease.tenant_id,
        start_date: lease.start_date,
        end_date: new Date().toISOString().split('T')[0] // Current date in YYYY-MM-DD format
      }

      return $fetch(`/api/leases/${lease.id}/end`, {
        method: 'PATCH',
        headers: token ? {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        } : {
          'Content-Type': 'application/json'
        },
        body: endData
      })
    })

    await Promise.all(promises)

    toast.add({
      title: 'Success',
      description: `${activeLeases.length} lease(s) have been ended.`,
      color: 'success'
    })

    // Clear selection and refresh data
    table.value?.tableApi?.resetRowSelection()
    await refreshLeases()

  } catch (error: any) {
    console.error('Error ending leases:', error)

    let errorMessage = 'Failed to end some leases'
    if (error.data?.detail) {
      errorMessage = error.data.detail
    }

    toast.add({
      title: 'Error',
      description: errorMessage,
      color: 'error'
    })
  }
}

// Recurring payment modal functions
function openRecurringPaymentModal(lease: Lease) {
  selectedLeaseForRecurringPayment.value = lease
  isRecurringPaymentModalOpen.value = true
}

function closeRecurringPaymentModal() {
  isRecurringPaymentModalOpen.value = false
  selectedLeaseForRecurringPayment.value = null
}

async function handleRecurringPaymentSuccess(response: any) {
  toast.add({
    title: 'Payments Created',
    description: `Created ${response.paymentsCreated} payments for lease`,
    color: 'success'
  })

  // Refresh data if needed
  await refreshLeases()
}

function getRowItems(row: Row<Lease>) {
  const isLeaseActive = row.original.is_active

  return [
    {
      type: 'label',
      label: 'Actions'
    },
    {
      label: 'View payments',
      icon: 'i-lucide-wallet',
      onSelect() {
        navigateTo(`/home/payments?leaseId=${row.original.id}`)
      }
    },
    ...(isLeaseActive ? [{
      label: 'Create recurring payments',
      icon: 'i-lucide-calendar-plus',
      color: 'primary',
      onSelect() {
        openRecurringPaymentModal(row.original)
      }
    }] : []),
    {
      type: 'separator'
    },
    {
      label: isLeaseActive ? 'End lease' : 'Activate lease',
      icon: isLeaseActive ? 'i-lucide-calendar-x' : 'i-lucide-calendar-check',
      color: isLeaseActive ? 'warning' : 'success',
      onSelect() {
        if (isLeaseActive) {
          endLease(row.original)
        } else {
          activateLease(row.original)
        }
      }
    }
  ]
}

const columns: TableColumn<Lease>[] = [
  {
    id: 'select',
    header: ({ table }) =>
      h(UCheckbox, {
        'modelValue': table.getIsSomePageRowsSelected()
          ? 'indeterminate'
          : table.getIsAllPageRowsSelected(),
        'onUpdate:modelValue': (value: boolean | 'indeterminate') =>
          table.toggleAllPageRowsSelected(!!value),
        'ariaLabel': 'Select all'
      }),
    cell: ({ row }) =>
      h(UCheckbox, {
        'modelValue': row.getIsSelected(),
        'onUpdate:modelValue': (value: boolean | 'indeterminate') => row.toggleSelected(!!value),
        'ariaLabel': 'Select row'
      })
  },
  {
    accessorKey: 'id',
    header: 'ID'
  },
  {
    accessorKey: 'tenantEmail',
    header: ({ column }) => {
      const isSorted = column.getIsSorted()

      return h(UButton, {
        color: 'neutral',
        variant: 'ghost',
        label: 'Tenant',
        icon: isSorted
          ? isSorted === 'asc'
            ? 'i-lucide-arrow-up-narrow-wide'
            : 'i-lucide-arrow-down-wide-narrow'
          : 'i-lucide-arrow-up-down',
        class: '-mx-2.5',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc')
      })
    },
    cell: ({ row }) => {
      const user = row.original.user
      if (!user) {
        return h('div', { class: 'flex items-center gap-3' }, [
          h(UAvatar, {
            src: 'https://ui-avatars.com/api/?name=Unknown+User',
            alt: 'Unknown User',
            size: 'lg'
          }),
          h('div', undefined, [
            h('p', { class: 'font-medium text-(--ui-text-highlighted)' }, 'Unknown User'),
            h('p', { class: 'text-sm text-(--ui-text-muted)' }, 'No user data')
          ])
        ])
      }

      return h('div', { class: 'flex items-center gap-3' }, [
        h(UAvatar, {
          src: user.avatar_url || `https://ui-avatars.com/api/?name=${user.first_name}+${user.last_name}`,
          alt: `${user.first_name} ${user.last_name}`,
          size: 'lg'
        }),
        h('div', undefined, [
          h('p', { class: 'font-medium text-(--ui-text-highlighted)' }, `${user.first_name} ${user.last_name}`),
          h('p', { class: 'text-sm text-(--ui-text-muted)' }, user.email)
        ])
      ])
    }
  },
  {
    accessorKey: 'unit.property.title',
    header: 'Property',
    cell: ({ row }) => {
      const property = row.original.unit?.property
      if (!property) {
        return h('div', undefined, [
          h('p', { class: 'font-medium text-(--ui-text-highlighted)' }, 'Unknown Property'),
          h('p', { class: 'text-sm text-(--ui-text-muted)' }, 'No property data')
        ])
      }

      return h('div', undefined, [
        h('p', { class: 'font-medium text-(--ui-text-highlighted)' }, property.title),
        h('p', { class: 'text-sm text-(--ui-text-muted)' }, property.address)
      ])
    }
  },
  {
    accessorKey: 'unit.name',
    header: 'Unit',
    cell: ({ row }) => {
      return row.original.unit?.name || 'Unknown Unit'
    }
  },
  {
    accessorKey: 'start_date',
    header: ({ column }) => {
      const isSorted = column.getIsSorted()

      return h(UButton, {
        color: 'neutral',
        variant: 'ghost',
        label: 'Start Date',
        icon: isSorted
          ? isSorted === 'asc'
            ? 'i-lucide-arrow-up-narrow-wide'
            : 'i-lucide-arrow-down-wide-narrow'
          : 'i-lucide-arrow-up-down',
        class: '-mx-2.5',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc')
      })
    },
    cell: ({ row }) => {
      const date = new Date(row.original.start_date)
      return date.toLocaleDateString('pl-PL')
    }
  },
  {
    accessorKey: 'end_date',
    header: ({ column }) => {
      const isSorted = column.getIsSorted()

      return h(UButton, {
        color: 'neutral',
        variant: 'ghost',
        label: 'End Date',
        icon: isSorted
          ? isSorted === 'asc'
            ? 'i-lucide-arrow-up-narrow-wide'
            : 'i-lucide-arrow-down-wide-narrow'
          : 'i-lucide-arrow-up-down',
        class: '-mx-2.5',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc')
      })
    },
    cell: ({ row }) => {
      if (!row.original.end_date) return 'Ongoing'
      const date = new Date(row.original.end_date)
      return date.toLocaleDateString('pl-PL')
    }
  },
  {
    accessorKey: 'is_active',
    header: 'Status',
    filterFn: 'equals',
    cell: ({ row }) => {
      const status = row.original.is_active ? 'active' : 'inactive'
      const color = {
        active: 'success' as const,
        inactive: 'error' as const
      }[status] || 'neutral'

      const displayStatus = {
        active: 'Active',
        inactive: 'Inactive'
      }[status] || status

      return h(UBadge, { class: 'capitalize', variant: 'subtle', color }, () =>
        displayStatus
      )
    }
  },
  {
    id: 'actions',
    cell: ({ row }) => {
      return h(
        'div',
        { class: 'text-right' },
        h(
          UDropdownMenu,
          {
            content: {
              align: 'end'
            },
            items: getRowItems(row)
          },
          () =>
            h(UButton, {
              icon: 'i-lucide-ellipsis-vertical',
              color: 'neutral',
              variant: 'ghost',
              class: 'ml-auto'
            })
        )
      )
    }
  }
]

const statusFilter = ref('all')

watch(() => statusFilter.value, (newVal) => {
  if (!table?.value?.tableApi) return

  const statusColumn = table.value.tableApi.getColumn('is_active')
  if (!statusColumn) return

  if (newVal === 'all') {
    statusColumn.setFilterValue(undefined)
  } else {
    statusColumn.setFilterValue(newVal === 'active')
  }
})

const pagination = ref({
  pageIndex: 0,
  pageSize: 10
})

definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})
</script>

<template>
  <UDashboardPanel id="leases">
    <template #header>
      <UDashboardNavbar :title="unitFilter ? 'Unit Leases' : propertyFilter ? 'Property Leases' : 'Leases'">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <div class="flex items-center gap-2">
            <UButton
              v-if="propertyFilter || unitFilter"
              label="Show All Leases"
              color="neutral"
              variant="ghost"
              icon="i-lucide-x"
              @click="propertyFilter ? clearPropertyFilter() : clearUnitFilter()"
            />
            <LeasesAddModal />
          </div>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <!-- Filter info -->
      <div v-if="propertyFilter" class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <UIcon name="i-lucide-filter" class="text-blue-600" />
            <span class="text-sm text-blue-800">
              Showing leases for property: <strong>{{ propertyName || `#${propertyFilter}` }}</strong>
            </span>
          </div>
          <div class="flex items-center gap-2">
            <UButton
              size="xs"
              color="blue"
              variant="soft"
              icon="i-lucide-building"
              @click="navigateTo(`/home/properties?propertyId=${propertyFilter}`)"
            >
              View Property
            </UButton>
            <UButton
              size="xs"
              color="blue"
              variant="ghost"
              icon="i-lucide-x"
              @click="clearPropertyFilter"
            >
              Clear
            </UButton>
          </div>
        </div>
      </div>

      <!-- Unit Filter info -->
      <div v-if="unitFilter" class="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <UIcon name="i-lucide-filter" class="text-green-600" />
            <span class="text-sm text-green-800">
              Showing leases for unit: <strong>{{ unitName || `#${unitFilter}` }}</strong>
            </span>
          </div>
          <div class="flex items-center gap-2">
            <UButton
              size="xs"
              color="green"
              variant="soft"
              icon="i-lucide-home"
              @click="navigateTo('/home/units')"
            >
              View Units
            </UButton>
            <UButton
              size="xs"
              color="green"
              variant="ghost"
              icon="i-lucide-x"
              @click="clearUnitFilter"
            >
              Clear
            </UButton>
          </div>
        </div>
      </div>

      <div class="flex flex-wrap items-center justify-between gap-1.5">
        <UInput
          :model-value="(table?.tableApi?.getColumn('tenantEmail')?.getFilterValue() as string)"
          class="max-w-sm"
          icon="i-lucide-search"
          placeholder="Filter tenants..."
          @update:model-value="table?.tableApi?.getColumn('tenantEmail')?.setFilterValue($event)"
        />

        <div class="flex flex-wrap items-center gap-1.5">
          <UButton
            v-if="table?.tableApi?.getFilteredSelectedRowModel().rows.length"
            label="End Selected"
            color="warning"
            variant="subtle"
            icon="i-lucide-calendar-x"
            :disabled="selectedActiveLeases.length === 0"
            @click="endSelectedLeases"
          >
            <template #trailing>
              <UKbd>
                {{ selectedActiveLeases.length }} / {{ table?.tableApi?.getFilteredSelectedRowModel().rows.length }}
              </UKbd>
            </template>
          </UButton>

          <USelect
            v-model="statusFilter"
            :items="[
              { label: 'All', value: 'all' },
              { label: 'Active', value: 'active' },
              { label: 'Inactive', value: 'inactive' }
            ]"
            :ui="{ trailingIcon: 'group-data-[state=open]:rotate-180 transition-transform duration-200' }"
            placeholder="Filter status"
            class="min-w-28"
          />
          <UDropdownMenu
            :items="
              table?.tableApi
                ?.getAllColumns()
                .filter((column) => column.getCanHide())
                .map((column) => ({
                  label: upperFirst(column.id),
                  type: 'checkbox' as const,
                  checked: column.getIsVisible(),
                  onUpdateChecked(checked: boolean) {
                    table?.tableApi?.getColumn(column.id)?.toggleVisibility(!!checked)
                  },
                  onSelect(e?: Event) {
                    e?.preventDefault()
                  }
                })) || []
            "
            :content="{ align: 'end' }"
          >
            <UButton
              label="Display"
              color="neutral"
              variant="outline"
              trailing-icon="i-lucide-settings-2"
            />
          </UDropdownMenu>
        </div>
      </div>

      <UTable
        ref="table"
        v-model:column-filters="columnFilters"
        v-model:column-visibility="columnVisibility"
        v-model:row-selection="rowSelection"
        v-model:pagination="pagination"
        :pagination-options="{
          getPaginationRowModel: getPaginationRowModel()
        }"
        class="shrink-0"
        :data="filteredData"
        :columns="columns"
        :loading="status === 'pending'"
        :ui="{
          base: 'table-fixed border-separate border-spacing-0',
          thead: '[&>tr]:bg-(--ui-bg-elevated)/50 [&>tr]:after:content-none',
          tbody: '[&>tr]:last:[&>td]:border-b-0',
          th: 'py-1 first:rounded-l-[calc(var(--ui-radius)*2)] last:rounded-r-[calc(var(--ui-radius)*2)] border-y border-(--ui-border) first:border-l last:border-r',
          td: 'border-b border-(--ui-border)'
        }"
      />

      <div class="flex items-center justify-between gap-3 border-t border-(--ui-border) pt-4 mt-auto">
        <div class="text-sm text-(--ui-text-muted)">
          {{ table?.tableApi?.getFilteredSelectedRowModel().rows.length || 0 }} of
          {{ table?.tableApi?.getFilteredRowModel().rows.length || 0 }} row(s) selected.
        </div>

        <div class="flex items-center gap-1.5">
          <UPagination
            :default-page="(table?.tableApi?.getState().pagination.pageIndex || 0) + 1"
            :items-per-page="table?.tableApi?.getState().pagination.pageSize"
            :total="table?.tableApi?.getFilteredRowModel().rows.length"
            @update:page="(p) => table?.tableApi?.setPageIndex(p - 1)"
          />
        </div>
      </div>
    </template>
  </UDashboardPanel>

  <!-- Recurring Payment Modal -->
  <RecurringPaymentModal
    :is-open="isRecurringPaymentModalOpen"
    :lease-id="selectedLeaseForRecurringPayment?.id || 0"
    :lease-data="selectedLeaseForRecurringPayment ? {
      start_date: selectedLeaseForRecurringPayment.start_date,
      end_date: selectedLeaseForRecurringPayment.end_date,
      unit: {
        monthly_rent: selectedLeaseForRecurringPayment.unit?.monthly_rent || 0
      }
    } : undefined"
    @close="closeRecurringPaymentModal"
    @success="handleRecurringPaymentSuccess"
  />
</template>
