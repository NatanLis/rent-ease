<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import { upperFirst } from 'scule'
import { getPaginationRowModel, type Row } from '@tanstack/table-core'
import AddModal from '~/components/properties/AddModal.vue'
import EditModal from '~/components/properties/EditModal.vue'

const UButton = resolveComponent('UButton')
const UBadge = resolveComponent('UBadge')
const UDropdownMenu = resolveComponent('UDropdownMenu')
const UCheckbox = resolveComponent('UCheckbox')

const toast = useToast()
const table = useTemplateRef('table')

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

// Edit modal state
const isEditModalOpen = ref(false)
const propertyToEdit = ref<Property | null>(null)

// Delete confirmation modal state
const isDeleteModalOpen = ref(false)
const propertyToDelete = ref<Property | null>(null)

const route = useRoute()

const columnFilters = ref([{
  id: 'title',
  value: ''
}])
const columnVisibility = ref()
const rowSelection = ref({})

const { getToken } = useAuth()
const token = await getToken()

// Reactive data instead of useFetch
const data = ref<Property[]>([])
const status = ref<'pending' | 'error' | 'success'>('pending')

// Property filter from URL parameter (to filter by specific property ID)
const propertyIdFilter = ref<string | null>(null)

// Check for property filter in URL
onMounted(() => {
  if (route.query.propertyId) {
    propertyIdFilter.value = route.query.propertyId as string
  }
  fetchProperties()
})

// Watch for route changes
watch(() => route.query.propertyId, (newPropertyId) => {
  propertyIdFilter.value = newPropertyId as string || null
})

// Computed filtered data
const filteredData = computed(() => {
  if (!propertyIdFilter.value) {
    return data.value
  }
  return data.value.filter(property => property.id.toString() === propertyIdFilter.value)
})

// Function to clear property filter
function clearPropertyFilter() {
  propertyIdFilter.value = null
  navigateTo('/home/properties')
}

// Get user role to determine endpoint
const { getUser } = useUser()
const user = getUser()

// Function to fetch properties
async function fetchProperties() {
  try {
    status.value = 'pending'
    const result = await $fetch<Property[]>('/api/properties', {
      headers: token ? {
        'Authorization': `Bearer ${token}`
      } : {}
    })
    data.value = result
    status.value = 'success'
  } catch (error) {
    console.error('Error fetching properties:', error)
    status.value = 'error'
  }
}

// Function to open edit modal
function openEditModal(property: Property) {
  propertyToEdit.value = property
  isEditModalOpen.value = true
}

// Function to open delete confirmation modal
function openDeleteModal(property: Property) {
  propertyToDelete.value = property
  isDeleteModalOpen.value = true
}

// Function to delete property
async function confirmDeleteProperty() {
  if (!propertyToDelete.value) return

  try {
    const token = getToken()

    await $fetch(`/api/properties/${propertyToDelete.value.id}`, {
      method: 'DELETE',
      headers: token ? {
        'Authorization': `Bearer ${token}`
      } : {}
    })

    toast.add({
      title: 'Success',
      description: `Property "${propertyToDelete.value.title}" has been deleted`,
      color: 'success'
    })

    // Close modal and refresh properties list
    isDeleteModalOpen.value = false
    propertyToDelete.value = null
    await fetchProperties()

  } catch (error: any) {
    console.error('Error deleting property:', error)

    // Handle different error cases
    let errorMessage = 'Failed to delete property'

    if (error.status === 409 || error.statusCode === 409) {
      // Conflict - likely active leases
      errorMessage = error.data?.detail || 'Cannot delete property with active leases'
    } else if (error.data?.detail) {
      errorMessage = error.data.detail
    }

    toast.add({
      title: 'Error',
      description: errorMessage,
      color: 'error'
    })
  }
}

// Provide refresh function for child components
provide('refreshProperties', fetchProperties)

// Function to generate context menu items for table row
function getRowItems(row: Row<Property>) {
  const hasActiveLeases = row.original.activeLeases > 0

  return [
    {
      type: 'label',
      label: 'Actions'
    },
    {
      label: 'View units',
      icon: 'i-lucide-building',
      onSelect() {
        navigateTo(`/home/units?propertyId=${row.original.id}`)
      }
    },
    {
      label: 'View leases',
      icon: 'i-lucide-file-text',
      onSelect() {
        navigateTo(`/home/leases?propertyId=${row.original.id}`)
      }
    },
    {
      type: 'separator'
    },
    {
      label: 'Edit property',
      icon: 'i-lucide-edit',
      color: 'primary',
      onSelect() {
        openEditModal(row.original)
      }
    },
    {
      label: 'Delete property',
      icon: 'i-lucide-trash',
      color: hasActiveLeases ? 'neutral' : 'error',
      disabled: hasActiveLeases,
      onSelect() {
        if (!hasActiveLeases) {
          openDeleteModal(row.original)
        } else {
          toast.add({
            title: 'Cannot delete property',
            description: 'Property has active leases. Please terminate all leases before deleting.',
            color: 'warning'
          })
        }
      }
    }
  ]
}

