<script setup lang="ts">
import * as z from 'zod'
import type { FormSubmitEvent } from '@nuxt/ui'

interface Unit {
  id: number
  name: string
  monthlyRent: number
}

interface Property {
  id: number
  title: string
  address: string
}

interface Tenant {
  id: number
  email: string
  first_name: string
  last_name: string
}

const schema = z.object({
  property_id: z.string().transform(val => parseInt(val)),
  unit_id: z.string().transform(val => parseInt(val)),
  tenant_id: z.string().transform(val => parseInt(val)),
  start_date: z.string(),
  end_date: z.string().optional()
})

type Schema = z.output<typeof schema>

const open = ref(false)

const state = reactive({
  property_id: '' as string,
  unit_id: '' as string,
  tenant_id: '' as string,
  start_date: '',
  end_date: ''
})

const units = ref<Unit[]>([])
const properties = ref<Property[]>([])
const tenants = ref<Tenant[]>([])
const loadingUnits = ref(false)
const loadingProperties = ref(false)
const loadingTenants = ref(false)
const pending = ref(false)

const toast = useToast()
const { getToken } = useAuth()

const refreshLeases = inject<() => Promise<void>>('refreshLeases')

async function fetchUnitsForProperty(propertyId: string) {
  if (!propertyId) return

  loadingUnits.value = true
  try {
    const token = getToken()
    const response = await $fetch(`/api/units/property/${propertyId}`, {
      method: 'GET',
      headers: token ? {
        'Authorization': `Bearer ${token}`
      } : {}
    })
    units.value = response
  } catch (error) {
    console.error('Error fetching units for property:', error)
    toast.add({
      title: 'Error',
      description: 'Failed to load units for this property',
      color: 'error'
    })
    units.value = []
  } finally {
    loadingUnits.value = false
  }
}

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

async function fetchTenants() {
  loadingTenants.value = true
  try {
    const token = getToken()
    const response = await $fetch('/api/tenants/', {
      method: 'GET',
      headers: token ? {
        'Authorization': `Bearer ${token}`
      } : {}
    })
    tenants.value = response
  } catch (error) {
    console.error('Error fetching tenants:', error)
    toast.add({
      title: 'Error',
      description: 'Failed to load tenants',
      color: 'error'
    })
  } finally {
    loadingTenants.value = false
  }
}

watch(open, async (isOpen) => {
  if (isOpen) {
    if (properties.value.length === 0) {
      await fetchProperties()
    }
    if (tenants.value.length === 0) {
      await fetchTenants()
    }
  }
})

// Handle property selection change
async function onPropertyChange(propertyId: string) {
  console.log('Property changed to:', propertyId)
  state.unit_id = ''
  units.value = []

  if (propertyId) {
    await fetchUnitsForProperty(propertyId)
  }
}

const isButtonDisabled = computed(() => {
  const disabled = pending.value || !state.property_id || !state.unit_id || !state.tenant_id || !state.start_date
  return disabled
})

const propertyOptions = computed(() => {
  if (!properties.value || properties.value.length === 0) {
    return []
  }

  return properties.value.map(property => ({
    label: property.title,
    value: property.id.toString()
  }))
})

const unitOptions = computed(() => {
  if (!units.value || units.value.length === 0) {
    return []
  }

  return units.value.map(unit => ({
    label: `${unit.name} (${unit.monthlyRent} PLN/month)`,
    value: unit.id.toString()
  }))
})

const tenantOptions = computed(() => {
  if (!tenants.value || tenants.value.length === 0) {
    return []
  }

  return tenants.value.map(tenant => ({
    label: `${tenant.first_name} ${tenant.last_name} (${tenant.email})`,
    value: tenant.id.toString()
  }))
})

function onError(errors: any) {
  toast.add({
    title: 'Validation Error',
    description: 'Please check all required fields',
    color: 'error'
  })
}

async function onSubmit(event: FormSubmitEvent<Schema>) {
  pending.value = true
  try {
    const token = getToken()

    // Prepare data for backend (exclude property_id as it's not needed)
    const { property_id, ...backendData } = event.data

    // Clean up end_date - remove if empty
    if (!backendData.end_date || backendData.end_date === '') {
      delete backendData.end_date
    }

    // Additional validation - ensure unit_id is not empty
    if (!backendData.unit_id) {
      throw new Error('Unit selection is required')
    }

    const response = await $fetch('/api/leases/', {
      method: 'POST',
      body: backendData,
      headers: token ? {
        'Authorization': `Bearer ${token}`
      } : {}
    })

    const selectedUnit = units.value.find(u => u.id === event.data.unit_id)
    const selectedTenant = tenants.value.find(t => t.id === event.data.tenant_id)

    toast.add({
      title: 'Success',
      description: `Lease created for ${selectedTenant?.first_name} ${selectedTenant?.last_name} in ${selectedUnit?.name}`,
      color: 'success'
    })

    Object.assign(state, {
      property_id: '',
      unit_id: '',
      tenant_id: '',
      start_date: '',
      end_date: ''
    })

    open.value = false

    if (refreshLeases) {
      await refreshLeases()
    }

  } catch (error: any) {
    console.error('Error creating lease:', error)
    toast.add({
      title: 'Error',
      description: error.data?.detail || 'Failed to create lease',
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
      label="Add Lease"
      icon="i-lucide-plus"
      @click="open = true"
    />

    <UModal v-model:open="open" title="New Lease" description="Create a new lease agreement">
      <template #body>
        <UForm
          :schema="schema"
          :state="state"
          class="space-y-4"
          @submit="onSubmit"
          @error="onError"
        >
          <UFormField label="Property" name="property_id" required>
            <USelect
              v-model="state.property_id"
              :items="propertyOptions"
              placeholder="Select a property..."
              class="w-full"
              :disabled="loadingProperties"
              @update:model-value="onPropertyChange"
            />
          </UFormField>

          <UFormField label="Unit" name="unit_id" required>
            <USelect
              v-model="state.unit_id"
              :items="unitOptions"
              :placeholder="loadingUnits ? 'Loading units...' : unitOptions.length === 0 && state.property_id ? 'No units available for this property' : 'Select a unit...'"
              class="w-full"
              :disabled="loadingUnits || !state.property_id"
            />
          </UFormField>

          <UFormField label="Tenant" name="tenant_id" required>
            <USelect
              v-model="state.tenant_id"
              :items="tenantOptions"
              placeholder="Select a tenant..."
              class="w-full"
              :disabled="loadingTenants"
            />
          </UFormField>

          <UFormField label="Start Date" name="start_date" required>
            <UInput
              v-model="state.start_date"
              type="date"
              class="w-full"
            />
          </UFormField>

          <UFormField label="End Date (optional)" name="end_date">
            <UInput
              v-model="state.end_date"
              type="date"
              class="w-full"
              placeholder="Leave empty for ongoing lease"
            />
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
              :disabled="isButtonDisabled"
            />
          </div>
        </UForm>
      </template>
    </UModal>
  </div>
</template>
