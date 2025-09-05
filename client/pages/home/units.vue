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

const columnFilters = ref([{
  id: 'name',
  value: ''
}])
const columnVisibility = ref()
const rowSelection = ref({ 1: true })

const { data, status } = await useFetch<Unit[]>('/mock/units', {
  lazy: true
})

function getRowItems(row: Row<Unit>) {
  return [
    {
      type: 'label',
      label: 'Actions'
    },
    {
      label: 'Copy unit ID',
      icon: 'i-lucide-copy',
      onSelect() {
        navigator.clipboard.writeText(row.original.id.toString())
        toast.add({
          title: 'Copied to clipboard',
          description: 'Unit ID copied to clipboard'
        })
      }
    },
    {
      type: 'separator'
    },
    {
      label: 'View unit details',
      icon: 'i-lucide-list'
    },
    {
      label: 'View property',
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
      label: 'Edit unit',
      icon: 'i-lucide-edit',
      color: 'primary'
    },
    {
      label: 'Delete unit',
      icon: 'i-lucide-trash',
      color: 'error',
      onSelect() {
        toast.add({
          title: 'Unit deleted',
          description: 'The unit has been deleted.'
        })
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
})
</script>

<template>
  <UDashboardPanel id="units">
    <template #header>
      <UDashboardNavbar title="Units">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <UButton
            label="Add Unit"
            icon="i-lucide-plus"
            color="primary"
          />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
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
