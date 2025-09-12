<script setup lang="ts">
import * as z from 'zod'
import type { FormSubmitEvent } from '@nuxt/ui'

// Property interface definition
interface Property {
  id: number
  title: string
  description: string | null
  address: string
  price: number
  owner_id: number
  units_count: number
  active_leases: number
}

// Props definition
interface Props {
  property: Property | null
  open: boolean
}

// Emits definition
interface Emits {
  (e: 'update:open', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// Form validation schema definition
const schema = z.object({
  title: z.string().min(2, 'Title too short'),
  description: z.string().optional(),
  address: z.string().min(5, 'Address too short'),
  price: z.number().min(1, 'Price must be greater than 0')
})

type Schema = z.output<typeof schema>

// Form state
const state = reactive<Partial<Schema>>({
  title: undefined,
  description: undefined,
  address: undefined,
  price: undefined
})

const toast = useToast()
const pending = ref(false)

// Refresh properties function from parent component
const refreshProperties = inject<() => Promise<void>>('refreshProperties')

const { getToken } = useAuth()

// Computed for modal open state
const isOpen = computed({
  get: () => props.open,
  set: (value: boolean) => emit('update:open', value)
})

// Watch for property changes to update form state
watch(
  () => props.property,
  (newProperty) => {
    if (newProperty) {
      state.title = newProperty.title
      state.description = newProperty.description || ''
      state.address = newProperty.address
      state.price = newProperty.price
    }
  },
  { immediate: true }
)

// Form submit handler
async function onSubmit(event: FormSubmitEvent<Schema>) {
  if (!props.property) return

  console.log('Edit form submitted with data:', event.data)
  pending.value = true

  try {
    const token = getToken()
    console.log('Token:', token ? 'Present' : 'Missing')

    const response = await $fetch(`/api/properties/${props.property.id}`, {
      method: 'PATCH',
      body: event.data,
      headers: token ? {
        'Authorization': `Bearer ${token}`
      } : {}
    })

    console.log('API Response:', response)

    toast.add({
      title: 'Success',
      description: `Property "${event.data.title}" has been updated`,
      color: 'success'
    })

    isOpen.value = false

    // Refresh properties list
    if (refreshProperties) {
      await refreshProperties()
    }

  } catch (error: any) {
    console.error('Error updating property:', error)
    toast.add({
      title: 'Error',
      description: error.data?.detail || 'Failed to update property',
      color: 'error'
    })
  } finally {
    pending.value = false
  }
}

// Handle modal close
function handleClose() {
  isOpen.value = false
}
</script>

<template>
  <UModal
    v-model:open="isOpen"
    title="Edit Property"
    description="Update property information"
  >
    <template #body>
      <UForm
        :schema="schema"
        :state="state"
        class="space-y-4"
        @submit="onSubmit"
      >
        <UFormField label="Title" placeholder="2-room apartment" name="title">
          <UInput v-model="state.title" class="w-full" />
        </UFormField>

        <UFormField label="Address" placeholder="123 Example Street, Warsaw" name="address">
          <UInput v-model="state.address" class="w-full" />
        </UFormField>

        <UFormField label="Price (PLN/month)" placeholder="2500" name="price">
          <UInput
            v-model.number="state.price"
            type="number"
            class="w-full"
            min="0"
            step="0.01"
          />
        </UFormField>

        <UFormField label="Description (optional)" placeholder="Property description..." name="description">
          <UTextarea v-model="state.description" class="w-full" rows="3" />
        </UFormField>

        <div class="flex justify-end gap-2">
          <UButton
            label="Cancel"
            color="neutral"
            variant="subtle"
            @click="handleClose"
            :disabled="pending"
          />
          <UButton
            label="Update"
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
