<script setup lang="ts">
import * as z from 'zod'
import type { FormSubmitEvent } from '@nuxt/ui'

// Form validation schema definition
const schema = z.object({
  title: z.string().min(2, 'Title too short'),
  description: z.string().optional(),
  address: z.string().min(5, 'Address too short'),
  price: z.number().min(1, 'Price must be greater than 0')
})

// Modal state (open/closed)
const open = ref(false)

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

// Form submit handler
async function onSubmit(event: FormSubmitEvent<Schema>) {
  console.log('Form submitted with data:', event.data)
  pending.value = true

  try {
    const token = getToken()
    console.log('Token:', token ? 'Present' : 'Missing')

    const response = await $fetch('/api/properties/', {
      method: 'POST',
      body: event.data,
      headers: token ? {
        'Authorization': `Bearer ${token}`
      } : {}
    })

    console.log('API Response:', response)

    toast.add({
      title: 'Success',
      description: `New property "${event.data.title}" has been added`,
      color: 'success'
    })

    open.value = false

    // Reset form
    Object.keys(state).forEach(key => {
      state[key as keyof Schema] = undefined
    })

    // Refresh properties list
    if (refreshProperties) {
      await refreshProperties()
    }

  } catch (error: any) {
    console.error('Error creating property:', error)
    toast.add({
      title: 'Error',
      description: error.data?.detail || 'Failed to create property',
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
      label="Add Property"
      icon="i-lucide-plus"
      @click="open = true"
    />

    <UModal v-model:open="open" title="New Property" description="Add a new property to the database">
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
