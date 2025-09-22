<script setup lang="ts">
import * as z from 'zod'
import type { FormSubmitEvent } from '@nuxt/ui'
import type { RecurringPaymentCreate, RecurringPaymentResponse } from '~/data/payments'

interface Props {
  isOpen: boolean
  leaseId: number
  leaseData?: {
    start_date: string
    end_date?: string
    unit?: {
      monthly_rent: number
    }
  }
}

interface Emits {
  (e: 'close'): void
  (e: 'success', response: RecurringPaymentResponse): void
}

const schema = z.object({
  documentType: z.string().min(1, 'Document type is required'),
  amount: z.union([
    z.string().transform(val => parseFloat(val)).refine(val => !isNaN(val) && val > 0, 'Amount must be greater than 0'),
    z.number().refine(val => val > 0, 'Amount must be greater than 0')
  ]),
  frequency: z.enum(['monthly', 'quarterly', 'yearly']),
  dueDay: z.number().min(1).max(31),
  description: z.string().optional()
})

type Schema = z.output<typeof schema>

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { getToken } = useAuth()
const toast = useToast()

// Modal open state - computed to handle v-model properly
const isOpen = computed({
  get: () => props.isOpen,
  set: (value) => {
    if (!value) {
      emit('close')
    }
  }
})

// Form state
const state = reactive({
  documentType: 'Rent Invoice',
  amount: '',
  frequency: 'monthly' as 'monthly' | 'quarterly' | 'yearly',
  dueDay: 1,
  description: ''
})

const pending = ref(false)

// Options
const documentTypeOptions = [
  { label: 'Rent Invoice', value: 'Rent Invoice' },
  { label: 'Security Deposit', value: 'Security Deposit' },
  { label: 'Maintenance Fee', value: 'Maintenance Fee' },
  { label: 'Other', value: 'Other' }
]

const frequencyOptions = [
  { label: 'Monthly', value: 'monthly' },
  { label: 'Quarterly', value: 'quarterly' },
  { label: 'Yearly', value: 'yearly' }
]

const dueDayOptions = Array.from({ length: 31 }, (_, i) => ({
  label: (i + 1).toString(),
  value: i + 1
}))

// Auto-fill amount with monthly rent if available and document type is Rent Invoice
watch(() => state.documentType, (newType) => {
  if (newType === 'Rent Invoice' && props.leaseData?.unit?.monthly_rent && !state.amount) {
    state.amount = props.leaseData.unit.monthly_rent.toString()
  }
})

// Watch for lease data changes
watch(() => props.leaseData, (newLeaseData) => {
  if (newLeaseData?.unit?.monthly_rent && state.documentType === 'Rent Invoice' && !state.amount) {
    state.amount = newLeaseData.unit.monthly_rent.toString()
  }
}, { immediate: true })

// Form validation
const isButtonDisabled = computed(() => {
  return pending.value || !state.documentType || !state.amount || parseFloat(state.amount) <= 0 || !state.frequency || state.dueDay < 1 || state.dueDay > 31
})

// Preview calculations
const preview = computed(() => {
  if (isButtonDisabled.value || !props.leaseData || !state.amount) return null

  const startDate = new Date(props.leaseData.start_date)
  const endDate = props.leaseData.end_date ? new Date(props.leaseData.end_date) : new Date(Date.now() + 365 * 24 * 60 * 60 * 1000)

  const totalAmount = parseFloat(state.amount)

  // Calculate number of payments based on frequency
  const diffMonths = (endDate.getFullYear() - startDate.getFullYear()) * 12 + (endDate.getMonth() - startDate.getMonth())

  let paymentsCount = 0
  switch (state.frequency) {
    case 'monthly':
      paymentsCount = Math.ceil(diffMonths)
      break
    case 'quarterly':
      paymentsCount = Math.ceil(diffMonths / 3)
      break
    case 'yearly':
      paymentsCount = Math.ceil(diffMonths / 12)
      break
  }

  if (paymentsCount === 0) paymentsCount = 1

  const amountPerPayment = Math.round((totalAmount / paymentsCount) * 100) / 100
  const lastPaymentAmount = totalAmount - (amountPerPayment * (paymentsCount - 1))

  return {
    paymentsCount,
    amountPerPayment,
    lastPaymentAmount,
    startDate: startDate.toLocaleDateString('en-US'),
    endDate: endDate.toLocaleDateString('en-US')
  }
})

function onError(errors: any) {
  toast.add({
    title: 'Validation Error',
    description: 'Please check all required fields',
    color: 'error'
  })
}