// Table columns definition
const columns: TableColumn<Property>[] = [
  {
    id: 'select',
    header: ({ table }) =>
      h(UCheckbox, {
        'modelValue': table.getIsSomePageRowsSelected()
          ? 'indeterminate'
          : table.getIsAllPageRowsSelected(),
        'onUpdate:modelValue': (value: boolean | 'indeterminate') =>
          table.toggleAllPageRowsSelected(!!value),
        'ariaLabel': 'Select all'
      }),
    cell: ({ row }) =>
      h(UCheckbox, {
        'modelValue': row.getIsSelected(),
        'onUpdate:modelValue': (value: boolean | 'indeterminate') => row.toggleSelected(!!value),
        'ariaLabel': 'Select row'
      })
  },
  {
    accessorKey: 'id',
    header: 'ID'
  },
  {
    accessorKey: 'title',
    header: ({ column }) => {
      const isSorted = column.getIsSorted()

      return h(UButton, {
        color: 'neutral',
        variant: 'ghost',
        label: 'Property',
        icon: isSorted
          ? isSorted === 'asc'
            ? 'i-lucide-arrow-up-narrow-wide'
            : 'i-lucide-arrow-down-wide-narrow'
          : 'i-lucide-arrow-up-down',
        class: '-mx-2.5',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc')
      })
    },
    cell: ({ row }) => {
      return h('div', undefined, [
        h('p', { class: 'font-medium text-(--ui-text-highlighted)' }, row.original.title),
        h('p', { class: 'text-sm text-(--ui-text-muted)' }, row.original.description || 'No description')
      ])
    }
  },
  {
    accessorKey: 'address',
    header: 'Address',
    cell: ({ row }) => {
      return h('div', { class: 'flex items-center gap-2' }, [
        h('i', { class: 'i-lucide-map-pin text-sm text-(--ui-text-muted)' }),
        h('span', { class: 'text-sm' }, row.original.address)
      ])
    }
  },
  {
    accessorKey: 'price',
    header: 'Price',
    cell: ({ row }) => {
      return h('div', { class: 'text-right' }, [
        h('p', { class: 'font-medium text-(--ui-text-highlighted)' }, `${row.original.price.toLocaleString('pl-PL')} zł`),
        h('p', { class: 'text-sm text-(--ui-text-muted)' }, 'per month')
      ])
    }
  },
  {
    accessorKey: 'units_count',
    header: 'Units',
    cell: ({ row }) => {
      return h('div', { class: 'text-center' }, [
        h('p', { class: 'font-medium text-(--ui-text-highlighted)' }, row.original.unitsCount),
        h('p', { class: 'text-sm text-(--ui-text-muted)' }, 'total')
      ])
    }
  },
  {
    accessorKey: 'active_leases',
    header: 'Active Leases',
    cell: ({ row }) => {
      return h('div', { class: 'text-center' }, [
        h('p', { class: 'font-medium text-(--ui-text-highlighted)' }, row.original.activeLeases),
        h('p', { class: 'text-sm text-(--ui-text-muted)' }, 'occupied')
      ])
    }
  },
  {
    id: 'actions',
    cell: ({ row }) => {
      return h(
        'div',
        { class: 'text-right' },
        h(
          UDropdownMenu,
          {
            content: {
              align: 'end'
            },
            items: getRowItems(row)
          },
          () =>
            h(UButton, {
              icon: 'i-lucide-ellipsis-vertical',
              color: 'neutral',
              variant: 'ghost',
              class: 'ml-auto'
            })
        )
      )
    }
  }
]

// Pagination configuration
const pagination = ref({
  pageIndex: 0,
  pageSize: 10
})

// Page metadata configuration
definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})
</script>

