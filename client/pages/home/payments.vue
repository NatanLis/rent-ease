<script setup lang="ts">
import { h, watch } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import { upperFirst } from 'scule'
import { getPaginationRowModel, type Row } from '@tanstack/table-core'
import type { Payment } from '~/data/payments'

const UBadge = resolveComponent('UBadge')
const UButton = resolveComponent('UButton')
const UDropdownMenu = resolveComponent('UDropdownMenu')
const UCheckbox = resolveComponent('UCheckbox')

const toast = useToast()
const table = useTemplateRef('table')

const { getToken } = useAuth()
const token = await getToken()

const route = useRoute()

// Modal states
const selectedPaymentForAttach = ref<Payment | null>(null)
const showAttachInvoiceModal = ref(false)
const selectedPaymentForDetails = ref<Payment | null>(null)
const showDetailsModal = ref(false)

// Lease filter from URL parameter
const leaseFilter = ref<string | null>(null)
// Lease data for displaying lease info when filtering by lease
const leaseData = ref<any | null>(null)

// Tenant filter from URL parameter
const tenantFilter = ref<string | null>(null)
// Tenant data for displaying tenant info when filtering by tenant
const tenantData = ref<any | null>(null)

// Table state
const columnFilters = ref([{
  id: 'receiver',
  value: ''
}])
const columnVisibility = ref()
const rowSelection = ref({})
const pagination = ref({
  pageIndex: 0,
  pageSize: 10
})

// Load payments from API - with support for filtering by lease or tenant
const allPayments = ref<Payment[]>([])

// Computed URL for payments API based on filters
const paymentsApiUrl = computed(() => {
  if (leaseFilter.value) {
    return `/api/payments/lease/${leaseFilter.value}`
  }
  if (tenantFilter.value) {
    return `/api/payments/tenant/${tenantFilter.value}`
  }
  return '/api/payments'
})

// Fetch payments data
const { data: paymentsData, pending: paymentsPending, refresh: refreshPayments } = await useFetch<Payment[]>(paymentsApiUrl, {
  default: () => [],
  server: false,
  headers: token ? {
    'Authorization': `Bearer ${token}`
  } : {}
})

// Watch for data changes and update local payments
watch(paymentsData, (newPayments) => {
  if (newPayments) {
    allPayments.value = [...newPayments]
  }
}, { immediate: true })

// Watch for filter changes and refresh data
watch([leaseFilter, tenantFilter], async () => {
  await refreshPayments()
})

// Provide refresh function for child components
provide('refreshPayments', refreshPayments)

const selectedStatus = ref('all')

// Check for lease filter in URL
onMounted(async () => {
  if (route.query.leaseId) {
    leaseFilter.value = route.query.leaseId as string
    await fetchLeaseData(leaseFilter.value)
  }
  if (route.query.tenantId) {
    tenantFilter.value = route.query.tenantId as string
    await fetchTenantData(tenantFilter.value)
  }
})

// Watch for route changes
watch(() => route.query.leaseId, async (newLeaseId) => {
  leaseFilter.value = newLeaseId as string || null
  if (newLeaseId) {
    await fetchLeaseData(newLeaseId as string)
  } else {
    leaseData.value = null
  }
})

watch(() => route.query.tenantId, async (newTenantId) => {
  tenantFilter.value = newTenantId as string || null
  if (newTenantId) {
    await fetchTenantData(newTenantId as string)
  } else {
    tenantData.value = null
  }
})

// Function to fetch lease data when filtering by lease
async function fetchLeaseData(leaseId: string) {
  try {
    const result = await $fetch(`/api/leases/${leaseId}`, {
      headers: token ? {
        'Authorization': `Bearer ${token}`
      } : {}
    })
    leaseData.value = result
  } catch (error) {
    console.error('Error fetching lease data:', error)
    leaseData.value = null
  }
}

// Function to fetch tenant data when filtering by tenant
async function fetchTenantData(tenantId: string) {
  try {
    const result = await $fetch(`/api/tenants/${tenantId}`, {
      headers: token ? {
        'Authorization': `Bearer ${token}`
      } : {}
    })
    tenantData.value = result
  } catch (error) {
    console.error('Error fetching tenant data:', error)
    tenantData.value = null
  }
}

// Function to clear lease filter
function clearLeaseFilter() {
  leaseFilter.value = null
  leaseData.value = null
  navigateTo('/home/payments')
}