// Submit handler
async function onSubmit(event: FormSubmitEvent<Schema>) {
  pending.value = true

  try {
    const token = getToken()

    const recurringPaymentData: RecurringPaymentCreate = {
      leaseId: props.leaseId,
      documentType: event.data.documentType,
      amount: event.data.amount,
      frequency: event.data.frequency,
      dueDay: event.data.dueDay,
      description: event.data.description || undefined
    }

    const response = await $fetch<RecurringPaymentResponse>('/api/payments/recurring', {
      method: 'POST',
      body: recurringPaymentData,
      headers: token ? {
        'Authorization': `Bearer ${token}`
      } : {}
    })

    toast.add({
      title: 'Success',
      description: `Created ${response.paymentsCreated} payments for total amount $${response.totalAmount}`,
      color: 'success'
    })

    // Reset form
    Object.assign(state, {
      documentType: 'Rent Invoice',
      amount: '',
      frequency: 'monthly',
      dueDay: 1,
      description: ''
    })

    emit('success', response)
    isOpen.value = false

  } catch (error: any) {
    console.error('Error creating recurring payments:', error)
    toast.add({
      title: 'Error',
      description: error.data?.detail || error.message || 'Failed to create recurring payments',
      color: 'error'
    })
  } finally {
    pending.value = false
  }
}

// Helper functions
function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'PLN'
  }).format(amount)
}

// Reset form when modal opens
watch(() => props.isOpen, (newIsOpen) => {
  if (newIsOpen) {
    // Auto-fill amount if available
    if (props.leaseData?.unit?.monthly_rent && state.documentType === 'Rent Invoice') {
      state.amount = props.leaseData.unit.monthly_rent.toString()
    }
  } else {
    // Reset form when modal closes
    Object.assign(state, {
      documentType: 'Rent Invoice',
      amount: '',
      frequency: 'monthly',
      dueDay: 1,
      description: ''
    })
  }
})
</script>

<template>
  <UModal v-model:open="isOpen" title="Create Recurring Payments" description="Set up recurring payments for the lease">
    <template #body>
      <UForm
        :schema="schema"
        :state="state"
        class="space-y-4"
        @submit="onSubmit"
        @error="onError"
      >
        <!-- Document Type -->
        <UFormField label="Document Type" name="documentType" required>
          <USelect
            v-model="state.documentType"
            :items="documentTypeOptions"
            placeholder="Select document type"
            class="w-full"
            :disabled="pending"
          />
        </UFormField>

        <!-- Amount -->
        <UFormField label="Total Amount ($)" name="amount" required>
          <UInput
            v-model="state.amount"
            type="number"
            step="0.01"
            min="0"
            placeholder="0.00"
            class="w-full"
            :disabled="pending"
          />
        </UFormField>

        <!-- Frequency -->
        <UFormField label="Payment Frequency" name="frequency" required>
          <USelect
            v-model="state.frequency"
            :items="frequencyOptions"
            placeholder="Select frequency"
            class="w-full"
            :disabled="pending"
          />
        </UFormField>

        <!-- Due Day -->
        <UFormField label="Due Day of Month" name="dueDay" required>
          <USelect
            v-model="state.dueDay"
            :items="dueDayOptions"
            placeholder="Select day of month"
            class="w-full"
            :disabled="pending"
          />
        </UFormField>

        <!-- Description -->
        <UFormField label="Description (optional)" name="description">
          <UTextarea
            v-model="state.description"
            placeholder="Additional payment description"
            class="w-full"
            :disabled="pending"
            rows="3"
          />
        </UFormField>

        <!-- Preview -->
        <div v-if="preview" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 class="text-sm font-medium text-blue-900 mb-2">Payment Preview</h4>
          <div class="text-sm text-blue-800 space-y-1">
            <p><strong>Number of payments:</strong> {{ preview.paymentsCount }}</p>
            <p><strong>Amount per payment:</strong> {{ formatCurrency(preview.amountPerPayment) }}</p>
            <p v-if="preview.lastPaymentAmount !== preview.amountPerPayment">
              <strong>Last payment:</strong> {{ formatCurrency(preview.lastPaymentAmount) }}
            </p>
            <p><strong>Period:</strong> {{ preview.startDate }} - {{ preview.endDate }}</p>
          </div>
        </div>

        <div class="flex justify-end gap-2">
          <UButton
            label="Cancel"
            color="neutral"
            variant="subtle"
            @click="isOpen = false"
            :disabled="pending"
          />
          <UButton
            label="Create Payments"
            color="primary"
            variant="solid"
            type="submit"
            :loading="pending"
            :disabled="isButtonDisabled"
          />
        </div>
      </UForm>
    </template>
  </UModal>
</template>
