<script setup lang="ts">
import * as z from 'zod'
import type { FormSubmitEvent } from '@nuxt/ui'

const schema = z.object({
  first_name: z.string().min(2, 'Too short'),
  last_name: z.string().min(2, 'Too short'),
  email: z.string().email('Invalid email'),
  password: z.string().min(6, 'Password too short')
})
const open = ref(false)

type Schema = z.output<typeof schema>

const state = reactive<Partial<Schema>>({
  first_name: undefined,
  last_name: undefined,
  email: undefined,
  password: undefined
})

const toast = useToast()
const pending = ref(false)

const refreshTenants = inject<() => Promise<void>>('refreshTenants')

const { getToken } = useAuth()

async function onSubmit(event: FormSubmitEvent<Schema>) {
  pending.value = true

  try {
    const token = getToken()
    const { data } = await $fetch('/api/tenants/', {
      method: 'POST',
      body: event.data,
      headers: token ? {
        'Authorization': `Bearer ${token}`
      } : {}
    })

    toast.add({
      title: 'Success',
      description: `New tenant ${event.data.first_name} ${event.data.last_name} added`,
      color: 'success'
    })

    open.value = false

    Object.keys(state).forEach(key => {
      state[key as keyof Schema] = undefined
    })

    if (refreshTenants) {
      await refreshTenants()
    }

  } catch (error: any) {
    toast.add({
      title: 'Error',
      description: error.data?.detail || 'Failed to create tenant',
      color: 'error'
    })
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <UModal v-model:open="open" title="New tenant" description="Add a new tenant to the database">
    <UButton label="New tenant" icon="i-lucide-plus" />

    <template #body>
      <UForm
        :schema="schema"
        :state="state"
        class="space-y-4"
        @submit="onSubmit"
      >
        <UFormField label="First Name" placeholder="John" name="first_name">
          <UInput v-model="state.first_name" class="w-full" />
        </UFormField>

        <UFormField label="Last Name" placeholder="Doe" name="last_name">
          <UInput v-model="state.last_name" class="w-full" />
        </UFormField>

        <UFormField label="Email" placeholder="john.doe@example.com" name="email">
          <UInput v-model="state.email" type="email" class="w-full" />
        </UFormField>

        <UFormField label="Password" placeholder="••••••••" name="password">
          <UInput v-model="state.password" type="password" class="w-full" />
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
</template>