// Function to clear tenant filter
function clearTenantFilter() {
  tenantFilter.value = null
  tenantData.value = null
  navigateTo('/home/payments')
}

// Backend now handles status calculation automatically

// No longer needed - backend calculates status automatically
// Update statuses when component mounts
// onMounted(() => {
//   updatePaymentStatuses()
// })


// Status filter options
const statusOptions = [
  { label: 'All Status', value: 'all' },
  { label: 'Paid', value: 'Paid' },
  { label: 'Pending', value: 'Pending' },
  { label: 'Overdue', value: 'Overdue' }
]

// Function to mark payment as paid
async function markPaymentAsPaid(paymentId: number) {
  try {
    await $fetch(`/api/payments/${paymentId}/mark-paid`, {
      method: 'PATCH',
      headers: token ? {
        'Authorization': `Bearer ${token}`
      } : {}
    })

    // Refresh the payments list to get updated data
    await refreshPayments()

    toast.add({
      title: 'Payment status updated',
      description: 'Payment marked as paid',
      color: 'success'
    })
  } catch (error: any) {
    console.error('Error marking payment as paid:', error)
    toast.add({
      title: 'Error updating payment status',
      description: error.data?.detail || error.message || 'Unknown error',
      color: 'error'
    })
  }
}

// Function to mark payment as unpaid
async function markPaymentAsUnpaid(paymentId: number) {
  try {
    await $fetch(`/api/payments/${paymentId}/mark-unpaid`, {
      method: 'PATCH',
      headers: token ? {
        'Authorization': `Bearer ${token}`
      } : {}
    })

    // Refresh the payments list to get updated data
    await refreshPayments()

    toast.add({
      title: 'Payment status updated',
      description: 'Payment marked as unpaid',
      color: 'success'
    })
  } catch (error: any) {
    console.error('Error marking payment as unpaid:', error)
    toast.add({
      title: 'Error updating payment status',
      description: error.data?.detail || error.message || 'Unknown error',
      color: 'error'
    })
  }
}

//...existing code

// Function to open attach invoice modal
function openAttachInvoiceModal(payment: Payment) {
  selectedPaymentForAttach.value = payment
  showAttachInvoiceModal.value = true
}

// Function to open payment details modal
function openDetailsModal(payment: Payment) {
  selectedPaymentForDetails.value = payment
  showDetailsModal.value = true
}

// Function to close attach invoice modal
function closeAttachInvoiceModal() {
  selectedPaymentForAttach.value = null
  showAttachInvoiceModal.value = false
}

// Function to close details modal
function closeDetailsModal() {
  selectedPaymentForDetails.value = null
  showDetailsModal.value = false
}

