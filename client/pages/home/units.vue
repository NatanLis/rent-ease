<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import { upperFirst } from 'scule'
import { getPaginationRowModel, type Row } from '@tanstack/table-core'
import AddModal from '~/components/units/AddModal.vue'
import EditModal from '~/components/units/EditModal.vue'

const UButton = resolveComponent('UButton')
const UBadge = resolveComponent('UBadge')
const UDropdownMenu = resolveComponent('UDropdownMenu')
const UCheckbox = resolveComponent('UCheckbox')

const toast = useToast()
const table = useTemplateRef('table')

// Define unit type
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

// Edit modal state
const isEditModalOpen = ref(false)
const unitToEdit = ref<Unit | null>(null)

// Delete confirmation modal state
const isDeleteModalOpen = ref(false)
const unitToDelete = ref<Unit | null>(null)

const route = useRoute()

const columnFilters = ref([{
  id: 'name',
  value: ''
}])
const columnVisibility = ref()
const rowSelection = ref()

const { getToken } = useAuth()
const token = await getToken()

// Reactive data instead of useFetch
const data = ref<Unit[]>([])
const status = ref<'pending' | 'error' | 'success'>('pending')

// Property filter from URL parameter
const propertyFilter = ref<string | null>(null)

// Check for property filter in URL
onMounted(() => {
  if (route.query.propertyId) {
    propertyFilter.value = route.query.propertyId as string
  }
  fetchUnits()
})

// Watch for route changes
watch(() => route.query.propertyId, (newPropertyId) => {
  propertyFilter.value = newPropertyId as string || null
})

// Computed filtered data
const filteredData = computed(() => {
  if (!propertyFilter.value) {
    return data.value
  }
  return data.value.filter(unit => unit.propertyId.toString() === propertyFilter.value)
})

// Get property name for better UX
const propertyName = computed(() => {
  if (!propertyFilter.value || filteredData.value.length === 0) return null
  return filteredData.value[0]?.propertyTitle
})

// Function to clear property filter
function clearPropertyFilter() {
  propertyFilter.value = null
  navigateTo('/home/units')
}

// Function to fetch units
async function fetchUnits() {
  try {
    status.value = 'pending'
    const result = await $fetch<Unit[]>('/api/units', {
      headers: token ? {
        'Authorization': `Bearer ${token}`
      } : {}
    })
    data.value = result
    status.value = 'success'
  } catch (error) {
    console.error('Error fetching units:', error)
    status.value = 'error'
  }
}

// Provide refresh function for child components
provide('refreshUnits', fetchUnits)

// Function to open edit modal
function openEditModal(unit: Unit) {
  unitToEdit.value = unit
  isEditModalOpen.value = true
}

// Function to open delete confirmation modal
function openDeleteModal(unit: Unit) {
  unitToDelete.value = unit
  isDeleteModalOpen.value = true
}

