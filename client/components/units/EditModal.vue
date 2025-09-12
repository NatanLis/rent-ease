<script setup lang="ts">
import * as z from 'zod'
import type { FormSubmitEvent } from '@nuxt/ui'

// Unit interface matching the main component
interface Unit {
  id: number
  propertyId: number
  name: string
  description: string | null
  monthlyRent: number
  propertyTitle: string
  propertyAddress: string
  activeLeases: number
  status: 'occupied' | 'available' | 'maintenance'
}

// Property interface for dropdown
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

// Props
interface Props {
  open: boolean
  unit: Unit | null
}

// Emits
interface Emits {
  (e: 'update:open', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// Form validation schema
const schema = z.object({
  property_id: z.string().min(1, 'Please select a property').transform(val => parseInt(val)),
  name: z.string().min(1, 'Unit name is required'),
  description: z.string().optional(),
  monthly_rent: z.number().min(0, 'Monthly rent must be non-negative')
})

type Schema = z.output<typeof schema>

// Form state
const state = reactive({
  property_id: '' as string,
  name: '',
  description: '',
  monthly_rent: 0
})

// Properties data for dropdown
const properties = ref<Property[]>([])
const loadingProperties = ref(false)
const pending = ref(false)

// API utilities
const toast = useToast()
const { getToken } = useAuth()

// Computed for modal state
const isOpen = computed({
  get: () => props.open,
  set: (value) => emit('update:open', value)
})

// Status options - removed since status is calculated automatically
// const statusOptions = [
//   { label: 'Available', value: 'available' },
//   { label: 'Occupied', value: 'occupied' },
//   { label: 'Maintenance', value: 'maintenance' }
// ]

// Fetch properties from API for dropdown
async function fetchProperties() {
  loadingProperties.value = true
  try {
    const token = getToken()
    const response = await $fetch('/api/properties/', {
      method: 'GET',
      headers: token ? {
        'Authorization': `Bearer ${token}`
      } : {}
    })
    properties.value = response
  } catch (error) {
    console.error('Error fetching properties:', error)
    toast.add({
      title: 'Error',
      description: 'Failed to load properties',
      color: 'error'
    })
  } finally {
    loadingProperties.value = false
  }
}

// Load properties when modal opens
watch(() => props.open, async (isOpen) => {
  if (isOpen) {
    if (properties.value.length === 0) {
      await fetchProperties()
    }
  } else {
    // Reset form when closing modal
    state.property_id = ''
    state.name = ''
    state.description = ''
    state.monthly_rent = 0
  }
})

// Property options for dropdown
const propertyOptions = computed(() => {
  if (!properties.value || properties.value.length === 0) {
    return []
  }

  return properties.value.map(p => ({
    label: p.title,
    value: p.id.toString() // Convert to string
  }))
})

// Set unit data when properties are loaded
watch([propertyOptions, () => props.unit], ([options, unit]) => {
  if (options.length > 0 && unit && !state.property_id) {
    state.property_id = unit.propertyId.toString() // Convert to string
    state.name = unit.name
    state.description = unit.description || ''
    state.monthly_rent = unit.monthlyRent
  }
}, { immediate: true })

// Get refresh function from parent
const refreshUnits = inject('refreshUnits') as (() => Promise<void>) | undefined

// Form submission handler
async function onSubmit(event: FormSubmitEvent<Schema>) {
  if (!props.unit) return

  pending.value = true
  try {
    const token = getToken()
    await $fetch(`/api/units/${props.unit.id}`, {
      method: 'PATCH',
      body: {
        property_id: event.data.property_id,
        name: event.data.name,
        description: event.data.description || null,
        monthly_rent: event.data.monthly_rent
        // Note: status is calculated automatically by backend
      },
      headers: token ? {
        'Authorization': `Bearer ${token}`
      } : {}
    })

    toast.add({
      title: 'Success',
      description: `Unit "${event.data.name}" updated successfully`,
      color: 'success'
    })

    // Close modal
    isOpen.value = false

    // Refresh units list
    if (refreshUnits) {
      await refreshUnits()
    }

  } catch (error: any) {
    console.error('Error updating unit:', error)
    toast.add({
      title: 'Error',
      description: error.data?.detail || 'Failed to update unit',
      color: 'error'
    })
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <UModal
    v-model:open="isOpen"
    title="Edit Unit"
    description="Update unit information"
  >
    <template #body>
      <UForm
        v-if="unit"
        :schema="schema"
        :state="state"
        class="space-y-4"
        @submit="onSubmit"
      >
        <!-- Property Selection -->
        <UFormField label="Property" name="property_id" required>
          <USelect
            v-model="state.property_id"
            :items="propertyOptions"
            placeholder="Select a property..."
            class="w-full"
            :disabled="loadingProperties"
          />
        </UFormField>

        <!-- Unit Name -->
        <UFormField label="Unit Name" name="name" required>
          <UInput v-model="state.name" placeholder="e.g., Unit 1A" class="w-full" />
        </UFormField>

        <!-- Description -->
        <UFormField label="Description (optional)" name="description">
          <UTextarea
            v-model="state.description"
            placeholder="Optional unit description..."
            :rows="3"
            class="w-full"
          />
        </UFormField>

        <!-- Monthly Rent -->
        <UFormField label="Monthly Rent (PLN/month)" name="monthly_rent" required>
          <UInput
            v-model.number="state.monthly_rent"
            type="number"
            step="0.01"
            min="0"
            placeholder="0.00"
            class="w-full"
          />
        </UFormField>

        <!-- Actions -->
        <div class="flex justify-end gap-2">
          <UButton
            label="Cancel"
            color="neutral"
            variant="subtle"
            @click="isOpen = false"
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