// Function to download invoice file with authentication
async function downloadInvoiceFile(payment: Payment) {
  if (!payment.invoiceFileUrl) {
    toast.add({
      title: 'Error',
      description: 'No invoice file attached',
      color: 'red'
    })
    return
  }

  try {
    const response = await fetch(payment.invoiceFileUrl, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('Failed to download file')
    }

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.style.display = 'none'
    a.href = url
    a.download = payment.invoiceFileName || 'invoice.pdf'
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (error) {
    console.error('Error downloading invoice:', error)
    toast.add({
      title: 'Error',
      description: 'Failed to download invoice file',
      color: 'red'
    })
  }
}

// Function to handle invoice attachment success
async function onInvoiceAttached() {
  await refreshPayments()
  closeAttachInvoiceModal()
}

// Function to get dropdown menu items for each payment
function getRowItems(row: Row<Payment>) {
  const payment = row.original
  const items = [
    {
      type: 'label',
      label: 'Actions'
    },
    {
      label: 'View Details',
      icon: 'i-lucide-eye',
      color: 'blue',
      onSelect: () => openDetailsModal(payment)
    }
  ]

  // Add attach invoice option if no invoice is attached
  if (!payment.invoiceFileUrl) {
    items.push({
      label: 'Attach Invoice',
      icon: 'i-lucide-paperclip',
      color: 'green',
      onSelect: () => openAttachInvoiceModal(payment)
    })
  }

  items.push(
    {
      type: 'separator'
    },
    {
      type: 'label',
      label: 'Change Status'
    }
  )

  // Add appropriate status change option based on current status
  if (payment.isPaid) {
    items.push({
      label: 'Mark as Unpaid',
      icon: 'i-lucide-x-circle',
      color: 'warning',
      onSelect: () => markPaymentAsUnpaid(payment.id)
    })
  } else {
    // For 'Pending' or 'Overdue' status, allow marking as paid
    items.push({
      label: 'Mark as Paid',
      icon: 'i-lucide-check-circle',
      color: 'success',
      onSelect: () => markPaymentAsPaid(payment.id)
    })
  }

  items.push(
    {
      type: 'separator'
    },
    {
      label: 'Delete payment',
      icon: 'i-lucide-trash',
      color: 'error',
      async onSelect() {
        try {
          await $fetch(`/api/payments/${payment.id}`, {
            method: 'DELETE',
            headers: token ? {
              'Authorization': `Bearer ${token}`
            } : {}
          })

          // Refresh the payments list
          await refreshPayments()

          toast.add({
            title: 'Payment deleted',
            description: `Payment #${payment.id} has been deleted.`,
            color: 'success'
          })
        } catch (error: any) {
          console.error('Error deleting payment:', error)
          toast.add({
            title: 'Error deleting payment',
            description: error.data?.detail || error.message || 'Unknown error',
            color: 'error'
          })
        }
      }
    }
  )

  return items
}

// Filtered payments based on selected status and search query (for table display)
const payments = computed(() => {
  let filtered = allPayments.value

  // Filter by lease if leaseFilter is set
  if (leaseFilter.value) {
    filtered = filtered.filter(payment => payment.lease?.id.toString() === leaseFilter.value)
  }

  // Filter by tenant if tenantFilter is set
  if (tenantFilter.value) {
    filtered = filtered.filter(payment =>
      payment.lease?.tenant_id.toString() === tenantFilter.value ||
      payment.lease?.user?.id.toString() === tenantFilter.value
    )
  }

  // Filter by status
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(payment => payment.status === selectedStatus.value)
  }

  return filtered
})