// Function to delete unit
async function confirmDeleteUnit() {
  if (!unitToDelete.value) return

  try {
    const token = getToken()

    await $fetch(`/api/units/${unitToDelete.value.id}`, {
      method: 'DELETE',
      headers: token ? {
        'Authorization': `Bearer ${token}`
      } : {}
    })

    toast.add({
      title: 'Success',
      description: `Unit "${unitToDelete.value.name}" has been deleted`,
      color: 'success'
    })

    // Close modal and refresh units list
    isDeleteModalOpen.value = false
    unitToDelete.value = null
    await fetchUnits()

  } catch (error: any) {
    console.error('Error deleting unit:', error)

    // Handle different error cases
    let errorMessage = 'Failed to delete unit'

    if (error.status === 409 || error.statusCode === 409) {
      // Conflict - likely active leases
      errorMessage = error.data?.detail || 'Cannot delete unit with active leases'
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

function getRowItems(row: Row<Unit>) {
  const hasActiveLeases = row.original.activeLeases > 0

  return [
    {
      type: 'label',
      label: 'Actions'
    },
    {
      label: 'View property',
      icon: 'i-lucide-building',
      onSelect() {
        navigateTo(`/home/properties?propertyId=${row.original.propertyId}`)
      }
    },
    {
      label: 'View leases',
      icon: 'i-lucide-file-text',
      onSelect() {
        navigateTo(`/home/leases?unitId=${row.original.id}`)
      }
    },
    {
      type: 'separator'
    },
    {
      label: 'Edit unit',
      icon: 'i-lucide-edit',
      color: 'primary',
      onSelect() {
        openEditModal(row.original)
      }
    },
    {
      label: 'Delete unit',
      icon: 'i-lucide-trash',
      color: hasActiveLeases ? 'neutral' : 'error',
      disabled: hasActiveLeases,
      onSelect() {
        if (!hasActiveLeases) {
          openDeleteModal(row.original)
        } else {
          toast.add({
            title: 'Cannot delete unit',
            description: 'Unit has active leases. Please terminate all leases before deleting.',
            color: 'warning'
          })
        }
      }
    }
  ]
}

const columns: TableColumn<Unit>[] = [
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
    accessorKey: 'name',
    header: ({ column }) => {
      const isSorted = column.getIsSorted()

      return h(UButton, {
        color: 'neutral',
        variant: 'ghost',
        label: 'Unit',
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
        h('p', { class: 'font-medium text-(--ui-text-highlighted)' }, row.original.name),
        h('p', { class: 'text-sm text-(--ui-text-muted)' }, row.original.description || 'No description')
      ])
    }
  },
  {
    accessorKey: 'propertyTitle',
    header: 'Property',
    cell: ({ row }) => {
      return h('div', undefined, [
        h('p', { class: 'font-medium text-(--ui-text-highlighted)' }, row.original.propertyTitle),
        h('p', { class: 'text-sm text-(--ui-text-muted)' }, row.original.propertyAddress)
      ])
    }
  },
  {
    accessorKey: 'monthlyRent',
    header: 'Monthly Rent',
    cell: ({ row }) => {
      return h('div', { class: 'text-right' }, [
        h('p', { class: 'font-medium text-(--ui-text-highlighted)' }, `${row.original.monthlyRent.toLocaleString('pl-PL')} zł`),
        h('p', { class: 'text-sm text-(--ui-text-muted)' }, 'per month')
      ])
    }
  },
  {
    accessorKey: 'activeLeases',
    header: 'Active Leases',
    cell: ({ row }) => {
      return h('div', { class: 'text-center' }, [
        h('p', { class: 'font-medium text-(--ui-text-highlighted)' }, row.original.activeLeases),
        h('p', { class: 'text-sm text-(--ui-text-muted)' }, 'leases')
      ])
    }
  },
  {
    accessorKey: 'status',
    header: 'Status',
    filterFn: 'equals',
    cell: ({ row }) => {
      const color = {
        occupied: 'success' as const,
        available: 'info' as const,
        maintenance: 'warning' as const
      }[row.original.status] || 'neutral'

      const displayStatus = {
        occupied: 'Occupied',
        available: 'Available',
        maintenance: 'Maintenance'
      }[row.original.status] || row.original.status

      return h(UBadge, { class: 'capitalize', variant: 'subtle', color }, () =>
        displayStatus
      )
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

const statusFilter = ref('all')

watch(() => statusFilter.value, (newVal) => {
  if (!table?.value?.tableApi) return

  const statusColumn = table.value.tableApi.getColumn('status')
  if (!statusColumn) return

  if (newVal === 'all') {
    statusColumn.setFilterValue(undefined)
  } else {
    statusColumn.setFilterValue(newVal)
  }
})

const pagination = ref({
  pageIndex: 0,
  pageSize: 10
})

definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})
</script>

<template>
  <UDashboardPanel id="units">
    <template #header>
      <UDashboardNavbar
        :title="propertyFilter && propertyName ? `Units - ${propertyName}` : 'Units'"
      >
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #trailing>
          <UBadge
            v-if="propertyFilter"
            :label="`${filteredData.length} units`"
            variant="subtle"
            color="primary"
          />
        </template>

        <template #right>
          <div class="flex items-center gap-2">
            <UButton
              v-if="propertyFilter"
              label="Show All Units"
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
      <div v-if="propertyFilter" class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <UIcon name="i-lucide-filter" class="text-blue-600" />
            <span class="text-sm text-blue-800">
              Showing units for property: <strong>{{ propertyName || `#${propertyFilter}` }}</strong>
            </span>
          </div>
          <div class="flex items-center gap-2">
            <UButton
              size="xs"
              color="blue"
              variant="soft"
              icon="i-lucide-building"
              @click="navigateTo(`/home/properties?propertyId=${propertyFilter}`)"
            >
              View Property
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
          :model-value="(table?.tableApi?.getColumn('name')?.getFilterValue() as string)"
          class="max-w-sm"
          icon="i-lucide-search"
          placeholder="Filter units..."
          @update:model-value="table?.tableApi?.getColumn('name')?.setFilterValue($event)"
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

          <USelect
            v-model="statusFilter"
            :items="[
              { label: 'All', value: 'all' },
              { label: 'Occupied', value: 'occupied' },
              { label: 'Available', value: 'available' },
              { label: 'Maintenance', value: 'maintenance' }
            ]"
            :ui="{ trailingIcon: 'group-data-[state=open]:rotate-180 transition-transform duration-200' }"
            placeholder="Filter status"
            class="min-w-28"
          />
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
    :unit="unitToEdit"
  />

  <!-- Delete Confirmation Modal -->
  <UModal
    v-model:open="isDeleteModalOpen"
    title="Delete Unit"
    description="This action cannot be undone"
  >
    <template #body>
      <div class="space-y-4">
        <div v-if="unitToDelete" class="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-sm text-red-800">
            Are you sure you want to delete the unit
            <strong>"{{ unitToDelete.name }}"</strong>?
          </p>
          <p class="text-xs text-red-600 mt-2">
            This will permanently delete the unit and all associated data.
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
            @click="confirmDeleteUnit"
          />
        </div>
      </div>
    </template>
  </UModal>
</template>