<template>
  <UDashboardPanel id="properties">
    <template #header>
      <UDashboardNavbar
        :title="propertyIdFilter ? 'Property Details' : 'Properties'"
      >
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #trailing>
          <UBadge
            v-if="propertyIdFilter && filteredData.length > 0"
            :label="filteredData[0].title"
            variant="subtle"
            color="primary"
          />
        </template>

        <template #right>
          <div class="flex items-center gap-2">
            <UButton
              v-if="propertyIdFilter"
              label="Show All Properties"
              color="neutral"
              variant="ghost"
              icon="i-lucide-x"
              @click="clearPropertyFilter"
            />
            <AddModal />
          </div>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <!-- Filter info -->
      <div v-if="propertyIdFilter && filteredData.length > 0" class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <UIcon name="i-lucide-filter" class="text-blue-600" />
            <span class="text-sm text-blue-800">
              Viewing property details: <strong>{{ filteredData[0].title }}</strong>
            </span>
          </div>
          <div class="flex items-center gap-2">
            <UButton
              size="xs"
              color="blue"
              variant="soft"
              icon="i-lucide-home"
              @click="navigateTo(`/home/units?propertyId=${propertyIdFilter}`)"
            >
              View Units
            </UButton>
            <UButton
              size="xs"
              color="blue"
              variant="ghost"
              icon="i-lucide-x"
              @click="clearPropertyFilter"
            >
              Clear
            </UButton>
          </div>
        </div>
      </div>

      <div class="flex flex-wrap items-center justify-between gap-1.5">
        <UInput
          :model-value="(table?.tableApi?.getColumn('title')?.getFilterValue() as string)"
          class="max-w-sm"
          icon="i-lucide-search"
          placeholder="Search properties..."
          @update:modelValue="table?.tableApi?.getColumn('title')?.setFilterValue($event)"
        />

        <div class="flex flex-wrap items-center gap-1.5">
          <UButton
            v-if="table?.tableApi?.getFilteredSelectedRowModel().rows.length"
            label="Delete Selected"
            color="error"
            variant="subtle"
            icon="i-lucide-trash"
          >
            <template #trailing>
              <UKbd>
                {{ table?.tableApi?.getFilteredSelectedRowModel().rows.length }}
              </UKbd>
            </template>
          </UButton>

          <UDropdownMenu
            :items="
              table?.tableApi
                ?.getAllColumns()
                .filter((column) => column.getCanHide())
                .map((column) => ({
                  label: upperFirst(column.id),
                  type: 'checkbox' as const,
                  checked: column.getIsVisible(),
                  onUpdateChecked(checked: boolean) {
                    table?.tableApi?.getColumn(column.id)?.toggleVisibility(!!checked)
                  },
                  onSelect(e?: Event) {
                    e?.preventDefault()
                  }
                }))
            "
            :content="{ align: 'end' }"
          >
            <UButton
              label="Display"
              color="neutral"
              variant="outline"
              trailing-icon="i-lucide-settings-2"
            />
          </UDropdownMenu>
        </div>
      </div>

      <UTable
        ref="table"
        v-model:column-filters="columnFilters"
        v-model:column-visibility="columnVisibility"
        v-model:row-selection="rowSelection"
        v-model:pagination="pagination"
        :pagination-options="{
          getPaginationRowModel: getPaginationRowModel()
        }"
        class="shrink-0"
        :data="filteredData"
        :columns="columns"
        :loading="status === 'pending'"
        :ui="{
          base: 'table-fixed border-separate border-spacing-0',
          thead: '[&>tr]:bg-(--ui-bg-elevated)/50 [&>tr]:after:content-none',
          tbody: '[&>tr]:last:[&>td]:border-b-0',
          th: 'py-1 first:rounded-l-[calc(var(--ui-radius)*2)] last:rounded-r-[calc(var(--ui-radius)*2)] border-y border-(--ui-border) first:border-l last:border-r',
          td: 'border-b border-(--ui-border)'
        }"
      />

      <div class="flex items-center justify-between gap-3 border-t border-(--ui-border) pt-4 mt-auto">
        <div class="text-sm text-(--ui-text-muted)">
          {{ table?.tableApi?.getFilteredSelectedRowModel().rows.length || 0 }} of
          {{ table?.tableApi?.getFilteredRowModel().rows.length || 0 }} row(s) selected.
        </div>

        <div class="flex items-center gap-1.5">
          <UPagination
            :default-page="(table?.tableApi?.getState().pagination.pageIndex || 0) + 1"
            :items-per-page="table?.tableApi?.getState().pagination.pageSize"
            :total="table?.tableApi?.getFilteredRowModel().rows.length"
            @update:page="(p) => table?.tableApi?.setPageIndex(p - 1)"
          />
        </div>
      </div>
    </template>
  </UDashboardPanel>

  <!-- Edit Modal -->
  <EditModal
    v-model:open="isEditModalOpen"
    :property="propertyToEdit"
  />

  <!-- Delete Confirmation Modal -->
  <UModal
    v-model:open="isDeleteModalOpen"
    title="Delete Property"
    description="This action cannot be undone"
  >
    <template #body>
      <div class="space-y-4">
        <div v-if="propertyToDelete" class="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-sm text-red-800">
            Are you sure you want to delete the property
            <strong>"{{ propertyToDelete.title }}"</strong>?
          </p>
          <p class="text-xs text-red-600 mt-2">
            This will permanently delete the property and all associated data.
          </p>
        </div>

        <div class="flex justify-end gap-2">
          <UButton
            label="Cancel"
            color="neutral"
            variant="subtle"
            @click="isDeleteModalOpen = false"
          />
          <UButton
            label="Delete"
            color="error"
            variant="solid"
            @click="confirmDeleteProperty"
          />
        </div>
      </div>
    </template>
  </UModal>
</template>
