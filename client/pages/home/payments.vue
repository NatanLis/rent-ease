<script setup lang="ts">
import { h, watch } from 'vue'
import type { Payment } from '~/data/payments'
import { mockPayments } from '~/data/payments'

const UBadge = resolveComponent('UBadge')
const UButton = resolveComponent('UButton')
const UDropdownMenu = resolveComponent('UDropdownMenu')

// Load mock data - will be replaced with database connection later
const allPayments = ref<Payment[]>([...mockPayments])
const selectedStatus = ref('all')
const searchQuery = ref('')

// Add Payment form state
const isAddOpen = ref(false)
const documentTypeOptions = [
  { label: 'Rent Invoice', value: 'Rent Invoice' },
  { label: 'Security Deposit', value: 'Security Deposit' },
  { label: 'Maintenance Fee', value: 'Maintenance Fee' },
  { label: 'Other', value: 'Other' }
]

// Fetch tenants and leases to power selects and auto property mapping
const { data: tenants, pending: tenantsPending } = await useFetch<any[]>('/api/tenants', { default: () => [], server: false })
const { data: leasesData, pending: leasesPending } = await useFetch<any[]>('/api/leases', { default: () => [], server: false })
const { data: properties, pending: propertiesPending } = await useFetch<any[]>('/api/properties', { default: () => [], server: false })

const tenantOptions = computed(() => (tenants.value || []).map((t: any) => ({
  label: `${t.name} (${t.email})`,
  value: t.email,
  name: t.name
})))

const propertyOptions = computed(() => (properties.value || []).map((p: any) => ({
  label: p.title || p.propertyTitle || p.name,
  value: p.title || p.propertyTitle || p.name
})))

const newPayment = ref({
  documentType: '',
  receiverEmail: '',
  receiverName: '',
  property: '',
  grossValue: '',
  dueDate: '',
  description: ''
})

// Touched state for lazy validation
const touched = ref({
  documentType: false,
  receiverEmail: false,
  property: false,
  grossValue: false,
  dueDate: false,
  description: false
})
const submittedAttempt = ref(false)

function openAddPaymentForm() {
  isAddOpen.value = true
}

function cancelAddPayment() {
  isAddOpen.value = false
  newPayment.value = {
    documentType: '',
    receiverEmail: '',
    receiverName: '',
    property: '',
    grossValue: '',
    dueDate: '',
    description: ''
  }
}

// Auto-fill property based on selected tenant via active lease
watch(() => newPayment.value.receiverEmail, (email) => {
  if (!email) {
    newPayment.value.property = ''
    newPayment.value.receiverName = ''
    return
  }
  const tenant = (tenants.value || []).find((t: any) => t.email === email)
  newPayment.value.receiverName = tenant?.name || email
  const activeLease = (leasesData.value || []).find((l: any) => (l.tenantEmail === email) && (l.isActive === true || l.status === 'active'))
  newPayment.value.property = activeLease?.propertyTitle || ''
})

function submitAddPayment() {
  submittedAttempt.value = true
  if (!isFormValid.value) {
    toast.add({ title: 'Please fix the form errors', color: 'error' })
    return
  }

  const today = new Date(); today.setHours(0,0,0,0)
  const due = new Date(newPayment.value.dueDate); due.setHours(0,0,0,0)
  const status: 'Paid' | 'Pending' | 'Overdue' = due < today ? 'Overdue' : 'Pending'

  const payment: Payment = {
    id: Math.max(0, ...allPayments.value.map(p => p.id)) + 1,
    createdAt: new Date().toISOString(),
    documentType: newPayment.value.documentType,
    grossValue: parseFloat(newPayment.value.grossValue),
    dueDate: newPayment.value.dueDate,
    receiver: newPayment.value.receiverName || newPayment.value.receiverEmail,
    property: newPayment.value.property || 'Unknown',
    status,
    description: newPayment.value.description || ''
  }

  allPayments.value.unshift(payment)
  cancelAddPayment()
  toast.add({ title: 'Payment added', description: `#${payment.id} for ${formatCurrency(payment.grossValue)}`, color: 'success' })
  submittedAttempt.value = false
}

