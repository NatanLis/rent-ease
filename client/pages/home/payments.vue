<script setup lang="ts">
import { h } from 'vue'
import type { Payment } from '~/data/payments'
import { mockPayments } from '~/data/payments'

const UBadge = resolveComponent('UBadge')
const UButton = resolveComponent('UButton')
const UDropdownMenu = resolveComponent('UDropdownMenu')

// Load mock data - will be replaced with database connection later
const allPayments = ref<Payment[]>([...mockPayments])
const selectedStatus = ref('all')
const searchQuery = ref('')

// Function to automatically update payment status based on due date
function updatePaymentStatuses() {
  const today = new Date()
  today.setHours(0, 0, 0, 0) // Reset time to start of day for accurate comparison
  
  allPayments.value.forEach(payment => {
    const dueDate = new Date(payment.dueDate)
    dueDate.setHours(0, 0, 0, 0) // Reset time to start of day
    
    // Only update if payment is not already paid
    if (payment.status !== 'Paid') {
      if (dueDate < today) {
        payment.status = 'Overdue'
      } else if (payment.status === 'Overdue' && dueDate >= today) {
        // If it was overdue but now the due date is in the future, set back to pending
        payment.status = 'Pending'
      }
    }
  })
}

// Update statuses when component mounts
onMounted(() => {
  updatePaymentStatuses()
  
  // Optional: Update statuses every hour to catch overdue payments
  // Uncomment the line below if you want automatic hourly updates
  // setInterval(updatePaymentStatuses, 60 * 60 * 1000) // 1 hour
})


// Status filter options
const statusOptions = [
  { label: 'All Status', value: 'all' },
  { label: 'Paid', value: 'Paid' },
  { label: 'Pending', value: 'Pending' },
  { label: 'Overdue', value: 'Overdue' }
]

// Function to update selected status (not needed with USelect v-model)
function updateStatus(status: string) {
  selectedStatus.value = status
}

// Simple function to add new payment using prompts (like inbox)
function addPayment() {
  // For testing, let's create a simple payment first
  const testPayment: Payment = {
    id: Math.max(...allPayments.value.map(p => p.id)) + 1,
    createdAt: new Date().toISOString(),
    documentType: 'Test Invoice',
    grossValue: 100.00,
    dueDate: '2024-12-31',
    receiver: 'Test Receiver',
    property: 'Test Property',
    status: 'Pending',
    description: 'Test payment'
  }

  allPayments.value.unshift(testPayment)
  
  // Now try the prompts
  const documentType = prompt('Document Type (Invoice, Receipt, Contract, Statement, Other):')?.trim()
  if (!documentType) {
    return
  }

  const grossValue = prompt('Gross Value (PLN):')?.trim()
  if (!grossValue || isNaN(parseFloat(grossValue))) {
    alert('Please enter a valid number for gross value')
    return
  }

  const receiver = prompt('Receiver:')?.trim()
  if (!receiver) {
    return
  }

  const property = prompt('Property:')?.trim()
  if (!property) {
    return
  }

  const dueDate = prompt('Due Date (YYYY-MM-DD):')?.trim()
  if (!dueDate) {
    return
  }

  const description = prompt('Description (optional):')?.trim() || ''

  // Determine initial status based on due date
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const paymentDueDate = new Date(dueDate)
  paymentDueDate.setHours(0, 0, 0, 0)
  
  let initialStatus: 'Paid' | 'Pending' | 'Overdue' = 'Pending'
  if (paymentDueDate < today) {
    initialStatus = 'Overdue'
  }

  const payment: Payment = {
    id: Math.max(...allPayments.value.map(p => p.id)) + 1,
    createdAt: new Date().toISOString(),
    documentType,
    grossValue: parseFloat(grossValue),
    dueDate,
    receiver,
    property,
    status: initialStatus,
    description
  }

  allPayments.value.unshift(payment) // Add to beginning of array
}

// Function to update payment status
function updatePaymentStatus(paymentId: number, newStatus: 'Paid' | 'Pending' | 'Overdue') {
  const payment = allPayments.value.find(p => p.id === paymentId)
  if (payment) {
    payment.status = newStatus
  }
}

