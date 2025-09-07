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

// Define lease type based on backend LeaseResponse
interface Lease {
  id: number
  unit_id: number
  tenant_id: number
  start_date: string
  end_date: string | null
  is_active: boolean
  user: {
    id: number
    email: string
    first_name: string
    last_name: string
    avatar_url?: string
  }
  unit: {
    id: number
    name: string
    monthly_rent: number
    property: {
      id: number
      title: string
      address: string
    }
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

// Add computed property for tenant email filtering
const dataWithTenantEmail = computed(() => {
  return data.value.map(lease => ({
    ...lease,
    tenantEmail: lease.user?.email || 'unknown@example.com'
  }))
})

// Get user role to determine which endpoint to use
const { getUser } = useUser()
const user = getUser()

// Use different endpoints based on user role
const endpoint = user?.isAdmin() ? '/api/leases/all' : '/api/leases/owner'

// Fetch data on mount
onMounted(async () => {
  try {
    status.value = 'pending'
    const result = await $fetch<Lease[]>(endpoint, {
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
      const user = row.original.user
      if (!user) {
        return h('div', { class: 'flex items-center gap-3' }, [
          h(UAvatar, {
            src: 'https://ui-avatars.com/api/?name=Unknown+User',
            alt: 'Unknown User',
            size: 'lg'
          }),
          h('div', undefined, [
            h('p', { class: 'font-medium text-(--ui-text-highlighted)' }, 'Unknown User'),
            h('p', { class: 'text-sm text-(--ui-text-muted)' }, 'No user data')
          ])
        ])
      }
      
      return h('div', { class: 'flex items-center gap-3' }, [
        h(UAvatar, {
          src: user.avatar_url || `https://ui-avatars.com/api/?name=${user.first_name}+${user.last_name}`,
          alt: `${user.first_name} ${user.last_name}`,
          size: 'lg'
        }),
        h('div', undefined, [
          h('p', { class: 'font-medium text-(--ui-text-highlighted)' }, `${user.first_name} ${user.last_name}`),
          h('p', { class: 'text-sm text-(--ui-text-muted)' }, user.email)
        ])
      ])
    }
  },
  {
    accessorKey: 'unit.property.title',
    header: 'Property',
    cell: ({ row }) => {
      const property = row.original.unit?.property
      if (!property) {
        return h('div', undefined, [
          h('p', { class: 'font-medium text-(--ui-text-highlighted)' }, 'Unknown Property'),
          h('p', { class: 'text-sm text-(--ui-text-muted)' }, 'No property data')
        ])
      }
      
      return h('div', undefined, [
        h('p', { class: 'font-medium text-(--ui-text-highlighted)' }, property.title),
        h('p', { class: 'text-sm text-(--ui-text-muted)' }, property.address)
      ])
    }
  },
  {
    accessorKey: 'unit.name',
    header: 'Unit',
    cell: ({ row }) => {
      return row.original.unit?.name || 'Unknown Unit'
    }
  },
  {
    accessorKey: 'start_date',
    header: 'Start Date',
    cell: ({ row }) => {
      const date = new Date(row.original.start_date)
      return date.toLocaleDateString('pl-PL')
    }
  },
  {
    accessorKey: 'end_date',
    header: 'End Date',
    cell: ({ row }) => {
      if (!row.original.end_date) return 'Ongoing'
      const date = new Date(row.original.end_date)
      return date.toLocaleDateString('pl-PL')
    }
  },
  {
    accessorKey: 'is_active',
    header: 'Status',
    filterFn: 'equals',
    cell: ({ row }) => {
      const status = row.original.is_active ? 'active' : 'inactive'
      const color = {
        active: 'success' as const,
        inactive: 'error' as const
      }[status] || 'neutral'

      const displayStatus = {
        active: 'Active',
        inactive: 'Inactive'
      }[status] || status

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

  const statusColumn = table.value.tableApi.getColumn('is_active')
  if (!statusColumn) return

  if (newVal === 'all') {
    statusColumn.setFilterValue(undefined)
  } else {
    statusColumn.setFilterValue(newVal === 'active')
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
        :data="dataWithTenantEmail"
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
