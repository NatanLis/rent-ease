<script setup lang="ts">
import type { Payment } from '~/data/payments'

interface Props {
  payment: Payment
  open: boolean
}

interface Emits {
  (e: 'close'): void
  (e: 'updated'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { getToken } = useAuth()
const toast = useToast()

const isOpen = computed({
  get: () => props.open,
  set: (value) => {
    if (!value) {
      emit('close')
    }
  }
})

const invoiceFile = ref<File | null>(null)
const uploading = ref(false)

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  invoiceFile.value = input.files?.[0] || null
}

async function attachInvoice() {
  if (!invoiceFile.value) return

  uploading.value = true

  try {
    const token = getToken()
    const formData = new FormData()
    formData.append('invoiceFile', invoiceFile.value)

    await $fetch(`/api/payments/${props.payment.id}/attach-invoice`, {
      method: 'POST',
      body: formData,
      headers: token ? {
        'Authorization': `Bearer ${token}`
      } : {}
    })

    toast.add({
      title: 'Invoice attached',
      description: 'Invoice has been successfully attached to the payment',
      color: 'success'
    })

    isOpen.value = false
    invoiceFile.value = null
    emit('updated')

  } catch (error: any) {
    console.error('Error attaching invoice:', error)
    toast.add({
      title: 'Error attaching invoice',
      description: error.data?.detail || error.message || 'Unknown error',
      color: 'error'
    })
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <UModal v-model:open="isOpen" title="Attach Invoice" :description="`Attach invoice to payment #${payment.id}`">
    <template #body>
      <div class="space-y-4">
        <div class="bg-gray-50 p-4 rounded-lg">
          <h4 class="text-sm font-medium text-gray-900 mb-2">Payment Details</h4>
          <div class="text-sm text-gray-600 space-y-1">
            <p><strong>ID:</strong> #{{ payment.id }}</p>
            <p><strong>Type:</strong> {{ payment.documentType }}</p>
            <p><strong>Amount:</strong> {{ new Intl.NumberFormat('pl-PL', { style: 'currency', currency: 'PLN' }).format(payment.grossValue) }}</p>
            <p><strong>Receiver:</strong> {{ payment.receiver }}</p>
          </div>
        </div>

        <div class="space-y-2">
          <label class="block text-sm font-medium text-gray-700">
            Select PDF Invoice File
          </label>
          <div class="relative">
            <input
              type="file"
              accept=".pdf"
              @change="onFileChange"
              class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
            />
            <div class="flex items-center justify-between p-3 border border-gray-300 rounded-lg bg-white hover:bg-gray-50 transition-colors">
              <span class="text-sm text-gray-500">
                {{ invoiceFile ? invoiceFile.name : 'Choose PDF file...' }}
              </span>
              <button type="button" class="px-4 py-2 bg-blue-50 text-blue-700 rounded-full text-sm font-semibold hover:bg-blue-100 pointer-events-none">
                Browse
              </button>
            </div>
          </div>
          <p v-if="invoiceFile" class="text-xs text-green-600">
            Selected: {{ invoiceFile.name }}
          </p>
        </div>

        <div class="flex justify-end gap-2 pt-4">
          <UButton
            label="Cancel"
            color="neutral"
            variant="subtle"
            @click="isOpen = false"
            :disabled="uploading"
          />
          <UButton
            label="Attach Invoice"
            color="primary"
            variant="solid"
            @click="attachInvoice"
            :loading="uploading"
            :disabled="!invoiceFile || uploading"
          />
        </div>
      </div>
    </template>
  </UModal>
</template>
