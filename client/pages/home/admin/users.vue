<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import { upperFirst } from 'scule'
import { getPaginationRowModel, type Row } from '@tanstack/table-core'

interface AdminUser {
  id: number
  name: string
  email: string
  role: 'ADMIN' | 'OWNER' | 'TENANT'
  status: 'active' | 'inactive'
  avatar?: {
    src: string
  }
  location: string
  createdAt: string
}

const UAvatar = resolveComponent('UAvatar')
const UButton = resolveComponent('UButton')
const UBadge = resolveComponent('UBadge')
const UDropdownMenu = resolveComponent('UDropdownMenu')
const UCheckbox = resolveComponent('UCheckbox')

const toast = useToast()
const table = useTemplateRef('table')

const columnFilters = ref([{
  id: 'email',
  value: ''
}])
const columnVisibility = ref()
const rowSelection = ref({ 1: true })

const { data, status } = await useFetch<AdminUser[]>('/api/mock/admin/users', {
  lazy: true
})

function getRowItems(row: Row<AdminUser>) {
  return [
    {
      type: 'label',
      label: 'Actions'
    },
    {
      label: 'Copy user ID',
      icon: 'i-lucide-copy',
      onSelect() {
        navigator.clipboard.writeText(row.original.id.toString())
        toast.add({
          title: 'Copied to clipboard',
          description: 'User ID copied to clipboard'
        })
      }
    },
    {
      type: 'separator'
    },
    {
      label: 'View user details',
      icon: 'i-lucide-list'
    },
    {
      label: 'Edit user role',
      icon: 'i-lucide-user-cog'
    },
    {
      label: 'Reset password',
      icon: 'i-lucide-key'
    },
    {
      type: 'separator'
    },
    {
      label: 'Deactivate user',
      icon: 'i-lucide-user-x',
      color: 'warning',
      onSelect() {
        toast.add({
          title: 'User deactivated',
          description: 'The user has been deactivated.'
        })
      }
    },
    {
      label: 'Delete user',
      icon: 'i-lucide-trash',
      color: 'error',
      onSelect() {
        toast.add({
          title: 'User deleted',
          description: 'The user has been deleted.'
        })
      }
    }
  ]
}

const columns: TableColumn<AdminUser>[] = [
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
    header: 'Name',
    cell: ({ row }) => {
      return h('div', { class: 'flex items-center gap-3' }, [
        h(UAvatar, {
          ...row.original.avatar,
          size: 'lg'
        }),
        h('div', undefined, [
          h('p', { class: 'font-medium text-(--ui-text-highlighted)' }, row.original.name),
          h('p', { class: 'text-sm text-(--ui-text-muted)' }, row.original.email)
        ])
      ])
    }
  },
  {
    accessorKey: 'role',
    header: 'Role',
    filterFn: 'equals',
    cell: ({ row }) => {
      const color = {
        ADMIN: 'red' as const,
        OWNER: 'blue' as const,
        TENANT: 'green' as const
      }[row.original.role] || 'neutral'

      const displayRole = {
        ADMIN: 'Administrator',
        OWNER: 'Property Owner',
        TENANT: 'Tenant'
      }[row.original.role] || row.original.role

      return h(UBadge, { class: 'capitalize', variant: 'subtle', color }, () =>
        displayRole
      )
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
    accessorKey: 'location',
    header: 'Location',
    cell: ({ row }) => row.original.location
  },
  {
    accessorKey: 'createdAt',
    header: 'Created',
    cell: ({ row }) => {
      const date = new Date(row.original.createdAt)
      return date.toLocaleDateString()
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
const roleFilter = ref('all')

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

watch(() => roleFilter.value, (newVal) => {
  if (!table?.value?.tableApi) return

  const roleColumn = table.value.tableApi.getColumn('role')
  if (!roleColumn) return

  if (newVal === 'all') {
    roleColumn.setFilterValue(undefined)
  } else {
    roleColumn.setFilterValue(newVal)
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
  <UDashboardPanel id="admin-users">
    <template #header>
      <UDashboardNavbar title="Users Management">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <UButton
            label="Add User"
            color="primary"
            icon="i-lucide-plus"
          />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="flex flex-wrap items-center justify-between gap-1.5">
        <UInput
          :model-value="(table?.tableApi?.getColumn('email')?.getFilterValue() as string)"
          class="max-w-sm"
          icon="i-lucide-search"
          placeholder="Filter emails..."
          @update:modelValue="table?.tableApi?.getColumn('email')?.setFilterValue($event)"
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
            v-model="roleFilter"
            :items="[
              { label: 'All Roles', value: 'all' },
              { label: 'Administrator', value: 'ADMIN' },
              { label: 'Property Owner', value: 'OWNER' },
              { label: 'Tenant', value: 'TENANT' }
            ]"
            :ui="{ trailingIcon: 'group-data-[state=open]:rotate-180 transition-transform duration-200' }"
            placeholder="Filter role"
            class="min-w-32"
          />

          <USelect
            v-model="statusFilter"
            :items="[
              { label: 'All Status', value: 'all' },
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
        :data="data ?? undefined"
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