// Table columns definition
const columns: TableColumn<Payment>[] = [
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
      }),
    size: 40
  },
  {
    accessorKey: 'id',
    header: 'ID',
    size: 80
  },
  {
    accessorKey: 'createdAt',
    header: ({ column }) => {
      const isSorted = column.getIsSorted()

      return h(UButton, {
        color: 'neutral',
        variant: 'ghost',
        label: 'Created',
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
      return h('span', {}, formatDate(row.original.createdAt))
    }
  },
  {
    accessorKey: 'documentType',
    header: 'Document Type',
    size: 150
  },
  {
    accessorKey: 'grossValue',
    header: ({ column }) => {
      const isSorted = column.getIsSorted()

      return h(UButton, {
        color: 'neutral',
        variant: 'ghost',
        label: 'Gross Value',
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
      return h('span', { class: 'font-semibold' }, formatCurrency(row.original.grossValue))
    }
  },
  {
    accessorKey: 'dueDate',
    header: ({ column }) => {
      const isSorted = column.getIsSorted()

      return h(UButton, {
        color: 'neutral',
        variant: 'ghost',
        label: 'Due Date',
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
      return h('span', {}, formatDate(row.original.dueDate))
    }
  },
  {
    accessorKey: 'receiver',
    header: ({ column }) => {
      const isSorted = column.getIsSorted()

      return h(UButton, {
        color: 'neutral',
        variant: 'ghost',
        label: 'Receiver',
        icon: isSorted
          ? isSorted === 'asc'
            ? 'i-lucide-arrow-up-narrow-wide'
            : 'i-lucide-arrow-down-wide-narrow'
          : 'i-lucide-arrow-up-down',
        class: '-mx-2.5',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc')
      })
    }
  },
  {
    accessorKey: 'lease.unit.name',
    header: 'Unit',
    cell: ({ row }) => {
      const unitName = row.original.lease?.unit?.name || 'N/A'
      const propertyTitle = row.original.lease?.unit?.property?.title || ''

      return h('div', { class: 'flex flex-col' }, [
        h('span', { class: 'font-medium' }, unitName),
        h('span', { class: 'text-xs text-(--ui-text-muted)' }, propertyTitle)
      ])
    }
  },
  {
    accessorKey: 'status',
    header: 'Status',
    filterFn: 'equals',
    cell: ({ row }) => {
      const color = {
        Paid: 'success' as const,
        Pending: 'warning' as const,
        Overdue: 'error' as const
      }[row.original.status] || 'neutral'

      return h(UBadge, { class: 'capitalize', variant: 'subtle', color }, () =>
        row.original.status
      )
    }
  },
  {
    accessorKey: 'invoiceFileUrl',
    header: 'Invoice',
    size: 80,
    cell: ({ row }) => {
      const hasInvoice = !!row.original.invoiceFileUrl

      return h('div', { class: 'flex items-center justify-center' }, [
        hasInvoice ?
          h(UButton, {
            icon: 'i-lucide-file-text',
            color: 'success',
            variant: 'ghost',
            size: 'sm',
            title: 'View Invoice',
            onClick: () => downloadInvoiceFile(row.original)
          }) :
          h('span', {
            class: 'text-xs text-gray-400',
            title: 'No invoice attached'
          }, '—')
      ])
    }
  },
  {
    id: 'actions',
    size: 80,
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

// Status filter watcher
const statusFilter = ref('all')

watch(() => statusFilter.value, (newVal) => {
  if (!table?.value?.tableApi) return

  const statusColumn = table.value.tableApi.getColumn('status')
  if (!statusColumn) return

  if (newVal === 'all') {
    statusColumn.setFilterValue(undefined)
  } else {
    statusColumn.setFilterValue(newVal)
  }
})

// Function to delete selected payments
async function deleteSelectedPayments() {
  const selectedRows = table?.value?.tableApi?.getFilteredSelectedRowModel().rows || []
  const selectedIds = selectedRows.map(row => row.original.id)

  if (selectedIds.length === 0) {
    return
  }

  try {
    // Delete payments one by one (backend doesn't have bulk delete endpoint)
    await Promise.all(selectedIds.map(id =>
      $fetch(`/api/payments/${id}`, {
        method: 'DELETE',
        headers: token ? {
          'Authorization': `Bearer ${token}`
        } : {}
      })
    ))

    // Refresh the payments list
    await refreshPayments()

    // Clear selection
    rowSelection.value = {}

    toast.add({
      title: 'Payments deleted',
      description: `${selectedIds.length} payment(s) have been deleted.`,
      color: 'success'
    })
  } catch (error: any) {
    console.error('Error deleting payments:', error)
    toast.add({
      title: 'Error deleting payments',
      description: error.data?.detail || error.message || 'Unknown error',
      color: 'error'
    })
  }
}

// Summary statistics (always from all payments, not filtered)
// Fetch payment statistics from API
const { data: statisticsData, pending: statisticsPending } = await useFetch<any>('/api/payments/statistics', {
  default: () => ({ total: 0, paid: 0, pending: 0, overdue: 0 }),
  server: false,
  headers: token ? {
    'Authorization': `Bearer ${token}`
  } : {}
})

const totalPayments = computed(() => statisticsData.value?.total || allPayments.value.length)
const paidCount = computed(() => statisticsData.value?.paid || allPayments.value.filter(p => p.status === 'Paid').length)
const pendingCount = computed(() => statisticsData.value?.pending || allPayments.value.filter(p => p.status === 'Pending').length)
const overdueCount = computed(() => statisticsData.value?.overdue || allPayments.value.filter(p => p.status === 'Overdue').length)

const getStatusColor = (status: string) => {
  switch (status) {
    case 'Paid':
      return 'green'
    case 'Pending':
      return 'yellow'
    case 'Overdue':
      return 'red'
    default:
      return 'gray'
  }
}

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pl-PL', {
    style: 'currency',
    currency: 'PLN'
  }).format(value)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('pl-PL')
}

definePageMeta({
  layout: 'dashboard',
})
</script>

<template>
  <UDashboardPanel id="payments">
    <template #header>
      <UDashboardNavbar :title="tenantFilter ? 'Tenant Payments' : leaseFilter ? 'Lease Payments' : 'Payments'" :ui="{ right: 'gap-3' }">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <div class="flex items-center gap-2">
            <UButton
              v-if="leaseFilter || tenantFilter"
              label="Show All Payments"
              color="neutral"
              variant="ghost"
              icon="i-lucide-x"
              @click="leaseFilter ? clearLeaseFilter() : clearTenantFilter()"
            />
            <PaymentsAddModal />
          </div>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <!-- Lease Filter info -->
      <div v-if="leaseFilter" class="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <UIcon name="i-lucide-filter" class="text-green-600" />
            <span class="text-sm text-green-800">
              Showing payments for lease: <strong>{{ leaseData?.unit?.name || `#${leaseFilter}` }}</strong>
              <span v-if="leaseData?.unit?.property?.title" class="text-green-600">
                - {{ leaseData.unit.property.title }}
              </span>
            </span>
          </div>
          <div class="flex items-center gap-2">
            <UButton
              size="xs"
              color="green"
              variant="soft"
              icon="i-lucide-file-text"
              @click="navigateTo(`/home/leases?unitId=${leaseData?.unit_id}`)"
            >
              View Lease
            </UButton>
            <UButton
              size="xs"
              color="green"
              variant="ghost"
              icon="i-lucide-x"
              @click="clearLeaseFilter"
            >
              Clear
            </UButton>
          </div>
        </div>
      </div>

      <!-- Tenant Filter info -->
      <div v-if="tenantFilter" class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <UIcon name="i-lucide-filter" class="text-blue-600" />
            <span class="text-sm text-blue-800">
              Showing payments for tenant: <strong>{{ tenantData?.name || `#${tenantFilter}` }}</strong>
              <span v-if="tenantData?.email" class="text-blue-600">
                - {{ tenantData.email }}
              </span>
            </span>
          </div>
          <div class="flex items-center gap-2">
            <UButton
              size="xs"
              color="blue"
              variant="soft"
              icon="i-lucide-user"
              @click="navigateTo('/home/tenants')"
            >
              View Tenants
            </UButton>
            <UButton
              size="xs"
              color="blue"
              variant="ghost"
              icon="i-lucide-x"
              @click="clearTenantFilter"
            >
              Clear
            </UButton>
          </div>
        </div>
      </div>

      <div class="space-y-6">
        <!-- Summary Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <UCard>
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500">Total Payments</p>
                <p class="text-2xl font-bold">{{ totalPayments }}</p>
              </div>
              <UIcon name="i-lucide-credit-card" class="w-8 h-8 text-blue-500" />
            </div>
          </UCard>

          <UCard>
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500">Paid</p>
                <p class="text-2xl font-bold text-green-600">
                  {{ paidCount }}
                </p>
              </div>
              <UIcon name="i-lucide-check-circle" class="w-8 h-8 text-green-500" />
            </div>
          </UCard>

          <UCard>
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500">Pending</p>
                <p class="text-2xl font-bold text-yellow-600">
                  {{ pendingCount }}
                </p>
              </div>
              <UIcon name="i-lucide-clock" class="w-8 h-8 text-yellow-500" />
            </div>
          </UCard>

          <UCard>
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500">Overdue</p>
                <p class="text-2xl font-bold text-red-600">
                  {{ overdueCount }}
                </p>
              </div>
              <UIcon name="i-lucide-alert-circle" class="w-8 h-8 text-red-500" />
            </div>
          </UCard>
        </div>

        <!-- Filters and Table -->
        <div class="flex flex-wrap items-center justify-between gap-1.5">
          <UInput
            :model-value="(table?.tableApi?.getColumn('receiver')?.getFilterValue() as string)"
            class="max-w-sm"
            icon="i-lucide-search"
            placeholder="Filter receivers..."
            @update:model-value="table?.tableApi?.getColumn('receiver')?.setFilterValue($event)"
          />

          <div class="flex flex-wrap items-center gap-1.5">
            <UButton
              v-if="table?.tableApi?.getFilteredSelectedRowModel().rows.length"
              label="Delete"
              color="error"
              variant="subtle"
              icon="i-lucide-trash"
              @click="deleteSelectedPayments"
            >
              <template #trailing>
                <UKbd>
                  {{ table?.tableApi?.getFilteredSelectedRowModel().rows.length }}
                </UKbd>
              </template>
            </UButton>

            <USelect
              v-model="statusFilter"
              :items="[
                { label: 'All', value: 'all' },
                { label: 'Paid', value: 'Paid' },
                { label: 'Pending', value: 'Pending' },
                { label: 'Overdue', value: 'Overdue' }
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
          :data="payments"
          :columns="columns"
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
      </div>

      <!-- Modals -->
      <PaymentsAttachInvoiceModal
        v-if="selectedPaymentForAttach"
        :payment="selectedPaymentForAttach"
        :open="showAttachInvoiceModal"
        @close="closeAttachInvoiceModal"
        @updated="onInvoiceAttached"
      />

      <PaymentsViewDetailsModal
        v-if="selectedPaymentForDetails"
        :payment="selectedPaymentForDetails"
        :open="showDetailsModal"
        @close="closeDetailsModal"
      />
    </template>
  </UDashboardPanel>
</template>
