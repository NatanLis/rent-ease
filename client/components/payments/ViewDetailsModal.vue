<script setup lang="ts">
import type { Payment } from '~/data/payments'

interface Props {
  payment: Payment
  open: boolean
}

interface Emits {
  (e: 'close'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { getToken } = useAuth()
const token = await getToken()
const toast = useToast()

const isOpen = computed({
  get: () => props.open,
  set: (value) => {
    if (!value) {
      emit('close')
    }
  }
})

function formatCurrency(value: number) {
  return new Intl.NumberFormat('pl-PL', {
    style: 'currency',
    currency: 'PLN'
  }).format(value)
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString('pl-PL')
}

async function downloadInvoice() {
  if (!props.payment.invoiceFileUrl) {
    toast.add({
      title: 'Error',
      description: 'No invoice file attached',
      color: 'red'
    })
    return
  }

  try {
    const response = await fetch(props.payment.invoiceFileUrl, {
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
    a.download = props.payment.invoiceFileName || 'invoice.pdf'
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
</script>

<template>
  <UModal v-model:open="isOpen" title="Payment Details" :description="`Details for payment #${payment.id}`">
    <template #body>
      <div class="space-y-6">
        <!-- Basic Information -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Payment ID</label>
            <div class="text-sm">#{{ payment.id }}</div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Created Date</label>
            <div class="text-sm">{{ formatDate(payment.createdAt) }}</div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Document Type</label>
            <div class="text-sm">{{ payment.documentType }}</div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Amount</label>
            <div class="text-sm font-semibold">{{ formatCurrency(payment.grossValue) }}</div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
            <div class="text-sm">{{ formatDate(payment.dueDate) }}</div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Receiver</label>
            <div class="text-sm">{{ payment.receiver }}</div>
          </div>
        </div>

        <!-- Status -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <UBadge
            :color="payment.status === 'Paid' ? 'success' : payment.status === 'Pending' ? 'warning' : 'error'"
            variant="subtle"
            class="capitalize"
          >
            {{ payment.status }}
          </UBadge>
        </div>

        <!-- Description -->
        <div v-if="payment.description">
          <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <div class="text-sm p-3 rounded-md">{{ payment.description }}</div>
        </div>

        <!-- Lease Information -->
        <div v-if="payment.lease" class="border-t pt-4">
          <h4 class="text-lg font-medium mb-3">Lease Information</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Tenant</label>
              <div class="text-sm">
                {{ payment.lease.user.first_name }} {{ payment.lease.user.last_name }}
              </div>
              <div class="text-xs text-gray-500">{{ payment.lease.user.email }}</div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Unit</label>
              <div class="text-sm">{{ payment.lease.unit.name }}</div>
              <div class="text-xs text-gray-500">Monthly rent: {{ formatCurrency(payment.lease.unit.monthly_rent) }}</div>
            </div>

            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Property</label>
              <div class="text-sm">{{ payment.lease.unit.property.title }}</div>
              <div class="text-xs text-gray-500">{{ payment.lease.unit.property.address }}</div>
            </div>
          </div>
        </div>

        <!-- Invoice Information -->
        <div v-if="payment.invoiceFileUrl" class="border-t pt-4">
          <h4 class="text-lg font-medium mb-3">Invoice</h4>
          <div class="bg-green-50 border border-green-200 rounded-lg p-4">
            <div class="flex items-center justify-between">
              <div>
                <div class="text-sm font-medium text-green-900">
                  {{ payment.invoiceFileName || 'Invoice.pdf' }}
                </div>
                <div class="text-xs text-green-700">
                  Invoice file attached
                </div>
              </div>
              <UButton
                icon="i-lucide-download"
                label="Download"
                variant="subtle"
                @click="downloadInvoice"
              />
            </div>
          </div>
        </div>
        <div v-else class="border-t pt-4">
          <h4 class="text-lg font-medium mb-3">Invoice</h4>
          <div class="border border-gray-200 rounded-lg p-4">
            <div class="text-sm text-center">
              No invoice file attached
            </div>
          </div>
        </div>

        <!-- Close Button -->
        <div class="flex justify-end pt-4">
          <UButton
            label="Close"
            color="neutral"
            variant="subtle"
            @click="isOpen = false"
          />
        </div>
      </div>
    </template>
  </UModal>
</template>
