<script setup lang="ts">
import * as z from 'zod'
import type { FormSubmitEvent } from '@nuxt/ui'

const schema = z.object({
  documentType: z.string().min(1, 'Please select a document type'),
  leaseId: z.string().min(1, 'Please select a lease'),
  grossValue: z.union([
    z.string().min(1, 'Please enter amount').refine((val) => !isNaN(Number(val)) && Number(val) > 0, 'Amount must be a positive number'),
    z.number().positive('Amount must be a positive number')
  ]),
  dueDate: z.string().min(1, 'Please enter due date'),
  description: z.string().optional(),
  invoiceFile: z.any().optional()
})

const open = ref(false)

type Schema = z.output<typeof schema>

const state = reactive<Partial<Schema>>({
  documentType: undefined,
  leaseId: undefined,
  grossValue: undefined,
  dueDate: undefined,
  description: undefined,
  invoiceFile: undefined
})

const invoiceFile = ref<File | null>(null)

const toast = useToast()
const pending = ref(false)

const refreshPayments = inject<() => Promise<void>>('refreshPayments')

const { getToken } = useAuth()
const token = await getToken()

// Document type options
const documentTypeOptions = [
  { label: 'Rent Invoice', value: 'Rent Invoice' },
  { label: 'Security Deposit', value: 'Security Deposit' },
  { label: 'Maintenance Fee', value: 'Maintenance Fee' },
  { label: 'Other', value: 'Other' }
]

// Fetch active leases
const { data: leasesData, pending: leasesPending } = await useFetch<any[]>('/api/leases/all', {
  default: () => [],
  server: false,
  headers: token ? {
    'Authorization': `Bearer ${token}`
  } : {}
})

// Create lease options with format: #{lease_id} + {unit_name}
const leaseOptions = computed(() => {
  if (!leasesData.value) return []

  return leasesData.value
    .filter((lease: any) => lease.is_active) // Only active leases
    .map((lease: any) => ({
      label: `#${lease.id} + ${lease.unit?.name || 'Unknown Unit'}`,
      value: lease.id.toString()
    }))
})

async function onSubmit(event: FormSubmitEvent<Schema>) {
  pending.value = true

  try {
    const token = getToken()

    // Find the selected lease to get tenant info
    const selectedLease = leasesData.value?.find((lease: any) =>
      lease.id.toString() === event.data.leaseId
    )

    // Create FormData for file upload if there's an invoice file
    if (invoiceFile.value) {
      const formData = new FormData()
      formData.append('documentType', event.data.documentType!)
      formData.append('grossValue', typeof event.data.grossValue === 'number' ? event.data.grossValue.toString() : event.data.grossValue!)
      formData.append('dueDate', event.data.dueDate!)
      formData.append('receiver', selectedLease?.user ? `${selectedLease.user.first_name} ${selectedLease.user.last_name}` : 'Unknown')
      formData.append('description', event.data.description || 'One-time payment')
      formData.append('leaseId', event.data.leaseId!)
      formData.append('invoiceFile', invoiceFile.value)

      const result = await $fetch('/api/payments/with-invoice', {
        method: 'POST',
        body: formData,
        headers: token ? {
          'Authorization': `Bearer ${token}`
        } : {}
      })

      toast.add({
        title: 'Payment created',
        description: `Payment #${result.id} for ${formatCurrency(result.grossValue)} has been created with invoice`,
        color: 'success'
      })
    } else {
      // Original logic for payments without invoice
      const paymentData = {
        documentType: event.data.documentType!,
        grossValue: typeof event.data.grossValue === 'number' ? event.data.grossValue : parseFloat(event.data.grossValue!),
        dueDate: event.data.dueDate,
        receiver: selectedLease?.user ? `${selectedLease.user.first_name} ${selectedLease.user.last_name}` : 'Unknown',
        description: event.data.description || 'One-time payment',
        leaseId: parseInt(event.data.leaseId!)
      }

      const result = await $fetch('/api/payments', {
        method: 'POST',
        body: paymentData,
        headers: token ? {
          'Authorization': `Bearer ${token}`
        } : {}
      })

      toast.add({
        title: 'Payment created',
        description: `Payment #${result.id} for ${formatCurrency(result.grossValue)} has been created`,
        color: 'success'
      })
    }

    open.value = false

    // Reset form
    Object.keys(state).forEach(key => {
      state[key as keyof Schema] = undefined
    })
    invoiceFile.value = null

    if (refreshPayments) {
      await refreshPayments()
    }

  } catch (error: any) {
    toast.add({
      title: 'Error',
      description: error.data?.detail || 'Failed to create payment',
      color: 'error'
    })
  } finally {
    pending.value = false
  }
}

// Helper function to format currency
function formatCurrency(amount: number) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}
</script>

<template>
  <UModal v-model:open="open" title="New Payment" description="Create a new one-time payment">
    <UButton label="Add Payment" icon="i-lucide-plus" />

    <template #body>
      <UForm
        :schema="schema"
        :state="state"
        class="space-y-4"
        @submit="onSubmit"
      >
        <UFormField label="Document Type" name="documentType" description="Select the type of payment">
          <USelect
            v-model="state.documentType"
            :items="documentTypeOptions"
            placeholder="Select document type..."
            class="w-full"
          />
        </UFormField>

        <UFormField label="Lease" name="leaseId" description="Select an active lease">
          <USelect
            v-model="state.leaseId"
            :items="leaseOptions"
            placeholder="Select lease..."
            :loading="leasesPending"
            class="w-full"
          />
        </UFormField>

        <UFormField label="Amount" name="grossValue" description="Payment amount in USD">
          <UInput
            v-model="state.grossValue"
            type="number"
            step="0.01"
            min="0"
            placeholder="0.00"
            class="w-full"
          />
        </UFormField>

        <UFormField label="Due Date" name="dueDate" description="When the payment is due">
          <UInput
            v-model="state.dueDate"
            type="date"
            class="w-full"
          />
        </UFormField>

        <UFormField label="Description" name="description" description="Optional description for the payment">
          <UTextarea
            v-model="state.description"
            placeholder="Payment description..."
            class="w-full"
            rows="3"
          />
        </UFormField>

        <UFormField label="Invoice File (Optional)" name="invoiceFile" description="Upload PDF invoice file">
          <div class="space-y-2">
            <input
              type="file"
              accept=".pdf"
              @change="(e) => invoiceFile = (e.target as HTMLInputElement).files?.[0] || null"
              class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
            <p v-if="invoiceFile" class="text-xs text-green-600">
              Selected: {{ invoiceFile.name }}
            </p>
          </div>
        </UFormField>

        <div class="flex justify-end gap-2">
          <UButton
            label="Cancel"
            color="neutral"
            variant="subtle"
            @click="open = false"
            :disabled="pending"
          />
          <UButton
            label="Create Payment"
            color="primary"
            variant="solid"
            type="submit"
            :loading="pending"
            :disabled="pending"
          />
        </div>
      </UForm>
    </template>
  </UModal>
</template>