// Inline validation
const documentTypeError = computed(() => newPayment.value.documentType ? '' : 'Please select a document type')
const receiverEmailError = computed(() => newPayment.value.receiverEmail ? '' : 'Please select a tenant')
const propertyError = computed(() => newPayment.value.property ? '' : 'Select or auto-fill a property')
const grossValueError = computed(() => {
  const v = parseFloat(newPayment.value.grossValue)
  if (!newPayment.value.grossValue) return 'Enter an amount'
  if (Number.isNaN(v) || v <= 0) return 'Enter a valid amount > 0'
  return ''
})
const dueDateError = computed(() => newPayment.value.dueDate ? '' : 'Please select a due date')
const isSubmitting = ref(false)
const isFormValid = computed(() => !documentTypeError.value && !receiverEmailError.value && !propertyError.value && !grossValueError.value && !dueDateError.value)

const toast = useToast()

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
            @click="openAddPaymentForm"
          >
            Add Payment
          </UButton>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="space-y-6">
        <!-- Add Payment Inline Form -->
        <UCard v-if="isAddOpen">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="flex items-start gap-3">
              <label class="w-40 text-sm text-(--ui-text-muted) mt-2">Document type:</label>
              <div class="flex-1 space-y-1">
                <USelect v-model="newPayment.documentType" :items="documentTypeOptions" placeholder="Select type" class="w-full" @blur="touched.documentType = true" />
                <p v-if="(touched.documentType || submittedAttempt) && documentTypeError" class="text-xs text-red-500">{{ documentTypeError }}</p>
              </div>
            </div>

            <div class="flex items-start gap-3">
              <label class="w-40 text-sm text-(--ui-text-muted) mt-2">Receiver:</label>
              <div class="flex-1 space-y-1">
                <USelect v-model="newPayment.receiverEmail" :items="tenantOptions" :loading="tenantsPending" placeholder="Select tenant" class="w-full" @blur="touched.receiverEmail = true" />
                <p v-if="(touched.receiverEmail || submittedAttempt) && receiverEmailError" class="text-xs text-red-500">{{ receiverEmailError }}</p>
              </div>
            </div>

            <div class="flex items-start gap-3">
              <label class="w-40 text-sm text-(--ui-text-muted) mt-2">Property:</label>
              <div class="flex-1 space-y-1">
                <UInput v-model="newPayment.property" :disabled="!!newPayment.receiverEmail" placeholder="Auto-selected from active lease" class="w-full" @blur="touched.property = true" />
                <p v-if="(touched.property || submittedAttempt) && propertyError" class="text-xs text-red-500">{{ propertyError }}</p>
                <p v-if="!newPayment.property && newPayment.receiverEmail" class="text-xs text-(--ui-text-muted)">No active lease found. You can pick a property:</p>
                <USelect v-if="!newPayment.property && newPayment.receiverEmail" v-model="newPayment.property" :items="propertyOptions" :loading="propertiesPending" placeholder="Select property" class="w-full" @blur="touched.property = true" />
              </div>
            </div>

            <div class="flex items-start gap-3">
              <label class="w-40 text-sm text-(--ui-text-muted) mt-2">Gross value (PLN):</label>
              <div class="flex-1 space-y-1">
                <UInput v-model="newPayment.grossValue" type="number" step="0.01" placeholder="0.00" class="w-full" @blur="touched.grossValue = true" />
                <p v-if="(touched.grossValue || submittedAttempt) && grossValueError" class="text-xs text-red-500">{{ grossValueError }}</p>
              </div>
            </div>

            <div class="flex items-start gap-3">
              <label class="w-40 text-sm text-(--ui-text-muted) mt-2">Due date:</label>
              <div class="flex-1 space-y-1">
                <UInput v-model="newPayment.dueDate" type="date" class="w-full" @blur="touched.dueDate = true" />
                <p v-if="(touched.dueDate || submittedAttempt) && dueDateError" class="text-xs text-red-500">{{ dueDateError }}</p>
              </div>
            </div>

            <div class="flex items-center gap-3">
              <label class="w-40 text-sm text-(--ui-text-muted)">Description:</label>
              <UInput v-model="newPayment.description" placeholder="Optional description" class="flex-1" />
            </div>
          </div>

          <template #footer>
            <div class="flex justify-end gap-2">
              <UButton color="neutral" variant="ghost" @click="cancelAddPayment">Cancel</UButton>
              <UButton color="primary" @click="submitAddPayment" :disabled="!isFormValid || tenantsPending || leasesPending || propertiesPending">Add</UButton>
            </div>
          </template>
        </UCard>

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
