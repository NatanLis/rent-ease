<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import { upperFirst } from 'scule'
import { getPaginationRowModel, type Row } from '@tanstack/table-core'

const UButton = resolveComponent('UButton')
const UBadge = resolveComponent('UBadge')
const UDropdownMenu = resolveComponent('UDropdownMenu')
const UCheckbox = resolveComponent('UCheckbox')

const toast = useToast()
const table = useTemplateRef('table')

// Define property type
interface Property {
  id: number
  title: string
  description: string | null
  address: string
  price: number
  ownerId: number
  unitsCount: number
  activeLeases: number
  status: 'active' | 'available' | 'maintenance'
}

const columnFilters = ref([{
  id: 'title',
  value: ''
}])
const columnVisibility = ref()
const rowSelection = ref({ 1: true })

// Get user role to determine which endpoint to use
const { getUser } = useUser()
const user = getUser()
const { getToken } = useAuth()
const token = await getToken()

// Use different endpoints based on user role
const endpoint = user?.isAdmin() ? '/api/properties/all' : '/api/properties'

// Use reactive data instead of useFetch
const data = ref<Property[]>([])
const status = ref<'pending' | 'error' | 'success'>('pending')

// Fetch data with authorization header
async function fetchProperties() {
  try {
    status.value = 'pending'
    const response = await fetch(endpoint, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`Failed to fetch properties: ${response.status}`)
    }
    
    data.value = await response.json()
    status.value = 'success'
  } catch (error) {
    console.error('Error fetching properties:', error)
    status.value = 'error'
    data.value = []
  }
}

// Fetch data on mount
await fetchProperties()

function getRowItems(row: Row<Property>) {
  return [
    {
      type: 'label',
      label: 'Actions'
    },
    {
      label: 'Copy property ID',
      icon: 'i-lucide-copy',
      onSelect() {
        navigator.clipboard.writeText(row.original.id.toString())
        toast.add({
          title: 'Copied to clipboard',
          description: 'Property ID copied to clipboard'
        })
      }
    },
    {
      type: 'separator'
    },
    {
      label: 'View property details',
      icon: 'i-lucide-list'
    },
    {
      label: 'View units',
      icon: 'i-lucide-building'
    },
    {
      label: 'View leases',
      icon: 'i-lucide-file-text'
    },
    {
      type: 'separator'
    },
    {
      label: 'Edit property',
      icon: 'i-lucide-edit',
      color: 'primary'
    },
    {
      label: 'Delete property',
      icon: 'i-lucide-trash',
      color: 'error',
      onSelect() {
        toast.add({
          title: 'Property deleted',
          description: 'The property has been deleted.'
        })
      }
    }
  ]
}

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
    accessorKey: 'unitsCount',
    header: 'Units',
    cell: ({ row }) => {
      return h('div', { class: 'text-center' }, [
        h('p', { class: 'font-medium text-(--ui-text-highlighted)' }, row.original.unitsCount),
        h('p', { class: 'text-sm text-(--ui-text-muted)' }, 'total')
      ])
    }
  },
  {
    accessorKey: 'activeLeases',
    header: 'Active Leases',
    cell: ({ row }) => {
      return h('div', { class: 'text-center' }, [
        h('p', { class: 'font-medium text-(--ui-text-highlighted)' }, row.original.activeLeases),
        h('p', { class: 'text-sm text-(--ui-text-muted)' }, 'occupied')
      ])
    }
  },
  {
    accessorKey: 'status',
    header: 'Status',
    filterFn: 'equals',
    cell: ({ row }) => {
      const color = {
        active: 'success' as const,
        available: 'info' as const,
        maintenance: 'warning' as const
      }[row.original.status] || 'neutral'

      const displayStatus = {
        active: 'Active',
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
  <UDashboardPanel id="properties">
    <template #header>
      <UDashboardNavbar title="Properties">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <UButton
            label="Add Property"
            icon="i-lucide-plus"
            color="primary"
          />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="flex flex-wrap items-center justify-between gap-1.5">
        <UInput
          :model-value="(table?.tableApi?.getColumn('title')?.getFilterValue() as string)"
          class="max-w-sm"
          icon="i-lucide-search"
          placeholder="Filter properties..."
          @update:model-value="table?.tableApi?.getColumn('title')?.setFilterValue($event)"
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
              { label: 'Active', value: 'active' },
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
        :data="data"
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
</template>