// Function to get dropdown menu items for each payment
function getPaymentActions(payment: Payment) {
  return [
    {
      type: 'label',
      label: 'Change Status'
    },
    {
      label: 'Mark as Paid',
      icon: 'i-lucide-check-circle',
      color: 'success',
      disabled: payment.status === 'Paid',
      onSelect: () => updatePaymentStatus(payment.id, 'Paid')
    },
    {
      label: 'Mark as Pending',
      icon: 'i-lucide-clock',
      color: 'warning',
      disabled: payment.status === 'Pending',
      onSelect: () => updatePaymentStatus(payment.id, 'Pending')
    },
    {
      label: 'Mark as Overdue',
      icon: 'i-lucide-alert-circle',
      color: 'error',
      disabled: payment.status === 'Overdue',
      onSelect: () => updatePaymentStatus(payment.id, 'Overdue')
    }
  ]
}

// Filtered payments based on selected status and search query (for table display)
const payments = computed(() => {
  let filtered = allPayments.value

  // Filter by status
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(payment => payment.status === selectedStatus.value)
  }

  // Filter by search query
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    filtered = filtered.filter(payment => 
      payment.receiver.toLowerCase().includes(query) ||
      payment.property.toLowerCase().includes(query) ||
      payment.documentType.toLowerCase().includes(query) ||
      payment.id.toString().includes(query)
    )
  }

  return filtered
})

// Summary statistics (always from all payments, not filtered)
const totalPayments = computed(() => allPayments.value.length)
const paidCount = computed(() => allPayments.value.filter(p => p.status === 'Paid').length)
const pendingCount = computed(() => allPayments.value.filter(p => p.status === 'Pending').length)
const overdueCount = computed(() => allPayments.value.filter(p => p.status === 'Overdue').length)

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
      <UDashboardNavbar title="Payments" :ui="{ right: 'gap-3' }">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <UButton 
            icon="i-lucide-plus"
            size="md"
            class="rounded-full"
            @click="addPayment"
          >
            Add Payment
          </UButton>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
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

        <!-- Payments Table -->
        <UCard>
          <template #header>
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold">Payment Records</h3>
              <div class="flex gap-2">
                <UInput
                  v-model="searchQuery"
                  icon="i-lucide-search"
                  placeholder="Search payments..."
                  class="w-64"
                />
                <USelect
                  v-model="selectedStatus"
                  :items="statusOptions"
                  placeholder="Filter by status"
                  class="w-48"
                />
              </div>
            </div>
          </template>

          <UTable 
            :data="payments" 
            :columns="[
              { accessorKey: 'id', header: 'ID' },
              { 
                accessorKey: 'createdAt', 
                header: 'Created',
                cell: ({ row }) => {
                  return h('span', {}, formatDate(row.original.createdAt))
                }
              },
              { accessorKey: 'documentType', header: 'Document Type' },
              { 
                accessorKey: 'grossValue', 
                header: 'Gross Value',
                cell: ({ row }) => {
                  return h('span', { class: 'font-semibold' }, formatCurrency(row.original.grossValue))
                }
              },
              { 
                accessorKey: 'dueDate', 
                header: 'Due Date',
                cell: ({ row }) => {
                  return h('span', {}, formatDate(row.original.dueDate))
                }
              },
              { accessorKey: 'receiver', header: 'Receiver' },
              { accessorKey: 'property', header: 'Property' },
              { 
                accessorKey: 'status', 
                header: 'Status',
                cell: ({ row }) => {
                  const color = {
                    'Paid': 'success' as const,
                    'Pending': 'warning' as const,
                    'Overdue': 'error' as const
                  }[row.original.status] || 'neutral'

                  return h(UBadge, { 
                    class: 'capitalize', 
                    variant: 'subtle', 
                    color 
                  }, () => row.original.status)
                }
              },
              {
                id: 'actions',
                header: 'Actions',
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
                        items: getPaymentActions(row.original)
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
            ]" 
          />
        </UCard>
      </div>
    </template>
  </UDashboardPanel>
</template>
