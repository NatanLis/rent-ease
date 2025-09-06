<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import { upperFirst } from 'scule'
import { getPaginationRowModel, type Row } from '@tanstack/table-core'

const UButton = resolveComponent('UButton')
const UBadge = resolveComponent('UBadge')
const UDropdownMenu = resolveComponent('UDropdownMenu')
const UCheckbox = resolveComponent('UCheckbox')
const UAvatar = resolveComponent('UAvatar')

const toast = useToast()
const table = useTemplateRef('table')

// Define lease type
interface Lease {
  id: number
  unitId: number
  tenantId: number
  startDate: string
  endDate: string | null
  isActive: boolean
  tenantEmail: string
  unitName: string
  propertyTitle: string
  propertyAddress: string
  status: 'active' | 'inactive'
  avatar: {
    src: string
  }
}

const columnFilters = ref([{
  id: 'tenantEmail',
  value: ''
}])
const columnVisibility = ref()
const rowSelection = ref({})

const { getToken } = useAuth()
const token = await getToken()

// Use reactive data instead of useFetch
const data = ref<Lease[]>([])
const status = ref<'pending' | 'error' | 'success'>('pending')

// Fetch data on mount
onMounted(async () => {
  try {
    status.value = 'pending'
    const result = await $fetch<Lease[]>('/api/leases', {
      headers: token ? {
        'Authorization': `Bearer ${token}`
      } : {}
    })
    data.value = result
    status.value = 'success'
  } catch (error) {
    status.value = 'error'
  }
})

function getRowItems(row: Row<Lease>) {
  return [
    {
      type: 'label',
      label: 'Actions'
    },
    {
      label: 'Copy lease ID',
      icon: 'i-lucide-copy',
      onSelect() {
        navigator.clipboard.writeText(row.original.id.toString())
        toast.add({
          title: 'Copied to clipboard',
          description: 'Lease ID copied to clipboard'
        })
      }
    },
    {
      type: 'separator'
    },
    {
      label: 'View lease details',
      icon: 'i-lucide-list'
    },
    {
      label: 'View payments',
      icon: 'i-lucide-wallet'
    },
    {
      type: 'separator'
    },
    {
      label: 'End lease',
      icon: 'i-lucide-calendar-x',
      color: 'warning',
      onSelect() {
        toast.add({
          title: 'Lease ended',
          description: 'The lease has been ended.'
        })
      }
    }
  ]
}

const columns: TableColumn<Lease>[] = [
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
    accessorKey: 'tenantEmail',
    header: ({ column }) => {
      const isSorted = column.getIsSorted()

      return h(UButton, {
        color: 'neutral',
        variant: 'ghost',
        label: 'Tenant',
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
      return h('div', { class: 'flex items-center gap-3' }, [
        h(UAvatar, {
          ...row.original.avatar,
          size: 'lg'
        }),
        h('div', undefined, [
          h('p', { class: 'font-medium text-(--ui-text-highlighted)' }, row.original.tenantEmail.split('@')[0]),
          h('p', { class: 'text-sm text-(--ui-text-muted)' }, row.original.tenantEmail)
        ])
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
    accessorKey: 'unitName',
    header: 'Unit'
  },
  {
    accessorKey: 'startDate',
    header: 'Start Date',
    cell: ({ row }) => {
      const date = new Date(row.original.startDate)
      return date.toLocaleDateString('pl-PL')
    }
  },
  {
    accessorKey: 'endDate',
    header: 'End Date',
    cell: ({ row }) => {
      if (!row.original.endDate) return 'Ongoing'
      const date = new Date(row.original.endDate)
      return date.toLocaleDateString('pl-PL')
    }
  },
  {
    accessorKey: 'status',
    header: 'Status',
    filterFn: 'equals',
    cell: ({ row }) => {
      const color = {
        active: 'success' as const,
        inactive: 'error' as const
      }[row.original.status] || 'neutral'

      const displayStatus = {
        active: 'Active',
        inactive: 'Inactive'
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
  <UDashboardPanel id="leases">
    <template #header>
      <UDashboardNavbar title="Leases">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <UButton
            label="Add Lease"
            icon="i-lucide-plus"
            color="primary"
          />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="flex flex-wrap items-center justify-between gap-1.5">
        <UInput
          :model-value="(table?.tableApi?.getColumn('tenantEmail')?.getFilterValue() as string)"
          class="max-w-sm"
          icon="i-lucide-search"
          placeholder="Filter tenants..."
          @update:model-value="table?.tableApi?.getColumn('tenantEmail')?.setFilterValue($event)"
        />

        <div class="flex flex-wrap items-center gap-1.5">
          <UButton
            v-if="table?.tableApi?.getFilteredSelectedRowModel().rows.length"
            label="End Selected"
            color="warning"
            variant="subtle"
            icon="i-lucide-calendar-x"
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
              { label: 'Inactive', value: 'inactive' }
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
                })) || []
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
