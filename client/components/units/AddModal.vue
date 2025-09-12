<script setup lang="ts">
import * as z from 'zod'
import type { FormSubmitEvent } from '@nuxt/ui'

// Property interface for dropdown - matches API response
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

// Form validation schema definition
const schema = z.object({
  property_id: z.string().min(1, 'Please select a property').transform(val => parseInt(val)),
  name: z.string().min(1, 'Unit name is required'),
  description: z.string().optional(),
  monthly_rent: z.number().min(0, 'Monthly rent must be non-negative')
})

type Schema = z.output<typeof schema>

// Modal state
const open = ref(false)

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

// Refresh units function from parent component
const refreshUnits = inject<() => Promise<void>>('refreshUnits')

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
watch(open, async (isOpen) => {
  if (isOpen && properties.value.length === 0) {
    await fetchProperties()
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

// Form submission handler
async function onSubmit(event: FormSubmitEvent<Schema>) {
  pending.value = true
  try {
    const token = getToken()
    await $fetch('/api/units/', {
      method: 'POST',
      body: event.data,
      headers: token ? {
        'Authorization': `Bearer ${token}`
      } : {}
    })

    toast.add({
      title: 'Success',
      description: `Unit "${event.data.name}" created successfully`,
      color: 'success'
    })

    // Reset form and close modal
    Object.assign(state, {
      property_id: '',
      name: '',
      description: '',
      monthly_rent: 0
    })

    open.value = false

    // Refresh units list
    if (refreshUnits) {
      await refreshUnits()
    }

  } catch (error: any) {
    console.error('Error creating unit:', error)
    toast.add({
      title: 'Error',
      description: error.data?.detail || 'Failed to create unit',
      color: 'error'
    })
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <div>
    <UButton
      label="Add Unit"
      icon="i-lucide-plus"
      @click="open = true"
    />

    <UModal v-model:open="open" title="New Unit" description="Add a new unit to the selected property">
      <template #body>
        <UForm
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
              @click="open = false"
              :disabled="pending"
            />
            <UButton
              label="Create"
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
  </div>
</template>
