<script setup lang="ts">
const { data: invoices, refresh, pending } = await useFetch<any[]>('/api/invoices', { default: () => [], server: false })
const { data: properties, pending: propertiesPending } = await useFetch<any[]>('/api/properties', { default: () => [], server: false })

const title = ref('')
const value = ref('')
const property = ref('')
const file = ref<File | null>(null)
const uploading = ref(false)

const propertyOptions = computed(() => (properties.value || []).map((p: any) => ({ label: p.title || p.name, value: p.title || p.name })))

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  file.value = input.files?.[0] || null
}

async function uploadInvoice() {
  if (!title.value || !value.value || !property.value || !file.value) return
  uploading.value = true
  try {
    const form = new FormData()
    form.append('title', title.value)
    form.append('value', value.value)
    form.append('property', property.value)
    form.append('file', file.value)
    await $fetch('/api/invoices', { method: 'POST', body: form })
    title.value = ''
    value.value = ''
    property.value = ''
    file.value = null
    await refresh()
  } finally {
    uploading.value = false
  }
}

definePageMeta({ layout: 'dashboard' })
</script>

<template>
  <UDashboardPanel id="invoices">
    <template #header>
      <UDashboardNavbar title="Invoices" />
    </template>

    <template #body>
      <div class="space-y-6">
        <UCard>
          <template #header>
            <h3 class="text-lg font-semibold">Upload New Invoice</h3>
          </template>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="flex items-center gap-3">
              <label class="w-40 text-sm text-(--ui-text-muted)">Title:</label>
              <UInput v-model="title" placeholder="Invoice title" class="flex-1" />
            </div>
            <div class="flex items-center gap-3">
              <label class="w-40 text-sm text-(--ui-text-muted)">Value (PLN):</label>
              <UInput v-model="value" type="number" step="0.01" placeholder="0.00" class="flex-1" />
            </div>
            <div class="flex items-center gap-3">
              <label class="w-40 text-sm text-(--ui-text-muted)">Property:</label>
              <USelect v-model="property" :items="propertyOptions" :loading="propertiesPending" placeholder="Select property" class="flex-1" />
            </div>
            <div class="flex items-center gap-3">
              <label class="w-40 text-sm text-(--ui-text-muted)">File:</label>
              <input type="file" accept="application/pdf,image/*" @change="onFileChange" class="flex-1" />
            </div>
          </div>
          <template #footer>
            <div class="flex justify-end">
              <UButton :loading="uploading" :disabled="!title || !value || !property || !file" color="primary" @click="uploadInvoice">Upload</UButton>
            </div>
          </template>
        </UCard>

        <UCard>
          <template #header>
            <h3 class="text-lg font-semibold">Invoices List</h3>
          </template>
          <UTable
            :loading="pending"
            :data="invoices || []"
            :columns="[
              { accessorKey: 'id', header: 'ID', cell: ({ row }) => `#${row.original.id}` },
              { accessorKey: 'title', header: 'Title' },
              { accessorKey: 'property', header: 'Property' },
              { accessorKey: 'value', header: 'Value', cell: ({ row }) => new Intl.NumberFormat('pl-PL', { style: 'currency', currency: 'PLN' }).format(row.original.value || 0) },
              { accessorKey: 'createdAt', header: 'Uploaded', cell: ({ row }) => new Date(row.original.createdAt).toLocaleString('pl-PL') },
              { accessorKey: 'fileUrl', header: 'File', cell: ({ row }) => h('a', { href: row.original.fileUrl, target: '_blank', class: 'text-(--ui-primary)' }, 'Open') }
            ]"
          />
        </UCard>
      </div>
    </template>
  </UDashboardPanel>
</template>


